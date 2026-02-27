from fastmcp import FastMCP
from typing import Optional
import json
from .main import add as add_note_cmd, show as show_note_cmd, sync as sync_cmd

# Initialize FastMCP server
mcp = FastMCP("agent-notes")

@mcp.tool()
def add_agent_note(
    message: str,
    type: str = "decision",
    agent_id: str = "mcp-agent",
    ref: str = "HEAD",
    data: Optional[str] = None
) -> str:
    """
    Add an agentic note to a git commit.
    Types: decision, trace, memory, intent.
    Data should be a JSON string.
    """
    try:
        # We reuse the logic but capture the output
        # For a production library, we'd refactor main.py to separate logic from Typer
        # But for now, we'll invoke the functional logic
        add_note_cmd(message=message, type=type, agent_id=agent_id, ref=ref, data=data)
        return f"Successfully added {type} note to {ref}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def show_agent_notes(
    ref: str = "HEAD",
    type: Optional[str] = None
) -> str:
    """
    Retrieve agentic notes for a commit.
    """
    try:
        # Simple wrapper for now
        show_note_cmd(ref=ref, type=type)
        return "Notes displayed in logs (capture logic pending refactor)"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def diff_agent_notes(
    base: str = "main",
    head: str = "HEAD",
    type: Optional[str] = None
) -> str:
    """
    Retrieve all agentic notes for commits between a base ref and head.
    Useful for reviewing progress in a feature branch before a merge.
    """
    try:
        from .main import diff as diff_cmd
        diff_cmd(base=base, head=head, type=type)
        return "Diff displayed in logs"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def sync_agent_notes() -> str:
    """
    Sync agent notes with remote origin (push/pull refs).
    """
    try:
        sync_cmd()
        return "Sync complete"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
