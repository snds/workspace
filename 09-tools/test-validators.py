#!/usr/bin/env python3
"""Negative fixtures: each detector must FAIL a planted defect.

The live-tree validators only see a healthy checkout. A broken detector looks
green forever. This harness plants small broken trees and asserts errors.
Pattern: vault-retrieve.py --eval.

Usage:
  python3 09-tools/test-validators.py
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent


def load(name: str):
    path = TOOLS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
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


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestValidatorFixtures)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
