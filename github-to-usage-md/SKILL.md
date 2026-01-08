---
name: github-to-usage-md
description: Generate a concise Markdown usage document from a GitHub repository link. Use when the user provides a GitHub URL and asks to “总结成使用文档/说明文档”, “写一个 README/USAGE.md”, “explain what this repo does and how to use it”, or wants a quick purpose + usage guide for an open-source project.
---

# GitHub To Usage MD

## Overview

Turn a GitHub URL into a short, practical `.md` usage doc: what the project does, how to install/run it, and minimal examples/commands.

## Workflow (recommended)

1. Collect repo context (clone + README snippets + file tree)

```bash
python3 scripts/collect_repo_context.py "https://github.com/org/repo" --out REPO_CONTEXT.md
```

2. Read `REPO_CONTEXT.md` and (if needed) open the repo locally to inspect:
   - `README*`, `docs/`, examples, CLI entrypoints
   - build/install manifests: `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `Dockerfile`, `Makefile`, etc.
3. Write a new Markdown doc (default filename suggestions):
   - `USAGE.md` (preferred when you don’t want to change upstream README)
   - or `README.md` (when the repo lacks one / user explicitly wants README)
4. Keep it brief and runnable: include commands the user can paste.

## Output Format (USAGE.md template)

Use this structure unless the repo strongly suggests another:

```md
# <Project Name>

<1–2 sentences: what it does, for whom, why>

- Repo: <link>
- License: <if obvious>

## What It Does
- <3–6 bullets: key capabilities>

## Quick Start
<the minimal path to “it runs”>

## Install
<only the relevant path(s): pip/npm/cargo/go/docker>

## Run
<common commands>

## Configuration
<env vars / config file path / flags>

## Examples
<1–3 short examples>

## Notes
<limitations, OS requirements, common pitfalls>
```

## Heuristics (how to infer usage)

- Prefer upstream instructions: if README has “Installation/Usage”, paraphrase and keep commands verbatim.
- If multiple stacks exist, pick the primary one (based on README + manifest prominence).
- If there is a CLI:
  - Find the entrypoint (`__main__.py`, `console_scripts`, `bin/`, `cmd/`, `main.go`, `src/index.ts`, etc.)
  - Provide `--help` invocation and one realistic example command.
- If it’s a library:
  - Provide import snippet + minimal example.
- If it’s a service/app:
  - Provide local dev + production run (docker or build) if available.

## Resources

### scripts/
- `scripts/collect_repo_context.py`: clones (or reads a local repo) and writes `REPO_CONTEXT.md` with a partial file tree + README snippets to drive the summary.
