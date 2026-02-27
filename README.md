# Agent Notes (agent-notes) 🦞

**Persistent Agentic Memory embedded directly in your Git history.**

`agent-notes` is a library and MCP server that allows AI agents (like Claude Code, Windsurf, or OpenClaw) to store their implementation decisions, intent, and execution traces directly in Git commits using [**Git Notes**](https://git-scm.com/docs/git-notes). 

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
uv run --project path/to/agent-notes agent-notes-dx onboard
```

### 2. Manual Commands
You can also use the CLI directly:

```bash
# Add a decision note to the current commit
agent-notes add "Refactored auth to use Pydantic" --type decision

# Show all agent notes for a commit
agent-notes show HEAD --rich

# View a beautiful log of the last 20 commits with notes
agent-notes log --limit 20

# Review all notes between a feature branch and main
agent-notes diff main
```

### 🔍 Multi-Channel Visibility
By default, the `log` and `diff` commands aggregate notes from **all namespaces** for every commit. This gives you a complete "Technical Handover" of everything that happened.

- **Filter by Type:** Use `--type decision` to see only high-level reasoning.
- **Rich Visualization:** Use `--rich` (default) for a structured dashboard or `--plain` for raw text.

---

## 📸 Screenshots

### The Agentic Log (`agent-notes log`)
The `log` command builds a structured dashboard of your project's technical history:

![Agent Notes Log Table](https://raw.githubusercontent.com/codeninja/agent-notes/main/docs/assets/log_table.png)

### Technical Handover (`agent-notes show`)
Individual notes are wrapped in Rich Panels, making them easy to read:

![Agent Note Show Panel](https://raw.githubusercontent.com/codeninja/agent-notes/main/docs/assets/show_panel.png)

---

## 🤖 For Agents (MCP Tools)

When the MCP server is enabled, agents gain access to:

- `add_agent_note`: Store reasoning or traces.
- `show_agent_notes`: Read the "Decision Trail".
- `log_agent_notes`: Walk back through history (e.g., last 20 commits).
- `diff_agent_notes`: Review notes between branches (e.g., `main..HEAD`).
- `sync_agent_notes`: Ensure the local memory is in sync.

### Standard Namespaces
- `refs/notes/agent/decision`: High-level "why" behind changes.
- `refs/notes/agent/intent`: The original prompt or goal.
- `refs/notes/agent/trace`: Execution paths or tool-call logs.
- `refs/notes/agent/memory`: Long-term context.

---

## 🛠 Developer Experience (DX) CLI

The `agent-notes-dx` tool simplifies the setup process:

- `agent-notes-dx onboard`: The "one-and-done" command. Registers the MCP server and initializes the current project.
- `agent-notes-dx auto-sync`: Configures your local Git repo to **automatically fetch and push** agent notes during your normal `git pull` and `git push` workflow.
- `agent-notes-dx init-project`: Creates `.claude/skills/agent-notes.md` in your repo.
- `agent-notes-dx register-mcp`: Adds the server to your global Claude configuration.
- `agent-notes-dx onboard-openclaw`: (Internal) Registers the skill with OpenClaw assistants.

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
- **Syncing:** Notes are only pushed/pulled when `agent-notes sync` (or the corresponding tool) is called.

---

## 🏗 Publishing (Internal)

This project uses `uv` for publishing. To publish a new version:

1. Update the version in `pyproject.toml`.
2. Push a new tag: `git tag -a v0.1.0 -m "v0.1.0" && git push origin v0.1.0`.
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
