from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from itertools import combinations, product
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "verify_startup.py"
SPEC = importlib.util.spec_from_file_location("phase0_verifier", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
VERIFIER_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER_MODULE)
COPIED = [
    "AGENTS.md", "OPTIVEST_AI_POLICY_V10.md", ".gitattributes", ".ai/START_HERE.md",
    ".ai/HANDOFF.md", ".ai/DECISIONS.md", ".ai/FILE_MAP.md",
    ".ai/TEST_STATUS.md", ".ai/TODO.md", ".ai/PRODUCTION_GATE.json",
    ".ai/RESEARCH_TRIALS.jsonl",
]


class VerifyStartupTests(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name) / "workspace"
        root.mkdir()
        for relative in COPIED:
            source, target = REPO / relative, root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Phase0 Test"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "phase0@example.invalid"], cwd=root, check=True, capture_output=True)
        return temp, root

    def git(self, root: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
        return subprocess.run(
            ["git", *args], cwd=root, input=input_bytes, check=True, capture_output=True,
        ).stdout

    def make_state_commit(self, root: Path) -> tuple[str, str]:
        start = root / ".ai/START_HERE.md"
        text = start.read_text(encoding="utf-8")
        self.assertIn("- Commit / HEAD: `UNBORN`", text)
        start.write_text(
            text.replace(
                "- Commit / HEAD: `UNBORN`",
                f"- Commit / HEAD: `STATE_SHA256:{'0' * 64}`",
                1,
            ),
            encoding="utf-8",
            newline="\n",
        )
        self.git(root, "add", ".")
        self.git(root, "commit", "-m", "placeholder state")
        status, report = self.verify(root)
        self.assertEqual(status, 1)
        self.assertEqual([item["code"] for item in report["findings"]], ["GIT_STATE_DIGEST_MISMATCH"])
        state = report["observed"]["state_sha256"]
        self.assertRegex(state, r"^[0-9a-f]{64}$")
        start.write_text(
            start.read_text(encoding="utf-8").replace(
                f"STATE_SHA256:{'0' * 64}", f"STATE_SHA256:{state}", 1
            ),
            encoding="utf-8",
            newline="\n",
        )
        self.git(root, "add", ".ai/START_HERE.md")
        self.git(root, "commit", "--amend", "--no-edit")
        head = self.git(root, "rev-parse", "HEAD").decode("ascii").strip()
        status, report = self.verify(root)
        self.assertEqual(status, 0, report)
        self.assertEqual(report["observed"]["state_sha256"], state)
        self.assertEqual(report["observed"]["head"], head)
        return head, state

    def verify(self, root: Path) -> tuple[int, dict]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root)],
            cwd=root, text=True, encoding="utf-8", capture_output=True,
        )
        self.assertEqual(result.stderr, "")
        return result.returncode, json.loads(result.stdout)

    def assert_fail_code(self, root: Path, code: str) -> None:
        status, report = self.verify(root)
        self.assertNotEqual(status, 0)
        self.assertEqual(report["production_readiness"], "NOT PRODUCTION READY")
        self.assertIn(code, {item["code"] for item in report["findings"]})

    def snapshot(self, root: Path) -> dict[str, str]:
        """Hash every worktree and Git-admin file: verifier calls are read-only."""
        result = {}
        for path in root.rglob("*"):
            if path.is_file():
                result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        return result

    def injected_git_report(
        self,
        root: Path,
        faults: set[str],
        *,
        token_source: str = "candidate",
        token_variant: str = "missing",
    ) -> tuple[int, dict]:
        """Exercise frozen Git-fault precedence against a disposable real repo.

        Git cannot naturally emit every corrupt binary stream or successful
        command with stderr, so only those transport seams are injected.  The
        repository, its commit, index and all command reads are real.
        """
        verifier = VERIFIER_MODULE.Verifier(root)
        verifier.check_policy()
        verifier.check_start_here()
        applied: set[str] = set()
        token_applied: set[str] = set()
        if "GIT_TOKEN" in faults and token_source == "candidate":
            verifier.recorded_head_candidate = "not-a-state-token"
            applied.add("GIT_TOKEN")
            token_applied.add("candidate")
        self.assertIn(token_source, {"candidate", "blob"})
        original = verifier._run_git

        def malformed_token_blob(output: bytes) -> bytes:
            match = VERIFIER_MODULE.STATE_TOKEN_BYTES.search(output)
            assert match is not None
            if token_variant == "missing":
                return output[:match.start()] + b"- Commit / HEAD: `NOT_A_STATE_TOKEN`" + output[match.end():]
            if token_variant == "duplicate":
                return output + b"- Commit / HEAD: `STATE_SHA256:" + match.group(1) + b"`\n"
            if token_variant == "bom":
                return b"\xef\xbb\xbf" + output
            if token_variant == "cr":
                return output.replace(b"\n", b"\r\n", 1)
            if token_variant == "nul":
                return output + b"\0"
            if token_variant == "non_utf8":
                return output + b"\xff"
            self.fail(f"unknown committed-token fixture variant: {token_variant}")
            return output

        def tree_with_start_mode(output: bytes, mode: bytes) -> bytes:
            records = output[:-1].split(b"\0")
            changed = []
            for record in records:
                if record.endswith(b"\t.ai/START_HERE.md"):
                    header, path = record.split(b"\t", 1)
                    _, kind, oid = header.split(b" ")
                    record = b" ".join((mode, kind, oid)) + b"\t" + path
                changed.append(record)
            return b"\0".join(changed) + b"\0"

        def tree_with_collision(output: bytes) -> bytes:
            entry = next(record for record in output[:-1].split(b"\0") if b"\t.ai/START_HERE.md" in record)
            header, _ = entry.split(b"\t", 1)
            return output + header + b"\tCase.txt\0" + header + b"\tcase.txt\0"

        def wrapped(*args: str):
            code, output, stderr = original(*args)
            if "GIT_COMMAND" in faults and args == ("status", "--porcelain=v1", "-z", "--untracked-files=all"):
                applied.add("GIT_COMMAND")
                return 1, b"source-output-must-not-leak", b"source-stderr-must-not-leak"
            if "GIT_ROOT" in faults and args == ("rev-parse", "--show-toplevel"):
                applied.add("GIT_ROOT")
                return 0, b"C:/wrong-root\n", b""
            if "GIT_OBJECT_FORMAT" in faults and args == ("rev-parse", "--show-object-format"):
                applied.add("GIT_OBJECT_FORMAT")
                return 0, b"sha256\n", b""
            if "GIT_BRANCH" in faults and args == ("symbolic-ref", "--quiet", "--short", "HEAD"):
                applied.add("GIT_BRANCH")
                return 0, b"other\n", b""
            if "GIT_TREE" in faults and args == ("ls-tree", "-rz", "--full-tree", "HEAD"):
                transformed = output
                if "GIT_START_ENTRY" in faults:
                    transformed = tree_with_start_mode(transformed, b"100755")
                    applied.add("GIT_START_ENTRY")
                if "GIT_CASE_COLLISION" in faults:
                    transformed = tree_with_collision(transformed)
                    applied.add("GIT_CASE_COLLISION")
                applied.add("GIT_TREE")
                return 0, transformed + b"truncated-tree", b""
            if args == ("ls-tree", "-rz", "--full-tree", "HEAD"):
                transformed = output
                if "GIT_START_ENTRY" in faults:
                    transformed = tree_with_start_mode(transformed, b"100755")
                    applied.add("GIT_START_ENTRY")
                if "GIT_CASE_COLLISION" in faults:
                    transformed = tree_with_collision(transformed)
                    applied.add("GIT_CASE_COLLISION")
                return 0, transformed, b""
            if "GIT_INDEX" in faults and args == ("ls-files", "-s", "-z", "--", ".ai/START_HERE.md"):
                applied.add("GIT_INDEX")
                return 0, b"", b""
            if "GIT_INDEX_FLAGS" in faults and args == ("ls-files", "-f", "-z", "--", ".ai/START_HERE.md"):
                applied.add("GIT_INDEX_FLAGS")
                return 0, b"h .ai/START_HERE.md\0", b""
            if "GIT_WORKTREE" in faults and args == ("status", "--porcelain=v1", "-z", "--", ".ai/START_HERE.md"):
                applied.add("GIT_WORKTREE")
                return 0, b" M .ai/START_HERE.md\0", b""
            if (
                "GIT_TOKEN" in faults
                and token_source == "blob"
                and args == ("cat-file", "blob", "HEAD:.ai/START_HERE.md")
            ):
                applied.add("GIT_TOKEN")
                token_applied.add("blob")
                return 0, malformed_token_blob(output), b""
            if "GIT_STATE_DIGEST_MISMATCH" in faults and args == ("cat-file", "blob", "HEAD:.ai/START_HERE.md"):
                match = VERIFIER_MODULE.STATE_TOKEN_BYTES.search(output)
                assert match is not None
                applied.add("GIT_STATE_DIGEST_MISMATCH")
                return 0, output[:match.start(1)] + b"0" * 64 + output[match.end(1):], b""
            return code, output, stderr

        verifier._run_git = wrapped
        passed = verifier.check_git()
        self.assertEqual(faults, applied, f"pair fixture lost an injected fault: {faults=} {applied=}")
        if "GIT_TOKEN" in faults:
            self.assertEqual(token_applied, {token_source}, "token trigger did not use the requested source")
        return (0 if passed else 1), verifier.report()

    def expected_git_fault_report(
        self, code: str, head: str, state: str, *, recorded_state: str | None = None,
        recorded_established: bool = True,
    ) -> dict:
        """Literal rev4 top-level oracle, including all established nulls."""
        observed = {
            "branch": None, "head": None, "state_sha256": None,
            "recorded_branch": None, "recorded_head": None,
            "dirty": None, "dirty_counts": None,
            "policy_sha256": VERIFIER_MODULE.POLICY_HASH,
        }
        if code not in {"GIT_COMMAND", "GIT_ROOT", "GIT_OBJECT_FORMAT", "GIT_BRANCH"}:
            observed["branch"] = "main"
            observed["head"] = head
        if recorded_established and code in {"GIT_TREE", "GIT_CASE_COLLISION", "GIT_START_ENTRY", "GIT_INDEX", "GIT_INDEX_FLAGS", "GIT_WORKTREE", "GIT_STATE_DIGEST_MISMATCH"}:
            observed["recorded_branch"] = "main"
            observed["recorded_head"] = f"STATE_SHA256:{recorded_state or state}"
        if code == "GIT_STATE_DIGEST_MISMATCH":
            observed["state_sha256"] = state
            observed["dirty"] = False
            observed["dirty_counts"] = {
                "staged": 0, "unstaged": 0, "untracked": 0, "total": 0, "truncated": False,
            }
        path, reason = VERIFIER_MODULE.GIT_FAILURES[code]
        return {
            "startup_integrity": "FAIL",
            "production_readiness": "NOT PRODUCTION READY",
            "observed": observed,
            "findings": [{"code": code, "path": path, "reason": reason}],
            "capability_limits": [
                "Structural consistency only; no investment or model validation.",
                "OOS, shadow, and approval provenance are not validated.",
                "Append-only trial history is NOT VERIFIED from a current snapshot.",
            ],
        }

    def test_valid_unborn_is_structural_only_and_readonly(self) -> None:
        temp, root = self.make_root()
        with temp:
            before = self.snapshot(root)
            status, report = self.verify(root)
            self.assertEqual(status, 0)
            self.assertEqual(report["startup_integrity"], "PASS")
            self.assertEqual(report["production_readiness"], "NOT PRODUCTION READY")
            self.assertTrue(report["observed"]["dirty"])
            self.assertGreater(report["observed"]["dirty_counts"]["untracked"], 0)
            self.assertIn("Structural consistency only; no investment or model validation.", report["capability_limits"])
            self.assertEqual(before, self.snapshot(root))

    def test_policy_byte_mutation_and_newline_mutation_fail(self) -> None:
        for suffix in (b"x", b"\r\n"):
            temp, root = self.make_root()
            with temp:
                policy = root / "OPTIVEST_AI_POLICY_V10.md"
                policy.write_bytes(policy.read_bytes() + suffix)
                self.assert_fail_code(root, "POLICY_HASH_MISMATCH")

    def test_duplicate_gate_key_and_boolean_id_fail(self) -> None:
        temp, root = self.make_root()
        with temp:
            gate = root / ".ai/PRODUCTION_GATE.json"
            gate.write_text('{"policy_filename":"x","policy_filename":"y"}', encoding="utf-8")
            self.assert_fail_code(root, "GATE_JSON_INVALID")
        temp, root = self.make_root()
        with temp:
            gate = json.loads((root / ".ai/PRODUCTION_GATE.json").read_text(encoding="utf-8"))
            gate["items"][0]["id"] = True
            (root / ".ai/PRODUCTION_GATE.json").write_text(json.dumps(gate), encoding="utf-8")
            self.assert_fail_code(root, "GATE_ITEM_ID")

    def test_gate_requirement_readiness_and_unknown_keys_fail(self) -> None:
        temp, root = self.make_root()
        with temp:
            gate_path = root / ".ai/PRODUCTION_GATE.json"
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
            gate["production_readiness"] = "PRODUCTION READY"
            gate_path.write_text(json.dumps(gate), encoding="utf-8")
            self.assert_fail_code(root, "GATE_READINESS_INVALID")
        temp, root = self.make_root()
        with temp:
            gate_path = root / ".ai/PRODUCTION_GATE.json"
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
            gate["items"][0]["requirement"] += " altered"
            gate["extra"] = 1
            gate_path.write_text(json.dumps(gate), encoding="utf-8")
            self.assert_fail_code(root, "GATE_SCHEMA_INVALID")

    def test_malformed_and_unknown_trial_provenance_fail(self) -> None:
        temp, root = self.make_root()
        with temp:
            ledger = root / ".ai/RESEARCH_TRIALS.jsonl"
            ledger.write_text("{bad}\n", encoding="utf-8")
            self.assert_fail_code(root, "TRIAL_JSON_INVALID")
        temp, root = self.make_root()
        with temp:
            (root / ".ai/RESEARCH_TRIALS.jsonl").write_text(
                '{"policy_hash":"a","policy_hash":"b"}\n', encoding="utf-8"
            )
            self.assert_fail_code(root, "TRIAL_JSON_INVALID")
        temp, root = self.make_root()
        with temp:
            record = {
                "trial_id": "trial-1", "hypothesis": "h", "dataset_snapshot": "unknown",
                "dataset_hash": "a", "commit": "b", "feature_parameter_set": "c",
                "risk_budget": "d", "oos_period": "e", "model_name": "f",
                "model_version": "g", "prompt_hash": "h", "policy_hash": "0" * 64,
                "random_seed": 7, "optimizer_version": "i", "result": "j", "disposition": "accepted",
            }
            (root / ".ai/RESEARCH_TRIALS.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
            self.assert_fail_code(root, "TRIAL_PROVENANCE_INVALID")

    def test_trial_null_requires_na_reason_and_blank_lines_fail(self) -> None:
        temp, root = self.make_root()
        with temp:
            record = {
                "trial_id": "trial-1", "hypothesis": "h", "dataset_snapshot": None,
                "dataset_hash": "a", "commit": "b", "feature_parameter_set": "c", "risk_budget": "d",
                "oos_period": "e", "model_name": "f", "model_version": "g", "prompt_hash": "h",
                "policy_hash": "0" * 64, "random_seed": 7, "optimizer_version": "i", "result": "j", "disposition": "accepted",
            }
            (root / ".ai/RESEARCH_TRIALS.jsonl").write_text(json.dumps(record) + "\n\n", encoding="utf-8")
            self.assert_fail_code(root, "TRIAL_NULL_PROVENANCE")
            self.assert_fail_code(root, "TRIAL_BLANK_LINE")

    def test_start_here_metadata_and_git_mismatches_fail(self) -> None:
        temp, root = self.make_root()
        with temp:
            start = root / ".ai/START_HERE.md"
            text = start.read_text(encoding="utf-8").replace("- Mandate:", "- Mandate missing:")
            start.write_text(text, encoding="utf-8")
            self.assert_fail_code(root, "START_HERE_METADATA_FIELD")
        temp, root = self.make_root()
        with temp:
            start = root / ".ai/START_HERE.md"
            start.write_text(start.read_text(encoding="utf-8").replace("`main`", "`other`", 1), encoding="utf-8")
            self.assert_fail_code(root, "START_HERE_BRANCH")
            self.assert_fail_code(root, "GIT_RECORDED_BRANCH_MISMATCH")

    def test_parent_repo_and_non_main_branch_fail(self) -> None:
        temp, root = self.make_root()
        with temp:
            nested = root / "nested"
            nested.mkdir()
            for relative in COPIED:
                source, target = root / relative, nested / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            self.assert_fail_code(nested, "GIT_ROOT")
        temp, root = self.make_root()
        with temp:
            subprocess.run(["git", "checkout", "-b", "other"], cwd=root, check=True, capture_output=True)
            self.assert_fail_code(root, "GIT_BRANCH")

    def test_dangling_main_ref_fails_and_true_unborn_passes(self) -> None:
        temp, root = self.make_root()
        with temp:
            status, report = self.verify(root)
            self.assertEqual(status, 0)
            self.assertEqual(report["observed"]["head"], "UNBORN")
        temp, root = self.make_root()
        with temp:
            dangling = "a" * 40
            ref = root / ".git/refs/heads/main"
            ref.parent.mkdir(parents=True, exist_ok=True)
            ref.write_text(dangling + "\n", encoding="ascii")
            start = root / ".ai/START_HERE.md"
            start.write_text(start.read_text(encoding="utf-8").replace("`UNBORN`", f"`{dangling}`", 1), encoding="utf-8")
            self.assert_fail_code(root, "GIT_COMMAND")

    def test_committed_main_head_and_dirty_observation_pass(self) -> None:
        temp, root = self.make_root()
        with temp:
            (root / "marker").write_text("commit fixture", encoding="utf-8")
            subprocess.run(["git", "add", "marker"], cwd=root, check=True, capture_output=True)
            subprocess.run(
                ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "fixture"],
                cwd=root, check=True, capture_output=True,
            )
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, text=True, capture_output=True).stdout.strip()
            start = root / ".ai/START_HERE.md"
            start.write_text(start.read_text(encoding="utf-8").replace("`UNBORN`", f"`{head}`", 1), encoding="utf-8")
            (root / "dirty.txt").write_text("untracked", encoding="utf-8")
            status, report = self.verify(root)
            self.assertEqual(status, 0)
            self.assertEqual(report["observed"]["head"], head)
            self.assertTrue(report["observed"]["dirty"])
            self.assertGreaterEqual(report["observed"]["dirty_counts"]["untracked"], 1)

    def test_state_first_later_and_content_identical_commits(self) -> None:
        temp, root = self.make_root()
        with temp:
            (root / "payload.txt").write_bytes(b"one\n")
            _, initial_state = self.make_state_commit(root)

            self.git(root, "commit", "--allow-empty", "-m", "content identical")
            status, report = self.verify(root)
            self.assertEqual(status, 0, report)
            self.assertEqual(report["observed"]["state_sha256"], initial_state)

            (root / "payload.txt").write_bytes(b"two\n")
            self.git(root, "add", "payload.txt")
            self.git(root, "commit", "-m", "later content")
            status, report = self.verify(root)
            self.assertEqual(status, 1)
            self.assertEqual([item["code"] for item in report["findings"]], ["GIT_STATE_DIGEST_MISMATCH"])
            next_state = report["observed"]["state_sha256"]
            self.assertNotEqual(next_state, initial_state)

            start = root / ".ai/START_HERE.md"
            start.write_text(
                start.read_text(encoding="utf-8").replace(initial_state, next_state, 1),
                encoding="utf-8", newline="\n",
            )
            self.git(root, "add", ".ai/START_HERE.md")
            self.git(root, "commit", "--amend", "--no-edit")
            status, report = self.verify(root)
            self.assertEqual(status, 0, report)
            self.assertEqual(report["observed"]["state_sha256"], next_state)

    def test_state_digest_detects_add_delete_rename_mode_and_start_edits(self) -> None:
        cases = ("add", "delete", "rename", "mode", "start", "digits")
        for case in cases:
            with self.subTest(case=case):
                temp, root = self.make_root()
                with temp:
                    (root / "payload.txt").write_bytes(b"payload\n")
                    _, state = self.make_state_commit(root)
                    if case == "add":
                        (root / "added.txt").write_bytes(b"added\n")
                        self.git(root, "add", "added.txt")
                    elif case == "delete":
                        self.git(root, "rm", "payload.txt")
                    elif case == "rename":
                        self.git(root, "mv", "payload.txt", "renamed.txt")
                    elif case == "mode":
                        self.git(root, "update-index", "--chmod=+x", "payload.txt")
                    else:
                        start = root / ".ai/START_HERE.md"
                        raw = start.read_bytes()
                        if case == "start":
                            start.write_bytes(raw.replace(b"# Startup state", b"# Startup state changed", 1))
                        else:
                            start.write_bytes(raw.replace(state.encode("ascii"), b"1" * 64, 1))
                        self.git(root, "add", ".ai/START_HERE.md")
                    self.git(root, "commit", "-m", f"stale {case}")
                    status, report = self.verify(root)
                    self.assertEqual(status, 1)
                    self.assertEqual([item["code"] for item in report["findings"]], ["GIT_STATE_DIGEST_MISMATCH"])
                    if case == "digits":
                        self.assertEqual(report["observed"]["state_sha256"], state)

    def test_state_clean_autocrlf_clone_passes(self) -> None:
        temp, root = self.make_root()
        with temp:
            self.make_state_commit(root)
            clone = Path(temp.name) / "clone"
            subprocess.run(
                ["git", "-c", "core.autocrlf=true", "clone", "-q", str(root), str(clone)],
                check=True, capture_output=True,
            )
            working = (clone / ".ai/START_HERE.md").read_bytes()
            committed = subprocess.run(
                ["git", "cat-file", "blob", "HEAD:.ai/START_HERE.md"],
                cwd=clone, check=True, capture_output=True,
            ).stdout
            self.assertIn(b"\r\n", working)
            self.assertNotIn(b"\r", committed)
            self.assertNotEqual(working, committed)
            status, report = self.verify(clone)
            self.assertEqual(status, 0, report)

    def test_state_hidden_index_flag_matrix_is_closed_and_readonly(self) -> None:
        temp, root = self.make_root()
        with temp:
            self.make_state_commit(root)
            for assume, skip, fsmonitor in product((False, True), repeat=3):
                with self.subTest(assume=assume, skip=skip, fsmonitor=fsmonitor):
                    self.git(root, "config", "core.fsmonitor", "false")
                    self.git(root, "update-index", "--no-assume-unchanged", ".ai/START_HERE.md")
                    self.git(root, "update-index", "--no-skip-worktree", ".ai/START_HERE.md")
                    self.git(root, "update-index", "--no-fsmonitor-valid", ".ai/START_HERE.md")
                    self.git(root, "config", "core.fsmonitor", "true")
                    # Establish an actual divergence before each hidden state is
                    # marked.  This mirrors the bypass: Git is then told not to
                    # refresh/compare that already-divergent path.
                    if assume or skip or fsmonitor:
                        start = root / ".ai/START_HERE.md"
                        start.write_bytes(
                            start.read_bytes().replace(b"# Startup state", b"# Hidden state", 1)
                        )
                    if assume:
                        self.git(root, "update-index", "--assume-unchanged", ".ai/START_HERE.md")
                    if skip:
                        self.git(root, "update-index", "--skip-worktree", ".ai/START_HERE.md")
                    if fsmonitor:
                        self.git(root, "update-index", "--fsmonitor-valid", ".ai/START_HERE.md")
                    # Snapshot after the fixture mutation: verification itself
                    # must not clear flags, refresh the index, or rewrite files.
                    before = self.snapshot(root)
                    status, report = self.verify(root)
                    if assume or skip or fsmonitor:
                        self.assertEqual(status, 1)
                        self.assertEqual([item["code"] for item in report["findings"]], ["GIT_INDEX_FLAGS"])
                        self.assertIsNone(report["observed"]["state_sha256"])
                        self.assertIsNone(report["observed"]["dirty"])
                    else:
                        self.assertEqual(status, 0, report)
                    self.assertEqual(before, self.snapshot(root))

    def test_state_staged_index_only_and_untracked_replacement_fail(self) -> None:
        for case in ("staged", "index-only", "untracked-replacement"):
            with self.subTest(case=case):
                temp, root = self.make_root()
                with temp:
                    self.make_state_commit(root)
                    start = root / ".ai/START_HERE.md"
                    head_bytes = self.git(root, "show", "HEAD:.ai/START_HERE.md")
                    start.write_bytes(head_bytes.replace(b"# Startup state", b"# Changed", 1))
                    self.git(root, "add", ".ai/START_HERE.md")
                    if case == "index-only":
                        start.write_bytes(head_bytes)
                    elif case == "untracked-replacement":
                        self.git(root, "rm", "--cached", ".ai/START_HERE.md")
                    status, report = self.verify(root)
                    self.assertEqual(status, 1)
                    self.assertEqual([item["code"] for item in report["findings"]], ["GIT_INDEX"])

    def test_state_missing_committed_start_entry_is_not_command_failure(self) -> None:
        temp, root = self.make_root()
        with temp:
            self.make_state_commit(root)
            start = root / ".ai/START_HERE.md"
            saved = start.read_bytes()
            self.git(root, "rm", ".ai/START_HERE.md")
            self.git(root, "commit", "-m", "missing start fixture")
            start.parent.mkdir(parents=True, exist_ok=True)
            start.write_bytes(saved)
            before = self.snapshot(root)
            status, report = self.verify(root)
            self.assertEqual(status, 1)
            self.assertEqual([item["code"] for item in report["findings"]], ["GIT_START_ENTRY"])
            self.assertEqual(before, self.snapshot(root))

    def test_state_wrong_mode_committed_start_entry_is_not_command_failure(self) -> None:
        temp, root = self.make_root()
        with temp:
            self.make_state_commit(root)
            self.git(root, "update-index", "--chmod=+x", ".ai/START_HERE.md")
            self.git(root, "commit", "-m", "executable start fixture")
            before = self.snapshot(root)
            status, report = self.verify(root)
            self.assertEqual(status, 1)
            self.assertEqual([item["code"] for item in report["findings"]], ["GIT_START_ENTRY"])
            self.assertEqual(before, self.snapshot(root))

    def test_portable_path_grammar_and_tree_collision(self) -> None:
        valid = (b"a", b"good/path-1.txt", b".ai/START_HERE.md", b"A_B.C-d")
        invalid = (
            b"", b"CON", b"aux.txt", b"name.", b"name ", b"a:b", b"../x", b"/abs",
            b"a\\b", b"e\xcc\x81.txt", b"a//b", b"a" * 101, b"x/" + b"a" * 239,
        )
        for path in valid:
            self.assertTrue(VERIFIER_MODULE.Verifier._portable_path(path), path)
        for path in invalid:
            self.assertFalse(VERIFIER_MODULE.Verifier._portable_path(path), path)

        oid = b"0" * 40
        records = (
            b"100644 blob " + oid + b"\t.ai/START_HERE.md\0"
            b"100644 blob " + oid + b"\tCase.txt\0"
            b"100644 blob " + oid + b"\tcase.txt\0"
        )
        entries, collision = VERIFIER_MODULE.Verifier._parse_tree(records)
        self.assertIsNotNone(entries)
        self.assertTrue(collision)

    def test_state_fixed_failures_precedence_and_report_shape(self) -> None:
        temp, root = self.make_root()
        with temp:
            self.make_state_commit(root)

            def report_with(rewrite):
                verifier = VERIFIER_MODULE.Verifier(root)
                verifier.check_policy()
                verifier.check_start_here()
                original = verifier._run_git

                def wrapped(*args: str):
                    changed = rewrite(args, original)
                    if changed is None:
                        return original(*args)
                    return (*changed, b"") if len(changed) == 2 else changed

                verifier._run_git = wrapped
                verifier.check_git()
                return verifier.report()

            cases = {
                "GIT_COMMAND": lambda args, original: (1, b"") if args == ("rev-parse", "--show-toplevel") else None,
                "GIT_ROOT": lambda args, original: (0, b"C:/not-the-root\n") if args == ("rev-parse", "--show-toplevel") else None,
                "GIT_OBJECT_FORMAT": lambda args, original: (0, b"sha256\n") if args == ("rev-parse", "--show-object-format") else None,
                "GIT_BRANCH": lambda args, original: (0, b"other\n") if args == ("symbolic-ref", "--quiet", "--short", "HEAD") else None,
                "GIT_TREE": lambda args, original: (0, b"bad\0") if args == ("ls-tree", "-rz", "--full-tree", "HEAD") else None,
                "GIT_INDEX": lambda args, original: (0, b"") if args == ("ls-files", "-s", "-z", "--", ".ai/START_HERE.md") else None,
                "GIT_INDEX_FLAGS": lambda args, original: (0, b"h .ai/START_HERE.md\0") if args == ("ls-files", "-f", "-z", "--", ".ai/START_HERE.md") else None,
                "GIT_WORKTREE": lambda args, original: (0, b" M .ai/START_HERE.md\0") if args == ("status", "--porcelain=v1", "-z", "--", ".ai/START_HERE.md") else None,
            }
            expected_keys = {
                "branch", "head", "state_sha256", "recorded_branch", "recorded_head",
                "dirty", "dirty_counts", "policy_sha256",
            }
            for code, rewrite in cases.items():
                with self.subTest(code=code):
                    report = report_with(rewrite)
                    path, reason = VERIFIER_MODULE.GIT_FAILURES[code]
                    self.assertEqual(report["findings"], [{"code": code, "path": path, "reason": reason}])
                    self.assertEqual(report["startup_integrity"], "FAIL")
                    self.assertEqual(report["production_readiness"], "NOT PRODUCTION READY")
                    self.assertEqual(set(report["observed"]), expected_keys)

            # Token precedes tree, and tree precedes index flags.
            start = root / ".ai/START_HERE.md"
            original_start = start.read_bytes()
            start.write_bytes(original_start.replace(b"STATE_SHA256:", b"STATE_SHA256:X", 1))
            report = report_with(
                lambda args, original: (0, b"bad\0") if args == ("ls-tree", "-rz", "--full-tree", "HEAD") else None
            )
            self.assertEqual([item["code"] for item in report["findings"]], ["GIT_TOKEN"])
            start.write_bytes(original_start)
            report = report_with(
                lambda args, original: (0, b"bad\0") if args == ("ls-tree", "-rz", "--full-tree", "HEAD")
                else ((0, b"h .ai/START_HERE.md\0") if args == ("ls-files", "-f", "-z", "--", ".ai/START_HERE.md") else None)
            )
            self.assertEqual([item["code"] for item in report["findings"]], ["GIT_TREE"])

    def test_rev4_complete_exact_fault_and_pair_matrix_is_readonly(self) -> None:
        """Freeze all twelve rows and all 66 first-fault pairs as real-repo probes."""
        rows = tuple(VERIFIER_MODULE.GIT_FAILURES)
        temp, root = self.make_root()
        with temp:
            head, state = self.make_state_commit(root)
            for code in rows:
                with self.subTest(row=code):
                    before = self.snapshot(root)
                    status, report = self.injected_git_report(root, {code})
                    self.assertEqual(status, 1)
                    self.assertEqual(
                        report,
                        self.expected_git_fault_report(
                            code, head, state,
                            recorded_state="0" * 64 if code == "GIT_STATE_DIGEST_MISMATCH" else None,
                        ),
                    )
                    encoded = json.dumps(report, sort_keys=True)
                    self.assertNotIn("source-output-must-not-leak", encoded)
                    self.assertNotIn("source-stderr-must-not-leak", encoded)
                    self.assertEqual(before, self.snapshot(root))
            for earlier, later in combinations(rows, 2):
                with self.subTest(earlier=earlier, later=later):
                    before = self.snapshot(root)
                    status, report = self.injected_git_report(root, {earlier, later})
                    self.assertEqual(status, 1)
                    self.assertEqual(
                        report,
                        self.expected_git_fault_report(
                            earlier, head, state,
                            recorded_state="0" * 64 if later == "GIT_STATE_DIGEST_MISMATCH" else None,
                        ),
                    )
                    self.assertEqual(before, self.snapshot(root))

    def test_case_collision_precedes_wrong_start_entry_in_a_genuine_combined_tree(self) -> None:
        """The collision/START pair must contain both raw tree mutations, not a proxy."""
        temp, root = self.make_root()
        with temp:
            head, state = self.make_state_commit(root)
            before = self.snapshot(root)
            status, report = self.injected_git_report(root, {"GIT_CASE_COLLISION", "GIT_START_ENTRY"})
            self.assertEqual(status, 1)
            self.assertEqual(
                report,
                self.expected_git_fault_report("GIT_CASE_COLLISION", head, state),
            )
            self.assertEqual(before, self.snapshot(root))

    def test_committed_malformed_blob_token_precedes_an_independently_malformed_tree(self) -> None:
        """Use an actual committed bad START blob; only the impossible tree bytes are injected."""
        temp, root = self.make_root()
        with temp:
            self.make_state_commit(root)
            start = root / ".ai/START_HERE.md"
            valid_worktree = start.read_bytes()
            start.write_bytes(valid_worktree.replace(b"STATE_SHA256:", b"STATE_SHA257:", 1))
            self.git(root, "add", ".ai/START_HERE.md")
            self.git(root, "commit", "-m", "malformed committed token fixture")
            committed_head = self.git(root, "rev-parse", "HEAD").decode("ascii").strip()
            # Keep the worktree candidate valid so this exercises the distinct
            # committed-blob token route, not the retained candidate route.
            start.write_bytes(valid_worktree)
            verifier = VERIFIER_MODULE.Verifier(root)
            verifier.check_policy()
            verifier.check_start_here()
            original = verifier._run_git

            def wrapped(*args: str):
                if args == ("ls-tree", "-rz", "--full-tree", "HEAD"):
                    return 0, b"malformed-tree\0", b""
                return original(*args)

            verifier._run_git = wrapped
            before = self.snapshot(root)
            self.assertFalse(verifier.check_git())
            self.assertEqual(
                verifier.report(),
                self.expected_git_fault_report("GIT_TOKEN", committed_head, "unused"),
            )
            self.assertEqual(before, self.snapshot(root))

    def test_committed_blob_token_variants_precede_later_tree_rows(self) -> None:
        """All frozen committed-token malformed forms outrank tree/collision/START."""
        variants = ("missing", "duplicate", "bom", "cr", "nul", "non_utf8")
        later_rows = ("GIT_TREE", "GIT_CASE_COLLISION", "GIT_START_ENTRY")
        temp, root = self.make_root()
        with temp:
            head, state = self.make_state_commit(root)
            for variant in variants:
                for later in later_rows:
                    with self.subTest(variant=variant, later=later):
                        before = self.snapshot(root)
                        status, report = self.injected_git_report(
                            root,
                            {"GIT_TOKEN", later},
                            token_source="blob",
                            token_variant=variant,
                        )
                        self.assertEqual(status, 1)
                        self.assertEqual(report, self.expected_git_fault_report("GIT_TOKEN", head, state))
                        self.assertEqual(before, self.snapshot(root))

    def test_rev4_binary_and_command_stderr_faults_are_closed_and_readonly(self) -> None:
        """Inject only otherwise-unrealizable corrupt streams/stderr into a real repo."""
        temp, root = self.make_root()
        with temp:
            self.make_state_commit(root)

            def report_with(rewrite):
                verifier = VERIFIER_MODULE.Verifier(root)
                verifier.check_policy()
                verifier.check_start_here()
                original = verifier._run_git

                def wrapped(*args: str):
                    changed = rewrite(args, original)
                    return original(*args) if changed is None else changed

                verifier._run_git = wrapped
                before = self.snapshot(root)
                passed = verifier.check_git()
                self.assertEqual(before, self.snapshot(root))
                return 0 if passed else 1, verifier.report()

            reads = (
                ("rev-parse", "--show-toplevel"),
                ("rev-parse", "--show-object-format"),
                ("symbolic-ref", "--quiet", "--short", "HEAD"),
                ("rev-parse", "--verify", "--quiet", "HEAD"),
                ("rev-parse", "--verify", "--quiet", "HEAD^{commit}"),
                ("ls-tree", "-rz", "--full-tree", "HEAD"),
                ("cat-file", "blob", "HEAD:.ai/START_HERE.md"),
                ("ls-files", "-s", "-z", "--", ".ai/START_HERE.md"),
                ("ls-files", "-v", "-z", "--", ".ai/START_HERE.md"),
                ("ls-files", "-t", "-z", "--", ".ai/START_HERE.md"),
                ("ls-files", "-f", "-z", "--", ".ai/START_HERE.md"),
                ("status", "--porcelain=v1", "-z", "--", ".ai/START_HERE.md"),
                ("status", "--porcelain=v1", "-z", "--untracked-files=all"),
            )
            for read in reads:
                for exit_code in (0, 1):
                    with self.subTest(read=read, exit_code=exit_code):
                        status, report = report_with(
                            lambda args, original, read=read, exit_code=exit_code:
                            (exit_code, original(*args)[1] if exit_code == 0 else b"", b"stderr-secret")
                            if args == read else None
                        )
                        self.assertEqual(status, 1)
                        self.assertEqual([item["code"] for item in report["findings"]], ["GIT_COMMAND"])
                        self.assertNotIn("stderr-secret", json.dumps(report))

            malformed = {
                "tree_truncated": (("ls-tree", "-rz", "--full-tree", "HEAD"), (0, b"bad", b""), "GIT_TREE"),
                "tree_duplicate": (("ls-tree", "-rz", "--full-tree", "HEAD"), (0, b"100644 blob " + b"0" * 40 + b"\tdup\0" * 2, b""), "GIT_TREE"),
                "stage_truncated": (("ls-files", "-s", "-z", "--", ".ai/START_HERE.md"), (0, b"100644", b""), "GIT_INDEX"),
                "tag_truncated": (("ls-files", "-v", "-z", "--", ".ai/START_HERE.md"), (0, b"H .ai/START_HERE.md", b""), "GIT_INDEX_FLAGS"),
                "whole_truncated": (("status", "--porcelain=v1", "-z", "--untracked-files=all"), (0, b"?? no-nul", b""), "GIT_COMMAND"),
            }
            for name, (read, replacement, expected) in malformed.items():
                with self.subTest(binary=name):
                    status, report = report_with(
                        lambda args, original, read=read, replacement=replacement: replacement if args == read else None
                    )
                    self.assertEqual(status, 1)
                    self.assertEqual([item["code"] for item in report["findings"]], [expected])

    def test_git_command_stderr_and_later_command_precede_state_semantics(self) -> None:
        """Every Git read is fail-closed before token/tree/index semantics."""
        temp, root = self.make_root()
        with temp:
            self.make_state_commit(root)
            start = root / ".ai/START_HERE.md"
            original_start = start.read_bytes()

            def report_with(rewrite):
                verifier = VERIFIER_MODULE.Verifier(root)
                verifier.check_policy()
                verifier.check_start_here()
                original = verifier._run_git

                def wrapped(*args: str):
                    changed = rewrite(args, original)
                    return original(*args) if changed is None else changed

                verifier._run_git = wrapped
                verifier.check_git()
                return verifier.report()

            # This is the post-review counterexample: a later cat-file command
            # failure must win over the earlier-looking invalid machine token.
            start.write_bytes(original_start.replace(b"STATE_SHA256:", b"STATE_SHA256:X", 1))
            report = report_with(
                lambda args, original: (1, b"", b"fatal fixture")
                if args == ("cat-file", "blob", "HEAD:.ai/START_HERE.md") else None
            )
            self.assertEqual([item["code"] for item in report["findings"]], ["GIT_COMMAND"])
            self.assertNotIn("fatal fixture", json.dumps(report))
            start.write_bytes(original_start)

            # stderr is a failure even at exit zero, for every read used in the
            # committed state path.  The snapshots prove the verifier itself
            # did not change the repository while rejecting the fixture.
            reads = (
                ("ls-tree", "-rz", "--full-tree", "HEAD"),
                ("cat-file", "blob", "HEAD:.ai/START_HERE.md"),
                ("ls-files", "-s", "-z", "--", ".ai/START_HERE.md"),
                ("ls-files", "-v", "-z", "--", ".ai/START_HERE.md"),
                ("ls-files", "-t", "-z", "--", ".ai/START_HERE.md"),
                ("ls-files", "-f", "-z", "--", ".ai/START_HERE.md"),
                ("status", "--porcelain=v1", "-z", "--", ".ai/START_HERE.md"),
                ("status", "--porcelain=v1", "-z", "--untracked-files=all"),
            )
            for read in reads:
                with self.subTest(read=read):
                    before = self.snapshot(root)

                    def stderr_rewrite(args, original):
                        if args == read:
                            code, output, _ = original(*args)
                            return code, output, b"fixture stderr"
                        return None

                    report = report_with(stderr_rewrite)
                    self.assertEqual([item["code"] for item in report["findings"]], ["GIT_COMMAND"])
                    self.assertNotIn("fixture stderr", json.dumps(report))
                    self.assertEqual(before, self.snapshot(root))

            # Nonzero later reads also beat every later state finding.  The
            # malformed tree remains an independently lower-priority semantic.
            report = report_with(
                lambda args, original: (1, b"", b"")
                if args == ("status", "--porcelain=v1", "-z", "--untracked-files=all")
                else ((0, b"bad\0", b"") if args == ("ls-tree", "-rz", "--full-tree", "HEAD") else None)
            )
            self.assertEqual([item["code"] for item in report["findings"]], ["GIT_COMMAND"])

    def test_git_status_failure_is_a_finding(self) -> None:
        temp, root = self.make_root()
        with temp:
            verifier = VERIFIER_MODULE.Verifier(root)
            original_git = verifier._run_git

            def failing_status(*args: str) -> tuple[int, bytes, bytes]:
                if args == ("status", "--porcelain=v1", "-z", "--untracked-files=all"):
                    return 1, b"", b""
                return original_git(*args)

            verifier._run_git = failing_status
            verifier.check_git()
            self.assertEqual([item["code"] for item in verifier.report()["findings"]], ["GIT_COMMAND"])

    def test_unborn_git_command_stderr_is_closed_and_readonly(self) -> None:
        """The true-UNBORN path has its own applicable read set, including show-ref."""
        temp, root = self.make_root()
        with temp:
            reads = (
                ("rev-parse", "--show-toplevel"),
                ("rev-parse", "--show-object-format"),
                ("symbolic-ref", "--quiet", "--short", "HEAD"),
                ("rev-parse", "--verify", "--quiet", "HEAD"),
                ("rev-parse", "--verify", "--quiet", "HEAD^{commit}"),
                ("show-ref", "--verify", "--quiet", "refs/heads/main"),
                ("status", "--porcelain=v1", "-z", "--untracked-files=all"),
            )
            for read in reads:
                for exit_code in (0, 1):
                    with self.subTest(read=read, exit_code=exit_code):
                        verifier = VERIFIER_MODULE.Verifier(root)
                        verifier.check_policy()
                        verifier.check_start_here()
                        original = verifier._run_git

                        def wrapped(*args: str, read=read, exit_code=exit_code):
                            if args == read:
                                return exit_code, b"unborn-stdout-secret", b"unborn-stderr-secret"
                            return original(*args)

                        verifier._run_git = wrapped
                        before = self.snapshot(root)
                        self.assertFalse(verifier.check_git())
                        report = verifier.report()
                        self.assertEqual([item["code"] for item in report["findings"]], ["GIT_COMMAND"])
                        self.assertNotIn("unborn-stdout-secret", json.dumps(report))
                        self.assertNotIn("unborn-stderr-secret", json.dumps(report))
                        self.assertEqual(before, self.snapshot(root))

    def test_missing_required_file_and_directory_substitution_fail(self) -> None:
        temp, root = self.make_root()
        with temp:
            (root / ".ai/TODO.md").unlink()
            self.assert_fail_code(root, "FILE_NOT_REGULAR")
        temp, root = self.make_root()
        with temp:
            policy = root / "OPTIVEST_AI_POLICY_V10.md"
            policy.unlink()
            policy.mkdir()
            self.assert_fail_code(root, "FILE_NOT_REGULAR")

    def test_external_policy_link_fails_when_supported(self) -> None:
        temp, root = self.make_root()
        with temp:
            outside = Path(temp.name) / "outside-policy.md"
            outside.write_bytes((root / "OPTIVEST_AI_POLICY_V10.md").read_bytes())
            policy = root / "OPTIVEST_AI_POLICY_V10.md"
            policy.unlink()
            try:
                policy.symlink_to(outside)
            except OSError:
                self.skipTest("symlink creation is unavailable on this platform")
            self.assert_fail_code(root, "FILE_OUTSIDE_ROOT")


if __name__ == "__main__":
    unittest.main()
