"""Tests for the feature charter validator. Run with: pytest -q"""

import copy
import importlib.util
from datetime import date
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "feature-charter" / "skills" / "feature-charter"
spec = importlib.util.spec_from_file_location("charter", SKILL / "scripts" / "charter.py")
charter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(charter)

TODAY = "2026-10-22"
CFG = dict(charter.DEFAULTS)
GOOD = {
    "id": "FC-100",
    "status": "approved",
    "owner": "PM",
    "builder": "build-agent",
    "judge": "eval-agent",
    "approved": "2026-10-01",
    "hypothesis": {"we_believe": "x", "for": "y", "will_result_in": "z", "because": "w"},
    "needle": {"name": "Median days to paid", "rung": "user_outcome", "definition": "d", "source": "events",
               "baseline": 34, "target": 27, "direction": "decrease", "min_change": 4, "window_days": 28},
    "guardrails": [{"name": "Complaints", "limit": "under 1 per 100"}],
    "evaluation": {"method": "before_after", "review_date": "2026-11-10", "keep_if": "k", "kill_if": "x",
                   "iterate_if": "i", "if_inconclusive": "sunset", "look_at": "6 interviews"},
    "removal": {"flag": "f", "code_paths": ["src/f"], "estimate_hours": 4},
    "decision_log": [],
    "amendments": [],
}


def run(data):
    rep = charter.validate(charter.Charter(data, "test"), CFG, date.fromisoformat(TODAY))
    return {f for f, _ in rep.errors}, {f for f, _ in rep.warnings}


def changed(**paths):
    data = copy.deepcopy(GOOD)
    for dotted, value in paths.items():
        keys = dotted.split("__")
        cur = data
        for k in keys[:-1]:
            cur = cur[k]
        cur[keys[-1]] = value
    return data


def test_good_charter_passes_clean():
    errors, warnings = run(GOOD)
    assert errors == set() and warnings == set()


@pytest.mark.parametrize("path", sorted((ROOT / "examples").glob("*/*.md")))
def test_examples_have_no_errors(path):
    charters = charter.load_file(path)
    if path.name == "before.md" or path.name == "README.md":
        assert charters == []
        return
    assert len(charters) == 1, f"{path} should hold exactly one charter"
    rep = charter.validate(charters[0], CFG, date.fromisoformat(TODAY))
    assert rep.errors == [], rep.errors


def test_before_and_after_keep_every_original_heading():
    for folder in sorted((ROOT / "examples").glob("0*")):
        before = [l for l in (folder / "before.md").read_text().splitlines() if l.startswith("#")]
        after = [l for l in (folder / "after.md").read_text().splitlines() if l.startswith("#")]
        assert [h for h in after if h in before] == before, f"{folder.name}: original headings changed"


def test_builder_cannot_judge():
    assert "judge" in run(changed(judge="build-agent"))[0]


def test_activity_rung_is_an_error_unless_insurance():
    assert "needle.rung" in run(changed(needle__rung="adopted"))[0]
    data = changed(needle__rung="adopted", value_type="insurance", insurance_reason="needed at tax time")
    errors, warnings = run(data)
    assert "needle.rung" not in errors and "needle.rung" in warnings


def test_inconclusive_never_means_keep():
    assert "evaluation.if_inconclusive" in run(changed(evaluation__if_inconclusive="keep"))[0]


def test_review_date_limit():
    assert "evaluation.review_date" in run(changed(evaluation__review_date="2026-12-31"))[0]


def test_target_must_move_in_direction():
    assert "needle.target" in run(changed(needle__target=40))[0]


def test_proposed_charter_can_leave_unknowns():
    data = changed(status="proposed", approved=None, builder="", judge="",
                   needle__baseline="measure_before_launch", needle__target=None,
                   evaluation__review_date=None)
    errors, warnings = run(data)
    assert errors == set()
    assert {"builder", "judge", "needle.baseline", "needle.target", "evaluation.review_date"} <= warnings


def test_unmeasured_baseline_needs_min_change_by_approval():
    proposed = changed(status="proposed", approved=None, needle__baseline="measure_before_launch",
                       needle__target=None, needle__min_change=None)
    assert "needle.min_change" in run(proposed)[1]
    approved = changed(needle__baseline="measure_before_launch", needle__target=None, needle__min_change=None)
    assert "needle.min_change" in run(approved)[0]


