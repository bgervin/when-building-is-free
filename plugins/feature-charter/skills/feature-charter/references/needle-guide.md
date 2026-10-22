# Choosing the needle

The needle is the one number that decides whether a feature earned its place. This guide covers picking it, protecting it from gaming, and measuring it when you don't have much traffic.

## Contents
1. The Needle Ladder
2. Placing common metrics
3. Picking the needle
4. Why usage is not the needle
5. Insurance features
6. Guardrails and Goodhart's law
7. Evaluation methods by traffic
8. Bad needles and better ones

## 1. The Needle Ladder

Seven rungs between "shipped" and "worth it." Each rung is necessary for the one above it, and none of the lower rungs proves the upper ones.

| Rung | Name | Question | Example signal |
|---|---|---|---|
| 1 | shipped | Is it live and reachable? | Flag on, route live, acceptance criteria pass |
| 2 | discovered | Do people find it? | Share of active users who saw the entry point |
| 3 | adopted | Do people try it? | Share who used it at least once |
| 4 | retained | Do people come back to it? | Share of adopters using it again in week 4 |
| 5 | task_success | Does it do the job better than before? | Completion rate, time on task, error rate |
| 6 | user_outcome | Did the user's goal move? | Invoices paid sooner, hours saved |
| 7 | business_outcome | Did the business move? | Retention, revenue, cost to serve |

Rungs 1 to 4 are activity. Rungs 5 to 7 are results. The needle is a result. Activity numbers go in `diagnostics`, where they explain why the needle did or didn't move.

The ladder builds on Google's HEART framework (Rodden, Hutchinson and Fu, CHI 2010), Kohavi's Overall Evaluation Criterion, and the output versus outcome distinction.

## 2. Placing common metrics

Not every metric in a spec maps neatly to a rung. Label these consistently:

| Metric | Label | Use it as |
|---|---|---|
| Views, opens, impressions, "saw the entry point" | rung 2, discovered | Diagnostic |
| First use, turned it on, completed a setup flow | rung 3, adopted | Diagnostic |
| Weekly or repeat use | rung 4, retained | Diagnostic |
| Volume counts: items sent, suggestions accepted, jobs per session, PRs merged | volume count, activity | Diagnostic. Never a target: volume rises without value |
| Performance and reliability: latency, uptime, error budgets | a requirement, not on the ladder | Keep as a requirement; often a good guardrail |
| Satisfaction with the feature itself (thumbs up, feature CSAT) | activity | Diagnostic or guardrail |
| Completion, time on task, error rate for the job | rung 5, task success | Can be the needle |

## 3. Picking the needle

1. Start from `hypothesis.will_result_in`. Measure that outcome as directly as you can.
2. Go as high on the ladder as you can measure within the review window. Rung 7 is ideal but often slow or noisy; rung 5 or 6 is usually the right trade.
3. If the true outcome is slow (retention, churn), pick a leading indicator that plausibly predicts it, and say so in the definition. Combining several short-term proxies into one predicted outcome is the idea behind the surrogate index (Athey, Chetty, Imbens and Kang).
4. Write the definition so two people get the same number: numerator, denominator, unit (per user, per account, per invoice) and window.
5. Set `min_change`: the smallest improvement that pays for the feature's upkeep. A real but tiny gain may not be worth maintaining forever.
6. Never guess a baseline. Use `measure_before_launch` and make measuring it the first task.

## 4. Why usage is not the needle

1. Usage can signal failure. Heavy use of help, retries or back-and-forth navigation often means the product is confusing.
2. Usage doesn't prove cause. Users may have reached the same outcome another way.
3. Usage is easy to inflate. Notifications, prompts and defaults drive clicks without delivering value, and an agent given a usage target finds those levers fast.
4. Usage and value come apart. In Microsoft's Office mobile contextual command bar experiment, edits rose substantially while two-week retention didn't change significantly (Fabijan et al., ICSE 2017).
5. Product-level counts (DAU, WAU, MAU) are too coarse to tell whether one feature worked, and they count presence, not value.

If you need an "active" number, define it around value: an account that had an invoice paid this week, not one that logged in.

## 5. Insurance features

Some features earn their keep by rarely being used: data export, audit logs, account recovery, compliance reports. Set `value_type: insurance`, explain why in `insurance_reason`, and choose a needle about reliability when invoked (the export opens cleanly in the accountant's software, recovery succeeds within 10 minutes), not frequency. The validator allows an activity rung for insurance features with a warning, but a reliability needle at rung 5 is better.

## 6. Guardrails and Goodhart's law

"When a measure becomes a target, it ceases to be a good measure." Four ways it happens, and the defense for each (Manheim and Garrabrant, 2018):

| Variant | What happens | Defense |
|---|---|---|
| Regressional | The proxy is noisy, so the winner was partly luck | Longer windows, holdbacks, replication |
| Extremal | Proxy and goal agree in normal ranges but split at the extremes | Guardrails with ceilings, not just floors |
| Causal | You push something correlated with success that doesn't cause it | Experiments or holdbacks, not correlations |
| Adversarial | An optimizer, person or agent, exploits the gap | Separate builder and judge; lock the definition; look at real examples |

Every charter needs at least one guardrail. Pair it with the needle: speed with error rate, automation with complaints, adoption with satisfaction.

Give each guardrail a margin. "Reopen rate no higher than before" can be breached by normal week-to-week noise, and a breached guardrail means sunset. Write "rises by no more than 1 point", sized from how much the number usually moves. If you don't know the usual variation, say so and ask; don't invent it.

Factory metrics fail the same way. PR velocity, time to merge, human interactions per PR and tokens burned all measure how hard the factory runs, not whether what it ships works.

## 7. Evaluation methods by traffic

| Method | Use when | Notes |
|---|---|---|
| `ab_test` | Thousands of weekly users in the affected segment | Randomize and compare. Run a power calculation first. |
| `holdback` | Moderate traffic, or to check a launched feature still earns its keep | Keep the feature off for a small slice. Also the cleanest test before deprecating. |
| `before_after` | Low traffic, typical for small business products | Same accounts before and after. Log anything else that shipped to them, and watch for seasonality. |
| `qualitative` | Very low traffic, or an outcome that is hard to count | Structured interviews or session reviews. Decide in advance what you'd need to hear to keep it. |

A staged rollout is a comparison too: beta customers against similar customers not yet in the beta. Record it as `holdback` and name both groups in the definition.

Seasonal features (heat waves, tax time) should be approved so the review window covers the season. If the season arrives late, one approved amendment can extend the review date.

Small products can't reach statistical significance. That doesn't remove the need to write the bet down first; it changes the evidence. Write `keep_if` in terms you can observe: "at least 4 of the 6 office managers say they stopped chasing invoices by phone, and median days to paid drops by 4 or more."

## 8. Bad needles and better ones

| Bad needle | Why | Better needle |
|---|---|---|
| Clicks on the new dashboard | Activity, easy to inflate | Share of weekly reviews finished without exporting to a spreadsheet |
| MAU | Product-wide, insensitive to one feature | Share of accounts completing the core job in the period |
| AI suggestions accepted | Output, and gameable | Share of tickets resolved on first reply without reopening within 7 days |
| Checklist completion rate | Rung 3: finishing the checklist isn't the goal | Share of new workspaces that complete the core job within 7 days |
| NPS | Slow, broad, easy to skew | Task completion plus one in-context satisfaction question |
