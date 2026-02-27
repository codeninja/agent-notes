import typer
import json
import os
import subprocess
from pathlib import Path

app = typer.Typer(help="Agent Notes Developer Experience Tools")

def get_mcp_config():
    project_path = Path(os.getcwd()).resolve()
    return {
        "command": "uv",
        "args": ["run", "--project", str(project_path), "python", "-m", "agent_notes.mcp"]
    }

@app.command()
def init_project():
    """
    Initialize the current project with the agent-notes skill for Claude Code.
    """
    try:
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        typer.echo("❌ Error: Not a git repository. Cannot initialize project skill.")
        return

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

@app.command()
def register_mcp():
    """
    Add the agent-notes MCP server to the global Claude Desktop config.
    """
    config_paths = [
        Path.home() / ".claude_desktop_config.json",
        Path.home() / "Library/Application Support/Claude/claude_desktop_config.json",
        Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
    ]
    
    config_path = None
    for p in config_paths:
        if p.exists():
            config_path = p
            break
            
    new_server = get_mcp_config()
    
    if config_path:
        try:
            config = json.loads(config_path.read_text())
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            
            config["mcpServers"]["agent-notes"] = new_server
            config_path.write_text(json.dumps(config, indent=2))
            typer.echo(f"✅ Successfully registered MCP server in {config_path}")
        except Exception as e:
            typer.echo(f"❌ Failed to update config: {e}")
    else:
        typer.echo("⚠️ Could not locate Claude config. Manually add this to mcpServers:")
        typer.echo(json.dumps({"agent-notes": new_server}, indent=2))

@app.command()
def auto_sync():
    """
    Configure the current repository to automatically fetch agent notes during 'git fetch' or 'git pull'.
    """
    try:
        # Check if we are in a git repo
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.STDOUT)
        
        # Add the fetch refspec to remote origin
        # The '+' prefix allows non-fast-forward updates to the notes
        cmd = ["git", "config", "--add", "remote.origin.fetch", "+refs/notes/agent/*:refs/notes/agent/*"]
        subprocess.check_call(cmd)
        
        typer.echo("✅ Auto-sync enabled: 'git pull' and 'git fetch' will now include agent notes.")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Error: {e}")

@app.command()
def stop_auto_sync():
    """
    Remove the automatic agent notes fetch configuration from the current repository.
    """
    try:
        # Check if we are in a git repo
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.STDOUT)
        
        # Unset the specific refspec
        subprocess.check_call(["git", "config", "--unset-all", "remote.origin.fetch", "refs/notes/agent/\\*"])
        
        typer.echo("✅ Auto-sync disabled: Agent notes will no longer be fetched automatically.")
    except subprocess.CalledProcessError as e:
        if e.returncode == 5:
            typer.echo("ℹ️ Auto-sync was not enabled for this repository.")
        else:
            typer.echo(f"❌ Error: {e}")

@app.command()
def onboard():
    """
    Full onboarding: Register MCP server and initialize current project.
    """
    typer.echo("🚀 Starting Agent Notes Onboarding...")
    register_mcp()
    init_project()
    typer.echo("🎉 Onboarding complete.")

if __name__ == "__main__":
    app()
