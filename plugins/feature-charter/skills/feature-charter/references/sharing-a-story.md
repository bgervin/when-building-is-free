# Offering to share a charter story

After a review records a decision, you may offer the person one optional way to share how it went. The stories show the skill's maintainer whether charters lead to real keep, iterate, sunset and removal decisions. Nothing is sent unless the person submits it themselves.

## When to offer

- Only at the end of a review that recorded a decision (Workflow C), or when a removal is recorded (Workflow D).
- Once per decision. If the person declines or doesn't respond, drop it and don't raise it again.
- Never while drafting a charter or gating a build.
- Never if the person has said they don't want these prompts, or the repository's `.feature-charter.yml` sets `story_prompt: false`.

## Rules

1. **Never submit it yourself**, even if you have GitHub access. You only offer a link. Submitting is the person's decision.
2. **Anonymize the draft.** Leave out company, product, customer, team and people names, internal URLs, and every number. The person can add numbers on the form if they choose.
3. **Show exactly what the link contains** before you offer it.
4. **Keep the story to two or three sentences:** the bet in plain words, what the review showed (no figures), and the decision.

## Building the link

Use the validator so the link holds only the decision, the rung, the spec format and the story text you showed the person:

```bash
python scripts/charter.py story-link FC-007 docs/specs/ --format "GitHub issue" \
  --story "We bet that automatic payment reminders would get invoices paid sooner. The review showed a clear drop in days to paid and no complaints. We kept it and will confirm with a holdback."
```

It prints a URL that opens a pre-filled "Charter story" form on GitHub. The person answers one more question there ("Would this decision have happened without the charter?") and decides whether to submit.

## What to say

End your review report with something like:

> This charter led to a **sunset** decision. If you'd like to share how it went with the maintainer of the feature-charter skill, this link opens a pre-filled GitHub form. It contains only the decision, the rung, the spec format and this summary; nothing is sent unless you submit it:
>
> "We bet that ... The review showed ... We decided to ..."
>
> [Share the story](URL)
