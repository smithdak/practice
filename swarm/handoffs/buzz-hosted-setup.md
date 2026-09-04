# buzz-hosted-setup Handoff

## Status

BLOCKED — hosted setup and owner-only pilot complete; unrestricted
member-triggered agents and public launch are not complete.

## Summary

Executed the owner's direct setup request. Recovered Buzz loading, configured
twelve streams and two supplemental forums, linked the repository/project,
tested a manual workflow, and verified Steward, Librarian, and Research Auditor
responses. Recorded the actual runtime boundary instead of representing
owner-only smoke tests as member-facing launch acceptance.

## Files changed

- `buzz/DEPLOYMENT_2026-09-04.md`
- `buzz/CHANNELS.md`
- `buzz/agents/registry.yaml` (status interpretation, not permission grants)
- `release/OWNER_REVIEW.md` (setup evidence, no invented blanket gate clearance)
- `swarm/handoffs/buzz-hosted-setup.md`

A private local access inventory was also created outside Git. It contains
identity references, sponsor, scopes, and review date; no credentials.

## Validation

- Actual relay and desktop inspections, event IDs, agent replies, and limits
  are retained in the deployment record.
- Steward readiness: all five checks passed on 2026-09-04.
- `python scripts/validate.py --release` with `PYTHONUTF8=1`: passed.
- `git diff --check`: passed (Windows line-ending notices only).
- No manifest task was assigned for this direct owner-operated setup;
  `--task buzz-hosted-setup` is not a valid manifest task. Use release validation;
  do not modify the manifest to manufacture task membership.

## Decisions made

- Use the owner's explicit setup approval without repeated permission loops.
- Keep forum root topics human-created and workflows unscheduled.
- Keep the three agent runtimes owner-only. Runtime `bypassPermissions` makes
  widening requests to untrusted members an unsafe workstation boundary.
- Preserve existing other-community runtimes and memberships.
- No Git push or public launch announcement.

## Risks or unresolved questions

The next technical boundary is an isolated, least-privilege agent runtime plus
a non-owner mention test. Current prompts and `bot` memberships do not enforce
read-only tools or file isolation. Computer Use cannot alter in-app security
settings under its safety rules; do not resolve this by toggling permission
bypass or exposing the current runtime to everyone.

Review access by 2026-09-11; expiry is an instruction, not automatic revocation.
Public launch still requires the specific evidence and human decisions in
`release/OWNER_REVIEW.md`. The setup receipt is a manual human acknowledgment,
not an activation command.

## Deferred opportunities

- Isolated member-facing agent host and tested tool allowlist.
- Human invitation/recovery/continuity and launch measurement evidence.
- Multi-person huddle verification, actual Sessions, and real contributor trials.
- Claim-level source links for the platform snapshot, as flagged by the auditor.
