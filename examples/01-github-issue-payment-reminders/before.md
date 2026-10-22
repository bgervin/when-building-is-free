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

## Success metrics

- 60% of active accounts turn on reminders within a month.
- 5,000 reminders sent per week.
- Reminder email open rate above 40%.

## Notes

Feedback theme "late payments" has 23 of 61 Q3 feedback items. Interviews: 5 of 6 office managers spend 2 to 4 hours a week on follow-up calls. Telemetry: median days from invoice sent to paid is 34, on net-30 terms.
