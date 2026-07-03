"""TestImage model - 检测图片表.

Matches Drizzle schema:
  id: uuid, survey_id: uuid NOT NULL, type: varchar(50) NOT NULL,
  label: varchar(255), image_url: text NOT NULL, sort_order: integer DEFAULT 0.
"""

import uuid
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class TestImage(Base, TimestampMixin):
    """检测图片表 (test_image)."""

    __tablename__ = "test_image"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    survey_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("surveys.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str | None] = mapped_column(String(255))
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int | None] = mapped_column(Integer, default=0)
    created_by: Mapped[str | None] = mapped_column(String(255))
    updated_by: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    survey = relationship("Survey", back_populates="test_images")
