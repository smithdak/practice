# Flagship launch video brief

## Working title

**Can this answer survive the work?**

## Job of the video

Show the difference between receiving a plausible model answer and building a method that can be used, checked, and improved. The viewer should see the Practice thesis happen through visible work: frame a task, assemble context, redesign the workflow, verify the output, record limitations, and share the reusable result.

This is a launch film for **Practice — the open community for AI practitioners.** It is not a product tour, a model comparison, or a biography of Dakota.

## Audience and outcome

The primary viewer is responsible for making AI useful in a real context but may not identify as an AI expert. That includes individual Practitioners, builders, operators, internal champions, consultants, and leaders.

After watching, the viewer should understand:

- why a fast answer is only the beginning;
- what turns an experiment into reviewable capability;
- how Git and Buzz serve different parts of open collaboration; and
- the single next action to take.

## Format

- **Length:** 100–120 seconds.
- **Frame:** 16:9 master, composed so a 9:16 crop can preserve the active work area.
- **Style:** documentary screen capture with restrained voiceover, close shots of hands and notes, and brief direct-to-camera bookends.
- **Sound:** real keyboard, page, and room sounds under a minimal score. Let verification moments breathe; do not use synthetic “success” chimes.
- **On-screen type:** short labels that name the work: `Context`, `Boundary`, `Check`, `Evidence`, `Share`.

Dakota is the on-screen builder and narrator. The perspective comes from the decisions being made in the captured work, not from personal history or claims of prior success.

## Demonstration scenario

Use one real, non-sensitive repository change from Practice. A suitable example is revising a small section of guidance against a written acceptance checklist. Capture the actual files, diff, validation output, and limitations that exist at production time.

The sequence must be truthful:

1. Open the bounded task and its acceptance criteria.
2. Gather the approved context that controls the change.
3. Ask a model or agent for a draft within that boundary.
4. Inspect the diff instead of accepting the completion claim.
5. Run the relevant checks and show one human judgment the automated check cannot make.
6. Record a limitation or correction.
7. Show the canonical artifact in Git and route the discussion through Buzz.

Do not stage a fabricated failure, result, metric, comment, or community interaction. If the captured draft passes its automated checks, the tension comes from the remaining human review. If a real check fails, show the correction without turning it into drama.

## Storyboard and voiceover

| Time | Picture: show the work | Voiceover / sound | On-screen text |
| --- | --- | --- | --- |
| 0:00–0:08 | Tight screen capture: a model produces a polished answer. Cursor pauses over the response. Hard cut to the task's acceptance checklist. | **Dakota:** “The answer arrived in seconds. Now the work starts.” | `An answer is not acceptance.` |
| 0:08–0:20 | Brief direct-to-camera line, then hands return to keyboard. Intercut the task boundary, allowed files, and desired output. | “I need to know what it was asked to do, what context controlled it, and what a good result means here.” | `Boundary` |
| 0:20–0:34 | Open a context pack or controlling source. Highlight source authority, a constraint, and an exclusion. Show only safe repository material. | “A useful method makes its inputs and limits visible. That is the difference between a lucky draft and work another person can inspect.” | `Context` |
| 0:34–0:48 | Show a simple workflow map: draft → deterministic check → human review → accept/revise. Mark the approval point before publication. | “Then I design the path around the consequence. The system can draft. Checks can catch defined failures. A person still owns the decision to publish.” | `Workflow + owner` |
| 0:48–1:05 | Split view: agent completion statement on one side, repository diff on the other. Inspect changed lines and follow one claim to its source. | “A completion message is a claim. The diff, the source, and the test record are evidence.” Keyboard and mouse sounds come forward. | `Claim → evidence` |
| 1:05–1:18 | Run the real validator. Then show the human checklist and make or record one genuine correction or limitation if present. | “Passing a check matters. It also does not answer every question. Review has to match the risk, and uncertainty stays in the record.” | `Verify` |
| 1:18–1:33 | Pull back from the single file to the open Guide and the three canonical Practices in Git. Show visible version history or diff view. | “Practice makes these methods open: context you can reuse, workflows you can examine, and verification another Practitioner can challenge and improve.” | `Open artifacts in Git` |
| 1:33–1:45 | Show Buzz `start-here`, then a prepared introduction that names a role, one non-sensitive task, a capability outcome, and a first small action. Do not imply the post came from another member. | “Buzz is where humans and agents coordinate around the work. Git is where the durable result remains available to inspect and fork.” | `Coordinate in Buzz` / `Preserve in Git` |
| 1:45–1:55 | Dakota selects one canonical Practice in Git, then moves to the prepared `start-here` post. End card carries the fixed positioning. | “Choose one real task. Inspect one open method. Bring back what happened.” | `Practice`<br>`The open community for AI practitioners.` |

## Capture plan

### Required footage

- One clean direct-to-camera setup for the opening transition; keep total talking-head footage under 15 seconds.
- Screen recording at native resolution of:
  - the bounded task and acceptance criteria;
  - approved context or source material;
  - the model or agent draft;
  - the repository diff;
  - the real validation command and result;
  - a human review note, correction, or limitation;
  - [The AI-Native Practitioner Guide](../../guides/ai-native-practitioner/README.md);
  - [Practice 001: Reusable Context Pack](../../practices/001-context-pack.md);
  - [Practice 002: Workflow Redesign](../../practices/002-workflow-redesign.md);
  - [Practice 003: Agent Verification Gate](../../practices/003-verification-gate.md); and
  - the [`start-here` orientation for Buzz](../../buzz/canvases/start-here.md).
- Close shots of writing the acceptance criteria, marking the approval boundary, and comparing the output with the source.
- One wide shot that shows the builder moving between the task, terminal, and notes.

### Production safeguards

- Use a fresh capture workspace containing no secrets, private keys, personal information, notifications, private repository names, or confidential inputs.
- Disable notifications and inspect the browser, shell prompt, recent-file lists, terminal history, and environment output before recording.
- Record actual commands and results. Do not replace failed checks with a fabricated pass in the edit.
- Crop or blur only incidental sensitive data; if the sensitive material is essential to the shot, recapture with safe inputs.
- Use generic model framing unless the specific tool is necessary to reproduce the demonstrated step.
- Caption every spoken line and ensure code, diffs, and check results remain readable without relying on color alone.

## Editorial rules

- Keep the model response visually impressive for no more than three seconds. The subject is the work around the response.
- Favor cursor movement, selections, edits, diffs, test output, and review marks over abstract animation.
- Do not use stock robots, glowing brains, science-fiction interfaces, speed counters, adoption claims, or market statistics.
- Do not describe the demonstrated workflow as reliable, safe, or improved beyond what the captured evidence establishes.
- Preserve pauses around the diff and human review so verification feels like the main action, not an obstacle in a montage.
- Mention the ethos only if a longer cut needs it; the master already demonstrates **Learn it. Build it. Use it. Share it.** through action.

## End card and one invitation

Keep the card on screen long enough to read and provide a scannable repository link plus the Buzz entry route when final URLs are available.

Do not add secondary buttons, newsletter signup, follower request, or “learn more” prompt.

> **Choose one non-sensitive task, inspect the relevant canonical Practice in Git, and post your first action or result in [`start-here` on Buzz](../../buzz/canvases/start-here.md).**
