---
name: skill-anatomy
description: >
  Validates that skills follow the required anatomy (Overview, When to Use, Process,
  Rationalizations, Red Flags, Verification). Use when creating a new skill, reviewing
  an existing skill's structure, or when another skill-creation tool is active and the
  output needs structural validation. Also triggers when editing a SKILL.md file.
---

# Skill Anatomy

## Overview

Every skill lives in `skills/<skill-name>/SKILL.md`. This skill enforces the standard anatomy: six mandatory sections beyond the frontmatter, each with a specific purpose and format. Consistent structure makes skills discoverable, followable, and auditable by agents.

This skill does NOT cover frontmatter field details, variable substitutions, or invocation control — those belong to `lda-core:create-skill`. This skill owns the **content structure** of SKILL.md.

## When to Use

- When creating a new skill (before or after writing the frontmatter)
- When reviewing an existing skill's SKILL.md for structural completeness
- When another skill-creation tool produced output that needs anatomy validation
- When editing any SKILL.md file

## File Location

Every skill lives in its own directory under `skills/`:

```
skills/
  skill-name/
    SKILL.md           # Required: The skill definition
    supporting-file.md # Optional: Reference material loaded on demand
```

## The Anatomy

Every SKILL.md must contain these sections in order:

```
┌─────────────────────────────────────────────────┐
│  SKILL.md                                       │
│                                                 │
│  ┌─ Frontmatter ─────────────────────────────┐  │
│  │ name: lowercase-hyphen-name               │  │
│  │ description: Guides agents through [task].│  │
│  │              Use when…                    │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  Overview         → What this skill does        │
│  When to Use      → Triggering conditions       │
│  Process          → Step-by-step workflow        │
│  Rationalizations → Excuses + rebuttals          │
│  Red Flags        → Signs something's wrong      │
│  Verification     → Evidence requirements        │
└─────────────────────────────────────────────────┘
```

### SKILL.md Format

````markdown
---
name: skill-name-with-hyphens
description: Guides agents through [task/workflow]. Use when [specific trigger conditions].
---

# Skill Title

## Overview
One-two sentences explaining what this skill does and why it matters.

## When to Use
- Bullet list of triggering conditions (symptoms, task types)
- When NOT to use (exclusions)

## [Core Process / The Workflow / Steps]
The main workflow, broken into numbered steps or phases.
Include code examples where they help.
Use flowcharts (ASCII) where decision points exist.

## [Specific Techniques / Patterns]
Detailed guidance for specific scenarios.

## Common Rationalizations
| Rationalization | Reality |
|---|---|
| Excuse agents use to skip steps | Why the excuse is wrong |

## Red Flags
- Behavioral patterns indicating the skill is being violated

## Verification
- [ ] Checklist of exit criteria
````

## Process

Follow these phases sequentially. Each has a hard-gate: do NOT advance until the section passes.

### Phase 1: Validate Frontmatter

**Criteria:**
- `name` is lowercase kebab-case, matches the folder name
- `description` contains ONLY triggering conditions ("Use when…", "Triggers when…")
- `description` does NOT summarize the skill's process or workflow
- `description` is specific enough that Claude can decide whether to invoke it

**Good** (`test-driven-development`):
```yaml
description: Drives development with tests. Use when implementing any logic, fixing any
  bug, or changing any behavior. Use when you need to prove that code works.
```

**Bad:**
```yaml
description: Walks through the red-green-refactor cycle: write a test, write code, clean up.
```

**Hard-gate:** If description contains process summaries, rewrite to focus on triggers before proceeding.

---

### Phase 2: Validate Overview

The "elevator pitch" for the skill. Answers: *What does this skill do, and why should an agent follow it?*

**Criteria:**
- 2-4 sentences maximum
- Says WHAT the skill does, not HOW it does it
- A reader who has never seen the skill can understand its purpose

**Good** (`test-driven-development`):
> Write a failing test before writing the code that makes it pass. For bug fixes, reproduce the bug with a test before attempting a fix. Tests are proof — "seems right" is not done.

**Bad:**
> This skill walks you through writing a test, then writing minimal code to pass it, then refactoring while keeping tests green.

**Hard-gate:** If the overview exceeds 4 sentences or describes the process, rewrite it.

---

### Phase 3: Validate When to Use

Helps agents and humans decide if this skill applies. Include positive triggers AND exclusions.

**Criteria:**
- Bulleted list of concrete, observable conditions
- Each condition describes a situation the agent can detect, not a vague intent
- No entries like "when appropriate", "when needed"
- Minimum 3 triggering conditions

**Good** (`test-driven-development`):
```markdown
## When to Use
- Implementing any new logic or behavior
- Fixing any bug (the Prove-It Pattern)
- Modifying existing functionality

**When NOT to use:** Pure configuration changes, documentation updates.
```

