# Agent Notes (agent-notes) 🦞

**Persistent Agentic Memory embedded directly in your Git history.**

`agentnotes` is a library and MCP server that allows AI agents (like Claude Code, Windsurf, or OpenClaw) to store their implementation decisions, intent, and execution traces directly in Git commits using [**Git Notes**](https://git-scm.com/docs/git-notes). 

### Why Git Notes?
Unlike standard Markdown files or external databases, Git Notes allow for **atomic coupling** of reasoning to code without cluttering your history or causing merge collisions. 

**[Read the full justification here →](docs/WHY_GIT_NOTES.md)**

By using custom namespaces (refs), agents can share a "collective memory" that survives across sessions and is synced with the repository without polluting the main commit messages.

---

## 📦 Installation (from PyPI)

```bash
pip install agent-notes
# OR using uv
uv tool install agent-notes
```

## 🚀 Quick Start (For Humans)

### 1. Install & Onboard
If you are using Claude Desktop or Claude Code, you can set everything up in one command:

```bash
# Register the MCP server globally and initialize the current project
uv run --project path/to/agent-notes agentnotes-dx onboard
```

### 2. Manual Commands
You can also use the CLI directly:

```bash
# Add a decision note to the current commit
agentnotes add "Refactored auth to use Pydantic" --type decision

# Show all agent notes for a commit
agentnotes show HEAD --rich

# View a beautiful log of the last 20 commits with notes
agentnotes log --limit 20

# Review all notes between a feature branch and main
agentnotes diff main
```

### 🔍 Multi-Channel Visibility
By default, the `log` and `diff` commands aggregate notes from **all namespaces** for every commit. This gives you a complete "Technical Handover" of everything that happened.

- **Filter by Type:** Use `--type decision` to see only high-level reasoning.
- **Rich Visualization:** Use `--rich` (default) for a structured dashboard or `--plain` for raw text.

---

## 📸 Screenshots

### The Agentic Log (`agentnotes log`)
The `log` command builds a structured dashboard of your project's technical history:

#### Pretty Logs

![Agent Notes Pretty Log Table](https://raw.githubusercontent.com/codeninja/agent-notes/main/docs/assets/log.png)


#### Text based console logs
```text
                         Agentic Memory: Last 5 commits                         
╭──────────┬──────────┬───────────┬────────────────────────────────────────────╮
│ Commit   │ Type     │ Agent     │ Message                                    │
├──────────┼──────────┼───────────┼────────────────────────────────────────────┤
│ 792d19c7 │ decision │ claw      │ Bumped version to 0.2.3. Improved DX...    │
├──────────┼──────────┼───────────┼────────────────────────────────────────────┤
│ f46c599b │ decision │ claw      │ Updated get_mcp_config for global installs │
├──────────┼──────────┼───────────┼────────────────────────────────────────────┤
│ 3638b0e6 │ decision │ claw      │ Renamed CLI entrypoints to agentnotes      │
╰──────────┴──────────┴───────────┴────────────────────────────────────────────╯
```

### Technical Handover (`agentnotes show`)
Individual notes are wrapped in Rich Panels, making them easy to read:

```text
╭─────────────────────────── Agent Note: decision ────────────────────────────╮
│ Message: Added comprehensive test suite for the CLI and DX tools.           │
│ Agent: claw                                                                 │
│ Time: 2026-02-27T17:45:00Z                                                  │
╰─────────────────────────────────────────────────────────────────────────────╯
```

---

## 🤖 For Agents (MCP Tools)

When the MCP server is enabled, agents gain access to:

- `add_agent_note`: Store reasoning or traces.
- `show_agent_notes`: Read the "Decision Trail".
- `log_agent_notes`: Walk back through history (e.g., last 20 commits).
- `diff_agent_notes`: Review notes between branches (e.g., `main..HEAD`).
- `sync_agent_notes`: Ensure the local memory is in sync.

---

## 🛠 Developer Experience (DX) CLI

The `agentnotes-dx` tool simplifies the setup process:

- `agentnotes-dx onboard`: The "one-and-done" command. Registers the MCP server and initializes the current project.
- `agentnotes-dx auto-sync`: Configures your local Git repo to **automatically fetch and push** agent notes during your normal `git pull` and `git push` workflow.
- `agentnotes-dx init-project`: Creates `.claude/skills/agentnotes.md` in your repo.
- `agentnotes-dx register-mcp`: Adds the server to your global Claude configuration.
- `agentnotes-dx onboard-openclaw`: (Internal) Registers the skill with OpenClaw assistants.

---

## ❓ Notes vs. Commit Messages

Why not just put this in the commit message?

- **Zero Pollution:** Keep your `git log` clean for human review. Agents can be as verbose as they need to be in the notes without cluttering the history.
- **Post-Commit Context:** Unlike commit messages, notes can be added, updated, or appended to *after* a commit is pushed without changing the hash or requiring a force-push.
- **Structured Channels:** Use namespaces (`decision`, `trace`, `intent`) to separate high-level reasoning from low-level execution logs.
- **Machine Determinism:** Standard commit messages are unstructured text. Agent Notes are versioned JSON, allowing other agents to parse and "understand" the history with 100% accuracy.

---

## 🏗 Tech Stack
- **Python 3.12+** (managed via `uv`)
- **Pydantic**: For structured, versioned memory schemas.
- **GitPython**: For deterministic Git ref manipulation.
- **FastMCP**: For high-performance MCP server delivery.

---

## 🔒 Safety & Privacy
- **Metadata Only:** Notes are attached to commits but do not modify your source code or change commit hashes.
- **Namespaced:** Uses `refs/notes/agent/*` to stay separate from standard user notes.
- **Syncing:** Notes are only pushed/pulled when `agentnotes sync` (or the corresponding tool) is called.

---

## 🏗 Publishing (Internal)

This project uses `uv` for publishing. To publish a new version:

1. Update the version in `pyproject.toml`.
2. Push a new tag: `git tag -a v0.2.3 -m "v0.2.3" && git push origin v0.2.3`.
3. The GitHub Action will automatically build and publish to PyPI using the `PYPI_TOKEN` secret.

Alternatively, to publish manually:
```bash
make bump-patch  # or minor/major
git commit -am "chore: bump version"
make tag         # tags and pushes to trigger GitHub Action
```

Or fully manual:
```bash
make build
make publish
```

---
*Created by Dallas Pool (@codeninja)*
