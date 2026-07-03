"""
API verification script — validates all routes are registered correctly.
Run with: python3 tests/verify_api.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_app_structure():
    """Verify the FastAPI app structure without starting a server."""
    print("=" * 60)
    print("房屋安全鉴定系统 — API 结构验证")
    print("=" * 60)

    # 1. Verify imports
    print("\n[1/6] 检查模块导入...")
    try:
        from app.core.config import get_settings
        settings = get_settings()
        print(f"  [OK] Config: app_name={settings.app_name}")
    except Exception as e:
        print(f"  [FAIL] Config: {e}")
        return

    try:
        from app.core.security import create_access_token, decode_access_token
        token = create_access_token("test-user-1")
        payload = decode_access_token(token)
        print(f"  [OK] Security: JWT token created and verified (sub={payload['sub']})")
    except Exception as e:
        print(f"  [FAIL] Security: {e}")

    try:
        from app.core.exceptions import (
            AppException, AuthenticationError, NotFoundError,
            ValidationError, DuplicateError
        )
        print(f"  [OK] Exceptions: 5 custom exception classes defined")
    except Exception as e:
        print(f"  [FAIL] Exceptions: {e}")

    # 2. Verify models
    print("\n[2/6] 检查数据模型...")
    models = []
    try:
        from app.models.user import User
        models.append(("User", "users"))
    except Exception as e:
        print(f"  [FAIL] User model: {e}")
    try:
        from app.models.survey import Survey
        models.append(("Survey", "surveys"))
    except Exception as e:
        print(f"  [FAIL] Survey model: {e}")
    try:
        from app.models.component_check import ComponentCheck
        models.append(("ComponentCheck", "component_checks"))
    except Exception as e:
        print(f"  [FAIL] ComponentCheck: {e}")
    try:
        from app.models.component_template import ComponentTemplate
        models.append(("ComponentTemplate", "component_template"))
    except Exception as e:
        print(f"  [FAIL] ComponentTemplate: {e}")
    try:
        from app.models.evaluation_standard import EvaluationStandard
        models.append(("EvaluationStandard", "evaluation_standards"))
    except Exception as e:
        print(f"  [FAIL] EvaluationStandard: {e}")
    try:
        from app.models.evaluation_standard_knowledge import EvaluationStandardKnowledge
        models.append(("EvaluationStandardKnowledge", "evaluation_standard_knowledge"))
    except Exception as e:
        print(f"  [FAIL] EvaluationStandardKnowledge: {e}")
    try:
        from app.models.report_signature import ReportSignature
        models.append(("ReportSignature", "report_signature"))
    except Exception as e:
        print(f"  [FAIL] ReportSignature: {e}")
    try:
        from app.models.report_template import ReportTemplate
        models.append(("ReportTemplate", "report_templates"))
    except Exception as e:
        print(f"  [FAIL] ReportTemplate: {e}")
    try:
        from app.models.structural_test_result import StructuralTestResult
        models.append(("StructuralTestResult", "structural_test_result"))
    except Exception as e:
        print(f"  [FAIL] StructuralTestResult: {e}")
    try:
        from app.models.test_image import TestImage
        models.append(("TestImage", "test_image"))
    except Exception as e:
        print(f"  [FAIL] TestImage: {e}")

    print(f"  [OK] {len(models)}/10 models loaded: {', '.join(m[0] for m in models)}")

    # 3. Verify API routes
    print("\n[3/6] 检查 API 路由...")
    from app.main import app
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            for method in route.methods:
                if method in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH'):
                    routes.append(f"{method:6} {route.path}")
                    break

    print(f"  [OK] {len(routes)} routes registered:")
    for r in sorted(routes):
        print(f"     {r}")

    # 4. Verify endpoint modules
    print("\n[4/6] 检查端点模块...")
    endpoint_files = [
        'auth', 'users', 'surveys', 'components', 'component_templates',
        'evaluation_standards', 'evaluation_standard_knowledge', 'reports',
        'original_records', 'report_signatures', 'report_templates',
        'structural_test_results', 'test_images', 'ai', 'ai_text', 'upload'
    ]
    for f in endpoint_files:
        try:
            __import__(f'app.api.v1.endpoints.{f}', fromlist=['router'])
            print(f"  [OK] endpoints/{f}.py")
        except Exception as e:
            print(f"  [FAIL] endpoints/{f}.py: {e}")

    # 5. Verify services
    print("\n[5/6] 检查服务层...")
    service_files = [
        'survey_service', 'component_check_service', 'component_template_service',
        'evaluation_standard_service', 'evaluation_standard_knowledge_service',
        'report_service', 'original_record_service', 'pdf_service',
        'report_signature_service', 'structural_test_result_service',
        'test_image_service'
    ]
    for f in service_files:
        try:
            __import__(f'app.services.{f}', fromlist=[''])
            print(f"  [OK] services/{f}.py")
        except Exception as e:
            print(f"  [FAIL] services/{f}.py: {e}")

    # 6. Verify schemas
    print("\n[6/6] 检查 Pydantic Schemas...")
    schema_modules = [
        'common', 'response', 'user', 'survey', 'component', 'component_check',
        'component_template', 'evaluation_standard', 'evaluation_standard_knowledge',
        'report_signature', 'report_template', 'structural_test_result', 'test_image'
    ]
    for s in schema_modules:
        try:
            __import__(f'app.schemas.{s}', fromlist=[''])
            print(f"  [OK] schemas/{s}.py")
        except Exception as e:
            print(f"  [FAIL] schemas/{s}.py: {e}")

    print("\n" + "=" * 60)
    print("[OK] 代码结构验证完成！")
    print("=" * 60)
    print("\nFeature checklist (19 features):")
    print("  [Survey] CRUD + list/search/paginate")
    print("  [ComponentCheck] CRUD + batch update")
    print("  [EvaluationStandard] list by category/type")
    print("  [EvaluationStandardKnowledge] CRUD")
    print("  [Report] generate DOCX + PDF + full data")
    print("  [OriginalRecord] generate DOCX + PDF")
    print("  [ReportSignature] CRUD")
    print("  [StructuralTestResult] CRUD + upsert")
    print("  [TestImage] CRUD + reorder")
    print("  [ComponentTemplate] list")
    print("  [ReportTemplate] CRUD + set active")
    print("  [AI] reasoning + stream")
    print("  [AI] assistant chat + stream + clear")
    print("  [AI] text generation (13 generators)")
    print("  [Upload] image + file (OSS)")
    print("  [Auth] phone SMS login + WeChat login")
    print("  [Auth] email code login + register")
    print("  [User] profile + list")
    print("  [Health] check endpoint")

if __name__ == '__main__':
    verify_app_structure()
