"""Phase 2 forward-only provider evidence staging."""
from alembic import op
import sqlalchemy as sa

revision = "0002_phase2"
down_revision = "0001_phase1"
branch_labels = None
depends_on = None

USES = "'NETWORK_CAPTURE','LOCAL_RAW_STORAGE','RETENTION','DERIVED_STORAGE','INTERNAL_DISPLAY','REDISTRIBUTION','COMMERCIAL_PRODUCTION'"
TERMINAL = "'SUCCEEDED','FAILED_HTTP','FAILED_INTEGRITY','FAILED_PARSE','FAILED_VALIDATION','BLOCKED_POLICY'"

def ident():
    return sa.Column("id", sa.String(), primary_key=True)

def stamp(name, nullable=False):
    return sa.Column(name, sa.DateTime(timezone=True), nullable=nullable)

def hex_check(column):
    return f"length({column})=64 AND {column}=lower({column}) AND {column} NOT GLOB '*[^0-9a-f]*'"

def upgrade():
    op.create_table(
        "license_evidence_versions", ident(),
        sa.Column("provider_id", sa.String(), sa.ForeignKey("providers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("artifact_sha256", sa.String(), nullable=False),
        sa.Column("canonical_url", sa.String(), nullable=False), stamp("retrieved_at"),
        sa.Column("reviewer", sa.String(), nullable=False), sa.Column("reason", sa.String(), nullable=False), stamp("created_at"),
        sa.CheckConstraint(hex_check("artifact_sha256"), name="ck_license_hash"),
        sa.CheckConstraint("length(trim(canonical_url))>0 AND length(trim(reviewer))>0 AND length(trim(reason))>0", name="ck_license_text"),
    )
    op.create_table(
        "license_use_permissions", ident(),
        sa.Column("license_evidence_version_id", sa.String(), sa.ForeignKey("license_evidence_versions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("use_type", sa.String(), nullable=False), sa.Column("permission", sa.String(), nullable=False), sa.Column("duty", sa.String()),
        sa.UniqueConstraint("license_evidence_version_id", "use_type", name="uq_license_use"),
        sa.CheckConstraint("permission IN ('ALLOWED','BLOCKED','NOT_VERIFIED')", name="ck_license_permission"),
        sa.CheckConstraint(f"use_type IN ({USES})", name="ck_license_use_type"),
    )
    op.create_table(
        "provider_dataset_versions", ident(),
        sa.Column("provider_id", sa.String(), sa.ForeignKey("providers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("dataset_name", sa.String(), nullable=False), sa.Column("semantic_version", sa.String(), nullable=False),
        sa.Column("endpoint_url", sa.String(), nullable=False), sa.Column("parser_name", sa.String(), nullable=False),
        sa.Column("parser_hash", sa.String(), nullable=False),
        sa.Column("license_evidence_version_id", sa.String(), sa.ForeignKey("license_evidence_versions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("timestamp_semantics", sa.String(), nullable=False), sa.Column("rate_policy", sa.JSON(), nullable=False),
        sa.Column("validation_status", sa.String(), nullable=False), stamp("created_at"),
        sa.CheckConstraint("validation_status='NOT_VERIFIED'", name="ck_dataset_unverified"),
        sa.CheckConstraint(hex_check("parser_hash"), name="ck_dataset_parser_hash"),
    )
    op.create_table(
        "capture_scopes", ident(),
        sa.Column("provider_dataset_version_id", sa.String(), sa.ForeignKey("provider_dataset_versions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("capture_scope_key", sa.String(), nullable=False), sa.Column("request_identity", sa.String(), nullable=False), stamp("created_at"),
        sa.UniqueConstraint("provider_dataset_version_id", "capture_scope_key", name="uq_capture_scope"),
        sa.CheckConstraint("length(trim(capture_scope_key))>0 AND length(trim(request_identity))>0", name="ck_scope_text"),
    )
    op.create_table(
        "ingestion_runs", ident(),
        sa.Column("capture_scope_id", sa.String(), sa.ForeignKey("capture_scopes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("request_fingerprint", sa.String(), nullable=False), sa.Column("state", sa.String(), nullable=False),
        stamp("request_started_at"), stamp("response_completed_at", True), sa.Column("error_code", sa.String()), sa.Column("error_reason", sa.String()),
        sa.Column("retry_of_id", sa.String(), sa.ForeignKey("ingestion_runs.id", ondelete="RESTRICT")),
        sa.Column("configuration_hash", sa.String(), nullable=False), stamp("created_at"),
        sa.CheckConstraint(f"state IN ('STARTED',{TERMINAL})", name="ck_run_state"),
        sa.CheckConstraint(hex_check("request_fingerprint") + " AND " + hex_check("configuration_hash"), name="ck_run_hashes"),
        sa.CheckConstraint("(state='STARTED' AND response_completed_at IS NULL AND error_code IS NULL AND error_reason IS NULL) OR (state='SUCCEEDED' AND response_completed_at>=request_started_at AND error_code IS NULL AND error_reason IS NULL) OR (state NOT IN ('STARTED','SUCCEEDED') AND response_completed_at>=request_started_at AND length(trim(error_code))>0 AND length(trim(error_reason))>0)", name="ck_run_terminal"),
    )
    op.create_table(
        "raw_objects", sa.Column("sha256", sa.String(), primary_key=True), sa.Column("byte_length", sa.Integer(), nullable=False),
        sa.Column("object_key", sa.String(), nullable=False, unique=True), stamp("created_at"),
        sa.CheckConstraint(hex_check("sha256"), name="ck_raw_sha"),
        sa.CheckConstraint("byte_length>=0 AND object_key=substr(sha256,1,2)||'/'||sha256", name="ck_raw_identity"),
    )
    op.create_table(
        "source_snapshots", ident(),
        sa.Column("capture_scope_id", sa.String(), sa.ForeignKey("capture_scopes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("run_id", sa.String(), sa.ForeignKey("ingestion_runs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("manifest", sa.JSON(), nullable=False), sa.Column("manifest_sha256", sa.String(), nullable=False),
        sa.Column("parser_version", sa.String(), nullable=False), sa.Column("parser_hash", sa.String(), nullable=False),
        stamp("observed_at"), stamp("usable_at"), sa.Column("state", sa.String(), nullable=False), stamp("created_at"),
        sa.UniqueConstraint("capture_scope_id", "manifest_sha256", name="uq_snapshot_manifest"),
        sa.CheckConstraint(hex_check("manifest_sha256") + " AND " + hex_check("parser_hash"), name="ck_snapshot_hashes"),
        sa.CheckConstraint("usable_at>=observed_at AND state='SUCCEEDED'", name="ck_snapshot_state_time"),
    )
    op.create_table(
        "source_snapshot_parts", ident(),
        sa.Column("snapshot_id", sa.String(), sa.ForeignKey("source_snapshots.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False), sa.Column("part_name", sa.String(), nullable=False),
        sa.Column("raw_sha256", sa.String(), sa.ForeignKey("raw_objects.sha256", ondelete="RESTRICT"), nullable=False),
        sa.Column("byte_length", sa.Integer(), nullable=False), sa.Column("media_type", sa.String(), nullable=False),
        stamp("response_completed_at"), sa.Column("http_status", sa.Integer(), nullable=False), sa.Column("response_headers", sa.JSON()),
        sa.Column("final_url", sa.String()), sa.Column("redirect_count", sa.Integer(), nullable=False), sa.Column("redirect_chain", sa.JSON()),
        stamp("request_started_at"), sa.Column("source_time_text", sa.String()), sa.Column("source_timezone", sa.String()),
        sa.Column("source_precision", sa.String()), stamp("source_published_at", True), stamp("available_at_claimed", True),
        stamp("available_at_validated", True), sa.Column("source_time_reason", sa.String()),
        sa.UniqueConstraint("snapshot_id", "ordinal", name="uq_part_ordinal"), sa.UniqueConstraint("snapshot_id", "part_name", name="uq_part_name"),
        sa.CheckConstraint("ordinal>0 AND byte_length>=0 AND redirect_count>=0", name="ck_part_numeric"),
        sa.CheckConstraint("http_status BETWEEN 100 AND 599 AND response_completed_at>=request_started_at", name="ck_part_transport"),
        sa.CheckConstraint("length(trim(part_name))>0 AND length(trim(media_type))>0 AND length(trim(source_time_reason))>0", name="ck_part_text"),
        sa.CheckConstraint("available_at_validated IS NULL", name="ck_part_unvalidated"),
    )
    op.create_table(
        "ingestion_attempts", ident(),
        sa.Column("run_id", sa.String(), sa.ForeignKey("ingestion_runs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("part_name", sa.String(), nullable=False), stamp("request_started_at"), stamp("response_completed_at"),
        sa.Column("http_status", sa.Integer()), sa.Column("response_headers", sa.JSON()), sa.Column("final_url", sa.String()),
        sa.Column("redirect_count", sa.Integer(), nullable=False, server_default="0"), sa.Column("redirect_chain", sa.JSON()),
        sa.Column("error_code", sa.String()), sa.Column("raw_sha256", sa.String(), sa.ForeignKey("raw_objects.sha256", ondelete="RESTRICT")),
        sa.CheckConstraint("redirect_count>=0 AND response_completed_at>=request_started_at", name="ck_attempt_time"),
        sa.CheckConstraint("(http_status BETWEEN 100 AND 599) OR length(trim(error_code))>0", name="ck_attempt_outcome"),
    )
    op.create_table(
        "source_rows", ident(),
        sa.Column("snapshot_id", sa.String(), sa.ForeignKey("source_snapshots.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("part_id", sa.String(), sa.ForeignKey("source_snapshot_parts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("row_key", sa.String(), nullable=False), sa.Column("row_hash", sa.String(), nullable=False), sa.Column("normalized", sa.JSON(), nullable=False),
        sa.UniqueConstraint("snapshot_id", "row_key", name="uq_source_row"),
        sa.CheckConstraint(hex_check("row_hash"), name="ck_source_row_hash"), sa.CheckConstraint("length(trim(row_key))>0", name="ck_source_row_key"),
    )
    op.create_table("dataset_heads",sa.Column("capture_scope_id",sa.String(),sa.ForeignKey("capture_scopes.id",ondelete="RESTRICT"),primary_key=True),sa.Column("snapshot_id",sa.String(),sa.ForeignKey("source_snapshots.id",ondelete="RESTRICT"),nullable=False),stamp("updated_at"))
    op.create_table("source_security_candidates",ident(),sa.Column("capture_scope_id",sa.String(),sa.ForeignKey("capture_scopes.id",ondelete="RESTRICT"),nullable=False),sa.Column("stable_key",sa.String(),nullable=False),sa.Column("state",sa.String(),nullable=False),stamp("created_at"),sa.UniqueConstraint("capture_scope_id","stable_key",name="uq_candidate_key"),sa.CheckConstraint("state='UNRESOLVED'",name="ck_candidate_unresolved"))
    op.create_table("staged_membership_events",ident(),sa.Column("candidate_id",sa.String(),sa.ForeignKey("source_security_candidates.id",ondelete="RESTRICT"),nullable=False),sa.Column("snapshot_id",sa.String(),sa.ForeignKey("source_snapshots.id",ondelete="RESTRICT"),nullable=False),sa.Column("event_type",sa.String(),nullable=False),stamp("observed_at"),stamp("usable_at"),sa.Column("reason",sa.String(),nullable=False),sa.CheckConstraint("event_type IN ('FIRST_OBSERVED','PRESENT','POSSIBLE_REMOVAL','REAPPEARED')",name="ck_event_type"),sa.CheckConstraint("usable_at>=observed_at AND length(trim(reason))>0",name="ck_event_time_reason"))
    op.create_table("identity_review_revisions",ident(),sa.Column("candidate_id",sa.String(),sa.ForeignKey("source_security_candidates.id",ondelete="RESTRICT"),nullable=False),sa.Column("supersedes_id",sa.String(),sa.ForeignKey("identity_review_revisions.id",ondelete="RESTRICT")),sa.Column("revision",sa.Integer(),nullable=False),sa.Column("status",sa.String(),nullable=False),sa.Column("actor",sa.String(),nullable=False),sa.Column("method_version",sa.String(),nullable=False),sa.Column("evidence_ids",sa.JSON(),nullable=False),sa.Column("reason",sa.String(),nullable=False),stamp("created_at"),sa.UniqueConstraint("supersedes_id",name="uq_identity_predecessor"),sa.CheckConstraint("revision>0 AND status IN ('UNRESOLVED','MATCHED_REVIEWED','CONFLICT','NO_MATCH','REJECTED') AND length(trim(actor))>0 AND length(trim(method_version))>0 AND length(trim(reason))>0",name="ck_review_state"))
    op.create_table("identity_review_heads",sa.Column("candidate_id",sa.String(),sa.ForeignKey("source_security_candidates.id",ondelete="RESTRICT"),primary_key=True),sa.Column("revision_id",sa.String(),sa.ForeignKey("identity_review_revisions.id",ondelete="RESTRICT"),nullable=False))
    op.create_table("run_snapshot_results",ident(),sa.Column("run_id",sa.String(),sa.ForeignKey("ingestion_runs.id",ondelete="RESTRICT"),nullable=False,unique=True),sa.Column("snapshot_id",sa.String(),sa.ForeignKey("source_snapshots.id",ondelete="RESTRICT"),nullable=False),sa.Column("result_type",sa.String(),nullable=False),stamp("created_at"),sa.CheckConstraint("result_type IN ('NEW','REUSED')",name="ck_run_result_type"))
    for table in ("license_evidence_versions","license_use_permissions","provider_dataset_versions","capture_scopes","raw_objects","source_snapshot_parts","source_rows","ingestion_attempts","source_security_candidates","staged_membership_events","identity_review_revisions","run_snapshot_results"):
        op.execute(f"CREATE TRIGGER trg_{table}_immutable_update BEFORE UPDATE ON {table} BEGIN SELECT RAISE(ABORT, 'immutable {table}'); END")
        op.execute(f"CREATE TRIGGER trg_{table}_immutable_delete BEFORE DELETE ON {table} BEGIN SELECT RAISE(ABORT, 'immutable {table}'); END")
    op.execute("CREATE TRIGGER trg_ingestion_runs_delete BEFORE DELETE ON ingestion_runs BEGIN SELECT RAISE(ABORT, 'immutable ingestion_runs'); END")
    op.execute("""CREATE TRIGGER trg_source_snapshots_immutable_update BEFORE UPDATE ON source_snapshots
        WHEN NOT (OLD.usable_at=OLD.observed_at AND NEW.usable_at>=NEW.observed_at
          AND NEW.id=OLD.id AND NEW.capture_scope_id=OLD.capture_scope_id AND NEW.run_id=OLD.run_id
          AND NEW.manifest=OLD.manifest AND NEW.manifest_sha256=OLD.manifest_sha256
          AND NEW.parser_version=OLD.parser_version AND NEW.parser_hash=OLD.parser_hash
          AND NEW.observed_at=OLD.observed_at AND NEW.state=OLD.state AND NEW.created_at=OLD.created_at)
        BEGIN SELECT RAISE(ABORT, 'immutable source_snapshots'); END""")
    op.execute("CREATE TRIGGER trg_source_snapshots_immutable_delete BEFORE DELETE ON source_snapshots BEGIN SELECT RAISE(ABORT, 'immutable source_snapshots'); END")
    op.execute("CREATE TRIGGER trg_ingestion_runs_started_insert BEFORE INSERT ON ingestion_runs WHEN NEW.state!='STARTED' BEGIN SELECT RAISE(ABORT, 'runs must start before terminal transition'); END")
    op.execute(f"""CREATE TRIGGER trg_ingestion_runs_transition BEFORE UPDATE ON ingestion_runs
        WHEN NOT (OLD.state='STARTED' AND NEW.state IN ({TERMINAL})
          AND NEW.capture_scope_id=OLD.capture_scope_id AND NEW.request_fingerprint=OLD.request_fingerprint
          AND NEW.request_started_at=OLD.request_started_at AND NEW.retry_of_id IS OLD.retry_of_id
          AND NEW.configuration_hash=OLD.configuration_hash AND NEW.created_at=OLD.created_at)
        BEGIN SELECT RAISE(ABORT, 'invalid run transition'); END""")
    op.execute("""CREATE TRIGGER trg_run_success_relation BEFORE UPDATE ON ingestion_runs
        WHEN NEW.state='SUCCEEDED' AND NOT EXISTS (SELECT 1 FROM run_snapshot_results WHERE run_id=NEW.id)
        BEGIN SELECT RAISE(ABORT, 'successful run requires snapshot relation'); END""")
    op.execute("""CREATE TRIGGER trg_snapshot_scope BEFORE INSERT ON source_snapshots
        WHEN NOT EXISTS (SELECT 1 FROM ingestion_runs r WHERE r.id=NEW.run_id AND r.capture_scope_id=NEW.capture_scope_id AND r.state='STARTED')
        BEGIN SELECT RAISE(ABORT, 'snapshot run scope mismatch'); END""")
    op.execute("""CREATE TRIGGER trg_part_integrity BEFORE INSERT ON source_snapshot_parts
        WHEN NOT EXISTS (SELECT 1 FROM raw_objects o WHERE o.sha256=NEW.raw_sha256 AND o.byte_length=NEW.byte_length)
        BEGIN SELECT RAISE(ABORT, 'part raw mismatch'); END""")
    op.execute("""CREATE TRIGGER trg_row_snapshot BEFORE INSERT ON source_rows
        WHEN NOT EXISTS (SELECT 1 FROM source_snapshot_parts p WHERE p.id=NEW.part_id AND p.snapshot_id=NEW.snapshot_id)
        BEGIN SELECT RAISE(ABORT, 'row part snapshot mismatch'); END""")
    op.execute("""CREATE TRIGGER trg_head_scope_insert BEFORE INSERT ON dataset_heads
        WHEN NOT EXISTS (SELECT 1 FROM source_snapshots s JOIN ingestion_runs r ON r.id=s.run_id JOIN run_snapshot_results rr ON rr.snapshot_id=s.id AND rr.run_id=r.id WHERE s.id=NEW.snapshot_id AND s.capture_scope_id=NEW.capture_scope_id AND s.state='SUCCEEDED' AND s.usable_at>=s.observed_at AND r.state='SUCCEEDED')
          OR NOT EXISTS (SELECT 1 FROM source_snapshot_parts WHERE snapshot_id=NEW.snapshot_id)
          OR NOT EXISTS (SELECT 1 FROM source_rows WHERE snapshot_id=NEW.snapshot_id)
        BEGIN SELECT RAISE(ABORT, 'head scope mismatch'); END""")
    op.execute("""CREATE TRIGGER trg_head_scope_update BEFORE UPDATE ON dataset_heads
        WHEN OLD.capture_scope_id!=NEW.capture_scope_id OR NOT EXISTS (SELECT 1 FROM source_snapshots s JOIN ingestion_runs r ON r.id=s.run_id JOIN run_snapshot_results rr ON rr.snapshot_id=s.id AND rr.run_id=r.id WHERE s.id=NEW.snapshot_id AND s.capture_scope_id=NEW.capture_scope_id AND s.state='SUCCEEDED' AND s.usable_at>=s.observed_at AND r.state='SUCCEEDED')
          OR NOT EXISTS (SELECT 1 FROM source_snapshot_parts WHERE snapshot_id=NEW.snapshot_id)
          OR NOT EXISTS (SELECT 1 FROM source_rows WHERE snapshot_id=NEW.snapshot_id)
        BEGIN SELECT RAISE(ABORT, 'head scope mismatch'); END""")
    op.execute("CREATE TRIGGER trg_head_delete BEFORE DELETE ON dataset_heads BEGIN SELECT RAISE(ABORT, 'immutable dataset head identity'); END")
    op.execute("""CREATE TRIGGER trg_head_nasdaq_pair_insert BEFORE INSERT ON dataset_heads
        WHEN (SELECT capture_scope_key FROM capture_scopes WHERE id=NEW.capture_scope_id)='US_LISTED_DIRECTORY'
         AND NOT EXISTS (SELECT 1 FROM source_snapshot_parts WHERE snapshot_id=NEW.snapshot_id GROUP BY snapshot_id HAVING count(*)=2 AND sum(ordinal=1 AND part_name='nasdaqlisted')=1 AND sum(ordinal=2 AND part_name='otherlisted')=1)
        BEGIN SELECT RAISE(ABORT, 'incomplete nasdaq pair'); END""")
    op.execute("""CREATE TRIGGER trg_head_nasdaq_pair_update BEFORE UPDATE ON dataset_heads
        WHEN (SELECT capture_scope_key FROM capture_scopes WHERE id=NEW.capture_scope_id)='US_LISTED_DIRECTORY'
         AND NOT EXISTS (SELECT 1 FROM source_snapshot_parts WHERE snapshot_id=NEW.snapshot_id GROUP BY snapshot_id HAVING count(*)=2 AND sum(ordinal=1 AND part_name='nasdaqlisted')=1 AND sum(ordinal=2 AND part_name='otherlisted')=1)
        BEGIN SELECT RAISE(ABORT, 'incomplete nasdaq pair'); END""")
    op.execute("""CREATE TRIGGER trg_run_result_scope BEFORE INSERT ON run_snapshot_results
        WHEN NOT EXISTS (SELECT 1 FROM ingestion_runs r JOIN source_snapshots s ON s.id=NEW.snapshot_id WHERE r.id=NEW.run_id AND r.capture_scope_id=s.capture_scope_id)
        BEGIN SELECT RAISE(ABORT, 'run result scope mismatch'); END""")
    op.execute("""CREATE TRIGGER trg_event_scope BEFORE INSERT ON staged_membership_events
        WHEN NOT EXISTS (SELECT 1 FROM source_security_candidates c JOIN source_snapshots s ON s.id=NEW.snapshot_id WHERE c.id=NEW.candidate_id AND c.capture_scope_id=s.capture_scope_id)
        BEGIN SELECT RAISE(ABORT, 'event scope mismatch'); END""")
    op.execute("""CREATE TRIGGER trg_review_successor BEFORE INSERT ON identity_review_revisions
        WHEN (NEW.revision=1 AND NEW.supersedes_id IS NOT NULL)
          OR (NEW.revision>1 AND NOT EXISTS (SELECT 1 FROM identity_review_revisions p WHERE p.id=NEW.supersedes_id AND p.candidate_id=NEW.candidate_id AND p.revision+1=NEW.revision))
        BEGIN SELECT RAISE(ABORT, 'review chain mismatch'); END""")
    op.execute("""CREATE TRIGGER trg_review_head_insert BEFORE INSERT ON identity_review_heads
        WHEN NOT EXISTS (SELECT 1 FROM identity_review_revisions r WHERE r.id=NEW.revision_id AND r.candidate_id=NEW.candidate_id)
        BEGIN SELECT RAISE(ABORT, 'review head mismatch'); END""")
    op.execute("""CREATE TRIGGER trg_review_head_update BEFORE UPDATE ON identity_review_heads
        WHEN OLD.candidate_id!=NEW.candidate_id OR NOT EXISTS (SELECT 1 FROM identity_review_revisions r JOIN identity_review_revisions oldr ON oldr.id=OLD.revision_id WHERE r.id=NEW.revision_id AND r.candidate_id=NEW.candidate_id AND r.revision>oldr.revision)
        BEGIN SELECT RAISE(ABORT, 'review head mismatch'); END""")
    op.execute("""CREATE TRIGGER trg_collector_review_state BEFORE INSERT ON identity_review_revisions
        WHEN NEW.actor='collector' AND NEW.status!='UNRESOLVED'
        BEGIN SELECT RAISE(ABORT, 'collector may create unresolved review only'); END""")
    op.execute("CREATE TRIGGER trg_review_head_delete BEFORE DELETE ON identity_review_heads BEGIN SELECT RAISE(ABORT, 'immutable review head identity'); END")
def downgrade():
    tables = (
        "identity_review_heads", "identity_review_revisions", "staged_membership_events",
        "source_security_candidates", "run_snapshot_results", "dataset_heads", "source_rows",
        "ingestion_attempts", "source_snapshot_parts", "source_snapshots", "raw_objects",
        "ingestion_runs", "capture_scopes", "provider_dataset_versions",
        "license_use_permissions", "license_evidence_versions",
    )
    for table in tables:
        op.drop_table(table)
