# My Claude Code Skills

## Diagrams & Visualization
- **archify** — HTML architecture/workflow diagrams with dark/light themes
- **diagram-design** — branded diagrams as HTML/SVG/PNG
- **excalidraw-diagram** — Excalidraw JSON diagrams
- **visualize** — inline Obsidian diagrams for lessons
- **tldraw-offline** — operate the tldraw offline canvas app: inspect and edit open `.tldraw` files, draw diagrams from Mermaid, add board scripts (installed by the app, see Preferred Apps)

## Documents & Presentations
- **html-slides** — self-contained HTML slide decks with edit mode and print-to-PDF

## Planning & Design
- **grill-me** — stress-test a plan via relentless interview
- **grill-with-docs** — grill against domain model + update docs inline
- **idea-refine** — divergent/convergent idea refinement

## Development Workflow
- **ai-dev-workflow** — full workflow: idea → grill → PRD → vertical slices → TDD → QA → review → merge
- **git-workflow-and-versioning** — git branching and commit practices
- **tdd** — test-driven development (red-green-refactor)

## Code Quality
- **debugging-and-error-recovery** — systematic root-cause debugging
- **improve-codebase-architecture** — find refactoring opportunities

## Teaching
- **learn** — AI tutor: probes understanding, teaches step by step

## Domain-Specific
- **pinokio** — Pinokio app runtime discovery

## Meta
- **skill-anatomy** — validate skill structure (Overview, When to Use, etc.)

## Preferred Apps
- **[tldraw offline](https://github.com/tldraw/tldraw-offline)** — desktop whiteboard on tldraw's infinite canvas, saved as local `.tldraw` files with no account or server. Connected to Claude Code through the app's own menu: **Install Agent Skills** adds the `tldraw-offline` skill and subagent. The app must be running with a file open; Claude talks to its local HTTP API with a per-launch token. Only open `.tldraw` files you trust, since they can embed scripts that run on open.
