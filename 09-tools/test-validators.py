#!/usr/bin/env python3
"""Negative fixtures: each detector must FAIL a planted defect.

The live-tree validators only see a healthy checkout. A broken detector looks
green forever. This harness plants small broken trees and asserts errors.
Pattern: vault-retrieve.py --eval.

Usage:
  python3 09-tools/test-validators.py                       # every class
  python3 09-tools/test-validators.py TestSurfaces TestWsHook  # named classes only
  python3 09-tools/test-validators.py --strict-skips TestIdentity

Exit: 0 green · 1 a test failed · 2 unknown class name · 3 a test skipped under
--strict-skips (a device measure that silently SKIPs is not a pass).
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT_DIR = TOOLS.parent


def load(name: str):
    """Load a 09-tools module by stem ("nightly") or a repo-relative path
    ("00-bootstrap/doctor/render_shims.py")."""
    if "/" in name or name.endswith(".py"):
        path = ROOT_DIR / name
        name = path.stem
    else:
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

    @staticmethod
    def _isolated_env(home):
        return {"HOME": str(home), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}

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

    def test_self_test_passes(self):
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            env = dict(os.environ, **self._isolated_env(td))
            r = subprocess.run([sys.executable, str(TOOLS / "intent-run.py"), "--self-test"],
                               capture_output=True, text=True, env=env, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])

    def test_frontmatter_and_approval_grammar(self):
        ir = load("intent-run")

        def fm(line):
            meta, _, comments = ir._split_frontmatter_ex("---\n" + line + "\n---\n")
            return meta, comments

        meta, comments = fm("approval: approved via PR 12")
        self.assertEqual(meta["approval"], "approved via PR 12")
        self.assertEqual(ir.approval_detail(meta, comments)["pr"], 12)
        meta, comments = fm('approval: "approved via PR #12"')
        self.assertEqual(meta["approval"], "approved via PR #12")
        self.assertEqual(ir.approval_detail(meta, comments)["errors"], [])
        meta, comments = fm("approval: approved via PR #12")
        self.assertEqual(comments["approval"], "#12")
        self.assertTrue(ir.approval_detail(meta, comments)["errors"])
        self.assertTrue(any(level == "ERROR" for level, _ in ir.lint_spec(
            {"meta": meta, "meta_comments": comments})))
        self.assertEqual(fm("blocked_by: x#F-003")[0]["blocked_by"], "x#F-003")
        self.assertEqual(fm("profile: personal-solo # c")[0]["profile"], "personal-solo")
        det = ir.approval_detail(fm("approval: approved 2026-09-22 by Sean (chat 'go')")[0])
        self.assertEqual((det["kind"], det["by"], det["grammar_ok"]), ("approved", "Sean", True))

    def test_escaped_pipe_and_measure_delimiter(self):
        ir = load("intent-run")
        rows = ir._parse_table("| a | b |\n|---|---|\n| (foo\\|bar) | z |\n")
        self.assertEqual(rows, [{"a": "(foo|bar)", "b": "z"}])
        spec = ir.parse_spec("---\nprofile: p\n---\n## Fidelity / acceptance checklist\n\n"
                             "- [ ] x -- measure: python3 a.py -- signal: y\n")
        self.assertEqual(spec["checks"][0]["measure"], "python3 a.py")

    def test_no_git_write_invariant(self):
        ir = load("intent-run")
        self.assertEqual(ir.git_write_violations((TOOLS / "intent-run.py").read_text(encoding="utf-8")), [])
        self.assertTrue(ir.git_write_violations("import subprocess\nsubprocess.run(['git','commit'])\n"))

    def test_verify_human_and_injection_never_run(self):
        import contextlib
        import io
        import subprocess
        from unittest import mock
        ir = load("intent-run")
        with tempfile.TemporaryDirectory() as tds:
            td = Path(tds).resolve()
            with mock.patch.dict(os.environ, self._isolated_env(td)):
                repo = td / "repo"
                (repo / "09-tools").mkdir(parents=True)
                subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True, timeout=30)
                (repo / "09-tools" / "ok.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
                subprocess.run(["git", "add", "09-tools/ok.py"], cwd=repo, check=True, timeout=30)
                pwned, human = td / "pwned", td / "human"
                spec = td / "spec.md"
                spec.write_text(
                    "---\nprofile: personal-solo\napproval: approved 2026-01-01 by Fixture\n---\n"
                    "## Fidelity / acceptance checklist\n\n"
                    "- [ ] ok -- measure: python3 09-tools/ok.py\n"
                    f"- [ ] injected -- measure: python3 09-tools/x.py; touch {pwned}\n"
                    f"- [ ] person -- measure: human: touch {human}\n", encoding="utf-8")
                results = set()
                for automated in (True, False):
                    buf = io.StringIO()
                    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                        rc = ir.cmd_verify(spec, True, str(repo), automated=automated)
                    results.add((automated, rc))
                    self.assertFalse(pwned.exists(), buf.getvalue())
                    self.assertFalse(human.exists(), buf.getvalue())
                    self.assertIn("HUMAN: person", buf.getvalue())
                self.assertIn((True, 2), results)
                self.assertIn((False, 1), results)

    def test_automated_context_fail_closed_and_claudecode_tty(self):
        ir = load("intent-run")

        def boom():
            raise ImportError("absent")

        self.assertTrue(ir.automated_context(loader=boom)[0])
        tty = {"stdin": True, "stdout": True}
        fake = ir.automated_context(env={"CLAUDECODE": "1"}, ancestry=[], isatty=tty,
                                    loader=lambda: ir._FakeResolver)
        self.assertTrue(fake[0])
        if (TOOLS / "profile_resolve.py").is_file():
            pr = load("profile_resolve")
            self.assertTrue(ir.automated_context(env={"CLAUDECODE": "1"}, ancestry=[], isatty=tty,
                                                 loader=lambda: pr)[0])
            self.assertTrue(ir.automated_context(env={"CI": "1"}, ancestry=[], isatty=tty,
                                                 loader=lambda: pr)[0])

    def test_scope_audit_held_and_integrator_paths(self):
        import contextlib
        import io
        from unittest import mock
        ir = load("intent-run")
        with tempfile.TemporaryDirectory() as tds:
            td = Path(tds).resolve()
            with mock.patch.dict(os.environ, self._isolated_env(td)):
                spec = td / "INTENT-fixture.md"
                spec.write_text((TOOLS / "fixtures" / "intent_run" / "synthetic-spec.md")
                                .read_text(encoding="utf-8"), encoding="utf-8")

                def run(files, name):
                    repo, env = ir._new_repo(td, name)
                    h = ir._History(repo, env)
                    b0 = h.commit("main", "base", {"README.md": "x\n"})
                    tip = h.commit("intent/T2", "wave0(T2): work", files, frm=b0)
                    h.flush()
                    merged = dict(files, **{"tools/test-validators.py": "# w9\n"})
                    h.commit("main", "wave0(T9a): merge intent/T2", merged, frm=b0, merge=tip)
                    h.flush()
                    buf = io.StringIO()
                    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                        rc = ir.cmd_scope_audit(spec, task=None, rev=None, wave_merges=True,
                                                ref="main", root=str(repo))
                    return rc, buf.getvalue()

                rc, out = run({"tools/beta.py": "b\n"}, "ok")
                self.assertEqual(rc, 0, out)
                rc, out = run({"tools/beta.py": "b\n", "held/x.md": "x\n"}, "held")
                self.assertEqual(rc, 1, out)
                self.assertIn("held: held/x.md", out)


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

    # --- appended to TestSessionStatus (H25) ---
    def test_self_test_oracle_and_family_cases(self):
        import contextlib
        import io
        ss = load("session-status")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = ss.self_test()
        if rc == 3:
            self.skipTest("the 2ff02e7 card oracle is not in local history (shallow clone)")
        self.assertEqual(rc, 0)

    def test_no_hostname_map_literal(self):
        src = (TOOLS / "session-status.py").read_text(encoding="utf-8")
        self.assertNotIn("HOSTNAME" + "_MAP", src)

    def test_cursor_sessionstart_renders_the_cursor_card(self):
        """T10 rerun L-01: Cursor exports CLAUDE_PROJECT_DIR into every hook process, which detection
        ranks as Claude. The Cursor shim still renders the Cursor card (no Claude-only hiding)."""
        script = ROOT_DIR / "00-bootstrap" / "dist" / "cursor-sessionstart.sh"
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            (home / ".claude").mkdir()
            (home / ".claude" / "workspace-brain-path").write_text(f"{ROOT_DIR}\n", encoding="utf-8")
            env = {"HOME": str(home), "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "CURSOR_VERSION": "2.0",
                   "CURSOR_PROJECT_DIR": str(ROOT_DIR), "CLAUDE_PROJECT_DIR": str(ROOT_DIR)}
            r = subprocess.run(["bash", str(script)], input='{"cursor_version": "2.0"}', env=env,
                               capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        ctx = json.loads(r.stdout)["additional_context"]
        self.assertIn("workspace: LOADED", ctx)
        self.assertNotIn("handled by Cursor/Codex", ctx)

    def test_import_failure_label_is_short_hostname(self):
        import socket
        ss = load("session-status")
        saved = sys.modules.get("profile_resolve")
        sys.modules["profile_resolve"] = None
        try:
            self.assertEqual(ss.machine_label(), socket.gethostname().split(".", 1)[0])
        finally:
            if saved is None:
                sys.modules.pop("profile_resolve", None)
            else:
                sys.modules["profile_resolve"] = saved


class TestSetupTemplates(unittest.TestCase):
    """T10 rerun L-03: the setup gitconfig template never routes the personal identity over the projects
    root of a device whose default identity is an employer one (employer checkouts live there: I1)."""

    def test_gitconfig_template_has_no_personal_route_over_an_employer_projects_root(self):
        import re
        tpl = (ROOT_DIR / "00-bootstrap" / "setup" / "gitconfig.template").read_text(encoding="utf-8")
        routes = re.findall(r'\[includeIf "gitdir(?:/i)?:([^"]+)"\]\s*\n\s*path\s*=\s*(\S+)', tpl)
        self.assertTrue(routes)
        dev = json.loads((ROOT_DIR / "02-shared-references" / "devices.json").read_text(encoding="utf-8"))
        ids = {i["id"]: i for i in dev["identities"]}
        roots = {d["projects_root"] for d in dev["devices"]
                 if ids.get(d.get("default_identity"), {}).get("class") == "employer"}
        self.assertTrue(roots)
        for pat, path in routes:
            if "personal" not in path:
                continue
            for r in roots:
                with self.subTest(route=pat, projects_root=r):
                    self.assertFalse(f"~/{r}/".casefold().startswith(pat.rstrip("*").casefold()),
                                     f"{pat} -> {path} covers ~/{r}/")


class TestPublicClaims(unittest.TestCase):
    """T10 rerun L-04: a public gate description never claims a parity the registrations do not deliver."""

    def test_surface_parity_claim_matches_the_cursor_registrations(self):
        regs = ""
        for rel in ("00-bootstrap/dist/cursor-hooks.json", ".cursor/hooks.json"):
            p = ROOT_DIR / rel
            if p.is_file():
                regs += p.read_text(encoding="utf-8")
        if "cursor-prompt-route" in regs or "beforeSubmitPrompt" in regs:
            self.skipTest("a Cursor prompt-route registration exists again; the parity claim may stand")
        agents = " ".join((ROOT_DIR / "AGENTS.md").read_text(encoding="utf-8").split())
        self.assertNotIn("every surface delivers the SAME context", agents)


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


class TestProfileResolve(unittest.TestCase):
    """H2 resolver: fixtures, shipped tables, detection seams, scan refusal (profile_resolve.py)."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load("profile_resolve")

    def test_self_test_negative_fixtures(self):
        rc = self.mod.self_test()
        if rc == 3:
            self.skipTest("profile_resolve self-test SKIPPED cases (git below 2.54, ps not permitted, or a pinned copy)")
        self.assertEqual(rc, 0)

    def test_shipped_tables_validate(self):
        res = self.mod.validate_tables()["tables"]
        for name in ("devices", "context-remotes"):
            self.assertTrue(res[name]["present"], name)
            self.assertTrue(res[name]["ok"], res[name]["errors"])
        for name, entry in res.items():
            if entry["present"]:
                self.assertTrue(entry["ok"], f"{name}: {entry['errors']}")

    def test_hostname_normalization(self):
        for row in self.mod.load_table("devices").get("devices") or []:
            h0 = (row.get("hostnames") or [None])[0]
            if not h0:
                continue
            for host in (h0 + ".lan", h0.lower(), h0.upper() + ".local"):
                self.assertEqual(self.mod.current_device(hostname=host)["id"], row["id"])
        dev = self.mod.current_device(hostname="host-z.local", scutil=lambda: None)
        self.assertEqual(dev["id"], "unknown")
        self.assertFalse(dev["hostname_known"])
        self.assertTrue(dev["notice"])

    def test_normalize_remote_drops_userinfo(self):
        fake = "not-a-real-" + "credential"
        n = self.mod.normalize_remote(f"https://someone:{fake}@bitbucket.org/Acme-BB/x.git")
        self.assertEqual((n["host"], n["owner"], n["slug"], n["form"]),
                         ("bitbucket.org", "acme-bb", "acme-bb/x", "https-userinfo"))
        self.assertNotIn(fake, json.dumps(n))
        self.assertEqual(self.mod.normalize_remote("github-work:acme-corp/x")["host"], "github.com")

    def test_scan_refused_under_claude_env_cache_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            tel = self.mod.ws_paths(home=home)["telemetry"]
            tel.mkdir(parents=True)
            cache = tel / "checkouts.json"
            cache.write_text('{"schema_version": 1, "checkouts": []}\n', encoding="utf-8")
            before = cache.read_bytes()
            det = self.mod.detect_surface(env={"CLAUDE_PROJECT_DIR": "/x"}, ancestry=[{"comm": "launchd"}],
                                          isatty={"stdin": False, "stdout": False})
            out = self.mod.scan(home=home, detection=det)
            self.assertTrue(out["refused"])
            self.assertEqual(cache.read_bytes(), before)

    def test_agent_check_seams(self):
        tty = {"stdin": True, "stdout": True}
        shell = [{"comm": "zsh"}, {"comm": "Terminal"}, {"comm": "launchd"}]
        self.assertTrue(self.mod.agent_check(env={}, ancestry=shell, isatty=tty)["human"])
        self.assertFalse(self.mod.agent_check(env={"CI": "1"}, ancestry=shell, isatty=tty)["human"])
        self.assertFalse(self.mod.agent_check(env={"CLAUDECODE": "1"}, ancestry=shell, isatty=tty)["human"])
        r = self.mod.agent_check(env={}, ancestry=[{"comm": "zsh"}, {"comm": "Claude Helper (Renderer)"}], isatty=tty)
        self.assertFalse(r["human"])
        self.assertIn("agent:claude", r["reasons"])

    def test_workspace_classifies_personal(self):
        res = self.mod.repo_resolve(str(ROOT_DIR), detection=self.mod.detect_surface(
            env={}, ancestry=[{"comm": "claude"}], isatty={"stdin": False, "stdout": False}))
        self.assertIn(res["source"], ("workspace-root", "linked-worktree"))
        self.assertEqual(self.mod.classify_word(res), "personal")

    @unittest.skipUnless(os.environ.get("CI"), "real stub-ancestor chain runs in CI only")
    def test_stub_ancestor_chain(self):
        rc = self.mod.self_test(stub_chain=True)
        git = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10).stdout.strip()
        # A SKIP (exit 3) is not a pass; name it: the hook-level floor fixtures need git >= 2.54 (T10 rerun T-04).
        self.assertEqual(rc, 0, f"self_test(stub_chain=True) exit {rc}; skipped {list(self.mod._SELFTEST_SKIPS)}; "
                                f"{git} (the hook-level floor fixtures need git >= 2.54)")


