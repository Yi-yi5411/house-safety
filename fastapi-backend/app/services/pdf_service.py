"""PDF generation service for reports and original records.

Uses fpdf2 for pure Python PDF generation with Chinese text support.
"""

from __future__ import annotations

import uuid
from io import BytesIO

from fpdf import FPDF
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.report_service import get_full_report_data, _sort_components, _group_by_category
from app.services.original_record_service import get_original_record_data
from app.models.survey import Survey
from app.models.component_check import ComponentCheck
from app.models.structural_test_result import StructuralTestResult


class ChinesePDF(FPDF):
    """PDF class with Chinese font support."""

    def __init__(self):
        super().__init__()
        self.add_font("cjk", "", "Helvetica", uni=True)  # fallback
        # Try to use a CJK font if available
        self._has_cjk = False

    def setup_fonts(self) -> None:
        """Try to register CJK-capable fonts."""
        import os
        # Common CJK font paths on different systems
        cjk_fonts = [
            # Windows
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            # Linux/Docker
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
            # macOS
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
        ]
        for font_path in cjk_fonts:
            if os.path.exists(font_path):
                try:
                    self.add_font("cjk", "", font_path, uni=True)
                    self.add_font("cjk", "B", font_path, uni=True)
                    self._has_cjk = True
                    return
                except Exception:
                    continue

    def _use_font(self, bold: bool = False):
        """Select appropriate font for current text."""
        if self._has_cjk:
            self.set_font("cjk", "B" if bold else "", size=10)
        else:
            self.set_font("Helvetica", "B" if bold else "", size=10)

    def cjk_cell(self, w, h, text, bold=False, align="L", border=0):
        """Output a cell with CJK text."""
        self._use_font(bold)
        self.cell(w, h, text, border=border, align=align)

    def cjk_multi_cell(self, w, h, text, bold=False, align="L"):
        """Output multi-cell with CJK text."""
        self._use_font(bold)
        self.multi_cell(w, h, text, align=align)


async def generate_report_pdf(survey_id: uuid.UUID, db: AsyncSession) -> BytesIO:
    """Generate a PDF report for a survey."""
    data = await get_full_report_data(survey_id, db)

    survey: Survey = data["survey"]
    components: list[ComponentCheck] = data["components"]
    structural_tests: list[StructuralTestResult] = data["structural_tests"]

    sorted_components = _sort_components(components)
    ai = survey.ai_reasoning_result or {}
    if not isinstance(ai, dict):
        ai = {}

    pdf = ChinesePDF()
    pdf.setup_fonts()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ---- Title ----
    pdf.cjk_cell(0, 12, "房屋安全鉴定报告", bold=True, align="C")
    pdf.ln(8)

    # ---- Survey Info ----
    pdf.cjk_cell(0, 8, f"鉴定编号：{survey.survey_no or ''}", align="C")
    pdf.ln(6)
    pdf.cjk_cell(0, 8, f"房屋地址：{survey.address or ''}", align="C")
    pdf.ln(10)

    # ---- Basic Info Section ----
    pdf.cjk_cell(0, 8, "一、房屋基本信息", bold=True)
    pdf.ln(8)

    info_items = [
        ("结构类型", survey.structure_type),
        ("建造年份", survey.build_year),
        ("层数", str(survey.floor_count) if survey.floor_count else ""),
        ("建筑面积", f"{survey.build_area}㎡" if survey.build_area else ""),
        ("鉴定类别", survey.survey_category or "整幢鉴定"),
        ("产权人", survey.property_owner),
        ("使用人", survey.property_user),
        ("委托人", survey.client_name),
        ("联系电话", survey.contact_phone),
    ]
    for label, value in info_items:
        if value:
            pdf.cjk_cell(0, 7, f"  {label}：{value}")
            pdf.ln(6)
    pdf.ln(4)

    # ---- Conclusion ----
    pdf.cjk_cell(0, 8, "二、鉴定结论", bold=True)
    pdf.ln(8)
    pdf.cjk_cell(0, 7, f"  鉴定结论：{ai.get('conclusion', '')}")
    pdf.ln(6)
    pdf.cjk_cell(0, 7, f"  基础评定：{ai.get('basicEvaluation', '')}")
    pdf.ln(6)
    pdf.cjk_cell(0, 7, f"  风险等级：{ai.get('riskLevel', '')}")
    pdf.ln(6)
    pdf.cjk_cell(0, 7, f"  处理建议：{ai.get('suggestion', '')}")
    pdf.ln(10)

    # ---- Component Summary ----
    pdf.cjk_cell(0, 8, "三、构件检查统计", bold=True)
    pdf.ln(8)

    grouped = _group_by_category(sorted_components)
    categories = ["地基基础", "上部承重结构", "围护结构", "其他"]
    for cat in categories:
        checks = grouped.get(cat, [])
        pdf.cjk_cell(0, 7, f"  {cat}：{len(checks)}个构件")
        pdf.ln(6)
    pdf.ln(4)

    # ---- Component Details ----
    pdf.cjk_cell(0, 8, "四、构件检查明细", bold=True)
    pdf.ln(8)

    for comp in sorted_components[:50]:  # Limit to 50 items
        pdf.cjk_cell(0, 6, f"  · {comp.name}（{comp.category}）")
        pdf.ln(5)
        if comp.damage_description:
            pdf.cjk_multi_cell(0, 5, f"    损坏描述：{comp.damage_description}")
        if comp.ai_evaluation_result:
            pdf.cjk_cell(0, 5, f"    评定结果：{comp.ai_evaluation_result}")
            pdf.ln(5)
        if comp.photos:
            pdf.cjk_cell(0, 5, f"    照片：{len(comp.photos)}张")
            pdf.ln(5)
        pdf.ln(2)

    # ---- Structural Test Results ----
    if structural_tests:
        pdf.add_page()
        pdf.cjk_cell(0, 8, "五、结构检测结果", bold=True)
        pdf.ln(8)
        for test in structural_tests:
            test_items = [
                ("检测单位", test.test_unit),
                ("资质证书号", test.certificate_no),
                ("检测人员", test.test_personnel),
                ("报告编号", test.report_no),
                ("主要检测内容", test.main_test_content),
                ("检测标准", test.test_standards),
                ("检测结果综述", test.test_results_summary),
                ("损伤综述", test.damage_summary),
                ("原因分析", test.cause_analysis),
                ("结论", test.conclusion),
                ("处理建议", test.handling_suggestion),
                ("安全等级", f"{test.safety_level}级" if test.safety_level else None),
            ]
            for label, value in test_items:
                if value:
                    pdf.cjk_cell(0, 6, f"  {label}：{value[:120]}")
                    pdf.ln(5)
            pdf.ln(4)

    # ---- Footer ----
    pdf.ln(10)
    pdf.cjk_cell(0, 8, "湖北省建筑工程质量监督检验测试中心有限公司", align="C")
    pdf.ln(6)
    pdf.cjk_cell(0, 6, "（房屋安全鉴定报告）", align="C")

    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf


async def generate_original_record_pdf(survey_id: uuid.UUID, db: AsyncSession) -> BytesIO:
    """Generate a PDF original record for a survey."""
    data = await get_original_record_data(survey_id, db)

    survey: Survey = data["survey"]
    components: list[ComponentCheck] = data["components"]
    tests: list[StructuralTestResult] = data["structural_tests"]

    ai = survey.ai_reasoning_result or {}
    if not isinstance(ai, dict):
        ai = {}

    pdf = ChinesePDF()
    pdf.setup_fonts()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ---- Title ----
    pdf.cjk_cell(0, 12, "房屋安全鉴定原始记录", bold=True, align="C")
    pdf.ln(8)
    pdf.cjk_cell(0, 8, f"记录编号：{survey.survey_no or ''}", align="C")
    pdf.ln(10)

    # ---- Building Info ----
    pdf.cjk_cell(0, 8, "一、房屋基本信息", bold=True)
    pdf.ln(8)
    info_items = [
        ("房屋地址", survey.address),
        ("结构类型", survey.structure_type),
        ("建造年份", survey.build_year),
        ("层数", str(survey.floor_count) if survey.floor_count else ""),
        ("建筑面积", f"{survey.build_area}㎡" if survey.build_area else ""),
        ("鉴定类别", survey.survey_category or "整幢鉴定"),
        ("委托人", survey.client_name),
        ("联系电话", survey.contact_phone),
        ("产权人", survey.property_owner),
        ("使用人", survey.property_user),
    ]
    for label, value in info_items:
        if value:
            pdf.cjk_cell(0, 7, f"  {label}：{value}")
            pdf.ln(6)
    pdf.ln(4)

    # ---- AI Results ----
    if ai:
        pdf.cjk_cell(0, 8, "二、AI推理结果", bold=True)
        pdf.ln(8)
        ai_items = [
            ("鉴定结论", ai.get("conclusion")),
            ("基础评定", ai.get("basicEvaluation")),
            ("风险等级", ai.get("riskLevel")),
            ("建议", ai.get("suggestion")),
        ]
        for label, value in ai_items:
            if value:
                pdf.cjk_cell(0, 7, f"  {label}：{value}")
                pdf.ln(6)
        pdf.ln(4)

    # ---- Component Checks ----
    heading_num = "三" if ai else "二"
    pdf.cjk_cell(0, 8, f"{heading_num}、构件检查记录", bold=True)
    pdf.ln(8)

    for idx, comp in enumerate(components):
        pdf.cjk_cell(0, 6, f"  {idx + 1}. {comp.name}（{comp.category}）")
        pdf.ln(5)
        if comp.axis_line:
            pdf.cjk_cell(0, 5, f"     部位：{comp.axis_line}")
            pdf.ln(5)
        if comp.damage_description:
            pdf.cjk_multi_cell(0, 5, f"     损坏描述：{comp.damage_description[:200]}")
        if comp.ai_evaluation_result:
            pdf.cjk_cell(0, 5, f"     评定结果：{comp.ai_evaluation_result}")
            pdf.ln(5)
        if comp.photos:
            pdf.cjk_cell(0, 5, f"     照片：{len(comp.photos)}张")
            pdf.ln(5)
        pdf.ln(2)

    # ---- Structural Test Results ----
    if tests:
        pdf.add_page()
        pdf.cjk_cell(0, 8, "结构检测结果", bold=True)
        pdf.ln(8)
        for test in tests:
            test_items = [
                ("检测单位", test.test_unit),
                ("检测报告编号", test.report_no),
                ("主要检测内容", test.main_test_content),
                ("检测结果综述", test.test_results_summary),
            ]
            for label, value in test_items:
                if value:
                    pdf.cjk_multi_cell(0, 5, f"  {label}：{value[:200]}")
                    pdf.ln(2)
            pdf.ln(4)

    # ---- Footer ----
    pdf.ln(10)
    pdf.cjk_cell(0, 8, f"鉴定单位：湖北省建筑工程质量监督检验测试中心有限公司")
    pdf.ln(6)

    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf
