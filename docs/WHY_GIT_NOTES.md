# Why Git Notes for Agentic Memory?

Storing agentic memory (reasoning, traces, and intent) directly in a Git repository is a powerful pattern, but why use **Git Notes** instead of standard Markdown files or external databases?

## 1. Atomic Coupling (Zero Context Drift)
Standard documentation files (like `MEMORY.md`) are part of the working tree. If you revert a commit, the documentation reverts too. While this seems correct, the *reasoning* for why the code was in that reverted state is often lost or buried in diffs.
*   **The Git Notes Advantage:** Notes are attached to the **Commit Hash**. The memory is glued to the specific state of the code at that exact moment in time. Even as the branch evolves, the "soul" of that specific commit remains accessible.

## 2. Zero Collision & Noise
Agents working on the same repository often need to record high-frequency data (like tool-call traces). Storing this in Markdown files leads to constant merge collisions and clutters the `git log` with documentation updates that aren't actually code changes.
*   **The Git Notes Advantage:** Notes live in their own "shadow" refs (`refs/notes/agent/*`). They are invisible to standard `git status` and `git log` views. Agents can record detailed traces in the background without bothering the human developer.

## 3. Structured Multi-Agent Coordination
In a shared file, multi-agent coordination is messy. Agents have to parse and append to a single text document.
*   **The Git Notes Advantage:** We utilize Git's native namespacing. Different agents or different *types* of data (Decisions vs. Traces) live in separate namespaces. This allows for a structured audit trail that is easy for both humans and machines to filter.

## 4. Distributed Truth
External vector databases or state-management services require an internet connection and API keys. If an agent is working in a sandbox or offline, it loses its memory.
*   **The Git Notes Advantage:** The memory is **distributed with the code**. When you `git clone` a repository, you are cloning its memory. The repository becomes a self-contained, sovereign entity that carries its own history and reasoning wherever it goes.

## 5. Deterministic Retrieval
Agents often struggle with "needle in a haystack" problems when reading large context files.
*   **The Git Notes Advantage:** An agent can query specifically for the note attached to the current `HEAD`. It receives the exact context relevant to the code it is currently looking at—no more, no less. This minimizes hallucinations and keeps the context window clean.

---

*Git Notes turn your repository from a collection of snapshots into a living record of intent.*
