# TB-412: Export invoices to CSV for my accountant

**Type:** Story
**Epic:** Accounting integrations
**Story points:** 5

## Story

As a business owner, I want to export my invoices to a CSV file, so that my accountant can do my books without asking me for copies of every invoice.

## Acceptance criteria

1. Owners can choose a date range and export all invoices in it.
2. The CSV includes invoice number, customer, issue date, due date, line items, tax, total and payment status.
3. The file opens correctly in Excel and Google Sheets.
4. Column names and formats match QuickBooks Online's invoice import.
5. Exports of up to 5,000 invoices finish in under 30 seconds.
6. **New:** Ships behind the `invoice-csv-export` flag, and logs `export.created` and `export.downloaded`.

## Notes

Requested by 9 customers this year, mostly at tax time. Two churned customers cited "can't get my data out" in exit surveys.

## Outcome charter

**The bet:** We believe a CSV export in QuickBooks import format, for owners whose accountants do their books, will let accountants import a year of invoices without manual fixes, because today they rebuild the data by hand from PDFs.

**How we'll know:** This is an insurance feature: most owners will use it once or twice a year, so low usage is expected. It earns its place if exports import cleanly when someone does need one. We'll ask accountants directly at the review date.

```feature-charter
id: FC-031
status: proposed
owner: PM, Accounting integrations
builder: integrations team
judge: customer success lead
approved: null

hypothesis:
  we_believe: a date-range CSV export in QuickBooks Online's invoice import format
  for: owners whose external accountants do their books
  will_result_in: accountants importing a period's invoices without manual fixes or extra requests to the owner
  because: today accountants rebuild invoice data by hand from emailed PDFs

value_type: insurance
insurance_reason: >
  Owners need this a few times a year, at tax time and when an accountant changes.
  Being unable to get data out was cited by two churned customers, so its value is
  being reliable when needed, not being used often.

needle:
  name: Exports imported without manual fixes
  rung: task_success
  definition: >
    Of exports made in the window, the share where the owner's accountant confirms the file
    imported into their accounting software without editing columns or rows. Collected with a
    one-question email to the accountant 3 days after each export.
  source: export.created events and the follow-up question's answers
  baseline: 0
  target: 80
  direction: increase
  min_change: 50
  window_days: 42

guardrails:
  - name: Support tickets about exports
    limit: no more than 1 per 10 exports
  - name: Exports that fail or time out
    limit: under 2%

diagnostics:
  - Exports per month (expected to be low and seasonal)
  - Share of exports opened in a spreadsheet versus imported

evaluation:
  method: qualitative
  review_date: null
  keep_if: at least 8 of 10 accountants who answer say the file imported without fixes, and both guardrails hold
  kill_if: fewer than 5 of 10 imported without fixes; replace with a direct QuickBooks integration instead
  iterate_if: 5 to 7 of 10; fix the columns accountants report
  if_inconclusive: iterate
  look_at: call 5 of the accountants and watch one import live
  weekly_users: null

removal:
  flag: invoice-csv-export
  code_paths: [src/exports/invoices_csv.py, web/src/settings/ExportPanel.tsx]
  data: none stored; exports are generated on demand
  estimate_hours: 3

decision_log: []
amendments: []
```

## Open questions

- The baseline is zero because there is no export today, so the target is an absolute bar: 80% of exports import cleanly. Does the owner agree with that bar?
- How will the judge reach accountants? Owners would need to share their accountant's email when they export.
