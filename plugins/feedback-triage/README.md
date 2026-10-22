# feedback-triage

An agent skill that triages feedback and GitHub issues against a written product strategy, then hands the best opportunities to [`feature-charter`](../feature-charter) as bets.

When building is nearly free, cost no longer says no for you. This skill makes the strategy say it instead, and records every no so it doesn't have to be argued twice.

## What it does

1. **Sorts** issues and feedback into the strategy's product areas.
2. **Merges duplicates** and counts distinct accounts, not mentions or votes.
3. **Applies past rulings**, drafting a reply that links the ruling and says what would reopen it.
4. **Checks strategy fit and flags six failure modes:** the loudest voice, the hostage customer, the rearview mirror (copying competitors), the HiPPO, the parity reflex (internal competition) and the zombie commitment.
5. **Shortlists opportunities**, ranked by the evidence that users fail at a result (telemetry first), then by accounts in the target segment.
6. **Places each on a horizon** by evidence: tune (H1, proven), bet (H2), probe (H3, a cheap test).

Everything is a recommendation. Nothing is closed, labelled or chartered until the owner approves.

## What's inside

| Path | What it is |
|---|---|
| `skills/feedback-triage/SKILL.md` | Instructions: write the strategy, triage a batch, handle one request, turn a brief into a bet, run the leadership review |
| `skills/feedback-triage/templates/strategy.md` | The strategy file: diagnosis, segments, policies, areas, horizon mix, rulings |
| `skills/feedback-triage/templates/triage-report.md` | The report the owner approves |
| `skills/feedback-triage/templates/opportunity-brief.md` | The bridge from triage to a charter |
| `skills/feedback-triage/references/` | The triage protocol, the six failure modes, writing a strategy that decides things, the bet board |
| `skills/feedback-triage/scripts/triage.py` | Validator for strategies and briefs, horizon mix check, bet board generator |

## Install

In Claude Code (2.1.275 or later):

```text
/plugin install feedback-triage --marketplace bgervin/when-building-is-free
```

In GitHub Copilot CLI:

```bash
copilot plugin marketplace add bgervin/when-building-is-free
copilot plugin install feedback-triage@when-building-is-free
```

Install `feature-charter` too; the two skills hand work to each other.

## Use it

- "Draft a strategy.md for this repo from our planning docs."
- "Triage the open issues labelled feedback against our strategy."
- "Our largest customer wants a QuickBooks Desktop sync. Triage it."
- "Make the bet board for Thursday's leadership review."

```bash
pip install pyyaml
python .github/skills/feedback-triage/scripts/triage.py validate strategy.md triage/ docs/specs/
python .github/skills/feedback-triage/scripts/triage.py board strategy.md triage/ docs/specs/ --out bet-board.md
```

See the [worked example](../../examples/05-strategy-and-triage) for the same backlog ranked by votes and then triaged against a strategy.

MIT licensed. No telemetry.
