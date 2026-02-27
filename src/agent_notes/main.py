import typer
from typing import Optional
import json
import os
from datetime import datetime
from pydantic import BaseModel, Field
from git import Repo, GitCommandError

app = typer.Typer(help="Agentic Memory via Git Notes")

class AgentNote(BaseModel):
    version: str = "1.0"
    agent_id: str
    type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
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

@app.command()
def add(
    message: str,
    type: str = typer.Option("decision", help="Note type (namespace)"),
    agent_id: str = typer.Option("unknown-agent", help="Identifier of the agent"),
    ref: str = typer.Option("HEAD", help="Git reference to attach note to"),
    data: Optional[str] = typer.Option(None, help="JSON string of structured data")
):
    """Add an agentic note to a commit."""
    repo = get_repo()
    note_data = AgentNote(
        agent_id=agent_id,
        type=type,
        message=message,
        data=json.loads(data) if data else None
    )
    
    note_json = note_data.model_dump_json()
    note_ref = get_note_ref(type)
    
    try:
        # GitPython doesn't have a direct notes wrapper, use git.execute
        repo.git.execute(["git", "notes", "--ref", note_ref, "add", "-m", note_json, ref])
        typer.echo(f"Successfully added {type} note to {ref}")
    except GitCommandError as e:
        typer.echo(f"Error adding note: {e}")
        raise typer.Exit(code=1)

@app.command()
def show(
    ref: str = typer.Argument("HEAD", help="Git reference to show notes for"),
    type: Optional[str] = typer.Option(None, help="Filter by note type"),
    all_agents: bool = typer.Option(False, "--all", help="Aggregate all agent notes")
):
    """Show agentic notes for a commit."""
    repo = get_repo()
    
    # Logic to list refs and fetch notes will go here
    # For now, a simple single-ref fetch
    types = [type] if type else ["decision", "trace", "memory", "intent"]
    
    found = False
    for t in types:
        note_ref = get_note_ref(t)
        try:
            content = repo.git.execute(["git", "notes", "--ref", note_ref, "show", ref])
            typer.echo(f"--- TYPE: {t} ---")
            typer.echo(content)
            found = True
        except GitCommandError:
            continue
            
    if not found:
        typer.echo(f"No agentic notes found for {ref}")

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

if __name__ == "__main__":
    app()
