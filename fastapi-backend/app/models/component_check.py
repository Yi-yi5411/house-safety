"""ComponentCheck (构件检查) SQLAlchemy model.

Matches Drizzle schema:
  id: uuid, survey_id: uuid NOT NULL, photos: text[],
  name: varchar(100), category: varchar(100), axis_line: varchar(100),
  checked_item_ids: jsonb DEFAULT [], description_values: jsonb DEFAULT {},
  ai_evaluation_result: varchar(255), ai_evaluation_clause: varchar(255).

Extra fields beyond Drizzle (additive, for extended functionality):
  component_type, floor_location, position_desc, damage_description,
  damage_level, crack_width, crack_length, deformation_value, corrosion_degree, remark.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ComponentCheck(Base, TimestampMixin):
    """构件检查记录模型。"""

    __tablename__ = "component_checks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    survey_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("surveys.id", ondelete="CASCADE"),
        nullable=False,
    )

    # 构件信息 (matches Drizzle)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    axis_line: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 检查项 (matches Drizzle)
    checked_item_ids: Mapped[list | None] = mapped_column(
        JSONB, default=[], nullable=True
    )
    description_values: Mapped[dict | None] = mapped_column(
        JSONB, default={}, nullable=True
    )

    # AI 推理 (matches Drizzle: varchar(255))
    ai_evaluation_result: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    ai_evaluation_clause: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    # 照片 (matches Drizzle: text[])
    photos: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )

    # ---- 扩展字段（原始Drizzle无，但FastAPI需要） ----
    component_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    floor_location: Mapped[str | None] = mapped_column(String(64), nullable=True)
    position_desc: Mapped[str | None] = mapped_column(String(256), nullable=True)
    damage_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    damage_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    crack_width: Mapped[float | None] = mapped_column(nullable=True)
    crack_length: Mapped[float | None] = mapped_column(nullable=True)
    deformation_value: Mapped[float | None] = mapped_column(nullable=True)
    corrosion_degree: Mapped[str | None] = mapped_column(String(32), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---- 关系 ----
    survey: Mapped["Survey"] = relationship(
        "Survey", back_populates="components"
    )

    def __repr__(self) -> str:
        return f"<ComponentCheck id={self.id} name={self.name}>"
