# Contributing

Thanks for helping. The most useful contributions are:

1. **Before and after examples** in spec formats not covered yet: RFCs, Kiro specs, Linear projects, Azure Boards features, Shape Up pitches. Add a folder under `examples/` with `before.md`, `after.md` and a short entry in `examples/README.md`. Keep the original spec intact in `after.md`; the point is enrichment, not replacement.
2. **Validator fixes** with a test in `tests/`.
3. **Field reports**: a charter that led to a keep, iterate, sunset or removal decision (use the Charter story issue form), or one that didn't fit your situation (open a regular issue).

## Ground rules

- The skill adds to a team's spec. Changes that make it rewrite or restructure specs won't be accepted.
- Don't put real customer data or internal company documents in examples. Fictional products are fine.
- Plain language. No em dashes in docs.

## Checks

```bash
pip install pyyaml pytest
pytest -q
claude plugin validate .
```

CI runs the same checks on every pull request. To validate examples by hand, check one file at a time: `examples/01-*/after.md` and `review.md` are two snapshots of the same charter, so a folder scan reports their shared id as a duplicate.
