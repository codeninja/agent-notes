import typer
import subprocess
import os
from pathlib import Path

app = typer.Typer(help="Agent Notes Developer Experience Tools")

@app.command()
def init_claude():
    """
    Initialize Claude Code with the agent-notes skill.
    This creates the necessary MCP config and skill file.
    """
    project_root = Path(os.getcwd())
    
    # 1. Create the skill file for Claude Code
    # Claude Code looks for files in .claude/skills/
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
    
    # 2. Add MCP configuration suggestion
    # In a real environment, we'd append to ~/.claude/config.json or similar
    typer.echo("Initialized Claude Code skill in .claude/skills/agent-notes.md")
    typer.echo("\nTo enable the MCP server, add this to your Claude config:")
    typer.echo(f'uv run --project {project_root} python -m agent_notes.mcp')

if __name__ == "__main__":
    app()
