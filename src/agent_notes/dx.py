import typer
import subprocess
import os
from pathlib import Path

app = typer.Typer(help="Agent Notes Developer Experience Tools")

@app.command()
def onboard():
    """
    Onboard the current user by adding the agent-notes MCP server to the global Claude config.
    """
    # ... (onboard logic) ...

@app.command()
def init_project():
    """
    Initialize the current project with the agent-notes skill for Claude Code.
    """
    project_root = Path(os.getcwd())
    skill_dir = project_root / ".claude" / "skills"
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    skill_content = """# Agent Notes Skill
This skill allows you to record your implementation decisions and trace your work directly into the Git history using Git Notes.

## Rules
1. ALWAYS record a 'decision' note after finishing a significant task.
2. Use the 'intent' note to document the prompt or goal before starting.
3. Use the 'sync_agent_notes' tool before and after your work loop.

## Tools
- `add_agent_note(message, type, data)`: Add memory to the current commit.
- `show_agent_notes(ref)`: See what other agents (or your past self) thought.
- `sync_agent_notes()`: Push/pull memory from the cloud.
"""
    (skill_dir / "agent-notes.md").write_text(skill_content)
    typer.echo(f"✅ Initialized Claude Code skill in {skill_dir}/agent-notes.md")

if __name__ == "__main__":
    app()
