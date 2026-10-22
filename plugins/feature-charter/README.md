# feature-charter

An agent skill that adds an **outcome charter** to the specs your team already writes: PRDs, GitHub issues, user stories, Spec Kit specs and RFCs. It doesn't replace your template.

A charter turns a spec's success claim into a pre-registered bet:

- **The bet:** we believe this change, for these users, will produce this outcome, because of this mechanism.
- **The needle:** one result metric at rung 5 or higher on the Needle Ladder (task success, user outcome or business outcome). Usage numbers stay as diagnostics.
- **Guardrails:** what must not get worse.
- **Rules written before the data arrives:** keep if, kill if, iterate if. Inconclusive never means keep.
- **An expiry date:** first review within 45 days of approval; each renewal within 90.
- **A removal plan:** kill switch, code paths, stored data, hours to delete.

## What's inside

| Path | What it is |
|---|---|
| `skills/feature-charter/SKILL.md` | The instructions agents follow: enrich a spec, gate a build, run a review, sunset and remove |
| `skills/feature-charter/templates/outcome-charter.md` | The section to add to any spec |
| `skills/feature-charter/templates/snippets/` | Where and how to add it in a PRD, GitHub issue form, user story, Spec Kit spec, RFC and pull request template |
| `skills/feature-charter/references/` | The Needle Ladder and needle guide, the review protocol, and a worked example |
| `skills/feature-charter/scripts/charter.py` | Validator: checks charters, enforces pre-registration, lists overdue reviews |
| `skills/feature-charter/assets/charter-gate.yml` | GitHub Actions workflow that enforces all of the above |

## Install

In Claude Code (2.1.275 or later):

```text
/plugin install feature-charter --marketplace bgervin/when-building-is-free
```

In GitHub Copilot CLI:

```bash
copilot plugin marketplace add bgervin/when-building-is-free
copilot plugin install feature-charter@when-building-is-free
```

## Use it

Ask your agent in plain language, for example:

- "Add an outcome charter to docs/specs/payment-reminders.md."
- "Review the success metrics in this PRD. Which ones are activity and which are results?"
- "FC-007's review date is today. Run the review."

The validator needs Python 3.9+ and PyYAML. Run it from wherever the skill folder is; for example, after copying the skill into a repository's `.github/skills/`:

```bash
pip install pyyaml
python .github/skills/feature-charter/scripts/charter.py validate docs/specs/
python .github/skills/feature-charter/scripts/charter.py due docs/specs/
python .github/skills/feature-charter/scripts/charter.py require FC-007 docs/specs/
```

With a plugin install, ask your agent to run it.

After a review decision, the skill may offer a link to share an anonymized story on GitHub. Nothing is sent unless you submit the form yourself; set `story_prompt: false` in `.feature-charter.yml` to turn the offer off. The skill sends no telemetry.

See the [repository README](../../README.md) for installation in Claude Code, GitHub Copilot and other agents, and for before and after examples.

MIT licensed.
