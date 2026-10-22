# Automatic payment reminders for overdue invoices

**Labels:** feature, invoicing
**Product:** Tradebook (invoicing for plumbing, HVAC and electrical contractors)

## Summary

Office managers spend hours every week phoning customers about unpaid invoices. Tradebook should send polite reminders automatically so they don't have to.

## User story

As an office manager, I want Tradebook to remind customers about invoices automatically, so that I spend less time chasing payments.

## Proposal

- Email reminder 3 days before the due date.
- Email and SMS reminder 7 days after the due date if the invoice is still unpaid.
- Reminders use the business's name and logo, and include a pay-now link.
- Office managers can turn reminders on or off per customer and edit the wording.

## Acceptance criteria

- [ ] Reminders send on schedule for invoices with a due date.
- [ ] No reminder is sent once an invoice is marked paid.
- [ ] Customers can unsubscribe from reminders with one click.
- [ ] Office managers can preview a reminder before turning it on.
- [ ] Reminder sends are logged on the invoice timeline.
- [ ] **New:** Ships behind the `invoice-reminders` flag, and emits `invoice.sent`, `invoice.paid`, `reminder.sent`, `reminder.unsubscribed` and `reminder.complaint`.

## Success metrics

- 60% of active accounts turn on reminders within a month. *(rung 3, adopted: diagnostic)*
- 5,000 reminders sent per week. *(volume count, activity: diagnostic)*
- Reminder email open rate above 40%. *(rung 2, discovered: diagnostic)*

None of these says whether invoices get paid sooner, which is what the user story asks for. The charter below adds that as the needle and keeps these as diagnostics.

## Outcome charter

**The bet:** We believe automatic reminders before and after the due date, for office managers who chase unpaid invoices by phone, will get invoices paid sooner and cut follow-up calls, because most late payments are forgotten rather than disputed.

**How we'll know:** Median days from invoice sent to paid drops from 34 to 27 by September 30. If it drops by less than 2 days, or customers complain, we remove the feature.

```feature-charter
id: FC-007
status: live
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
  method: before_after
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

decision_log: []
amendments: []
```

## Notes

Feedback theme "late payments" has 23 of 61 Q3 feedback items. Interviews: 5 of 6 office managers spend 2 to 4 hours a week on follow-up calls. Telemetry: median days from invoice sent to paid is 34, on net-30 terms.