def test_keep_needs_next_review_within_limit():
    keep = {"date": "2026-11-10", "decision": "keep", "evidence": "e", "decided_by": "PM"}
    assert "decision_log[0].next_review" in run(changed(status="kept", decision_log=[keep]))[0]
    keep["next_review"] = "2027-06-01"
    assert "decision_log[0].next_review" in run(changed(status="kept", decision_log=[keep]))[0]
    keep["next_review"] = "2027-01-15"
    assert run(changed(status="kept", decision_log=[keep]))[0] == set()


def test_status_needs_matching_decision():
    assert "status" in run(changed(status="sunset"))[0]


def test_locked_fields_need_amendment(tmp_path):
    old = copy.deepcopy(GOOD)
    new = changed(needle__target=30)
    rep = charter.Report(charter.Charter(new, "t"))
    charter.check_baseline(old, new, rep)
    assert [f for f, _ in rep.errors] == ["needle.target"]
    new["amendments"] = [{"date": "2026-10-10", "field": "needle.target", "from": 27, "to": 30,
                          "reason": "baseline remeasured", "approved_by": "PM"}]
    rep = charter.Report(charter.Charter(new, "t"))
    charter.check_baseline(old, new, rep)
    assert rep.errors == []


def test_unapproved_charter_can_change_freely():
    old = changed(status="proposed", approved=None)
    new = changed(status="proposed", approved=None, needle__target=30)
    rep = charter.Report(charter.Charter(new, "t"))
    charter.check_baseline(old, new, rep)
    assert rep.errors == []


def test_markdown_blocks_and_folder_scan(tmp_path):
    spec_md = tmp_path / "docs" / "spec.md"
    spec_md.parent.mkdir()
    spec_md.write_text("# Spec\n\nText\n\n```feature-charter\n" + yaml.safe_dump(GOOD) + "```\n")
    (tmp_path / "docs" / "workflow.yml").write_text("on: push\njobs: {}\n")
    (tmp_path / "docs" / "notes.md").write_text("# Notes\n\n```yaml\nneedle: 1\n```\n")
    found = [c for f, explicit in charter.find_files([str(tmp_path / "docs")]) for c in charter.load_file(f, explicit)]
    assert [c.id for c in found] == ["FC-100"]
    assert found[0].line == 5


def test_template_placeholder_is_skipped(capsys):
    code = charter.main(["validate", str(SKILL / "templates" / "outcome-charter.md")])
    assert code == 0
    assert "Skipped 1 placeholder" in capsys.readouterr().out


def test_skill_files_are_skipped_in_folder_scans():
    files = [f for f, _ in charter.find_files([str(ROOT / "plugins")])]
    assert not any("feature-charter" in f.parts and "skills" in f.parts for f in files)


def test_require_command(tmp_path, capsys):
    spec_md = tmp_path / "spec.md"
    spec_md.write_text("```feature-charter\n" + yaml.safe_dump(GOOD) + "```\n")
    assert charter.main(["require", "FC-100", str(tmp_path), "--today", TODAY]) == 0
    assert charter.main(["require", "FC-999", str(tmp_path)]) == 1
    spec_md.write_text("```feature-charter\n" + yaml.safe_dump(changed(status="proposed")) + "```\n")
    assert charter.main(["require", "FC-100", str(tmp_path), "--today", TODAY]) == 1


def test_due_reports_overdue_and_stuck():
    cs = [charter.Charter(changed(evaluation__review_date="2026-10-15"), "a"),
          charter.Charter(changed(id="FC-101", status="sunset", decision_log=[
              {"date": "2026-08-01", "decision": "sunset", "evidence": "e", "decided_by": "PM"}]), "b")]
    rows = charter.due_rows(cs, CFG, date.fromisoformat(TODAY), 14)
    assert sorted(r["state"] for r in rows) == ["overdue", "stuck_in_sunset"]


