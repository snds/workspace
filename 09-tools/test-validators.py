#!/usr/bin/env python3
"""Negative fixtures: each detector must FAIL a planted defect.

The live-tree validators only see a healthy checkout. A broken detector looks
green forever. This harness plants small broken trees and asserts errors.
Pattern: vault-retrieve.py --eval.

Usage:
  python3 09-tools/test-validators.py
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT_DIR = TOOLS.parent


def load(name: str):
    path = TOOLS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    # Python 3.14 dataclasses look up sys.modules[cls.__module__] during decorate.
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestValidatorFixtures(unittest.TestCase):
    def test_workspace_rejects_unindexed_knowledge(self):
        vw = load("validate-workspace")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            kdir = root / "08-knowledge" / "research"
            kdir.mkdir(parents=True)
            (kdir / "orphan-entry.md").write_text("# Orphan\n", encoding="utf-8")
            index = root / "08-knowledge" / "_INDEX.md"
            index.write_text("# Index\nNo mention of the orphan.\n", encoding="utf-8")
            errors = []
            vw.check_knowledge(
                errors,
                knowledge_dir=root / "08-knowledge",
                knowledge_index=index,
                root=root,
            )
            self.assertTrue(any("orphan-entry" in e for e in errors), errors)

    def test_workspace_rejects_unindexed_memory(self):
        vw = load("validate-workspace")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mdir = root / "06-context" / "memory"
            mdir.mkdir(parents=True)
            (mdir / "fact-orphan.md").write_text("# Orphan fact\n", encoding="utf-8")
            index = mdir / "MEMORY.md"
            index.write_text("# Memory\n", encoding="utf-8")
            errors = []
            vw.check_memory(errors, memory_dir=mdir, memory_index=index)
            self.assertTrue(any("fact-orphan" in e for e in errors), errors)

    def test_workspace_rejects_unlogged_archive(self):
        vw = load("validate-workspace")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = root / "_archive"
            archive.mkdir()
            (archive / "lost-note.md").write_text("# Lost\n", encoding="utf-8")
            log = archive / "ARCHIVE-LOG.md"
            log.write_text("# Log\nNothing about lost-note.\n", encoding="utf-8")
            errors = []
            vw.check_archive(errors, archive=archive, archive_log=log, root=root)
            self.assertTrue(any("lost-note" in e for e in errors), errors)

    def test_workspace_rejects_missing_adapter(self):
        vw = load("validate-workspace")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            errors = []
            vw.check_adapters(errors, root=root, files=["GEMINI.md"], configs=[])
            self.assertTrue(any("missing tool adapter: GEMINI.md" in e for e in errors), errors)

    def test_workspace_rejects_adapter_without_contract(self):
        vw = load("validate-workspace")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "GEMINI.md").write_text("# Gemini\nDo whatever.\n", encoding="utf-8")
            errors = []
            vw.check_adapters(errors, root=root, files=["GEMINI.md"], configs=[])
            self.assertTrue(any("AGENTS.md" in e for e in errors), errors)
            self.assertTrue(any("close-out" in e for e in errors), errors)

    def test_links_rejects_dangling_related(self):
        vl = load("validate-links")
        with tempfile.TemporaryDirectory() as td:
            skills = Path(td) / "03-skills"
            a = skills / "aaa"
            a.mkdir(parents=True)
            (a / "SKILL.md").write_text(
                "---\nname: aaa\n---\n\n## Related\n- hub → [[ghost-skill]]\n",
                encoding="utf-8",
            )
            recs, aliases = vl.load_skills(skills)
            errors, _warnings = vl.collect_findings(recs, aliases)
            self.assertTrue(any("dangling" in e and "ghost-skill" in e for e in errors), errors)

    def test_links_rejects_missing_reciprocal(self):
        vl = load("validate-links")
        with tempfile.TemporaryDirectory() as td:
            skills = Path(td) / "03-skills"
            (skills / "aaa").mkdir(parents=True)
            (skills / "bbb").mkdir(parents=True)
            (skills / "aaa" / "SKILL.md").write_text(
                "---\nname: aaa\n---\n\n## Related\n- hub → [[bbb]]\n",
                encoding="utf-8",
            )
            (skills / "bbb" / "SKILL.md").write_text(
                "---\nname: bbb\n---\n\n## Related\n",
                encoding="utf-8",
            )
            recs, aliases = vl.load_skills(skills)
            errors, _warnings = vl.collect_findings(recs, aliases)
            self.assertTrue(any("not reciprocated" in e for e in errors), errors)

    def test_integrity_rejects_dangling_wikilink(self):
        vi = load("validate-integrity")
        errs = vi.dangling_wikilinks(
            "note.md",
            "See [[zz-fixture-ghost-note-xyz]].",
            names=set(),
            root=Path(tempfile.gettempdir()),
        )
        self.assertTrue(any("zz-fixture-ghost-note-xyz" in e for e in errs), errs)

    def test_integrity_skips_vendored_copilot_not_vault(self):
        vi = load("validate-integrity")
        self.assertTrue(vi.excluded_from_scan("copilot/skills/obsidian-markdown/SKILL.md"))
        self.assertTrue(vi.excluded_from_scan("copilot/skills/obsidian-markdown/references/EMBEDS.md"))
        self.assertFalse(vi.excluded_from_scan("03-skills/qa/SKILL.md"))
        self.assertFalse(vi.excluded_from_scan("08-knowledge/design/centric-plm-design-system.md"))
        self.assertFalse(vi.excluded_from_scan(".claude/skills/session-end/SKILL.md"))

    def test_integrity_rejects_name_dir_mismatch(self):
        vi = load("validate-integrity")
        err = vi.skill_name_dir_error(
            "03-skills/foo/SKILL.md",
            "foo",
            "---\nname: bar\n---\n",
        )
        self.assertIsNotNone(err)
        self.assertIn("bar", err)
        self.assertIn("foo", err)

    def test_capabilities_rejects_missing_reciprocity(self):
        vc = load("validate-capabilities")
        cap = {
            "kind": "mcp",
            "provides": "x",
            "detect": {},
            "install": {},
            "fallback": "degrade",
            "powers": [],
        }
        errors, _warnings = vc.check_contract(
            {"figma-mcp": cap},
            {"lead-ui-designer": {"requires": ["figma-mcp"]}},
            "figma-mcp is documented in prose",
        )
        self.assertTrue(any("reciprocity" in e for e in errors), errors)

    def test_capabilities_accepts_reciprocal_pair(self):
        vc = load("validate-capabilities")
        cap = {
            "kind": "mcp",
            "provides": "x",
            "detect": {},
            "install": {},
            "fallback": "degrade",
            "powers": ["lead-ui-designer"],
        }
        errors, warnings = vc.check_contract(
            {"figma-mcp": cap},
            {"lead-ui-designer": {"requires": ["figma-mcp"]}},
            "figma-mcp is documented in prose",
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_vault_health_rejects_dangling_relation(self):
        vh = load("vault-health")
        text = (
            "---\n"
            "relations:\n"
            "  builds-on:\n"
            "    - \"[[ghost-note]]\"\n"
            "---\n"
            "# Hi\n"
        )
        dang = vh.dangling_relations(text, known_stems={"other"})
        self.assertEqual(dang, ["ghost-note"])

    def test_registry_parses_wrapped_flow_list(self):
        br = load("build-registry")
        fm = br.parse_frontmatter(
            "---\nname: wrap\ntriggers: [foo, bar,\n  baz]\n---\n"
        )
        self.assertEqual(fm.get("triggers"), ["foo", "bar", "baz"])

    def test_routing_string_triggers_are_not_characters(self):
        ev = load("evaluate-skill-routing")
        self.assertEqual(
            ev._as_terms("[career-ops, career ops, portal scanner,"),
            ["career-ops", "career ops", "portal scanner"],
        )
        self.assertEqual(ev._as_terms("single"), ["single"])

    def test_routing_lint_rejects_stopword_trigger(self):
        ev = load("evaluate-skill-routing")
        original = ev.load_registry
        ev.load_registry = lambda: {"fake-skill": ["a", "ok"]}
        try:
            errors = ev.lint_triggers()
        finally:
            ev.load_registry = original
        self.assertTrue(any("stopword" in e and "fake-skill" in e for e in errors), errors)

    def test_routing_detects_missing_expected_skill(self):
        ev = load("evaluate-skill-routing")
        errors = ev.eval_case(
            {
                "id": "planted-miss",
                "utterance": "hello world with no skill words",
                "expect_skills": ["does-not-exist-skill"],
            }
        )
        self.assertTrue(any("does-not-exist-skill" in e for e in errors), errors)

    def test_routing_article_does_not_load_career_ops(self):
        ev = load("evaluate-skill-routing")
        errors = ev.eval_case(
            {
                "id": "article-a",
                "utterance": "continually run whenever it makes the most sense during a session",
                "forbid_skills": ["career-ops-job-search", "job-search-strategist"],
            }
        )
        self.assertEqual(errors, [])


class TestIntentRun(unittest.TestCase):
    SAMPLE = """---
