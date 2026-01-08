# Repo Context: openskills

- Source: `https://github.com/numman-ali/openskills`

## Detected Stack

- Node.js

## File Tree (partial)

```
.github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/config.yml
.github/ISSUE_TEMPLATE/feature_request.md
.github/workflows/ci.yml
.gitignore
.npmignore
CHANGELOG.md
CONTRIBUTING.md
examples/my-first-skill/SKILL.md
LICENSE
package-lock.json
package.json
README.md
SECURITY.md
src/cli.ts
src/commands/install.ts
src/commands/list.ts
src/commands/manage.ts
src/commands/read.ts
src/commands/remove.ts
src/commands/sync.ts
src/types.ts
src/utils/agents-md.ts
src/utils/dirs.ts
src/utils/marketplace-skills.ts
src/utils/skills.ts
src/utils/yaml.ts
tests/commands/install.test.ts
tests/commands/sync.test.ts
tests/integration/e2e.test.ts
tests/utils/dirs.test.ts
tests/utils/skills.test.ts
tests/utils/yaml.test.ts
tsconfig.json
tsup.config.ts
vitest.config.ts
```

## README (truncated)

- Path: `README.md`

```md
# OpenSkills

[![npm version](https://img.shields.io/npm/v/openskills.svg)](https://www.npmjs.com/package/openskills)
[![npm downloads](https://img.shields.io/npm/dm/openskills.svg)](https://www.npmjs.com/package/openskills)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**The closest implementation matching Claude Code's skills system** — same prompt format, same marketplace, same folders, just using CLI instead of tools.

```bash
npm i -g openskills
openskills install anthropics/skills
openskills sync
```

> **Found this useful?** Follow [@nummanali](https://x.com/nummanali) for more AI tooling!

---

## What Is This?

OpenSkills brings **Anthropic's skills system** to all AI coding agents (Claude Code, Cursor, Windsurf, Aider).

**For Claude Code users:**
- Install skills from any GitHub repo, not just the marketplace
- Install from local paths or private git repos
- Share skills across multiple agents
- Version control your skills in your repo
- Symlink skills for local development

**For other agents (Cursor, Windsurf, Aider):**
- Get Claude Code's skills system universally
- Access Anthropic's marketplace skills via GitHub
- Use progressive disclosure (load skills on demand)

---

## How It Matches Claude Code Exactly

OpenSkills replicates Claude Code's skills system with **100% compatibility**:

- ✅ **Same prompt format** — `<available_skills>` XML with skill tags
- ✅ **Same marketplace** — Install from [anthropics/skills](https://github.com/anthropics/skills)
- ✅ **Same folders** — Uses `.claude/skills/` by default
- ✅ **Same SKILL.md format** — YAML frontmatter + markdown instructions
- ✅ **Same progressive disclosure** — Load skills on demand, not upfront

**Only difference:** Claude Code uses `Skill` tool, OpenSkills uses `openskills read <name>` CLI command.

**Advanced:** Use `--universal` flag to install to `.agent/skills/` for Claude Code + other agents sharing one AGENTS.md.

---

## Quick Start

### 1. Install

```bash
npm i -g openskills
```

### 2. Install Skills

```bash
# Install from Anthropic's marketplace (interactive selection, default: project)
openskills install anthropics/skills

# Or install from any GitHub repo
openskills install your-org/custom-skills
```

### 3. Sync to AGENTS.md

_NOTE: You must have a pre-existing AGENTS.md file for sync to update._

```bash
openskills sync
```

Done! Your agent now has skills with the same `<available_skills>` format as Claude Code.

---

## How It Works (Technical Deep Dive)

### Claude Code's Skills System

When you use Claude Code with skills installed, Claude's system prompt includes:

```xml
<skills_instructions>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively.

How to use skills:
- Invoke skills using this tool with the skill name only (no arguments)
- When you invoke a skill, you will see <command-message>The "{name}" skill is loading</command-message>
- The skill's prompt will expand and provide detailed instructions

Important:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already running
</skills_instructions>

<available_skills>
<skill>
<name>pdf</name>
<description>Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms...</description>
<location>plugin</location>
</skill>

<skill>
<name>xlsx</name>
<description>Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis...</description>
<location>plugin</location>
</skill>
</available_skills>
```

**How Claude uses it:**
1. User asks: "Extract data from this PDF"
2. Claude scans `<available_skills>` → finds "pdf" skill
3. Claude invokes: `Skill("pdf")`
4. SKILL.md content loads with detailed instructions
5. Claude follows instructions to complete task

### OpenSkills' System (Identical Format)

OpenSkills generates the **exact same** `<available_skills>` XML in your AGENTS.md:

```xml
<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively.

How to use skills:
- Invoke: Bash("openskills read <skill-name>")
- The skill content will load with detailed instructions
- Base directory provided in output for resolving bundled resources

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
</usage>

<available_skills>

<skill>
<name>pdf</name>
<description>Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms...</description>
<location>project</location>
</skill>

<skill>
<name>xlsx</name>
<description>Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis...</description>
<location>project</location>
</skill>

</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>
```

**How agents use it:**
1. User asks: "Extract data from this PDF"
2. Agent scans `<available_skills>` → finds "pdf" skill
3. Agent invokes: `Bash("openskills read pdf")`
4. SKILL.md content is output to agent's context
5. Agent follows instructions to complete task

### Side-by-Side Comparison

| Aspect | Claude Code | OpenSkills |
|--------|-------------|------------|
| **System Prompt** | Built into Claude Code | In AGENTS.md |
| **Invocation** | `Skill("pdf")` tool | `openskills read pdf` CLI |
| **Prompt Format** | `<available_skills>` XML | `<available_skills>` XML (identical) |
| **Folder Structure** | `.claude/skills/` | `.claude/skills/` (identical) |
| **SKILL.md Format** | YAML + markdown | YAML + markdown (identical) |
| **Progressive Disclosure** | Yes | Yes |
| **Bundled Resources** | `references/`, `scripts/`, `assets/` | `references/`, `scripts/`, `assets/` (identical) |
| **Marketplace** | Anthropic marketplace | GitHub (anthropics/skills) |

**Everything is identical except the invocation method.**

### The SKILL.md Format

Both use the exact same format:

```markdown
---
name: pdf
description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms.
---

# PDF Skill Instructions

When the user asks you to work with PDFs, follow these steps:

1. Install dependencies: `pip install pypdf2`
2. Extract text using the extract_text.py script in scripts/
3. For bundled resources, use the base directory provided in the skill output
4. ...

[Detailed instructions that Claude/agent follows]
```

**Progressive disclosure:** The full instructions load only when the skill is invoked, keeping your agent's context clean.

---

## Why CLI Instead of MCP?

**MCP (Model Context Protocol)** is Anthropic's protocol for connecting AI to external tools and data sources. It's great for:
- Database connections
- API integrations
- Real-time data fetching
- External service integration

**Skills (SKILL.md format)** are different — they're for:
- Specialized workflows (PDF manipulation, spreadsheet editing)
- Bundled resources (scripts, templates, references)
- Progressive disclosure (load instructions only when needed)
- Static, reusable patterns

**Why not implement skills via MCP?**

1. **Skills are static instructions, not dynamic tools**
   MCP is for server-client connections. Skills are markdown files with instructions.

2. **No server needed**
   Skills are just files. MCP requires running servers.

3. **Universal compatibility**
   CLI works with any agent (Claude Code, Cursor, Windsurf, Aider). MCP requires MCP support.

4. **Follows Anthropic's design**
   Anthropic created skills as SKILL.md files, not MCP servers. We're implementing their spec.

5. **Simpler for users**
   `openskills install anthropics/skills` vs "configure MCP server, set up authentication, manage server lifecycle"

**MCP and skills solve different problems.** OpenSkills implements Anthropic's skills spec (SKILL.md format) the way it was designed — as progressively-loaded markdown instructions.

---

## Claude Code Compatibility

You can use **both** Claude Code plugins and OpenSkills project skills together:

**In your `<available_skills>` list:**
```xml
<skill>
<name>pdf</name>
<description>...</description>
<location>plugin</location>  <!-- Claude Code marketplace -->
</skill>

