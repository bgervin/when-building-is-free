#!/usr/bin/env python3
"""Strategy, opportunity brief and bet board tool for the feedback-triage skill.

Three kinds of fenced YAML blocks live in the Markdown your team already keeps:

  ```product-strategy    the diagnosis, target segments, policies, areas, horizon mix and rulings
  ```opportunity-brief   one triaged opportunity: who struggles, at which rung, how many, which policy
  ```feature-charter     the bet (from the feature-charter skill); its optional `strategy` block links here

Commands:
  validate PATH [PATH ...] [--json] [--strict] [--today YYYY-MM-DD] [--config FILE]
      check strategies and briefs, and that every link between strategy, briefs and charters resolves
  mix PATH [PATH ...] [--today] [--config]
      compare active charters by horizon with the strategy's horizon mix
  board PATH [PATH ...] [--since YYYY-MM-DD] [--today] [--config] [--out FILE]
      write a one-page bet board in Markdown: betting, probing, tuning, decided, not betting, off plan

Blocks with placeholder ids (ST-000, OPP-000, FC-000) are skipped.
Exit codes: 0 ok, 1 problems found, 2 usage error. Needs PyYAML (pip install pyyaml).
Settings can be overridden in .feedback-triage.yml at the repository root, or with --config.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

DEFAULTS = {
    "max_strategy_review_days": 120,   # a strategy is a bet too: review it at least this often
    "min_segment_accounts": 3,         # fewer distinct accounts in the target segment: design partner or hostage?
    "mix_tolerance_points": 15,        # how far the active horizon mix may drift from the strategy's, in points
    "board_window_days": 90,           # "decided this quarter" looks back this far unless --since is given
    "sunset_stuck_days": 30,           # a feature sunset longer than this without removal is off plan
}
PLACEHOLDERS = {"ST-000", "OPP-000", "FC-000"}
KINDS = ("product-strategy", "opportunity-brief", "feature-charter")
FENCE = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})[ \t]*(?P<kind>product-strategy|opportunity-brief|feature-charter)[ \t]*$",
                   re.MULTILINE)

RUNGS = ["shipped", "discovered", "adopted", "retained", "task_success", "user_outcome", "business_outcome"]
RESULT_RUNG = RUNGS.index("task_success")
HORIZONS = {"tune": "H1", "bet": "H2", "probe": "H3"}
RULINGS = {"no", "not_now", "services"}
FAILURE_MODES = {"loudest_voice", "hostage_customer", "rearview_mirror", "hippo", "parity_reflex", "zombie_commitment"}
BRIEF_STATUSES = {"shortlisted", "probing", "chartered", "parked", "ruled_out"}
STRATEGY_STATUSES = {"draft", "approved", "retired"}
ACTIVE_CHARTER = {"approved", "building", "live", "under_review", "iterating", "kept"}
GOAL_WORDS = re.compile(
    r"^\s*(?:(?:we|our\s+\w+)\s+(?:will\s+|aim\s+to\s+|want\s+to\s+|plan\s+to\s+|need\s+to\s+|must\s+)?)?"
    r"(increase|grow|improve|reach|achieve|double|triple|hit|maximi[sz]e|boost|win)\b", re.IGNORECASE)
TARGET_NUMBER = re.compile(r"\d+(\.\d+)?\s*%|\$\s?\d")
STATUS_ORDER = ["proposed", "approved", "building", "live", "under_review", "iterating", "kept", "sunset", "removed"]
IDS = {"strategy": r"ST-[\w.-]+", "policy": r"P-\d+", "ruling": r"R-\d+", "brief": r"OPP-\d+"}


# --------------------------------------------------------------------- loading


class Block:
    def __init__(self, kind: str, data, source: str, line: int | None = None):
        self.kind, self.data, self.source, self.line = kind, data, source, line

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
        raise SystemExit("PyYAML is required: pip install pyyaml")
    return yaml


def extract(text: str) -> list[tuple[str, int, str]]:
    out = []
    for m in FENCE.finditer(text):
        fence = m.group("fence")
        start = m.end() + 1
        close = re.compile(rf"^[ \t]*{re.escape(fence[0])}{{{len(fence)},}}[ \t]*$", re.MULTILINE)
        end = close.search(text, start)
        body = text[start: end.start() if end else len(text)]
        indent = m.group("indent")
        if indent:
            body = "\n".join(l[len(indent):] if l.startswith(indent) else l for l in body.splitlines())
        out.append((m.group("kind"), text.count("\n", 0, m.start()) + 1, body))
    return out


def in_skill(f: Path) -> bool:
    """Folder scans skip the skills' own templates and references wherever they are installed."""
    parts = f.parts
    return any(parts[i] == "skills" and parts[i + 1] in {"feature-charter", "feedback-triage"}
               for i in range(len(parts) - 1))


def find_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files.extend(f for f in sorted(path.rglob("*.md"))
                         if not {".git", "node_modules"} & set(f.parts) and not in_skill(f))
        elif path.exists():
            files.append(path)
        else:
            raise SystemExit(f"No such file or directory: {p}")
    return files


