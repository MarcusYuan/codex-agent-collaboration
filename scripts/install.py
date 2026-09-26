#!/usr/bin/env python3
"""Install this repository's shared Codex Desktop agent configuration."""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from datetime import datetime, timezone
from uuid import uuid4

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required to run this installer.")

import tomllib


REPO = Path(__file__).resolve().parent.parent
ROLES = (
    "luna_reader", "luna_worker", "luna_browser", "sol_worker",
    "sol_reviewer", "astra_advisor",
)
ROLE_MARKER = "# Managed by codex-agent-collaboration\n"
START = "<!-- BEGIN codex-agent-collaboration managed instructions -->"
END = "<!-- END codex-agent-collaboration managed instructions -->"
ROOT_KEYS = ("model", "model_reasoning_effort")
AGENT_KEYS = (
    "enabled", "max_concurrent_threads_per_session", "default_subagent_model",
    "default_subagent_reasoning_effort",
)
ROLE_MODELS = {
    "luna_reader": "gpt-6-luna", "luna_worker": "gpt-6-luna",
    "luna_browser": "gpt-6-luna", "sol_worker": "gpt-6-sol",
    "sol_reviewer": "gpt-6-sol", "astra_advisor": "gpt-6-astra",
}
REQUIRED_CONFIG = {
    "model": "gpt-6-sol",
    "model_reasoning_effort": "medium",
    "agents": {
        "enabled": True,
        "max_concurrent_threads_per_session": 8,
        "default_subagent_model": "gpt-6-luna",
        "default_subagent_reasoning_effort": "high",
    },
}
HEADER = re.compile(r"^\s*\[([^\[\]]+)\]\s*(?:#.*)?$")
KEY = re.compile(r"^(\s*)([A-Za-z0-9_-]+)\s*=")


class InstallError(Exception):
    pass


class _ArgumentError(Exception):
    pass


class _InstallerArgumentParser(argparse.ArgumentParser):
    """Keep command-line mistakes distinct from check drift's exit status 2."""

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self._print_message(f"{self.prog}: error: {message}\n", sys.stderr)
        raise _ArgumentError(message)


def _read(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise InstallError(f"Cannot read {path}: {exc}") from exc


def _toml(data: bytes, label: str) -> dict:
    try:
        value = tomllib.loads(data.decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise InstallError(f"Invalid TOML in {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise InstallError(f"Invalid TOML in {label}")
    return value


def _text(data: bytes, label: str) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeError as exc:
        raise InstallError(f"Invalid UTF-8 in {label}: {exc}") from exc


def _same_semantics(left: object, right: object) -> bool:
    """Compare parsed TOML values without Python's bool/int/float equality coercion."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return (left.keys() == right.keys()
                and all(_same_semantics(value, right[key]) for key, value in left.items()))
    if isinstance(left, list):
        return (len(left) == len(right)
                and all(_same_semantics(a, b) for a, b in zip(left, right)))
    if isinstance(left, float) and math.isnan(left):
        return math.isnan(right)
    return left == right


def _managed_instructions(existing: str, source: str, replace: bool) -> str:
    if START in source or END in source:
        raise InstallError("Source AGENTS file contains installer markers")
    block = f"{START}\n{source.rstrip()}\n{END}"
    starts, ends = existing.count(START), existing.count(END)
    if starts != ends or starts > 1:
        raise InstallError("AGENTS.md has incomplete or duplicate managed markers")
    if starts:
        before, rest = existing.split(START, 1)
        _, after = rest.split(END, 1)
        return before + block + after
    if existing.strip() and not replace:
        raise InstallError("AGENTS.md contains unmanaged instructions; use --replace-instructions")
    return block + "\n"


def _value_comment(line: str) -> str:
    """Return an inline comment without treating quoted # characters as comments."""
    quote = None
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
        elif quote == '"' and char == "\\":
            escaped = True
        elif quote and char == quote:
            quote = None
        elif not quote and char in "\"'":
            quote = char
        elif not quote and char == "#":
            return line[index:].rstrip("\r\n")
    return ""


def _config(existing: bytes, desired: bytes) -> bytes:
    wanted = _toml(desired, "config/codex.toml")
    if (set(wanted) != {*ROOT_KEYS, "agents"}
            or not isinstance(wanted.get("agents"), dict)
            or set(wanted["agents"]) != set(AGENT_KEYS)):
        raise InstallError("config/codex.toml must contain only the expected root and agents fields")
    for key in ROOT_KEYS:
        if type(wanted[key]) is not str or wanted[key] != REQUIRED_CONFIG[key]:
            raise InstallError(f"Invalid config/codex.toml value for {key}")
    for key in AGENT_KEYS:
        value, expected_value = wanted["agents"][key], REQUIRED_CONFIG["agents"][key]
        if type(value) is not type(expected_value) or value != expected_value:
            raise InstallError(f"Invalid config/codex.toml value for agents.{key}")
    current = _toml(existing, "target config.toml") if existing else {}
    agents = current.get("agents", {})
    if not isinstance(agents, dict):
        raise InstallError("Target agents value is not a table")
    if "max_threads" in agents:
        raise InstallError("Legacy agents.max_threads is present; resolve it before installing")
    expected = copy.deepcopy(current)
    for key in ROOT_KEYS:
        expected[key] = wanted[key]
    expected.setdefault("agents", {}).update(wanted["agents"])
    if _same_semantics(current, expected):
        return existing

    raw = _text(existing, "target config.toml")
    if raw and not raw.endswith("\n"):
        raw += "\n"
    lines = raw.splitlines(keepends=True)
    sections: dict[str, list[tuple[int, str, str]]] = {"root": [], "agents": []}
    header_pos: dict[str, int] = {}
    section = "root"
    first_header = len(lines)
    for index, line in enumerate(lines):
        match = HEADER.match(line)
        if match:
            section = match.group(1).strip()
            first_header = min(first_header, index)
            if section == "agents":
                header_pos["agents"] = index
            continue
        assignment = KEY.match(line)
        if assignment and section in sections:
            sections[section].append((index, assignment.group(2), assignment.group(1)))

    replacements: dict[int, str] = {}
    insertions: dict[int, list[str]] = {}
    for section_name, keys, insert_at in (
        ("root", ROOT_KEYS, first_header),
        ("agents", AGENT_KEYS, None),
    ):
        present = {name: (index, indent) for index, name, indent in sections[section_name]}
        if section_name == "agents":
            if "agents" not in header_pos:
                insertions.setdefault(len(lines), []).extend(["\n[agents]\n"])
                insert_at = len(lines)
            else:
                next_header = next((i for i in range(header_pos["agents"] + 1, len(lines))
                                    if HEADER.match(lines[i])), len(lines))
                insert_at = next_header
        for key in keys:
            value = desired_value(wanted[key] if section_name == "root" else wanted["agents"][key])
            if key in present:
                index, indent = present[key]
                comment = _value_comment(lines[index])
                replacements[index] = f"{indent}{key} = {value}{'  ' + comment if comment else ''}\n"
            else:
                insertions.setdefault(insert_at, []).append(f"{key} = {value}\n")
    output = []
    for index, line in enumerate(lines):
        output.extend(insertions.get(index, ()))
        output.append(replacements.get(index, line))
    output.extend(insertions.get(len(lines), ()))
    result = "".join(output).encode("utf-8")
    after = _toml(result, "proposed config.toml")
    if not _same_semantics(after, expected):
        raise InstallError("Cannot safely edit target config.toml structure")
    return result


def desired_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    raise InstallError("Unexpected config value type")


def _validate_role(data: dict, name: str, path: Path) -> None:
    for key in ("name", "description", "developer_instructions"):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise InstallError(f"Source role {path} needs nonempty string {key}")
    if data["name"] != name:
        raise InstallError(f"Source role {path} has wrong name: expected {name}")
    if data.get("model") != ROLE_MODELS[name]:
        raise InstallError(f"Source role {path} has wrong model: expected {ROLE_MODELS[name]}")
    if data.get("model_reasoning_effort") != "high":
        raise InstallError(f"Source role {path} needs model_reasoning_effort = high")


def _check_path(path: Path, home: Path) -> None:
    if not path.is_relative_to(home):
        raise InstallError(f"Target escapes Codex home: {path}")
    parents = (home, *(parent for parent in path.parents if parent.is_relative_to(home)))
    for candidate in parents:
        if candidate.is_symlink():
            raise InstallError(f"Symlink path is not allowed: {candidate}")
        if candidate.exists() and not candidate.is_dir():
            raise InstallError(f"Target parent is not a directory: {candidate}")
    if path.is_symlink():
        raise InstallError(f"Symlink target is not allowed: {path}")
    if path.exists() and not path.is_file():
        raise InstallError(f"Target is not a regular file: {path}")


def _atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def install(repo: Path, home: Path, language: str = "en", dry_run: bool = False,
            replace_instructions: bool = False, replace_roles: bool = False) -> list[Path]:
    home = home.expanduser().absolute()
    if home.is_symlink():
        raise InstallError(f"Symlink Codex home is not allowed: {home}")
    override = home / "AGENTS.override.md"
    if override.is_symlink():
        raise InstallError(f"Symlink override is not allowed: {override}")
    if override.exists() and _read(override).strip():
        raise InstallError(f"{override} is nonempty and takes priority over AGENTS.md")

    source_agents = repo / ("AGENTS.md" if language == "en" else "AGENTS.zh-CN.md")
    source_text = _text(_read(source_agents), str(source_agents))
    if not source_text.strip():
        raise InstallError(f"Source is empty: {source_agents}")
    snippet = _read(repo / "config" / "codex.toml")
    _toml(snippet, "config/codex.toml")

    targets = [home / "AGENTS.md", home / "config.toml"]
    targets += [home / "agents" / f"{name}.toml" for name in ROLES]
    for target in targets:
        _check_path(target, home)
    previous = {target: _read(target) if target.exists() else None for target in targets}
    old_modes = {target: stat.S_IMODE(target.stat().st_mode)
                 for target in targets if previous[target] is not None}
    proposed: dict[Path, bytes] = {}
    current_agents = _text(previous[targets[0]] or b"", str(targets[0]))
    proposed[targets[0]] = _managed_instructions(
        current_agents, source_text, replace_instructions).encode("utf-8")
    proposed[targets[1]] = _config(previous[targets[1]] or b"", snippet)
    for name, target in zip(ROLES, targets[2:]):
        role_path = repo / "agents" / f"{name}.toml"
        source = _read(role_path)
        role = _toml(source, str(role_path))
        _validate_role(role, name, role_path)
        if not source.strip():
            raise InstallError(f"Source role is empty: {role_path}")
        role_text = _text(source, str(role_path))
        if role_text.startswith(ROLE_MARKER):
            role_text = role_text[len(ROLE_MARKER):]
        wanted_role = (ROLE_MARKER + role_text.rstrip() + "\n").encode("utf-8")
        current = previous[target]
        if current is not None and not current.startswith(ROLE_MARKER.encode()):
            if current.strip() != role_text.encode().strip() and not replace_roles:
                raise InstallError(f"Unmanaged role differs: {target}; use --replace-roles")
        proposed[target] = wanted_role
    changes = [target for target in targets if proposed[target] != previous[target]]
    if dry_run or not changes:
        return changes

    backup_dir = home / "backups" / "codex-agent-collaboration" / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid4().hex[:8])
    _check_path(backup_dir / "manifest.json", home)
    manifest = []
    written: list[Path] = []
    try:
        backup_dir.mkdir(parents=True, mode=0o700)
        os.chmod(backup_dir, 0o700)
        for target in changes:
            old = previous[target]
            relative = target.relative_to(home)
            entry = {"target": str(relative), "existed": old is not None}
            if old is not None:
                entry["mode"] = old_modes[target]
                saved = backup_dir / relative
                _atomic_write(saved, old, 0o600)
                entry["backup"] = str(relative)
            manifest.append(entry)
        _atomic_write(backup_dir / "manifest.json",
                      (json.dumps(manifest, indent=2) + "\n").encode(), 0o600)
        for target in changes:
            old = previous[target]
            mode = old_modes[target] if old is not None else 0o600
            _atomic_write(target, proposed[target], mode)
            written.append(target)
    except OSError as exc:
        rollback_errors = []
        for target in reversed(written):
            try:
                old = previous[target]
                if old is None:
                    target.unlink()
                else:
                    _atomic_write(target, old, old_modes[target])
            except OSError as rollback_exc:
                rollback_errors.append(f"{target}: {rollback_exc}")
        detail = f"Install failed: {exc}. Backups: {backup_dir}"
        if rollback_errors:
            detail += "; rollback errors: " + "; ".join(rollback_errors)
        raise InstallError(detail) from exc
    print(f"Backups and restore manifest: {backup_dir}")
    return changes


def main(argv: list[str] | None = None) -> int:
    parser = _InstallerArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME") or "~/.codex"))
    parser.add_argument("--language", choices=("en", "zh-CN"), default="en")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check", action="store_true",
                        help="check whether managed files match the selected installation")
    parser.add_argument("--replace-instructions", action="store_true")
    parser.add_argument("--replace-roles", action="store_true")
    try:
        args = parser.parse_args(argv)
    except _ArgumentError:
        return 1
    if args.check and args.dry_run:
        try:
            parser.error("--check and --dry-run cannot be used together")
        except _ArgumentError:
            return 1
    try:
        changes = install(REPO, args.codex_home, args.language,
                          args.dry_run or args.check,
                          args.replace_instructions, args.replace_roles)
    except (InstallError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if not changes:
        print("Already up to date.")
    elif args.check:
        for target in changes:
            print(f"Drift: {target}")
        return 2
    else:
        action = "Would update" if args.dry_run else "Updated"
        for target in changes:
            print(f"{action}: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
