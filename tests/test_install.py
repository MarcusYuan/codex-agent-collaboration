"""Focused safety tests for the Codex Desktop installer."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "install.py"
spec = importlib.util.spec_from_file_location("install", SCRIPT)
assert spec and spec.loader
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.repo = root / "repo"
        self.home = root / "codex"
        (self.repo / "agents").mkdir(parents=True)
        (self.repo / "config").mkdir()
        (self.repo / "AGENTS.md").write_text("English rules\n", encoding="utf-8")
        (self.repo / "AGENTS.zh-CN.md").write_text("中文规则\n", encoding="utf-8")
        (self.repo / "config" / "codex.toml").write_bytes(
            (SCRIPT.parents[1] / "config" / "codex.toml").read_bytes())
        for role in installer.ROLES:
            (self.repo / "agents" / f"{role}.toml").write_text(
                f'name = "{role}"\n'
                'description = "Fixture role"\n'
                f'model = "{installer.ROLE_MODELS[role]}"\n'
                'model_reasoning_effort = "high"\n'
                'developer_instructions = "Do the fixture task."\n', encoding="utf-8")

    def run_install(self, **options):
        return installer.install(self.repo, self.home, **options)

    def test_new_install_and_language(self):
        changes = self.run_install(language="zh-CN")
        self.assertEqual(len(changes), 8)
        self.assertIn("中文规则", (self.home / "AGENTS.md").read_text())
        self.assertEqual(tomllib.loads((self.home / "config.toml").read_text())["agents"]
                         ["max_concurrent_threads_per_session"], 8)
        self.assertTrue((self.home / "agents" / "luna_reader.toml").read_text()
                        .startswith(installer.ROLE_MARKER))
        backups = list((self.home / "backups" / "codex-agent-collaboration").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertTrue((backups[0] / "manifest.json").exists())

    def test_config_preserves_unrelated_text_comments_and_values(self):
        self.home.mkdir()
        original = '# Personal note\napproval_policy = "on-request"\n\n[tools]\nweb = true\n'
        (self.home / "config.toml").write_text(original)
        self.run_install()
        result = (self.home / "config.toml").read_text()
        self.assertIn("# Personal note", result)
        self.assertIn('approval_policy = "on-request"', result)
        self.assertIn("[tools]\nweb = true\n", result)
        parsed = tomllib.loads(result)
        self.assertEqual(parsed["tools"], {"web": True})
        self.assertEqual(result.count("[agents]"), 1)

    def test_unmanaged_instructions_and_roles_are_protected(self):
        self.home.mkdir()
        (self.home / "AGENTS.md").write_text("Personal rules\n")
        with self.assertRaisesRegex(installer.InstallError, "replace-instructions"):
            self.run_install()
        self.assertFalse((self.home / "config.toml").exists())
        changes = self.run_install(replace_instructions=True)
        self.assertIn(self.home / "AGENTS.md", changes)
        (self.home / "agents" / "luna_reader.toml").write_text('name = "other"\n')
        before = (self.home / "AGENTS.md").read_bytes()
        with self.assertRaisesRegex(installer.InstallError, "replace-roles"):
            self.run_install()
        self.assertEqual((self.home / "AGENTS.md").read_bytes(), before)
        self.run_install(replace_roles=True)
        self.assertIn('name = "luna_reader"',
                      (self.home / "agents" / "luna_reader.toml").read_text())

    def test_managed_block_preserves_text_outside_it(self):
        self.home.mkdir()
        content = ("Before\n\n" + installer.START + "\nOld\n" + installer.END
                   + "\n\nAfter\n")
        (self.home / "AGENTS.md").write_text(content)
        self.run_install()
        result = (self.home / "AGENTS.md").read_text()
        self.assertTrue(result.startswith("Before\n\n"))
        self.assertTrue(result.endswith("\n\nAfter\n"))
        self.assertNotIn("Old", result)

    def test_dry_run_is_zero_write(self):
        changes = self.run_install(dry_run=True)
        self.assertEqual(len(changes), 8)
        self.assertFalse(self.home.exists())

    def test_repeated_install_is_idempotent(self):
        self.run_install()
        first_config = (self.home / "config.toml").read_bytes()
        backups = self.home / "backups" / "codex-agent-collaboration"
        first_count = len(list(backups.iterdir()))
        self.assertEqual(self.run_install(), [])
        self.assertEqual((self.home / "config.toml").read_bytes(), first_config)
        self.assertEqual(len(list(backups.iterdir())), first_count)

    def test_equivalent_existing_config_remains_byte_identical(self):
        self.home.mkdir()
        snippet = (self.repo / "config" / "codex.toml").read_text()
        original = ("# Keep this exact formatting\n" + snippet.replace(
            'model = "gpt-6-sol"', 'model="gpt-6-sol"  # selected model'))
        (self.home / "config.toml").write_text(original)
        self.run_install()
        self.assertEqual((self.home / "config.toml").read_text(), original)

    def test_invalid_toml_preflight_changes_nothing(self):
        self.home.mkdir()
        (self.home / "config.toml").write_text("[broken\n")
        with self.assertRaisesRegex(installer.InstallError, "Invalid TOML"):
            self.run_install()
        self.assertFalse((self.home / "AGENTS.md").exists())
        self.assertFalse((self.home / "backups").exists())

    def test_invalid_role_preflight_changes_nothing(self):
        (self.repo / "agents" / "sol_worker.toml").write_text("[invalid\n")
        with self.assertRaisesRegex(installer.InstallError, "Invalid TOML"):
            self.run_install()
        self.assertFalse(self.home.exists())

    def test_missing_role_field_preflight_changes_nothing(self):
        role = self.repo / "agents" / "luna_reader.toml"
        role.write_text(role.read_text().replace('description = "Fixture role"\n', ''))
        with self.assertRaisesRegex(installer.InstallError, "nonempty string description"):
            self.run_install()
        self.assertFalse(self.home.exists())

    def test_wrong_role_model_preflight_changes_nothing(self):
        role = self.repo / "agents" / "luna_browser.toml"
        role.write_text(role.read_text().replace('gpt-6-luna', 'gpt-6-sol'))
        with self.assertRaisesRegex(installer.InstallError, "wrong model"):
            self.run_install()
        self.assertFalse(self.home.exists())

    def test_wrong_role_name_preflight_changes_nothing(self):
        role = self.repo / "agents" / "sol_worker.toml"
        role.write_text(role.read_text().replace('name = "sol_worker"', 'name = "other"'))
        with self.assertRaisesRegex(installer.InstallError, "wrong name"):
            self.run_install()
        self.assertFalse(self.home.exists())

    def test_bad_source_config_shape_preflight_changes_nothing(self):
        (self.repo / "config" / "codex.toml").write_text(
            'model = "gpt-6-sol"\nmodel_reasoning_effort = "medium"\nagents = "bad"\n')
        with self.assertRaisesRegex(installer.InstallError, "expected root and agents fields"):
            self.run_install()
        self.assertFalse(self.home.exists())

    def test_numeric_values_do_not_masquerade_as_managed_types(self):
        for index, override in enumerate(("enabled = 1", "max_concurrent_threads_per_session = 8.0")):
            with self.subTest(override=override):
                self.home = Path(self.temp.name) / f"codex-numeric-{index}"
                self.home.mkdir()
                snippet = (self.repo / "config" / "codex.toml").read_text()
                old = ("enabled = true" if index == 0
                       else "max_concurrent_threads_per_session = 8")
                (self.home / "config.toml").write_text(snippet.replace(old, override))
                changes = self.run_install()
                self.assertIn(self.home / "config.toml", changes)
                parsed = tomllib.loads((self.home / "config.toml").read_text())
                self.assertIs(type(parsed["agents"]["enabled"]), bool)
                self.assertIs(type(parsed["agents"]["max_concurrent_threads_per_session"]), int)

    def test_non_table_agents_values_fail_preflight(self):
        for index, value in enumerate(("[]", "0", "false")):
            with self.subTest(value=value):
                self.home = Path(self.temp.name) / f"codex-agents-{index}"
                self.home.mkdir()
                original = f"agents = {value}\n".encode()
                (self.home / "config.toml").write_bytes(original)
                with self.assertRaisesRegex(installer.InstallError, "not a table"):
                    self.run_install()
                self.assertEqual((self.home / "config.toml").read_bytes(), original)
                self.assertFalse((self.home / "AGENTS.md").exists())
                self.assertFalse((self.home / "backups").exists())

    def test_symlink_target_is_rejected(self):
        self.home.mkdir()
        outside = Path(self.temp.name) / "outside"
        outside.write_text("keep")
        (self.home / "config.toml").symlink_to(outside)
        with self.assertRaisesRegex(installer.InstallError, "Symlink"):
            self.run_install()
        self.assertEqual(outside.read_text(), "keep")
        self.assertFalse((self.home / "AGENTS.md").exists())

    def test_write_failure_rolls_back_prior_targets(self):
        original_write = installer._atomic_write
        failed = False

        def fail_config(path, data, mode=0o600):
            nonlocal failed
            if path == self.home / "config.toml" and not failed:
                failed = True
                raise OSError("simulated write failure")
            return original_write(path, data, mode)

        with patch.object(installer, "_atomic_write", side_effect=fail_config):
            with self.assertRaisesRegex(installer.InstallError, "simulated write failure"):
                self.run_install()
        self.assertFalse((self.home / "AGENTS.md").exists())
        self.assertFalse((self.home / "config.toml").exists())
        backup_dir = next((self.home / "backups" / "codex-agent-collaboration").iterdir())
        self.assertTrue((backup_dir / "manifest.json").exists())

    def test_legacy_alias_is_rejected_before_write(self):
        self.home.mkdir()
        original = b"[agents]\nmax_threads = 8\n"
        (self.home / "config.toml").write_bytes(original)
        with self.assertRaisesRegex(installer.InstallError, "Legacy agents.max_threads"):
            self.run_install()
        self.assertEqual((self.home / "config.toml").read_bytes(), original)
        self.assertFalse((self.home / "AGENTS.md").exists())

    def test_override_blocks_install(self):
        self.home.mkdir()
        (self.home / "AGENTS.override.md").write_text("Priority rules\n")
        with self.assertRaisesRegex(installer.InstallError, "takes priority"):
            self.run_install()
        self.assertFalse((self.home / "backups").exists())


if __name__ == "__main__":
    unittest.main()
