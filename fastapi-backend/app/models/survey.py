"""Survey (房屋安全鉴定记录) SQLAlchemy model."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Survey(Base, TimestampMixin):
    """房屋安全鉴定记录模型 — 包含 60+ 字段。"""

    __tablename__ = "surveys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ---- 基本信息 ----
    project_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    build_year: Mapped[str | None] = mapped_column(String(50), nullable=True)
    structure_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    floor_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    underground_floors: Mapped[int | None] = mapped_column(Integer, nullable=True)
    build_area: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    land_area: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    building_height: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2), nullable=True
    )
    usage: Mapped[str | None] = mapped_column(String(128), nullable=True)
    usage_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    owner_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    owner_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    owner_id_card: Mapped[str | None] = mapped_column(String(18), nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # ---- 建造与设计 ----
    design_unit: Mapped[str | None] = mapped_column(String(256), nullable=True)
    construction_unit: Mapped[str | None] = mapped_column(String(256), nullable=True)
    supervision_unit: Mapped[str | None] = mapped_column(String(256), nullable=True)
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    renovation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    renovation_scope: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---- 结构信息 ----
    foundation_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    foundation_depth: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    bearing_capacity: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2), nullable=True
    )
    seismic_design_intensity: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )
    seismic_grade: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fire_resistance_rating: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )
    roof_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    roof_waterproof: Mapped[str | None] = mapped_column(String(64), nullable=True)
    wall_material: Mapped[str | None] = mapped_column(String(128), nullable=True)
    floor_material: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # ---- 环境与地质 ----
    geological_condition: Mapped[str | None] = mapped_column(Text, nullable=True)
    surrounding_buildings: Mapped[str | None] = mapped_column(Text, nullable=True)
    terrain_slope: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    groundwater_level: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    soil_type: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # ---- 鉴定信息 ----
    survey_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    survey_purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    survey_method: Mapped[str | None] = mapped_column(String(256), nullable=True)
    surveyor_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    surveyor_cert: Mapped[str | None] = mapped_column(String(64), nullable=True)
    conclusion: Mapped[str | None] = mapped_column(Text, nullable=True)
    basic_evaluation: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_reasoning_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ---- 报告与原始记录 ----
    survey_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    survey_category: Mapped[str | None] = mapped_column(String(100), nullable=True, default="整幢鉴定")
    survey_category_desc: Mapped[str | None] = mapped_column(Text, nullable=True)
    site_plan_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    building_profile: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ---- 地址与委托方 ----
    street: Mapped[str | None] = mapped_column(String(255), nullable=True)
    community: Mapped[str | None] = mapped_column(String(255), nullable=True)
    property_owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    property_user: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    entrust_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    survey_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    inspection_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    inspection_complete_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ---- Word 模板字段 ----
    house_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    property_nature: Mapped[str | None] = mapped_column(String(100), nullable=True)
    property_certificate_no: Mapped[str | None] = mapped_column(String(255), nullable=True)
    eaves_height: Mapped[str | None] = mapped_column(String(50), nullable=True)
    design_usage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    survey_unit: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ---- 专项标识 ----
    is_rural_dangerous_repair: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_protected_building: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_historical_certificate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_training_institution: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_self_building_special_report: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_self_building: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_commercial_self_building: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    census_house_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    self_building_check_code: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ---- 文字描述 ----
    current_usage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    usage_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_environment: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluation_standards: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---- 状态与元数据 ----
    status: Mapped[str] = mapped_column(
        String(50), default="draft", nullable=False
    )
    creator: Mapped[str | None] = mapped_column(String(255), nullable=True)
    creator_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    report_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_record_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ---- 关系 ----
    components: Mapped[list[ComponentCheck]] = relationship(
        "ComponentCheck", back_populates="survey", cascade="all, delete-orphan"
    )
    structural_test_results: Mapped[list[StructuralTestResult]] = relationship(
        "StructuralTestResult", back_populates="survey", cascade="all, delete-orphan"
    )
    report_signatures: Mapped[list[ReportSignature]] = relationship(
        "ReportSignature", back_populates="survey", cascade="all, delete-orphan"
    )
    test_images: Mapped[list[TestImage]] = relationship(
        "TestImage", back_populates="survey", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Survey id={self.id} address={self.address}>"
