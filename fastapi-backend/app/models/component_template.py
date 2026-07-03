"""ComponentTemplate model - 构件模板表."""

import uuid
from typing import Any

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ComponentTemplate(Base, TimestampMixin):
    """构件模板表 (component_template).

    Matches Drizzle schema:
      id: uuid, category: varchar(100) NOT NULL, name: varchar(100) NOT NULL,
      check_items: jsonb NOT NULL, display_order: integer DEFAULT 0.
    """

    __tablename__ = "component_template"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    check_items: Mapped[list[Any]] = mapped_column(JSONB, nullable=False)
    display_order: Mapped[int | None] = mapped_column(Integer, default=0)
    created_by: Mapped[str | None] = mapped_column(String(255))
    updated_by: Mapped[str | None] = mapped_column(String(255))
