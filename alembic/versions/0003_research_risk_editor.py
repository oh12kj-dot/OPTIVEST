"""research risk editor immutable documents

Revision ID: 0003_research_risk_editor
Revises: 0002_phase2
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_research_risk_editor"
down_revision = "0002_phase2"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("research_risk_editor_markers",
        sa.Column("risk_budget_version_id",sa.String(),sa.ForeignKey("risk_budget_versions.id",ondelete="RESTRICT"),primary_key=True),
        sa.Column("schema_version",sa.String(),nullable=False),sa.Column("document_sha256",sa.String(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.CheckConstraint("schema_version = 'RESEARCH_RISK_EDITOR_V1'",name="ck_editor_marker_schema"),sa.CheckConstraint("length(document_sha256)=64 AND document_sha256 GLOB '[0-9a-f]*' AND document_sha256 NOT GLOB '*[^0-9a-f]*'",name="ck_editor_marker_digest"),sa.CheckConstraint("length(created_at) > 0",name="ck_editor_marker_created_at"))
    op.create_table("research_risk_editor_documents",
        sa.Column("risk_budget_version_id",sa.String(),sa.ForeignKey("research_risk_editor_markers.risk_budget_version_id",ondelete="RESTRICT"),primary_key=True),
        sa.Column("schema_version",sa.String(),nullable=False),sa.Column("canonical_document",sa.Text(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.CheckConstraint("schema_version = 'RESEARCH_RISK_EDITOR_V1'",name="ck_editor_document_schema"),sa.CheckConstraint("json_valid(canonical_document)=1",name="ck_editor_document_json"),sa.CheckConstraint("length(created_at) > 0",name="ck_editor_document_created_at"))
    for table in ("research_risk_editor_markers","research_risk_editor_documents"):
        for action in ("UPDATE","DELETE"):
            op.execute(f"CREATE TRIGGER trg_{table}_{action.lower()} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT, 'immutable editor record'); END")

def downgrade():
    op.drop_table("research_risk_editor_documents")
    op.drop_table("research_risk_editor_markers")
