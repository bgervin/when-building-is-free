# Feature Specification: Guided onboarding checklist

**Feature Branch**: `014-onboarding-checklist`
**Created**: 2026-10-12
**Status**: Draft
**Input**: User description: "New Tradebook workspaces should get a short checklist that walks them through setup: add business details, add a customer, create and send a first invoice."

## User Scenarios & Testing *(mandatory)*

### User Story 1: Finish setup from a checklist (Priority: P1)

A new owner signs up and sees a checklist on the dashboard with four steps: business details, logo, first customer, first invoice. Each step links to the right screen and ticks itself off when done.

**Why this priority**: New workspaces that never send an invoice don't convert to paid plans.

**Independent Test**: Create a new workspace, complete each step, and confirm the checklist updates and disappears when all steps are done.

**Acceptance Scenarios**:

1. **Given** a new workspace, **When** the owner opens the dashboard, **Then** the checklist shows four unchecked steps.
2. **Given** the owner has added a customer, **When** they return to the dashboard, **Then** the customer step is checked.
3. **Given** all steps are complete, **When** the owner opens the dashboard, **Then** the checklist is replaced by a short confirmation and then hidden.

### User Story 2: Dismiss the checklist (Priority: P2)

Experienced owners migrating from another tool can dismiss the checklist.

**Why this priority**: Forcing setup steps on experienced users slows them down.

**Independent Test**: Dismiss the checklist and confirm it stays hidden across sessions and devices.

**Acceptance Scenarios**:

1. **Given** the checklist is visible, **When** the owner selects Dismiss, **Then** it is hidden for the whole workspace.

### Edge Cases

- A workspace created by importing data from another tool already has customers and invoices: matching steps start checked.
- Two owners in one workspace complete steps at the same time.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST show the checklist to workspaces created in the last 30 days that haven't dismissed it.
- **FR-002**: System MUST check off each step automatically when its underlying record exists.
- **FR-003**: Each step MUST link directly to the screen that completes it.
- **FR-004**: Owners MUST be able to dismiss the checklist for the whole workspace.

### Key Entities

- **ChecklistState**: per workspace; which steps are complete, dismissed flag, timestamps.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 90% of new workspaces complete the checklist within 7 days. *(rung 3, adopted: diagnostic. Completing the checklist isn't the goal; sending the first invoice is.)*
- **SC-002**: The checklist renders in under 1 second on the dashboard. *(a performance requirement, not on the ladder: kept as a requirement and used as a guardrail)*
- **SC-003**: Support tickets about account setup drop by 30%. *(rung 7, cost to serve: a good outcome, but setup tickets are too few to read within 45 days; kept as a secondary result)*
- **New:** **SC-004**: The share of new workspaces that send their first invoice within 7 days of signing up rises from 38% to 46%. *(rung 6, user outcome: the needle. The 38% baseline is from Assumptions; the 46% target is proposed for the owner to confirm.)*

## Outcome charter

**The bet:** We believe a four-step setup checklist, for owners of new Tradebook workspaces, will get more of them to send a first invoice in their first week, because most stall on setup steps they don't know they need.

**How we'll know:** SC-004 rises from 38% to 46% for workspaces that see the checklist, compared with a 20% holdback that doesn't. If it rises by less than 3 points, or dashboard speed suffers, the checklist is removed.

```feature-charter
id: FC-014
status: approved
owner: PM, Activation
builder: speckit implement agents
judge: evaluation agent, reviewed by the PM, Activation
approved: 2026-10-20

hypothesis:
  we_believe: a four-step setup checklist on the dashboard (business details, logo, first customer, first invoice)
  for: owners of Tradebook workspaces in their first 30 days
  will_result_in: more workspaces sending their first invoice within 7 days of signing up
  because: most new owners stall on setup steps they don't know they need before invoicing

value_type: frequency

needle:
  name: New workspaces sending a first invoice within 7 days (SC-004)
  rung: user_outcome
  definition: >
    Of workspaces created in the window, the share that send at least one invoice within
    7 days of signup. Checklist group versus a 20% holdback, assigned at signup.
  source: workspace.created and invoice.sent events
  baseline: 38
  target: 46
  direction: increase
  min_change: 3
  window_days: 28

guardrails:
  - name: Checklist render time (SC-002)
    limit: under 1 second on the dashboard
  - name: Time to first invoice for owners who dismiss the checklist
    limit: no slower than the holdback group

diagnostics:
  - SC-001 checklist completion within 7 days
  - Share of owners who dismiss the checklist
  - SC-003 setup tickets (secondary result, read at the next review)

evaluation:
  method: holdback
  weekly_users: 400
  review_date: 2026-12-03
  keep_if: SC-004 rises by 3 points or more versus the holdback and both guardrails hold
  kill_if: SC-004 rises by less than 1 point, or either guardrail is breached
  iterate_if: a rise of 1 to 3 points; change the step order or wording
  if_inconclusive: sunset
  look_at: watch 10 session recordings of owners who finished the checklist but sent no invoice

removal:
  flag: onboarding-checklist
  code_paths: [src/onboarding/checklist/, web/src/dashboard/Checklist.tsx]
  data: checklist_state table; drop on removal
  estimate_hours: 6

decision_log: []
amendments: []
```

## Assumptions

- About 400 new workspaces are created each week.
- Today 38% of new workspaces send their first invoice within 7 days of signing up.
- Setup tickets are tagged "setup" by the support team.
- **New:** The plan includes the `onboarding-checklist` flag, holdback assignment at signup, and the events above. Instrumentation is part of the feature, not a follow-up task.
