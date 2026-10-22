# Tradebook feedback backlog: Q3 2026 review

**Product:** Tradebook (invoicing for plumbing, HVAC and electrical contractors)
**Prepared for:** Q4 planning, October 14, 2026
**Source:** GitHub issues labelled `feedback`, opened July 1 to September 30, sorted by 👍

## Top requests by votes

| Issue | Request | Area | Votes | Accounts | Accounts with 2 to 20 field staff |
|---|---|---|---|---|---|
| #205 | Dark mode | mobile | 48 | 4 | 3 |
| #230 | Two-way QuickBooks Desktop sync | integrations | 31 | 1 | 0 |
| #247 | AI estimate builder like FieldPro's | invoicing | 22 | 5 | 4 |
| #240 | Photos of the finished job on the invoice | invoicing | 12 | 8 | 8 |
| #198 | Custom invoice themes and fonts | invoicing | 11 | 7 | 6 |
| #212 | Remind customers automatically about overdue invoices | payments | 9 | 7 | 6 |
| #244 | Can't send an invoice from a job site with no signal | mobile | 9 | 11 | 11 |
| #203 | Bulk reports for the office | invoicing | 8 | 4 | 3 |
| #221 | Take a deposit before starting a big job | payments | 7 | 4 | 4 |
| #215 | Auto-email customers when an invoice is late | payments | 6 | 5 | 5 |
| #255 | New workspace: where do I start? | onboarding | 6 | 6 | 6 |
| #219 | Text customers a payment link | payments | 5 | 4 | 4 |
| #238 | Progress billing for multi-week jobs | payments | 5 | 3 | 2 |
| #233 | Reminder before the due date | payments | 4 | 3 | 3 |
| #249 | Generate estimates with AI | invoicing | 4 | 2 | 2 |
| #236 | QuickBooks Desktop: sync payments back | integrations | 3 | 1 | 0 |
| #257 | Can't find where to add my logo | onboarding | 3 | 3 | 3 |
| #250 | Estimate from a photo of the job | invoicing | 2 | 1 | 1 |
| #251 | Accept crypto payments | payments | 0 | 0 | 0 |

## Proposed for Q4

The three most-voted requests:

