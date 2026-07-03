"""EvaluationStandardKnowledge model - 鉴定依据标准知识库表.

Matches Drizzle schema:
  id: uuid, name: varchar(255) NOT NULL, code: varchar(255) NOT NULL,
  type: varchar(50) NOT NULL, content: text, is_default: boolean DEFAULT false.
"""

import uuid

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class EvaluationStandardKnowledge(Base, TimestampMixin):
    """鉴定依据标准知识库表 (evaluation_standard_knowledge)."""

    __tablename__ = "evaluation_standard_knowledge"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str | None] = mapped_column(String(255))
    updated_by: Mapped[str | None] = mapped_column(String(255))
