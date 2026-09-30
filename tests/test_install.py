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

    def test_upgrade_managed_sol_models_preserves_other_settings(self):
        self.run_install()
        config = self.home / "config.toml"
        config.write_text('# Personal setting\napproval_policy = "on-request"\n' +
                          config.read_text().replace('gpt-6.1-sol', 'gpt-6-sol'))
        sol_paths = [self.home / "agents" / f"{role}.toml"
                     for role in ("sol_worker", "sol_reviewer")]
        for path in sol_paths:
            path.write_text(path.read_text().replace('gpt-6.1-sol', 'gpt-6-sol'))
        other_roles = {self.home / "agents" / f"{role}.toml"
                       for role in installer.ROLES} - set(sol_paths)
        unchanged = {path: path.read_bytes() for path in other_roles}
        previous = {path: path.read_bytes() for path in [config, *sol_paths]}

        self.assertEqual(set(self.run_install()), set(previous))
        parsed = tomllib.loads(config.read_text())
        self.assertEqual(parsed["model"], "gpt-6.1-sol")
        self.assertEqual(parsed["model_reasoning_effort"], "medium")
        self.assertEqual(parsed["approval_policy"], "on-request")
        self.assertTrue(config.read_text().startswith("# Personal setting\n"))
        for path in sol_paths:
            role = tomllib.loads(path.read_text())
            self.assertEqual(role["model"], "gpt-6.1-sol")
            self.assertEqual(role["model_reasoning_effort"], installer.ROLE_EFFORTS[path.stem])
        for path, content in unchanged.items():
            self.assertEqual(path.read_bytes(), content)
        backup = sorted((self.home / "backups" / "codex-agent-collaboration").iterdir())[-1]
        for path, content in previous.items():
            self.assertEqual((backup / path.relative_to(self.home)).read_bytes(), content)
        self.assertEqual(self.run_install(), [])

    def prepare_previous_role_layout(self):
        self.run_install()
        analyst = self.home / "agents" / "sol_analyst.toml"
        analyst.unlink()
        worker = self.home / "agents" / "sol_worker.toml"
        worker.write_text(worker.read_text().replace(
            'model_reasoning_effort = "medium"', 'model_reasoning_effort = "high"'))
        retired = self.home / "agents" / "luna_worker.toml"
        retired.write_text(worker.read_text().replace('sol_worker', 'luna_worker').replace(
            'gpt-6.1-sol', 'gpt-6-luna'))
        retired.chmod(0o640)
        return retired, worker, analyst

    def test_role_transition_preview_check_backup_and_idempotence(self):
        retired, worker, analyst = self.prepare_previous_role_layout()
        old_retired = retired.read_bytes()
        before = self.tree_state(self.home)
        code, stdout, stderr = self.run_main("--dry-run")
        self.assertEqual((code, stderr), (0, ""))
        self.assertIn(f"Would remove: {retired}\n", stdout)
        self.assertEqual(before, self.tree_state(self.home))
        code, stdout, stderr = self.run_main("--check")
        self.assertEqual((code, stderr), (2, ""))
        self.assertEqual(set(stdout.splitlines()), {f"Drift: {path}" for path in (retired, worker, analyst)})
        self.assertEqual(before, self.tree_state(self.home))
        code, stdout, stderr = self.run_main()
        self.assertEqual((code, stderr), (0, ""))
        self.assertIn(f"Removed: {retired}\n", stdout)
        self.assertFalse(retired.exists())
        self.assertEqual(tomllib.loads(worker.read_text())["model_reasoning_effort"], "medium")
        self.assertEqual(tomllib.loads(analyst.read_text())["model_reasoning_effort"], "high")
        backup = sorted((self.home / "backups" / "codex-agent-collaboration").iterdir())[-1]
        self.assertEqual((backup / "agents" / "luna_worker.toml").read_bytes(), old_retired)
        entries = json.loads((backup / "manifest.json").read_text())
        entry = next(item for item in entries if item["target"] == "agents/luna_worker.toml")
        self.assertEqual((entry["action"], entry["mode"]), ("remove", 0o640))
        self.assertEqual(self.run_install(), [])
        self.assertEqual(self.run_main("--check"), (0, "Already up to date.\n", ""))

    def test_unmanaged_retired_role_blocks_all_changes(self):
        retired, _, _ = self.prepare_previous_role_layout()
        retired.write_text('name = "personal_role"\n')
        before = self.tree_state(self.home)
        for options in ({}, {"dry_run": True}, {"replace_roles": True}):
            with self.subTest(options=options), self.assertRaisesRegex(installer.InstallError, "Retired role is unmanaged"):
                self.run_install(**options)
            self.assertEqual(before, self.tree_state(self.home))

    def test_failure_after_retirement_restores_role_and_permissions(self):
        retired, worker, analyst = self.prepare_previous_role_layout()
        old_retired, old_worker = retired.read_bytes(), worker.read_bytes()
        original_write = installer._atomic_write

        def fail_worker(path, data, mode=0o600):
            if path == worker:
                self.assertFalse(retired.exists())
                raise OSError("simulated role write failure")
            return original_write(path, data, mode)

        with patch.object(installer, "_atomic_write", side_effect=fail_worker):
            with self.assertRaisesRegex(installer.InstallError, "simulated role write failure"):
                self.run_install()
        self.assertEqual(retired.read_bytes(), old_retired)
        self.assertEqual(retired.stat().st_mode & 0o777, 0o640)
        self.assertEqual(worker.read_bytes(), old_worker)
        self.assertFalse(analyst.exists())

    def test_wrong_worker_or_analyst_effort_blocks_install(self):
        for name, bad_effort in (("sol_worker", "high"), ("sol_analyst", "medium")):
            path = self.repo / "agents" / f"{name}.toml"
            original = path.read_text()
            with self.subTest(name=name):
                path.write_text(original.replace(
                    f'model_reasoning_effort = "{installer.ROLE_EFFORTS[name]}"',
                    f'model_reasoning_effort = "{bad_effort}"'))
                with self.assertRaisesRegex(installer.InstallError, "model_reasoning_effort"):
                    self.run_install()
                self.assertFalse(self.home.exists())
            path.write_text(original)

    def test_retirement_failure_rolls_back_prior_instruction_update(self):
        retired, worker, analyst = self.prepare_previous_role_layout()
        instructions = self.home / "AGENTS.md"
        instructions.write_text(instructions.read_text().replace("English rules", "Previous rules"))
        previous = {path: path.read_bytes() for path in (instructions, retired, worker)}
        original_unlink = Path.unlink

        def fail_retirement(path, *args, **kwargs):
            if path == retired:
                raise OSError("simulated retirement failure")
            return original_unlink(path, *args, **kwargs)

        with patch.object(Path, "unlink", fail_retirement):
            with self.assertRaisesRegex(installer.InstallError, "simulated retirement failure"):
                self.run_install()
        for path, content in previous.items():
            self.assertEqual(path.read_bytes(), content)
        self.assertFalse(analyst.exists())

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

    def test_check_missing_home_reports_drift_without_creating_anything(self):
        before = self.tree_state(self.home)
        code, stdout, stderr = self.run_main("--check")
        self.assertEqual(code, 2)
        self.assertEqual(stderr, "")
        self.assertEqual(len([line for line in stdout.splitlines() if line.startswith("Drift: ")]), 8)
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
        role = self.home / "agents" / "luna_reader.toml"
        agents.write_text(agents.read_text().replace("English rules", "Changed rules"))
        config.write_text(config.read_text().replace('model = "gpt-6.1-sol"', 'model = "other"'))
        role.write_text(role.read_text().replace("Fixture role", "Changed role"))
        (self.home / "agents" / "sol_worker.toml").unlink()
        before = self.tree_state(self.home)
        code, stdout, stderr = self.run_main("--check")
        self.assertEqual(code, 2)
        self.assertEqual(stderr, "")
        self.assertEqual(set(stdout.splitlines()), {
            f"Drift: {agents}", f"Drift: {config}", f"Drift: {role}",
            f"Drift: {self.home / 'agents' / 'sol_worker.toml'}",
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
        role = role_dir / "luna_reader.toml"
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
                              if line.startswith("Would update: ")]), 8)
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
        role.write_text(role.read_text().replace('gpt-6-luna', 'gpt-6.1-sol'))
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
            'model = "gpt-6.1-sol"\nmodel_reasoning_effort = "medium"\nagents = "bad"\n')
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
