# Before and after examples

Each folder holds a realistic spec in a common format (`before.md`) and the same spec enriched with an outcome charter (`after.md`). The enrichment keeps every section and every line the author wrote. The changes are additions, marked **New:**, and short rung labels in italics.

The products are fictional. Facts in the "after" versions (baselines, traffic, feedback counts) come from the "before" versions; where a fact wasn't known, the charter says so instead of guessing. Targets, thresholds and limits are the proposed bet, which the owner confirms when approving the charter. Owners and approval dates stand in for answers the spec's owner would give.

| Folder | Format | The lesson |
|---|---|---|
| [01-github-issue-payment-reminders](01-github-issue-payment-reminders) | GitHub issue | The most common case: three activity metrics and no result. Includes `review.md`, the same issue at its review date. |
| [02-prd-suggested-replies](02-prd-suggested-replies) | PRD | An AI feature, where the obvious target ("suggestions accepted") rewards the wrong behaviour. |
| [03-user-story-invoice-export](03-user-story-invoice-export) | User story | An insurance feature: valuable when needed, so low usage is fine. |
| [04-spec-kit-onboarding-checklist](04-spec-kit-onboarding-checklist) | Spec Kit `spec.md` | A spec built for agents, with measurable success criteria that still measure the wrong thing. |
| [05-strategy-and-triage](05-strategy-and-triage) | A backlog review, `strategy.md` and a bet board | The same backlog ranked by votes, then triaged against a strategy (the `feedback-triage` skill). |

## 01: GitHub issue, payment reminders

**Before:** success meant 60% adoption, 5,000 reminders a week and a 40% open rate. None of those says whether invoices get paid sooner, which is the point of the user story.

**Added:**
- A label on each success metric, marking all three as activity (adopted, a volume count, discovered) and so diagnostics.
- One acceptance criterion: ship behind a flag and emit the events the needle needs.
- An outcome charter with a rung 6 needle: median days from invoice sent to paid, 34 to 27.

**Worth noticing:** the 45-day expiry date shaped the needle. Invoices take about a month to be paid, so the definition counts only invoices sent in the first week and caps unpaid ones at 35 days. That keeps the result readable by the review date.

**`review.md`** shows the review on the expiry date: the needle fell 6 days, guardrails held, 5 of 6 office managers report fewer calls. Decision: keep, with the next review in 83 days. Switching that review to a holdback is recorded as an approved amendment, because the method is part of the locked bet.

## 02: PRD, suggested replies

**Before:** success meant 50% weekly agent adoption, 10,000 accepted suggestions a day and CSAT at 4.5 or above.

**Added:**
- Labels. "Suggestions accepted" is a volume count and gets a warning: as a target, it rewards accepting suggestions whether or not they solve anything (Goodhart's law).
- A new rung 5 needle: first-reply resolution, meaning tickets solved by the first reply and not reopened within 7 days.
- The existing CSAT goal became a guardrail, joined by reopen rate and escalations.
- A 10% holdback added to the rollout plan.
- Two open questions only the owner can answer.

**Worth noticing:** the PRD didn't say what first-reply resolution is today, so the charter doesn't invent it. The baseline is `measure_before_launch`, and the bet is stated as a minimum change of 4 points.

## 03: User story, invoice export

**Before:** a well-formed story with five acceptance criteria and no success measure at all.

**Added:**
- One acceptance criterion for the flag and events.
- An insurance charter. Most owners export once or twice a year, so the needle is reliability when used: the share of exports that import into the accountant's software without manual fixes. The evaluation is qualitative, asking accountants directly.

**Worth noticing:** the kill condition names the alternative ("replace with a direct QuickBooks integration"), so a failed bet still produces a decision.

## 04: Spec Kit spec, onboarding checklist

**Before:** a complete Spec Kit `spec.md`. Its success criteria are measurable, but SC-001 (90% complete the checklist) is rung 3: finishing a checklist isn't the goal.

**Added:**
- A note on SC-001, SC-002 and SC-003, and a new SC-004 at rung 6: the share of new workspaces sending a first invoice within 7 days, from 38% (the spec's own Assumptions) to a proposed 46%.
- An outcome charter between Success Criteria and Assumptions, with a 20% holdback, the Spec Kit implement agents as builder and a separate evaluation agent as judge. SC-002's render limit, as written, became a guardrail.
- One assumption: instrumentation and the flag belong in the plan, not a follow-up task.

**Worth noticing:** SC-003 (setup tickets down 30%) is a good business outcome but too rare to read within 45 days. It stays as a secondary result for the next review rather than being thrown away.

## 05: Strategy and triage

**Before:** Tradebook's Q3 backlog review, sorted by 👍. The three most-voted requests are proposed for Q4: dark mode, a two-way QuickBooks Desktop sync for the largest account, and an AI estimate builder that a competitor launched in August. The founder's crypto payments request is labelled `priority/exec`.

**Added**, keeping every line the author wrote:
- A flag on each Q4 proposal and the executive request: the loudest voice, the hostage customer, the rearview mirror and the HiPPO, each with its evidence and a proposed ruling.
- The six triage steps: areas, duplicates merged by distinct account, past rulings, strategy fit, a shortlist ranked by evidence that a result fails, and horizons.
- Four opportunity briefs. Two are already charters (FC-007 in example 01 and FC-014 in example 04), one is a probe, and one is the next bet.

**`strategy.md`** is the strategy the triage ran against: a diagnosis, one target and one non-target segment, five policies that each decide a real issue, five areas, a horizon mix and six rulings.

**`bet-board.md`** is generated from the strategy, the briefs and the charters in examples 01 and 04. It shows bets running at a third of active work against a plan of half, which is why the next bet (OPP-004) has room.

**Worth noticing:** none of the three most-voted requests makes the shortlist. The top new opportunity, invoices that fail to send from a job site with no signal, had 9 votes but 11 accounts and telemetry showing 14% of mobile sends failing.

## Check them yourself

```bash
pip install pyyaml
python plugins/feature-charter/skills/feature-charter/scripts/charter.py validate examples/02-prd-suggested-replies/after.md
```

Validate one file at a time: `after.md` and `review.md` in example 01 are two snapshots of the same charter, so a folder scan reports their shared id as a duplicate.

For the triage example, validate the strategy, briefs and the charters they link to, and regenerate the bet board:

```bash
T=plugins/feedback-triage/skills/feedback-triage/scripts/triage.py
F="examples/05-strategy-and-triage/strategy.md examples/05-strategy-and-triage/after.md examples/01-github-issue-payment-reminders/review.md examples/04-spec-kit-onboarding-checklist/after.md"
python $T validate $F --today 2026-10-22
python $T board $F --today 2026-10-22 --out examples/05-strategy-and-triage/bet-board.md
```