**Bad:**
```markdown
## When to Use
- When it makes sense
- When needed
```

**Hard-gate:** If any condition is vague or unobservable, rewrite it to be specific.

---

### Phase 4: Validate Process

The heart of the skill. Must be a workflow, not prose.

**Criteria:**
- Numbered steps or named phases
- Each step has a clear action AND an exit criterion (what must be true to advance)
- Includes a flow diagram (ASCII or graphviz dot)
- Steps are ordered — dependencies between steps are explicit

**Good — ASCII flow diagram** (`test-driven-development`):
```
    RED                GREEN              REFACTOR
 Write a test    Write minimal code    Clean up the
 that fails  ──→  to make it pass  ──→  implementation  ──→  (repeat)
      │                  │                    │
      ▼                  ▼                    ▼
   Test FAILS        Test PASSES         Tests still PASS
```

**Good vs Bad steps:**
- **Good:** "Run `pytest` and verify all tests pass before advancing."
- **Bad:** "Make sure the tests work."

**Hard-gate:** If any step lacks an exit criterion, or if there is no flow diagram, fix it before proceeding.

---

### Phase 5: Validate Rationalizations

The anti-skip table. Prevents agents from rationalizing their way out of following the skill.

**Criteria:**
- Table format: `| Rationalization | Reality |`
- Minimum 4 rows
- Each "Reality" must be a direct, specific rebuttal — not a generic "but you should do it anyway"

**Good** (`test-driven-development`):
| Rationalization | Reality |
|---|---|
| "I'll write tests after the code works" | You won't. And tests written after the fact test implementation, not behavior. |
| "This is too simple to test" | Simple code gets complicated. The test documents the expected behavior. |

**Hard-gate:** If fewer than 4 rows, or any rebuttal is generic, expand the table.

---

### Phase 6: Validate Red Flags

Observable signs the skill is not being followed — visible from outside the process.

**Criteria:**
- Bulleted list, minimum 4 entries
- Each flag is an observable symptom, not a restatement of a process step
- Flags describe what goes WRONG, not what should go right

**Good** (`test-driven-development`):
> - Bug fixes without reproduction tests
> - Tests that pass on the first run (they may not be testing what you think)
> - "All tests pass" but no tests were actually run

**Bad** (negated steps, not symptoms):
> - Didn't write tests first
> - Skipped the refactor phase

**Hard-gate:** If fewer than 4 flags, or flags are just negated process steps, rewrite as observable symptoms.

---

### Phase 7: Validate Verification

Evidence requirements that prove the skill was followed correctly.

**Criteria:**
- Checklist format (`- [ ]`)
- Each item requires observable evidence (file exists, output matches, test passes)
- No items that rely on subjective judgment
- Minimum 4 verification items

**Good** (`test-driven-development`):
```markdown
- [ ] Every new behavior has a corresponding test
- [ ] All tests pass: `pytest`
- [ ] Bug fixes include a reproduction test that failed before the fix
- [ ] No tests were skipped or disabled
```

**Hard-gate:** If any item is subjective or unverifiable, replace it with a concrete check.

---

### Phase 8: Final Audit

- [ ] SKILL.md is under 500 lines
- [ ] All supporting files referenced via relative markdown links (not inlined)
- [ ] No section is empty or contains only placeholder text
- [ ] Sections appear in canonical order (Overview → When to Use → Process → Rationalizations → Red Flags → Verification)
- [ ] The skill reads as a workflow an agent follows, not a reference document it consults

If the SKILL.md exceeds 500 lines, extract detailed reference material into supporting files (`references/`, `examples/`) and link to them.

## Supporting Files

Create supporting files only when:
- Reference material exceeds 100 lines (keep the main SKILL.md focused)
- Code tools or scripts are needed
- Checklists are long enough to justify separate files

Keep patterns and principles inline when under 50 lines.

## Writing Principles

1. **Process over knowledge.** Skills are workflows, not reference docs. Steps, not facts.
2. **Specific over general.** "Run `npm test`" beats "verify the tests".
3. **Evidence over assumption.** Every verification checkbox requires proof.
4. **Anti-rationalization.** Every skip-worthy step needs a counter-argument in the rationalizations table.
5. **Progressive disclosure.** Main SKILL.md is the entry point. Supporting files are loaded only when needed.
6. **Token-conscious.** Every section must justify its inclusion. If removing it wouldn't change agent behavior, remove it.

## Naming Conventions

- Skill directories: `lowercase-hyphen-separated`
- Skill files: `SKILL.md` (always uppercase)
- Supporting files: `lowercase-hyphen-separated.md`
- References: stored in `references/` at the project root, not inside skill directories

