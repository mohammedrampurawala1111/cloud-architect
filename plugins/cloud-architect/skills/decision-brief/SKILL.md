---
name: decision-brief
description: Turn an architecture design into a one-page decision brief for the CTO, written as the principal architect's recommendation, and record the CTO's decision afterwards. Use when the user must present a plan to a CTO or other decision-maker, or reports the decision.
---

# Decision brief: principal architect → CTO

Roles are fixed:
- **You are the principal architect.** You analyse, compare, recommend and say
  why. You never make the decision, and never write as if it were made.
- **The CTO (or the decision-maker the user names) decides.** The brief exists
  so they can decide in about ten minutes.

**No repository or project folder (e.g. Claude chat, Cowork).** If there is
no repository or writable project folder available (for example in Claude chat
or Cowork without a folder), do not try to write files: deliver every document
in the conversation as Markdown sections with the same headings, and say once
that files weren't written. Skip repo scanning and say the team profile is
self-reported.

## When to run
- At the end of `design`, always (it is part of the deliverables).
- On request for an existing `docs/architecture/<system>/` folder: read its
  README, options, cost and ADRs first and build only from them. Don't invent
  numbers that aren't in the folder.
- When the user reports the decision: go to "Recording the decision".

## Write `decision-brief.md`
Keep it to one page (about 400-600 words plus two tables). Use plain business
language; link to the detailed docs instead of repeating them.

```markdown
# Decision brief: <system name>

**From:** Principal architect · **To:** <CTO name or "CTO"> · **Date:** YYYY-MM-DD
**Decision needed:** <one sentence: which architecture to build> · **By:** <date, or "before <milestone>">

## Context
- What we're building and for whom (one line)
- The constraint that shapes the decision (team capacity, deadline, compliance, budget)
- Team: <size, on-call>, operational complexity budget <N>/5

## Options at a glance
| | A. … | B. … | C. … |
|---|---|---|---|
| Fits the team? | Within | Within | Exceeds |
| Rough cost / month (estimate) | €…–€… | €…–€… | €…–€… |
| Ops burden (highest component) | Low | Medium | High |
| Org guardrail exceptions | 0 | 1 | 3 |
| Time to first release | … | … | … |
| Lock-in | Low / Medium / High | … | … |
| Main risk | … | … | … |

## Recommendation
I recommend **B** because … (two or three reasons tied to requirements and the
team). A is the fallback if … . C becomes right when … .

## What approving B commits us to
- Spend: roughly €…–€…/month infrastructure (estimate; detailed costing is yours)
- Team: what the design assumes of the team (skills, on-call), from the team-fit verdict
- Guardrail exceptions: … (with an org profile)
- Reversibility: … (what is hard to undo)

## Top risks
| Risk | Impact | Mitigation |
|---|---|---|

## Decision
- [ ] A. …
- [ ] B. … (recommended)
- [ ] C. …
- [ ] Not yet: need … (more information, a spike, a pilot)

Decided by: ________ Date: ________ Conditions: ________

Details: [README](README.md) · [options](options.md) · [diagrams](diagrams.md) ·
[ADRs](adr/README.md) · [controls](controls.md)
```

Rules:
- Every verdict comes from the team-fit table and every cost range
  from `options.md`; copy them, don't recompute.
- Show the options fairly: give each its real strength, including the ones you
  don't recommend. Include the option the user or CTO asked for, even if it
  exceeds the team's budget, with its verdict.
- State trade-offs in business terms (money, time, people, risk, reversibility).
- In residency mode add one row "Meets residency and compliance needs?" and link
  `controls.md`.
- Leave out the "Org guardrail exceptions" row when there is no org profile.
- Leave the Decision section unticked and every ADR **Proposed**, with
  `Deciders: CTO` (or the named person).
- In chat, end with: "Ready for the CTO's decision", the recommendation in one
  line, and the questions the CTO is likely to ask, with short answers.

## Recording the decision
Only when the user reports it (for example "the CTO chose B, on condition we
hire a platform engineer by Q3"):
1. Tick the chosen box and fill in decided by, date and conditions in
   `decision-brief.md`. Don't change the analysis above it.
2. ADRs: chosen option's ADRs → **Accepted**, with `Deciders:` and date;
   decisions it replaces → **Rejected** with a one-line reason. Record
   conditions under Consequences. Update `adr/README.md`.
3. `README.md`: add "Decision: B, approved by <name> on <date>" near the top.
4. If the CTO chose an option other than the recommendation, record it without
   arguing; add its risks and mitigations from `options.md` to the README.
5. If the CTO set conditions that are checkable (e.g. "only if data stays in
   eu-central-1"), add them as fitness criteria to the relevant ADRs.
6. If the answer was "not yet", list what is needed and keep everything Proposed.
