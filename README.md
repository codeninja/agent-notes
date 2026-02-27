# Agent Notes (agent-notes) 🦞

**Persistent Agentic Memory embedded directly in your Git history.**

`agent-notes` is a library and MCP server that allows AI agents (like Claude Code, Windsurf, or OpenClaw) to store their implementation decisions, intent, and execution traces directly in Git commits using [**Git Notes**](https://git-scm.com/docs/git-notes). 

By using custom namespaces (refs), agents can share a "collective memory" that survives across sessions and is synced with the repository without polluting the main commit messages.

---

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
agent-notes add "Refactored auth to use Pydantic for better validation" --type decision

# Show all agent notes for a commit
agent-notes show HEAD --all

# Sync agent memory with the remote origin
agent-notes sync
```

---

## 🤖 For Agents (MCP Tools)

When the MCP server is enabled, agents gain access to:

- `add_agent_note`: Store reasoning or traces.
- `show_agent_notes`: Read the "Decision Trail" left by previous agents or humans.
- `sync_agent_notes`: Ensure the local memory is in sync with the team/origin.

### Standard Namespaces
- `refs/notes/agent/decision`: High-level "why" behind changes.
- `refs/notes/agent/intent`: The original prompt or goal.
- `refs/notes/agent/trace`: Execution paths or tool-call logs.
- `refs/notes/agent/memory`: Long-term context.

---

## 🛠 Developer Experience (DX) CLI

The `agent-notes-dx` tool simplifies the setup process:

- `agent-notes-dx register-mcp`: Adds the server to your `claude_desktop_config.json`.
- `agent-notes-dx init-project`: Creates `.claude/skills/agent-notes.md` in your repo to "teach" Claude how to use the memory.
- `agent-notes-dx onboard`: Runs both of the above.

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
*Created by Dallas Pool (@codeninja)*
