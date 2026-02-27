import typer
import json
import os
import subprocess
from pathlib import Path

app = typer.Typer(
    help="Agent Notes Developer Experience Tools",
    no_args_is_help=True
)

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
    Configure the current repository to automatically fetch and push agent notes.
    """
    try:
        # Check if we are in a git repo
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.STDOUT)
        
        # 1. Configure Fetch: Ensure standard heads AND agent notes are fetched
        # We check if it exists first to avoid duplicates
        existing_fetch = subprocess.run(["git", "config", "--get-all", "remote.origin.fetch"], capture_output=True, text=True).stdout
        if "refs/notes/agent/*:refs/notes/agent/*" not in existing_fetch:
            subprocess.check_call(["git", "config", "--add", "remote.origin.fetch", "+refs/notes/agent/*:refs/notes/agent/*"])
        
        # 2. Configure Push: Ensure standard heads AND agent notes are pushed
        # Explicitly setting push refspecs overrides the default push behavior (push.default).
        # To keep branch pushing working, we MUST include a heads refspec if we add any push refspec.
        existing_push = subprocess.run(["git", "config", "--get-all", "remote.origin.push"], capture_output=True, text=True).stdout
        
        if "refs/heads/*:refs/heads/*" not in existing_push:
            subprocess.check_call(["git", "config", "--add", "remote.origin.push", "refs/heads/*:refs/heads/*"])
        
        if "refs/notes/agent/*:refs/notes/agent/*" not in existing_push:
            subprocess.check_call(["git", "config", "--add", "remote.origin.push", "refs/notes/agent/*:refs/notes/agent/*"])
        
        typer.echo("✅ Auto-sync (Fetch) enabled: 'git pull' will include agent notes.")
        typer.echo("✅ Auto-sync (Push) enabled: 'git push' will include agent notes and all branches.")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Error: {e}")

@app.command()
def stop_auto_sync():
    """
    Remove automatic fetch and push configurations for agent notes.
    """
    try:
        # Check if we are in a git repo
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], stderr=subprocess.STDOUT)
        
        # Unset fetch refspec
        subprocess.check_call(["git", "config", "--unset-all", "remote.origin.fetch", "refs/notes/agent/\\*"])
        
        # Unset push refspec
        subprocess.check_call(["git", "config", "--unset-all", "remote.origin.push", "refs/notes/agent/\\*"])
        
        typer.echo("✅ Auto-sync disabled for both Fetch and Push.")
    except subprocess.CalledProcessError as e:
        if e.returncode == 5:
            typer.echo("ℹ️ Auto-sync was not enabled for this repository.")
        else:
            typer.echo(f"❌ Error: {e}")

@app.command()
def onboard_openclaw():
    """
    Onboard the agent-notes skill to the local OpenClaw workspace.
    """
    workspace_skills_dir = Path("/home/codeninja/.openclaw/workspace/skills")
    if not workspace_skills_dir.exists():
        typer.echo("❌ Error: OpenClaw workspace skills directory not found at /home/codeninja/.openclaw/workspace/skills")
        return

    skill_target_dir = workspace_skills_dir / "agent-notes"
    skill_target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Create the OpenClaw SKILL.md
    project_root = Path(os.getcwd()).resolve()
    skill_content = f"""---
name: agent-notes
description: Persistent Agentic Memory via Git Notes. Use this to record implementation decisions, intent, and execution traces directly in the Git history.
---

# Agent Notes Skill

This skill allows you to record your implementation decisions and trace your work directly in the Git history using [Git Notes](https://git-scm.com/docs/git-notes).

## Usage
- ALWAYS record a 'decision' note after finishing a significant task.
- Use the 'intent' note to document the goal before starting.
- Use 'auto-sync' to ensure memory is pushed/pulled alongside code.

## Tools (CLI via shell)
- `agent-notes add "message" --type [decision|intent|trace|memory]`
- `agent-notes log`
- `agent-notes show HEAD`
- `agent-notes-dx auto-sync`

## Integration
This skill assumes `agent-notes` is installed in the python environment. 
Path: `{project_root}`
"""
    (skill_target_dir / "SKILL.md").write_text(skill_content)
    
    typer.echo(f"✅ Successfully onboarded 'agent-notes' skill to OpenClaw at {skill_target_dir}/SKILL.md")
    typer.echo("ℹ️ OpenClaw will now recognize 'agent-notes' as an available skill.")

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
