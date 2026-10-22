# Product strategy: Tradebook

**Product:** Tradebook (invoicing for plumbing, HVAC and electrical contractors). Fictional, like every example in this repository.

## The challenge

Small contractors get paid late because invoicing happens days after the job, from the office, by someone who wasn't there. The work is done; the money arrives five weeks later. Every feature competes with that gap.

## Who we serve, and who we don't

We serve owner-operated contractors with 2 to 20 field staff, where the owner or one office manager does the books. We don't serve mid-size contractors with 50 or more field staff and a finance team: they need ERP integrations, multi-entity accounting and approval chains, and enterprise field-service suites serve them well.

## How we'll choose

1. Cash cycle first: anything that gets contractors from job done to money in the bank sooner beats anything that makes the office tidier.
2. The person in the truck comes first; office-only features come second.
3. Payment methods follow what contractors' customers already use.
4. Integrate with the accounting tools our segment uses, one way first, and never build desktop or ERP integrations as product.
5. Match a competitor's feature only when lost deals or churn reasons in our segment cite it.

## Where the effort goes

Tune 30%, bet 50%, probe 20%, as a share of active bets and probes. Most effort goes to chartered bets on the cash cycle, and about a third to tuning what has proven itself. A fifth goes to cheap probes, because a week of interviews or a fake door costs almost nothing now.

## What we've ruled out

See the rulings in the block below, and the Not betting section of the [bet board](bet-board.md).

```product-strategy
id: ST-2026H2
name: Tradebook
status: approved
owner: Head of Product, Tradebook
approved: 2026-07-06
review_date: 2026-10-30

diagnosis: >
  Small contractors get paid late because invoicing happens days after the job, from the office,
  by someone who wasn't there. Median days from invoice sent to paid is 34 on net-30 terms.
  Every feature competes with that gap.

segments:
  target:
    - id: SEG-01
      name: Owner-operated contractors
      definition: Plumbing, HVAC and electrical businesses with 2 to 20 field staff, where the owner or one office manager does the books
  not_target:
    - id: SEG-X1
      name: Mid-size contractors
      why: 50 or more field staff and a finance team; they need ERP integrations, multi-entity accounting and approval chains

policies:
  - id: P-01
    statement: Cash cycle first. Work that gets contractors from job done to money in the bank sooner beats work that makes the office tidier.
    decides: Yes to automatic payment reminders (#212). Not now to custom invoice themes (#198).
  - id: P-02
    statement: The person in the truck comes first; office-only features come second.
    decides: Yes to sending an invoice from the job site without signal (#244). Not now to bulk office reports (#203).
  - id: P-03
    statement: Payment methods follow what contractors' customers already use; we add a method only when target accounts' customers ask to pay that way.
    decides: No to accepting crypto payments (#251).
  - id: P-04
    statement: We integrate with the accounting tools our segment uses (QuickBooks Online, Xero), one way first. Desktop and ERP integrations are services work, not product.
    decides: Services, not roadmap, for a two-way QuickBooks Desktop sync (#230).
  - id: P-05
    statement: We match a competitor's feature only when lost deals or churn reasons in our segment cite it.
    decides: Not now to an AI estimate builder (#247).

areas:
  - {id: invoicing, name: Invoicing, labels: [area/invoicing], owner: PM, Invoicing}
  - {id: payments, name: Payments and reminders, labels: [area/payments], owner: Head of Product, Tradebook}
  - {id: mobile, name: Mobile field app, labels: [area/mobile], owner: PM, Mobile}
  - {id: onboarding, name: Onboarding, labels: [area/onboarding], owner: PM, Activation}
  - {id: integrations, name: Accounting integrations, labels: [area/integrations], owner: PM, Accounting integrations}

horizons:
  tune: 30
  bet: 50
  probe: 20

rulings:
  - id: R-001
    request: Custom invoice themes and fonts
    ruling: not_now
    policy: P-01
    reason: Makes invoices prettier, not paid sooner. No lost deals cite it.
    reopen_if: The cash-cycle bets are decided, or five target accounts cite branding when they cancel
    decided_by: Head of Product, Tradebook
    date: 2026-07-06
    issues: ["#198"]
  - id: R-002
    request: Accept crypto payments on invoices
    ruling: "no"
    policy: P-03
    reason: Asked for by the founder, not by customers. No target account reports a customer asking to pay this way.
    reopen_if: Ten target accounts report customers asking to pay in crypto within a quarter
    decided_by: Founder and Head of Product, Tradebook
    date: 2026-10-15
    issues: ["#251"]
  - id: R-003
    request: Two-way QuickBooks Desktop sync
    ruling: services
    policy: P-04
    reason: One account needs it, with 140 field staff, outside the target segment. Priced as a services integration for that account; kept out of the product.
    reopen_if: Three target accounts on QuickBooks Desktop ask within one quarter
    decided_by: Head of Product, Tradebook
    date: 2026-10-15
    issues: ["#230", "#236"]
  - id: R-004
    request: AI estimate builder like a competitor's
    ruling: not_now
    policy: P-05
    reason: Real interest from 7 target accounts, but every request came in the two weeks after a competitor's launch post, and no lost deal or churn reason in Q3 mentions estimating.
    reopen_if: Estimating appears in lost-deal or churn reasons for two months running
    decided_by: Head of Product, Tradebook
    date: 2026-10-15
    issues: ["#247", "#249", "#250"]
  - id: R-005
    request: Dark mode
    ruling: not_now
    policy: P-01
    reason: 48 votes from 4 accounts, 31 of them from one company's technicians. No task fails without it.
    reopen_if: Ten target accounts ask, or field testing shows screens can't be read at night
    decided_by: Head of Product, Tradebook
    date: 2026-10-15
    issues: ["#205"]
  - id: R-006
    request: Bulk reports for the office
    ruling: not_now
    policy: P-02
    reason: Office-only, and 3 target accounts ask. The field work comes first.
    reopen_if: Ten target accounts ask, or office managers report spending more than an hour a week assembling reports
    decided_by: Head of Product, Tradebook
    date: 2026-10-15
    issues: ["#203"]
```
