#!/usr/bin/env python3
"""Feature charter validator.

A feature charter is a short, machine-checkable block you add to the spec you
already use (PRD, GitHub issue, user story, Spec Kit spec, RFC). It turns the
spec's success claim into a pre-registered bet with an expiry date.

Where charters live:
  * Inside Markdown: a fenced code block whose language is `feature-charter`.
    A spec may hold one block; a file may hold several.
  * Standalone: a .yaml, .yml or .json file containing one charter.

Commands:
  validate PATH [PATH ...] [--baseline OLD] [--strict] [--json] [--today YYYY-MM-DD] [--config FILE]
  due PATH [PATH ...] [--soon-days N] [--json] [--no-fail] [--today YYYY-MM-DD] [--config FILE]
  require ID PATH [PATH ...]   exit 0 only if charter ID exists, is approved or later, and validates

Blocks with the placeholder id FC-000 (used in templates) are skipped.

Exit codes: 0 ok, 1 problems found, 2 usage error.
Needs PyYAML (pip install pyyaml). JSON-only use needs nothing extra.

Settings (defaults below) can be overridden in .feature-charter.yml at the
repository root, or with --config.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

DEFAULTS = {
    "max_review_days": 45,          # first review no later than this after approval
    "max_renewal_days": 90,         # a keep or iterate decision must schedule the next review within this
    "low_traffic_weekly_users": 1000,
    "removal_warn_hours": 40,
    "sunset_stuck_days": 30,
    "id_pattern": r"FC-\d{3,}",
}
PLACEHOLDER_ID = "FC-000"   # the id used in templates; blocks with it are skipped

RUNGS = ["shipped", "discovered", "adopted", "retained", "task_success", "user_outcome", "business_outcome"]
RESULT_RUNG = RUNGS.index("task_success")
STATUSES = ["proposed", "approved", "building", "live", "under_review", "kept", "iterating", "sunset", "removed"]
APPROVED_OR_LATER = set(STATUSES) - {"proposed"}
MEASURED = {"live", "under_review", "kept", "iterating", "sunset", "removed"}
REVIEWABLE = {"approved", "building", "live", "under_review", "iterating", "kept"}
METHODS = {"ab_test", "holdback", "before_after", "qualitative"}
DECISIONS = {"keep", "iterate", "sunset", "removed"}
LOCKED = ["hypothesis", "needle", "guardrails", "evaluation"]
FENCE = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})[ \t]*feature-charter[ \t]*$", re.MULTILINE)
USAGE_WORDS = re.compile(
    r"\b(clicks?|page ?views?|sessions?|[dwm]au|daily active|weekly active|monthly active|active users?|"
    r"visits?|impressions?|opens?|usage|times used|engagement|suggestions? (shown|accepted))\b",
    re.IGNORECASE,
)


# --------------------------------------------------------------------- loading


class Charter:
    def __init__(self, data: dict, source: str, line: int | None = None):
        self.data, self.source, self.line = data, source, line

    @property
    def where(self) -> str:
        return f"{self.source}:{self.line}" if self.line else self.source

    @property
    def id(self) -> str:
        return str(self.data.get("id") or "?") if isinstance(self.data, dict) else "?"


def _yaml():
    try:
        import yaml  # type: ignore
    except ImportError:
        raise SystemExit("PyYAML is required for YAML and Markdown charters: pip install pyyaml")
    return yaml


def extract_blocks(text: str) -> list[tuple[int, str]]:
    """Return (line number, body) for each ```feature-charter block in Markdown."""
    blocks = []
    for m in FENCE.finditer(text):
        fence = m.group("fence")
        start = m.end() + 1
        close = re.compile(rf"^[ \t]*{re.escape(fence[0])}{{{len(fence)},}}[ \t]*$", re.MULTILINE)
        end = close.search(text, start)
        body = text[start: end.start() if end else len(text)]
        indent = m.group("indent")
        if indent:
            body = "\n".join(l[len(indent):] if l.startswith(indent) else l for l in body.splitlines())
        blocks.append((text.count("\n", 0, m.start()) + 1, body))
    return blocks


def looks_like_charter(data) -> bool:
    return isinstance(data, dict) and ("needle" in data or "hypothesis" in data)


def load_file(path: Path, explicit: bool = True) -> list[Charter]:
    """Charters in a file. Standalone YAML or JSON found by a folder scan counts only if it
    looks like a charter, so workflows and other config files are ignored."""
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".json", ".yaml", ".yml"}:
        try:
            data = json.loads(text) if suffix == ".json" else _yaml().safe_load(text)
        except Exception:
            if explicit:
                raise
            return []
        if not explicit and not looks_like_charter(data):
            return []
        return [Charter(data, str(path))]
    if suffix in {".md", ".markdown"}:
        out = []
        for line, body in extract_blocks(text):
            try:
                data = _yaml().safe_load(body)
            except Exception as exc:  # noqa: BLE001
                data = {"__error__": f"could not parse block: {exc}"}
            out.append(Charter(data, str(path), line))
        return out
    return []


def in_skill(f: Path) -> bool:
    """Folder scans skip this skill's own templates and examples wherever it is installed."""
    parts = f.parts
    return any(parts[i] == "skills" and parts[i + 1] == "feature-charter" for i in range(len(parts) - 1))


def find_files(paths: list[str]) -> list[tuple[Path, bool]]:
    """(file, named explicitly) pairs."""
    files: list[tuple[Path, bool]] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            for ext in ("*.md", "*.markdown", "*.yaml", "*.yml", "*.json"):
                files.extend((f, False) for f in sorted(path.rglob(ext))
                             if not {".git", "node_modules"} & set(f.parts) and not in_skill(f))
        elif path.exists():
            files.append((path, True))
        else:
            raise SystemExit(f"No such file or directory: {p}")
    return files


def find_config() -> Path | None:
    """.feature-charter.yml in the current folder or the nearest parent, stopping at the repository root."""
    here = Path.cwd().resolve()
    for folder in (here, *here.parents):
        if (folder / ".feature-charter.yml").exists():
            return folder / ".feature-charter.yml"
        if (folder / ".git").exists():
            break
    return None


def load_config(explicit: str | None) -> dict:
    cfg = dict(DEFAULTS)
    candidate = Path(explicit) if explicit else (find_config() or Path(".feature-charter.yml"))
    if candidate.exists():
        data = _yaml().safe_load(candidate.read_text(encoding="utf-8")) or {}
        unknown = set(data) - set(DEFAULTS)
        if unknown:
            raise SystemExit(f"Unknown settings in {candidate}: {', '.join(sorted(unknown))}")
        for key, value in data.items():
            if key == "id_pattern":
                if not isinstance(value, str):
                    raise SystemExit(f"{candidate}: id_pattern must be a string")
                re.compile(value)
            elif not is_number(value) or value <= 0:
                raise SystemExit(f"{candidate}: {key} must be a positive number")
        cfg.update(data)
    elif explicit:
        raise SystemExit(f"Config file not found: {explicit}")
    return cfg


# --------------------------------------------------------------------- helpers


def to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict)):
        return not value
    return False


def get(data, dotted, default=None):
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def word(v):
    """A value usable in set membership tests: strings as is, anything else as None."""
    return v if isinstance(v, str) else None


def relative_change(v):
    """'15%' -> 15.0 for a min_change given relative to the baseline; None otherwise."""
    if isinstance(v, str) and re.fullmatch(r"\s*\d+(\.\d+)?\s*%\s*", v):
        return float(v.strip().rstrip("%"))
    return None


def decisions(c: dict) -> list[dict]:
    return [d for d in (c.get("decision_log") or []) if isinstance(d, dict) and to_date(d.get("date"))]


def last_decision(c: dict, kind: str | None = None):
    rows = [d for d in decisions(c) if kind is None or d.get("decision") == kind]
    return max(rows, key=lambda d: to_date(d["date"])) if rows else None


def next_due(c: dict):
    status = word(c.get("status"))
    if status == "kept":
        keep = last_decision(c, "keep")
        return to_date(keep.get("next_review")) if keep else None
    if status == "iterating":
        it = last_decision(c, "iterate")
        if it and to_date(it.get("next_review")):
            return to_date(it.get("next_review"))
    if status in REVIEWABLE:
        return to_date(get(c, "evaluation.review_date"))
    return None


class Report:
    def __init__(self, charter: Charter):
        self.where, self.id = charter.where, charter.id
        self.errors: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []

    def error(self, f, m):
        self.errors.append((f, m))

    def warn(self, f, m):
        self.warnings.append((f, m))

    def ok(self, strict=False):
        return not self.errors and not (strict and self.warnings)

    def as_dict(self):
        return {"where": self.where, "id": self.id,
                "errors": [{"field": f, "message": m} for f, m in self.errors],
                "warnings": [{"field": f, "message": m} for f, m in self.warnings]}


# -------------------------------------------------------------------- validate


def validate(ch: Charter, cfg: dict, today: date) -> Report:
    r = Report(ch)
    c = ch.data
    if not isinstance(c, dict):
        r.error("block", "a charter must be a YAML mapping")
        return r
    if "__error__" in c:
        r.error("block", c["__error__"])
        return r

    status = word(c.get("status"))
    approved_stage = status in APPROVED_OR_LATER

    def need(field, msg="required", after_approval=False):
        value = get(c, field)
        if blank(value):
            if after_approval and not approved_stage:
                r.warn(field, f"{msg} (required once the charter is approved)")
            else:
                r.error(field, msg)
        return value

    # Identity, roles, dates
    cid = need("id")
    if cid and not re.fullmatch(cfg["id_pattern"], str(cid)):
        r.error("id", f"must match {cfg['id_pattern']} (for example FC-001)")
    need("status")
    if c.get("status") is not None and status not in STATUSES:
        r.error("status", f"must be one of {', '.join(STATUSES)}")
    need("owner", "name the person who approves the bet and makes the keep or kill call", after_approval=True)
    builder = need("builder", "name who or what builds it", after_approval=True)
    judge = need("judge", "name who or what evaluates it", after_approval=True)
    if not blank(builder) and not blank(judge) and str(builder).strip().casefold() == str(judge).strip().casefold():
        r.error("judge", "must differ from builder: the builder never grades its own work")
    approved = to_date(c.get("approved"))
    if c.get("approved") not in (None, "") and approved is None:
        r.error("approved", "must be a date (YYYY-MM-DD)")
    if approved_stage and approved is None:
        r.error("approved", f"status is '{status}' but there is no approval date")

    # The bet
    for part in ("we_believe", "for", "will_result_in", "because"):
        need(f"hypothesis.{part}")
    value_type = word(c.get("value_type", "frequency"))
    if value_type not in {"frequency", "insurance"}:
        r.error("value_type", "must be frequency or insurance")
    if value_type == "insurance" and blank(c.get("insurance_reason")):
        r.error("insurance_reason", "say why this feature is valuable when needed rather than when used often")

    # The needle
    for f in ("name", "rung", "definition"):
        need(f"needle.{f}")
    need("needle.source", "say where the number comes from (events, table, survey)", after_approval=True)
    rung = get(c, "needle.rung")
    if rung is not None and word(rung) not in RUNGS:
        r.error("needle.rung", f"must be one of {', '.join(RUNGS)}")
    elif rung is not None and RUNGS.index(rung) < RESULT_RUNG:
        msg = (f"'{rung}' is an activity rung. The needle should be task_success, user_outcome or "
               "business_outcome; keep this metric as a diagnostic")
        (r.warn if value_type == "insurance" else r.error)("needle.rung", msg)
    if USAGE_WORDS.search(str(get(c, "needle.name", ""))):
        r.warn("needle.name", "reads like a usage count. Usage is a diagnostic unless the definition ties it to a completed outcome")

    baseline, target = get(c, "needle.baseline"), get(c, "needle.target")
    direction = word(get(c, "needle.direction"))
    if blank(baseline):
        r.error("needle.baseline", "a number, or measure_before_launch. Never a guess")
    elif baseline == "measure_before_launch":
        if status in MEASURED:
            r.error("needle.baseline", f"status is '{status}' but the baseline was never recorded")
        else:
            r.warn("needle.baseline", "not measured yet; measure it before launch")
    elif not is_number(baseline):
        r.error("needle.baseline", "must be a number or measure_before_launch")
    mmc = get(c, "needle.min_change")
    pct = relative_change(mmc)
    if mmc is not None and not ((is_number(mmc) and mmc > 0) or (pct is not None and pct > 0)):
        r.error("needle.min_change", "must be a positive number in the needle's units, or a percentage such as '10%'")
    if target is None and baseline == "measure_before_launch" and status not in MEASURED:
        r.warn("needle.target", "set once the baseline is measured; until then min_change states the bet")
        if mmc is None:
            msg = "with no baseline yet, min_change states the size of the bet (a percentage such as '10%' works)"
            (r.error if approved_stage else r.warn)("needle.min_change", msg)
    elif not is_number(target):
        r.error("needle.target", "required and must be a number")
    if direction not in {"increase", "decrease"}:
        r.error("needle.direction", "must be increase or decrease")
    if mmc is None and not (target is None and baseline == "measure_before_launch"):
        r.warn("needle.min_change", "set the smallest change worth the feature's carrying cost")
    if is_number(baseline) and is_number(target) and direction in {"increase", "decrease"}:
        if (direction == "increase" and target <= baseline) or (direction == "decrease" and target >= baseline):
            r.error("needle.target", f"target must move the baseline in the '{direction}' direction")
        elif is_number(mmc) and mmc > 0 and abs(target - baseline) < mmc:
            r.warn("needle.target", "the target change is smaller than min_change")
        elif pct and baseline and abs(target - baseline) < abs(baseline) * pct / 100:
            r.warn("needle.target", "the target change is smaller than min_change")

    # Guardrails
    guardrails = c.get("guardrails")
    if not isinstance(guardrails, list) or not guardrails:
        r.error("guardrails", "at least one guardrail: what must not get worse")
    else:
        for i, g in enumerate(guardrails):
            if not isinstance(g, dict):
                r.error(f"guardrails[{i}]", "must be a mapping with name and limit")
                continue
            for f in ("name", "limit"):
                if blank(g.get(f)):
                    r.error(f"guardrails[{i}].{f}", "required")

    # Evaluation and expiry
    method = word(get(c, "evaluation.method"))
    if method not in METHODS:
        r.error("evaluation.method", f"must be one of {', '.join(sorted(METHODS))}")
    review = to_date(get(c, "evaluation.review_date"))
    if review is None:
        if approved_stage:
            r.error("evaluation.review_date", "required (YYYY-MM-DD): every bet needs an expiry date")
        else:
            r.warn("evaluation.review_date", f"set it at approval, at most {cfg['max_review_days']} days later")
    elif approved:
        span = (review - approved).days
        extended = any(isinstance(a, dict) and str(a.get("field", "")).strip() == "evaluation.review_date"
                       and not blank(a.get("approved_by")) and not blank(a.get("reason"))
                       for a in c.get("amendments") or [])
        limit = cfg["max_review_days"] * (2 if extended else 1)
        if span <= 0:
            r.error("evaluation.review_date", "must be after the approval date")
        elif span > limit:
            how = " with one approved extension" if extended else "; one approved amendment can extend it"
            r.error("evaluation.review_date", f"{span} days after approval; the limit is {limit}{how}")
    elif review <= today:
        r.warn("evaluation.review_date", "is not in the future")
    for f in ("keep_if", "kill_if"):
        need(f"evaluation.{f}", "write the condition before the data arrives")
    if blank(get(c, "evaluation.iterate_if")):
        r.warn("evaluation.iterate_if", "results between keep and kill will be inconclusive without it")
    inconclusive = word(get(c, "evaluation.if_inconclusive"))
    if inconclusive == "keep":
        r.error("evaluation.if_inconclusive", "inconclusive never means keep; use sunset or iterate")
    elif inconclusive not in {"sunset", "iterate"}:
        r.error("evaluation.if_inconclusive", "must be sunset or iterate")
    weekly = get(c, "evaluation.weekly_users")
    if method == "ab_test" and is_number(weekly) and weekly < cfg["low_traffic_weekly_users"]:
        r.warn("evaluation.method", f"an A/B test with about {weekly} weekly users is likely underpowered; "
                                    "consider holdback, before_after or qualitative")
    if blank(get(c, "evaluation.look_at")):
        r.warn("evaluation.look_at", "name the real sessions or people you will look at, not just the dashboard")

    # Removal plan
    need("removal.flag", "every feature ships behind a kill switch", after_approval=True)
    hours = get(c, "removal.estimate_hours")
    if hours is None:
        (r.error if approved_stage else r.warn)("removal.estimate_hours", "estimate what deleting it would cost")
    elif not is_number(hours):
        r.error("removal.estimate_hours", "must be a number of hours")
    elif hours > cfg["removal_warn_hours"]:
        r.warn("removal.estimate_hours", f"{hours} hours to remove is expensive; isolate the feature before building")

    # Decision log and status
    for i, d in enumerate(c.get("decision_log") or []):
        w = f"decision_log[{i}]"
        if not isinstance(d, dict):
            r.error(w, "must be a mapping")
            continue
        if word(d.get("decision")) not in DECISIONS:
            r.error(f"{w}.decision", f"must be one of {', '.join(sorted(DECISIONS))}")
        ddate = to_date(d.get("date"))
        if ddate is None:
            r.error(f"{w}.date", "required (YYYY-MM-DD)")
        for f in ("evidence", "decided_by"):
            if blank(d.get(f)):
                r.error(f"{w}.{f}", "required")
        if d.get("decision") in {"keep", "iterate"}:
            nxt = to_date(d.get("next_review"))
            if nxt is None:
                r.error(f"{w}.next_review", f"'{d.get('decision')}' is a renewal, not a permanent pass: set next_review")
            elif ddate and (nxt - ddate).days > cfg["max_renewal_days"]:
                r.error(f"{w}.next_review", f"{(nxt - ddate).days} days out; the limit is {cfg['max_renewal_days']}")
    expected = {"kept": "keep", "iterating": "iterate", "sunset": "sunset", "removed": "removed"}
    if status in expected:
        latest = last_decision(c)
        if not latest or latest.get("decision") != expected[status]:
            r.error("status", f"'{status}' needs a '{expected[status]}' entry as the latest decision")

    for i, a in enumerate(c.get("amendments") or []):
        w = f"amendments[{i}]"
        if not isinstance(a, dict):
            r.error(w, "must be a mapping")
            continue
        for f in ("date", "field", "reason", "approved_by"):
            if blank(a.get(f)):
                r.error(f"{w}.{f}", "required")

    due = next_due(c)
    if due and due < today:
        latest = last_decision(c)
        if not latest or to_date(latest["date"]) < due:
            r.warn("review", f"review was due {due.isoformat()} and has no decision")
    return r


# -------------------------------------------------- pre-registration (baseline)


def leaves(value, prefix=""):
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            out.update(leaves(v, f"{prefix}.{k}" if prefix else str(k)))
        return out
    if isinstance(value, list):
        out = {}
        for i, v in enumerate(value):
            out.update(leaves(v, f"{prefix}[{i}]"))
        return out or {prefix: []}
    return {prefix: value}


def norm(v):
    d = to_date(v) if not is_number(v) else None
    return d.isoformat() if d else v


def check_baseline(old: dict, new: dict, report: Report):
    if to_date(old.get("approved")) is None:
        return
    before = [json.dumps(a, sort_keys=True, default=str) for a in old.get("amendments") or []]
    added = [a for a in new.get("amendments") or []
             if isinstance(a, dict) and json.dumps(a, sort_keys=True, default=str) not in before]
    for section in LOCKED:
        a, b = leaves(old.get(section), section), leaves(new.get(section), section)
        for path in sorted(set(a) | set(b)):
            if norm(a.get(path)) == norm(b.get(path)):
                continue
            covered = any(
                (path == str(x.get("field", "")).strip() or path.startswith(str(x.get("field", "")).strip() + ".")
                 or path.startswith(str(x.get("field", "")).strip() + "["))
                and not blank(x.get("approved_by")) and not blank(x.get("reason"))
                for x in added)
            if not covered:
                report.error(path, "changed after approval without a new approved amendment (pre-registration)")


# ------------------------------------------------------------------------- due


def due_rows(charters: list[Charter], cfg: dict, today: date, soon: int) -> list[dict]:
    rows = []
    for ch in charters:
        c = ch.data
        if not isinstance(c, dict) or "__error__" in c:
            rows.append({"id": ch.id, "where": ch.where, "state": "unreadable", "detail": "could not parse"})
            continue
        due = next_due(c)
        if due:
            latest = last_decision(c)
            if not (latest and to_date(latest["date"]) >= due):
                days = (due - today).days
                if days < 0:
                    rows.append({"id": ch.id, "where": ch.where, "state": "overdue",
                                 "detail": f"review due {due} ({-days} days ago), status {c.get('status')}"})
                elif days <= soon:
                    rows.append({"id": ch.id, "where": ch.where, "state": "due_soon",
                                 "detail": f"review due {due} (in {days} days)"})
        if c.get("status") == "sunset":
            s = last_decision(c, "sunset")
            sdate = to_date(s["date"]) if s else None
            if sdate and (today - sdate).days > cfg["sunset_stuck_days"]:
                rows.append({"id": ch.id, "where": ch.where, "state": "stuck_in_sunset",
                             "detail": f"sunset {sdate}, still not removed after {(today - sdate).days} days"})
    return rows


def require_one(wanted, charters, paths, cfg, today) -> int:
    matches = [ch for ch in charters if ch.id == wanted]
    if not matches:
        print(f"FAIL  {wanted} not found under {', '.join(paths)}")
        return 1
    if len(matches) > 1:
        print(f"FAIL  {wanted} is defined more than once: {', '.join(m.where for m in matches)}")
        return 1
    ch = matches[0]
    status = word(ch.data.get("status")) if isinstance(ch.data, dict) else None
    rep = validate(ch, cfg, today)
    if status not in APPROVED_OR_LATER:
        print(f"FAIL  {wanted} at {ch.where} is not approved (status: {status})")
        return 1
    if not rep.ok():
        print(f"FAIL  {wanted} at {ch.where} has errors:")
        for f, m in rep.errors:
            print(f"  ERROR {f}: {m}")
        return 1
    print(f"PASS  {wanted} at {ch.where} (status: {status})")
    return 0



# ------------------------------------------------------------------------- cli


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Validate feature charters embedded in specs.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="check charters in files or directories")
    v.add_argument("paths", nargs="+")
    v.add_argument("--baseline", help="earlier version of the (single) file, to enforce pre-registration")
    v.add_argument("--strict", action="store_true", help="treat warnings as errors")
    v.add_argument("--json", action="store_true")
    v.add_argument("--today")
    v.add_argument("--config")
    d = sub.add_parser("due", help="list overdue reviews and features stuck in sunset")
    d.add_argument("paths", nargs="+")
    d.add_argument("--soon-days", type=int, default=14)
    d.add_argument("--json", action="store_true")
    d.add_argument("--no-fail", action="store_true")
    d.add_argument("--today")
    d.add_argument("--config")
    q = sub.add_parser("require", help="check that referenced charters exist, are approved and validate")
    q.add_argument("id", nargs="?", help="a charter id; or use --text")
    q.add_argument("paths", nargs="+")
    q.add_argument("--text", help="text to scan for charter ids, such as a pull request description")
    q.add_argument("--today")
    q.add_argument("--config")
    a = ap.parse_args(argv)

    today = to_date(a.today) if a.today else date.today()
    if today is None:
        ap.error("--today must be YYYY-MM-DD")
    cfg = load_config(a.config)
    files = find_files(a.paths)

    charters: list[Charter] = []
    load_errors: list[Report] = []
    skipped = 0
    for f, explicit in files:
        try:
            for ch in load_file(f, explicit):
                if ch.id == PLACEHOLDER_ID:
                    skipped += 1
                else:
                    charters.append(ch)
        except SystemExit:
            raise
        except Exception as exc:  # noqa: BLE001
            rep = Report(Charter({}, str(f)))
            rep.error("file", f"could not read: {exc}")
            load_errors.append(rep)

    if a.cmd == "require":
        if a.text is not None:
            if a.id:
                a.paths.insert(0, a.id)
                charters.extend(c for f, e in find_files([a.id]) for c in load_file(f, e) if c.id != PLACEHOLDER_ID)
            ids = sorted(set(re.findall(cfg["id_pattern"], a.text)) - {PLACEHOLDER_ID})
            if not ids:
                print(f"FAIL  no charter id matching {cfg['id_pattern']} found in the text")
                return 1
            return max(require_one(i, charters, a.paths, cfg, today) for i in ids)
        if not a.id:
            ap.error("give a charter id, or --text")
        return require_one(a.id, charters, a.paths, cfg, today)

    if a.cmd == "validate":
        if a.baseline and len(files) != 1:
            ap.error("--baseline works with exactly one file")
        old_by_id = {}
        if a.baseline:
            old = [ch for ch in load_file(Path(a.baseline)) if isinstance(ch.data, dict)]
            old_by_id = {ch.id: ch.data for ch in old}
            if len(old) == 1 and len(charters) == 1 and charters[0].id != old[0].id \
                    and to_date(old[0].data.get("approved")):
                rep = Report(charters[0])
                rep.error("id", f"changed from {old[0].id} after approval; an approved bet keeps its id")
                load_errors.append(rep)
        reports = list(load_errors)
        for ch in charters:
            rep = validate(ch, cfg, today)
            if ch.id in old_by_id:
                check_baseline(old_by_id[ch.id], ch.data, rep)
            reports.append(rep)
        seen: dict[str, str] = {}
        for ch, rep in zip(charters, reports[len(load_errors):]):
            if ch.id != "?" and ch.id in seen:
                rep.error("id", f"duplicate id, also used at {seen[ch.id]}")
            seen.setdefault(ch.id, ch.where)
        if a.json:
            print(json.dumps([r.as_dict() for r in reports], indent=2))
        elif not reports:
            print("No feature charters found." + (f" Skipped {skipped} placeholder block(s) with id {PLACEHOLDER_ID}." if skipped else ""))
        else:
            for r in reports:
                print(f"{'PASS' if r.ok(a.strict) else 'FAIL'}  {r.id}  {r.where}  "
                      f"({len(r.errors)} errors, {len(r.warnings)} warnings)")
                for f, m in r.errors:
                    print(f"  ERROR {f}: {m}")
                for f, m in r.warnings:
                    print(f"  WARN  {f}: {m}")
        return 0 if all(r.ok(a.strict) for r in reports) else 1

    rows = due_rows(charters, cfg, today, a.soon_days)
    if a.json:
        print(json.dumps(rows, indent=2))
    elif not rows:
        print("Nothing due: no overdue reviews, nothing stuck in sunset.")
    else:
        for row in rows:
            print(f"{row['state'].upper():16} {row['id']:8} {row['detail']}  ({row['where']})")
    failing = any(r["state"] in {"overdue", "stuck_in_sunset", "unreadable"} for r in rows)
    return 1 if failing and not a.no_fail else 0


if __name__ == "__main__":
    sys.exit(main())
