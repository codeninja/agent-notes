import typer
from typing import Optional
import json
import os
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from git import Repo, GitCommandError

app = typer.Typer(
    help="Agentic Memory via Git Notes",
    no_args_is_help=True
)

class AgentNote(BaseModel):
    version: str = "1.0"
    agent_id: str
    type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: str
    data: Optional[dict] = None

def get_repo():
    try:
        return Repo(os.getcwd(), search_parent_directories=True)
    except Exception:
        typer.echo("Error: Not a git repository.")
        raise typer.Exit(code=1)

def get_note_ref(note_type: str):
    return f"refs/notes/agent/{note_type}"

def get_default_agent_id():
    return os.environ.get("AGENT_ID") or os.environ.get("USER") or "unknown-agent"

@app.command()
def add(
    message: str,
    type: str = typer.Option("decision", help="Note type (namespace)"),
    agent_id: str = typer.Option(None, help="Identifier of the agent (defaults to $AGENT_ID or $USER)"),
    ref: str = typer.Option("HEAD", help="Git reference to attach note to"),
    data: Optional[str] = typer.Option(None, help="JSON string of structured data"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing note"),
):
    """Add an agentic note to a commit."""
    repo = get_repo()
    
    # Resolve agent_id
    final_agent_id = agent_id or get_default_agent_id()
    
    note_data = AgentNote(
        agent_id=final_agent_id,
        type=type,
        message=message,
        data=json.loads(data) if data else None
    )
    
    note_json = note_data.model_dump_json()
    note_ref = get_note_ref(type)
    
    try:
        # GitPython doesn't have a direct notes wrapper, use git.execute
        args = ["git", "notes", "--ref", note_ref, "add", "-m", note_json]
        if force:
            args.append("-f")
        args.append(ref)
        repo.git.execute(args)
        typer.echo(f"Successfully added {type} note to {ref}")
    except GitCommandError as e:
        typer.echo(f"Error adding note: {e}")
        raise typer.Exit(code=1)

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

# ... (AgentNote class and existing helper functions) ...

def get_remote_url(repo):
    try:
        url = repo.remote().url
        if url.endswith(".git"):
            url = url[:-4]
        if url.startswith("git@github.com:"):
            url = url.replace("git@github.com:", "https://github.com/")
        return url
    except Exception:
        return None

@app.command()
def log(
    limit: int = typer.Option(20, help="Number of commits to check for notes"),
    ref: str = typer.Argument("HEAD", help="Git reference to start from"),
    type: Optional[str] = typer.Option(None, help="Filter by note type"),
    rich: bool = typer.Option(True, "--rich/--plain", help="Use Rich for beautiful output"),
):
    """Show agentic notes for the last N commits."""
    repo = get_repo()
    remote_url = get_remote_url(repo)
    
    try:
        commits = list(repo.iter_commits(ref, max_count=limit))
        
        if not commits:
            console.print(f"[yellow]No commits found starting from {ref}[/yellow]")
            return

        if rich:
            table = Table(title=f"Agentic Memory: Last {len(commits)} commits", box=box.ROUNDED, expand=True)
            table.add_column("Commit", style="cyan", no_wrap=True)
            table.add_column("Type", style="magenta")
            table.add_column("Agent", style="green")
            table.add_column("Message", style="italic")

            types = [type] if type else ["decision", "trace", "memory", "intent"]
            
            for commit in commits:
                commit_has_notes = False
                for t in types:
                    note_ref = get_note_ref(t)
                    try:
                        content = repo.git.execute(["git", "notes", "--ref", note_ref, "show", commit.hexsha])
                        note_data = json.loads(content)
                        
                        commit_display = commit.hexsha[:8]
                        if remote_url and "github.com" in remote_url:
                            link = f"{remote_url}/commit/{commit.hexsha}"
                            commit_display = f"[link={link}]{commit.hexsha[:8]}[/link]"

                        table.add_row(
                            commit_display,
                            t,
                            note_data.get("agent_id", "unknown"),
                            note_data.get("message", "")
                        )
                        commit_has_notes = True
                    except (GitCommandError, json.JSONDecodeError):
                        continue
                if commit_has_notes:
                    table.add_section()
            
            console.print(table)
        else:
            # Fallback to existing plain text logic
            typer.echo(f"--- Agentic Notes: Last {len(commits)} commits starting from {ref} ---")
            types = [type] if type else ["decision", "trace", "memory", "intent"]
            for commit in commits:
                commit_found = False
                for t in types:
                    note_ref = get_note_ref(t)
                    try:
                        content = repo.git.execute(["git", "notes", "--ref", note_ref, "show", commit.hexsha])
                        if not commit_found:
                            typer.echo(f"\nCOMMIT: {commit.hexsha[:8]}")
                            commit_found = True
                        typer.echo(f"  [{t}]: {content}")
                    except GitCommandError:
                        continue
    except GitCommandError as e:
        console.print(f"[red]Error reading log: {e}[/red]")
        raise typer.Exit(code=1)

@app.command()
def diff(
    base: str = typer.Argument("main", help="Base branch/ref to compare against"),
    head: str = typer.Option("HEAD", help="Head ref to compare from"),
    type: Optional[str] = typer.Option(None, help="Filter by note type"),
    rich: bool = typer.Option(True, "--rich/--plain", help="Use Rich for beautiful output"),
):
    """Show all agentic notes for commits between base and head."""
    repo = get_repo()
    remote_url = get_remote_url(repo)
    
    # Check if 'main' or 'master' should be used if default is requested
    if base == "main":
        try:
            repo.git.rev_parse("--verify", "main")
        except GitCommandError:
            base = "master"

    try:
        # Get list of commit hashes between base and head
        commits = list(repo.iter_commits(f"{base}..{head}"))
        
        if not commits:
            if rich:
                console.print(f"[yellow]No new commits found between {base} and {head}[/yellow]")
            else:
                typer.echo(f"No new commits found between {base} and {head}")
            return

        if rich:
            table = Table(title=f"Agentic Memory: {base}..{head}", box=box.ROUNDED, expand=True)
            table.add_column("Commit", style="cyan", no_wrap=True)
            table.add_column("Type", style="magenta")
            table.add_column("Agent", style="green")
            table.add_column("Message", style="italic")

            types = [type] if type else ["decision", "trace", "memory", "intent"]
            
            for commit in commits:
                commit_has_notes = False
                for t in types:
                    note_ref = get_note_ref(t)
                    try:
                        content = repo.git.execute(["git", "notes", "--ref", note_ref, "show", commit.hexsha])
                        note_data = json.loads(content)

                        commit_display = commit.hexsha[:8]
                        if remote_url and "github.com" in remote_url:
                            link = f"{remote_url}/commit/{commit.hexsha}"
                            commit_display = f"[link={link}]{commit.hexsha[:8]}[/link]"

                        table.add_row(
                            commit_display,
                            t,
                            note_data.get("agent_id", "unknown"),
                            note_data.get("message", "")
                        )
                        commit_has_notes = True
                    except (GitCommandError, json.JSONDecodeError):
                        continue
                if commit_has_notes:
                    table.add_section()
            
            console.print(table)
        else:
            typer.echo(f"--- Agentic Notes: {base}..{head} ({len(commits)} commits) ---")
            
            types = [type] if type else ["decision", "trace", "memory", "intent"]
            
            for commit in commits:
                commit_found = False
                for t in types:
                    note_ref = get_note_ref(t)
                    try:
                        content = repo.git.execute(["git", "notes", "--ref", note_ref, "show", commit.hexsha])
                        if not commit_found:
                            typer.echo(f"\nCOMMIT: {commit.hexsha[:8]}")
                            commit_found = True
                        typer.echo(f"  [{t}]: {content}")
                    except GitCommandError:
                        continue
                    
    except GitCommandError as e:
        if rich:
            console.print(f"[red]Error calculating diff: {e}[/red]")
        else:
            typer.echo(f"Error calculating diff: {e}")
        raise typer.Exit(code=1)

@app.command()
def show(
    ref: str = typer.Argument("HEAD", help="Git reference to show notes for"),
    type: Optional[str] = typer.Option(None, help="Filter by note type"),
    all_agents: bool = typer.Option(False, "--all", help="Aggregate all agent notes"),
    rich: bool = typer.Option(True, "--rich/--plain", help="Use Rich for beautiful output"),
):
    """Show agentic notes for a commit."""
    repo = get_repo()
    types = [type] if type else ["decision", "trace", "memory", "intent"]
    
    found = False
    for t in types:
        note_ref = get_note_ref(t)
        try:
            content = repo.git.execute(["git", "notes", "--ref", note_ref, "show", ref])
            if rich:
                try:
                    note_data = json.loads(content)
                    console.print(Panel(
                        f"[bold green]Message:[/bold green] {note_data.get('message')}\n"
                        f"[bold magenta]Agent:[/bold magenta] {note_data.get('agent_id')}\n"
                        f"[bold blue]Time:[/bold blue] {note_data.get('timestamp')}",
                        title=f"Agent Note: {t}",
                        subtitle=f"Ref: {ref}",
                        box=box.ROUNDED
                    ))
                except json.JSONDecodeError:
                    typer.echo(f"--- TYPE: {t} ---")
                    typer.echo(content)
            else:
                typer.echo(f"--- TYPE: {t} ---")
                typer.echo(content)
            found = True
        except GitCommandError:
            continue
            
    if not found:
        console.print(f"[yellow]No agentic notes found for {ref}[/yellow]")

@app.command()
def sync():
    """Sync agentic notes with remote origin."""
    repo = get_repo()
    try:
        typer.echo("Fetching agent notes...")
        repo.git.execute(["git", "fetch", "origin", "refs/notes/agent/*:refs/notes/agent/*"])
        typer.echo("Pushing agent notes...")
        repo.git.execute(["git", "push", "origin", "refs/notes/agent/*"])
        typer.echo("Sync complete.")
    except GitCommandError as e:
        typer.echo(f"Sync failed: {e}")

@app.command()
def mcp():
    """Run the FastMCP server."""
    from .mcp import mcp as mcp_server
    mcp_server.run()

if __name__ == "__main__":
    app()
