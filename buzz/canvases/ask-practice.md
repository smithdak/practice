# Ask Practice

Bring the exact point where useful work has stalled. You do not need a polished
solution; give another Practitioner enough context to suggest a next check,
experiment, or decision.

## Start with five short lines

```text
Outcome: …
Current approach: …
Constraint or failure risk: …
Tried so far: …
A useful reply would help me decide or test: …
```

Use a sanitized description when the real inputs are restricted. Never include
credentials, personal data, private keys, or client-confidential material.

## A helpful reply leaves something testable

- Restate the problem and surface a missing assumption.
- Suggest one bounded experiment, source, or decision rule.
- Name the failure mode or evidence that would change the recommendation.
- Route reusable work into the smallest suitable Git artifact.

Move to `learn`, `use`, `automate`, `build`, or `transform` once the next
outcome is clear. Use `showcase` only after there is an implementation or
result to inspect.

### Example (hypothetical)

> **Outcome:** reduce missed decisions in a weekly brief. **Current approach:**
> copy decisions manually from approved notes. **Constraint:** a person must
> verify every owner and date. **Tried:** a generated draft, but it omitted one
> decision. **Useful reply:** help me design a five-case check before choosing a
> tool.
