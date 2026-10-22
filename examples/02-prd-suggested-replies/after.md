# PRD: Suggested replies for support agents

**Product:** Deskline help desk
**Author:** PM, Agent Experience
**Status:** Draft for review

## Overview

Use the help desk's history of resolved tickets to suggest a reply when an agent opens a ticket. The agent can send it as is, edit it, or ignore it.

## Problem

Agents spend most of their handle time writing replies to questions that have been answered hundreds of times before. New agents take about 6 weeks to get up to speed because they don't know the standard answers. Customers wait longer for first replies during peak hours.

## Goals

- Help agents answer common questions faster.
- Make new agents productive sooner.
- Reduce customer wait times.

## Non-goals

- Fully automated replies sent without an agent.
- Suggestions for phone or chat channels (email tickets only in v1).

## Target users

Support agents at Deskline customers with at least 10 agents and 2,000 tickets a month.

## Requirements

1. When an agent opens an email ticket, show up to 3 suggested replies within 2 seconds.
2. Each suggestion cites the past tickets or help articles it drew from.
3. Agents can insert a suggestion into the reply editor and edit it before sending.
4. Admins can turn suggestions off per team and exclude ticket categories.
5. No suggestion is generated for tickets tagged billing dispute, legal or security.

## Success metrics

- 50% of agents use suggested replies at least once a week. *(rung 4, retained: diagnostic)*
- 10,000 suggestions accepted per day across all customers. *(volume count, activity: diagnostic. Don't make this a target: it rewards accepting suggestions whether or not they solve the problem.)*
- CSAT stays at or above 4.5. *(guardrail)*
- **New:** first-reply resolution rate rises by at least 4 points over its baseline. *(rung 5, task success: the needle. See the charter.)*

## Outcome charter

**The bet:** We believe suggested replies, for support agents at mid-size Deskline customers, will resolve more email tickets on the first reply, because most tickets repeat questions the help desk has already answered well.

**How we'll know:** First-reply resolution rises by at least 4 points in eligible categories, with CSAT and reopen rate holding, measured against a 10% holdback of accounts. Decision on the review date; if it misses, suggestions are switched off.

```feature-charter
id: FC-024
status: proposed
owner: PM, Agent Experience
builder: agent-experience squad with coding agents
judge: support analytics team
approved: null

hypothesis:
  we_believe: showing up to 3 suggested replies drawn from resolved tickets and help articles
  for: email support agents at Deskline customers with 10 or more agents
  will_result_in: more tickets resolved by the first reply, without lower satisfaction
  because: most tickets repeat questions the help desk has already answered well

value_type: frequency

needle:
  name: First-reply resolution rate
  rung: task_success
  definition: >
    Share of email tickets in eligible categories that are solved by the first agent reply
    and not reopened within 7 days, per account per week, averaged across accounts.
  source: ticket.created, ticket.replied, ticket.solved and ticket.reopened events
  baseline: measure_before_launch
  target: null
  direction: increase
  min_change: 4
  window_days: 28

guardrails:
  - name: CSAT on eligible tickets
    limit: stays at or above 4.5
  - name: Reopen rate within 7 days
    limit: rises by no more than 1 percentage point
  - name: Escalations caused by a wrong suggested answer
    limit: no more than 0.5% of tickets where a suggestion was used

diagnostics:
  - Share of agents using suggestions weekly (the original 50% goal)
  - Suggestions accepted per day (the original 10,000 goal)
  - Share of accepted suggestions edited before sending
  - Median handle time

evaluation:
  method: holdback
  review_date: null
  keep_if: first-reply resolution rises by 4 points or more versus the holdback and every guardrail holds
  kill_if: the rise is under 2 points, or any guardrail is breached
  iterate_if: a rise of 2 to 4 points with guardrails holding; improve retrieval for the weakest categories
  if_inconclusive: sunset
  look_at: read 50 tickets where a suggestion was sent unedited, and 50 where it was ignored; sit with 5 new agents for an hour each

removal:
  flag: suggested-replies
  code_paths: [services/suggestions/, web/src/editor/SuggestionPanel.tsx]
  data: suggestion_log table and the ticket embedding index; delete both on removal
  estimate_hours: 16

decision_log: []
amendments: []
```

## Rollout

Beta with 20 customer accounts for 4 weeks, then general availability **to 90% of accounts, keeping a 10% holdback until the review date. (New)** Ships behind `suggested-replies`.

## Open questions

- Should acceptance require at least one edit?
- How do we handle tickets in languages other than English?
- **New:** Who approves the charter, and when? Approving it at general availability fits the schedule: the 45-day clock, the holdback and the 28-day window all start then.
- **New:** Measure first-reply resolution on eligible categories during the beta, then set the target. The proposed bet is at least 4 points; is that the right bar?
