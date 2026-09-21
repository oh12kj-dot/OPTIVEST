"""Independent Sol acceptance probes for frozen RESEARCH-RISK-EDITOR-V1.

These tests encode selected mandatory negatives from design section 11.  They
are intentionally kept separate from the implementer's tests so any failure is
review evidence rather than an application-code correction.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys

import pytest
from sqlalchemy import text

from optivest import risk_editor
from optivest.db import make_session
from tests.test_phase1 import close_client, migrated_client


def _payload(status: dict, declaration: dict) -> dict:
    return {
        "request_kind": "FULL_DECLARATION",
        "schema_version": risk_editor.SCHEMA,
        "expected_current_version_id": status["risk_budget_version_id"],
        "mandate_version_id": status["mandate_version_id"],
        "rationale": "independent frozen-contract probe",
        "declaration": declaration,
    }


def _row(declaration: dict, metric: str) -> dict:
    return next(row for row in declaration["constraints"] if row["metric"] == metric)


def test_template_decimal_identity_survives_normalization_and_save():
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        declaration = risk_editor.template()
        response = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, declaration)),
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 201, response.text
        rows = {row["metric"]: row for row in response.json()["declaration"]["constraints"]}
        assert rows["MAX_SINGLE_NAME_EQUITY"]["limit"]["value"] == "10"
        assert rows["PASSIVE_MARKET_IMPLEMENTATION"]["limit"]["value"] == "100"
        assert rows["MAX_SECTOR_INDUSTRY"]["limit"]["value"] == "30"
    finally:
        close_client(client)


def test_forbidden_structural_risk_mode_is_rejected():
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        declaration = risk_editor.template()
        risk = _row(declaration, "MAX_SINGLE_NAME_EQUITY")["risk"]
        risk.update(
            mode="ROBUST_CHANCE",
            epsilon={"value": "0.1", "reason": None},
            u_risk_version={"value": "draft-u", "reason": None},
        )
        response = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, declaration)),
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422, response.text
    finally:
        close_client(client)


@pytest.mark.parametrize("mutation", ["joint", "percent"])
def test_malformed_joint_group_and_out_of_range_percent_are_rejected(mutation):
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        declaration = risk_editor.template()
        if mutation == "joint":
            declaration["joint_groups"] = [{}]
        else:
            _row(declaration, "MAX_SECTOR_INDUSTRY")["limit"]["value"] = "999"
        response = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, declaration)),
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422, (mutation, response.text)
    finally:
        close_client(client)


def test_preview_contains_recursive_declaration_changes():
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        declaration = risk_editor.template()
        _row(declaration, "MAX_SINGLE_NAME_EQUITY")["limit"]["value"] = "9"
        response = client.post(
            "/api/v1/risk-budgets/preview",
            content=json.dumps(_payload(status, declaration)),
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 200, response.text
        assert response.json()["changes"], response.text
    finally:
        close_client(client)


def test_api_rejects_unsupported_charset_and_content_encoding():
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        raw = json.dumps(_payload(status, risk_editor.template())).encode("utf-8")
        charset = client.post(
            "/api/v1/risk-budgets/preview",
            content=raw,
            headers={"content-type": "application/json; charset=shift_jis"},
        )
        encoded = client.post(
            "/api/v1/risk-budgets/preview",
            content=raw,
            headers={"content-type": "application/json", "content-encoding": "gzip"},
        )
        assert charset.status_code == 415, charset.text
        assert encoded.status_code == 415, encoded.text
    finally:
        close_client(client)


def test_preflight_adds_current_editor_evaluator_blockers():
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        saved = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, risk_editor.template())),
            headers={"content-type": "application/json"},
        )
        assert saved.status_code == 201, saved.text
        now = datetime.now(timezone.utc).isoformat()
        response = client.post(
            "/api/v1/decision-preflights",
            json={
                "mandate_version_id": status["mandate_version_id"],
                "risk_budget_version_id": saved.json()["id"],
                "decision_timestamp": now,
                "tradable_at": now,
            },
        )
        assert response.status_code == 201, response.text
        blockers = set(response.json()["blocker_codes"])
        assert {"RISK_FEASIBILITY_NOT_VERIFIED", "MODEL_IMPACT_NOT_AVAILABLE"} <= blockers
    finally:
        close_client(client)


def test_projection_drift_blocks_exact_head_verifier():
    _, client, url = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        saved = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, risk_editor.template())),
            headers={"content-type": "application/json"},
        )
        assert saved.status_code == 201, saved.text
        version_id = saved.json()["id"]
        with client.app.state.engine.begin() as connection:
            connection.exec_driver_sql("DROP TRIGGER trg_risk_constraints_no_update")
            connection.execute(
                text(
                    "UPDATE risk_constraints SET limit_value=77 "
                    "WHERE risk_budget_version_id=:version_id "
                    "AND metric='MAX_SECTOR_INDUSTRY'"
                ),
                {"version_id": version_id},
            )
        engine, factory = make_session(url)
        session = factory()
        try:
            with pytest.raises(risk_editor.EditorStorageError):
                risk_editor.verify_risk_editor(session)
        finally:
            session.close()
            engine.dispose()
    finally:
        close_client(client)


def test_forged_historical_server_envelope_blocks_verifier():
    _, client, url = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        first = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, risk_editor.template())),
            headers={"content-type": "application/json"},
        )
        assert first.status_code == 201, first.text
        first_id = first.json()["id"]
        clone = {
            "request_kind": "CLONE_CURRENT",
            "schema_version": risk_editor.SCHEMA,
            "expected_current_version_id": first_id,
            "mandate_version_id": status["mandate_version_id"],
            "rationale": "make first V1 historical",
            "declaration": None,
        }
        second = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(clone),
            headers={"content-type": "application/json"},
        )
        assert second.status_code == 201, second.text
        with client.app.state.engine.begin() as connection:
            raw = connection.execute(
                text(
                    "SELECT canonical_document FROM research_risk_editor_documents "
                    "WHERE risk_budget_version_id=:version_id"
                ),
                {"version_id": first_id},
            ).scalar_one()
            envelope = json.loads(raw)
            envelope["status"] = "APPROVED"
            forged = risk_editor.canonical(envelope)
            digest = hashlib.sha256(forged.encode("utf-8")).hexdigest()
            connection.exec_driver_sql("DROP TRIGGER trg_research_risk_editor_documents_update")
            connection.exec_driver_sql("DROP TRIGGER trg_research_risk_editor_markers_update")
            connection.execute(
                text(
                    "UPDATE research_risk_editor_documents SET canonical_document=:raw "
                    "WHERE risk_budget_version_id=:version_id"
                ),
                {"raw": forged, "version_id": first_id},
            )
            connection.execute(
                text(
                    "UPDATE research_risk_editor_markers SET document_sha256=:digest "
                    "WHERE risk_budget_version_id=:version_id"
                ),
                {"digest": digest, "version_id": first_id},
            )
        engine, factory = make_session(url)
        session = factory()
        try:
            with pytest.raises(risk_editor.EditorStorageError):
                risk_editor.verify_risk_editor(session)
        finally:
            session.close()
            engine.dispose()
    finally:
        close_client(client)


def test_status_fails_closed_after_current_document_digest_corruption():
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        saved = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, risk_editor.template())),
            headers={"content-type": "application/json"},
        )
        assert saved.status_code == 201, saved.text
        with client.app.state.engine.begin() as connection:
            connection.exec_driver_sql("DROP TRIGGER trg_research_risk_editor_markers_update")
            connection.execute(
                text(
                    "UPDATE research_risk_editor_markers SET document_sha256=:digest "
                    "WHERE risk_budget_version_id=:version_id"
                ),
                {"digest": "a" * 64, "version_id": saved.json()["id"]},
            )
        response = client.get("/api/v1/status")
        assert response.status_code == 503, response.text
        assert response.json() == {"error": {"code": "EDITOR_STORAGE_INVALID", "fields": []}}
    finally:
        close_client(client)


def test_api_error_envelope_is_not_nested_under_fastapi_detail():
    _, client, _ = migrated_client()
    try:
        raw = b'{"request_kind":"FULL_DECLARATION","request_kind":"CLONE_CURRENT"}'
        response = client.post(
            "/api/v1/risk-budgets/preview",
            content=raw,
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422
        assert "error" in response.json(), response.text
        assert "detail" not in response.json(), response.text
    finally:
        close_client(client)


def test_marker_digest_check_rejects_nonhex_lowercase_text():
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        with pytest.raises(Exception):
            with client.app.state.engine.begin() as connection:
                connection.execute(
                    text(
                        "INSERT INTO research_risk_editor_markers "
                        "(risk_budget_version_id,schema_version,document_sha256,created_at) "
                        "VALUES (:version_id,'RESEARCH_RISK_EDITOR_V1',:digest,CURRENT_TIMESTAMP)"
                    ),
                    {"version_id": status["risk_budget_version_id"], "digest": "z" * 64},
                )
    finally:
        close_client(client)


def test_projection_failure_is_internal_and_rolls_back(monkeypatch):
    _, client, _ = migrated_client()
    try:
        before = client.get("/api/v1/status").json()
        with client.app.state.engine.connect() as connection:
            count_before = connection.execute(text("SELECT count(1) FROM risk_budget_versions")).scalar_one()

        def fail_projection(*_args, **_kwargs):
            raise RuntimeError("independent injected projection failure")

        monkeypatch.setattr(risk_editor, "project", fail_projection)
        response = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(before, risk_editor.template())),
            headers={"content-type": "application/json"},
        )
        after = client.get("/api/v1/status").json()
        with client.app.state.engine.connect() as connection:
            count_after = connection.execute(text("SELECT count(1) FROM risk_budget_versions")).scalar_one()
        assert after["risk_budget_version_id"] == before["risk_budget_version_id"]
        assert count_after == count_before
        assert response.status_code == 500, response.text
        assert response.json() == {"error": {"code": "INTERNAL_ERROR", "fields": []}}
    finally:
        close_client(client)


def test_strict_decoder_rejects_nested_duplicates_and_raw_limits():
    for raw in (
        b'{"x":{"value":1,"value":2}}',
        b'{"risk":{"mode":"A","mode":"B"}}',
        b'{"joint_groups":[{"group_id":"a","group_id":"b"}]}',
    ):
        with pytest.raises(risk_editor.EditorError, match="JSON_DUPLICATE_KEY"):
            risk_editor.strict_decode(raw)
    for raw, code in (
        (b"\xef\xbb\xbf{}", "JSON_ENCODING"),
        (b'{"x":NaN}', "JSON_INVALID"),
        (b"{" + b'\"x\":\"' + b"a" * 1_048_576 + b'\"}', "JSON_SIZE"),
    ):
        with pytest.raises(risk_editor.EditorError, match=code):
            risk_editor.strict_decode(raw)


def test_all_four_legacy_v1_successor_transitions_are_represented():
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        legacy_clone = client.post(
            "/api/v1/risk-budgets/versions",
            json={
                "expected_current_version_id": status["risk_budget_version_id"],
                "mandate_version_id": status["mandate_version_id"],
                "rationale": "legacy clone",
            },
        )
        assert legacy_clone.status_code == 201, legacy_clone.text
        assert legacy_clone.json()["editor_document_status"] == "LEGACY_NOT_VERIFIED"

        status["risk_budget_version_id"] = legacy_clone.json()["id"]
        legacy_to_v1 = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, risk_editor.template())),
            headers={"content-type": "application/json"},
        )
        assert legacy_to_v1.status_code == 201, legacy_to_v1.text
        assert legacy_to_v1.json()["editor_document_status"] == "V1"

        v1_id = legacy_to_v1.json()["id"]
        v1_clone = client.post(
            "/api/v1/risk-budgets/versions",
            json={
                "request_kind": "CLONE_CURRENT",
                "schema_version": risk_editor.SCHEMA,
                "expected_current_version_id": v1_id,
                "mandate_version_id": status["mandate_version_id"],
                "rationale": "V1 clone",
                "declaration": None,
            },
        )
        assert v1_clone.status_code == 201, v1_clone.text
        assert v1_clone.json()["declaration"] == legacy_to_v1.json()["declaration"]

        status["risk_budget_version_id"] = v1_clone.json()["id"]
        v1_full = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, risk_editor.template("GROWTH_RESEARCH_V1"))),
            headers={"content-type": "application/json"},
        )
        assert v1_full.status_code == 201, v1_full.text
        assert v1_full.json()["editor_document_status"] == "V1"
        assert len(client.get("/api/v1/risk-budgets/versions").json()["items"]) == 5
    finally:
        close_client(client)


def test_sqlite_busy_maps_to_write_conflict():
    _, client, _ = migrated_client()
    blocker = client.app.state.engine.connect()
    transaction = None
    try:
        status = client.get("/api/v1/status").json()
        transaction = blocker.exec_driver_sql("BEGIN IMMEDIATE")
        response = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, risk_editor.template())),
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 409, response.text
        assert response.json() == {"error": {"code": "WRITE_CONFLICT", "fields": []}}
    finally:
        blocker.rollback()
        blocker.close()
        close_client(client)


@pytest.mark.parametrize(
    "mutation",
    [
        "risk_unknown_field",
        "stress_on_structural",
        "hybrid_on_structural",
        "wrong_catalog_horizon",
        "component_unknown_field",
        "not_applicable_reason_on_applicable_field",
    ],
)
def test_closed_nested_schema_and_class_matrix_are_enforced(mutation):
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        declaration = risk_editor.template()
        structural = _row(declaration, "MAX_SINGLE_NAME_EQUITY")
        if mutation == "risk_unknown_field":
            structural["risk"]["unfrozen"] = "accepted"
        elif mutation == "stress_on_structural":
            structural["stress"].update(
                proposed_role="DIAGNOSTIC",
                version={"value": "stress-v", "reason": None},
            )
        elif mutation == "hybrid_on_structural":
            structural["hybrid"]["observed_component"] = {
                "value": "claimed observation",
                "reason": None,
            }
        elif mutation == "wrong_catalog_horizon":
            structural["horizon"] = {
                "value": {
                    "kind": "OBSERVATION",
                    "unit": None,
                    "count": None,
                    "event_clock": "CURRENT_PORTFOLIO",
                },
                "reason": None,
            }
        elif mutation == "component_unknown_field":
            component = _row(declaration, "MAX_TURNOVER_IMPLEMENTATION_COST")["components"][0]
            component["unfrozen"] = "accepted"
        elif mutation == "not_applicable_reason_on_applicable_field":
            structural["definition"] = {"value": None, "reason": "NOT_APPLICABLE"}
        response = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, declaration)),
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422, (mutation, response.text)
    finally:
        close_client(client)


def test_wire_array_permutation_is_canonicalized_to_catalog_order():
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        declaration = risk_editor.template()
        declaration["constraints"] = list(reversed(declaration["constraints"]))
        response = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, declaration)),
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 201, response.text
        body = response.json()
        assert [row["metric"] for row in body["declaration"]["constraints"]] == [
            item[0] for item in risk_editor.METRICS
        ]
    finally:
        close_client(client)


def test_generated_template_retains_derived_balanced_name():
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        response = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, risk_editor.template())),
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 201, response.text
        assert response.json()["name"] == "BALANCED_RESEARCH_V1"
    finally:
        close_client(client)


def test_template_diagnostics_emit_frozen_missing_semantics_blockers():
    declaration = risk_editor.template()
    result = risk_editor.diagnostics(declaration, mandate_horizon=7, current=True)
    codes = {finding["code"] for finding in result["findings"]}
    blockers = set(result["blockers"])
    assert "FIELD_UNSPECIFIED" in codes
    assert {
        "RISK_SEMANTICS_UNSPECIFIED",
        "RISK_CALIBRATION_NOT_VERIFIED",
        "STRESS_SEMANTICS_UNSPECIFIED",
        "STRESS_VALIDATION_NOT_VERIFIED",
        "HYBRID_COMPONENT_NOT_VERIFIED",
        "JOINT_DEFINITION_MISSING",
        "JOINT_RISK_NOT_VERIFIED",
    } <= blockers


def test_cli_show_uses_the_same_version_serializer_as_api():
    _, client, url = migrated_client()
    try:
        api_value = client.get("/api/v1/risk-budgets/current").json()
        environment = os.environ.copy()
        environment["OPTIVEST_DATABASE_URL"] = url
        result = subprocess.run(
            [sys.executable, "-m", "optivest.cli", "risk-budget", "show"],
            cwd=os.fspath(os.path.dirname(os.path.dirname(__file__))),
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout) == api_value
    finally:
        close_client(client)


def test_risk_editor_page_exposes_actual_row_and_component_edit_controls():
    _, client, _ = migrated_client()
    try:
        response = client.get("/risk-budget")
        assert response.status_code == 200
        html = response.text
        assert html.count("<input") >= 19
        assert "TURNOVER" in html and "IMPLEMENTATION_COST" in html
        assert "history" in html.lower()
    finally:
        close_client(client)


def test_oversized_api_body_maps_to_413():
    _, client, _ = migrated_client()
    try:
        response = client.post(
            "/api/v1/risk-budgets/preview",
            content=b"{" + b" " * 1_048_576 + b"}",
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 413, response.text
        assert response.json() == {"error": {"code": "JSON_SIZE", "fields": []}}
    finally:
        close_client(client)


def test_corrupt_current_editor_blocks_preflight_without_snapshot_insert():
    _, client, _ = migrated_client()
    try:
        status = client.get("/api/v1/status").json()
        saved = client.post(
            "/api/v1/risk-budgets/versions",
            content=json.dumps(_payload(status, risk_editor.template())),
            headers={"content-type": "application/json"},
        )
        assert saved.status_code == 201, saved.text
        with client.app.state.engine.begin() as connection:
            connection.exec_driver_sql("DROP TRIGGER trg_research_risk_editor_markers_update")
            connection.execute(
                text(
                    "UPDATE research_risk_editor_markers SET document_sha256=:digest "
                    "WHERE risk_budget_version_id=:version_id"
                ),
                {"digest": "b" * 64, "version_id": saved.json()["id"]},
            )
            before = connection.execute(text("SELECT count(1) FROM decision_snapshots")).scalar_one()
        now = datetime.now(timezone.utc).isoformat()
        response = client.post(
            "/api/v1/decision-preflights",
            json={
                "mandate_version_id": status["mandate_version_id"],
                "risk_budget_version_id": saved.json()["id"],
                "decision_timestamp": now,
                "tradable_at": now,
            },
        )
        with client.app.state.engine.connect() as connection:
            after = connection.execute(text("SELECT count(1) FROM decision_snapshots")).scalar_one()
        assert response.status_code == 503, response.text
        assert after == before
    finally:
        close_client(client)
