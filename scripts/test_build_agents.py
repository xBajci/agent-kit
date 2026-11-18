import importlib.machinery
import importlib.util
import tempfile
import tomllib
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
loader = importlib.machinery.SourceFileLoader("build_agents", str(HERE / "build-agents"))
spec = importlib.util.spec_from_loader("build_agents", loader)
build_agents = importlib.util.module_from_spec(spec)
loader.exec_module(build_agents)

POINTER = build_agents.RUNTIME_POINTER
AGENT = f"""---
name: demo
description: Demo role.
model: sonnet
effort: high
tools: Read, Bash
---

{POINTER}

You are the demo.
"""


class BuildAgentsTest(unittest.TestCase):
    def setUp(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        self.tmp = Path(tmpdir.name)
        (self.tmp / "src/agents").mkdir(parents=True)
        (self.tmp / "src/runtime.md").write_text("# Runtime\n\nBe careful.\n")
        (self.tmp / "src/agents/demo.md").write_text(AGENT, encoding="utf-8")

    def test_claude_output_inlines_runtime_and_keeps_frontmatter(self):
        out = build_agents.build(self.tmp)
        text = out[Path("agents/demo.md")]
        self.assertTrue(text.startswith("---\nname: demo\n"))
        self.assertIn("model: sonnet", text)
        self.assertIn("Be careful.", text)
        self.assertNotIn(POINTER, text)

    def test_codex_output_is_valid_toml(self):
        out = build_agents.build(self.tmp)
        data = tomllib.loads(out[Path("codex/agents/demo.toml")])
        self.assertEqual(data["name"], "demo")
        self.assertEqual(data["model_reasoning_effort"], "high")
        self.assertIn("Be careful.", data["developer_instructions"])

    def test_missing_pointer_is_an_error(self):
        (self.tmp / "src/agents/demo.md").write_text(AGENT.replace(POINTER, ""))
        with self.assertRaises(ValueError):
            build_agents.build(self.tmp)

    def test_check_reports_stale_files(self):
        self.assertEqual(build_agents.write(self.tmp, check=True), ["agents/demo.md", "codex/agents/demo.toml"])
        build_agents.write(self.tmp, check=False)
        self.assertEqual(build_agents.write(self.tmp, check=True), [])

    def test_renamed_source_leaves_stale_outputs_that_check_reports_and_write_removes(self):
        build_agents.write(self.tmp, check=False)
        (self.tmp / "src/agents/demo.md").rename(self.tmp / "src/agents/other.md")
        text = (self.tmp / "src/agents/other.md").read_text().replace("name: demo", "name: other")
        (self.tmp / "src/agents/other.md").write_text(text)
        expected = ["agents/demo.md", "agents/other.md", "codex/agents/demo.toml", "codex/agents/other.toml"]
        self.assertEqual(build_agents.write(self.tmp, check=True), expected)
        self.assertTrue((self.tmp / "agents/demo.md").exists())
        self.assertEqual(build_agents.write(self.tmp, check=False), expected)
        self.assertFalse((self.tmp / "agents/demo.md").exists())
        self.assertFalse((self.tmp / "codex/agents/demo.toml").exists())
        self.assertEqual(build_agents.write(self.tmp, check=True), [])

    def test_files_without_marker_are_never_touched(self):
        (self.tmp / "agents").mkdir()
        (self.tmp / "agents/hand.md").write_text("hand written\n")
        self.assertNotIn("agents/hand.md", build_agents.write(self.tmp, check=False))
        self.assertTrue((self.tmp / "agents/hand.md").exists())

    def test_folded_description_collapses_whitespace_in_codex(self):
        src = AGENT.replace("description: Demo role.", "description: >\n  Demo\n  role   here.")
        (self.tmp / "src/agents/demo.md").write_text(src)
        data = tomllib.loads(build_agents.build(self.tmp)[Path("codex/agents/demo.toml")])
        self.assertEqual(data["description"], "Demo role here.")

    def test_body_with_triple_single_quotes_still_valid_toml(self):
        (self.tmp / "src/agents/demo.md").write_text(AGENT + "\nUse ''' quotes.\n")
        data = tomllib.loads(build_agents.build(self.tmp)[Path("codex/agents/demo.toml")])
        self.assertIn("''' quotes", data["developer_instructions"])

    def test_body_with_frontmatter_like_separator(self):
        (self.tmp / "src/agents/demo.md").write_text(AGENT + "\n---\nMore text.\n")
        out = build_agents.build(self.tmp)
        self.assertIn("\n---\nMore text.", out[Path("agents/demo.md")])
        data = tomllib.loads(out[Path("codex/agents/demo.toml")])
        self.assertIn("More text.", data["developer_instructions"])

    def test_unterminated_or_non_mapping_frontmatter_is_value_error(self):
        for bad in ("---\nname: demo\n", "---\n- a\n- b\n---\nbody\n"):
            (self.tmp / "src/agents/demo.md").write_text(bad)
            with self.assertRaises(ValueError):
                build_agents.build(self.tmp)


if __name__ == "__main__":
    unittest.main()
