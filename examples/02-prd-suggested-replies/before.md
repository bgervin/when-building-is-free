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

- 50% of agents use suggested replies at least once a week.
- 10,000 suggestions accepted per day across all customers.
- CSAT stays at or above 4.5.

## Rollout

Beta with 20 customer accounts for 4 weeks, then general availability.

## Open questions

- Should acceptance require at least one edit?
- How do we handle tickets in languages other than English?
