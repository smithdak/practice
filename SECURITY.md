# Security policy

This repository holds documentation, templates, and small offline Python
utilities. It ships no service, stores no user data, and requires no
credentials to use. The security surface that matters here is therefore
narrower than for most repositories — and one part of it is unusual, so read
the second section even if you only skim the first.

## What to report

Please report any of the following:

- a script in `scripts/`, `tests/`, or `skills/` that could damage a
  contributor's working copy, execute untrusted input, or reach the network
  when it claims to run offline;
- a secret, private key, credential, or personal datum committed anywhere in
  this repository or its history;
- guidance in a Practice, Guide, Lab, or Story that would lead a reader to
  expose credentials, leak confidential material, or grant an agent more
  access than the text acknowledges;
- a workflow under `.github/workflows/` that could be made to run untrusted
  code with repository write access.

The last two are the ones people miss. A published method that quietly assumes
an agent has broad access is a security defect in this project, not merely an
editorial one.

## What is out of scope

- The absence of a hosted service, authentication, or transport security — this
  repository has none by design.
- Constraints of the Buzz platform itself, which are documented as accepted
  operating limits in
  [buzz/PLATFORM_SNAPSHOT.md](buzz/PLATFORM_SNAPSHOT.md) and
  [ops/BUZZ_SECURITY.md](ops/BUZZ_SECURITY.md). Messages, direct messages, and
  uploaded media there are not end-to-end encrypted, and community
  documentation says so; report a case where an artifact contradicts that, not
  the limit itself.
- A theoretical weakness with no path to harm for a reader or contributor.

## How to report

**Do not open a public issue for an unfixed problem**, and do not include
credentials or personal data in any report.

Practice is pre-launch and the named private reporting route is an open owner
decision recorded in [docs/OWNER_GATES.md](docs/OWNER_GATES.md); it has not been
established yet. Until it is published here:

1. Use GitHub's private vulnerability reporting on this repository if it is
   enabled (**Security → Report a vulnerability**).
2. Otherwise contact a named human maintainer through their published official
   contact method and say that the matter is a security report, exactly as the
   [Code of Conduct](CODE_OF_CONDUCT.md) directs for conduct reports.

A report made in good faith will not be penalized, and no fixed response time
is promised — urgency, severity, and available evidence vary, and this project
does not yet have staffed coverage.

## Handling

Reports are assessed by humans. Agents may summarize and route a report; they
do not decide severity, contact a reporter, or close a report. That boundary is
the same one the [moderation model](community/MODERATION.md) sets for conduct
concerns.

When a fix lands, the change and the class of problem are described publicly;
reporter identity and private evidence are not published without permission.