def test_config_overrides(tmp_path):
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text("max_review_days: 120\n")
    cfg = charter.load_config(str(cfg_file))
    assert cfg["max_review_days"] == 120 and cfg["max_renewal_days"] == 90
    cfg_file.write_text("max_review_dayz: 1\n")
    with pytest.raises(SystemExit):
        charter.load_config(str(cfg_file))


def test_owner_can_wait_until_approval():
    errors, warnings = run(changed(status="proposed", approved=None, owner=""))
    assert "owner" not in errors and "owner" in warnings
    assert "owner" in run(changed(owner=""))[0]


def test_relative_min_change_and_bad_values():
    data = changed(status="proposed", approved=None, needle__baseline="measure_before_launch",
                   needle__target=None, needle__min_change="10%")
    assert run(data)[0] == set()
    assert "needle.min_change" in run(changed(needle__min_change=-2))[0]
    assert "needle.min_change" in run(changed(needle__min_change="lots"))[0]


def test_wrong_types_report_errors_instead_of_crashing():
    errors, _ = run(changed(status=["live"], needle__rung={"x": 1}, evaluation__method=[1]))
    assert {"status", "needle.rung", "evaluation.method"} <= errors


def test_one_approved_extension_doubles_the_review_limit():
    late = changed(evaluation__review_date="2026-11-30")
    assert "evaluation.review_date" in run(late)[0]
    late["amendments"] = [{"date": "2026-11-05", "field": "evaluation.review_date", "from": "2026-11-10",
                           "to": "2026-11-30", "reason": "events were broken for a week", "approved_by": "PM"}]
    assert run(late)[0] == set()


def test_changing_the_id_does_not_dodge_pre_registration(tmp_path, capsys):
    old, new = tmp_path / "old.md", tmp_path / "new.md"
    old.write_text("```feature-charter\n" + yaml.safe_dump(GOOD) + "```\n")
    new.write_text("```feature-charter\n" + yaml.safe_dump(changed(id="FC-101", needle__target=33)) + "```\n")
    assert charter.main(["validate", str(new), "--baseline", str(old), "--today", TODAY]) == 1
    assert "changed from FC-100" in capsys.readouterr().out


def test_require_scans_text_with_configured_pattern(tmp_path):
    (tmp_path / "spec.md").write_text("```feature-charter\n" + yaml.safe_dump(GOOD) + "```\n")
    assert charter.main(["require", str(tmp_path), "--text", "Implements FC-100.", "--today", TODAY]) == 0
    assert charter.main(["require", str(tmp_path), "--text", "No id here", "--today", TODAY]) == 1


def test_bad_config_value_is_rejected(tmp_path):
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text('max_review_days: "60"\n')
    with pytest.raises(SystemExit):
        charter.load_config(str(cfg_file))


def test_story_link_holds_only_safe_fields():
    from urllib.parse import urlparse, parse_qs
    keep = {"date": "2026-11-10", "decision": "keep", "evidence": "secret 34 to 28", "decided_by": "Jane Doe",
            "next_review": "2027-01-15"}
    url = charter.story_link(changed(status="kept", decision_log=[keep]), "We kept it.", "PRD")
    q = parse_qs(urlparse(url).query)
    assert url.startswith("https://github.com/bgervin/when-building-is-free/issues/new?")
    assert q["template"] == ["charter-story.yml"] and q["decision"] == ["keep"]
    assert q["rung"] == ["user_outcome"] and q["spec_format"] == ["PRD"] and q["story"] == ["We kept it."]
    assert "Jane" not in url and "secret" not in url and "FC-100" not in url


def test_story_link_needs_a_decision_and_respects_opt_out(tmp_path, monkeypatch):
    with pytest.raises(SystemExit):
        charter.story_link(GOOD, "x")
    spec_md = tmp_path / "spec.md"
    keep = {"date": "2026-11-10", "decision": "keep", "evidence": "e", "decided_by": "PM", "next_review": "2027-01-15"}
    spec_md.write_text("```feature-charter\n" + yaml.safe_dump(changed(status="kept", decision_log=[keep])) + "```\n")
    (tmp_path / ".feature-charter.yml").write_text("story_prompt: false\n")
    monkeypatch.chdir(tmp_path)
    assert charter.main(["story-link", "FC-100", str(spec_md), "--story", "x"]) == 1
