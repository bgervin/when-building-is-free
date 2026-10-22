### [OPP-000] [the opportunity in a few words]

<!--
One brief per shortlisted opportunity. It sits in the triage report (or its own
file) and is the bridge to a charter: its evidence and rung become the charter's
hypothesis, needle and `evidence`, and its strategy link becomes the charter's
`strategy` block.

Write the opportunity, not the feature. "Office managers lose hours chasing late
payments" is an opportunity; "add SMS reminders" is one possible solution to it.
-->

**Who struggles, with what:** [one sentence, in the users' terms]

**Evidence:** [distinct accounts, how many in the target segment, the telemetry that shows the failure, one or two quotes]

```opportunity-brief
id: OPP-000                 # placeholder: change it, or the validator skips this block
status: shortlisted         # shortlisted | probing | chartered | parked | ruled_out
area: ""                    # an area id from the strategy
segment: ""                 # a target segment id from the strategy
opportunity: ""             # who struggles, with what: the need, not the requested feature
requests: []                # the issues or feedback items grouped here, such as "#212"
breadth:
  accounts: 0               # distinct accounts asking, not mentions or votes
  in_segment: 0             # how many of them are in the target segment
  window: ""                # the period counted, such as Q3 2026
rung: user_outcome          # where the job fails: task_success | user_outcome | business_outcome
telemetry: ""               # what usage data shows about the failure, or "none yet"
severity: ""                # how bad it is for them, in their words
strategy:
  policy: ""                # the policy that makes this worth doing, such as P-01
  horizon: bet              # tune (H1) | bet (H2) | probe (H3)
flags: []                   # any of: loudest_voice, hostage_customer, rearview_mirror, hippo, parity_reflex, zombie_commitment
flag_notes: ""              # required when flagged: why it should still go ahead
probe_ends: null            # for status probing: the date the probe stops and a decision is made
charter: ""                 # for status chartered: the charter id, such as FC-007
ruling: ""                  # for status ruled_out: the ruling id, such as R-004
```
