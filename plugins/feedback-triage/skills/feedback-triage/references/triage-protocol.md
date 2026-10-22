# Triage protocol

Six steps, in order. Steps 1 to 4 sort and filter; steps 5 and 6 rank and place. Nothing is closed, labelled, commented on or chartered until the owner approves the report.

## Gathering the inputs

**GitHub issues:**

```bash
gh issue list --state open --limit 500 \
  --json number,title,body,labels,author,createdAt,reactionGroups,comments,url > issues.json
```

- `reactionGroups` holds the 👍 counts (votes).
- `author` is a GitHub user, not a customer account. Map users to accounts if the team keeps that mapping (a CSV, an org field, an issue form field such as "Company"). If there is no mapping, say so and count distinct authors, labelled as authors, not accounts.

**Support or feedback tool exports** (Intercom, Zendesk, Productboard, a spreadsheet): ask for a CSV with at least item id, text, account or company, date and, if available, plan or segment.

**Telemetry:** ask for the few numbers that show where a job fails, such as failure rates, drop-offs, time to complete or workaround counts. Don't query production systems yourself unless the person asks you to and you have access.

Work on a copy. Large inputs go in files; process them with a script rather than reading every item into the conversation.

## Step 1: Sort into areas

- Use the strategy's `areas` and their `labels`. Existing area labels win; otherwise classify from the text.
- Items that fit no area go in Unsorted. Many unsorted items mean the areas are wrong, which is worth telling the owner.
- Classification is the part machines do well (Maalej et al., 2024). Still, spot-check about 10 items per area.

## Step 2: Merge duplicates

- Group items that ask for the same outcome, even when they propose different features.
- Keep the oldest or best-described item as the canonical one, and list the rest.
- Count distinct accounts per group: not items, comments or votes.
- Duplicate detection is useful but imperfect. Even strong methods find the right match in their top 10 only about 60 to 65% of the time (Cupid, 2023). Show your groupings; don't close anything automatically.

## Step 3: Check past rulings

- Match each group against the strategy's `rulings`.
- A match with no new evidence gets a proposed reply that links the ruling and states its reopen condition.
- A match with new evidence (the `reopen_if` condition is now met) goes forward, with the ruling named so the owner can reopen it deliberately.

Reply pattern for a ruled-out request:

> Thanks for this. We looked at [the request] on [date] and decided [not now / not to build it / to handle it as a services request], because [reason, one line]. We'll look again if [reopen_if]. The decision is recorded in [link to strategy.md#ruling-id].

## Step 4: Check strategy fit and flag failure modes

- Name the policy each group serves.
- If no policy fits, that is the finding. Propose a ruling (`no` or `not_now`), or ask the owner whether a policy is missing. Don't stretch a policy to cover it.
- Check every group against `references/failure-modes.md` and flag what applies, with one line of evidence for the flag.
- Requests from a `not_target` segment are a no or a services deal, not roadmap.

## Step 5: Shortlist per area

- Restate each surviving group as an opportunity: who struggles, with what. A request is a solution; climb back up to the need (Torres's opportunity solution tree; Ulwick's desired outcomes).
- Rank by the strength of evidence that a result fails: telemetry showing a failing task or outcome first, then requests alone. Within that, rank by distinct accounts in the target segment.
- Name the rung where the job fails (task success, user outcome, business outcome). An opportunity that only moves an activity rung is a diagnostic, not a priority.
- Show votes in the table but never rank by them.
- Telemetry beats anecdotes: a task that fails for 14% of the users who try it outranks a loud request with no failure behind it.

## Step 6: Place on a horizon

| Horizon | Use when | Next step |
|---|---|---|
| Tune (H1) | The feature exists and is proven; the opportunity is to improve or fix it | A change to an existing charter, or an iterate decision |
| Bet (H2) | The opportunity is real (breadth in segment, a failing rung in telemetry); the solution is unproven | A charter with the `feature-charter` skill |
| Probe (H3) | A hunch: little breadth, no telemetry yet, or a new segment | A probe with an end date: 5 to 10 interviews, a fake door, a prototype to 10 users |

- Check the strategy's horizon mix (`triage.py mix`). If bets are already over plan, say so before adding another.
- Write an opportunity brief for each shortlisted item (`templates/opportunity-brief.md`).

## After approval

Only after the owner approves:

1. Add the approved rulings to the strategy file.
2. Apply area labels.
3. Close duplicates and ruled-out items with the replies. Use GitHub's "close as not planned" for rulings and `/duplicate`-style links for duplicates.
4. For each brief marked for a bet, hand it to the `feature-charter` skill. The brief's opportunity, rung and evidence become the charter's hypothesis, needle and `evidence`, and its policy, area and horizon become the charter's `strategy` block.
5. Run `triage.py validate` on the strategy, the report and the charters.