def load(paths: list[str]) -> list[Block]:
    blocks = []
    for f in find_files(paths):
        for kind, line, body in extract(f.read_text(encoding="utf-8")):
            try:
                data = _yaml().safe_load(body)
            except Exception as exc:  # noqa: BLE001
                data = {"__error__": f"could not parse block: {exc}"}
            b = Block(kind, data, str(f), line)
            if b.id not in PLACEHOLDERS:
                blocks.append(b)
    return blocks


def find_config() -> Path | None:
    here = Path.cwd().resolve()
    for folder in (here, *here.parents):
        if (folder / ".feedback-triage.yml").exists():
            return folder / ".feedback-triage.yml"
        if (folder / ".git").exists():
            break
    return None


def load_config(explicit: str | None) -> dict:
    cfg = dict(DEFAULTS)
    candidate = Path(explicit) if explicit else find_config()
    if candidate and candidate.exists():
        data = _yaml().safe_load(candidate.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise SystemExit(f"{candidate} must be a mapping of setting: value")
        unknown = set(map(str, data)) - set(DEFAULTS)
        if unknown:
            raise SystemExit(f"Unknown settings in {candidate}: {', '.join(sorted(unknown))}")
        for key, value in data.items():
            if not is_number(value) or value < 0:
                raise SystemExit(f"{candidate}: {key} must be a number, 0 or more")
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


def is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def word(v):
    """A value usable as an id or in set membership tests: non-blank strings as is, anything else None."""
    return v.strip() if isinstance(v, str) and v.strip() else None


def get(data, dotted, default=None):
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def items(value) -> list:
    return value if isinstance(value, list) else []


def ruling_word(v):
    """YAML reads an unquoted `no` as False; accept it as the ruling 'no'."""
    return "no" if v is False else word(v)


def one_line(text, limit=110) -> str:
    s = " ".join(str(text if text is not None else "").split())
    s = s.replace("|", "/")
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def status_rank(c: dict) -> int:
    s = word(c.get("status"))
    return STATUS_ORDER.index(s) if s in STATUS_ORDER else -1


class Report:
    def __init__(self, block: Block):
        self.where, self.id, self.kind = block.where, block.id, block.kind
        self.errors: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []

    def error(self, f, m):
        self.errors.append((f, m))

    def warn(self, f, m):
        self.warnings.append((f, m))

    def ok(self, strict=False):
        return not self.errors and not (strict and self.warnings)

    def as_dict(self):
        return {"where": self.where, "kind": self.kind, "id": self.id,
                "errors": [{"field": f, "message": m} for f, m in self.errors],
                "warnings": [{"field": f, "message": m} for f, m in self.warnings]}


class Index:
    """What links can point at. Links resolve against approved strategies (drafts only when none is
    approved); retired strategies never resolve. The board uses the most recently approved one."""

    def __init__(self, blocks: list[Block]):
        valid = [b for b in blocks if b.kind == "product-strategy" and isinstance(b.data, dict)
                 and "__error__" not in b.data]
        approved = [b for b in valid if b.data.get("status") == "approved"]
        drafts = [b for b in valid if b.data.get("status") == "draft"]
        self.strategies = approved or drafts
        self.strategy = (max(approved, key=lambda b: to_date(b.data.get("approved")) or date.min) if approved
                         else (drafts[0] if drafts else None))
        self.policies, self.areas, self.target, self.not_target, self.rulings = {}, {}, {}, {}, {}
        for s in self.strategies:
            d = s.data
            for p in items(d.get("policies")):
                if isinstance(p, dict) and word(p.get("id")):
                    self.policies[word(p["id"])] = p
            for a in items(d.get("areas")):
                if isinstance(a, dict) and word(a.get("id")):
                    self.areas[word(a["id"])] = a
            segs = d.get("segments") if isinstance(d.get("segments"), dict) else {}
            for seg in items(segs.get("target")):
                if isinstance(seg, dict) and word(seg.get("id")):
                    self.target[word(seg["id"])] = seg
            for seg in items(segs.get("not_target")):
                if isinstance(seg, dict) and word(seg.get("id")):
                    self.not_target[word(seg["id"])] = seg
            for r in items(d.get("rulings")):
                if isinstance(r, dict) and word(r.get("id")):
                    self.rulings[word(r["id"])] = r
        self.duplicates: list[str] = []
        self.briefs = self._pick([b for b in blocks if b.kind == "opportunity-brief" and isinstance(b.data, dict)
                                  and "__error__" not in b.data], key=lambda b: status_rank(b.data))
        self.charters = self._pick([b for b in blocks if b.kind == "feature-charter" and isinstance(b.data, dict)
                                    and "__error__" not in b.data], key=self._charter_key)

    @staticmethod
    def _charter_key(b: Block):
        latest = last_decision(b.data)
        when = to_date(latest["date"]) if latest else to_date(b.data.get("approved"))
        return (when or date.min, status_rank(b.data))

    def _pick(self, found: list[Block], key) -> dict:
        groups: dict[str, list[Block]] = {}
        for b in found:
            groups.setdefault(b.id, []).append(b)
        out = {}
        for i, group in groups.items():
            chosen = max(group, key=key)
            out[i] = chosen
            if len(group) > 1:
                self.duplicates.append(f"{i} is defined in {len(group)} places; using {chosen.where}, the latest")
        return out


# -------------------------------------------------------------------- validate


def check_id(r: Report, field: str, value, pattern: str, example: str) -> str | None:
    v = word(value)
    if blank(value):
        r.error(field, f"required, like {example}")
    elif v is None or not re.fullmatch(pattern, v):
        r.error(field, f"must be an id like {example}")
        return None
    return v


def validate_strategy(b: Block, cfg: dict, today: date) -> Report:
    r = Report(b)
    d = b.data
    if not isinstance(d, dict):
        r.error("block", "a strategy must be a YAML mapping")
        return r
    if "__error__" in d:
        r.error("block", d["__error__"])
        return r
    status = word(d.get("status"))
    approved_stage = status in {"approved", "retired"}

    check_id(r, "id", d.get("id"), IDS["strategy"], "ST-2026H2")
    if status not in STRATEGY_STATUSES:
        r.error("status", f"must be one of {', '.join(sorted(STRATEGY_STATUSES))}")
    if blank(d.get("owner")):
        (r.error if approved_stage else r.warn)("owner", "name the person who owns the strategy and its rulings")
    approved = to_date(d.get("approved"))
    if approved_stage and approved is None:
        r.error("approved", f"status is '{status}' but there is no approval date")
    review = to_date(d.get("review_date"))
    if review is None:
        (r.error if approved_stage else r.warn)("review_date", "a strategy is a bet too: set a review date")
    elif approved:
        span = (review - approved).days
        if span <= 0:
            r.error("review_date", "must be after the approval date")
        elif span > cfg["max_strategy_review_days"]:
            r.error("review_date", f"{span} days after approval; the limit is {cfg['max_strategy_review_days']:g}")
    if review and status == "approved" and review < today:
        r.warn("review_date", f"the strategy review was due {review.isoformat()}")

    # Rumelt's kernel: diagnosis, guiding policy, coherent actions
    diag = d.get("diagnosis")
    if blank(diag) or not isinstance(diag, str) or diag.strip() in {'""', "''"}:
        r.error("diagnosis", "say what the challenge is. A strategy with no diagnosis is a list of goals")

    segs = d.get("segments")
    if not isinstance(segs, dict) or not items(segs.get("target")):
        r.error("segments.target", "name at least one target segment: who the product is for")
    else:
        for i, s in enumerate(items(segs.get("target"))):
            for f in ("id", "name", "definition"):
                if not isinstance(s, dict) or blank(s.get(f)):
                    r.error(f"segments.target[{i}].{f}", "required")
        if not items(segs.get("not_target")):
            r.warn("segments.not_target", "name who the product is not for. A strategy that excludes nobody decides nothing")
        for i, s in enumerate(items(segs.get("not_target"))):
            for f in ("id", "name", "why"):
                if not isinstance(s, dict) or blank(s.get(f)):
                    r.error(f"segments.not_target[{i}].{f}", "required")

    policies = items(d.get("policies"))
    if not policies:
        r.error("policies", "at least one guiding policy: a rule that can decide a real request")
    policy_ids = set()
    for i, p in enumerate(policies):
        w = f"policies[{i}]"
        if not isinstance(p, dict):
            r.error(w, "must be a mapping with id, statement and decides")
            continue
        pid = check_id(r, f"{w}.id", p.get("id"), IDS["policy"], "P-01")
        if pid and pid in policy_ids:
            r.error(f"{w}.id", f"duplicate policy id {pid}")
        if pid:
            policy_ids.add(pid)
        stmt = p.get("statement")
        if blank(stmt) or not isinstance(stmt, str):
            r.error(f"{w}.statement", "required, as one sentence")
        elif GOAL_WORDS.search(stmt) or TARGET_NUMBER.search(stmt):
            r.warn(f"{w}.statement", "reads like a goal or a target, not a policy (Rumelt: mistaking goals for "
                                     "strategy). Say how you will choose, not what you hope to reach")
        if blank(p.get("decides")):
            r.warn(f"{w}.decides", "give one real request this policy says yes or no to. A policy that decides nothing is fluff")

    areas = items(d.get("areas"))
    if not areas:
        r.error("areas", "list the product areas triage sorts into")
    for i, a in enumerate(areas):
        if not isinstance(a, dict) or not word(a.get("id")) or blank(a.get("name")):
            r.error(f"areas[{i}]", "needs an id (text) and a name")

    mix = d.get("horizons")
    if not isinstance(mix, dict):
        r.error("horizons", "set the share of active bets per horizon, for example {tune: 30, bet: 50, probe: 20}")
    else:
        unknown = set(map(str, mix)) - set(HORIZONS)
        if unknown:
            r.error("horizons", f"unknown horizon(s) {', '.join(sorted(unknown))}; use tune, bet and probe")
        vals = [mix.get(h) for h in HORIZONS]
        if not all(is_number(v) and v >= 0 for v in vals):
            r.error("horizons", "tune, bet and probe must each be a percentage")
        elif abs(sum(vals) - 100) > 0.5:
            r.error("horizons", f"tune, bet and probe add up to {sum(vals):g}; they must add up to 100")

    rids = set()
    for i, rl in enumerate(items(d.get("rulings"))):
        w = f"rulings[{i}]"
        if not isinstance(rl, dict):
            r.error(w, "must be a mapping")
            continue
        rid = check_id(r, f"{w}.id", rl.get("id"), IDS["ruling"], "R-001")
        if rid and rid in rids:
            r.error(f"{w}.id", f"duplicate ruling id {rid}")
        if rid:
            rids.add(rid)
        if ruling_word(rl.get("ruling")) not in RULINGS:
            r.error(f"{w}.ruling", f"must be one of {', '.join(sorted(RULINGS))} (quote \"no\" in YAML to be safe)")
        for f in ("request", "reason", "reopen_if", "decided_by"):
            if blank(rl.get(f)):
                msg = {"reopen_if": "say what new evidence would reopen it; a ruling without one is a grudge",
                       "decided_by": "who made the call"}.get(f, "required")
                r.error(f"{w}.{f}", msg)
        if to_date(rl.get("date")) is None:
            r.error(f"{w}.date", "required (YYYY-MM-DD)")
        pol = rl.get("policy")
        if blank(pol):
            r.error(f"{w}.policy", "cite the policy that decides it, or `none` with a policy_gap note")
        elif word(pol) == "none":
            if blank(rl.get("policy_gap")):
                r.error(f"{w}.policy_gap", "no policy decides this: say what policy is missing, for the owner")
            else:
                r.warn(f"{w}.policy", "decided without a policy. Add the missing policy at the next strategy review")
        elif word(pol) not in policy_ids:
            r.error(f"{w}.policy", f"{one_line(pol, 40)} is not a policy in this strategy")
    return r


def validate_brief(b: Block, ix: Index, cfg: dict) -> Report:
    r = Report(b)
    d = b.data
    if not isinstance(d, dict):
        r.error("block", "a brief must be a YAML mapping")
        return r
    if "__error__" in d:
        r.error("block", d["__error__"])
        return r
    check_id(r, "id", d.get("id"), IDS["brief"], "OPP-001")
    status = word(d.get("status"))
    if status not in BRIEF_STATUSES:
        r.error("status", f"must be one of {', '.join(sorted(BRIEF_STATUSES))}")
    if blank(d.get("opportunity")):
        r.error("opportunity", "who struggles, with what: the need behind the requests, not the requested feature")
    if not items(d.get("requests")):
        r.warn("requests", "list the issues or feedback items this opportunity groups")

    s = d.get("strategy")
    horizon = word(get(d, "strategy.horizon"))
    probe = status == "probing" or horizon == "probe"
    have_strategy = bool(ix.strategies)

    area = d.get("area")
    if blank(area):
        r.error("area", "required")
    elif not word(area):
        r.error("area", "must be an area id (text)")
    elif have_strategy and word(area) not in ix.areas:
        r.error("area", f"'{word(area)}' is not an area in the strategy")
    seg = d.get("segment")
    if blank(seg):
        r.error("segment", "name the target segment that has this need")
    elif not word(seg):
        r.error("segment", "must be a segment id (text)")
    elif have_strategy and word(seg) in ix.not_target:
        r.error("segment", f"'{word(seg)}' is a segment the strategy says the product is not for")
    elif have_strategy and word(seg) not in ix.target:
        if probe:
            r.warn("segment", f"'{word(seg)}' is not a target segment yet. Fine for a probe; add it to the strategy if the probe succeeds")
        else:
            r.error("segment", f"'{word(seg)}' is not a target segment in the strategy")

    breadth = d.get("breadth")
    if not isinstance(breadth, dict):
        r.error("breadth", "count distinct accounts, and how many of them are in the target segment")
    else:
        acc, ins = breadth.get("accounts"), breadth.get("in_segment")
        acc_ok = isinstance(acc, int) and not isinstance(acc, bool) and acc >= 0
        ins_ok = isinstance(ins, int) and not isinstance(ins, bool) and ins >= 0
        if not acc_ok:
            r.error("breadth.accounts", "a whole number of distinct accounts (not mentions or votes)")
        if not ins_ok:
            r.error("breadth.in_segment", "a whole number: how many of those accounts are in the target segment")
        elif acc_ok and ins > acc:
            r.error("breadth.in_segment", "can't be more than accounts")
        elif not probe and ins < cfg["min_segment_accounts"] and status in {"shortlisted", "chartered"}:
            r.warn("breadth.in_segment", f"fewer than {cfg['min_segment_accounts']:g} accounts in the target segment. "
                                         "Design partner or hostage customer? Name others who would use it within 90 days")

    rung = d.get("rung")
    if blank(rung):
        r.error("rung", "where the job fails: task_success, user_outcome or business_outcome")
    elif word(rung) not in RUNGS:
        r.error("rung", f"must be one of {', '.join(RUNGS)}")
    elif RUNGS.index(word(rung)) < RESULT_RUNG:
        r.warn("rung", f"'{rung}' is an activity rung. Name the result that fails for these users, or park it")

    if not isinstance(s, dict):
        r.error("strategy", "link the policy and horizon: {policy: P-01, horizon: bet}")
    else:
        pol = s.get("policy")
        if blank(pol):
            r.error("strategy.policy", "which policy says this is worth doing? If none fits, say so and ask the owner")
        elif not word(pol):
            r.error("strategy.policy", "must be a policy id such as P-01")
        elif have_strategy and word(pol) not in ix.policies:
            r.error("strategy.policy", f"{word(pol)} is not a policy in the strategy")
        if horizon not in HORIZONS:
            r.error("strategy.horizon", "must be tune (H1), bet (H2) or probe (H3)")
    if status == "probing":
        if horizon not in (None, "probe"):
            r.warn("strategy.horizon", f"status is probing but the horizon is {horizon}; a probe is horizon probe (H3)")
        if to_date(d.get("probe_ends")) is None:
            r.error("probe_ends", "a probe needs an end date (YYYY-MM-DD), when it stops and a decision is made")
    if not have_strategy:
        r.warn("strategy", "no approved or draft product-strategy block found in the scanned paths, so links were not checked")

    flags = d.get("flags")
    if flags is not None and not isinstance(flags, list):
        r.error("flags", "must be a list, such as [hippo]")
        flags = []
    flags = flags or []
    bad = [f for f in flags if word(f) not in FAILURE_MODES]
    if bad:
        r.error("flags", f"unknown flag(s) {', '.join(one_line(f, 30) for f in bad)}; use {', '.join(sorted(FAILURE_MODES))}")
    if flags and blank(d.get("flag_notes")):
        r.error("flag_notes", "a flagged opportunity needs a note on why it should still go ahead, for the approver")

    charter_id = d.get("charter")
    if status == "chartered":
        if blank(charter_id):
            r.error("charter", "status is chartered: name the charter, such as FC-007")
        elif not word(charter_id):
            r.error("charter", "must be a charter id such as FC-007")
        elif ix.charters and word(charter_id) not in ix.charters:
            r.warn("charter", f"{word(charter_id)} was not found in the scanned paths")
        elif word(charter_id) in ix.charters:
            cs = get(ix.charters[word(charter_id)].data, "strategy")
            if isinstance(cs, dict) and isinstance(s, dict):
                if word(cs.get("policy")) and word(cs.get("policy")) != word(s.get("policy")):
                    r.warn("charter", f"{charter_id} cites {cs.get('policy')} but this brief cites {s.get('policy')}")
                if word(cs.get("opportunity")) and word(cs.get("opportunity")) != word(d.get("id")):
                    r.warn("charter", f"{charter_id} points at {cs.get('opportunity')}, not this brief")
    ruling = d.get("ruling")
    if status == "ruled_out" and blank(ruling):
        r.error("ruling", "status is ruled_out: cite an approved ruling, such as R-004 (keep it parked until the ruling is approved)")
    elif not blank(ruling):
        if not word(ruling):
            r.error("ruling", "must be a ruling id such as R-004")
        elif ix.strategies and word(ruling) not in ix.rulings:
            r.error("ruling", f"{word(ruling)} is not a ruling in the strategy (park the brief until the ruling is approved)")
    return r


def validate_charter_link(b: Block, ix: Index) -> Report | None:
    """Only the links. The charter itself is checked by the feature-charter skill's charter.py."""
    d = b.data
    if not isinstance(d, dict) or not isinstance(d.get("strategy"), dict):
        return None
    r = Report(b)
    s = d["strategy"]
    if not ix.strategies:
        r.warn("strategy", "no approved or draft product-strategy block found in the scanned paths, so links were not checked")
        return r
    pol = s.get("policy")
    if blank(pol):
        r.error("strategy.policy", "required when a charter links to the strategy")
    elif word(pol) not in ix.policies:
        r.error("strategy.policy", f"{one_line(pol, 40)} is not a policy in the strategy")
    if not blank(s.get("area")) and word(s.get("area")) not in ix.areas:
        r.error("strategy.area", f"'{one_line(s.get('area'), 40)}' is not an area in the strategy")
    if not blank(s.get("horizon")) and word(s.get("horizon")) not in HORIZONS:
        r.error("strategy.horizon", "must be tune (H1), bet (H2) or probe (H3)")
    opp = s.get("opportunity")
    if not blank(opp) and ix.briefs and word(opp) not in ix.briefs:
        r.warn("strategy.opportunity", f"{one_line(opp, 40)} was not found in the scanned paths")
    return r


def validate_all(blocks: list[Block], cfg: dict, today: date) -> list[Report]:
    ix = Index(blocks)
    reports = []
    seen: dict[tuple[str, str], str] = {}
    charter_seen: dict[str, list[str]] = {}
    for b in blocks:
        if b.kind == "feature-charter":
            charter_seen.setdefault(b.id, []).append(b.where)
            rep = validate_charter_link(b, ix)
            if rep:
                reports.append(rep)
            continue
        rep = validate_strategy(b, cfg, today) if b.kind == "product-strategy" else validate_brief(b, ix, cfg)
        key = (b.kind, b.id)
        if b.id != "?" and key in seen:
            rep.error("id", f"duplicate id, also used at {seen[key]}")
        seen.setdefault(key, b.where)
        reports.append(rep)
    for cid, wheres in charter_seen.items():
        if len(wheres) > 1 and cid in ix.charters:
            rep = Report(ix.charters[cid])
            rep.warn("id", f"defined in {len(wheres)} places ({', '.join(wheres)}); links and the board use "
                           f"{ix.charters[cid].where}, the one with the latest decision")
            reports.append(rep)
    return reports


# ------------------------------------------------------------------ mix, board


def last_decision(c: dict, kind: str | None = None):
    rows = [x for x in items(c.get("decision_log"))
            if isinstance(x, dict) and to_date(x.get("date")) and (kind is None or x.get("decision") == kind)]
    return max(rows, key=lambda x: to_date(x["date"])) if rows else None


def next_due(c: dict):
    status = word(c.get("status"))
    if status in {"kept", "iterating"}:
        d = last_decision(c, "keep" if status == "kept" else "iterate")
        if d:
            return to_date(d.get("next_review"))
        if status == "kept":
            return None
    if status in ACTIVE_CHARTER:
        return to_date(get(c, "evaluation.review_date"))
    return None


def horizon_of(c: dict) -> str:
    """A kept charter is proven, so it is tuning (H1) whatever horizon it started in."""
    if c.get("status") == "kept":
        return "tune"
    h = word(get(c, "strategy.horizon"))
    return h if h in HORIZONS else "bet"


def active_charters(ix: Index) -> list[Block]:
    return [b for b in ix.charters.values() if word(b.data.get("status")) in ACTIVE_CHARTER]


def active_probes(ix: Index) -> list[Block]:
    """Probing briefs not already counted through an active charter."""
    linked = {word(get(b.data, "strategy.opportunity")) for b in active_charters(ix)}
    linked |= {word(b.data.get("charter")) and b.id for b in ix.briefs.values()
               if word(b.data.get("charter")) in {c.id for c in active_charters(ix)}}
    return [p for p in ix.briefs.values() if p.data.get("status") == "probing" and p.id not in linked]


def mix_rows(ix: Index, cfg: dict) -> tuple[list[dict], list[str]]:
    counts = {h: 0 for h in HORIZONS}
    for b in active_charters(ix):
        counts[horizon_of(b.data)] += 1
    counts["probe"] += len(active_probes(ix))
    total = sum(counts.values())
    plan = ix.strategy.data.get("horizons") if ix.strategy and ix.strategy.data.get("status") == "approved" else None
    plan = plan if isinstance(plan, dict) else {}
    rows, notes = [], []
    for h, label in HORIZONS.items():
        share = round(100 * counts[h] / total) if total else 0
        target = plan.get(h) if is_number(plan.get(h)) else None
        rows.append({"horizon": h, "label": label, "count": counts[h], "share": share, "target": target})
    if not plan:
        notes.append("No approved strategy with a horizon mix was found.")
    elif total < 3:
        notes.append(f"Only {total} active bet(s) and probe(s); too few to compare with the planned mix.")
    else:
        for row in rows:
            if row["target"] is not None and abs(row["share"] - row["target"]) > cfg["mix_tolerance_points"]:
                notes.append(f"{row['label']} {row['horizon']}: {row['share']}% of active bets against a plan of "
                             f"{row['target']:g}%")
    return rows, notes


def factory_line(ix: Index, since: date, today: date) -> str | None:
    """Hit rate, time to learn and deletion, from first decisions made in the window."""
    firsts = []
    for b in ix.charters.values():
        rows = [x for x in items(b.data.get("decision_log")) if isinstance(x, dict) and to_date(x.get("date"))]
        if not rows:
            continue
        first = min(rows, key=lambda x: to_date(x["date"]))
        if since <= to_date(first["date"]) <= today:
            firsts.append((b, first))
    removed = [b for b in ix.charters.values()
               if any(isinstance(x, dict) and x.get("decision") == "removed" and to_date(x.get("date"))
                      and since <= to_date(x["date"]) <= today for x in items(b.data.get("decision_log")))]
    if not firsts and not removed:
        return None
    parts = []
    if firsts:
        kept = sum(1 for b, x in firsts if x.get("decision") == "keep")
        parts.append(f"hit rate {kept} of {len(firsts)} first decisions kept")
        days = sorted((to_date(x["date"]) - to_date(b.data.get("approved"))).days for b, x in firsts
                      if to_date(b.data.get("approved")))
        if days:
            mid = days[len(days) // 2] if len(days) % 2 else (days[len(days) // 2 - 1] + days[len(days) // 2]) / 2
            parts.append(f"median time to learn {mid:g} days")
    parts.append(f"{len(removed)} feature{'s' if len(removed) != 1 else ''} removed")
    return "**Factory:** " + "; ".join(parts) + "."


def board(ix: Index, cfg: dict, today: date, since: date, invalid: list[str] | None = None) -> str:
    charters = sorted(ix.charters.values(), key=lambda b: b.id)
    strat = ix.strategy
    title = f"Bet board: {one_line(strat.data.get('name') or strat.id, 60)}" if strat else "Bet board"
    out = [f"# {title}", "", f"As of {today.isoformat()}. Decisions counted since {since.isoformat()}. "
           "Generated from the charters, briefs and strategy in this repository; edit those, not this page.", ""]

    def needle(c):
        b, t = get(c, "needle.baseline"), get(c, "needle.target")
        name = one_line(get(c, "needle.name"), 100)
        if b == "measure_before_launch":
            return f"{name}: baseline not yet measured"
        return f"{name}: {one_line(b, 20)} → {one_line(t, 20)}" if t is not None else name

    def bet(c):
        return one_line(f"{get(c, 'hypothesis.we_believe')} → {get(c, 'hypothesis.will_result_in')}", 120)

    def n(count, one, many):
        return f"{count} {one if count == 1 else many}"

    active = active_charters(ix)
    probes = active_probes(ix)
    decided = []
    for b in charters:
        for x in items(b.data.get("decision_log")):
            if isinstance(x, dict) and to_date(x.get("date")) and since <= to_date(x["date"]) <= today:
                decided.append((to_date(x["date"]), b, x))
    decided.sort(key=lambda t: (t[0], t[1].id), reverse=True)
    freed = sum(get(b.data, "removal.estimate_hours") for d, b, x in decided
                if x.get("decision") == "removed" and is_number(get(b.data, "removal.estimate_hours")))
    tally = {k: sum(1 for d, b, x in decided if x.get("decision") == k) for k in ("keep", "iterate", "sunset", "removed")}
    by_h = {h: sorted((b for b in active if horizon_of(b.data) == h), key=lambda b: b.id) for h in HORIZONS}
    out += [f"**{n(len(by_h['bet']), 'bet', 'bets')}, {n(len(by_h['probe']) + len(probes), 'probe', 'probes')}, "
            f"{n(len(by_h['tune']), 'proven feature', 'proven features')} under renewal.** "
            f"Decided since {since.isoformat()}: {tally['keep']} kept, {tally['iterate']} iterated, "
            f"{tally['sunset']} sunset, {tally['removed']} removed"
            + (f" (about {freed:g} hours of code deleted)" if freed else "") + ".", ""]
    factory = factory_line(ix, since, today)
    if factory:
        out += [factory, ""]

    out += ["## Betting (H2)", ""]
    if by_h["bet"]:
        out += ["| Charter | The bet | Needle | Decision due | Owner |", "|---|---|---|---|---|"]
        for b in by_h["bet"]:
            due = next_due(b.data)
            out.append(f"| {one_line(b.id, 20)} | {bet(b.data)} | {needle(b.data)} | "
                       f"{due.isoformat() if due else 'not set'} | {one_line(b.data.get('owner'), 40)} |")
    else:
        out.append("No active bets.")
    out += ["", "## Probing (H3)", ""]
    rows = [(b.id, bet(b.data), next_due(b.data)) for b in by_h["probe"]]
    rows += [(p.id, one_line(p.data.get("opportunity"), 120), to_date(p.data.get("probe_ends"))) for p in probes]
    if rows:
        out += ["| Id | The question | Ends |", "|---|---|---|"]
        out += [f"| {one_line(i, 20)} | {q} | {d.isoformat() if d else 'not set'} |" for i, q, d in rows]
    else:
        out.append("No probes running.")
    out += ["", "## Tuning (H1)", ""]
    if by_h["tune"]:
        out += ["| Charter | Feature | Needle | Next renewal |", "|---|---|---|---|"]
        for b in by_h["tune"]:
            due = next_due(b.data)
            out.append(f"| {one_line(b.id, 20)} | {one_line(get(b.data, 'hypothesis.we_believe'), 80)} | "
                       f"{needle(b.data)} | {due.isoformat() if due else 'not set'} |")
    else:
        out.append("No proven features under renewal.")
    out += ["", "## Decided", ""]
    if decided:
        out += ["| Date | Charter | Decision | Evidence | Decided by |", "|---|---|---|---|---|"]
        for d, b, x in decided:
            out.append(f"| {d.isoformat()} | {one_line(b.id, 20)} | {one_line(x.get('decision'), 20)} | "
                       f"{one_line(x.get('evidence'), 200)} | {one_line(x.get('decided_by'), 40)} |")
        out += ["", "A kill on its review date is the plan working. Count it next to what shipped."]
    else:
        out.append("No decisions in this window.")
    out += ["", "## Not betting", ""]
    rulings = [x for x in items(strat.data.get("rulings")) if isinstance(x, dict)] if strat else []
    rulings.sort(key=lambda x: (str(x.get("date")), str(x.get("id"))), reverse=True)
    if rulings:
        out += ["| Ruling | Request | Decision | Policy | Why | Reopens if |", "|---|---|---|---|---|---|"]
        for x in rulings:
            out.append(f"| {one_line(x.get('id'), 20)} | {one_line(x.get('request'), 90)} | "
                       f"{one_line(ruling_word(x.get('ruling')) or x.get('ruling'), 20)} | {one_line(x.get('policy'), 20)} | "
                       f"{one_line(x.get('reason'), 200)} | {one_line(x.get('reopen_if'), 160)} |")
    else:
        out.append("No rulings recorded. If nothing has been ruled out, the strategy isn't deciding anything yet.")

    off = []
    for b in active:
        due = next_due(b.data)
        latest = last_decision(b.data)
        if due and due < today and not (latest and to_date(latest["date"]) >= due):
            off.append(f"{b.id}: review was due {due.isoformat()} and has no decision")
    for p in probes:
        ends = to_date(p.data.get("probe_ends"))
        if ends and ends < today:
            off.append(f"{p.id}: the probe ended {ends.isoformat()} and has no decision")
    for b in charters:
        if b.data.get("status") == "sunset":
            s = last_decision(b.data, "sunset")
            if s and (today - to_date(s["date"])).days > cfg["sunset_stuck_days"]:
                off.append(f"{b.id}: sunset on {to_date(s['date']).isoformat()} and still not removed")
    if strat:
        rv = to_date(strat.data.get("review_date"))
        if rv and rv < today:
            off.append(f"The strategy review was due {rv.isoformat()}")
    mrows, notes = mix_rows(ix, cfg)
    off += [n_ for n_ in notes if "against a plan" in n_]
    off += ix.duplicates
    if invalid:
        off.append(f"{n(len(invalid), 'block fails', 'blocks fail')} validation ({', '.join(invalid)}); "
                   "run triage.py validate before trusting this board")
    out += ["", "## Off plan", ""]
    out += [f"- {x}" for x in off] if off else ["Nothing off plan."]
    out += ["", "**Horizon mix** (share of active bets and probes, against the strategy's plan):", "",
            "| Horizon | Now | Plan |", "|---|---|---|"]
    for row in mrows:
        plan = f"{row['target']:g}%" if row["target"] is not None else "not set"
        out.append(f"| {row['label']} {row['horizon']} | {row['count']} ({row['share']}%) | {plan} |")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------------- cli


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check strategies and opportunity briefs, and draw the bet board.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="check strategies, briefs and the links between them and charters")
    v.add_argument("paths", nargs="+")
    v.add_argument("--json", action="store_true")
    v.add_argument("--strict", action="store_true", help="treat warnings as errors")
    m = sub.add_parser("mix", help="active bets by horizon against the strategy's mix")
    m.add_argument("paths", nargs="+")
    bo = sub.add_parser("board", help="write a one-page bet board in Markdown")
    bo.add_argument("paths", nargs="+")
    bo.add_argument("--since", help="count decisions from this date (default: board_window_days ago)")
    bo.add_argument("--out", help="write to this file instead of printing")
    for p in (v, m, bo):
        p.add_argument("--today")
        p.add_argument("--config")
    a = ap.parse_args(argv)

    today = to_date(a.today) if a.today else date.today()
    if today is None:
        ap.error("--today must be YYYY-MM-DD")
    cfg = load_config(a.config)
    blocks = load(a.paths)

    if a.cmd == "validate":
        reports = validate_all(blocks, cfg, today)
        if a.json:
            print(json.dumps([r.as_dict() for r in reports], indent=2))
        elif not reports:
            print("No product-strategy or opportunity-brief blocks, and no charters linked to a strategy.")
        else:
            for r in reports:
                print(f"{'PASS' if r.ok(a.strict) else 'FAIL'}  {r.kind:17} {r.id:10} {r.where}  "
                      f"({len(r.errors)} errors, {len(r.warnings)} warnings)")
                for f, msg in r.errors:
                    print(f"  ERROR {f}: {msg}")
                for f, msg in r.warnings:
                    print(f"  WARN  {f}: {msg}")
        return 0 if all(r.ok(a.strict) for r in reports) else 1

    ix = Index(blocks)
    if a.cmd == "mix":
        rows, notes = mix_rows(ix, cfg)
        for row in rows:
            plan = f"{row['target']:g}%" if row["target"] is not None else "not set"
            print(f"{row['label']} {row['horizon']:6} {row['count']:3} active ({row['share']:3}%)   plan {plan}")
        for note in notes:
            print(f"NOTE  {note}")
        return 0

    since = to_date(a.since) if a.since else today - timedelta(days=int(cfg["board_window_days"]))
    if since is None:
        ap.error("--since must be YYYY-MM-DD")
    invalid = sorted({r.id for r in validate_all(blocks, cfg, today) if r.errors})
    text = board(ix, cfg, today, since, invalid)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"Wrote {a.out}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