## Cross-Skill References

Reference other skills by name — do NOT duplicate content between skills:

```markdown
Follow the `test-driven-development` skill for writing tests.
If the build breaks, use the `debugging-and-error-recovery` skill.
```

## Template

For a complete skeleton with placeholders, see [template.md](template.md).

## Reference: A Good Skill in Practice

`test-driven-development` is a canonical example. Each piece of its anatomy is shown below.

**Frontmatter** — solo condiciones de activación, sin describir el proceso:
```yaml
name: test-driven-development
description: Drives development with tests. Use when implementing any logic, fixing
  any bug, or changing any behavior. Use when you need to prove that code works,
  when a bug report arrives, or when you're about to modify existing functionality.
```

**Overview** — qué hace la skill, no cómo:
> Write a failing test before writing the code that makes it pass. For bug fixes, reproduce the bug with a test before attempting a fix. Tests are proof — "seems right" is not done.

**When to Use** — condiciones observables + exclusión explícita:
```markdown
- Implementing any new logic or behavior
- Fixing any bug (the Prove-It Pattern)
- Modifying existing functionality

**When NOT to use:** Pure configuration changes, documentation updates.
```

**Process** — diagrama de flujo + pasos con criterio de salida:
```
    RED                GREEN              REFACTOR
 Write a test    Write minimal code    Clean up the
 that fails  ──→  to make it pass  ──→  implementation  ──→  (repeat)
```

**Rationalizations** — rebatir excusas concretas, no genéricas:
| Rationalization | Reality |
|---|---|
| "I'll write tests after the code works" | You won't. Tests written after test implementation, not behavior. |
| "This is too simple to test" | Simple code gets complicated. The test documents expected behavior. |

**Red Flags** — síntomas observables desde fuera del proceso:
```
- Bug fixes without reproduction tests
- Tests that pass on the first run (may not be testing what you think)
- "All tests pass" but no tests were actually run
```

**Verification** — evidencia concreta, sin criterios subjetivos:
```markdown
- [ ] Every new behavior has a corresponding test
- [ ] All tests pass: `pytest`
- [ ] Bug fixes include a reproduction test that failed before the fix
- [ ] No tests were skipped or disabled
```

---

## Rationalizations

| Rationalization | Reality |
|---|---|
| "This skill is too simple to need Rationalizations and Red Flags" | Simple skills are where agents skip steps most often. The simpler the skill, the more tempting it is to shortcut — which is exactly why anti-skip sections exist. |
| "I'll add the Verification section later" | Later never comes. A skill without verification is a suggestion, not a standard. Write it now. |
| "The Process section is obvious, I don't need a diagram" | If the process is obvious, the diagram takes 30 seconds to write. If it's not obvious, the diagram is essential. Either way, write it. |
| "Red Flags are just the inverse of the Process steps" | Red Flags describe observable symptoms from outside the process, not negations of steps. "Didn't validate input" is a negated step. "API crashes on empty strings in production" is a red flag. |
| "The user just wants the skill written quickly" | A skill without structure gets ignored or followed inconsistently. Spending 5 extra minutes on anatomy saves hours of debugging malformed skill output later. |
| "I know the anatomy by heart, I don't need this validator" | Knowing the structure and following it under pressure are different things. The validator exists precisely for when you're confident you don't need it. |

## Red Flags

- A SKILL.md that jumps straight into instructions without an Overview or When to Use section
- Process section written as prose paragraphs instead of numbered steps with exit criteria
- No Rationalizations table, or a table with only 1-2 generic entries
- Red Flags section that just negates process steps ("didn't do step 3") instead of describing symptoms
- Verification section with subjective criteria ("code looks clean", "seems complete")
- SKILL.md over 500 lines with no supporting files extracted
- Overview section that describes the full process instead of summarizing purpose
- Description field in frontmatter that summarizes the workflow instead of listing triggers
- Missing flow diagram in a process-oriented skill
- "See Also" or "References" sections that link to nonexistent files

## Verification

After using this skill, verify:

- [ ] SKILL.md contains all 6 mandatory sections in canonical order
- [ ] Frontmatter `description` contains only trigger conditions, no process summaries
- [ ] Overview is 2-4 sentences describing WHAT, not HOW
- [ ] When to Use has minimum 3 concrete, observable conditions
- [ ] Process has numbered steps, each with exit criteria, and includes a flow diagram
- [ ] Rationalizations table has minimum 4 rows with specific rebuttals
- [ ] Red Flags list has minimum 4 observable symptoms
- [ ] Verification checklist has minimum 4 items with concrete evidence requirements
- [ ] SKILL.md is under 500 lines total
- [ ] Supporting files (if any) are referenced via relative markdown links
