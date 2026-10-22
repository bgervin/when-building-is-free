# The bet board, and keeping leaders aligned

Leaders want an arc for every investment. A roadmap's arc runs from idea to launch, so pulling a feature reads as a broken story and is never celebrated. A bet's arc runs from bet to evidence to decision, so a kill on the review date is the story finishing on time. The bet board shows that arc for the whole portfolio, on one page.

## Generate it

```bash
python scripts/triage.py board strategy.md triage/ docs/specs/ --out bet-board.md
```

It reads the strategy (rulings, horizon mix), opportunity briefs (probes) and charters (bets, decisions, removals). Because it is generated, it can't drift from the charters. Edit the sources, not the board.

| Section | Shows |
|---|---|
| Betting (H2) | Each active bet in one line, its needle from baseline to target, when the decision is due, the owner |
| Probing (H3) | Each probe's question and end date |
| Tuning (H1) | Proven features and their next renewal |
| Decided | Kept, iterated, sunset and removed, with the one-line evidence, plus hours of code deleted |
| Not betting | The rulings: request, decision, policy, reason, what would reopen it |
| Off plan | Overdue reviews, probes past their end date, sunsets never removed, a strategy past its review date, duplicate or invalid blocks, and the horizon mix against the plan |

## How to use it with leaders

1. **Pre-commit the kill.** Before work starts, the sponsoring leader approves the charter's `kill_if` and `review_date`. Annie Duke calls this kill criteria: a signal plus a deadline, set in advance, like a climber's turnaround time. Pulling the feature then keeps the leader's own promise.
2. **Review the board, not the roadmap.** Walk through it on a fixed cadence (monthly works): decisions due, decisions made, what's off plan.
3. **Celebrate decisions, not ships.** Read the Decided section first. At X, Astro Teller brings teams who end their projects on stage and gives them bonuses, because they "have done more in ending their project in this quarter than any of you did". Count kills and hours deleted next to features shipped.
4. **Point to Not betting when a request comes back.** It shows the request was heard, the policy that decided it and what would reopen it. That ends most re-litigation, including the parity requests and pet features.
5. **Re-check the drivers.** At each review, ask whether the reasons in the charter's `evidence` still hold. A feature promised internally whose drivers are gone is a zombie commitment. No script can detect that; the review question can, and the board makes sure every review date comes round.

## Metrics for the factory, not the feature

The board's Factory line reports three numbers from article No. 1, over the board's window:

- **Hit rate:** of the bets whose first decision fell in the window, how many were kept.
- **Time to learn:** the median days from approval to first decision.
- **Deletion:** features removed, and the hours of code deleted.

A hit rate near 100% means the team isn't betting, or the judge is grading its own work.