class TestActionPolicy(unittest.TestCase):
    """H22 action policy: committed table schema, decide() matrix, verb map, bypass, routes (profile_resolve.py)."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load("profile_resolve")
        cls.fx = TOOLS / "fixtures" / "action_policy"

    def _tmp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return Path(os.path.realpath(td.name))

    def test_t7_fixture_suite(self):
        fails = []
        self.mod._t7_self_test(self._tmp(), lambda cond, label: None if cond else fails.append(label))
        self.assertEqual(fails, [])

    def test_committed_tables_validate_and_fixture_mirrors_ids(self):
        res = self.mod.validate_tables()["tables"]
        for name in ("action-policy", "vetted-scripts"):
            self.assertTrue(res[name]["present"], name)
            self.assertTrue(res[name]["ok"], res[name]["errors"])
        real = self.mod.load_table("action-policy")
        fx = json.loads((self.fx / "action-policy.json").read_text(encoding="utf-8"))
        self.assertEqual([r["id"] for r in real["rules"]], [r["id"] for r in fx["rules"]])
        self.assertEqual([r["id"] for r in real["verb_map"]], [r["id"] for r in fx["verb_map"]])

    def test_schema_negatives_fail_the_validator(self):
        base = json.loads((self.fx / "action-policy.json").read_text(encoding="utf-8"))
        cases = [
            (lambda t: t["rules"][2]["when"].__setitem__("action_class", ["mischief"]), "unknown value 'mischief'"),
            (lambda t: t.pop("default_outcome"), "missing key 'default_outcome'"),
            (lambda t: t["rules"][0]["when"].__setitem__("mood", True), "unknown key 'mood'"),
            (lambda t: t["verb_map"][0].__setitem__("class", "mischief"), "unknown class"),
        ]
        for mutate, needle in cases:
            bad = json.loads(json.dumps(base))
            mutate(bad)
            errs = self.mod.validate_table("action-policy", bad)
            self.assertTrue(any(needle in e for e in errs), (needle, errs))

    def test_matrix_matches_item9_oracle(self):
        table = json.loads((self.fx / "action-policy.json").read_text(encoding="utf-8"))
        rows = self.mod._matrix_facts()
        self.assertGreater(len(rows), 10000)
        for f in rows:
            self.assertEqual(self.mod.policy_decide(f, table)["outcome"], self.mod._oracle(f), f)

    def test_committed_rows_p19_p21_p22_p40(self):
        t = self.mod.load_table("action-policy")
        base = {"walls_family": "claude", "device": "work-mbp", "positively_personal": False,
                "under_projects_root": False, "chain_has_agent": True, "hook_bypass": False}
        d = self.mod.policy_decide(dict(base, owner_class="unknown", action_class="author", has_remote=False), t)
        self.assertEqual((d["rule_id"][:3], d["outcome"]), ("P19", "allow"))
        d = self.mod.policy_decide(dict(base, owner_class="third-party", action_class="meta", has_remote=True), t)
        self.assertEqual((d["rule_id"][:3], d["outcome"]), ("P21", "allow"))
        d = self.mod.policy_decide(dict(base, owner_class="third-party", action_class="publish", has_remote=True), t)
        self.assertEqual((d["rule_id"][:3], d["outcome"]), ("P22", "deny"))
        d = self.mod.policy_decide({"walls_family": "cursor", "device": "personal-mbp", "owner_class": "employer",
                                    "action_class": "author", "chain_has_agent": True, "hook_bypass": False}, t)
        self.assertEqual((d["rule_id"][:3], d["outcome"]), ("P40", "deny"))

    def test_verb_map_and_hook_bypass(self):
        tmp = self._tmp()
        root = self.mod._t7_fixture_root(tmp)
        det = {"family_for_walls": "human", "agent_possible": False}

        def one(text, **kw):
            inv = self.mod.classify_command(text, cwd=str(tmp), root=root, detection=det, **kw)
            return inv[0]["class"], inv[0]["target_ref"], inv[0]["hook_bypass"]

        self.assertEqual(one("git frobnicate")[0], "author")
        self.assertEqual(one("git commit -m x", current_branch="main")[:2], ("author", "default"))
        self.assertEqual(one("git commit -m x", current_branch="feat/x")[:2], ("author", "non-default"))
        self.assertEqual(one("git push")[:2], ("merge", "unknown"))
        self.assertEqual(one("git push origin --delete feat/x")[0], "housekeeping")
        for text in ("git -c hook.x.command=true push", "git commit --no-verify -m x", "git commit -n -m x",
                     "GIT_CONFIG_COUNT=0 git push", "env -u GIT_CONFIG_COUNT git push"):
            self.assertTrue(one(text)[2], text)
        inv = self.mod.parse_command("cd /r && bash -lc \"command /usr/bin/git -C sub fetch\"")
        self.assertEqual((inv[0]["tool"], inv[0]["argv"], inv[0]["cwd_hint"]), ("git", ["fetch"], "/r/sub"))

    def test_hand_set_markers_and_composed_push_delete_denied(self):
        tmp = self._tmp()
        root = self.mod._t7_fixture_root(tmp)
        home = tmp / "t7-home"
        emp, _bare, _env = self.mod._employer_pair(tmp, home)
        det = self.mod.detect_surface(env={"WS_VETTED": "1", "WS_WALL_OK": "1"}, ancestry=[{"comm": "claude"}],
                                      isatty={"stdin": True, "stdout": True}, root=root)
        r = self.mod.policy(repo=str(emp), command="WS_VETTED=1 WS_WALL_OK=1 git push origin --delete feat/done",
                            root=root, home=home, detection=det, device="dev-a")
        self.assertEqual((r["outcome"], r["rule_id"]), ("deny", "P11-claude-employer-composed"))
        r = self.mod.policy(repo=str(emp), command="git commit -m x", root=root, home=home, detection=det,
                            device="dev-a", record=False)
        self.assertEqual((r["outcome"], r["route_to"]), ("route", ["cursor", "codex"]))


class TestVettedContext(unittest.TestCase):
    """H22 vetted path: pinned blob, lifted env, receipts, pin lag, prune fixes (profile_resolve.py, prune)."""

    @classmethod
    def setUpClass(cls):
        cls.mod = load("profile_resolve")

    def _tmp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return Path(os.path.realpath(td.name))

    def test_prune_self_test(self):
        self.assertEqual(load("prune-our-branches").self_test(), 0)

    def test_lift_env_drops_only_the_transport_block(self):
        env = {"HOME": "/h", "WS_SURFACE_FAMILY": "claude", "GH_CONFIG_DIR": "/h/gh", "GIT_AUTHOR_NAME": "x",
               "GIT_COMMITTER_EMAIL": "y", "GIT_CONFIG_COUNT": "3",
               "GIT_CONFIG_KEY_0": "hook.floor.command", "GIT_CONFIG_VALUE_0": "ws-hook",
               "GIT_CONFIG_KEY_1": "url.fixture-blocked-remote://.insteadOf", "GIT_CONFIG_VALUE_1": "git@github.com:acme-corp/",
               "GIT_CONFIG_KEY_2": "credential.https://github.com.helper", "GIT_CONFIG_VALUE_2": ""}
        root = self.mod._t7_fixture_root(self._tmp())
        out = self.mod.lift_env(env, root=root)
        self.assertEqual(out["GIT_CONFIG_COUNT"], "2")
        self.assertEqual((out["GIT_CONFIG_KEY_0"], out["GIT_CONFIG_KEY_1"]),
                         ("hook.floor.command", "credential.https://github.com.helper"))
        self.assertNotIn("GIT_CONFIG_KEY_2", out)
        self.assertNotIn("GIT_AUTHOR_NAME", out)
        self.assertNotIn("GIT_COMMITTER_EMAIL", out)
        self.assertEqual(out["WS_SURFACE_FAMILY"], "claude")
        self.assertEqual(out["GH_CONFIG_DIR"], "/h/gh")
        self.assertNotIn("GH_CONFIG_DIR", self.mod.lift_env(env, needs_employer_gh=True, root=root))

    def test_hash_mismatch_and_pin_lag(self):
        tmp = self._tmp()
        root = self.mod._t7_fixture_root(tmp)
        home = tmp / "t7-home"
        script = self.mod._write(root / "09-tools" / "fixture-housekeeper.py", "# v1\n")
        self.assertEqual(self.mod.vetted_status("fixture-housekeeper", home=home, root=root)["status"], "unpinned")
        self.mod._pin_fixture(home, root, "09-tools/fixture-housekeeper.py", self.mod.git_blob_sha(script))
        self.assertEqual(self.mod.vetted_status("fixture-housekeeper", home=home, root=root)["status"], "vetted")
        self.mod._write(script, "# v2, not pinned\n")
        self.assertEqual(self.mod.vetted_status("fixture-housekeeper", home=home, root=root)["status"], "hash-mismatch")
        self.mod._write(script, "# v1\n")
        reg = self.mod.TABLE_PATHS["vetted-scripts"]
        (root / reg).write_text(json.dumps({"schema_version": 1, "doc": "edited", "scripts": []}), encoding="utf-8")
        self.assertEqual(self.mod.vetted_status("fixture-housekeeper", home=home, root=root)["status"], "vetted")

    def test_receipts_never_create_control(self):
        home = self._tmp() / "bare-home"
        with self.assertRaises(OSError):
            self.mod.append_receipt({"type": "receipt", "result": "ok"}, home=home)
        self.assertFalse((home / ".config").exists())

    def test_present_state_v4_regression(self):
        tmp = self._tmp()
        home = tmp / "home"
        v4 = self.mod._v4_fixture_env(self.mod._git_env(home))
        if v4 is None:
            self.skipTest("no v4 fragment in this checkout")
        emp, bare, genv = self.mod._employer_pair(tmp, home)
        composed = self.mod._g(v4, "push", "origin", "--delete", "feat/done", cwd=emp)
        self.assertNotEqual(composed.returncode, 0)
        lifted = self.mod._g(self.mod.lift_env(v4), "push", "origin", "--delete", "feat/done", cwd=emp)
        self.assertEqual(lifted.returncode, 0, lifted.stderr)
        gone = self.mod._g(genv, "--git-dir", str(bare), "show-ref", "--verify", "--quiet", "refs/heads/feat/done")
        self.assertNotEqual(gone.returncode, 0)


class TestIdentity(unittest.TestCase):
    """G4b/H17: identity matrix, express override, floor decisions in process, hasconfig include (git >= 2.36)."""

    @classmethod
    def setUpClass(cls):
        cls.pr = load("profile_resolve")
        cls.rs = load("00-bootstrap/doctor/render_shims.py")
        cls.fc = load("09-tools/fixtures/identity/floor_cases.py")

    def _tmp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return Path(os.path.realpath(td.name))

    def _cases(self, cases):
        skipped = [c for c in cases if c[1] is None]
        if skipped:
            self.skipTest(f"{len(skipped)} case(s) skipped: {skipped[0][2]}")
        for name, passed, detail in cases:
            with self.subTest(case=name):
                self.assertTrue(passed, detail)

    def test_t8_unit_suite(self):
        fails = []
        self.pr._t8_self_test(self._tmp(), lambda cond, label: None if cond else fails.append(label))
        self.assertEqual(fails, [])

    def test_shipped_identity_keys(self):
        res = self.pr.validate_tables(require_all=True)["tables"]["devices"]
        self.assertTrue(res["ok"], res["errors"])
        dev = self.pr.load_table("devices")
        rule = self.pr.identity_rule("claude", "work-mbp", dev)
        self.assertEqual((rule["id"], rule["identity"], rule.get("overridable")), ("IR1", "snds", False))
        self.assertEqual(self.pr.identity_rule("cursor", "work-mbp", dev)["identity"], "centric")
        self.assertEqual(self.pr.identity_rule("codex", "personal-mbp", dev)["identity"], "snds")
        self.assertIsNone(self.pr.identity_rule("cursor", "unknown", dev))

    def test_shipped_employer_email_domain(self):
        """D5 (2026-09-23): the employer mail domain, matched exactly and casefolded; personal markers win."""
        dev, d5 = self.pr.load_table("devices"), "centricsoftware.com"
        self.assertIn(d5, dev["employer_allowlist"]["email_domains"])
        for addr, want in ((f"user@{d5}", "employer"), ("USER@CentricSoftware.COM", "employer"),
                           (f"user@{d5}.evil.io", "other"), (f"user@not{d5}", "other"), (f"user@mail.{d5}", "other")):
            with self.subTest(addr=addr):
                self.assertEqual(self.pr.email_class(addr, dev), want)
        both = json.loads(json.dumps(dev))
        both["personal_markers"]["emails"].append(f"user@{d5}")
        self.assertEqual(self.pr.email_class(f"user@{d5}", both), "personal")

    def test_hasconfig_include(self):
        self._cases(self.fc.identity_cases(self.pr, self.rs))


class TestOverlay(unittest.TestCase):
    """H17: the v5 overlay render (golden, owners x forms x case, guarded floor, no GIT_AUTHOR_*),
    the v4 reproduction, the tracked fragment, the gh belt and --install-claude-overlay on a temp HOME."""

    @classmethod
    def setUpClass(cls):
        cls.pr = load("profile_resolve")
        cls.rs = load("00-bootstrap/doctor/render_shims.py")
        cls.fc = load("09-tools/fixtures/identity/floor_cases.py")

    def test_emitter_cases(self):
        for name, passed, detail in self.rs.overlay_cases():
            with self.subTest(case=name):
                self.assertTrue(passed, detail)

    def test_tracked_fragment_is_the_v5_render(self):
        cr, dev = self.rs.identity_tables(ROOT_DIR)
        frag = json.loads((ROOT_DIR / "00-bootstrap/dist/settings-user-fragment.json").read_text(encoding="utf-8"))
        self.assertNotIn("env", frag)          # D-W1-4: other hosts import Claude's settings env
        envf = (ROOT_DIR / "00-bootstrap/dist/claude-overlay.env").read_text(encoding="utf-8")
        self.assertEqual(envf, self.rs.render_overlay_env_file(cr, dev, "v5"))
        env = dict(self.rs.overlay_env_file_pairs(cr, dev, "v5"))
        self.assertEqual(env, dict(self.rs.overlay_env(cr, dev, "v5"), WS_OVERLAY_CHANNEL="env-file"))
        self.assertEqual(env["WS_CLAUDE_OVERLAY"], "v5")
        self.assertFalse([k for k in env if k.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_"))])
        inc = (ROOT_DIR / "00-bootstrap/dist/git/claude-identity.inc").read_text(encoding="utf-8")
        self.assertEqual(inc, self.rs.render_claude_identity_inc(dev))

    def test_gh_belt_names_no_employer_account(self):
        dev = self.pr.load_table("devices")
        cr = self.pr.load_table("context-remotes")
        employer = [a for i in dev["identities"] if i["class"] == "employer" for a in i["accounts"]]
        employer += [o["owner"] for o in cr["owners"] if o["class"] == "employer"]
        self.assertTrue(employer)
        hosts = (ROOT_DIR / "00-bootstrap/dist/gh-claude/hosts.yml").read_text(encoding="utf-8").casefold()
        for name in employer:
            self.assertNotIn(name.casefold(), hosts)

    def test_install_claude_overlay_on_temp_home(self):
        for name, passed, detail in self.fc.overlay_install_cases(self.pr, self.rs):
            with self.subTest(case=name):
                self.assertTrue(passed, detail)


class TestClaudeFloor(unittest.TestCase):
    """G4a: the rendered floor under git >= 2.54 config hooks: listed, survives repo-local overrides,
    guarded when the pin is absent, exact hook arguments."""

    @classmethod
    def setUpClass(cls):
        cls.pr = load("profile_resolve")
        cls.rs = load("00-bootstrap/doctor/render_shims.py")
        cls.fc = load("09-tools/fixtures/identity/floor_cases.py")

    def test_floor_hook_cases(self):
        cases = self.fc.claude_floor_cases(self.pr, self.rs)
        if any(c[1] is None for c in cases):
            self.skipTest(cases[0][2])
        for name, passed, detail in cases:
            with self.subTest(case=name):
                self.assertTrue(passed, detail)


class TestFloorDecisions(unittest.TestCase):
    """G5b: floor decisions through real git hooks (transport block lifted, local bare remote), each with
    its own rule id on stderr; the declared bypass residuals; transport refusal is not a floor pass."""

    @classmethod
    def setUpClass(cls):
        cls.pr = load("profile_resolve")
        cls.rs = load("00-bootstrap/doctor/render_shims.py")
        cls.fc = load("09-tools/fixtures/identity/floor_cases.py")

    def test_floor_decision_cases(self):
        cases = self.fc.floor_decision_cases(self.pr, self.rs)
        for name, passed, detail in cases:
            if passed is None:
                continue
            with self.subTest(case=name):
                self.assertTrue(passed, detail)
        skipped = [c for c in cases if c[1] is None]
        if skipped:
            self.skipTest(f"{len(skipped)} case(s) SKIPPED: {skipped[0][2]}")


class TestGitLanes(unittest.TestCase):
    """H18: the global config-based git lanes, installed by the real installer into a temp HOME. In an
    employer-shaped temp repo an I1 commit and a Claude-chain commit are blocked with the repo byte-identical
    (including .git/), a rebase-created personal commit is blocked at pre-push, personal repos pass; the
    doctor --check audit finds config entries that replace, clear or disable a lane;
    the declared bypasses are recorded as residuals. git < 2.54 SKIPs (never a pass)."""

    @classmethod
    def setUpClass(cls):
        cls.gl = load("git_lanes")
        cls.lc = load("09-tools/fixtures/git_lanes/lane_cases.py")

    def test_rendered_include_is_current(self):
        self.assertEqual(self.gl.cmd_render(True), 0, "run python3 09-tools/git_lanes.py render")

    def test_lane_cases(self):
        cases = self.lc.lane_cases()
        for name, passed, detail in cases:
            if passed is None:
                continue
            with self.subTest(case=name):
                self.assertTrue(passed, detail)
        skipped = [c for c in cases if c[1] is None]
        if skipped:
            self.skipTest(f"{len(skipped)} case(s) SKIPPED: {skipped[0][2]}")


class TestPinLib(unittest.TestCase):
    """H24 pin_lib: its own fixture suite, plus the real-home guard against the REAL
    profile_resolve verdict (never a human verdict with confirm_real_home=True)."""

    def test_self_test(self):
        import subprocess
        r = subprocess.run([sys.executable, str(ROOT_DIR / "00-bootstrap/doctor/pin_lib.py"), "--self-test"],
                           capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])

    def test_real_home_refuses_injected_agent_with_real_profile_resolve(self):
        import functools
        pin_lib = load("00-bootstrap/doctor/pin_lib.py")
        pr = load("profile_resolve")
        calls = []
        saved = pin_lib._fs

        def spy(op, path, *args):
            calls.append((op, str(path)))
            raise AssertionError(f"write primitive reached: {op} {path}")
        pin_lib._fs = spy
        try:
            real = pin_lib.passwd_home()
            agent = functools.partial(pr.agent_check, env={"CLAUDECODE": "1"}, ancestry=[],
                                      isatty={"stdin": True, "stdout": True})
            with self.assertRaises(pin_lib.RefusedError):
                pin_lib.pin(repo=ROOT_DIR, home=real, confirm_real_home=True, agent_check=agent)
            with self.assertRaises(pin_lib.RefusedError):
                pin_lib.pin(repo=ROOT_DIR, home=real)
        finally:
            pin_lib._fs = saved
        self.assertEqual(calls, [])

    def test_pinned_paths_single_home(self):
        pin_lib = load("00-bootstrap/doctor/pin_lib.py")
        # wave 1 added 09-tools/git_lanes.py (H18), wall_guard.py (H15), and W1-6 (H20, walls F-11) the
        # heal sources, the pinned doctor entry and the doctor with every helper it executes.
        self.assertEqual(len(pin_lib.PINNED_PATHS), 20)
        self.assertEqual(len(set(pin_lib.PINNED_PATHS)), 20)
        self.assertIn("09-tools/profile_resolve.py", pin_lib.PINNED_PATHS)
        self.assertIn("09-tools/git_lanes.py", pin_lib.PINNED_PATHS)
        self.assertIn("09-tools/wall_guard.py", pin_lib.PINNED_PATHS)
        for rel in ("00-bootstrap/dist/workspace-sessionstart.sh", "00-bootstrap/dist/workspace-reassert.sh",
                    "00-bootstrap/dist/workspace-audit.sh", "00-bootstrap/dist/user-CLAUDE.md",
                    "00-bootstrap/dist/ws-doctor", "00-bootstrap/doctor/workspace-doctor.sh",
                    "00-bootstrap/doctor/pin_lib.py", "00-bootstrap/doctor/merge_settings.py",
                    "00-bootstrap/doctor/render_shims.py"):
            self.assertIn(rel, pin_lib.PINNED_PATHS)
            self.assertTrue((ROOT_DIR / rel).is_file(), rel)
        self.assertIn("ws-doctor", pin_lib.WRAPPERS)
        # Every file the doctor executes is pinned: each python3 helper path in the doctor sits under
        # $CDOC/$CODE (the doctor's own tree) or the pinned lib, and resolves to a pinned path.
        doc = (ROOT_DIR / "00-bootstrap/doctor/workspace-doctor.sh").read_text(encoding="utf-8")
        import re as _re
        for var, rel in _re.findall(r'python3 "\$(\w+)/([\w./-]+\.py)"', doc):
            if var == "DOC":
                self.assertEqual(rel, "installers.py")   # human-run only (TTY + human verdict)
                continue
            self.assertIn(var, ("CDOC", "CODE", "LIBC"), f"{var}/{rel}")
            full = ("00-bootstrap/doctor/" + rel) if var == "CDOC" else rel
            self.assertIn(full, pin_lib.PINNED_PATHS, full)


class TestInstaller(unittest.TestCase):
    """H24 installers: the fixture suite (refusal matrix, allow path, byte-exact uninstall,
    doctor modes with a hash spy and PATH stubs), plus the agent markers pinned in MARKERS (one
    env marker each for Cursor, Codex, Gemini and Claude, the CI marker, the family override and
    a Claude process in the ancestry) through the REAL profile_resolve.agent_check: every
    installer, both actions, must refuse. It does not run every marker surfaces.json declares."""

    MARKERS = [
        ({"CURSOR_AGENT": "1"}, []),
        ({"CODEX_THREAD_ID": "x"}, []),
        ({"GEMINI_CLI": "1"}, []),
        ({"WS_SURFACE_FAMILY": "claude"}, []),
        ({"CLAUDECODE": "1"}, []),
        ({"CI": "1"}, []),
        ({}, [{"pid": 4202, "ppid": 4201, "comm": "claude", "args": "claude"}]),
        ({}, [{"pid": 4202, "ppid": 4201, "comm": "Claude Helper", "args": "Claude Helper (Renderer)"}]),
    ]

    def test_self_test(self):
        import subprocess
        r = subprocess.run([sys.executable, str(ROOT_DIR / "00-bootstrap/doctor/installers.py"), "--self-test"],
                           capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])

    def test_every_marker_refuses_every_installer(self):
        import contextlib
        import functools
        import io
        if not (ROOT_DIR / "02-shared-references" / "surfaces.json").is_file():
            # The non-Claude env markers are declared in surfaces.json (T1); without it the
            # resolver only knows the built-in Claude and CI markers.
            self.skipTest("surfaces.json not present: non-Claude markers undeclared")
        inst = load("00-bootstrap/doctor/installers.py")
        pr = load("profile_resolve")
        tty = {"stdin": True, "stdout": True}
        with tempfile.TemporaryDirectory() as td:
            home = Path(td) / "home"
            home.mkdir()
            base_env = {"PATH": "/usr/bin:/bin", "HOME": str(home), "TERM": "xterm-256color"}
            for env, ancestry in self.MARKERS:
                check = functools.partial(pr.agent_check, env={**base_env, **env},
                                          ancestry=ancestry, isatty=tty)
                for name in inst.NAMES:
                    for action in inst.ACTIONS:
                        err = io.StringIO()
                        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                            rc = inst.run(name, action, home=home, repo=ROOT_DIR, agent_check=check,
                                          isatty=tty, confirm=lambda _p: "y",
                                          which=lambda _n: None, app_exists=lambda _p: False)
                        self.assertEqual(rc, 4, f"{name} {action} under {env or ancestry}")
                        self.assertIn("installer refused:", err.getvalue())
            self.assertEqual(list(home.iterdir()), [])


class TestSurfaces(unittest.TestCase):
    """G1: Rule C on the live surfaces.json (strict) plus planted coverage defects."""

    @classmethod
    def setUpClass(cls):
        cls.rs = load("00-bootstrap/doctor/render_shims.py")
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            cls.results = {name: (ok, detail) for name, ok, detail in cls.rs.self_test_cases()}

    def test_live_coverage_is_strictly_clean(self):
        res = self.rs.check(ROOT_DIR, only=["coverage"], pending_ok=False)
        self.assertEqual(res["errors"], [])
        self.assertEqual(res["warnings"], [])

    def test_minimum_surfaces_cover_every_component(self):
        t = self.rs.load_table(ROOT_DIR)
        rows = {s["id"]: s for s in t["surfaces"]}
        self.assertEqual(len(t["surfaces"]), 22)
        for m in t["minimum_surfaces"]:
            for c in t["components"]:
                with self.subTest(surface=m, component=c):
                    self.assertIn(c, rows[m]["coverage"])
        for s in t["surfaces"]:
            self.assertIn(s["family"], t["families"])

    def test_planted_coverage_defects_fail(self):
        for name in ("missing codex row", "row family not in families", "enforced with no verified_by",
                     "unresolvable verified_by in strict mode",
                     "unresolvable fixture ref is a warning under --pending-ok",
                     "unresolvable probe ref stays an error under --pending-ok", "invalid coverage mode",
                     "unknown top-level key",
                     "planned refs that all resolve give a notice and no warning",
                     "an unpromoted entry keeps strict mode clean (no errors, no warnings)",
                     "--check exits 0 and prints the notice outside warnings",
                     "--check --json exits 0 and prints the notice outside warnings",
                     "a verified_by ref on a non-enforced entry must resolve"):
            with self.subTest(case=name):
                ok, detail = self.results.get(name, (False, "case missing"))
                self.assertTrue(ok, detail)


class TestRenderShims(unittest.TestCase):
    """G2: rendered outputs match, one effective registration per surface/event/behaviour, wrappers pinned."""

    @classmethod
    def setUpClass(cls):
        cls.rs = load("00-bootstrap/doctor/render_shims.py")
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            cls.results = {name: (ok, detail) for name, ok, detail in cls.rs.self_test_cases()}

    def test_live_outputs_registrations_wrappers_clean(self):
        res = self.rs.check(ROOT_DIR, only=["outputs", "registrations", "wrappers"], pending_ok=False)
        self.assertEqual(res["errors"], [])
        self.assertEqual(res["warnings"], [])

    def test_rule_r_one_effective_registration(self):
        self.assertEqual(self.rs.effective_violations(self.rs.load_table(ROOT_DIR)), {})

    def test_project_registrations_reach_dispatcher_handlers(self):
        import ast
        tree = ast.parse((ROOT_DIR / ".claude" / "hooks" / "dispatcher.py").read_text(encoding="utf-8"))
        handlers = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "HANDLERS" for t in node.targets):
                handlers = {k.value for k in node.value.keys}
        self.assertTrue(handlers)
        settings = json.loads((ROOT_DIR / ".claude" / "settings.json").read_text(encoding="utf-8"))
        commands = [h["command"] for groups in settings["hooks"].values() for g in groups for h in g["hooks"]]
        self.assertTrue(commands)
        for cmd in commands:
            with self.subTest(command=cmd[-40:]):
                self.assertIn(cmd.rsplit(" ", 1)[-1], handlers)
                self.assertNotIn("$HOME", cmd)

    def test_planted_registration_and_output_defects_fail(self):
        for name in ("base fixture is clean", "write is idempotent",
                     "duplicate Cursor sessionEnd (project plus user)",
                     "plugin SessionStart duplicates the user hook without a claim_group",
                     "project-scope shim references $HOME", "host_skip on a command without host_filter",
                     "pending registration fails in strict mode", "wrapper sha mismatch",
                     "hand-edited output is drift", "--rev without render_shims.py exits 3",
                     "--verify-canonical passes a pure reformat and fails a value change",
                     "beacon renders from beacons.json and checks clean", "hand-edited beacon is drift",
                     "beacon over max_bytes fails", "beacon family not in surfaces.json fails",
                     "contract-core over the rule limit fails", "contract-core with a missing section fails",
                     "contract-core keeps the bullet verbatim, drops the rest, re-roots links"):
            with self.subTest(case=name):
                ok, detail = self.results.get(name, (False, "case missing"))
                self.assertTrue(ok, detail)


class TestEntryPoints(unittest.TestCase):
    """H6: entry points and per-surface floors (mirrors workspace-harness --self-test)."""

    @classmethod
    def setUpClass(cls):
        cls.wh = load("09-tools/workspace-harness.py")

    def test_live_entry_points_and_floors_clean(self):
        self.assertEqual(self.wh.check_entry_points(ROOT_DIR)["failures"], [])
        over = self.wh.run_tokens()["over_budget"]
        self.assertEqual([o for o in over if o.split(":")[0] in ("cursor_floor", "claude_floor", "web_pack")], [])

    def test_planted_entry_point_defects_fail(self):
        import tempfile
        for name, needle, plant in self.wh._entry_point_fixtures():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                files = self.wh._plant_entry_points(root)
                self.assertEqual(self.wh.check_entry_points(root, list(files))["failures"], [])
                plant(root, files)
                got = self.wh.check_entry_points(root, files)["failures"]
                self.assertTrue(any(needle in f for f in got), got)

    def test_codex_window_fail_and_baseline_relative_warn(self):
        cw = self.wh.codex_window
        fails, warns = cw({"AGENTS.md": 28_300, "00-bootstrap/dist/codex-AGENTS.md": 1_515}, baseline=28_000)
        self.assertTrue(fails)
        fails, warns = cw({"AGENTS.md": 28_500, "00-bootstrap/dist/codex-AGENTS.md": 1_515}, baseline=28_600)
        self.assertEqual((fails, bool(warns)), ([], True))
        self.assertTrue(cw({"AGENTS.md": 32_000, "00-bootstrap/dist/BEACON.md": 1_000}, baseline=40_000)[0])


class TestWsHook(unittest.TestCase):
    """G3a: payload goldens, dialects, dedupe, budget, fail-open, redaction, host filter, floor adapter, N1."""

    def test_ws_hook_cases(self):
        ws = load("ws_hook")
        cases = ws.self_test_cases()
        self.assertGreater(len(cases), 50)
        for name, ok, detail in cases:
            with self.subTest(case=name):
                self.assertTrue(ok, detail)


class TestLayer0Routing(unittest.TestCase):
    """H7: one matcher on every surface — stdin CLI, host payload adapters, is_user_turn (X2),
    longest-match suppression, brain resolution from any cwd, and the table-driven trajectory
    parity (including employer-shaped cwds on cursor and codex)."""

    def test_prompt_route_cases(self):
        pr = load("prompt_route")
        cases = pr.self_test_cases()
        self.assertGreater(len(cases), 30)
        for name, ok, detail in cases:
            with self.subTest(case=name):
                self.assertTrue(ok, detail)

    def test_trajectories(self):
        tool = TOOLS / "evaluate-surface-trajectories.py"
        for args in (["--self-test"], ["--check"]):
            with self.subTest(args=args):
                r = subprocess.run([sys.executable, str(tool), *args], capture_output=True, text=True,
                                   cwd=str(ROOT_DIR), timeout=600)
                self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-1000:])

    def test_trajectory_corpus_covers_h7(self):
        rows = [json.loads(ln) for ln in (ROOT_DIR / "02-shared-references" / "surface-trajectory-cases.jsonl")
                .read_text(encoding="utf-8").splitlines() if ln.strip()]
        employer = {s for r in rows if r.get("cwd") == "employer-shaped" for s in r.get("surfaces", [])}
        self.assertTrue({"cursor", "codex"} <= employer, employer)
        x2 = [r for r in rows if r.get("expect_empty") and r["utterance"].lstrip().startswith("<task-notification>")]
        self.assertTrue(x2 and "claude-code" in x2[0]["surfaces"], x2)
        self.assertTrue(any(r.get("forbid_paths") and "zero vector" in r["utterance"] for r in rows))
        self.assertTrue(any({"claude-chat", "aider"} <= set(r.get("surfaces", [])) for r in rows))


class TestHostFilter(unittest.TestCase):
    """G2b: boot output byte-identical to 2ff02e7 with and without a pin, except the recorded L-08
    case: Codex inside the workspace with a verified pin gets the card 2ff02e7 gives it outside the
    workspace, because Codex does not load the claude-project layer. Claude Code and Copilot in
    VS Code inside the workspace with a verified pin stay byte-identical (the deferral set is the
    layer's loaded_by in surfaces.json). Cursor silenced only when the pinned wrapper reports
    verified evidence (exit 3)."""

    def test_host_filter_goldens(self):
        ws = load("ws_hook")
        cases = ws.shell_golden_cases()
        self.assertGreater(len(cases), 40)
        for name, ok, detail in cases:
            with self.subTest(case=name):
                self.assertTrue(ok, detail)


class TestWallGuard(unittest.TestCase):
    """H15 exit gate: one corpus (09-tools/fixtures/wall_guard) through every host golden (Claude Code
    incl. the terminal, browser, filesystem-MCP and tracker payloads; Cursor beforeShellExecution,
    preToolUse and beforeMCPExecution; Codex with and without workdir and apply_patch; VS Code, Gemini,
    Copilot CLI, Windsurf, Cline), the Claude git floor, H18's git-lane entrypoint when present, and the
    generated belts; plus the item-9 matrix, R6 variants, nested chains, no env bypass, the HOME-empty
    cloud shim, byte-identical employer repos, timeout and malformed-payload fail-open, and the rendered
    shims and permission rules. A SKIP (the Codex app binary or H18's lanes absent) is not a pass."""

    @classmethod
    def setUpClass(cls):
        cls.wg = load("wall_guard")
        cls.rs = load("00-bootstrap/doctor/render_shims.py")
        cls.cases = load("09-tools/fixtures/wall_guard/cases.py")
        cls.results = cls.cases.all_cases(cls.wg, cls.rs)

    def _run(self, group: str, minimum: int = 1):
        rows = self.results[group]
        self.assertGreaterEqual(len(rows), minimum, group)
        for name, ok, detail in rows:
            if ok is None:
                continue
            with self.subTest(case=name):
                self.assertTrue(ok, detail)
        skipped = [r for r in rows if r[1] is None]
        if skipped:
            self.skipTest(f"{len(skipped)} case(s) SKIPPED: {skipped[0][2]}")

    def test_corpus_goldens(self):
        self._run("corpus", 60)

    def test_fail_open_log_and_rollout(self):
        self._run("misc", 8)

    def test_home_empty_cloud_shim(self):
        self._run("home_empty", 3)

    def test_belts_agree_with_core(self):
        self._run("belts", 4)

    def test_git_floor_agreement(self):
        self._run("floor", 5)

    def test_git_lane_agreement(self):
        self._run("lanes", 1)

    def test_rendered_shims_and_permissions(self):
        self._run("outputs", 7)


class TestEmployerSubstance(unittest.TestCase):
    """H25: employer-substance class of check-secrets (report-only in wave 0)."""

    def _quiet(self, fn, *a, **kw):
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return fn(*a, **kw)

    def test_self_test_fixtures(self):
        cs = load("check-secrets")
        self.assertEqual(self._quiet(cs.self_test), 0)

    def test_planted_flagged_allowlist_passes(self):
        cs = load("check-secrets")
        table = json.loads(
            (TOOLS / "fixtures" / "employer_substance" / "context-remotes.json").read_text(encoding="utf-8")
        )
        rules = cs.EmpRules(table)
        text = (
            "see https://github.com/acme-corp/zz-app/pull/1\n"
            "file acme-corp/zz-app/src/a.ts\n"
            "repo acme-corp/zz-lib\n"
            "owner-level acme-corp, acme-bb and acme-corp/* pass\n"
            "personal pat-sample/zz-tool/src/a.py passes\n"
        )
        self.assertEqual(rules.scan_text(text), [(1, "emp-url"), (2, "emp-path"), (3, "emp-slug")])

    def test_output_never_prints_matched_text(self):
        cs = load("check-secrets")
        import contextlib
        import io
        import shutil
        fx = TOOLS / "fixtures" / "employer_substance"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "vault"
            (root / "notes").mkdir(parents=True)
            (root / cs.REMOTES_REL).parent.mkdir(parents=True)
            shutil.copy(fx / "context-remotes.json", root / cs.REMOTES_REL)
            shutil.copy(fx / "planted.md", root / "notes" / "planted.md")
            fake = cs._FakeResolver(Path(td) / "home")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                rc = cs.main(["--class", "employer-substance", "--report", "--root", str(root)],
                             resolver=fake, home=Path(td) / "home")
            self.assertEqual(rc, 0)
            self.assertIn("notes/planted.md:3 emp-url", out.getvalue())
            self.assertNotIn("zz-planted", out.getvalue())

    def test_live_baseline_not_exceeded(self):
        # G7a: the committed baseline holds on the live tree (real tables, temp HOME for the cache).
        cs = load("check-secrets")
        if cs._resolver() is None:
            self.skipTest("profile_resolve not importable (pre-T2 tree)")
        with tempfile.TemporaryDirectory() as td:
            rc = self._quiet(cs.main, ["--class", "employer-substance", "--baseline-check"], home=Path(td))
        self.assertEqual(rc, 0)


class TestNightly(unittest.TestCase):
    """H1 sequencer: written-path diffing, phase order, lane matching, scope parsing."""

    def setUp(self):
        self.n = load("nightly")

    def test_written_between_reports_changed_created_and_deleted(self):
        before = {"a": "1", "b": "2", "gone": "3"}
        after = {"a": "1", "b": "9", "new": "4"}
        self.assertEqual(self.n.written_between(before, after), ["b", "gone", "new"])

    def test_phase_order_is_canonical_and_commit_flag_adds_commit(self):
        self.assertEqual(self.n._ordered_phases("verify,rebuild", False), ["rebuild", "verify"])
        self.assertEqual(self.n._ordered_phases("rebuild", True), ["rebuild", "commit"])
        with self.assertRaises(ValueError):
            self.n._ordered_phases("rebuild,bogus", False)

    def test_fixpoint_order_is_declared(self):
        tools = [s["tool"] for s in self.n.PHASES if s["phase"] == "rebuild"]
        self.assertEqual(tools, ["build-registry.py", "build-related.py", "build-registry.py",
                                 "build-trigger-routes.py"])
        self.assertTrue(self.n.PHASES[3]["fixpoint"])

    def test_lane_matches_only_skill_sources(self):
        m = self.n._lane_matches
        self.assertTrue(m("03-skills/x/SKILL.md"))
        self.assertTrue(m("02-shared-references/trigger-routes.json"))
        self.assertTrue(m("02-shared-references/knowledge-hints.json"))
        self.assertFalse(m("03-skills/skills.registry.json"))
        self.assertFalse(m("06-context/session-log.md"))

    def test_scope_rejects_unknown_and_empty(self):
        for bad in ("bogus", "session:", "range:"):
            with self.assertRaises(ValueError):
                self.n.resolve_scope(bad)
        self.assertIsNone(self.n.resolve_scope("all"))

    def test_session_scope_reads_ledger_and_baseline(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "06-context" / "sessions").mkdir(parents=True)
            (root / "06-context" / "sessions" / "S1.touched").write_text("a.md\n", encoding="utf-8")
            (root / ".workspace" / "state" / "sessions").mkdir(parents=True)
            (root / ".workspace" / "state" / "sessions" / "S1.json").write_text(json.dumps(
                {"schema_version": 1, "porcelain": [{"xy": " M", "path": "old.md", "orig": None}]}),
                encoding="utf-8")
            original = self.n._dirty_now
            self.n._dirty_now = lambda r: {"old.md", "new.md"}
            try:
                scope = self.n.resolve_scope("session:S1", root)
            finally:
                self.n._dirty_now = original
            self.assertEqual(scope, {"a.md", "new.md"})


class TestDispatcherDefer(unittest.TestCase):
    """Verified non-Claude hosts get no dispatcher output; Claude Code payloads proceed.

    Runs the real dispatcher against a temp repo that carries copies of the real
    ws_hook.py, profile_resolve.py and their tables, fed T1's golden payloads."""

    PAYLOADS = TOOLS / "fixtures" / "ws_hook" / "payloads"
    TABLES = ("surfaces.json", "devices.json", "delivery-playbooks/context-remotes.json")

    def _env(self, home):
        drop = ("GIT_", "CLAUDE", "CURSOR", "CODEX", "WS_", "GH_", "VSCODE", "TERM_PROGRAM",
                "GEMINI", "COPILOT", "AI_AGENT")
        env = {k: v for k, v in os.environ.items() if not k.startswith(drop)}
        env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1")
        return env

    def _repo(self, td):
        repo = Path(td) / "ws"
        (repo / "09-tools").mkdir(parents=True)
        for mod in ("ws_hook.py", "profile_resolve.py"):
            src = TOOLS / mod
            if not src.is_file():
                self.skipTest(f"{mod} not integrated yet")
            (repo / "09-tools" / mod).write_bytes(src.read_bytes())
        for rel in self.TABLES:
            src = ROOT_DIR / "02-shared-references" / rel
            if src.is_file():
                dst = repo / "02-shared-references" / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
        (repo / ".gitignore").write_text(".workspace/\n.claude/state/\n", encoding="utf-8")
        return repo

    def _run(self, repo, home, event, payload):
        env = self._env(home)
        env["CLAUDE_PROJECT_DIR"] = str(repo)
        return subprocess.run(
            [sys.executable, str(ROOT_DIR / ".claude" / "hooks" / "dispatcher.py"), event],
            input=json.dumps(payload), capture_output=True, text=True, env=env, cwd=str(repo),
            timeout=60)

    def test_foreign_host_payloads_exit_silently(self):
        files = sorted(self.PAYLOADS.glob("cursor.*.json")) + sorted(
            self.PAYLOADS.glob("copilot-vscode.*.json"))
        if not files:
            self.skipTest("T1 golden payloads not present")
        with tempfile.TemporaryDirectory() as td:
            repo, home = self._repo(td), Path(td) / "home"
            home.mkdir()
            subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True,
                           env=self._env(home), capture_output=True)
            for f in files:
                event = f.name.split(".")[1]
                if event not in ("session-start", "user-prompt", "pre-tool", "post-tool",
                                 "stop", "session-end"):
                    continue
                pl = json.loads(f.read_text(encoding="utf-8"))
                if event == "pre-tool":
                    pl = dict(pl, tool_name="mcp__figma__use_figma")
                r = self._run(repo, home, event, pl)
                self.assertEqual(r.returncode, 0, f.name)
                self.assertEqual(r.stdout, "", f"{f.name} produced output")

    def test_claude_code_payload_proceeds(self):
        f = self.PAYLOADS / "claude-code.pre-tool.json"
        if not f.is_file():
            # T1's goldens cover session-start and user-prompt only; T5 ships a pre-tool copy.
            f = TOOLS / "fixtures" / "nightly" / "payloads" / "claude-code.pre-tool.json"
        if not f.is_file():
            self.skipTest("no claude-code pre-tool payload present")
        with tempfile.TemporaryDirectory() as td:
            repo, home = self._repo(td), Path(td) / "home"
            home.mkdir()
            subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True,
                           env=self._env(home), capture_output=True)
            pl = dict(json.loads(f.read_text(encoding="utf-8")), tool_name="mcp__figma__use_figma",
                      session_id="t5-claude-proceeds")
            r = self._run(repo, home, "pre-tool", pl)
            self.assertEqual(r.returncode, 0)
            self.assertIn("permissionDecision", r.stdout)

    def test_unknown_event_exits_zero(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            r = self._run(Path(td), home, "no-such-event", {})
            self.assertEqual(r.returncode, 0)
            self.assertIn("unknown event", r.stderr)


class TestScopedCommitH1(unittest.TestCase):
    """H1 extensions of TestScopedCommit: written paths ride along, excluded paths never
    stage, sibling worktrees are never cleanup candidates, and intent/* branches never
    auto-commit. Reuses TestScopedCommit's loader (CLAUDE_PROJECT_DIR guard satisfied)."""

    _dispatcher = TestScopedCommit._dispatcher

    class _Git:
        def __init__(self, branch="main"):
            self.calls = []
            self.branch = branch

        def __call__(self, *args, **kwargs):
            self.calls.append(args)
            out = ""
            if args[:2] == ("symbolic-ref", "--short"):
                out = self.branch + "\n"
            return subprocess.CompletedProcess(["git", *args], 0, stdout=out, stderr="")

    def test_stage_adds_written_and_never_excluded(self):
        d = self._dispatcher()
        with tempfile.TemporaryDirectory() as td:
            sessions = Path(td)
            orig = (d.SESSIONS_DIR, d.git)
            d.SESSIONS_DIR, d.git = sessions, self._Git()
            try:
                (sessions / "s1.touched").write_text("03-skills/x/SKILL.md\n", encoding="utf-8")
                mode = d._stage_session_scope(
                    {"session_id": "s1"},
                    extra=["03-skills/y/SKILL.md", "03-skills/skills.registry.json"],
                    exclude={"03-skills/z/SKILL.md", "03-skills/skills.registry.json"})
                self.assertEqual(mode, "scoped")
                added = [c[-1] for c in d.git.calls if c[:3] == ("add", "-A", "--")]
                self.assertIn("03-skills/x/SKILL.md", added)
                self.assertIn("03-skills/y/SKILL.md", added)
                self.assertNotIn("03-skills/skills.registry.json", added)
                resets = [c for c in d.git.calls if c[:1] == ("reset",)]
                self.assertTrue(resets and "03-skills/z/SKILL.md" in resets[-1])
            finally:
                d.SESSIONS_DIR, d.git = orig

    def test_cleanup_never_touches_sibling_intent_worktrees(self):
        d = self._dispatcher()
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td) / "ws"
            (ws / ".claude" / "worktrees" / "n").mkdir(parents=True)
            (Path(td) / "ws.intent-x").mkdir()
            orig = (d.WORKSPACE_ROOT, d.git, d.in_git_repo, d._list_worktrees,
                    d._branch_fully_merged_into_main)
            d.WORKSPACE_ROOT, d.git, d.in_git_repo = ws, self._Git(), (lambda: True)
            d._list_worktrees = lambda: [
                {"path": str(ws), "branch": "refs/heads/main"},
                {"path": str(Path(td) / "ws.intent-x"), "branch": "refs/heads/intent/x"},
                {"path": str(ws / ".claude" / "worktrees" / "n"), "branch": "refs/heads/n"}]
            d._branch_fully_merged_into_main = lambda b: True
            try:
                cleaned, _ = d._cleanup_stale_worktrees()
            finally:
                (d.WORKSPACE_ROOT, d.git, d.in_git_repo, d._list_worktrees,
                 d._branch_fully_merged_into_main) = orig
            self.assertEqual(cleaned, ["n"])

    def test_session_end_on_intent_branch_never_commits(self):
        d = self._dispatcher()
        orig = (d.git, d.in_git_repo)
        d.git, d.in_git_repo = self._Git(branch="intent/x"), (lambda: True)
        try:
            d.handle_session_end({"session_id": "s1"})
            self.assertFalse(any(c[:1] in (("commit",), ("push",), ("add",)) for c in d.git.calls))
        finally:
            d.git, d.in_git_repo = orig


def main(argv: list) -> int:
    strict = "--strict-skips" in argv
    names = [a for a in argv if a != "--strict-skips"]
    module = sys.modules[__name__]
    loader = unittest.defaultTestLoader
    if names:
        unknown = [n for n in names if not isinstance(getattr(module, n, None), type)
                   or not issubclass(getattr(module, n), unittest.TestCase)]
        if unknown:
            print(f"test-validators: unknown test class(es): {', '.join(unknown)}", file=sys.stderr)
            return 2
        suite = unittest.TestSuite(loader.loadTestsFromTestCase(getattr(module, n)) for n in names)
    else:
        suite = loader.loadTestsFromModule(module)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    if strict and result.skipped:
        print(f"test-validators: {len(result.skipped)} skip(s) under --strict-skips", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
