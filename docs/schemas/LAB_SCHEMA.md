# Lab Schema

## Outcome

A Lab is a reproducible experiment or evaluation that answers one bounded question. It records the conditions, task set, scoring, costs, results, and limits needed for another Practitioner to inspect or repeat it. Use this schema with [the Lab template](../../templates/LAB.md).

A Lab measures the completion quality of the stated task set. It does not establish a general ranking of models, people, tools, or organizations.

## Canonical metadata

Every Lab begins with YAML front matter. Field names and controlled values are case-sensitive.

| Field | Required | Rule |
|---|---|---|
| `artifact_type` | Yes | Must be `lab`. |
| `title` | Yes | Non-empty, human-readable experiment title. |
| `summary` | Yes | Non-empty plain-language description of the question and bounded task; not an unsupported finding. |
| `status` | Yes | One of `proposed`, `running`, `completed`, or `deprecated`. |
| `primary_capability` | Yes | One of `learn`, `use`, `automate`, `build`, or `transform`; select the Lab's direct learning outcome. |
| `roles` | Yes | A non-empty list of controlled role values below. |
| `task_set_version` | Yes | Semantic version for the frozen task set, such as `0.1.0`. Increment it for any material task or scoring change. |
| `run_count` | Yes | Non-negative integer count of included runs. A run is one candidate configuration on one task for one trial. |
| `result_status` | Yes | One of `not-run`, `partial`, `complete`, or `invalidated`. It describes the evidence record, separately from publication status. |
| `last_run` | Yes | `null` only when `result_status` is `not-run`; otherwise an ISO date in `YYYY-MM-DD` form. |
| `version` | Yes | Semantic version for the Lab document, such as `0.1.0`. |
| `license` | Yes | `CC-BY-4.0`, the default content license. |
| `created` | Yes | ISO date in `YYYY-MM-DD` form. |
| `updated` | Yes | ISO date in `YYYY-MM-DD` form; it must not precede `created`. |
| `secondary_capabilities` | No | Additional controlled capability values directly supported by the Lab; do not repeat `primary_capability`. |
| `secondary_roles` | No | Additional controlled role values directly served by the Lab; do not repeat `roles`. |
| `authors` | No | Names, handles, or organizations that may be published. |
| `maintainers` | No | People or teams responsible for reruns and updates. |
| `source_links` | No | Safe-to-share sources, such as pricing pages or task-input provenance. Record an as-of date beside sources that can change. |
| `deprecated_on` | Conditional | ISO date required when `status` is `deprecated`. |
| `deprecation_reason` | Conditional | Non-empty reason required when `status` is `deprecated`. |
| `superseded_by` | No | Relative path or URL for a replacement, only when one exists. |

The controlled role vocabulary is: `individual-practitioner`, `engineer`, `architect`, `builder`, `operator`, `founder`, `services-leader`, `internal-ai-champion`, `transformation-lead`, `consultant`, `agency-implementer`, and `executive`.

## Required content

Every Lab contains these headings, in this order:

1. `Question` — one bounded comparison or test question.
2. `Hypothesis` — a falsifiable expectation and predeclared decision threshold; it is not a result.
3. `Variables` — independent variable, outcome measures, calculations, and uncontrolled confounders.
4. `Fixed conditions` — all conditions held constant across compared runs.
5. `Task set` — complete task packets or a resolvable dataset, required artifacts, and expected facts or conditions.
6. `Procedure` — ordered candidate-selection, execution, storage, blinding, and rerun steps.
7. `Evaluation rubric` — scale, task-specific pass conditions, critical errors, evaluator process, disagreement handling, and decision rule.
8. `Cost capture` — pricing source and date, token or usage record, calculation, currency, and exclusions.
9. `Results` — result status, run ledger, per-task quality and cost records, exclusions, raw-output locations or hashes, and aggregate calculation.
10. `Interpretation` — observed answer, bounded inference, and non-result after runs exist; leave it explicitly pending before execution.
11. `Limitations` — coverage, evaluator, version, price, sampling, and comparability limits.
12. `Reproduction` — materials and steps needed to repeat the same Lab.
13. `Changelog` — dated, meaningful changes.

