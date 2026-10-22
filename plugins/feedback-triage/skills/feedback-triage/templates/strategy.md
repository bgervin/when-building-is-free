# Product strategy: [product name]

<!--
One file, in the repository, that people and agents both read.
The prose is for people. The block underneath is the same strategy in a form
triage, charters and the bet board can check against.

The test for every line: could it decide a real request? A line that can't
is fluff (Rumelt). A target ("grow ARR 30%") is a goal, not a strategy;
put it in the diagnosis or leave it out, and write the policy that says how
you'll choose.

Keep it short: one screen of prose, then the block.
-->

## The challenge

[Two or three sentences: what is hard right now, and why. Name the obstacle, not the goal.]

## Who we serve, and who we don't

[One sentence each. Saying who the product is not for is what makes triage possible.]

## How we'll choose

[Three to six guiding policies in plain words. Each one should say yes to some requests and no to others.]

## Where the effort goes

[The horizon mix as a share of active bets and probes, and why. Tune (H1): features already proven to move a needle. Bet (H2): chartered bets with a 45-day review. Probe (H3): cheap tests of a hunch.]

## What we've ruled out

[The rulings table below is generated from the block's rulings by the bet board. A no recorded with its reason and a reopen condition stops the same request being re-argued every quarter.]

```product-strategy
id: ST-000                 # placeholder: change it (for example ST-2026H2), or the validator skips this block
name: ""                   # product name
status: draft              # draft | approved | retired
owner: ""                  # who owns the strategy and signs its rulings
approved: null             # date the owner approved it
review_date: null          # a strategy is a bet too: review it within 120 days of approval

diagnosis: ""               # the challenge, in two or three sentences (use > and indented lines for more than one)

segments:
  target:                  # who the product is for; triage counts breadth inside these
    - id: SEG-01
      name: ""
      definition: ""       # precise enough to tell whether an account is in or out
  not_target:              # who it is not for; their requests are services work or a no
    - id: SEG-X1
      name: ""
      why: ""

policies:                  # guiding policies: how you choose, not what you hope to reach
  - id: P-01
    statement: ""          # "We ..." in one sentence
    decides: ""            # one real request it says yes or no to, and which

areas:                     # product areas triage sorts into; match your issue labels
  - id: ""                 # for example payments
    name: ""
    labels: []             # issue labels for this area, such as area/payments
    owner: ""

horizons:                  # share of active bets and probes (a count, not hours); must add up to 100
  tune: 30                 # H1: proven features, renewed by charter review, deleted when they stop earning
  bet: 50                  # H2: chartered bets
  probe: 20                # H3: cheap probes of a hunch: interviews, fake doors, a prototype to 10 users

rulings: []                # what you have decided not to do, so triage can answer it next time:
                           # - id: R-001
                           #   request: ""          # the request, in the asker's words
                           #   ruling: "no"         # "no" | not_now | services (worth doing for one customer, priced as a deal); quote "no"
                           #   policy: P-01         # the policy that decides it; or none, with policy_gap: the policy that's missing
                           #   reason: ""
                           #   reopen_if: ""        # the evidence that would reopen it
                           #   decided_by: ""
                           #   date: YYYY-MM-DD
                           #   issues: []           # linked issues, closed with a link to this ruling
```
