# Adding an outcome charter to a Spec Kit spec (`spec.md`)

[Spec Kit](https://github.com/github/spec-kit) specs already have a mandatory **Success Criteria** section with measurable outcomes (SC-001, SC-002...). Keep it. The charter adds what Spec Kit leaves open: which criterion decides the feature's fate, by when, what must not get worse, and how to remove the feature if it misses.

**What to add:**

1. **Tag each success criterion** with a short trailing note in italics, for example `*(rung 3, adopted: diagnostic)*`. Criteria about completing a flow are usually rung 3 (adopted): keep them as diagnostics. Load and latency criteria are performance requirements, not on the ladder: keep them as requirements, and use them as guardrails.
2. **Make sure at least one criterion is a result** (rung 5 or higher). If none is, add one as the next SC number, starting the line with `**New:**`.
3. **Add an `## Outcome charter` section** after Success Criteria and before Assumptions, using `templates/outcome-charter.md`. In `needle.definition`, reference the criterion it measures, for example "SC-003".
4. **Put the measurement in the plan.** When you run `/speckit.plan` and `/speckit.tasks`, the plan should include the instrumentation events the needle and guardrails need, and the feature flag. Instrumentation is part of the feature, not a follow-up task.

Spec Kit's agents (the builder) should not edit the Outcome charter after approval. Give evaluation to a separate judge agent or person.
