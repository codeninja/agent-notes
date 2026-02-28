# Agent Notes Skill
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