<skill>
<name>custom-skill</name>
<description>...</description>
<location>project</location>  <!-- OpenSkills from GitHub -->
</skill>
```

They coexist perfectly. Claude invokes marketplace plugins via `Skill` tool, OpenSkills skills via CLI. No conflicts.

### Advanced: Universal Mode for Multi-Agent Setups

**Problem:** If you use Claude Code + other agents (Cursor, Windsurf, Aider) with one AGENTS.md, installing to `.claude/skills/` can create duplicates with Claude Code's marketplace plugins.

**Solution:** Use `--universal` to install to `.agent/skills/` instead:

```bash
openskills install anthropics/skills --universal
```

This installs skills to `.agent/skills/` which:
- ✅ Works with all agents via AGENTS.md
- ✅ Doesn't conflict with Claude Code's native marketplace plugins
- ✅ Keeps Claude Code's `<available_skills>` separate from AGENTS.md skills

**When to use:**
- ✅ You use Claude Code + Cursor/Windsurf/Aider with one AGENTS.md
- ✅ You want to avoid duplicate skill definitions
- ✅ You prefer `.agent/` for infrastructure (keeps `.claude/` for Claude Code only)

**When not to use:**
- ❌ You only use Claude Code (default `.claude/skills/` is fine)
- ❌ You only use non-Claude agents (default `.claude/skills/` is fine)

**Priority order:**
OpenSkills searches 4 locations in priority order:
1. `./.agent/skills/` (project universal)
2. `~/.agent/skills/` (global universal)
3. `./.claude/skills/` (project)
4. `~/.claude/skills/` (global)

Skills with same name only appear once (highest priority wins).

---

## Commands

```bash
openskills install <source> [options]  # Install from GitHub, local path, or private repo
openskills sync [-y] [-o <path>]       # Update AGENTS.md (or custom output)
openskills list                        # Show installed skills
openskills read <name>                 # Load skill (for agents)
openskills manage                      # Remove skills (interactive)
openskills remove <name>               # Remove specific skill
```

### Flags

- `--global` — Install globally to `~/.claude/skills` (default: project install)
- `--universal` — Install to `.agent/skills/` instead of `.claude/skills/` (advanced)
- `-y, --yes` — Skip all prompts including overwrites (for scripts/CI)
- `-o, --output <path>` — Custom output file for sync (default: `AGENTS.md`)

### Installation Modes

**Default (recommended):**
```bash
openskills install anthropics/skills
# → Installs to ./.claude/skills (project, gitignored)
```

**Global install:**
```bash
openskills install anthropics/skills --global
# → Installs to ~/.claude/skills (shared across projects)
```

**Universal mode (advanced):**
```bash
openskills install anthropics/skills --universal
# → Installs to ./.agent/skills (for Claude Code + other agents)
```

### Install from Local Paths

```bash
# Absolute path
openskills install /path/to/my-skill

# Relative path
openskills install ./local-skills/my-skill

# Home directory
openskills install ~/my-skills/custom-skill

# Install all skills from a directory
openskills install ./my-skills-folder
```

### Install from Private Git Repos

```bash
# SSH (uses your SSH keys)
openskills install git@github.com:your-org/private-skills.git

# HTTPS (may prompt for credentials)
openskills install https://github.com/your-org/private-skills.git
```

### Sync Options

```bash
# Sync to default AGENTS.md
openskills sync

# Sync to custom file (auto-creates if missing)
op
…(truncated)
```

## Extracted README Sections (best-effort)

### quick start

```md
## Quick Start
```
