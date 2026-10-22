# Adding an outcome charter to a PRD

Keep your PRD template. Make two changes.

**1. Sort your existing success metrics by rung.** Most PRD "success metrics" sections mix outcomes with activity. Don't delete anything; label it.

| If the metric measures... | Rung | Where it goes |
|---|---|---|
| Revenue, retention, cost to serve | 7 business outcome | Can be the needle |
| The user's goal (time saved, invoices paid, errors avoided) | 6 user outcome | Can be the needle |
| Doing the job better (completion rate, time on task, error rate) | 5 task success | Can be the needle |
| Usage, adoption, clicks, active users, satisfaction with the feature itself | 1 to 4 activity | Diagnostics |

Pick one result metric as the needle. Everything else stays in the PRD as a diagnostic or a guardrail.

**2. Add the Outcome charter section** from `templates/outcome-charter.md` directly under "Success metrics" (or "Goals and metrics"). If your PRD has a "Launch plan" or "Rollout" section, add one line there: "Ships behind flag `<flag>`; review on `<review date>`."

Common PRD sections and what they feed:

| PRD section | Charter field |
|---|---|
| Problem / Background | `hypothesis.because`, and optional `evidence` links |
| Target users / Personas | `hypothesis.for` |
| Goals | `hypothesis.will_result_in` |
| Success metrics | `needle`, `guardrails`, `diagnostics` |
| Non-goals | Nothing; leave it as is |
| Rollout / Launch plan | `evaluation.method`, `removal.flag` |
| Open questions | Anything you can't fill yet, such as an unmeasured baseline |