1. Dark mode (#205), 48 votes. *(Flag: loudest voice. 4 accounts, 3 in the target segment; 31 votes from one company outside it. Proposed ruling R-005, not now.)*
2. Two-way QuickBooks Desktop sync (#230), 31 votes. Northgate Mechanical, our largest account, says it is a condition of renewal. *(Flag: hostage customer. One account, outside the target segment. Proposed ruling R-003, services: priced as a deal for Northgate, kept off the roadmap.)*
3. AI estimate builder (#247), 22 votes. FieldPro launched one on August 26. *(Flag: rearview mirror. 7 target accounts across #247, #249 and #250, all in the two weeks after the launch; no lost deal cites it. Proposed ruling R-004, not now, reopened by lost-deal evidence.)*

**New:** None of the three is on the triaged shortlist below. Ranked by votes, the backlog puts a preference, one customer's contract and a competitor's launch ahead of the two problems with failure data behind them.

## Executive requests

- Accept crypto payments (#251), filed by the founder after a conference. Labelled `priority/exec`. *(Flag: HiPPO. No customer has asked, and policy P-03 adds payment methods only when customers' customers ask for them. Proposed ruling R-002, no, which the founder co-signed, with a reopen condition.)*

## Notes

- Votes are GitHub 👍 reactions. Accounts come from the issue form's Company field and the support tool. No account appears on more than one issue except Northgate Mechanical (#205, #230 and #236).
- 31 of the 48 votes on #205 come from Northgate Mechanical's technicians. Northgate has 140 field staff.
- #247, #249 and #250 were all opened between August 27 and September 9. No lost deal or churn reason in Q3 mentions estimating.
- #212, #215, #219 and #233 are about late payments. Payment reminders shipped as FC-007 and were kept at review on September 30.
- #255 and #257 are about setup. The guided onboarding checklist is specced as `014-onboarding-checklist`. 38% of new workspaces send a first invoice within 7 days.
- Telemetry: 14% of invoices started on mobile fail to send on the first try because there's no signal; 4 in 10 of those are re-sent from the office the next day.
- #198 (invoice themes) was ruled not now in July (R-001).
- The founder has not heard from a customer asking to pay in crypto.

## New: Triage against the strategy

**Strategy:** [ST-2026H2](strategy.md), approved July 6. **Triaged:** October 14 by the triage agent, approved October 15 by the Head of Product.

**The call to make:** approve rulings R-002 to R-006; take OPP-004 (sending from a job site with no signal) to a charter; run the deposits probe (OPP-002) until November 5. The bet board shows bets at a third of active work against a plan of half, so there's room for OPP-004.

### 1. By area

| Area | Issues | Distinct accounts | In target segment |
|---|---|---|---|
| Invoicing | 6 | 27 | 24 |
| Payments and reminders | 7 | 26 | 24 |
| Mobile field app | 2 | 15 | 14 |
| Onboarding | 2 | 9 | 9 |
| Accounting integrations | 2 | 1 | 0 |

### 2. Duplicates merged

| Kept as | Merged | Accounts (in segment) | Votes | Note |
|---|---|---|---|---|
| #212 late payments | #215, #219, #233 | 19 (18) | 24 | Already bet on: OPP-001, chartered as FC-007, kept September 30 |
| #247 AI estimates | #249, #250 | 8 (7) | 28 | Same ask in three forms |
| #221 deposits | #238 | 7 (6) | 12 | Deposits and progress billing are both "get paid before the job ends" |
| #255 setup | #257 | 9 (9) | 9 | Already specced as `014-onboarding-checklist` |
| #230 QuickBooks Desktop | #236 | 1 (0) | 34 | Same account |

### 3. Already ruled out or already bet on

| Issues | Matches | New evidence since? | Proposed reply |
|---|---|---|---|
| #198 | R-001, not now | No | Invoice themes are on hold while cash-cycle work comes first; we'll look again when those bets are decided or branding shows up in cancellations. |
| #212, #215, #219, #233 | OPP-001 and FC-007 | No: these predate the reminders launch | Reminders shipped in August behind `invoice-reminders`; links to the release note. Close as done. |

### 4. Strategy fit and failure modes

| Item or group | Fits | Flag | Why |
|---|---|---|---|
| #205 dark mode | None | loudest_voice | 48 votes, 4 accounts; no task fails without it |
| #230, #236 QuickBooks Desktop | P-04 says services | hostage_customer | One account, 140 field staff, outside the segment |
| #247, #249, #250 AI estimates | P-05 says not yet | rearview_mirror | All opened in the two weeks after a competitor's launch; no lost deal cites it |
| #251 crypto | P-03 says no | hippo | Filed by the founder; no customer has asked |
| #203 office reports | P-02 says second | None | Office-only; 3 target accounts |
| #240 job photos | Unclear | None | 8 target accounts, but no evidence yet that photos change when invoices get paid. Parked: ask whether disputes cite missing proof of work |

**Proposed new rulings:** R-002 to R-006, now in the [strategy's rulings](strategy.md) after approval on October 15.

### 5. Shortlist, ranked

Ranked by the strength of evidence that a result fails (telemetry first), then by accounts in the target segment. Votes are shown; they don't rank.

| Rank | Opportunity | Rung | Accounts in segment | Votes | Horizon | Next step |
|---|---|---|---|---|---|---|
| 1 | OPP-001: office managers lose hours chasing late payments | User outcome | 18 | 24 | Tune (H1) | FC-007 kept; next review December 22 |
| 2 | OPP-004: invoices started at a job site with no signal don't send | Task success | 11 | 9 | Bet (H2) | Charter next; the mix has room |
| 3 | OPP-003: new contractors don't send a first invoice in their first week | User outcome | 9 | 9 | Bet (H2) | Charter FC-014 on `014-onboarding-checklist` |
| 4 | OPP-002: contractors pay for materials before the customer pays anything | User outcome | 6 | 12 | Probe (H3) | 8 interviews and a "Request a deposit" fake door on quotes over $5,000, until November 5 |

### 6. Opportunity briefs

#### OPP-001: late payments

Already chartered in August as [FC-007](../01-github-issue-payment-reminders/review.md). Kept on September 30; the four issues predate the launch.

```opportunity-brief
id: OPP-001
status: chartered
area: payments
segment: SEG-01
opportunity: Office managers lose hours every week chasing customers who pay late, mostly because they forgot
requests: ["#212", "#215", "#219", "#233"]
breadth: {accounts: 19, in_segment: 18, window: Q3 2026}
rung: user_outcome
telemetry: Median days from invoice sent to paid is 34 on net-30 terms
severity: 5 of 6 office managers interviewed spend 2 to 4 hours a week on follow-up calls
strategy: {policy: P-01, horizon: tune}
flags: []
charter: FC-007
```

#### OPP-002: deposits before the job ends

**Who struggles, with what:** contractors on jobs over $5,000 pay for materials themselves and wait until the job ends to be paid anything.

```opportunity-brief
id: OPP-002
status: probing
area: payments
segment: SEG-01
opportunity: Contractors on large jobs pay for materials themselves and wait until the job ends to be paid anything
requests: ["#221", "#238"]
breadth: {accounts: 7, in_segment: 6, window: Q3 2026}
rung: user_outcome
telemetry: none yet
severity: Not yet known; the probe's interviews ask how often and how much
strategy: {policy: P-01, horizon: probe}
flags: []
probe_ends: 2026-11-05
```

#### OPP-003: first invoice in the first week

**Who struggles, with what:** owners of new workspaces stall on setup steps they don't know they need, and 38% send a first invoice within 7 days.

```opportunity-brief
id: OPP-003
status: chartered
area: onboarding
segment: SEG-01
opportunity: Owners of new workspaces stall on setup steps they don't know they need, so most don't send a first invoice in their first week
requests: ["#255", "#257"]
breadth: {accounts: 9, in_segment: 9, window: Q3 2026}
rung: user_outcome
telemetry: 38% of new workspaces send a first invoice within 7 days
severity: New workspaces that never send an invoice don't convert to paid plans
strategy: {policy: P-01, horizon: bet}
flags: []
charter: FC-014
```

#### OPP-004: sending from a job site with no signal

**Who struggles, with what:** technicians finish the job and start the invoice in the truck, but with no signal it doesn't send, and the office re-sends it the next day.

```opportunity-brief
id: OPP-004
status: shortlisted
area: mobile
segment: SEG-01
opportunity: Technicians start the invoice at the job site, but with no signal it fails to send and the office re-sends it the next day
requests: ["#244"]
breadth: {accounts: 11, in_segment: 11, window: Q3 2026}
rung: task_success
telemetry: 14% of invoices started on mobile fail to send on the first try; 4 in 10 of those are re-sent from the office the next day
severity: Every day an invoice waits adds a day to days-to-paid, the strategy's diagnosis
strategy: {policy: P-02, horizon: bet}
flags: []
```

## New: Not decided here

- Whether job photos (#240) belong in a probe. It depends on whether payment disputes cite missing proof of work, and nobody has checked.
- Northgate Mechanical's services deal (R-003): price, staffing and term are for sales and the Head of Product, not the roadmap.
