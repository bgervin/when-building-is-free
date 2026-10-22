# Adding an outcome charter to an RFC or design doc

RFCs and design docs focus on how to build something. Keep every section. The charter adds whether it was worth building.

**Where it goes:**

| If the doc has... | Put the charter... |
|---|---|
| A "Success metrics", "Goals" or "Measuring success" section | Directly after it |
| No success section | After the proposal or design, before risks, alternatives or rollout |

**What else to add, each line starting with `**New:**`:**

- **Design:** the events the needle and guardrails need. Instrumentation is part of the design.
- **Rollout:** "Ships behind flag `<flag>`; review on `<review date>`." If there's a beta, say whether the review happens before rollout widens.
- **Open questions:** add the section if the doc has none, for anything only the owner can answer.

**Mapping the status:** an RFC "In review" or "Draft" maps to `status: proposed`. "Accepted" or "Approved" maps to `approved`, with the acceptance date in `approved`.

**Builder and judge:** the RFC author is often the builder. Name a different person, team or agent as judge.
