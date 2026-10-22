"""Tests for the feedback-triage tool (strategy, briefs, links, mix, bet board). Run with: pytest -q"""

import copy
import importlib.util
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "feedback-triage" / "skills" / "feedback-triage"
spec = importlib.util.spec_from_file_location("triage", SKILL / "scripts" / "triage.py")
triage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(triage)

TODAY = date(2026, 10, 22)
CFG = dict(triage.DEFAULTS)
EX = ROOT / "examples"
EXAMPLE_PATHS = [str(EX / "05-strategy-and-triage" / "strategy.md"), str(EX / "05-strategy-and-triage" / "after.md"),
                 str(EX / "01-github-issue-payment-reminders" / "review.md"),
                 str(EX / "04-spec-kit-onboarding-checklist" / "after.md")]

STRATEGY = {
    "id": "ST-2026H2", "name": "Test", "status": "approved", "owner": "Head of Product",
    "approved": "2026-07-06", "review_date": "2026-10-30", "diagnosis": "Customers get paid late.",
    "segments": {"target": [{"id": "SEG-01", "name": "Small", "definition": "2 to 20 staff"}],
                 "not_target": [{"id": "SEG-X1", "name": "Large", "why": "needs an ERP"}]},
    "policies": [{"id": "P-01", "statement": "Cash cycle first.", "decides": "Yes to reminders"}],
    "areas": [{"id": "payments", "name": "Payments"}],
    "horizons": {"tune": 30, "bet": 50, "probe": 20},
    "rulings": [{"id": "R-001", "request": "Themes", "ruling": "not_now", "policy": "P-01", "reason": "Not paid sooner",
                 "reopen_if": "Five accounts cite it", "decided_by": "HoP", "date": "2026-07-06"}],
}
BRIEF = {
    "id": "OPP-001", "status": "shortlisted", "area": "payments", "segment": "SEG-01",
    "opportunity": "Office managers chase late payments", "requests": ["#1"],
    "breadth": {"accounts": 10, "in_segment": 8}, "rung": "user_outcome",
    "strategy": {"policy": "P-01", "horizon": "bet"}, "flags": [],
}


def blocks(strategy=None, brief=None, charter=None):
    out = []
    if strategy is not None:
        out.append(triage.Block("product-strategy", strategy, "s.md", 1))
    if brief is not None:
        out.append(triage.Block("opportunity-brief", brief, "b.md", 1))
    if charter is not None:
        out.append(triage.Block("feature-charter", charter, "c.md", 1))
    return out


def fields(reports, kind):
    rep = next(r for r in reports if r.kind == kind)
    return {f for f, _ in rep.errors}, {f for f, _ in rep.warnings}


def with_(base, **paths):
    data = copy.deepcopy(base)
    for dotted, value in paths.items():
        keys = dotted.split("__")
        cur = data
        for k in keys[:-1]:
            cur = cur[k]
        cur[keys[-1]] = value
    return data


def test_good_strategy_and_brief_pass_clean():
    reps = triage.validate_all(blocks(STRATEGY, BRIEF), CFG, TODAY)
    assert all(r.errors == [] and r.warnings == [] for r in reps)


def test_examples_validate_and_link():
    reps = triage.validate_all(triage.load(EXAMPLE_PATHS), CFG, TODAY)
    assert {r.id for r in reps} >= {"ST-2026H2", "OPP-001", "OPP-002", "OPP-003", "OPP-004", "FC-007", "FC-014"}
    assert all(r.errors == [] and r.warnings == [] for r in reps), [r.as_dict() for r in reps if not r.ok(True)]


def test_example_bet_board_is_current():
    ix = triage.Index(triage.load(EXAMPLE_PATHS))
    text = triage.board(ix, CFG, TODAY, date(2026, 7, 24))
    assert text == (EX / "05-strategy-and-triage" / "bet-board.md").read_text(encoding="utf-8"), \
        "regenerate examples/05-strategy-and-triage/bet-board.md (see examples/README.md)"


def test_goal_shaped_policy_and_no_exclusions_warn():
    s = with_(STRATEGY, policies=[{"id": "P-01", "statement": "Increase ARR by 30%", "decides": "x"}],
              segments={"target": STRATEGY["segments"]["target"], "not_target": []})
    _, warnings = fields(triage.validate_all(blocks(s), CFG, TODAY), "product-strategy")
    assert {"policies[0].statement", "segments.not_target"} <= warnings


def test_policy_without_decides_warns():
    s = with_(STRATEGY, policies=[{"id": "P-01", "statement": "Cash cycle first."}])
    _, warnings = fields(triage.validate_all(blocks(s), CFG, TODAY), "product-strategy")
    assert "policies[0].decides" in warnings


def test_rulings_need_reason_reopen_and_a_real_policy():
    s = with_(STRATEGY, rulings=[{"id": "R-001", "request": "x", "ruling": "maybe", "policy": "P-09", "date": "2026-07-06"}])
    errors, _ = fields(triage.validate_all(blocks(s), CFG, TODAY), "product-strategy")
    assert {"rulings[0].ruling", "rulings[0].policy", "rulings[0].reason", "rulings[0].reopen_if",
            "rulings[0].decided_by"} <= errors


def test_horizon_mix_must_add_to_100_and_review_has_a_limit():
    s = with_(STRATEGY, horizons={"tune": 30, "bet": 50, "probe": 30}, review_date="2027-03-01")
    errors, _ = fields(triage.validate_all(blocks(s), CFG, TODAY), "product-strategy")
    assert {"horizons", "review_date"} <= errors


