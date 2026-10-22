# Writing the strategy file

A strategy file is useful only if it can decide a real request. Most strategy decks can't, because they are goals and roadmaps rather than strategy. Rumelt's four hallmarks of bad strategy are a good checklist: fluff, failure to face the challenge, mistaking goals for strategy, and bad strategic objectives.

## Where the content comes from

Never invent strategy. Draft it from what the team already has: strategy decks, planning docs, OKRs, the README, the pitch, past decisions in issues. Then ask the owner to confirm each policy. Mark anything you inferred as a proposal.

## The kernel

| Part | What good looks like | What to push back on |
|---|---|---|
| Diagnosis | Names the obstacle: "Contractors' customers pay late because invoicing happens days after the job, from the office" | A goal dressed as a diagnosis: "We need to grow ARR 30%" |
| Target segments | Precise enough to tell whether an account is in: "2 to 20 field staff, owner-operated" | "SMB", "everyone", "developers" |
| Not target | Someone real you will say no to, and why | Empty. A strategy that excludes nobody decides nothing |
| Policies | A rule for choosing: "We build for the person in the truck first; office-only features come second" | A target: "Increase NPS to 50"; a value: "Delight customers" |
| Policy `decides` | One real request it says yes or no to | Blank. If you can't name one, the policy is fluff |
| Areas | The product's real areas, matching issue labels | Org chart names that mean nothing to users |
| Horizon mix | A deliberate split, with a reason | 100% bet, or no mix at all |

## The policy test

For each policy, take five real open issues and ask: does this policy say yes, no, or nothing? A policy that says nothing to all five is decoration. Rewrite it or drop it.

## Parity policies

If two products serve different audiences and are pushed toward feature parity, write a policy that names the short list of capabilities that must match, and why: shared data, a shared admin, a contractual promise. Everything else needs evidence from that product's own audience. The `parity_reflex` flag points at this policy.

## Horizons

Horizons are defined by evidence, not time. When building is nearly free, build time no longer separates them; what you know does.

- **Tune (H1):** proven. A charter was kept. Renew by review; delete when it stops earning.
- **Bet (H2):** the opportunity is real, the solution is unproven. A charter with a 45-day review.
- **Probe (H3):** a hunch. A cheap test with an end date.

Expect the mix to shift toward probes. When probes are cheap, ten that each kill an idea in a week beat one six-month bet. Model releases can also turn an H3 hunch into H1 table stakes in weeks, so review the strategy on a schedule (the validator enforces 120 days) and ask what just became cheap.

## Rulings

A ruling is a recorded no: the request, the decision (`no`, `not_now` or `services`), the policy behind it, the reason, what would reopen it, who decided and when. Rulings are what make triage fast the second time, and they are the "not betting" column of the bet board. A ruling without a reopen condition is a grudge; the validator requires one.

`services` is for the hostage customer: worth doing for one account, priced and staffed as a deal, kept off the roadmap.
