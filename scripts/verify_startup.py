#!/usr/bin/env python3
"""Read-only Phase 0 governance consistency verifier for OptiVest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


POLICY_NAME = "OPTIVEST_AI_POLICY_V10.md"
POLICY_HASH = "ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67"
GATE_SCOPE = "Manual evidence register; not runtime authorization"
NOT_READY = "NOT PRODUCTION READY"
REQUIRED_FILES = (
    "AGENTS.md",
    ".ai/START_HERE.md",
    ".ai/HANDOFF.md",
    ".ai/DECISIONS.md",
    ".ai/FILE_MAP.md",
    ".ai/TEST_STATUS.md",
    ".ai/RESEARCH_TRIALS.jsonl",
    ".ai/TODO.md",
    ".ai/PRODUCTION_GATE.json",
)
STRICT_FIELDS = ("Policy filename", "Policy SHA-256", "Branch", "Commit / HEAD")
METADATA_FIELDS = (
    "Updated", "Current task", "Role", "Delegation", "Policy version",
    "Decision version", "Risk Budget", "Mandate", "Validation", "Production", "Next file",
)
TRIAL_KEYS = {
    "trial_id", "hypothesis", "dataset_snapshot", "dataset_hash", "commit",
    "feature_parameter_set", "risk_budget", "oos_period", "model_name",
    "model_version", "prompt_hash", "policy_hash", "random_seed",
    "optimizer_version", "result", "disposition",
}
GATE_STATUSES = {"PASS", "FAIL", "NOT VERIFIED", "NOT APPROVED", "NOT APPLICABLE"}
HEX64 = re.compile(r"^[0-9A-Fa-f]{64}$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
STATE_TOKEN = re.compile(r"^STATE_SHA256:([0-9a-f]{64})$")
STATE_TOKEN_BYTES = re.compile(
    rb"(?m)^- Commit / HEAD: `STATE_SHA256:([0-9a-f]{64})`(?: \([^\r\n)]*\))?$"
)
PORTABLE_PATH = re.compile(rb"(?:[A-Za-z0-9._-]+/)*[A-Za-z0-9._-]+\Z")
START_PATH = ".ai/START_HERE.md"
START_PATH_BYTES = START_PATH.encode("ascii")
RESERVED_COMPONENT_STEMS = {
    b"CON", b"PRN", b"AUX", b"NUL", b"CLOCK$",
    *(f"COM{number}".encode("ascii") for number in range(1, 10)),
    *(f"LPT{number}".encode("ascii") for number in range(1, 10)),
}
GIT_FAILURES = {
    "GIT_COMMAND": ("", "Git command failed or returned malformed binary output."),
    "GIT_ROOT": ("", "Git root does not equal the requested workspace root."),
    "GIT_OBJECT_FORMAT": ("", "Git object format is not sha1."),
    "GIT_BRANCH": ("", "Git branch is not main."),
    "GIT_TOKEN": (START_PATH, "Recorded Commit / HEAD token is invalid."),
    "GIT_TREE": ("", "Committed tree record or portable path is invalid."),
    "GIT_CASE_COLLISION": ("", "Committed tree paths collide under ASCII case folding."),
    "GIT_START_ENTRY": (START_PATH, "Committed START_HERE entry is missing or is not a regular 100644 blob."),
    "GIT_INDEX": (START_PATH, "START_HERE index entry does not equal the committed stage-0 entry."),
    "GIT_INDEX_FLAGS": (START_PATH, "START_HERE has a hidden index or worktree flag."),
    "GIT_WORKTREE": (START_PATH, "START_HERE worktree state is not clean and regular inside the workspace."),
    "GIT_STATE_DIGEST_MISMATCH": (START_PATH, "Recorded state digest does not match committed workspace content."),
}
DIRTY_COUNT_LIMIT = 1000


class DuplicateKey(ValueError):
    pass


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey("duplicate JSON key")
        result[key] = value
    return result


def _json(text: str) -> Any:
    return json.loads(text, object_pairs_hook=_no_duplicates)


class Verifier:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.findings: list[dict[str, str]] = []
        self.observed: dict[str, Any] = {
            "branch": None,
            "head": None,
            "state_sha256": None,
            "recorded_branch": None,
            "recorded_head": None,
            "dirty": None,
            "dirty_counts": None,
            "policy_sha256": None,
        }
        self.recorded_branch_candidate: str | None = None
        self.recorded_head_candidate: str | None = None

    def fail(self, code: str, path: str = "", reason: str = "") -> None:
        self.findings.append({"code": code, "path": path, "reason": reason})

    def inside(self, candidate: Path) -> bool:
        try:
            candidate.resolve().relative_to(self.root)
            return True
        except (OSError, ValueError):
            return False

    def checked_file(self, relative: str) -> Path | None:
        path = self.root / relative
        try:
            if not path.is_file():
                self.fail("FILE_NOT_REGULAR", relative, "required regular file is missing or substituted")
                return None
            if not self.inside(path):
                self.fail("FILE_OUTSIDE_ROOT", relative, "resolved path escapes workspace root")
                return None
            return path
        except OSError:
            self.fail("FILE_UNREADABLE", relative, "required file cannot be inspected")
            return None

    def check_path_collisions(self) -> None:
        expected = {POLICY_NAME, *REQUIRED_FILES}
        lowered: dict[str, str] = {}
        try:
            for path in self.root.rglob("*"):
                if not path.is_file():
                    continue
                relative = path.relative_to(self.root).as_posix()
                key = relative.casefold()
                if key in {item.casefold() for item in expected}:
                    prior = lowered.get(key)
                    if prior is not None and prior != relative:
                        self.fail("PATH_CASE_COLLISION", relative, "canonical inspected path has a case collision")
                    lowered[key] = relative
        except OSError:
            self.fail("PATH_SCAN_FAILED", "", "workspace paths cannot be inspected")

    def read_text(self, relative: str) -> str | None:
        path = self.checked_file(relative)
        if path is None:
            return None
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            self.fail("FILE_DECODE_FAILED", relative, "file must be readable UTF-8 text")
            return None

    def check_required_files(self) -> None:
        for relative in REQUIRED_FILES:
            path = self.checked_file(relative)
            if path is None:
                continue
            if relative == ".ai/RESEARCH_TRIALS.jsonl":
                continue
            try:
                if not path.read_bytes().strip():
                    self.fail("FILE_BLANK", relative, "required file is blank")
            except OSError:
                self.fail("FILE_UNREADABLE", relative, "required file cannot be read")

    def policy_items(self, text: str) -> dict[int, str] | None:
        section = re.search(r"(?m)^# 18\. .*?$", text)
        if section is None:
            self.fail("POLICY_SECTION_18_MISSING", POLICY_NAME, "authoritative production-gate section is missing")
            return None
        items: dict[int, str] = {}
        for match in re.finditer(r"(?m)^(\d+)\.\s+(.+?)\s*$", text[section.end():]):
            item_id = int(match.group(1))
            if 1 <= item_id <= 25:
                if item_id in items:
                    self.fail("POLICY_GATE_ID_DUPLICATE", POLICY_NAME, "section 18 contains duplicate gate IDs")
                items[item_id] = match.group(2)
        if set(items) != set(range(1, 26)):
            self.fail("POLICY_GATE_ITEMS_INVALID", POLICY_NAME, "section 18 must contain exactly IDs 1 through 25")
            return None
        return items

    def check_policy(self) -> dict[int, str] | None:
        path = self.checked_file(POLICY_NAME)
        if path is None:
            return None
        try:
            data = path.read_bytes()
        except OSError:
            self.fail("POLICY_UNREADABLE", POLICY_NAME, "policy bytes cannot be read")
            return None
        digest = hashlib.sha256(data).hexdigest().upper()
        self.observed["policy_sha256"] = digest
        if digest != POLICY_HASH:
            self.fail("POLICY_HASH_MISMATCH", POLICY_NAME, "policy bytes do not match the selected authority")
            return None
        try:
            return self.policy_items(data.decode("utf-8"))
        except UnicodeDecodeError:
            self.fail("POLICY_DECODE_FAILED", POLICY_NAME, "policy must be UTF-8 text")
            return None

    def check_start_here(self) -> None:
        text = self.read_text(".ai/START_HERE.md")
        if text is None:
            return
        strict: dict[str, list[str]] = {label: [] for label in STRICT_FIELDS}
        metadata: dict[str, list[str]] = {label: [] for label in METADATA_FIELDS}
        for line in text.splitlines():
            for label in STRICT_FIELDS:
                match = re.fullmatch(rf"- {re.escape(label)}: `([^`]+)`(?: \([^)]*\))?", line)
                if match:
                    strict[label].append(match.group(1))
                elif line.startswith(f"- {label}:"):
                    self.fail("START_HERE_STRICT_GRAMMAR", ".ai/START_HERE.md", "machine field has invalid grammar")
            for label in METADATA_FIELDS:
                if line.startswith(f"- {label}:"):
                    value = line.split(":", 1)[1].strip()
                    metadata[label].append(value)
        for label, values in strict.items():
            if len(values) != 1:
                self.fail("START_HERE_STRICT_FIELD", ".ai/START_HERE.md", f"{label} must appear exactly once")
        for label, values in metadata.items():
            if len(values) != 1 or not values[0]:
                self.fail("START_HERE_METADATA_FIELD", ".ai/START_HERE.md", f"{label} must appear exactly once with a value")
        if all(len(strict[label]) == 1 for label in STRICT_FIELDS):
            if strict["Policy filename"][0] != POLICY_NAME:
                self.fail("START_HERE_POLICY_FILENAME", ".ai/START_HERE.md", "recorded policy filename differs")
            if not HEX64.fullmatch(strict["Policy SHA-256"][0]) or strict["Policy SHA-256"][0].upper() != POLICY_HASH:
                self.fail("START_HERE_POLICY_HASH", ".ai/START_HERE.md", "recorded policy hash differs")
            if strict["Branch"][0] != "main":
                self.fail("START_HERE_BRANCH", ".ai/START_HERE.md", "only main is accepted in Phase 0")
            head = strict["Commit / HEAD"][0]
            self.recorded_branch_candidate = strict["Branch"][0]
            self.recorded_head_candidate = head
        if len(metadata["Risk Budget"]) == 1 and not metadata["Risk Budget"][0].startswith("`PROVISIONAL / RISK BUDGET NOT APPROVED`"):
            self.fail("START_HERE_RISK_BUDGET", ".ai/START_HERE.md", "Phase 0 denial token is missing")
        if len(metadata["Production"]) == 1 and not metadata["Production"][0].startswith("`NOT PRODUCTION READY`"):
            self.fail("START_HERE_PRODUCTION", ".ai/START_HERE.md", "production denial token is missing")

    def _run_git(self, *args: str) -> tuple[int, bytes, bytes]:
        env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
        try:
            completed = subprocess.run(
                ["git", "-c", "core.refreshIndex=false", *args], cwd=self.root,
                env=env, capture_output=True, check=False,
            )
            return completed.returncode, completed.stdout, completed.stderr
        except (OSError, subprocess.SubprocessError):
            return 127, b"", b""

    def git(self, *args: str) -> tuple[int, str]:
        """Compatibility text wrapper used by retained Phase-0 tests."""
        code, output, stderr = self._run_git(*args)
        if code or stderr:
            return 1, ""
        try:
            return code, output.decode("utf-8").strip()
        except UnicodeDecodeError:
            return 1, ""

    @staticmethod
    def _line(output: bytes, *, encoding: str = "ascii") -> str | None:
        if output.endswith(b"\r\n"):
            raw = output[:-2]
        elif output.endswith(b"\n"):
            raw = output[:-1]
        else:
            return None
        if not raw or b"\r" in raw or b"\n" in raw or b"\0" in raw:
            return None
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            return None

    def _git_failure(self, code: str) -> bool:
        path, reason = GIT_FAILURES[code]
        self.findings = [{"code": code, "path": path, "reason": reason}]
        return False

    @staticmethod
    def _portable_path(path: bytes) -> bool:
        if not 1 <= len(path) <= 240 or PORTABLE_PATH.fullmatch(path) is None:
            return False
        for component in path.split(b"/"):
            if not 1 <= len(component) <= 100 or component in {b".", b".."}:
                return False
            if component.endswith((b".", b" ")):
                return False
            if component.split(b".", 1)[0].upper() in RESERVED_COMPONENT_STEMS:
                return False
        return True

    @staticmethod
    def _parse_tree(output: bytes) -> tuple[list[tuple[bytes, bytes, bytes, bytes, bytes]] | None, bool]:
        if not output or not output.endswith(b"\0"):
            return None, False
        entries: list[tuple[bytes, bytes, bytes, bytes, bytes]] = []
        seen: set[bytes] = set()
        folded: set[bytes] = set()
        collision = False
        for record in output[:-1].split(b"\0"):
            if not record or b"\t" not in record:
                return None, False
            header, path = record.split(b"\t", 1)
            parts = header.split(b" ")
            if len(parts) != 3:
                return None, False
            mode, object_type, object_id = parts
            if re.fullmatch(rb"[0-7]{6}", mode) is None or re.fullmatch(rb"[0-9a-f]{40}", object_id) is None:
                return None, False
            if (mode in {b"100644", b"100755", b"120000"} and object_type != b"blob") or (mode == b"160000" and object_type != b"commit"):
                return None, False
            if mode not in {b"100644", b"100755", b"120000", b"160000"}:
                return None, False
            if path in seen or not Verifier._portable_path(path):
                return None, False
            seen.add(path)
            key = path.lower()
            if key in folded:
                collision = True
            folded.add(key)
            entries.append((path, record + b"\0", mode, object_type, object_id))
        return entries, collision

    @staticmethod
    def _status_counts(output: bytes) -> dict[str, Any] | None:
        if not output:
            return {"staged": 0, "unstaged": 0, "untracked": 0, "total": 0, "truncated": False}
        if not output.endswith(b"\0"):
            return None
        records = output[:-1].split(b"\0")
        staged = unstaged = untracked = total = 0
        index = 0
        valid = b" MADRCU?!"
        while index < len(records):
            record = records[index]
            if len(record) < 4 or record[2:3] != b" " or record[0] not in valid or record[1] not in valid:
                return None
            x, y = record[0], record[1]
            total += 1
            if x == ord("?") and y == ord("?"):
                untracked += 1
            else:
                staged += int(x not in b" .")
                unstaged += int(y not in b" .")
            index += 1
            if x in b"RC" or y in b"RC":
                if index >= len(records) or not records[index]:
                    return None
                index += 1
        return {
            "staged": min(staged, DIRTY_COUNT_LIMIT),
            "unstaged": min(unstaged, DIRTY_COUNT_LIMIT),
            "untracked": min(untracked, DIRTY_COUNT_LIMIT),
            "total": min(total, DIRTY_COUNT_LIMIT),
            "truncated": total > DIRTY_COUNT_LIMIT,
        }

    def _observe_status(self) -> bool:
        code, output, stderr = self._run_git("status", "--porcelain=v1", "-z", "--untracked-files=all")
        counts = self._status_counts(output) if code == 0 and not stderr else None
        if counts is None:
            return self._git_failure("GIT_COMMAND")
        self.observed["dirty_counts"] = counts
        self.observed["dirty"] = bool(counts["total"])
        return True

    def _state_git_results(self) -> dict[str, tuple[int, bytes, bytes]]:
        """Collect every committed-state read before interpreting a state fault.

        Revision 4 makes a command failure the first table row.  Keeping the
        reads together prevents an early semantic return (for example a bad
        root) from hiding a failure in a later committed-state read.
        """
        return {
            "tree": self._run_git("ls-tree", "-rz", "--full-tree", "HEAD"),
            "blob": self._run_git("cat-file", "blob", f"HEAD:{START_PATH}"),
            "stage": self._run_git("ls-files", "-s", "-z", "--", START_PATH),
            "tag_v": self._run_git("ls-files", "-v", "-z", "--", START_PATH),
            "tag_t": self._run_git("ls-files", "-t", "-z", "--", START_PATH),
            "tag_f": self._run_git("ls-files", "-f", "-z", "--", START_PATH),
            "scoped": self._run_git("status", "--porcelain=v1", "-z", "--", START_PATH),
            "whole": self._run_git("status", "--porcelain=v1", "-z", "--untracked-files=all"),
        }

    def _state_commands_valid(self, results: dict[str, tuple[int, bytes, bytes]]) -> bool:
        """Reject command transport failures, except cat-file for a known absent entry."""
        tree_code, tree_output, tree_stderr = results["tree"]
        entries, _ = self._parse_tree(tree_output) if tree_code == 0 and not tree_stderr else (None, False)
        start_entries = [] if entries is None else [entry for entry in entries if entry[0] == START_PATH_BYTES]
        valid_start_entry = (
            entries is not None
            and len(start_entries) == 1
            and start_entries[0][2:4] == (b"100644", b"blob")
        )
        blob_code, _, blob_stderr = results["blob"]
        whole_code, whole_output, whole_stderr = results["whole"]
        whole_counts = self._status_counts(whole_output) if whole_code == 0 and not whole_stderr else None
        command_failed = (
            tree_code or tree_stderr
            or results["stage"][0] or results["stage"][2]
            or results["scoped"][0] or results["scoped"][2]
            or whole_counts is None
            or any(results[key][0] or results[key][2] for key in ("tag_v", "tag_t", "tag_f"))
            # A missing/non-regular entry is a specified START_ENTRY fault, so
            # its cat-file failure is expected.  In every other state it is a
            # command fault and wins the entire table.
            or (valid_start_entry and (blob_code or blob_stderr))
            or (entries is None and (blob_code or blob_stderr))
        )
        return not command_failed

    def _check_state_git(self, actual_head: str, results: dict[str, tuple[int, bytes, bytes]]) -> bool:
        recorded = self.recorded_head_candidate
        tree_code, tree_output, tree_stderr = results["tree"]
        blob_code, blob, blob_stderr = results["blob"]
        _, stage, _ = results["stage"]
        tag_results = [results[key] for key in ("tag_v", "tag_t", "tag_f")]
        _, scoped_status, _ = results["scoped"]
        whole_code, whole_status, whole_stderr = results["whole"]
        whole_counts = self._status_counts(whole_status) if whole_code == 0 and not whole_stderr else None
        if not self._state_commands_valid(results):
            return self._git_failure("GIT_COMMAND")

        entries, collision = self._parse_tree(tree_output)
        start_entries = [] if entries is None else [entry for entry in entries if entry[0] == START_PATH_BYTES]
        valid_start_entry = entries is not None and len(start_entries) == 1 and start_entries[0][2:4] == (b"100644", b"blob")
        token_match = STATE_TOKEN.fullmatch(recorded or "")
        # The worktree candidate token is row 5.  A successful committed blob
        # is the same row and must also be resolved before every later tree
        # semantic, even if the tree bytes are malformed.
        if token_match is None:
            return self._git_failure("GIT_TOKEN")
        if blob_code or blob_stderr:
            # `_state_commands_valid` has already made blob failure row 1 for
            # a valid START or an unparseable tree.  For parsed non-regular or
            # missing START entries it is expected; apply their later order.
            if entries is None or valid_start_entry:
                return self._git_failure("GIT_COMMAND")
            if collision:
                return self._git_failure("GIT_CASE_COLLISION")
            return self._git_failure("GIT_START_ENTRY")

        blob_match = None
        if not blob.startswith(b"\xef\xbb\xbf") and b"\r" not in blob and b"\0" not in blob:
            try:
                blob.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                pass
            else:
                matches = list(STATE_TOKEN_BYTES.finditer(blob))
                if len(matches) == 1:
                    blob_match = matches[0]
        if blob_match is None:
            return self._git_failure("GIT_TOKEN")
        self.observed["recorded_branch"] = self.recorded_branch_candidate
        self.observed["recorded_head"] = f"STATE_SHA256:{blob_match.group(1).decode('ascii')}"

        # From here the committed token is valid and its fields are safely
        # established.  Preserve the rev4 semantic sequence exactly.
        if entries is None:
            return self._git_failure("GIT_TREE")
        if collision:
            return self._git_failure("GIT_CASE_COLLISION")
        if not valid_start_entry:
            return self._git_failure("GIT_START_ENTRY")
        expected_stage = b"100644 " + start_entries[0][4] + b" 0\t" + START_PATH_BYTES + b"\0"
        if stage != expected_stage:
            return self._git_failure("GIT_INDEX")
        expected_tag = b"H " + START_PATH_BYTES + b"\0"
        if any(output != expected_tag for _, output, _ in tag_results):
            return self._git_failure("GIT_INDEX_FLAGS")

        start_path = self.root / START_PATH
        try:
            path_ok = (
                not start_path.is_symlink()
                and stat.S_ISREG(start_path.lstat().st_mode)
                and self.inside(start_path)
            )
        except OSError:
            path_ok = False
        if scoped_status or not path_ok:
            return self._git_failure("GIT_WORKTREE")
        self.observed["dirty_counts"] = whole_counts
        self.observed["dirty"] = bool(whole_counts["total"])

        normalized = blob[:blob_match.start(1)] + (b"0" * 64) + blob[blob_match.end(1):]
        normalized_sha = hashlib.sha256(normalized).hexdigest().encode("ascii")
        records = [(path, raw) for path, raw, _, _, _ in entries if path != START_PATH_BYTES]
        records.append((START_PATH_BYTES, b"100644 blob sha256:" + normalized_sha + b"\t" + START_PATH_BYTES + b"\0"))
        records.sort(key=lambda item: item[0])
        state_sha256 = hashlib.sha256(b"".join(raw for _, raw in records)).hexdigest()
        self.observed["state_sha256"] = state_sha256
        if blob_match.group(1).decode("ascii") != state_sha256:
            return self._git_failure("GIT_STATE_DIGEST_MISMATCH")
        return True

    def check_git(self) -> bool:
        code, top_output, top_stderr = self._run_git("rev-parse", "--show-toplevel")
        top = self._line(top_output, encoding="utf-8") if code == 0 and not top_stderr else None
        if code or top_stderr or top is None:
            return self._git_failure("GIT_COMMAND")
        format_code, format_output, format_stderr = self._run_git("rev-parse", "--show-object-format")
        object_format = self._line(format_output) if format_code == 0 and not format_stderr else None
        if format_code or format_stderr or object_format is None:
            return self._git_failure("GIT_COMMAND")

        branch_code, branch_output, branch_stderr = self._run_git("symbolic-ref", "--quiet", "--short", "HEAD")
        branch = self._line(branch_output) if branch_code == 0 and not branch_stderr else None
        if branch_code or branch_stderr:
            return self._git_failure("GIT_COMMAND")

        # --quiet keeps the valid UNBORN branch free of stderr while retaining
        # the frozen fail-closed rule for every command we actually invoke.
        head_code, head_output, head_stderr = self._run_git("rev-parse", "--verify", "--quiet", "HEAD")
        commit_code, commit_output, commit_stderr = self._run_git("rev-parse", "--verify", "--quiet", "HEAD^{commit}")
        commit = self._line(commit_output) if commit_code == 0 and not commit_stderr else None
        if commit_code == 0:
            if head_code or head_stderr:
                return self._git_failure("GIT_COMMAND")
            if commit is None or not SHA1.fullmatch(commit):
                return self._git_failure("GIT_COMMAND")
            actual_head = commit
        else:
            ref_code, _, ref_stderr = self._run_git("show-ref", "--verify", "--quiet", "refs/heads/main")
            if ref_code == 0 or head_code == 0 or head_stderr or commit_stderr or ref_stderr:
                return self._git_failure("GIT_COMMAND")
            if ref_code not in (0, 1):
                return self._git_failure("GIT_COMMAND")
            actual_head = "UNBORN"
        if actual_head != "UNBORN" and not SHA1.fullmatch(actual_head):
            return self._git_failure("GIT_COMMAND")

        # In committed mode resolve *all* state reads before emitting root,
        # object-format or branch semantics.  This is the rev4 global table
        # precedence rule, not a shortcut based on the apparent early fault.
        state_results = self._state_git_results() if actual_head != "UNBORN" else None
        if state_results is not None and not self._state_commands_valid(state_results):
            return self._git_failure("GIT_COMMAND")
        if actual_head == "UNBORN":
            status_code, status_output, status_stderr = self._run_git("status", "--porcelain=v1", "-z", "--untracked-files=all")
            if status_code or status_stderr or self._status_counts(status_output) is None:
                return self._git_failure("GIT_COMMAND")
        try:
            if Path(top).resolve() != self.root:
                return self._git_failure("GIT_ROOT")
        except OSError:
            return self._git_failure("GIT_ROOT")
        if object_format != "sha1":
            return self._git_failure("GIT_OBJECT_FORMAT")
        if branch != "main":
            return self._git_failure("GIT_BRANCH")
        self.observed["branch"] = branch
        self.observed["head"] = actual_head

        if actual_head != "UNBORN" and not SHA1.fullmatch(self.recorded_head_candidate or ""):
            assert state_results is not None
            return self._check_state_git(actual_head, state_results)

        self.observed["recorded_branch"] = self.recorded_branch_candidate
        self.observed["recorded_head"] = self.recorded_head_candidate
        if not self._observe_status():
            return False
        if self.recorded_branch_candidate != branch:
            self.fail("GIT_RECORDED_BRANCH_MISMATCH", ".ai/START_HERE.md", "recorded branch differs from Git")
        if self.recorded_head_candidate != actual_head:
            self.fail("GIT_RECORDED_HEAD_MISMATCH", ".ai/START_HERE.md", "recorded HEAD differs from Git")
        return True

    def check_gate(self, expected: dict[int, str] | None) -> None:
        text = self.read_text(".ai/PRODUCTION_GATE.json")
        if text is None or expected is None:
            return
        try:
            gate = _json(text)
        except (json.JSONDecodeError, DuplicateKey):
            self.fail("GATE_JSON_INVALID", ".ai/PRODUCTION_GATE.json", "gate JSON is malformed or has duplicate keys")
            return
        if type(gate) is not dict or set(gate) != {"policy_filename", "policy_sha256", "scope", "production_readiness", "items"}:
            self.fail("GATE_SCHEMA_INVALID", ".ai/PRODUCTION_GATE.json", "gate root keys or type are invalid")
            return
        if gate["policy_filename"] != POLICY_NAME or gate["policy_sha256"] != POLICY_HASH:
            self.fail("GATE_POLICY_PIN_MISMATCH", ".ai/PRODUCTION_GATE.json", "gate policy pin differs from authority")
        if gate["scope"] != GATE_SCOPE or gate["production_readiness"] != NOT_READY:
            self.fail("GATE_READINESS_INVALID", ".ai/PRODUCTION_GATE.json", "gate must retain Phase 0 scope and denial")
        if type(gate["items"]) is not list:
            self.fail("GATE_ITEMS_TYPE", ".ai/PRODUCTION_GATE.json", "items must be a list")
            return
        actual: dict[int, dict[str, Any]] = {}
        for item in gate["items"]:
            if type(item) is not dict or set(item) not in ({"id", "requirement", "status", "evidence"}, {"id", "requirement", "status", "evidence", "rationale"}):
                self.fail("GATE_ITEM_SCHEMA", ".ai/PRODUCTION_GATE.json", "gate item keys are invalid")
                continue
            item_id = item.get("id")
            if type(item_id) is not int or item_id in actual:
                self.fail("GATE_ITEM_ID", ".ai/PRODUCTION_GATE.json", "gate IDs must be unique integers")
                continue
            actual[item_id] = item
            if type(item["requirement"]) is not str or item["requirement"] != expected.get(item_id):
                self.fail("GATE_REQUIREMENT_MISMATCH", ".ai/PRODUCTION_GATE.json", "requirement must exactly match policy section 18")
            if type(item["status"]) is not str or item["status"] not in GATE_STATUSES:
                self.fail("GATE_STATUS_INVALID", ".ai/PRODUCTION_GATE.json", "unrecognized manual status")
            if type(item["evidence"]) is not list:
                self.fail("GATE_EVIDENCE_TYPE", ".ai/PRODUCTION_GATE.json", "evidence must be a list")
            if item["status"] == "PASS" and not item["evidence"]:
                self.fail("GATE_PASS_WITHOUT_EVIDENCE", ".ai/PRODUCTION_GATE.json", "declared PASS requires manual evidence references")
            if item["status"] == "NOT APPLICABLE" and (type(item.get("rationale")) is not str or not item["rationale"].strip()):
                self.fail("GATE_NA_RATIONALE", ".ai/PRODUCTION_GATE.json", "NOT APPLICABLE requires rationale")
        if set(actual) != set(expected):
            self.fail("GATE_ITEM_SET_INVALID", ".ai/PRODUCTION_GATE.json", "gate must cover exactly policy IDs 1 through 25")

    def check_trials(self) -> None:
        path = self.checked_file(".ai/RESEARCH_TRIALS.jsonl")
        if path is None:
            return
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            self.fail("TRIALS_UNREADABLE", ".ai/RESEARCH_TRIALS.jsonl", "ledger must be readable UTF-8")
            return
        if not raw:
            return
        for number, line in enumerate(raw.splitlines(), 1):
            if not line.strip():
                self.fail("TRIAL_BLANK_LINE", ".ai/RESEARCH_TRIALS.jsonl", "nonempty ledger cannot contain blank lines")
                continue
            try:
                record = _json(line)
            except (json.JSONDecodeError, DuplicateKey):
                self.fail("TRIAL_JSON_INVALID", ".ai/RESEARCH_TRIALS.jsonl", f"line {number} is malformed or duplicate")
                continue
            if type(record) is not dict or set(record) not in (TRIAL_KEYS, TRIAL_KEYS | {"not_applicable_reasons"}):
                self.fail("TRIAL_SCHEMA_INVALID", ".ai/RESEARCH_TRIALS.jsonl", f"line {number} has invalid keys")
                continue
            reasons = record.get("not_applicable_reasons", {})
            if type(reasons) is not dict:
                self.fail("TRIAL_NA_REASONS_TYPE", ".ai/RESEARCH_TRIALS.jsonl", f"line {number} reasons must be an object")
                continue
            for key, value in record.items():
                if key == "not_applicable_reasons":
                    continue
                if value is None:
                    if key in {"trial_id", "hypothesis", "policy_hash", "result", "disposition"} or type(reasons.get(key)) is not str or not reasons[key].strip():
                        self.fail("TRIAL_NULL_PROVENANCE", ".ai/RESEARCH_TRIALS.jsonl", f"line {number} null value lacks valid N/A reason")
                elif isinstance(value, bool) or (not isinstance(value, (str, int, float))) or (isinstance(value, str) and (not value.strip() or value.strip().casefold() in {"unknown", "unavailable"})):
                    self.fail("TRIAL_PROVENANCE_INVALID", ".ai/RESEARCH_TRIALS.jsonl", f"line {number} provenance is empty, unknown, or untyped")
            for key, reason in reasons.items():
                if key not in TRIAL_KEYS or record.get(key) is not None or type(reason) is not str or not reason.strip():
                    self.fail("TRIAL_NA_REASON_INVALID", ".ai/RESEARCH_TRIALS.jsonl", f"line {number} N/A reasons may only explain present null keys")
            if not isinstance(record["policy_hash"], str) or not HEX64.fullmatch(record["policy_hash"]):
                self.fail("TRIAL_POLICY_HASH_INVALID", ".ai/RESEARCH_TRIALS.jsonl", f"line {number} policy hash is invalid")
            if record["disposition"] not in {"accepted", "rejected"}:
                self.fail("TRIAL_DISPOSITION_INVALID", ".ai/RESEARCH_TRIALS.jsonl", f"line {number} disposition is invalid")

    def report(self) -> dict[str, Any]:
        findings = sorted(self.findings, key=lambda item: (item["code"], item["path"], item["reason"]))
        return {
            "startup_integrity": "PASS" if not findings else "FAIL",
            "production_readiness": NOT_READY,
            "observed": self.observed,
            "findings": findings,
            "capability_limits": [
                "Structural consistency only; no investment or model validation.",
                "OOS, shadow, and approval provenance are not validated.",
                "Append-only trial history is NOT VERIFIED from a current snapshot.",
            ],
        }

    def run(self) -> dict[str, Any]:
        self.check_path_collisions()
        self.check_required_files()
        expected = self.check_policy()
        self.check_start_here()
        if not self.check_git():
            return self.report()
        self.check_gate(expected)
        self.check_trials()
        return self.report()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify frozen OptiVest Phase 0 startup records.")
    parser.add_argument("--root", required=True, help="workspace root to inspect")
    args = parser.parse_args()
    try:
        report = Verifier(Path(args.root)).run()
    except Exception:
        report = {
            "startup_integrity": "FAIL", "production_readiness": NOT_READY,
            "observed": {
                "branch": None, "head": None, "state_sha256": None,
                "recorded_branch": None, "recorded_head": None,
                "dirty": None, "dirty_counts": None, "policy_sha256": None,
            },
            "findings": [{"code": "UNEXPECTED_VERIFIER_ERROR", "path": "", "reason": "verification could not complete"}],
            "capability_limits": ["Structural consistency only; no investment or model validation.", "OOS, shadow, and approval provenance are not validated.", "Append-only trial history is NOT VERIFIED from a current snapshot."],
        }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["startup_integrity"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
