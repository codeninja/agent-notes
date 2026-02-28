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
    # If we are in a development environment (editable install), use --project
    # Otherwise, assume global installation via 'agentnotes' entrypoint
    project_path = Path(os.getcwd()).resolve()
    if (project_path / "pyproject.toml").exists() and (project_path / "src" / "agent_notes").exists():
        return {
            "command": "uv",
            "args": ["run", "--project", str(project_path), "python", "-m", "agent_notes.mcp"]
        }
    else:
        # Global package installation
        return {
            "command": "agentnotes",
            "args": ["mcp"]
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

## The Core Philosophy
Agent Notes are NOT commit messages. 
- **Commit Messages** are for humans; they describe *what* changed in the code.
- **Agent Notes** are for the agentic chain; they describe the *why*, the *trade-offs*, and the *context* needed for the next agent to pick up where you left off.

## Rules
1. **The Handover:** Treat every 'decision' note as a technical handover to another senior engineer/agent. 
2. **Distinct Reasoning:** Do not just repeat the commit message. Explain *why* you chose this approach, what alternatives you rejected, and any "gotchas" you discovered.
3. **The Intent:** Use the 'intent' note *before* starting a task to document the goal.
4. **Automated Feedback:** Always 'sync_agent_notes' before starting to see what your predecessors left for you.

## Tools
- `add_agent_note(message, type, data)`: Add memory/handover to the current commit.
- `show_agent_notes(ref)`: See the technical handover from past agents.
- `sync_agent_notes()`: Push/pull the collective memory.

## CLI (Shell)
- `agentnotes add "message"`: Add a decision.
- `agentnotes log`: View history.
"""
    (skill_dir / "agentnotes.md").write_text(skill_content)
    typer.echo(f"✅ Initialized Claude Code skill in {skill_dir}/agentnotes.md")

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
        existing_fetch = subprocess.run(["git", "config", "--get-all", "remote.origin.fetch"], capture_output=True, text=True).stdout
        if "refs/notes/agent/*:refs/notes/agent/*" not in existing_fetch:
            subprocess.check_call(["git", "config", "--add", "remote.origin.fetch", "+refs/notes/agent/*:refs/notes/agent/*"])
        
        # 2. Configure Push: Ensure standard heads AND agent notes are pushed
        existing_push = subprocess.run(["git", "config", "--get-all", "remote.origin.push"], capture_output=True, text=True).stdout
        if "refs/heads/*:refs/heads/*" not in existing_push:
            subprocess.check_call(["git", "config", "--add", "remote.origin.push", "refs/heads/*:refs/heads/*"])
        if "refs/notes/agent/*:refs/notes/agent/*" not in existing_push:
            subprocess.check_call(["git", "config", "--add", "remote.origin.push", "refs/notes/agent/*:refs/notes/agent/*"])
        
        # 3. Configure post-merge hook for automated feedback
        hooks_dir = Path(".git/hooks")
        if hooks_dir.exists():
            post_merge_hook = hooks_dir / "post-merge"
            hook_content = "#!/bin/sh\n\necho '🦞 Agent Notes Feedback:'\nagentnotes diff ORIG_HEAD --head HEAD --rich || true\n"
            post_merge_hook.write_text(hook_content)
            post_merge_hook.chmod(0o755)
            typer.echo("✅ Post-merge hook enabled: 'git pull' will now display new agent notes.")

        typer.echo("✅ Auto-sync (Fetch) enabled: 'git pull' will include agent notes.")
        typer.echo("✅ Auto-sync (Push) enabled: 'git push' will include agent notes and all branches.")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Error: {e}")

@app.command()
def stop_auto_sync():
    """
    Remove automatic fetch, push, and hook configurations for agent notes.
    """
    try:
        # Check if we are in a git repo
        subprocess.check_output(["git-rev-parse", "--is-inside-work-tree"], stderr=subprocess.STDOUT)
        
        # Unset refspecs
        subprocess.run(["git", "config", "--unset-all", "remote.origin.fetch", "refs/notes/agent/\\*"], check=False)
        subprocess.run(["git", "config", "--unset-all", "remote.origin.push", "refs/notes/agent/\\*"], check=False)
        
        # Remove hook
        post_merge_hook = Path(".git/hooks/post-merge")
        if post_merge_hook.exists():
            # Only remove if it's our hook
            if "🦞 Agent Notes" in post_merge_hook.read_text():
                post_merge_hook.unlink()
                typer.echo("✅ Post-merge hook disabled.")
        
        typer.echo("✅ Auto-sync disabled.")
    except Exception as e:
        typer.echo(f"❌ Error: {e}")

@app.command()
def onboard_openclaw():
    """
    Onboard the agentnotes skill to the local OpenClaw workspace.
    """
    workspace_skills_dir = Path("/home/codeninja/.openclaw/workspace/skills")
    if not workspace_skills_dir.exists():
        typer.echo("❌ Error: OpenClaw workspace skills directory not found at /home/codeninja/.openclaw/workspace/skills")
        return

    skill_target_dir = workspace_skills_dir / "agentnotes"
    skill_target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Create the OpenClaw SKILL.md
    project_root = Path(os.getcwd()).resolve()
    skill_content = f"""---
name: agentnotes
description: Persistent Agentic Memory via Git Notes. Use this to record implementation decisions, intent, and execution traces directly in the Git history.
---

# Agent Notes Skill

This skill allows you to record technical handovers and implementation reasoning directly in the Git history, distinct from commit messages.

## The Handover Philosophy
Agent Notes facilitate a continuous "chain of thought" across multiple agent sessions.
- **Commit Messages:** Summarize the code change for the human history.
- **Agent Notes:** Provide a high-density technical handover for the next agent in the chain.

## Usage
- **Handover:** Treat the 'decision' note as a brain-dump for the next agent. Explain the "why," the rejected paths, and the mental model used.
- **Context:** Use 'show_agent_notes' or 'agentnotes log' to load the technical handover from previous agents before starting.
- **Sync:** Use 'auto-sync' to ensure the chain of thought is never broken.

## Tools (CLI via shell)
- `agentnotes add "message" --type [decision|intent|trace|memory]`
- `agentnotes log`
- `agentnotes-dx auto-sync`

## Integration
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