def test_diagnosis_and_target_segment_are_required():
    s = with_(STRATEGY, diagnosis="", segments={})
    errors, _ = fields(triage.validate_all(blocks(s), CFG, TODAY), "product-strategy")
    assert {"diagnosis", "segments.target"} <= errors


def test_brief_links_must_resolve():
    b = with_(BRIEF, area="mars", segment="SEG-99", strategy={"policy": "P-09", "horizon": "later"})
    errors, _ = fields(triage.validate_all(blocks(STRATEGY, b), CFG, TODAY), "opportunity-brief")
    assert {"area", "segment", "strategy.policy", "strategy.horizon"} <= errors


def test_brief_for_a_non_target_segment_is_an_error():
    errors, _ = fields(triage.validate_all(blocks(STRATEGY, with_(BRIEF, segment="SEG-X1")), CFG, TODAY),
                       "opportunity-brief")
    assert "segment" in errors


def test_narrow_breadth_warns_hostage_or_design_partner():
    b = with_(BRIEF, breadth={"accounts": 1, "in_segment": 1})
    _, warnings = fields(triage.validate_all(blocks(STRATEGY, b), CFG, TODAY), "opportunity-brief")
    assert "breadth.in_segment" in warnings


def test_breadth_counts_must_be_sane():
    b = with_(BRIEF, breadth={"accounts": 2, "in_segment": 5})
    errors, _ = fields(triage.validate_all(blocks(STRATEGY, b), CFG, TODAY), "opportunity-brief")
    assert "breadth.in_segment" in errors


def test_flags_need_notes_and_known_names():
    b = with_(BRIEF, flags=["hostage_customer", "squeaky_wheel"])
    errors, _ = fields(triage.validate_all(blocks(STRATEGY, b), CFG, TODAY), "opportunity-brief")
    assert {"flags", "flag_notes"} <= errors


def test_activity_rung_warns():
    _, warnings = fields(triage.validate_all(blocks(STRATEGY, with_(BRIEF, rung="adopted")), CFG, TODAY),
                         "opportunity-brief")
    assert "rung" in warnings


def test_chartered_brief_needs_its_charter_and_ruled_out_needs_a_ruling():
    errors, _ = fields(triage.validate_all(blocks(STRATEGY, with_(BRIEF, status="chartered")), CFG, TODAY),
                       "opportunity-brief")
    assert "charter" in errors
    errors, _ = fields(triage.validate_all(blocks(STRATEGY, with_(BRIEF, status="ruled_out", ruling="R-404")), CFG, TODAY),
                       "opportunity-brief")
    assert "ruling" in errors


def test_charter_strategy_link_must_resolve():
    ch = {"id": "FC-100", "status": "approved", "strategy": {"policy": "P-09", "area": "mars", "horizon": "bet"}}
    errors, _ = fields(triage.validate_all(blocks(STRATEGY, None, ch), CFG, TODAY), "feature-charter")
    assert {"strategy.policy", "strategy.area"} <= errors


def test_placeholders_and_skill_files_are_skipped():
    found = triage.load([str(SKILL)])
    assert found == []
    templ = triage.load([str(SKILL / "templates" / "strategy.md")])
    assert templ == []


def test_mix_flags_drift_from_plan():
    charters = [{"id": f"FC-{i}", "status": "live", "strategy": {"policy": "P-01", "horizon": "bet"}} for i in range(4)]
    bl = blocks(STRATEGY) + [triage.Block("feature-charter", c, "c.md") for c in charters]
    rows, notes = triage.mix_rows(triage.Index(bl), CFG)
    assert {r["horizon"]: r["share"] for r in rows} == {"tune": 0, "bet": 100, "probe": 0}
    assert any("bet" in n and "against a plan" in n for n in notes)


def test_kept_charter_counts_as_tuning():
    assert triage.horizon_of({"status": "kept", "strategy": {"horizon": "bet"}}) == "tune"


def test_board_lists_rulings_decisions_and_overdue_reviews():
    ch = {"id": "FC-100", "status": "live", "owner": "PM",
          "hypothesis": {"we_believe": "reminders", "will_result_in": "paid sooner"},
          "needle": {"name": "Days to paid", "baseline": 34, "target": 27},
          "evaluation": {"review_date": "2026-10-01"}, "decision_log": []}
    gone = {"id": "FC-101", "status": "removed", "removal": {"estimate_hours": 6},
            "decision_log": [{"date": "2026-10-10", "decision": "removed", "evidence": "deleted", "decided_by": "PM"}]}
    bl = blocks(STRATEGY) + [triage.Block("feature-charter", ch, "c.md"), triage.Block("feature-charter", gone, "d.md")]
    text = triage.board(triage.Index(bl), CFG, TODAY, date(2026, 7, 24))
    assert "R-001" in text and "FC-101 | removed" in text and "about 6 hours of code deleted" in text
    assert "FC-100: review was due 2026-10-01" in text


def test_cli_validate_exit_codes(tmp_path, capsys):
    good = tmp_path / "strategy.md"
    good.write_text("```product-strategy\n" + yaml.safe_dump(STRATEGY) + "```\n")
    assert triage.main(["validate", str(good), "--today", "2026-10-22"]) == 0
    bad = tmp_path / "bad.md"
    bad.write_text("```product-strategy\n" + yaml.safe_dump(with_(STRATEGY, diagnosis="")) + "```\n")
    assert triage.main(["validate", str(bad), "--today", "2026-10-22"]) == 1
