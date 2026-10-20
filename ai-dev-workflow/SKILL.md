---
name: ai-dev-workflow
description: Use when starting any non-trivial development task, new feature, or significant bugfix. Orchestrates the complete workflow from idea to merge, coordinating grill-me, PRD, vertical slices, TDD, QA, and code review phases. Trigger when user says "new feature", "let's build", "implement", or starts a development task without a clear plan.
---

# AI Development Workflow

Orchestrates the complete development lifecycle. Each phase produces an artifact that feeds the next.

**Principle:** The fundamentals that work well with humans also work well with AI. This is NOT "specs to code" — it's continuous alignment and design.


## Assess Complexity

Before starting, determine the approach:

| Signal | Action |
|--------|--------|
| Clear requirements, < 30 min, single module | **Trivial** — use `/tdd` directly |
| Unclear requirements, multiple modules, architectural decisions | **Non-trivial** — full workflow |
| "I'm not sure how to..." or "what should we..." | **Non-trivial** — start at Phase 1 |

**When in doubt, start with Grill Me.** The cost of alignment is low; the cost of misalignment is high.

---

## Phase 1: Grill Me

**Goal:** Shared design concept between human and AI.

**Pre-requisite:** Clear context. Always start a fresh session.

**Action:** Invoke `/grill-me` with the brief or problem description.

- 40-100 questions, each with a recommendation
- Accept when recommendations make sense, correct when they don't
- The asset is the **conversation** (the shared understanding), not a document
- **Cannot be automated or skipped** — this is human-in-the-loop

**Exit:** You and the AI agree on what to build and how.

---

## Phase 2: PRD

**Goal:** Document the destination, not a contract.

**Action:** At the end of the Grill Me session, ask the AI to generate a PRD with this structure:

```
## Problem Statement
## Solution
## User Stories
## Implementation Decisions
## Testing Decisions
## Modules to Modify
```

**Rules:**
- Do NOT over-analyze — shared understanding already exists from Phase 1
- Verify the **Modules to Modify** section — this is the most important part
- LLMs summarize well. If Grill Me was thorough, the PRD will be accurate.

**Exit:** PRD exists. Modules make sense.

---

## Phase 3: Vertical Slice Issues

**Goal:** Parallelizable tasks that each cross ALL layers.

**Action:** Ask the AI to break the PRD into issues. Then **reject horizontal slices**:

```
REJECT (horizontal):              ACCEPT (vertical):
  Issue 1: All DB schemas           Issue 1: DB + API + UI for Feature A
  Issue 2: All API endpoints        Issue 2: DB + API + UI for Feature B
  Issue 3: All frontend             Issue 3: DB + API + UI for Feature C
```

**Each issue must:**
- Cross all layers (DB + API + Frontend minimum)
- Produce something **visible and testable** end-to-end
- Define blocking relationships to enable parallelization

```
[Issue 1] ──────────┐
                     ├──> [Issue 4]
[Issue 2] ──────────┤
         \          │
          └──> [Issue 3]
```

**Exit:** All issues are vertical slices with clear dependencies.

---

## Phase 4: Implementation (AFK)

**Goal:** AI implements autonomously using TDD. This is **Night Shift** — no supervision needed.

**For each issue:**
1. Explore the relevant code
2. `/tdd` — red-green-refactor, one test at a time
3. Run feedback loops: `test`, `type-check`, `lint`
4. Commit
5. Mark issue complete

**Priority order:**
1. Critical bug fixes
2. Development infrastructure
3. Tracer bullets (vertical slices)
4. Quick wins
5. Refactors

**Feedback loop quality = ceiling of AI code quality.** If output is bad, improve the loops, not the prompt.

**Exit:** All issues implemented with passing tests and commits.

---

## Phase 5: QA Manual

**Goal:** Impose human judgment and taste. **Cannot be automated.**

**Action:**
1. Test the feature in the real environment (golden path + edge cases)
2. Evaluate UX, visual coherence, business logic
3. Create **new issues** for problems found → feed back to Phase 3
4. Do NOT pass a feature without manual testing

**This is Day Shift** — the human decides what meets the bar.

**Exit:** Feature works correctly and meets your standards. New issues created if needed.

---

## Phase 6: Code Review (Clean Context)

**Goal:** Fresh eyes catch what the implementer missed.

**CRITICAL:** Clear context before review. The implementer consumed tokens and is in the **dumb zone**. A fresh reviewer operates in the **smart zone**.

**Action:**
1. Clear context / start new session
2. Pass the `git diff` + coding standards to the reviewer
3. Use a code review subagent or `/lda-core:requesting-code-review`
4. **Push approach:** coding standards are always present in review context

**Exit:** Code meets standards, reviewer approves.

---

## Phase 7: Merge

Standard merge. The work is done.

---

## Cross-Cutting Principles

| Principle | Why |
|-----------|-----|
| **Vertical slices over horizontal** | Get feedback from iteration 1, not iteration N |
| **TDD always** | Tests before code — AI can't cheat |
| **Clear > Compact** | Compacting accumulates sediment; clear resets to smart zone |
| **QA is manual** | Automated QA lacks human judgment on UX and business sense |
| **Review in clean context** | Fresh tokens = smart zone = more bugs found |
| **Feedback loops = quality ceiling** | Bad loops produce bad code regardless of prompt |
| **Deep modules** | Simple interface, deep implementation — AI navigates better, tests are clearer. Run `/improve-codebase-architecture` periodically |

## Context Management

- **Smart zone:** first ~100K tokens. Monitor consumption.
- **When approaching limit:** clear context, start fresh. Do NOT compact multiple times.
- Issues, PRD, and commits preserve context across sessions — clearing is safe.
- **Day Shift** (human present): Phases 1, 2, 3, 5 — planning, alignment, QA
- **Night Shift** (AI alone): Phases 4, 6 — implementation, automated review
