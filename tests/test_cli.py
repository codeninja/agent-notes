import os
import json
import pytest
from pathlib import Path
from git import Repo
from typer.testing import CliRunner
from agent_notes.main import app
from agent_notes.dx import app as dx_app

runner = CliRunner()

@pytest.fixture
def temp_repo(tmp_path):
    """Create a temporary git repository for testing."""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    repo = Repo.init(repo_path)
    
    # Create a dummy file and commit it
    dummy_file = repo_path / "dummy.txt"
    dummy_file.write_text("hello")
    repo.index.add([str(dummy_file)])
    repo.index.commit("Initial commit")
    
    # Change to the repo directory
    old_cwd = os.getcwd()
    os.chdir(repo_path)
    yield repo_path
    os.chdir(old_cwd)

def test_add_note(temp_repo):
    """Test adding an agent note."""
    result = runner.invoke(app, ["add", "Test decision message", "--agent-id", "test-agent"])
    assert result.exit_code == 0
    assert "Successfully added decision note" in result.output

    # Verify note content
    result_show = runner.invoke(app, ["show", "HEAD", "--plain"])
    assert "Test decision message" in result_show.output
    assert "test-agent" in result_show.output

def test_add_note_force(temp_repo):
    """Test overwriting a note with --force."""
    runner.invoke(app, ["add", "First note"])
    
    # Attempting to add without force should fail
    result_fail = runner.invoke(app, ["add", "Second note"])
    assert result_fail.exit_code != 0
    
    # Adding with force should succeed
    result_success = runner.invoke(app, ["add", "Second note", "--force"])
    assert result_success.exit_code == 0
    
    result_show = runner.invoke(app, ["show", "HEAD", "--plain"])
    assert "Second note" in result_show.output

def test_log_notes(temp_repo):
    """Test viewing the log of notes."""
    # Add notes to two different commits
    runner.invoke(app, ["add", "Note 1"])
    
    # New commit
    repo = Repo(temp_repo)
    (temp_repo / "new.txt").write_text("new")
    repo.index.add(["new.txt"])
    repo.index.commit("Second commit")
    
    runner.invoke(app, ["add", "Note 2"])
    
    result = runner.invoke(app, ["log", "--limit", "2", "--plain"])
    assert result.exit_code == 0
    assert "Note 1" in result.output
    assert "Note 2" in result.output

def test_dx_init_project(temp_repo):
    """Test DX project initialization."""
    result = runner.invoke(dx_app, ["init-project"])
    assert result.exit_code == 0
    
    skill_file = temp_repo / ".claude" / "skills" / "agent-notes.md"
    assert skill_file.exists()
    assert "Agent Notes Skill" in skill_file.read_text()

def test_dx_auto_sync_config(temp_repo):
    """Test that auto-sync correctly modifies git config."""
    # We need to add a remote to test sync config
    repo = Repo(temp_repo)
    repo.create_remote("origin", "https://github.com/example/repo.git")
    
    result = runner.invoke(dx_app, ["auto-sync"])
    assert result.exit_code == 0
    
    config = repo.config_reader()
    
    # Check fetch refspec
    fetch_val = config.get_value('remote "origin"', "fetch")
    # get_value without all_items might return last one, let's just check the whole config string
    config_str = (temp_repo / ".git" / "config").read_text()
    assert "refs/notes/agent/*" in config_str
    
    # Check push refspec
    assert "refs/heads/*:refs/heads/*" in config_str
    assert "refs/notes/agent/*:refs/notes/agent/*" in config_str
