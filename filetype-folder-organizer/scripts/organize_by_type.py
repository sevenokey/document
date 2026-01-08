#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


MULTIPART_EXTENSIONS = (
    ".tar.gz",
    ".tar.bz2",
    ".tar.xz",
    ".tar.zst",
    ".tar.lz4",
)


def _is_relative_to(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
        return True
    except ValueError:
        return False


def normalize_type_name(file_path: Path) -> str:
    name = file_path.name
    lower = name.lower()

    if name.startswith(".") and name.count(".") == 1:
        return "dotfile"

    for ext in MULTIPART_EXTENSIONS:
        if lower.endswith(ext):
            return ext.lstrip(".")

    suffix = file_path.suffix.lower()
    if not suffix:
        return "no-extension"
    return suffix.lstrip(".")


_SAFE_FOLDER_RE = re.compile(r"[^a-zA-Z0-9._-]+")


def sanitize_folder_name(type_name: str) -> str:
    cleaned = _SAFE_FOLDER_RE.sub("_", type_name.strip())
    cleaned = cleaned.strip("._-")
    return cleaned or "unknown"


def unique_destination_path(dest_path: Path) -> Path:
    if not dest_path.exists():
        return dest_path

    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    for i in range(1, 10_000):
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate

    raise RuntimeError(f"Unable to find a free filename for: {dest_path}")


@dataclass(frozen=True)
class MovePlan:
    source: Path
    dest: Path
    action: str  # "move" | "copy"


def iter_source_files(source_dir: Path, recursive: bool) -> list[Path]:
    if recursive:
        files: list[Path] = []
        for root, dirs, filenames in os.walk(source_dir):
            root_path = Path(root)
            dirs[:] = [d for d in dirs if not (root_path / d).is_symlink()]
            for filename in filenames:
                p = root_path / filename
                if p.is_file() or p.is_symlink():
                    files.append(p)
        return files

    return [
        p
        for p in source_dir.iterdir()
        if (p.is_file() or p.is_symlink()) and not p.is_dir()
    ]


def build_plans(source_dir: Path, dest_root: Path, recursive: bool, action: str) -> list[MovePlan]:
    source_dir = source_dir.resolve()
    dest_root = dest_root.resolve()

    if recursive and _is_relative_to(dest_root, source_dir):
        raise ValueError(
            "--recursive requires --dest outside the source directory (to avoid re-sorting moved files)."
        )

    plans: list[MovePlan] = []
    for file_path in iter_source_files(source_dir, recursive=recursive):
        type_name = sanitize_folder_name(normalize_type_name(file_path))
        dest_dir = dest_root / type_name
        dest_path = dest_dir / file_path.name

        if file_path.resolve().parent == dest_dir.resolve():
            continue

        plans.append(MovePlan(source=file_path, dest=dest_path, action=action))

    return plans


def ensure_dir(path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    path.mkdir(parents=True, exist_ok=True)


def execute_plans(plans: list[MovePlan], dry_run: bool, verbose: bool) -> int:
    moved = 0
    for plan in plans:
        ensure_dir(plan.dest.parent, dry_run=dry_run)
        final_dest = unique_destination_path(plan.dest)

        if verbose or dry_run:
            print(f"{plan.action.upper()}: {plan.source} -> {final_dest}")

        if dry_run:
            moved += 1
            continue

        if plan.action == "move":
            shutil.move(str(plan.source), str(final_dest))
        elif plan.action == "copy":
            shutil.copy2(str(plan.source), str(final_dest))
        else:
            raise ValueError(f"Unknown action: {plan.action}")

        moved += 1

    return moved


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organize files in a folder into subfolders by file type (extension)."
    )
    parser.add_argument("source", help="Source folder whose files will be organized")
    parser.add_argument(
        "--dest",
        default=None,
        help="Destination root folder (default: same as source)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Include files in subfolders (requires --dest outside source)",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy instead of move",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print operations without changing files",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print operations",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    source_dir = Path(args.source).expanduser()
    if not source_dir.exists():
        print(f"ERROR: source does not exist: {source_dir}", file=sys.stderr)
        return 2
    if not source_dir.is_dir():
        print(f"ERROR: source is not a directory: {source_dir}", file=sys.stderr)
        return 2

    dest_root = Path(args.dest).expanduser() if args.dest else source_dir
    action = "copy" if args.copy else "move"

    try:
        plans = build_plans(source_dir, dest_root, recursive=args.recursive, action=action)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if not plans:
        if args.verbose or args.dry_run:
            print("No files to organize.")
        return 0

    moved = execute_plans(plans, dry_run=args.dry_run, verbose=args.verbose)
    if args.verbose or args.dry_run:
        print(f"Planned/processed {moved} file(s).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
