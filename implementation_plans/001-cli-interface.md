# Implementation Plan: `agent-notes` CLI Interface

## Phase 0: CLI Interface Definition

The goal is to create a deterministic, versioned interface for agents to read and write memories to Git.

### Core Command Structure

The CLI will use `agent-notes` as the entry point.

#### 1. Writing Notes
`agent-notes add [MESSAGE]`
- `--type [decision|trace|memory|intent]`: Target namespace. Default: `decision`.
- `--ref [HASH|HEAD]`: Target commit. Default: `HEAD`.
- `--agent-id [ID]`: Identifier for the agent creating the note.
- `--data [JSON_STRING]`: Optional structured payload.
- `--force`: Overwrite existing note in that namespace/ref.

#### 2. Reading Notes
`agent-notes show [REF]`
- `--type [TYPE]`: Filter by namespace.
- `--format [text|json]`: Output format.
- `--all`: Aggregate all agent namespaces for this commit.

`agent-notes list`
- `--limit [N]`: Show notes for the last N commits.
- `--search [QUERY]`: Grep through notes across history.

#### 3. Syncing (The "Agentic Handshake")
`agent-notes sync`
- Fetches all agent note refs from origin and pushes local ones.
- `git fetch origin refs/notes/agent/*:refs/notes/agent/*`
- `git push origin refs/notes/agent/*`

### Schema (Draft)
Notes will be stored as JSON internally:
```json
{
  "version": "1.0",
  "agent_id": "openclaw-main",
  "type": "decision",
  "timestamp": "2026-02-28T12:00:00Z",
  "message": "Used GitPython for CLI as it handles porcelain commands better than raw subprocess for refs.",
  "data": {
    "issue_id": "NS-123",
    "confidence": 0.95
  }
}
```

### Next Steps
1. Create `pyproject.toml` with `uv`.
2. Implement the CLI entry point using `typer` or `click`.
3. Implement the Git Note wrapper logic.
