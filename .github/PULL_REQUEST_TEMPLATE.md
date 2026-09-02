## Outcome

What becomes possible or clearer after this change? One or two sentences.

## Artifact type

Delete the ones that do not apply: Practice · Guide · Lab · Story · Note · Project · Community · Operations · Tooling

## Evidence

What was tested, observed, or sourced? Match the evidence to the claim — see the
[evidence table in CONTRIBUTING.md](../CONTRIBUTING.md#4-make-the-change-and-show-evidence).
For a current technical claim, give a primary-source URL and the date checked.

## Checks

- [ ] The change is scoped to one purpose; no unrelated cleanup rode along.
- [ ] Current claims carry a primary source and an as-of date.
- [ ] Examples, proposals, and hypotheticals are labeled; no outcome is invented.
- [ ] Licensing and attribution are correct for anything added or quoted.
- [ ] No secret, credential, personal datum, or confidential material is included.
- [ ] For a Story: the intake, consent, and redaction records are complete.
- [ ] For a method candidate: `maturity` and `evidence_quality` are unchanged unless a human maintainer recorded a promotion decision.

CI runs the unit tests, release validation, artifact schemas, skill-eval
definitions, and the link and as-of-date check. To run them locally:

```bash
python3 -m unittest discover -s tests
python3 scripts/validate.py --release
python3 scripts/validate_artifacts.py
python3 scripts/check_links.py
```

## Risks and follow-up

What could this get wrong, and what is deliberately left undone?
