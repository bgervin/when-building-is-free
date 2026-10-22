# Review protocol: keep, iterate or sunset

Run this when a charter's `evaluation.review_date` (or a decision's `next_review`) arrives, or when anyone asks whether a feature is worth keeping.

## Roles

- The **judge** gathers the evidence and recommends a decision. The judge is never the builder.
- The **owner** makes the decision and is named in `decided_by`.
- The **builder** can answer questions about the implementation but doesn't interpret results.

## Steps

1. **Read the charter as approved.** The locked sections plus approved amendments are the rules. Don't reinterpret thresholds now that the data is in.
2. **Check the data first.** Are the needle and guardrail events firing correctly? Did anything else ship to the same users during the window? If the data is broken, the result is inconclusive. You may extend the review once, recorded as an approved amendment to `evaluation.review_date` with a reason; the validator then allows up to twice the normal limit. Broken data never defaults to keep.
3. **Check guardrails.** If any guardrail went past its `limit`, the decision is sunset, whatever the needle did.
4. **Compare the needle with the written conditions.** Apply `keep_if`, `kill_if` and `iterate_if` literally. Report the observed value, baseline, target and the uncertainty: a confidence interval, or for qualitative methods the count of supporting and contradicting observations.
5. **Look at real examples** named in `evaluation.look_at`. Gaming and measurement errors are obvious in examples and invisible in aggregates.
6. **Weigh upkeep.** A positive result smaller than `needle.min_change` defaults to sunset: the feature isn't paying for its maintenance.
7. **Record the decision** in `decision_log` with date, decision, evidence (numbers and links) and `decided_by`. Update `status` to match.

## Decision rules

| Situation | Decision | Status |
|---|---|---|
| A guardrail was breached | sunset | `sunset` |
| `kill_if` met | sunset | `sunset` |
| `keep_if` met, change at least `min_change` | keep, with `next_review` at most 90 days out. Changing the method for the next review (for example to a holdback) is an amendment | `kept` |
| `iterate_if` met | iterate: amend the design, set `next_review` at most 90 days out. Two iterations at most; after that, inconclusive or negative means sunset | `iterating` |
| None of the above, or still inconclusive after one extension | apply `if_inconclusive` (sunset or iterate, never keep) | per decision |

The 45-day first review and 90-day renewal are starting defaults. Teams can change them in `.feature-charter.yml`.

## After a sunset

1. Turn the flag off for everyone.
2. Watch for two weeks: support tickets, complaints, guardrails. Unexpected pain means the needle missed something. That is worth a new charter, not a quiet revert.
3. Remove the code paths, tests, docs and stored data listed under `removal`.
4. When the removal merges, add a `removed` decision and set `status: removed`.

`charter.py due` lists features stuck in sunset for more than 30 days.

## After a keep

Keep is a renewal, not a permanent pass. At the next review, a holdback (turning the feature off for a small slice) is the strongest evidence it still earns its place.
