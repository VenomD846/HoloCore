# Codex Knowledge Retrieval Workflow

## Purpose

Use Graphify, MemPalace, and the Obsidian second brain to reduce unnecessary context while preserving relevant project knowledge.

## Source roles

- **Obsidian:** curated durable knowledge, architecture decisions, constraints, and project guidance.
- **MemPalace:** episodic history, previous attempts, debugging context, and conversation memory.
- **Graphify:** local code structure, symbols, dependencies, and file relationships.
- **Project files:** exact implementation details, read only after targeted retrieval identifies what matters.

## Relevance gates

Do not query every source for every task.

- Use Obsidian for architecture, project context, or documented decisions.
- Use MemPalace when continuing earlier work or investigating a previous decision, error, or attempt.
- Use Graphify for repository tasks involving structure, dependencies, or relationships.
- Skip MemPalace and Graphify for simple isolated edits unless the task explicitly needs them.

## Retrieval order

When multiple sources are relevant:

1. Check `C:\Cursor projects\Second Brain Obsidian\Second Brain\system\index.md`.
2. Follow only relevant linked Obsidian notes.
3. Query MemPalace within the current project wing or room.
4. Check or update the project's Graphify graph with local AST-only processing.
5. Read only the project files needed to verify the answer or make the change.

## Automatic maintenance

For meaningful project work:

```powershell
graphify update "<project-root>"
mempalace mine "<project-root>" --wing <project-name>
```

Use `--force` for Graphify only after files were deleted or renamed. Run `mempalace sync` when source files are deleted, moved, or gitignored.

Promote only verified, durable, reusable knowledge into atomic Obsidian notes. Update an existing note before creating a duplicate. Do not ingest uncertain claims or routine maintenance summaries.

## Expected benefit

The workflow reduces model context by selecting relevant notes, memories, graph relationships, and source files instead of sending an entire repository or conversation history. Measure it using input tokens, files read, retrieval latency, answer accuracy, and repeated-work rate.
