---
name: tdd
description: Test-driven development with red-green-refactor loop. Use when implementing any logic, fixing any bug, writing a new feature, or when the user mentions "red-green-refactor", "test first", or wants integration tests.
---

# Test-Driven Development

## Overview

Write a failing test before writing the code that makes it pass. Tests verify behavior through public interfaces, not implementation details — code can change entirely, tests shouldn't. For bug fixes, reproduce the bug with a test before attempting a fix. Tests are proof — "seems right" is not done. A codebase with good tests is an AI agent's superpower; a codebase without tests is a liability.

## When to Use

- Implementing any new logic or behavior
- Fixing any bug (Prove-It Pattern: reproduce before fixing)
- Modifying existing functionality that could break behavior
- Adding edge case handling to existing code
- Any change where you need to prove correctness, not just assume it

**When NOT to use:** Pure configuration changes, documentation updates, or static content changes with no behavioral impact.

## Process

```
Input received
      │
      ▼
Bug fix? ──Yes──→ Prove-It Pattern (Step 3)
      │
      No
      ▼
Clarify interface & behaviors (Step 1: Planning)
      │
      ▼
Tracer Bullet — first test (Step 2)
      │
      ▼
RED → GREEN loop, one behavior at a time (Step 2)
      │
      ▼
All behaviors covered? ──No──→ Next behavior
      │
      Yes
      ▼
Refactor (Step 4)
      │
      ▼
Done
```

### Step 1 — Planning

Before writing any test:

- [ ] Confirm what interface changes are needed (public API only — no private methods)
- [ ] List behaviors to verify — not implementation steps, behaviors
- [ ] Prioritize: critical paths and complex logic first
- [ ] Get user approval on the list

Ask: "What should the public interface look like? Which behaviors matter most?"

**You can't test everything.** Focus testing effort on critical paths, not every edge case.

**Exit:** Agreed list of prioritized behaviors to verify.

---

### Step 2 — RED → GREEN Loop

Write ONE test, make it pass, repeat:

```
RED:   Write test for one behavior → it FAILS (expected)
GREEN: Write minimal code to pass  → it PASSES

Repeat for each remaining behavior.
```

Rules:
- One test at a time
- Only enough code to pass the current test
- Don't anticipate future tests
- Test behavior (what), not implementation (how)

The first test is your **tracer bullet** — it proves the harness works and the path is wired end-to-end.

**Exit:** All behaviors from the plan have a passing test.

---

### Step 3 — Prove-It Pattern (Bug Fixes)

When a bug arrives, do NOT fix first:

```
Bug report arrives
      │
      ▼
Write a test that reproduces the bug
      │
      ▼
Test FAILS → bug confirmed
      │
      ▼
Implement the fix
      │
      ▼
Test PASSES → fix verified
      │
      ▼
Run full suite → no regressions
```

**Exit:** Reproduction test passes. Full suite green.

---

### Step 4 — Refactor

After all tests pass:

- [ ] Extract duplication
- [ ] Deepen modules (move complexity behind simple interfaces)
- [ ] Improve naming
- [ ] Run tests after every refactor step

**Never refactor while RED.** Get to GREEN first, then clean.

**Exit:** Tests still pass. Code is cleaner than before.

## Writing Good Tests

### Test State, Not Interactions

Assert on outcomes, not on which internal methods were called:

```python
# Good: tests what the function does (state-based)
def test_returns_tasks_sorted_newest_first():
    tasks = list_tasks(sort_by="created_at", sort_order="desc")
    assert tasks[0].created_at > tasks[1].created_at

# Bad: tests how it works internally (interaction-based)
def test_calls_db_with_order_by():
    list_tasks(sort_by="created_at", sort_order="desc")
    mock_db.query.assert_called_with(...)  # breaks on refactor, not on behavior change
```

### DAMP Over DRY

In tests, **Descriptive And Meaningful Phrases** beats DRY. Each test should tell a complete story without tracing through shared helpers:

```python
# Good: self-contained and readable
def test_rejects_tasks_with_empty_titles():
    with pytest.raises(ValueError, match="Title is required"):
        create_task(title="", assignee="user-1")

def test_trims_whitespace_from_titles():
    task = create_task(title="  Buy groceries  ", assignee="user-1")
    assert task.title == "Buy groceries"
```

Duplication in tests is acceptable when it makes each test independently understandable.

### Arrange-Act-Assert

```python
def test_marks_overdue_tasks_when_deadline_passed():
    # Arrange
    task = create_task(title="Test", deadline=date(2025, 1, 1))
    # Act
    result = check_overdue(task, reference_date=date(2025, 1, 2))
    # Assert
    assert result.is_overdue is True
```

### Prefer Real Implementations Over Mocks

```
Preference order (most to least preferred):
1. Real implementation  → highest confidence, catches real bugs
2. Fake                 → in-memory version of a dependency (e.g. fake DB)
3. Stub                 → returns canned data, no behavior
4. Mock                 → verifies method calls — use sparingly
```

Use mocks only when the real implementation is too slow, non-deterministic, or has uncontrollable side effects (external APIs, email sending). Over-mocking creates tests that pass while production breaks.

### Test Pyramid

Invest testing effort according to the pyramid:

```
        ╱╲
       ╱  ╲        E2E (~5%)
      ╱    ╲       Full user flows, real browser
     ╱──────╲
    ╱        ╲     Integration (~15%)
   ╱          ╲    Component interactions, API boundaries
  ╱────────────╲
 ╱              ╲  Unit (~80%)
╱                ╲ Pure logic, isolated, milliseconds each
╲────────────────╱
```

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll write tests after the code works" | You won't. Tests written after the fact test implementation, not behavior. |
| "This is too simple to test" | Simple code gets complicated. The test documents expected behavior and catches future regressions. |
| "Tests slow me down" | Tests slow you down now. They speed up every future change to that code. |
| "I tested it manually" | Manual tests don't persist. Tomorrow's change can break it silently with no way to know. |
| "It's a bug fix, I don't need a test" | Bug fixes without reproduction tests reappear. The test proves the fix works and guards against regression. |
| "The code is self-explanatory" | Tests ARE the specification. They document what the code should do, not just what it does. |

## Red Flags

- Writing code without a corresponding test
- Tests that pass on the first run without any implementation (may not be testing what you think)
- Bug fixes without a reproduction test that failed before the fix
- Tests that break when you rename an internal function — coupled to implementation, not behavior
- "All tests pass" but no tests were actually run
- Mocking internal collaborators instead of testing through the public interface
- Test names that don't describe the expected behavior ("test_works", "test_3")
- Skipping tests to make the suite pass

## Verification

After completing any implementation:

- [ ] Every new behavior has a corresponding test
- [ ] All tests pass
- [ ] Bug fixes include a reproduction test that failed before the fix
- [ ] Tests use the public interface only — no private method access
- [ ] Test names describe the behavior being verified
- [ ] No tests were skipped or disabled
- [ ] Mock usage is limited to external boundaries (APIs, email, slow deps)
