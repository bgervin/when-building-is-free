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

- **SC-001**: 90% of new workspaces complete the checklist within 7 days.
- **SC-002**: The checklist renders in under 1 second on the dashboard.
- **SC-003**: Support tickets about account setup drop by 30%.

## Assumptions

- About 400 new workspaces are created each week.
- Today 38% of new workspaces send their first invoice within 7 days of signing up.
- Setup tickets are tagged "setup" by the support team.