The template's heading names are canonical. Add context within these sections rather than replacing them with synonyms that obscure review.

## Status and result states

| Status or result state | Meaning | Minimum record |
|---|---|---|
| `status: proposed` with `result_status: not-run` | The plan is ready for execution but has no included observations. | Complete task set, fixed conditions, procedure, rubric, cost method, and reproduction plan; `run_count: 0`, `last_run: null`. |
| `status: running` with `result_status: partial` | Some planned runs exist but the predeclared run plan is incomplete. | Run ledger, raw-output location or hash, per-run scores and costs, exclusions, and a note identifying the incomplete portion. |
| `status: completed` with `result_status: complete` | The planned execution and scoring record are available. | All included runs, calculation, interpretation bounded to the task set, limitations, and reproduction record. |
| Any status with `result_status: invalidated` | Included results cannot support the stated comparison. | Exact invalidating condition, affected run IDs, retained record, and whether a new Lab is needed. |
| `status: deprecated` | The Lab remains inspectable but should not be run as written. | `deprecated_on`, `deprecation_reason`, and retained evidence and limitations. |

Do not change a task packet, required artifact, prompt, model configuration, rubric, evaluator policy, or aggregation rule and pool the new runs with the old record. Freeze the earlier record, increment `task_set_version`, and start a separate run group or Lab version.

## Evaluation and cost rules

The rubric must assess artifacts against requirements the task packet makes visible. State a critical error separately from point deductions when an error makes the artifact unusable for the stated task. If evaluators score outputs, they should be blinded to candidate identity where practicable; record when blinding failed. Preserve individual scores, disagreement, adjudication, exclusions, and calculation, not only an average.

Cost is a recorded outcome or constraint, not a substitute for quality. Capture the provider's published pricing source and as-of date, actual usage, currency, and formula. If an invoice or usage dashboard is used, record the access date and the fields transcribed without publishing account information. State excluded costs, such as evaluator labor or local infrastructure, so readers do not mistake model-request cost for total operating cost.

Before execution, define the quality threshold and any cost ceiling separately. A model configuration may be eligible only when it meets both, but never combine them into an unsupported composite score unless the Lab explicitly tests and justifies that measure.

## Reproduction and interpretation rules

Another Practitioner must be able to locate or reconstruct the task set, prompt, parameters, candidate identifier, model or tool version as supplied, run timestamps, randomization or seed setting when exposed, output records, scoring material, pricing source, and calculations. Redact secrets, personal data, and confidential task inputs. If redaction prevents exact reproduction, say what changed and classify the reproduction as partial.

Interpret only what the task set and run record support. A Lab comparing configurations on three artifact tasks may report those task scores and costs under the stated conditions. It may not declare a configuration generally more intelligent, generally better, or recommended for unrelated work. Publish a null, mixed, or failed result with the same record structure as a favorable result.

## Consistency rules a validator can enforce

1. Front matter parses as YAML and includes all required fields with controlled values.
2. Dates use `YYYY-MM-DD`; `updated` does not precede `created`; `last_run` is `null` only for `not-run`; and deprecated Labs include the required date and reason.
3. `task_set_version` and `version` match `MAJOR.MINOR.PATCH`; `run_count` is a non-negative integer; primary and secondary capabilities or roles do not overlap.
4. Required headings exist in canonical order.
5. A `not-run` Lab contains no claimed result, numeric score, cost, or model endorsement in `Results` or `Interpretation`.
6. Any completed or partial Lab has a run ledger with one identifiable record per included run, an output reference or hash, quality score, cost record, and exclusion status.
7. Relative links resolve within the repository.

Human review remains necessary to judge whether the task set measures the stated question, conditions are truly comparable, rubric anchors are meaningful, pricing was captured faithfully, outputs are safe to share, and interpretation stays within the evidence.
