# Adding an outcome charter to a user story (Jira, Linear, Azure Boards)

Keep the story format ("As a... I want... so that...") and the acceptance criteria. They answer "did we build it right?", which is rung 1 on the Needle Ladder. The charter answers "was it worth building?"

**What to add:**

1. Under the acceptance criteria, add an **Outcome charter** heading and paste the two sentences and the `feature-charter` block from `templates/outcome-charter.md`.
2. Use the story's "so that..." clause as the starting point for `hypothesis.will_result_in`. It is usually the outcome the team forgot to measure.
3. If your tracker strips code fences, put the block in a linked spec file or a pinned comment, and link it from the story.

**For small stories**, a charter can cover an epic instead: give the epic the charter, and have each story reference its `FC-` id. Charter the unit you would actually keep or remove.

**Insurance features** (export, audit logs, account recovery) are valuable when needed, not when used often. Set `value_type: insurance`, explain why in `insurance_reason`, and make the needle about reliability when invoked, not frequency.
