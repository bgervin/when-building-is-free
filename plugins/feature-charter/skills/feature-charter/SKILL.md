---
name: feature-charter
description: Enrich an existing feature spec (PRD, GitHub issue, user story, Spec Kit spec, RFC) with an outcome charter that makes the feature a pre-registered bet with an expiry date, then gate builds on it and run keep-or-kill reviews. Use whenever someone writes, reviews or prioritizes a spec, PRD, issue or story for new functionality; when success metrics, acceptance criteria or OKRs for a feature are being set; when a feature's review date arrives; and when someone asks whether a feature moved the needle, is worth keeping, or should be deprecated, even if nobody says "charter."
---

# Feature charter

Every feature is a bet. Before it is built, write down what should change for users, the one number that will show it, what must not get worse, when you'll decide, and how you'd remove it. At the review date the feature re-earns its place with evidence, or it's removed.

This skill **adds** that to whatever spec the team already uses. It never replaces the team's template, restructures their document, or deletes what they wrote.

## Why

1. **Most ideas don't work.** At Microsoft, Ronny Kohavi reported that only about a third of ideas tested in controlled experiments improved the metric they targeted. A factory that ships faster without measuring results mostly ships things that don't help.
2. **Cost used to be the filter.** When a feature took weeks, someone had to argue for it. Agents remove that cost, and the argument goes with it.
3. **Adding is cheap, removing is expensive.** Without an expiry date and a removal plan, software grows like the Winchester Mystery House.
4. **Goalposts move after launch.** Success defined before the data arrives is the only honest kind (pre-registration).

## The charter in one look

The charter is a short section, **Outcome charter**, added to the existing spec: two plain sentences for people, and a fenced `feature-charter` YAML block that agents and the validator can check. The full template with comments is in `templates/outcome-charter.md`.

| Part | What it holds |
|---|---|
| The bet | `hypothesis`: we believe [change] for [users] will [outcome] because [mechanism] |
| The needle | One metric at rung 5 or higher on the Needle Ladder, with baseline, target and `min_change` |
| Guardrails | At least one thing that must not get worse |
| Rules | `keep_if`, `kill_if`, `iterate_if`, written before the data arrives; inconclusive never means keep |
| Expiry date | `review_date`, at most 45 days after approval by default |
| Removal plan | Kill switch, code paths, stored data, hours to delete |

Hypothesis, needle, guardrails and evaluation lock when `approved` gets a date. After that they change only through an entry in `amendments` approved by the owner.

## Workflow A: Enrich an existing spec (the main job)

1. **Read the whole spec first** and identify its format: PRD, GitHub issue, user story, Spec Kit `spec.md`, RFC or design doc, or something custom. For format-specific placement, read the matching file in `templates/snippets/` (`prd.md`, `github-issue-form.yml`, `user-story.md`, `spec-kit.md`, `rfc.md`). For anything else, follow `rfc.md`.
2. **Keep the author's structure and words.** Don't rename sections, reorder them or rewrite requirements. Your changes are additions and annotations, marked the same way every time:
   - A line or list item you add starts with `**New:**`.
   - A note on an existing line goes at its end in italics: `*(rung 3, adopted: diagnostic)*`. The author's words stay as they were.
   - A new section (the Outcome charter, or Open questions if the spec has none) is an addition, not a restructure.
3. **Find the success claim.** Look in success metrics, goals, success criteria, KPIs, the "so that" clause of a story, and the acceptance criteria. Classify each metric with `references/needle-guide.md`; its section 2 covers metrics that aren't a rung, such as volume counts and performance requirements.
4. **Annotate, don't delete.** Leave activity metrics (usage, adoption, clicks, MAU, completion of a flow) in place and add a short note, such as "(rung 3: diagnostic)". If no metric is a result, propose one and say it's new.
5. **Add the Outcome charter section** where the spec's success metrics are, or at the end if there are none. Fill the two sentences and the block from what the spec already says. Use the spec's own terms.
6. **Don't invent facts.** Never make up a baseline, a traffic number, an owner or a date. Use `measure_before_launch` for unknown baselines and leave unknown fields empty, each with a question in the spec's open questions section (add one if there is none). `owner`, `builder`, `judge`, `source` and `removal` may stay empty while the charter is `proposed`; the validator only warns.
   Targets, thresholds and `min_change` are different: they are the bet, so propose them, say they are proposals, and ask the owner to confirm. If the baseline is unknown, state `min_change` as a percentage, such as `'10%'`.
