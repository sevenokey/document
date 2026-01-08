---
name: filetype-folder-organizer
description: Organize files in a specified folder by file type/extension, moving (or copying) each file into a newly created subfolder named after the type (e.g., pdf/, jpg/, docx/, no-extension/). Use when the user asks in Chinese or English to “按文件类型/按后缀分类文件”, “把某个文件夹里的文件按类型放到不同文件夹”, “sort/organize files by extension”, or similar cleanup/archiving requests.
---

# Filetype Folder Organizer

## Overview

Sort files in a folder into subfolders named by file type (file extension). Default behavior is non-recursive and moves files in-place under the source directory.

## Quick Start

1. Ask for the target folder path and whether the user wants to **move** (default) or **copy**.
2. Run a dry-run first:

```bash
python3 scripts/organize_by_type.py "/path/to/folder" --dry-run
```

3. If it looks correct, run it for real:

```bash
python3 scripts/organize_by_type.py "/path/to/folder" --verbose
```

## Workflow

1. Confirm inputs
   - `source`: the folder to organize
   - `dest`: where to create type folders (default: same as `source`)
   - `move` vs `copy`
   - `recursive` needs special handling (see below)
2. Run `--dry-run` and verify the planned moves/copies.
3. Run the real command.

## Commands

- Move files in-place (non-recursive):

```bash
python3 scripts/organize_by_type.py "/path/to/folder"
```

- Copy instead of move:

```bash
python3 scripts/organize_by_type.py "/path/to/folder" --copy
```

- Set a different destination root (creates `pdf/`, `jpg/`, ... under `dest`):

```bash
python3 scripts/organize_by_type.py "/path/to/source" --dest "/path/to/dest"
```

- Recursive mode (requires `--dest` outside `source`):

```bash
python3 scripts/organize_by_type.py "/path/to/source" --recursive --dest "/path/to/dest" --dry-run
```

## File Type Rules

- Uses the filename extension as the type folder name (lowercased): `report.PDF` → `pdf/`.
- Special cases:
  - Multi-part archives: `.tar.gz`, `.tar.xz`, `.tar.bz2`, `.tar.zst`, `.tar.lz4` → `tar.gz/`, etc.
  - No extension: `no-extension/`
  - Dotfiles like `.gitignore`: `dotfile/`
- Folder names are sanitized to be filesystem-safe (invalid characters become `_`).

## Safety Notes

- Always recommend running with `--dry-run` first for confirmation.
- If a destination filename already exists, the script auto-renames with `_1`, `_2`, etc.

## Resources

### scripts/
- `scripts/organize_by_type.py`: CLI utility to move/copy files into type-named folders.
