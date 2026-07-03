"""StructuralTestResult model - 结构检测结果表.

Matches Drizzle schema:
  id: uuid, survey_id: uuid NOT NULL, test_unit: varchar(255),
  certificate_no: varchar(255), test_personnel: varchar(255), report_no: varchar(255),
  test_date: timestamptz, main_test_content: text, test_standards: text,
  test_results_summary: text, damage_summary: text, cause_analysis: text,
  conclusion: text, handling_suggestion: text, safety_level: varchar(50).
"""

import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class StructuralTestResult(Base, TimestampMixin):
    """结构检测结果表 (structural_test_result)."""

    __tablename__ = "structural_test_result"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    survey_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("surveys.id"), nullable=False
    )
    test_unit: Mapped[str | None] = mapped_column(String(255))
    certificate_no: Mapped[str | None] = mapped_column(String(255))
    test_personnel: Mapped[str | None] = mapped_column(String(255))
    report_no: Mapped[str | None] = mapped_column(String(255))
    test_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    main_test_content: Mapped[str | None] = mapped_column(Text)
    test_standards: Mapped[str | None] = mapped_column(Text)
    test_results_summary: Mapped[str | None] = mapped_column(Text)
    damage_summary: Mapped[str | None] = mapped_column(Text)
    cause_analysis: Mapped[str | None] = mapped_column(Text)
    conclusion: Mapped[str | None] = mapped_column(Text)
    handling_suggestion: Mapped[str | None] = mapped_column(Text)
    safety_level: Mapped[str | None] = mapped_column(String(50))
    created_by: Mapped[str | None] = mapped_column(String(255))
    updated_by: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    survey = relationship("Survey", back_populates="structural_test_results")
