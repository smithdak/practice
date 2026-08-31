# Automate

Map first, automate second. Turn repeated work into a workflow whose trigger,
owners, checks, and recovery path remain visible.

## Map the current workflow

```text
Trigger and frequency: …
Steps and owners: …
Input and output: …
Decision requiring human approval: …
Likely failure and recovery: …
Observable success check: …
```

Label each step **deterministic**, **AI-suitable**, **human judgment**, or
**unsafe to automate**. Start with one reversible, low-risk step rather than
granting broad tool access.

### Example (hypothetical)

> A weekly intake starts when an approved form is submitted. A deterministic
> check verifies required fields; a model proposes a category; a person
> approves routing. If the proposal is uncertain, the item stays in the intake
> queue and the prior manual path remains available.

Move to `build` when implementation requires system architecture, code, or
observability. Move to `transform` when the main question is ownership,
governance, or organization-wide adoption. Use `use` for a one-off task.

Do not put secrets or production data in Buzz. Scheduled Buzz workflows remain
an experiment, not a launch dependency.
