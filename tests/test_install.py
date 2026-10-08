"""Focused safety tests for the Codex Desktop installer."""

from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
from contextlib import redirect_stderr, redirect_stdout
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
                f'model_reasoning_effort = "{installer.ROLE_EFFORTS[role]}"\n'
                'developer_instructions = "Do the fixture task."\n', encoding="utf-8")

    def run_install(self, **options):
        return installer.install(self.repo, self.home, **options)

    def run_main(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(installer, "REPO", self.repo), redirect_stdout(stdout), redirect_stderr(stderr):
            code = installer.main(["--codex-home", str(self.home), *args])
        return code, stdout.getvalue(), stderr.getvalue()

    def tree_state(self, root: Path):
        """Capture paths, bytes, permissions, and mtimes to prove check is read-only."""
        if not root.exists():
            return None
        entries = {}
        for path in [root, *sorted(root.rglob("*"))]:
            info = path.lstat()
            entries[path.relative_to(root.parent)] = (
                "dir" if path.is_dir() else "symlink" if path.is_symlink() else "file",
                path.read_bytes() if path.is_file() and not path.is_symlink() else None,
                info.st_mode, info.st_mtime_ns,
            )
        return entries

    def test_new_install_and_language(self):
        changes = self.run_install(language="zh-CN")
        self.assertEqual(len(changes), 4)
        self.assertIn("中文规则", (self.home / "AGENTS.md").read_text())
        self.assertEqual(tomllib.loads((self.home / "config.toml").read_text())["agents"],
                         {"enabled": True})
        self.assertTrue((self.home / "agents" / "luna_browser.toml").read_text()
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

    def test_upgrade_managed_sol_models_preserves_other_settings(self):
        self.run_install()
        config = self.home / "config.toml"
        config.write_text('# Personal setting\napproval_policy = "on-request"\n' +
                          config.read_text().replace('gpt-6.1-sol', 'gpt-6-sol'))
        other_roles = {self.home / "agents" / f"{role}.toml"
                       for role in installer.ROLES}
        unchanged = {path: path.read_bytes() for path in other_roles}
        previous = {config: config.read_bytes()}

        self.assertEqual(set(self.run_install()), set(previous))
        parsed = tomllib.loads(config.read_text())
        self.assertEqual(parsed["model"], "gpt-6.1-sol")
        self.assertEqual(parsed["model_reasoning_effort"], "medium")
        self.assertEqual(parsed["approval_policy"], "on-request")
        self.assertTrue(config.read_text().startswith("# Personal setting\n"))
        for path, content in unchanged.items():
            self.assertEqual(path.read_bytes(), content)
        backup = sorted((self.home / "backups" / "codex-agent-collaboration").iterdir())[-1]
        for path, content in previous.items():
            self.assertEqual((backup / path.relative_to(self.home)).read_bytes(), content)
        self.assertEqual(self.run_install(), [])

    def prepare_previous_role_layout(self):
        self.run_install()
        expert = self.home / "agents" / "astra_expert.toml"
        expert.unlink()
        browser = self.home / "agents" / "luna_browser.toml"
        browser.write_text(browser.read_text().replace("Fixture role", "Previous browser role"))
        retired = {}
        for name in installer.RETIRED_ROLES:
            path = self.home / "agents" / f"{name}.toml"
            path.write_text(installer.ROLE_MARKER + f'name = "{name}"\n')
            path.chmod(0o640)
            retired[path] = path.read_bytes()
        config = self.home / "config.toml"
        config.write_text(config.read_text() +
                          'max_concurrent_threads_per_session = 8\n'
                          'default_subagent_model = "gpt-6-luna"\n'
                          'default_subagent_reasoning_effort = "high"\n')
        return retired, browser, expert

    def test_role_transition_preview_check_backup_and_idempotence(self):
        retired, browser, expert = self.prepare_previous_role_layout()
        config = self.home / "config.toml"
        old_config = config.read_bytes()
        before = self.tree_state(self.home)
        code, stdout, stderr = self.run_main("--dry-run")
        self.assertEqual((code, stderr), (0, ""))
        for path in retired:
            self.assertIn(f"Would remove: {path}\n", stdout)
        self.assertEqual(before, self.tree_state(self.home))
        code, stdout, stderr = self.run_main("--check")
        self.assertEqual((code, stderr), (2, ""))
        self.assertEqual(set(stdout.splitlines()), {
            f"Drift: {path}" for path in (*retired, config, browser, expert)})
        self.assertEqual(before, self.tree_state(self.home))
        code, stdout, stderr = self.run_main()
        self.assertEqual((code, stderr), (0, ""))
        for path in retired:
            self.assertIn(f"Removed: {path}\n", stdout)
            self.assertFalse(path.exists())
        self.assertEqual(tomllib.loads(config.read_text())["agents"], {"enabled": True})
        self.assertEqual(tomllib.loads(expert.read_text())["model"], "gpt-6-astra")
        self.assertEqual(tomllib.loads(browser.read_text())["model"], "gpt-6-luna")
        backup = sorted((self.home / "backups" / "codex-agent-collaboration").iterdir())[-1]
        self.assertEqual((backup / "config.toml").read_bytes(), old_config)
        entries = json.loads((backup / "manifest.json").read_text())
        for path, content in retired.items():
            relative = path.relative_to(self.home)
            self.assertEqual((backup / relative).read_bytes(), content)
            entry = next(item for item in entries if item["target"] == str(relative))
            self.assertEqual((entry["action"], entry["mode"]), ("remove", 0o640))
        self.assertEqual(self.run_install(), [])
        self.assertEqual(self.run_main("--check"), (0, "Already up to date.\n", ""))

    def test_unmanaged_retired_role_blocks_all_changes(self):
        retired, _, _ = self.prepare_previous_role_layout()
        next(iter(retired)).write_text('name = "personal_role"\n')
        before = self.tree_state(self.home)
        for options in ({}, {"dry_run": True}, {"replace_roles": True}):
            with self.subTest(options=options), self.assertRaisesRegex(installer.InstallError, "Retired role is unmanaged"):
                self.run_install(**options)
            self.assertEqual(before, self.tree_state(self.home))

    def test_failure_after_retirement_restores_role_and_permissions(self):
        retired, browser, expert = self.prepare_previous_role_layout()
        config = self.home / "config.toml"
        previous = {path: path.read_bytes() for path in (*retired, config, browser)}
        original_write = installer._atomic_write

        def fail_browser(path, data, mode=0o600):
            if path == browser:
                self.assertTrue(all(not path.exists() for path in retired))
                self.assertTrue(expert.exists())
                raise OSError("simulated role write failure")
            return original_write(path, data, mode)

        with patch.object(installer, "_atomic_write", side_effect=fail_browser):
            with self.assertRaisesRegex(installer.InstallError, "simulated role write failure"):
                self.run_install()
        for path, content in previous.items():
            self.assertEqual(path.read_bytes(), content)
        for path in retired:
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)
        self.assertFalse(expert.exists())

    def test_wrong_specialist_effort_blocks_install(self):
        for name in installer.ROLES:
            path = self.repo / "agents" / f"{name}.toml"
            original = path.read_text()
            with self.subTest(name=name):
                path.write_text(original.replace(
                    f'model_reasoning_effort = "{installer.ROLE_EFFORTS[name]}"',
                    'model_reasoning_effort = "medium"'))
                with self.assertRaisesRegex(installer.InstallError, "model_reasoning_effort"):
                    self.run_install()
                self.assertFalse(self.home.exists())
            path.write_text(original)

    def test_retirement_failure_rolls_back_prior_instruction_update(self):
        retired, browser, expert = self.prepare_previous_role_layout()
        instructions = self.home / "AGENTS.md"
        instructions.write_text(instructions.read_text().replace("English rules", "Previous rules"))
        config = self.home / "config.toml"
        previous = {path: path.read_bytes() for path in (instructions, *retired, config, browser)}
        failed_path = list(retired)[-1]
        original_unlink = Path.unlink

        def fail_retirement(path, *args, **kwargs):
            if path == failed_path:
                raise OSError("simulated retirement failure")
            return original_unlink(path, *args, **kwargs)

        with patch.object(Path, "unlink", fail_retirement):
            with self.assertRaisesRegex(installer.InstallError, "simulated retirement failure"):
                self.run_install()
        for path, content in previous.items():
            self.assertEqual(path.read_bytes(), content)
        self.assertFalse(expert.exists())

    def test_unmanaged_instructions_and_roles_are_protected(self):
        self.home.mkdir()
        (self.home / "AGENTS.md").write_text("Personal rules\n")
        with self.assertRaisesRegex(installer.InstallError, "replace-instructions"):
            self.run_install()
        self.assertFalse((self.home / "config.toml").exists())
        changes = self.run_install(replace_instructions=True)
        self.assertIn(self.home / "AGENTS.md", changes)
        (self.home / "agents" / "luna_browser.toml").write_text('name = "other"\n')
        before = (self.home / "AGENTS.md").read_bytes()
        with self.assertRaisesRegex(installer.InstallError, "replace-roles"):
            self.run_install()
        self.assertEqual((self.home / "AGENTS.md").read_bytes(), before)
        self.run_install(replace_roles=True)
        self.assertIn('name = "luna_browser"',
                      (self.home / "agents" / "luna_browser.toml").read_text())

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
        self.assertEqual(len(changes), 4)
        self.assertFalse(self.home.exists())

    def test_check_missing_home_reports_drift_without_creating_anything(self):
        before = self.tree_state(self.home)
        code, stdout, stderr = self.run_main("--check")
        self.assertEqual(code, 2)
        self.assertEqual(stderr, "")
        self.assertEqual(len([line for line in stdout.splitlines() if line.startswith("Drift: ")]), 4)
        self.assertIsNone(self.tree_state(self.home))
        self.assertEqual(before, self.tree_state(self.home))

    def test_non_directory_home_or_agents_parent_is_an_error_without_writes(self):
        for layout in ("home-file", "agents-file"):
            with self.subTest(layout=layout):
                self.home = Path(self.temp.name) / f"codex-{layout}"
                if layout == "home-file":
                    self.home.write_bytes(b"existing home file")
                else:
                    self.home.mkdir()
                    (self.home / "agents").write_bytes(b"existing agents file")
                before = self.tree_state(self.home)
                for option in ("--check", "--dry-run"):
                    code, stdout, stderr = self.run_main(option)
                    self.assertEqual(code, 1)
                    self.assertEqual(stdout, "")
                    self.assertIn("Target parent is not a directory:", stderr)
                    self.assertEqual(before, self.tree_state(self.home))
                with self.assertRaisesRegex(installer.InstallError,
                                            "Target parent is not a directory"):
                    self.run_install()
                self.assertEqual(before, self.tree_state(self.home))

    def test_check_languages_match_only_selected_instruction_language(self):
        self.run_install(language="en")
        code, stdout, stderr = self.run_main("--check", "--language", "en")
        self.assertEqual((code, stdout, stderr), (0, "Already up to date.\n", ""))
        code, stdout, stderr = self.run_main("--check", "--language", "zh-CN")
        self.assertEqual(code, 2)
        self.assertEqual(stderr, "")
        self.assertEqual(stdout, f"Drift: {self.home / 'AGENTS.md'}\n")

    def test_check_reports_managed_drift_and_missing_targets_without_writes(self):
        self.run_install()
        agents = self.home / "AGENTS.md"
        config = self.home / "config.toml"
        role = self.home / "agents" / "luna_browser.toml"
        agents.write_text(agents.read_text().replace("English rules", "Changed rules"))
        config.write_text(config.read_text().replace('model = "gpt-6.1-sol"', 'model = "other"'))
        role.write_text(role.read_text().replace("Fixture role", "Changed role"))
        (self.home / "agents" / "astra_expert.toml").unlink()
        before = self.tree_state(self.home)
        code, stdout, stderr = self.run_main("--check")
        self.assertEqual(code, 2)
        self.assertEqual(stderr, "")
        self.assertEqual(set(stdout.splitlines()), {
            f"Drift: {agents}", f"Drift: {config}", f"Drift: {role}",
            f"Drift: {self.home / 'agents' / 'astra_expert.toml'}",
        })
        self.assertEqual(before, self.tree_state(self.home))

    def test_check_ignores_unmanaged_semantic_config_changes(self):
        self.run_install()
        config = self.home / "config.toml"
        original = config.read_text()
        config.write_text("# personal formatting\n" + original.replace(
            'model = "gpt-6.1-sol"', 'model="gpt-6.1-sol"  # same value'))
        code, stdout, stderr = self.run_main("--check")
        self.assertEqual((code, stdout, stderr), (0, "Already up to date.\n", ""))

    def test_check_can_compare_explicit_replace_strategy_without_writing(self):
        self.home.mkdir()
        agents = self.home / "AGENTS.md"
        agents.write_text("Local rules\n")
        role_dir = self.home / "agents"
        role_dir.mkdir()
        role = role_dir / "luna_browser.toml"
        role.write_text('name = "local"\n')
        before = self.tree_state(self.home)
        code, stdout, stderr = self.run_main("--check", "--replace-instructions", "--replace-roles")
        self.assertEqual(code, 2)
        self.assertIn(f"Drift: {agents}", stdout)
        self.assertIn(f"Drift: {role}", stdout)
        self.assertEqual(stderr, "")
        self.assertEqual(before, self.tree_state(self.home))
        self.assertFalse((self.home / "backups").exists())

    def test_cli_errors_and_help_exit_contract(self):
        code, stdout, stderr = self.run_main("--unknown")
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("error:", stderr)
        code, stdout, stderr = self.run_main("--check", "--dry-run")
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("cannot be used together", stderr)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--check", result.stdout)

    def test_check_oserror_is_reported_as_error(self):
        with patch.object(installer, "install", side_effect=OSError("permission denied")):
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = installer.main(["--check", "--codex-home", str(self.home)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("permission denied", stderr.getvalue())

    def test_dry_run_cli_regression_still_returns_zero_for_drift(self):
        code, stdout, stderr = self.run_main("--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(len([line for line in stdout.splitlines()
                              if line.startswith("Would update: ")]), 4)
        self.assertFalse(self.home.exists())

    def test_subprocess_check_returns_real_drift_exit_code(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--check", "--codex-home", str(self.home)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("Drift: ", result.stdout)
        self.assertEqual(result.stderr, "")
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
            'model = "gpt-6.1-sol"', 'model="gpt-6.1-sol"  # selected model'))
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
        (self.repo / "agents" / "astra_expert.toml").write_text("[invalid\n")
        with self.assertRaisesRegex(installer.InstallError, "Invalid TOML"):
            self.run_install()
        self.assertFalse(self.home.exists())

    def test_missing_role_field_preflight_changes_nothing(self):
        role = self.repo / "agents" / "luna_browser.toml"
        role.write_text(role.read_text().replace('description = "Fixture role"\n', ''))
        with self.assertRaisesRegex(installer.InstallError, "nonempty string description"):
            self.run_install()
        self.assertFalse(self.home.exists())

    def test_wrong_role_model_preflight_changes_nothing(self):
        role = self.repo / "agents" / "luna_browser.toml"
        role.write_text(role.read_text().replace('gpt-6-luna', 'gpt-6.1-sol'))
        with self.assertRaisesRegex(installer.InstallError, "wrong model"):
            self.run_install()
        self.assertFalse(self.home.exists())

    def test_wrong_role_name_preflight_changes_nothing(self):
        role = self.repo / "agents" / "astra_expert.toml"
        role.write_text(role.read_text().replace('name = "astra_expert"', 'name = "other"'))
        with self.assertRaisesRegex(installer.InstallError, "wrong name"):
            self.run_install()
        self.assertFalse(self.home.exists())

    def test_bad_source_config_shape_preflight_changes_nothing(self):
        (self.repo / "config" / "codex.toml").write_text(
            'model = "gpt-6.1-sol"\nmodel_reasoning_effort = "medium"\nagents = "bad"\n')
        with self.assertRaisesRegex(installer.InstallError, "expected root and agents fields"):
            self.run_install()
        self.assertFalse(self.home.exists())

    def test_numeric_values_do_not_masquerade_as_managed_types(self):
        for index, override in enumerate(("enabled = 1", "enabled = 1.0")):
            with self.subTest(override=override):
                self.home = Path(self.temp.name) / f"codex-numeric-{index}"
                self.home.mkdir()
                snippet = (self.repo / "config" / "codex.toml").read_text()
                (self.home / "config.toml").write_text(snippet.replace("enabled = true", override))
                changes = self.run_install()
                self.assertIn(self.home / "config.toml", changes)
                parsed = tomllib.loads((self.home / "config.toml").read_text())
                self.assertIs(type(parsed["agents"]["enabled"]), bool)

    def test_removed_agent_defaults_preserve_comments_and_nested_settings(self):
        self.home.mkdir()
        original = (
            '# Personal settings\nmodel = "gpt-6.1-sol"\n'
            'model_reasoning_effort = "medium"\n\n[agents] # Agent settings\n'
            '# Keep this standalone comment\nenabled = true\n'
            'max_concurrent_threads_per_session = 8 # old cap\n'
            'default_subagent_model = "gpt-6-luna"\n'
            'default_subagent_reasoning_effort = "high"\n'
            'custom_setting = "keep" # personal\n'
            '\n[agents.custom_role]\nconfig_file = "custom.toml"\n'
            '\n[profiles.personal.agents]\ndefault_subagent_model = "personal-model"\n'
        )
        config = self.home / "config.toml"
        config.write_text(original)
        unrelated = self.home / "agents" / "personal.toml"
        unrelated.parent.mkdir()
        unrelated.write_text('name = "personal"\n')
        self.run_install()
        result = config.read_text()
        parsed = tomllib.loads(result)
        self.assertEqual(parsed["agents"], {
            "enabled": True, "custom_setting": "keep",
            "custom_role": {"config_file": "custom.toml"},
        })
        self.assertEqual(parsed["profiles"]["personal"]["agents"],
                         {"default_subagent_model": "personal-model"})
        self.assertIn("[agents] # Agent settings\n# Keep this standalone comment", result)
        self.assertIn('custom_setting = "keep" # personal', result)
        self.assertEqual(unrelated.read_text(), 'name = "personal"\n')
        self.assertEqual(self.run_install(), [])

    def test_uneditable_removed_agent_key_fails_before_any_changes(self):
        self.home.mkdir()
        original = b'[agents]\nenabled = true\n"default_subagent_model" = "gpt-6-luna"\n'
        config = self.home / "config.toml"
        config.write_bytes(original)
        before = self.tree_state(self.home)
        with self.assertRaisesRegex(installer.InstallError, "Cannot safely edit"):
            self.run_install()
        self.assertEqual(before, self.tree_state(self.home))

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
