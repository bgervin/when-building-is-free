# FC-001: The feature-charter skill itself

This repository holds itself to the rules it publishes. The skill is a feature; this is its charter. Stars, installs and clones are diagnostics. The needle is whether charters lead to decisions.

**The bet:** We believe the feature-charter skill, for product managers running agentic software factories, will get features to an explicit keep, iterate or sunset decision on schedule, because an expiry date and rules written in advance leave no room to avoid deciding.

**How we'll know:** At least 3 charters, in public repositories or reported through the Charter story form, record a decision by December 6, 2026. Zero means the approach needs rethinking.

```feature-charter
id: FC-001
status: approved
owner: Barry Gervin
builder: Claude coding agents
judge: Barry Gervin, from public code search and charter stories
approved: 2026-10-22

hypothesis:
  we_believe: an agent skill that adds an outcome charter to the specs teams already write
  for: product managers running agentic software factories
  will_result_in: features reaching an explicit keep, iterate or sunset decision on schedule
  because: an expiry date and rules written in advance leave no room to avoid deciding

evidence:
  - "Most teams measure AI software factories by PR velocity and have no alternative (When Building Is Free, No. 1)"

value_type: frequency

needle:
  name: Charters that reach a recorded decision
  rung: task_success
  definition: >
    Count of distinct charters outside the examples folder, in public repositories found by code
    search for feature-charter blocks or described in Charter story issues, that record a keep,
    iterate, sunset or removed decision between approval and the review date.
  source: monthly GitHub code search for feature-charter blocks, and issues labelled charter-story
  baseline: 0
  target: 3
  direction: increase
  min_change: 1
  window_days: 45

guardrails:
  - name: Reports that the skill rewrote or restructured someone's spec
    limit: zero credible reports; enriching, not replacing, is the core promise
  - name: Reports of the CI gate being switched off because it fails wrongly
    limit: no more than one

diagnostics:
  - Repository views, and visits referred from linkedin.com
  - Clones and unique cloners
  - Installs shown on skills.sh
  - Stars and forks
  - Charters approved in public repositories, with or without a decision yet

evaluation:
  method: qualitative
  review_date: 2026-12-06
  keep_if: 3 or more charters record a decision and both guardrails hold
  kill_if: no charter records a decision and none is approved in a public repository, or a guardrail is breached
  iterate_if: 1 or 2 decisions, or approved charters whose review dates fall after December 6
  if_inconclusive: iterate
  look_at: read every charter found and every charter story; ask two adopters how long enrichment took and what they'd change

removal:
  flag: the feature-charter entry in both marketplace manifests
  code_paths: [plugins/feature-charter/]
  data: none stored; charter stories stay as public issues
  estimate_hours: 2

decision_log: []
amendments: []
```
