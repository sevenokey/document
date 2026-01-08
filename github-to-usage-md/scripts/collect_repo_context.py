#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


EXCLUDE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    ".cache",
    ".idea",
    ".vscode",
}

README_CANDIDATES = (
    "README.md",
    "README.MD",
    "README",
    "readme.md",
    "Readme.md",
)


@dataclass(frozen=True)
class RepoContext:
    source: str
    repo_dir: Path
    repo_name: str
    head_ref: str | None


def run(cmd: list[str], cwd: Path | None = None) -> str:
    p = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return p.stdout.strip()


def is_probably_github_url(s: str) -> bool:
    return s.startswith("https://github.com/") or s.startswith("git@github.com:")


def normalize_github_url(url: str) -> str:
    url = url.strip()
    if url.startswith("git@github.com:"):
        # git@github.com:org/repo(.git)
        path = url[len("git@github.com:") :]
        url = f"https://github.com/{path}"
    url = re.sub(r"\.git$", "", url)
    return url


def clone_repo(url: str, ref: str | None, depth: int) -> RepoContext:
    norm = normalize_github_url(url)
    repo_name = norm.rstrip("/").split("/")[-1]

    tmp_dir = Path(tempfile.mkdtemp(prefix="github-to-usage-md-"))
    repo_dir = tmp_dir / repo_name

    cmd = ["git", "clone", "--depth", str(depth), norm, str(repo_dir)]
    run(cmd)

    head_ref = None
    if ref:
        run(["git", "checkout", ref], cwd=repo_dir)
        head_ref = ref

    return RepoContext(source=norm, repo_dir=repo_dir, repo_name=repo_name, head_ref=head_ref)


def open_local_repo(path_str: str) -> RepoContext:
    repo_dir = Path(path_str).expanduser().resolve()
    if not repo_dir.exists() or not repo_dir.is_dir():
        raise ValueError(f"Local path is not a directory: {repo_dir}")
    if not (repo_dir / ".git").exists():
        # allow non-git dirs too; still useful for docs generation
        pass
    repo_name = repo_dir.name
    head_ref = None
    try:
        head_ref = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir) or None
    except Exception:
        head_ref = None
    return RepoContext(source=str(repo_dir), repo_dir=repo_dir, repo_name=repo_name, head_ref=head_ref)


def iter_tree(root: Path, max_depth: int) -> Iterable[str]:
    root = root.resolve()
    for current_root, dirs, files in os.walk(str(root)):
        current = Path(current_root).resolve()
        rel_dir = os.path.relpath(str(current), str(root))
        depth = 0 if rel_dir in (".", "") else len(Path(rel_dir).parts)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        if depth > max_depth:
            dirs[:] = []
            continue
        for f in files:
            p = current / f
            if p.is_symlink():
                continue
            yield os.path.relpath(str(p), str(root))


def format_tree(root: Path, max_depth: int, max_entries: int) -> list[str]:
    entries: list[str] = []
    for rel in sorted(iter_tree(root, max_depth=max_depth), key=lambda x: str(x).lower()):
        entries.append(str(rel))
        if len(entries) >= max_entries:
            break
    return entries


def find_first_existing(root: Path, candidates: Iterable[str]) -> Path | None:
    for c in candidates:
        p = root / c
        if p.exists() and p.is_file():
            return p
    return None


def read_text_snippet(path: Path, max_chars: int) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    data = data.strip()
    if len(data) > max_chars:
        return data[:max_chars].rstrip() + "\n…(truncated)"
    return data


SECTION_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)\s*$")


def extract_markdown_sections(md: str, wanted_titles: set[str], max_chars: int) -> dict[str, str]:
    wanted = {t.lower().strip() for t in wanted_titles}
    current_title: str | None = None
    current_lines: list[str] = []
    out: dict[str, str] = {}

    def flush() -> None:
        nonlocal current_title, current_lines
        if current_title is None:
            return
        key = current_title.lower().strip()
        if key in wanted and key not in out:
            text = "\n".join(current_lines).strip()
            if len(text) > max_chars:
                text = text[:max_chars].rstrip() + "\n…(truncated)"
            out[key] = text
        current_title = None
        current_lines = []

    for line in md.splitlines():
        m = SECTION_HEADER_RE.match(line)
        if m:
            flush()
            current_title = m.group(2)
            current_lines = [line]
            continue
        if current_title is not None:
            current_lines.append(line)

    flush()
    return out


