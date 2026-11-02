# The six failure modes

Each is the same mistake: something other than evidence of user need decides the roadmap. Flag them, explain the flag in one line, and leave the call to the owner. A flag is not a veto; some flagged requests are still right.

| Flag | What stands in for evidence | Signals to look for | The question to put to the owner |
|---|---|---|---|
| `loudest_voice` | Volume | Many votes or comments from few accounts; one long thread; votes from one company's staff; a recent spike after a social post | How many distinct accounts in the target segment, and what does telemetry say about everyone who didn't write in? |
| `hostage_customer` | One account's importance | One account (or one deal) behind the whole case; sales escalation; "they'll churn without it"; a launch partner and a conference date; a few engaged accounts speaking for a whole segment; "essential for regulated industries" | Can you name three other accounts in the target segment who would use this within 90 days? If not, is this a services deal? For a regulated-industry claim: does the telemetry show regulated customers behaving differently? |
| `rearview_mirror` | A competitor's launch | The request cites a competitor; it arrived in the weeks after their announcement; no lost deals or churn reasons cite it | Which of our users fail at what without it? Is it now table stakes (lost deals, churn reasons), or a delighter we're copying? |
| `hippo` | Seniority | Filed or forwarded by an executive; no user named; "the CEO wants" | Will the sponsor sign a charter with kill criteria and a review date, like any other bet? |
| `parity_reflex` | A sibling product's roadmap | "Product B has it, so Product A needs it"; parity checklists; two products for different audiences | Is this capability on the strategy's short parity list? If not, what does this product's own audience need? |
| `zombie_commitment` | A past promise | A feature committed to internally whose reasons have changed; "we said we'd ship it"; a charter whose evidence no longer holds | Do the drivers in the original case still hold? If a driver is gone, the bet reopens, whatever was promised. |

## Notes on each

**Loudest voice.** Feedback is self-selected. Online reviews skew to the extremes (the J-shaped distribution, Hu, Pavlou and Zhang), and in app store reviews only about 7% are feature requests (Pagano and Maalej, 2013). Count distinct accounts, then how many are in the target segment. Mentions and votes are diagnostics, like usage in the Needle Ladder.

**Hostage customer.** It comes in disguises:

- **The stage customer:** a customer willing to announce the feature with you at a conference. The keynote date holds the roadmap hostage as much as the customer does.
- **The proxy segment:** a handful of highly engaged accounts (incubations, forward-deployed engagements, a partner team's favourites) speaking for a segment of thousands.
- **The regulated-industry card:** "it's essential for regulated industries." Sometimes true, often untested. Before accepting it, split the telemetry by regulated and non-regulated customers; if they behave the same, the claim isn't evidence.

A design partner stands in for a segment you've chosen; their needs generalize, so building for them is research. A hostage customer is the segment; building for them is services work paid for by the roadmap. Free building makes this worse: when the build takes three weeks instead of six months, you can say yes to ten of them. The attention and maintenance costs stay the same, and the opportunities that moved while you weren't looking don't come back. The real cost isn't the build. It's the complexity every other customer and every future feature carries. The `services` ruling exists for this: worth doing, priced and staffed as a deal.

**Rearview mirror.** Armstrong and Collopy (1996) found that competitor-oriented objectives harmed profits across lab experiments and 54 years of data on 20 companies. That is about making a competitor the goal, not about never shipping a parity feature. In the Kano model yesterday's delighter becomes tomorrow's must-have; the test is evidence from your own segment.

**HiPPO.** Highest Paid Person's Opinion: the term came out of Microsoft's experimentation team in 2006. Most ideas, including senior people's, don't move the metric they target (Kohavi reported about a third do). The counter is not to refuse the sponsor but to give their idea the same charter and expiry date as everyone else's.

**Parity reflex.** Internal competition: two products for different audiences held to feature parity. It is the rearview mirror pointed at your own company. The counter is a parity policy in the strategy that names the few capabilities that must match, and why; build those once, in the shared platform.

**Zombie commitment.** Escalation of commitment (Staw, 1976): people who made the original decision invest more after bad news, to justify it. A charter's `evidence` records the drivers; each review re-checks them.