profile: personal-solo
approval: pending
---

# Spec

## Fidelity / acceptance checklist

- [ ] tests -- measure: python3 -c 'print(1)'
- [ ] no cmd

## Task graph

| id | role | skill / specialist | isolation | depends_on | status | evidence |
|---|---|---|---|---|---|---|
| T0 | coordinator | intent-coordination | n/a | - | | spec |
| T1 | implementor | design-engineer | worktree | T0 | | code |
"""

    def test_gate_blocks_pending_approval(self):
        ir = load("intent-run")
        spec = ir.parse_spec(self.SAMPLE)
        self.assertFalse(ir.approval_ok(spec["meta"]))
        self.assertEqual(ir.ready_implementors(spec), [])

    def test_ready_after_approval(self):
        ir = load("intent-run")
        spec = ir.parse_spec(self.SAMPLE.replace("approval: pending", "approval: approved 2026-09-04 by Sean"))
        self.assertTrue(ir.approval_ok(spec["meta"]))
        ready = ir.ready_implementors(spec)
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0]["id"], "T1")
        self.assertEqual(spec["checks"][0]["measure"], "python3 -c 'print(1)'")
        self.assertEqual(spec["checks"][1]["measure"], "")


class TestPromptRouteFollowthrough(unittest.TestCase):
    """Produce language must inject close-out; empty Layer 0 on work verbs must not be silent."""

    @classmethod
    def setUpClass(cls):
        cls.pr = load("prompt_route")
        cls.brain = cls.pr.resolve_brain_root(TOOLS.parent)
        if cls.brain is None:
            raise unittest.SkipTest("no portable workspace root")

    def test_figma_produce_injects_close_out(self):
        text = self.pr.route_prompt("build this in figma", self.brain)
        self.assertIn("close-out", text)
        self.assertIn("self-improve", text)
        self.assertIn("Project trigger detected", text)

    def test_implement_button_injects_close_out(self):
        text = self.pr.route_prompt("implement this button", self.brain)
        self.assertIn("close-out", text)
        self.assertIn("self-improve", text)

    def test_hub_hit_plus_work_verb_injects_close_out(self):
        text = self.pr.route_prompt("fix the spacing on this card", self.brain)
        self.assertIn("close-out", text)
        self.assertIn("self-improve", text)

    def test_ungrounded_work_verb_is_visible_miss(self):
        text = self.pr.route_prompt("make the primary button blue", self.brain)
        self.assertIn("Layer 0 missed", text)
        self.assertNotEqual(text, "")
        self.assertNotIn("Say that Layer 0 missed", text)

    def test_make_sure_is_not_a_miss(self):
        text = self.pr.route_prompt(
            "Make sure these are reliably wired across the workspace.",
            self.brain,
        )
        self.assertEqual(text, "")

    def test_greeting_stays_empty(self):
        text = self.pr.route_prompt("hello how are you today", self.brain)
        self.assertEqual(text, "")

    def test_produce_names_dispatch_cli(self):
        text = self.pr.route_prompt("build this in figma", self.brain)
        self.assertIn("close-out-dispatch.py", text)

    def test_layer0_miss_names_loadset_and_retrieve(self):
        text = self.pr.route_prompt("make the primary button blue", self.brain)
        self.assertIn("skill-loadset.py", text)
        self.assertIn("vault-retrieve.py", text)


class TestSkillLoadset(unittest.TestCase):
    def test_dashboard_palette_chain(self):
        sl = load("skill-loadset")
        result = sl.load_set("dark-mode palette for this dashboard")
        self.assertIn("uid-color-for-ui", result["load"])
        self.assertIn("design-foundations", result["load"])
        self.assertLess(
            result["load"].index("design-foundations"),
            result["load"].index("uid-color-for-ui"),
        )
        self.assertTrue(any(p.endswith("uid-color-for-ui/SKILL.md") for p in result["paths"]))
        self.assertIn("close-out-dispatch.py", result["close_out"])

    def test_self_test_cli(self):
        sl = load("skill-loadset")
        self.assertEqual(sl.self_test(), 0)


class TestCloseOutDispatch(unittest.TestCase):
    def test_check_covers_command_hubs(self):
        d = load("close-out-dispatch")
        self.assertEqual(d.check_table(), 0)

    def test_figma_splits_capture_from_assess(self):
        # A8 (2026-09-15): capture still needs MCP and stays an honest SKIP, but ASSESS is
        # now a real detector. Asserting both halves so neither can quietly regress — a
        # scripted "capture" would be a lie, and a skipped assess is the gap A8 closed.
        d = load("close-out-dispatch")
        plan = d.format_plan(["figma"])
        self.assertIn("figma-mcp-capture", plan)
        self.assertIn("SKIP `figma-mcp-capture`", plan)
        self.assertIn("CLI `figma-bind-probe.py --self-test`", plan)
        self.assertEqual(d.run_hubs(["lead-mobile-engineer"]), 2)

    def test_figma_probe_refuses_planted_violations(self):
        probe = load("figma-bind-probe")
        clean = json.loads((TOOLS / "fixtures"
                            / "figma-capture.clean.json").read_text(encoding="utf-8"))
        dirty = json.loads((TOOLS / "fixtures"
                            / "figma-capture.violations.json").read_text(encoding="utf-8"))
        self.assertEqual(probe.evaluate(clean)["failures"], [])
        self.assertTrue(probe.evaluate(dirty)["failures"])
        # Nothing to verify must never read as a pass.
        self.assertEqual(probe.evaluate({"system": "x"})["verified"], [])

    def test_from_prompt_figma(self):
        d = load("close-out-dispatch")
        data = json.loads(d.REGISTRY.read_text(encoding="utf-8"))
        hubs = d.hubs_for_prompt("build this in figma", data)
        self.assertIn("figma", hubs)


class TestCheckSecrets(unittest.TestCase):
    def test_planted_aws_key_fails(self):
        cs = load("check-secrets")
        planted = "AKIA" + "FAKESECRETTEST99"
        hits = cs.findings_in_text(f"aws_key={planted}\n")
        self.assertTrue(any(name == "aws-access-key" for name, _ in hits), hits)

    def test_clean_prose_passes(self):
        cs = load("check-secrets")
        self.assertEqual(cs.findings_in_text("Use the capability registry URL, not a key.\n"), [])

    def test_scan_planted_tree(self):
        cs = load("check-secrets")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            tools = root / "09-tools"
            tools.mkdir()
            planted = "sk-ant-" + ("a" * 24)
            (tools / "leak.txt").write_text(f"key={planted}\n", encoding="utf-8")
            errors = cs.scan_root(root)
            self.assertTrue(any("anthropic-key" in e for e in errors), errors)


class TestLayer0Schema(unittest.TestCase):
    def test_live_files_pass(self):
        vl = load("validate-layer0-schema")
        errors = vl.check_files()
        self.assertEqual(errors, [], errors)

    def test_missing_utterance_fails(self):
        vl = load("validate-layer0-schema")
        errors: list[str] = []
        vl.check_routing_case({"id": "x"}, "row", errors)
        self.assertTrue(any("utterance" in e for e in errors), errors)

    def test_malformed_jsonl_fails(self):
        vl = load("validate-layer0-schema")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bad = root / "cases.jsonl"
            bad.write_text("{not json\n", encoding="utf-8")
            tr = root / "tr.json"
            tr.write_text(
                '{"spec_version":"1.0","templates":{"A":"x"},"routes":{"a":"b"}}\n',
                encoding="utf-8",
            )
            kh = root / "kh.json"
            kh.write_text('{"spec_version":"1.0","hints":{"a":"b"}}\n', encoding="utf-8")
            errors = vl.check_files(tr, kh, bad)
            self.assertTrue(errors, errors)


class TestScopedCommit(unittest.TestCase):
    """The scoped-commit path must see Bash writes and must not take another session's."""

    def _dispatcher(self):
        # The dispatcher sys.exit(0)s at import without CLAUDE_PROJECT_DIR — that guard
        # is deliberate (a stray copy must not treat an arbitrary cwd as the workspace),
        # so satisfy it rather than working around it.
        path = ROOT_DIR / ".claude" / "hooks" / "dispatcher.py"
        if not path.is_file():
            self.skipTest("dispatcher not present")
        spec = importlib.util.spec_from_file_location("ws_dispatcher", path)
        if spec is None or spec.loader is None:
            self.skipTest("dispatcher not importable")
        mod = importlib.util.module_from_spec(spec)
        prior = os.environ.get("CLAUDE_PROJECT_DIR")
        os.environ["CLAUDE_PROJECT_DIR"] = str(ROOT_DIR)
        try:
            spec.loader.exec_module(mod)
        except SystemExit:  # pragma: no cover - guard tripped anyway
            self.skipTest("dispatcher aborted at import")
        finally:
            if prior is None:
                os.environ.pop("CLAUDE_PROJECT_DIR", None)
            else:
                os.environ["CLAUDE_PROJECT_DIR"] = prior
        return mod

    def test_other_session_claims_are_excluded(self):
        d = self._dispatcher()
        with tempfile.TemporaryDirectory() as td:
            sessions = Path(td)
            original = d.SESSIONS_DIR
            d.SESSIONS_DIR = sessions
            try:
                (sessions / "mine.touched").write_text("a.md\nshared.md\n", encoding="utf-8")
                (sessions / "theirs.touched").write_text("shared.md\nb.md\n", encoding="utf-8")
                claims = d._other_session_claims("mine")
                self.assertEqual(claims, {"shared.md", "b.md"})
                self.assertNotIn("a.md", claims)
                # and a session does not claim against itself
                self.assertEqual(d._other_session_claims("theirs"), {"a.md", "shared.md"})
            finally:
                d.SESSIONS_DIR = original

    def test_bash_writes_are_recorded_by_snapshot_diff(self):
        d = self._dispatcher()
        with tempfile.TemporaryDirectory() as td:
            sessions = Path(td)
            original_dir, original_dirty = d.SESSIONS_DIR, d._dirty_paths
            d.SESSIONS_DIR = sessions
            try:
                # Turn 1: two paths dirty. Neither came through an Edit/Write tool.
                d._dirty_paths = lambda: {"09-tools/x.py", "notes/y.md"}
                d._record_bash_writes("s1")
                touched = (sessions / "s1.touched").read_text(encoding="utf-8").split()
                self.assertIn("09-tools/x.py", touched)
                self.assertIn("notes/y.md", touched)
                # Turn 2: one new path. Only the new one is appended, no duplicates.
                d._dirty_paths = lambda: {"09-tools/x.py", "notes/y.md", "notes/z.md"}
                d._record_bash_writes("s1")
                touched = (sessions / "s1.touched").read_text(encoding="utf-8").split()
                self.assertIn("notes/z.md", touched)
                self.assertEqual(len(touched), len(set(touched)), "no duplicate entries")
                self.assertEqual(touched.count("09-tools/x.py"), 1)
            finally:
                d.SESSIONS_DIR, d._dirty_paths = original_dir, original_dirty

    def test_dirty_paths_parses_rename_and_untracked(self):
        d = self._dispatcher()
        original = d.git
        try:
            d.git = lambda *a, **k: type("R", (), {"stdout": ' M a.md\n?? b.md\nR  old.md -> new.md\n'})()
            self.assertEqual(d._dirty_paths(), {"a.md", "b.md", "new.md"})
        finally:
            d.git = original