7. **Pick an evaluation method that fits the traffic** (needle guide, section 7). Small products usually need `before_after` or `qualitative`.
8. **Give the charter an id.** Use the next unused `FC-` number in the repository (the validator lists the ids it finds), or the team's tracker numbers if they set `id_pattern` in `.feature-charter.yml`. Never leave the template's `FC-000`: the validator skips it as a placeholder.
9. **Run the validator** and fix every error that the spec's information allows. Warnings about unknowns are fine at `status: proposed`.
10. **Report back briefly:** what you added, which existing metrics you annotated and why, and the questions only the owner can answer.

If there is no spec at all, suggest the team's usual template, or write a minimal one-page spec (problem, users, requirements, acceptance criteria) and add the charter to it.

## Workflow B: Gate a build or PR

1. The work should reference an approved charter (`FC-` id) in the spec or PR body. `status: proposed` is not approved. `charter.py require FC-007 docs/` checks it, and `charter.py require docs/ --text "$PR_BODY"` checks every id a pull request mentions.
2. Confirm the feature ships behind `removal.flag` and emits the events the needle and guardrails need. A feature that can't be measured can't be judged, so instrumentation is part of the feature.
3. If the change touches a locked section, run the validator with `--baseline` against the previous version. It fails unless a matching approved amendment exists.

`assets/charter-gate.yml` is a GitHub Actions workflow that automates these checks.

## Workflow C: The review date

Follow `references/review-protocol.md`. The judge, never the builder, compares results with the written rules, checks guardrails, looks at real examples and records the decision in `decision_log`. A breached guardrail means sunset. Keep sets a `next_review` within 90 days.

## Workflow D: Sunset and removal

Sunset turns the flag off. Removal deletes the code, tests, docs and stored data. A feature stuck in sunset still costs upkeep. Record `removed` when the deletion merges.

## Builder and judge are different

The agent or team that builds a feature must not evaluate it or edit its locked sections. A builder that can see and redefine its own needle will move the number without moving the outcome (Goodhart's law). The validator enforces `builder` and `judge` being different once the charter is approved; respect the spirit of it too.

## Validator

`scripts/charter.py` is in this skill's folder; run it with that path (for example `.github/skills/feature-charter/scripts/charter.py` when the skill is copied into a repository). It needs Python 3.9+ and PyYAML (`pip install pyyaml`). It reads `feature-charter` blocks in Markdown, plus standalone `.yaml` or `.json` charters. Folder scans skip this skill's own templates and examples.

```bash
# Check one spec, or every spec under a folder
python scripts/charter.py validate docs/specs/payment-reminders.md
python scripts/charter.py validate docs/specs/

# Pre-registration check against the previous version
git show origin/main:docs/specs/payment-reminders.md > /tmp/base.md
python scripts/charter.py validate docs/specs/payment-reminders.md --baseline /tmp/base.md

# Reviews that are overdue or due soon, and sunsets never removed
python scripts/charter.py due docs/specs/
```

Defaults (45 days to first review, 90 per renewal, 1,000 weekly users before A/B testing is sensible) can be changed in `.feature-charter.yml`, which the validator looks for in the current folder and its parents up to the repository root (`templates/feature-charter.config.yml` has every setting). One approved amendment to `evaluation.review_date` can extend a review to twice the limit, for broken data or a seasonal feature. When a rule doesn't fit, fix the charter or use the visible escape hatches (for example `value_type: insurance`) rather than working around the check.

## Files

| File | Read when |
|---|---|
| `templates/outcome-charter.md` | Adding a charter to any spec |
| `templates/snippets/` | Placing it in a PRD, GitHub issue form, user story, Spec Kit spec, RFC or PR template |
| `references/needle-guide.md` | Choosing the needle, guardrails and evaluation method |
| `references/review-protocol.md` | A review date arrives, or someone asks whether to keep a feature |
| `references/example-enriched-issue.md` | Before your first enrichment, to see the expected size and tone |
| `assets/charter-gate.yml` | Setting up enforcement in a GitHub repository |
| `scripts/charter.py` | Validating charters and listing due reviews |
