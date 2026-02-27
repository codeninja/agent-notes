import typer
import subprocess
import os
from pathlib import Path

app = typer.Typer(help="Agent Notes Developer Experience Tools")

@app.command()
def onboard(
    init_project_repo: bool = typer.Option(True, "--init/--no-init", help="Automatically initialize the current project with the Claude skill")
):
    """
    Onboard the current user by adding the agent-notes MCP server to the global Claude config.
    """
    config_path = Path.home() / ".claude_desktop_config.json"
    if not config_path.exists():
        # macOS default
        config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    
    project_path = Path(os.getcwd()).resolve()
    mcp_command = "uv"
    mcp_args = ["run", "--project", str(project_path), "python", "-m", "agent_notes.mcp"]
    
    new_server = {
        "command": mcp_command,
        "args": mcp_args
    }
    
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            
            config["mcpServers"]["agent-notes"] = new_server
            config_path.write_text(json.dumps(config, indent=2))
            typer.echo(f"✅ Successfully added 'agent-notes' to {config_path}")
        except Exception as e:
            typer.echo(f"❌ Failed to update config: {e}")
    else:
        typer.echo(f"⚠️ Could not automatically locate Claude Desktop config.")
        typer.echo("Please manually add the following entry to your mcpServers:")
        typer.echo(json.dumps({"agent-notes": new_server}, indent=2))

    if init_project_repo:
        # Check if we are in a git repo before initializing
        try:
            subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.STDOUT)
            init_project()
        except subprocess.CalledProcessError:
            typer.echo("ℹ️ Not a git repository, skipping project initialization.")

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