class TestSessionStatus(unittest.TestCase):
    def test_check_and_card(self):
        ss = load("session-status")
        data = ss.collect(surface="test", via="test")
        self.assertGreaterEqual(data["pending"], 0)
        self.assertTrue(data["sha"])
        card = ss.format_card(data)
        self.assertIn("workspace: LOADED", card)
        self.assertIn("Active projects", card)
        self.assertIn("Pending:", card)
        self.assertIn("What's on the agenda today?", card)

    def test_pending_counts_open_boxes(self):
        ss = load("session-status")
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pc.md"
            path.write_text("- [ ] open one\n- [x] done\n- [ ] open two\n", encoding="utf-8")
            self.assertEqual(ss.count_pending(path), 2)

    def test_stamp_age_parses_heading_and_yaml(self):
        # Dates are computed relative to today, never hardcoded: a fixture stamped
        # with the authoring date turns green-on-write into a fail-forever clock bomb
        # (observed 2026-09-15, this very test). Assert the parser, not the calendar.
        ss = load("session-status")
        today = dt.date.today()
        with tempfile.TemporaryDirectory() as td:
            heading = Path(td) / "audit.md"
            heading.write_text(
                f"## {today - dt.timedelta(days=13)} — Personal MacBook Pro\n", encoding="utf-8"
            )
            yaml = Path(td) / "stamp"
            yaml.write_text(
                f"date: {today - dt.timedelta(days=3)}\nreport: x.md\n", encoding="utf-8"
            )
            self.assertEqual(ss._stamp_age_days(heading), 13)
            self.assertEqual(ss._stamp_age_days(yaml), 3)


