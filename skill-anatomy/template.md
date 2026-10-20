# Skill Anatomy Template

Use this skeleton when creating a new skill. Replace all `{{placeholders}}` with actual content. Delete these instructions when done.

---

````markdown
---
name: {{kebab-case-name}}
description: >
  {{Trigger conditions ONLY. "Use when…", "Triggers when…"
  Do NOT summarize the process. Do NOT describe what the skill does.
  Focus on: what situation should cause this skill to activate?}}
---

# {{Skill Title}}

## Overview

{{2-4 sentences. What does this skill do? Not how — just what.
A reader who has never seen this skill should understand its purpose.
No jargon, no references to internal implementation.}}

## When to Use

- {{Concrete, observable condition 1}}
- {{Concrete, observable condition 2}}
- {{Concrete, observable condition 3}}
- {{Add more as needed — minimum 3}}

## Process

{{Describe the workflow as numbered steps or named phases.
Each step needs: an action + what must be true to advance.
Include a graphviz diagram for the flow.}}

```dot
digraph {{skill_name}} {
    "{{Step 1}}" [shape=box];
    "{{Checkpoint}}" [shape=diamond];
    "{{Step 2}}" [shape=box];
    "{{Done}}" [shape=doublecircle];

    "{{Step 1}}" -> "{{Checkpoint}}";
    "{{Checkpoint}}" -> "{{Step 2}}" [label="pass"];
    "{{Checkpoint}}" -> "{{Step 1}}" [label="fail, revise"];
    "{{Step 2}}" -> "{{Done}}";
}
```

### Step 1: {{Name}}

{{What to do.}}

**Exit criterion:** {{What must be true to advance.}}

### Step 2: {{Name}}

{{What to do.}}

**Exit criterion:** {{What must be true to advance.}}

### Step N: {{Name}}

{{Continue as needed.}}

## Rationalizations

| Rationalization | Reality |
|---|---|
| "This is too simple to need {{this process}}" | {{Specific rebuttal. Why simplicity doesn't excuse skipping.}} |
| "I'll do {{this step}} later" | {{Specific rebuttal. Why deferral fails.}} |
| "I already know how to {{do this}}" | {{Specific rebuttal. Why familiarity doesn't excuse the process.}} |
| "The user didn't ask for {{this level of detail}}" | {{Specific rebuttal. Why the standard exists regardless of user request.}} |
| {{Add domain-specific rationalizations}} | {{Specific rebuttals}} |

## Red Flags

- {{Observable symptom 1 — what goes WRONG, not what should go right}}
- {{Observable symptom 2}}
- {{Observable symptom 3}}
- {{Observable symptom 4 — minimum 4 entries}}

## Verification

- [ ] {{Concrete evidence 1 — file exists, output matches, test passes}}
- [ ] {{Concrete evidence 2}}
- [ ] {{Concrete evidence 3}}
- [ ] {{Concrete evidence 4 — minimum 4 items, no subjective criteria}}
````
