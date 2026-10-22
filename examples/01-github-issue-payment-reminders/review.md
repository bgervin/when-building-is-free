# Automatic payment reminders: review on September 30

*The same issue six weeks later. The judge added the review summary below, and the owner recorded the decision in the charter: status, decision log, and one amendment switching the next review to a holdback. The rest of the issue is unchanged and omitted here.*

## Review summary

- **Needle:** median days to paid fell from 34 to 28 (6 days, above the 4-day minimum). 312 invoices across 37 accounts.
- **Guardrails:** 0.4 complaints per 100 reminders (limit 1). 2.1% of customers unsubscribed (limit 5%). Both held.
- **Look at:** 5 of 6 office managers report fewer follow-up calls. In 20 reminder threads, 2 customers asked to change the wording; none complained.
- **Diagnostics:** 71% of active accounts turned reminders on. Open rate 46%. These explain the result; they didn't decide it.
- **Other changes in the window:** none shipped to these accounts.

**Decision: keep.** Next review December 22, using a 10% holdback to confirm the effect holds.

## Outcome charter

```feature-charter
id: FC-007
status: kept
owner: Head of Product, Tradebook
builder: factory/build-agents
judge: factory/eval-agent with the analytics lead
approved: 2026-08-17

hypothesis:
  we_believe: email and SMS reminders 3 days before and 7 days after the due date
  for: office managers who chase unpaid invoices by phone
  will_result_in: invoices paid sooner and fewer follow-up calls
  because: most late payments are forgotten rather than disputed

evidence:
  - "Feedback theme late-payments: 23 of 61 Q3 items"
  - "Interviews: 5 of 6 office managers spend 2 to 4 hours a week on follow-up calls"

strategy: {policy: P-01, area: payments, horizon: bet}

value_type: frequency

needle:
  name: Median days from invoice sent to paid
  rung: user_outcome
  definition: >
    For invoices sent in the first 7 days after launch by accounts with reminders on,
    the median of (paid_at minus sent_at) in days. Invoices unpaid after 35 days count as 35.
    Baseline uses the same rule on the same accounts' invoices from the prior quarter.
  source: invoice.sent and invoice.paid events
  baseline: 34
  target: 27
  direction: decrease
  min_change: 4
  window_days: 42

guardrails:
  - name: Complaints about reminders
    limit: no more than 1 per 100 reminders sent
  - name: Reminder unsubscribes
    limit: no more than 5% of the business's customers

diagnostics:
  - Share of active accounts with reminders on (the original 60% goal)
  - Reminders sent per week (the original 5,000 goal)
  - Reminder open rate (the original 40% goal)
  - Follow-up calls logged by office managers

evaluation:
  method: holdback
  weekly_users: null
  review_date: 2026-09-30
  keep_if: median days to paid drops by 4 or more and both guardrails hold
  kill_if: median days to paid drops by less than 2, or either guardrail is breached
  iterate_if: a drop of 2 to 4 days with guardrails holding; try different timing or wording
  if_inconclusive: sunset
  look_at: interview the same 6 office managers; keep needs at least 4 to report fewer calls. Read 20 reminder threads for tone complaints.

removal:
  flag: invoice-reminders
  code_paths: [src/reminders/, src/jobs/reminder_scheduler.py]
  data: reminder_log table; drop on removal, nothing else references it
  estimate_hours: 4

decision_log:
  - date: 2026-09-30
    decision: keep
    evidence: >
      Median days to paid 34 to 28 on 312 invoices from 37 accounts. Complaints 0.4 per 100,
      unsubscribes 2.1%. 5 of 6 office managers report fewer calls. Analysis: reviews/FC-007-2026-09-30.md
    decided_by: Head of Product, Tradebook
    next_review: 2026-12-22

amendments:
  - date: 2026-09-30
    field: evaluation.method
    from: before_after
    to: holdback
    reason: the next review keeps reminders off for 10% of eligible accounts to confirm the effect holds
    approved_by: Head of Product, Tradebook
```
