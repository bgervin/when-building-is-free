## Outcome charter

<!--
Add this section to the spec you already use. Put it right after the spec's
success metrics, acceptance criteria or success criteria, or at the end.
Keep the rest of the spec as it is.

The two sentences below are for people. The block underneath is the same
bet in a form a validator and an agent can check. Fill both, keep them in sync.
Everything inside the block under hypothesis, needle, guardrails and
evaluation is locked once `approved` has a date: change it only by adding
an entry to `amendments`.
-->

**The bet:** We believe [change] for [specific users] will [observable outcome], because [why it should work].

**How we'll know:** [Needle metric] moves from [baseline] to [target] by [review date]. If it doesn't, we remove the feature.

```feature-charter
id: FC-000                  # placeholder: change it, or the validator skips this block
status: proposed            # proposed | approved | building | live | under_review | kept | iterating | sunset | removed
owner: ""                   # the person who approves the bet and makes the keep or kill call
builder: ""                 # who or what builds it (team, or agent id)
judge: ""                   # who or what evaluates it; never the builder
approved: null              # date the owner approved; locks the sections below

hypothesis:
  we_believe: ""            # the change
  for: ""                   # the users, specifically
  will_result_in: ""        # the outcome you could observe
  because: ""               # the mechanism

evidence: []                # optional: links or one-line facts behind the bet (feedback themes, telemetry, interviews)
                            # these are the bet's drivers: every review re-checks that they still hold

strategy:                   # optional: link to the product strategy; delete this block if there's no strategy file
  policy: ""                # the policy this bet serves, such as P-01
  area: ""                  # the product area, such as payments
  horizon: bet              # tune (H1, proven) | bet (H2, chartered bet) | probe (H3, cheap test of a hunch)
  opportunity: ""           # the opportunity brief it came from, such as OPP-001

value_type: frequency       # frequency, or insurance for features valuable when needed (export, audit, recovery)
insurance_reason: ""        # required for insurance features

needle:                     # one metric at rung 5 or higher on the Needle Ladder
  name: ""
  rung: task_success        # task_success | user_outcome | business_outcome
  definition: ""            # numerator, denominator, unit, window: precise enough that two people get the same number
  source: ""                # events, table or survey it comes from
  baseline: measure_before_launch   # a number once measured; never a guess
  target: null
  direction: increase       # increase | decrease
  min_change: null          # smallest change worth keeping the feature for; a percentage like '10%' if the baseline is unknown
  window_days: 28

guardrails:                 # what must not get worse
  - name: ""
    limit: ""

diagnostics: []             # usage, adoption and other rung 1 to 4 numbers: they explain results, never decide them

evaluation:
  method: before_after      # ab_test | holdback | before_after | qualitative
  weekly_users: null
  review_date: null         # the expiry date: at most 45 days after approval
  keep_if: ""
  kill_if: ""
  iterate_if: ""
  if_inconclusive: sunset   # sunset | iterate (never keep)
  look_at: ""               # real sessions or people you will check, beyond the dashboard

removal:
  flag: ""                  # kill switch
  code_paths: []
  data: ""                  # what it stores, and what happens to that data on removal
  estimate_hours: null

decision_log: []            # date, decision (keep | iterate | sunset | removed), evidence, decided_by, next_review
amendments: []              # date, field, from, to, reason, approved_by
```