def detect_stack(root: Path) -> list[str]:
    hits: list[str] = []
    checks = [
        ("Python", ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"]),
        ("Node.js", ["package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json"]),
        ("Rust", ["Cargo.toml"]),
        ("Go", ["go.mod"]),
        ("Java (Maven)", ["pom.xml"]),
        ("Java (Gradle)", ["build.gradle", "build.gradle.kts"]),
        ("Docker", ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]),
        ("Make", ["Makefile"]),
    ]
    for label, files in checks:
        if find_first_existing(root, files):
            hits.append(label)
    return hits


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Clone/read a GitHub repo and output a compact Markdown context file for writing a usage doc."
    )
    p.add_argument("source", help="GitHub URL (https://github.com/org/repo) or local repo path")
    p.add_argument("--ref", default=None, help="Git ref (branch/tag/sha) to checkout when cloning")
    p.add_argument("--depth", type=int, default=1, help="git clone depth (default: 1)")
    p.add_argument("--out", default="REPO_CONTEXT.md", help="Output markdown path (default: REPO_CONTEXT.md)")
    p.add_argument("--max-depth", type=int, default=2, help="Tree listing max depth (default: 2)")
    p.add_argument("--max-entries", type=int, default=300, help="Max tree entries (default: 300)")
    p.add_argument("--max-readme-chars", type=int, default=12_000, help="Max chars to include from README (default: 12000)")
    p.add_argument("--max-section-chars", type=int, default=6_000, help="Max chars per extracted section (default: 6000)")
    p.add_argument(
        "--keep-clone",
        action="store_true",
        help="Keep the cloned repo directory (prints its path).",
    )
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    source = args.source

    tmp_to_cleanup: Path | None = None
    try:
        if is_probably_github_url(source):
            ctx = clone_repo(source, ref=args.ref, depth=args.depth)
            tmp_to_cleanup = ctx.repo_dir.parent
        else:
            ctx = open_local_repo(source)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    root = ctx.repo_dir
    readme_path = find_first_existing(root, README_CANDIDATES)
    readme_text = read_text_snippet(readme_path, max_chars=args.max_readme_chars) if readme_path else ""

    wanted = {
        "quickstart",
        "quick start",
        "installation",
        "install",
        "usage",
        "getting started",
        "configuration",
        "run",
        "build",
        "develop",
        "docker",
    }
    extracted = extract_markdown_sections(readme_text, wanted_titles=wanted, max_chars=args.max_section_chars) if readme_text else {}

    tree = format_tree(root, max_depth=args.max_depth, max_entries=args.max_entries)
    stack = detect_stack(root)

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append(f"# Repo Context: {ctx.repo_name}")
    lines.append("")
    lines.append(f"- Source: `{ctx.source}`")
    if ctx.head_ref:
        lines.append(f"- Ref: `{ctx.head_ref}`")
    lines.append("")

    if stack:
        lines.append("## Detected Stack")
        lines.append("")
        for s in stack:
            lines.append(f"- {s}")
        lines.append("")

    lines.append("## File Tree (partial)")
    lines.append("")
    lines.append("```")
    lines.extend(tree if tree else ["(empty)"])
    lines.append("```")
    lines.append("")

    if readme_path and readme_text:
        lines.append("## README (truncated)")
        lines.append("")
        lines.append(f"- Path: `{readme_path.relative_to(root)}`")
        lines.append("")
        lines.append("```md")
        lines.append(readme_text)
        lines.append("```")
        lines.append("")

    if extracted:
        lines.append("## Extracted README Sections (best-effort)")
        lines.append("")
        for title in sorted(extracted.keys()):
            lines.append(f"### {title}")
            lines.append("")
            lines.append("```md")
            lines.append(extracted[title])
            lines.append("```")
            lines.append("")

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(str(out_path))

    if tmp_to_cleanup and not args.keep_clone:
        # best-effort cleanup; ignore failures
        try:
            for child in tmp_to_cleanup.iterdir():
                # safety: only delete our temp folder prefix
                pass
            import shutil

            shutil.rmtree(tmp_to_cleanup, ignore_errors=True)
        except Exception:
            pass
    elif tmp_to_cleanup and args.keep_clone:
        print(f"Kept clone at: {ctx.repo_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