class TestShadcnLintOverlay(unittest.TestCase):
    def _probe(self):
        path = TOOLS / "shadcn-lint" / "probe.py"
        spec = importlib.util.spec_from_file_location("shadcn_lint_probe", path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load {path}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["shadcn_lint_probe"] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_overlay_self_test_passes(self):
        probe = self._probe()
        self.assertEqual(probe.self_test(), [])

    def test_overlay_rejects_radix_step_and_allows_semantic(self):
        probe = self._probe()
        spec = probe.load_spec()
        self.assertEqual(probe.iter_leaks("bg-primary mt-4", spec), [])
        self.assertEqual(probe.iter_leaks("bg-blue-9", spec), ["bg-blue-9"])
        self.assertEqual(probe.iter_leaks("md:bg-blue-500/50", spec), ["md:bg-blue-500/50"])
        self.assertEqual(probe.iter_leaks("bg-white", spec), ["bg-white"])
        self.assertEqual(probe.iter_leaks("bg-cds-blue-500", spec), ["bg-cds-blue-500"])
        self.assertEqual(probe.iter_leaks("bg-cds-gray-1000", spec), ["bg-cds-gray-1000"])

    def test_overlay_policy_names_shadcn_rules(self):
        probe = self._probe()
        self.assertEqual(probe.validate_policy(), [])
        self.assertEqual(probe.validate_config(), [])

    def test_overlay_refuses_policy_that_disables_raw_colors(self):
        probe = self._probe()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "design-system.lint.json"
            rules = {name: "error" for name in probe.REQUIRED_SHADCN_RULES}
            path.write_text(
                json.dumps(
                    {
                        "rules": rules,
                        "overrides": [
                            {
                                "files": ["**/components/ui/**"],
                                "rules": {"shadcn/no-raw-colors": "off"},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            errors = probe.validate_policy(path)
            self.assertTrue(any("no-raw-colors" in e for e in errors), errors)

    def test_overlay_refuses_tuple_off_and_warn(self):
        probe = self._probe()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "design-system.lint.json"
            rules = {name: "error" for name in probe.REQUIRED_SHADCN_RULES}
            path.write_text(
                json.dumps(
                    {
                        "rules": {
                            **rules,
                            "shadcn/no-raw-colors": ["off", {"message": "x"}],
                        },
                        "overrides": [{"files": ["**/*"], "rules": {}}],
                    }
                ),
                encoding="utf-8",
            )
            errors = probe.validate_policy(path)
            self.assertTrue(any("no-raw-colors" in e for e in errors), errors)
            path.write_text(
                json.dumps(
                    {
                        "rules": rules,
                        "overrides": [
                            {
                                "files": ["**/components/ui/**"],
                                "rules": {"ds-lint/no-tier-leakage": "warn"},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            errors = probe.validate_policy(path)
            self.assertTrue(any("no-tier-leakage" in e for e in errors), errors)

    def test_overlay_refuses_config_without_companion_rule(self):
        probe = self._probe()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "eslint.ds.config.mjs"
            path.write_text("export default []\n", encoding="utf-8")
            errors = probe.validate_config(path)
            self.assertTrue(any("no-tier-leakage" in e for e in errors), errors)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
