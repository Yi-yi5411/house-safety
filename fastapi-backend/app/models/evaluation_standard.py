"""EvaluationStandard (评定标准) SQLAlchemy model.

Matches Drizzle schema:
  category: varchar(100) NOT NULL, component_type: varchar(100) NOT NULL,
  description: text NOT NULL, evaluation_result: varchar(255),
  evaluation_clause: varchar(255), sort_order: integer DEFAULT 0.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class EvaluationStandard(Base, TimestampMixin):
    """评定标准模型。"""

    __tablename__ = "evaluation_standards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    component_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation_result: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    evaluation_clause: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(255))
    updated_by: Mapped[str | None] = mapped_column(String(255))

    def __repr__(self) -> str:
        return (
            f"<EvaluationStandard id={self.id} "
            f"category={self.category} type={self.component_type}>"
        )
