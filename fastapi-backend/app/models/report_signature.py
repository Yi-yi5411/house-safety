"""ReportSignature model - 报告签名表.

Matches Drizzle schema:
  id: uuid, survey_id: uuid NOT NULL, type: varchar(50) NOT NULL,
  signatory_name: varchar(255), image_url: text, sign_date: timestamptz.
"""

import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ReportSignature(Base, TimestampMixin):
    """报告签名表 (report_signature)."""

    __tablename__ = "report_signature"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    survey_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("surveys.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    signatory_name: Mapped[str | None] = mapped_column(String(255))
    image_url: Mapped[str | None] = mapped_column(Text)
    sign_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[str | None] = mapped_column(String(255))
    updated_by: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    survey = relationship("Survey", back_populates="report_signatures")
