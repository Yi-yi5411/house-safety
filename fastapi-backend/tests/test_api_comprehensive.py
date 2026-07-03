"""
Comprehensive API functional test script.
Tests all endpoints of the running FastAPI server at http://localhost:8000.
Uses httpx for async HTTP requests.
"""
import sys
import os
import json
import uuid
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

BASE_URL = "http://localhost:8000"
API_PREFIX = f"{BASE_URL}/api/v1"

# Results tracking
results = []


def record(name: str, passed: bool, detail: str = ""):
    status = "PASS" if passed else "FAIL"
    results.append((name, passed, detail))
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))


# ============================================================
# 1. Health Check
# ============================================================
async def test_health():
    print("\n" + "=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(f"{BASE_URL}/health")
            record("/health", r.status_code == 200, f"status={r.status_code}, body={r.json()}")
        except Exception as e:
            record("/health", False, str(e))


# ============================================================
# 2. OpenAPI Docs
# ============================================================
async def test_docs():
    print("\n" + "=" * 60)
    print("TEST 2: API Documentation")
    print("=" * 60)
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(f"{BASE_URL}/docs")
            record("/docs", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("/docs", False, str(e))

        try:
            r = await client.get(f"{BASE_URL}/openapi.json")
            openapi = r.json()
            paths = list(openapi.get("paths", {}).keys())
            record("/openapi.json", r.status_code == 200, f"{len(paths)} paths registered")
        except Exception as e:
            record("/openapi.json", False, str(e))


# ============================================================
# 3. Auth Endpoints (without real SMS/Email — test error handling)
# ============================================================
async def test_auth():
    print("\n" + "=" * 60)
    print("TEST 3: Auth Endpoints")
    print("=" * 60)
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test email send — will fail due to SMTP config, but endpoint exists
        try:
            r = await client.post(f"{API_PREFIX}/auth/email/send", json={"email": "test@example.com"})
            # 200 = success, 500 = SMTP error (expected with dummy config)
            record("POST /auth/email/send", r.status_code in (200, 500), f"status={r.status_code}")
        except Exception as e:
            record("POST /auth/email/send", False, str(e))

        # Test phone send — will fail due to SMS config
        try:
            r = await client.post(f"{API_PREFIX}/auth/phone/send", json={"phone": "13800138000"})
            record("POST /auth/phone/send", r.status_code in (200, 500), f"status={r.status_code}")
        except Exception as e:
            record("POST /auth/phone/send", False, str(e))

        # Test login with invalid code
        try:
            r = await client.post(f"{API_PREFIX}/auth/login/phone", json={"phone": "13800138000", "code": "000000"})
            record("POST /auth/login/phone (invalid code)", r.status_code == 401, f"status={r.status_code}")
        except Exception as e:
            record("POST /auth/login/phone (invalid code)", False, str(e))

        # Test email login with invalid code
        try:
            r = await client.post(f"{API_PREFIX}/auth/login/email", json={"email": "test@example.com", "code": "000000"})
            record("POST /auth/login/email (invalid code)", r.status_code == 401, f"status={r.status_code}")
        except Exception as e:
            record("POST /auth/login/email (invalid code)", False, str(e))

        # Test /auth/me without token
        try:
            r = await client.get(f"{API_PREFIX}/auth/me")
            record("GET /auth/me (no token)", r.status_code in (401, 403), f"status={r.status_code}")
        except Exception as e:
            record("GET /auth/me (no token)", False, str(e))

        # Test wechat login with invalid code
        try:
            r = await client.post(f"{API_PREFIX}/auth/wechat/login", json={"code": "invalid-code"})
            record("POST /auth/wechat/login (invalid code)", r.status_code in (401, 500), f"status={r.status_code}")
        except Exception as e:
            record("POST /auth/wechat/login (invalid code)", False, str(e))


# ============================================================
# 4. Generate a valid JWT token for authenticated tests
# ============================================================
async def get_auth_token():
    """Generate a JWT token directly using the security module."""
    from app.core.security import create_access_token
    # Use user_id=1 as a test user (may not exist in DB, but token will be valid)
    token = create_access_token(subject="1")
    return token


# ============================================================
# 5. Survey CRUD
# ============================================================
async def test_surveys(token: str):
    print("\n" + "=" * 60)
    print("TEST 5: Survey CRUD")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # List surveys
        try:
            r = await client.get(f"{API_PREFIX}/surveys/", headers=headers)
            record("GET /surveys/", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /surveys/", False, str(e))

        # Create survey
        survey_id = None
        try:
            r = await client.post(f"{API_PREFIX}/surveys/", headers=headers, json={
                "address": "测试地址-武汉市洪山区",
                "structure_type": "砖混结构",
                "build_year": "2000年",
                "floor_count": 6,
                "build_area": 3000.50,
            })
            if r.status_code == 201:
                survey_id = r.json().get("id")
                record("POST /surveys/", True, f"created survey_id={survey_id}")
            else:
                record("POST /surveys/", False, f"status={r.status_code}, body={r.text[:200]}")
        except Exception as e:
            record("POST /surveys/", False, str(e))

        if not survey_id:
            print("  [SKIP] Remaining survey tests skipped (no survey_id)")
            return None

        # Get survey
        try:
            r = await client.get(f"{API_PREFIX}/surveys/{survey_id}", headers=headers)
            record("GET /surveys/{id}", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /surveys/{id}", False, str(e))

        # Update survey
        try:
            r = await client.put(f"{API_PREFIX}/surveys/{survey_id}", headers=headers, json={
                "address": "更新后地址-武汉市武昌区",
                "conclusion": "B级",
            })
            record("PUT /surveys/{id}", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("PUT /surveys/{id}", False, str(e))

        # List with filter
        try:
            r = await client.get(f"{API_PREFIX}/surveys/?keyword=武汉", headers=headers)
            record("GET /surveys/?keyword=武汉", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /surveys/?keyword=武汉", False, str(e))

        # Generate report
        try:
            r = await client.post(f"{API_PREFIX}/surveys/{survey_id}/generate-report", headers=headers)
            record("POST /surveys/{id}/generate-report", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("POST /surveys/{id}/generate-report", False, str(e))

        # Generate original record
        try:
            r = await client.post(f"{API_PREFIX}/surveys/{survey_id}/generate-original-record", headers=headers)
            record("POST /surveys/{id}/generate-original-record", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("POST /surveys/{id}/generate-original-record", False, str(e))

        # Delete survey (soft delete)
        try:
            r = await client.delete(f"{API_PREFIX}/surveys/{survey_id}", headers=headers)
            record("DELETE /surveys/{id}", r.status_code in (200, 204), f"status={r.status_code}")
        except Exception as e:
            record("DELETE /surveys/{id}", False, str(e))

        return survey_id


# ============================================================
# 6. Component Check CRUD
# ============================================================
async def test_components(token: str, survey_id: str | None):
    print("\n" + "=" * 60)
    print("TEST 6: Component Check CRUD")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # List components
        try:
            r = await client.get(f"{API_PREFIX}/components/", headers=headers)
            record("GET /components/", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /components/", False, str(e))

        # Create component
        component_id = None
        if survey_id:
            try:
                r = await client.post(f"{API_PREFIX}/components/", headers=headers, json={
                    "survey_id": survey_id,
                    "name": "砖墙",
                    "category": "上部承重结构",
                    "damage_level": "moderate",
                    "damage_description": "墙体出现竖向裂缝",
                })
                if r.status_code == 201:
                    component_id = r.json().get("id")
                    record("POST /components/", True, f"created id={component_id}")
                else:
                    record("POST /components/", False, f"status={r.status_code}, body={r.text[:200]}")
            except Exception as e:
                record("POST /components/", False, str(e))

            # Get component
            if component_id:
                try:
                    r = await client.get(f"{API_PREFIX}/components/{component_id}", headers=headers)
                    record("GET /components/{id}", r.status_code == 200, f"status={r.status_code}")
                except Exception as e:
                    record("GET /components/{id}", False, str(e))

                # Update component
                try:
                    r = await client.put(f"{API_PREFIX}/components/{component_id}", headers=headers, json={
                        "damage_level": "severe",
                        "damage_description": "裂缝扩展至3mm",
                    })
                    record("PUT /components/{id}", r.status_code == 200, f"status={r.status_code}")
                except Exception as e:
                    record("PUT /components/{id}", False, str(e))

                # Batch update
                try:
                    r = await client.put(f"{API_PREFIX}/components/batch", headers=headers, json={
                        "items": [{"id": component_id, "damage_description": "批量更新描述"}]
                    })
                    record("PUT /components/batch", r.status_code == 200, f"status={r.status_code}")
                except Exception as e:
                    record("PUT /components/batch", False, str(e))

                # Delete component
                try:
                    r = await client.delete(f"{API_PREFIX}/components/{component_id}", headers=headers)
                    record("DELETE /components/{id}", r.status_code in (200, 204), f"status={r.status_code}")
                except Exception as e:
                    record("DELETE /components/{id}", False, str(e))

        # List by survey_id
        if survey_id:
            try:
                r = await client.get(f"{API_PREFIX}/components/?survey_id={survey_id}", headers=headers)
                record("GET /components/?survey_id=...", r.status_code == 200, f"status={r.status_code}")
            except Exception as e:
                record("GET /components/?survey_id=...", False, str(e))


# ============================================================
# 7. Evaluation Standards
# ============================================================
async def test_evaluation_standards(token: str):
    print("\n" + "=" * 60)
    print("TEST 7: Evaluation Standards")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # List standards (dedicated endpoint)
        try:
            r = await client.get(f"{API_PREFIX}/evaluation-standards/", headers=headers)
            record("GET /evaluation-standards/", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /evaluation-standards/", False, str(e))

        # List with category filter
        try:
            r = await client.get(f"{API_PREFIX}/evaluation-standards/?category=地基基础", headers=headers)
            record("GET /evaluation-standards/?category=地基基础", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /evaluation-standards/?category=地基基础", False, str(e))

        # List standards via components router
        try:
            r = await client.get(f"{API_PREFIX}/components/standards", headers=headers)
            record("GET /components/standards", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /components/standards", False, str(e))

        # Create standard
        standard_id = None
        try:
            r = await client.post(f"{API_PREFIX}/components/standards", headers=headers, json={
                "category": "地基基础",
                "component_type": "地基",
                "name": "地基承载力检测",
                "description": "检测地基承载力是否满足设计要求",
                "clause": "GB 50007-2011",
                "sort_order": 1,
            })
            if r.status_code == 201:
                standard_id = r.json().get("id")
                record("POST /components/standards", True, f"created id={standard_id}")
            else:
                record("POST /components/standards", False, f"status={r.status_code}, body={r.text[:200]}")
        except Exception as e:
            record("POST /components/standards", False, str(e))

        # Update standard
        if standard_id:
            try:
                r = await client.put(f"{API_PREFIX}/components/standards/{standard_id}", headers=headers, json={
                    "description": "更新后的描述",
                })
                record("PUT /components/standards/{id}", r.status_code == 200, f"status={r.status_code}")
            except Exception as e:
                record("PUT /components/standards/{id}", False, str(e))

            # Delete standard
            try:
                r = await client.delete(f"{API_PREFIX}/components/standards/{standard_id}", headers=headers)
                record("DELETE /components/standards/{id}", r.status_code in (200, 204), f"status={r.status_code}")
            except Exception as e:
                record("DELETE /components/standards/{id}", False, str(e))


# ============================================================
# 8. Evaluation Standard Knowledge
# ============================================================
async def test_evaluation_standard_knowledge(token: str):
    print("\n" + "=" * 60)
    print("TEST 8: Evaluation Standard Knowledge")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # List
        try:
            r = await client.get(f"{API_PREFIX}/evaluation-standard-knowledge/", headers=headers)
            record("GET /evaluation-standard-knowledge/", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /evaluation-standard-knowledge/", False, str(e))

        # Create
        knowledge_id = None
        try:
            r = await client.post(f"{API_PREFIX}/evaluation-standard-knowledge/", headers=headers, json={
                "name": "JGJ 125-2016",
                "description": "危险房屋鉴定标准",
                "content": "本标准适用于既有房屋的危险性鉴定...",
                "category": "国家标准",
            })
            if r.status_code == 201:
                knowledge_id = r.json().get("id")
                record("POST /evaluation-standard-knowledge/", True, f"created id={knowledge_id}")
            else:
                record("POST /evaluation-standard-knowledge/", False, f"status={r.status_code}, body={r.text[:200]}")
        except Exception as e:
            record("POST /evaluation-standard-knowledge/", False, str(e))

        # Get by ID
        if knowledge_id:
            try:
                r = await client.get(f"{API_PREFIX}/evaluation-standard-knowledge/{knowledge_id}", headers=headers)
                record("GET /evaluation-standard-knowledge/{id}", r.status_code == 200, f"status={r.status_code}")
            except Exception as e:
                record("GET /evaluation-standard-knowledge/{id}", False, str(e))

            # Update
            try:
                r = await client.put(f"{API_PREFIX}/evaluation-standard-knowledge/{knowledge_id}", headers=headers, json={
                    "description": "更新后的描述",
                })
                record("PUT /evaluation-standard-knowledge/{id}", r.status_code == 200, f"status={r.status_code}")
            except Exception as e:
                record("PUT /evaluation-standard-knowledge/{id}", False, str(e))

            # Delete
            try:
                r = await client.delete(f"{API_PREFIX}/evaluation-standard-knowledge/{knowledge_id}", headers=headers)
                record("DELETE /evaluation-standard-knowledge/{id}", r.status_code in (200, 204), f"status={r.status_code}")
            except Exception as e:
                record("DELETE /evaluation-standard-knowledge/{id}", False, str(e))


# ============================================================
# 9. Component Templates
# ============================================================
async def test_component_templates(token: str):
    print("\n" + "=" * 60)
    print("TEST 9: Component Templates")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(f"{API_PREFIX}/component-templates/", headers=headers)
            record("GET /component-templates/", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /component-templates/", False, str(e))


# ============================================================
# 10. Report Templates
# ============================================================
async def test_report_templates(token: str):
    print("\n" + "=" * 60)
    print("TEST 10: Report Templates")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # List
        try:
            r = await client.get(f"{API_PREFIX}/report-templates/", headers=headers)
            record("GET /report-templates/", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /report-templates/", False, str(e))

        # Get active (may 404 if none)
        try:
            r = await client.get(f"{API_PREFIX}/report-templates/active", headers=headers)
            record("GET /report-templates/active", r.status_code in (200, 404), f"status={r.status_code}")
        except Exception as e:
            record("GET /report-templates/active", False, str(e))

        # Create template
        template_id = None
        try:
            r = await client.post(f"{API_PREFIX}/report-templates/", headers=headers, json={
                "name": "测试报告模板",
                "content": json.dumps({"title": "模板标题", "sections": []}),
                "is_active": True,
            })
            if r.status_code == 201:
                template_id = r.json().get("id")
                record("POST /report-templates/", True, f"created id={template_id}")
            else:
                record("POST /report-templates/", False, f"status={r.status_code}, body={r.text[:200]}")
        except Exception as e:
            record("POST /report-templates/", False, str(e))

        # Set active
        if template_id:
            try:
                r = await client.put(f"{API_PREFIX}/report-templates/{template_id}/active", headers=headers)
                record("PUT /report-templates/{id}/active", r.status_code == 200, f"status={r.status_code}")
            except Exception as e:
                record("PUT /report-templates/{id}/active", False, str(e))

            # Delete
            try:
                r = await client.delete(f"{API_PREFIX}/report-templates/{template_id}", headers=headers)
                record("DELETE /report-templates/{id}", r.status_code in (200, 204), f"status={r.status_code}")
            except Exception as e:
                record("DELETE /report-templates/{id}", False, str(e))


# ============================================================
# 11. Reports
# ============================================================
async def test_reports(token: str, survey_id: str | None):
    print("\n" + "=" * 60)
    print("TEST 11: Reports")
    print("=" * 60)
    if not survey_id:
        print("  [SKIP] No survey_id available")
        return

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get report
        try:
            r = await client.get(f"{API_PREFIX}/reports/{survey_id}", headers=headers)
            record("GET /reports/{survey_id}", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /reports/{survey_id}", False, str(e))

        # Get full data
        try:
            r = await client.get(f"{API_PREFIX}/reports/{survey_id}/full-data", headers=headers)
            record("GET /reports/{survey_id}/full-data", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /reports/{survey_id}/full-data", False, str(e))

        # Export DOCX
        try:
            r = await client.get(f"{API_PREFIX}/reports/{survey_id}/export", headers=headers)
            record("GET /reports/{survey_id}/export (DOCX)", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /reports/{survey_id}/export (DOCX)", False, str(e))

        # Export PDF
        try:
            r = await client.get(f"{API_PREFIX}/reports/{survey_id}/export/pdf", headers=headers)
            record("GET /reports/{survey_id}/export/pdf", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /reports/{survey_id}/export/pdf", False, str(e))


# ============================================================
# 12. Original Records
# ============================================================
async def test_original_records(token: str, survey_id: str | None):
    print("\n" + "=" * 60)
    print("TEST 12: Original Records")
    print("=" * 60)
    if not survey_id:
        print("  [SKIP] No survey_id available")
        return

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.get(f"{API_PREFIX}/original-records/{survey_id}", headers=headers)
            record("GET /original-records/{survey_id}", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /original-records/{survey_id}", False, str(e))

        try:
            r = await client.get(f"{API_PREFIX}/original-records/{survey_id}/export", headers=headers)
            record("GET /original-records/{survey_id}/export (DOCX)", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /original-records/{survey_id}/export (DOCX)", False, str(e))

        try:
            r = await client.get(f"{API_PREFIX}/original-records/{survey_id}/export/pdf", headers=headers)
            record("GET /original-records/{survey_id}/export/pdf", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /original-records/{survey_id}/export/pdf", False, str(e))


# ============================================================
# 13. Report Signatures
# ============================================================
async def test_report_signatures(token: str, survey_id: str | None):
    print("\n" + "=" * 60)
    print("TEST 13: Report Signatures")
    print("=" * 60)
    if not survey_id:
        print("  [SKIP] No survey_id available")
        return

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # List signatures
        try:
            r = await client.get(f"{API_PREFIX}/surveys/{survey_id}/signatures", headers=headers)
            record("GET /surveys/{id}/signatures", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /surveys/{id}/signatures", False, str(e))

        # Create signature
        sig_id = None
        try:
            r = await client.post(f"{API_PREFIX}/surveys/{survey_id}/signatures", headers=headers, json={
                "role": "鉴定负责人",
                "name": "张三",
                "certificate_no": "CERT-001",
            })
            if r.status_code == 201:
                sig_id = r.json().get("id")
                record("POST /surveys/{id}/signatures", True, f"created id={sig_id}")
            else:
                record("POST /surveys/{id}/signatures", False, f"status={r.status_code}, body={r.text[:200]}")
        except Exception as e:
            record("POST /surveys/{id}/signatures", False, str(e))

        # Update signature
        if sig_id:
            try:
                r = await client.put(f"{API_PREFIX}/surveys/{survey_id}/signatures/{sig_id}", headers=headers, json={
                    "name": "李四",
                })
                record("PUT /surveys/{id}/signatures/{sig_id}", r.status_code == 200, f"status={r.status_code}")
            except Exception as e:
                record("PUT /surveys/{id}/signatures/{sig_id}", False, str(e))

            # Delete signature
            try:
                r = await client.delete(f"{API_PREFIX}/surveys/{survey_id}/signatures/{sig_id}", headers=headers)
                record("DELETE /surveys/{id}/signatures/{sig_id}", r.status_code in (200, 204), f"status={r.status_code}")
            except Exception as e:
                record("DELETE /surveys/{id}/signatures/{sig_id}", False, str(e))


# ============================================================
# 14. Structural Test Results
# ============================================================
async def test_structural_test_results(token: str, survey_id: str | None):
    print("\n" + "=" * 60)
    print("TEST 14: Structural Test Results")
    print("=" * 60)
    if not survey_id:
        print("  [SKIP] No survey_id available")
        return

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # List
        try:
            r = await client.get(f"{API_PREFIX}/surveys/{survey_id}/structural-test-results", headers=headers)
            record("GET /surveys/{id}/structural-test-results", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /surveys/{id}/structural-test-results", False, str(e))

        # Create (upsert)
        result_id = None
        try:
            r = await client.post(f"{API_PREFIX}/surveys/{survey_id}/structural-test-results", headers=headers, json={
                "concrete_strength": "C25",
                "steel_type": "HRB400",
                "mortar_strength": "M7.5",
                "brick_strength": "MU10",
            })
            if r.status_code == 201:
                result_id = r.json().get("id")
                record("POST /surveys/{id}/structural-test-results", True, f"created id={result_id}")
            else:
                record("POST /surveys/{id}/structural-test-results", False, f"status={r.status_code}, body={r.text[:200]}")
        except Exception as e:
            record("POST /surveys/{id}/structural-test-results", False, str(e))

        # Update
        if result_id:
            try:
                r = await client.put(f"{API_PREFIX}/surveys/{survey_id}/structural-test-results/{result_id}", headers=headers, json={
                    "concrete_strength": "C30",
                })
                record("PUT /surveys/{id}/structural-test-results/{rid}", r.status_code == 200, f"status={r.status_code}")
            except Exception as e:
                record("PUT /surveys/{id}/structural-test-results/{rid}", False, str(e))

            # Delete
            try:
                r = await client.delete(f"{API_PREFIX}/surveys/{survey_id}/structural-test-results/{result_id}", headers=headers)
                record("DELETE /surveys/{id}/structural-test-results/{rid}", r.status_code in (200, 204), f"status={r.status_code}")
            except Exception as e:
                record("DELETE /surveys/{id}/structural-test-results/{rid}", False, str(e))


# ============================================================
# 15. Test Images
# ============================================================
async def test_test_images(token: str, survey_id: str | None):
    print("\n" + "=" * 60)
    print("TEST 15: Test Images")
    print("=" * 60)
    if not survey_id:
        print("  [SKIP] No survey_id available")
        return

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # List
        try:
            r = await client.get(f"{API_PREFIX}/surveys/{survey_id}/test-images", headers=headers)
            record("GET /surveys/{id}/test-images", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /surveys/{id}/test-images", False, str(e))

        # Create
        image_id = None
        try:
            r = await client.post(f"{API_PREFIX}/surveys/{survey_id}/test-images", headers=headers, json={
                "type": "外观",
                "label": "正面照",
                "image_url": "https://example.com/test.jpg",
                "sort_order": 1,
            })
            if r.status_code == 201:
                image_id = r.json().get("id")
                record("POST /surveys/{id}/test-images", True, f"created id={image_id}")
            else:
                record("POST /surveys/{id}/test-images", False, f"status={r.status_code}, body={r.text[:200]}")
        except Exception as e:
            record("POST /surveys/{id}/test-images", False, str(e))

        # Update
        if image_id:
            try:
                r = await client.put(f"{API_PREFIX}/surveys/{survey_id}/test-images/{image_id}", headers=headers, json={
                    "label": "侧面照",
                })
                record("PUT /surveys/{id}/test-images/{img_id}", r.status_code == 200, f"status={r.status_code}")
            except Exception as e:
                record("PUT /surveys/{id}/test-images/{img_id}", False, str(e))

            # Reorder
            try:
                r = await client.put(f"{API_PREFIX}/surveys/{survey_id}/test-images/reorder", headers=headers, json={
                    "items": [{"id": image_id, "sort_order": 2}]
                })
                record("PUT /surveys/{id}/test-images/reorder", r.status_code == 200, f"status={r.status_code}")
            except Exception as e:
                record("PUT /surveys/{id}/test-images/reorder", False, str(e))

            # Delete
            try:
                r = await client.delete(f"{API_PREFIX}/surveys/{survey_id}/test-images/{image_id}", headers=headers)
                record("DELETE /surveys/{id}/test-images/{img_id}", r.status_code in (200, 204), f"status={r.status_code}")
            except Exception as e:
                record("DELETE /surveys/{id}/test-images/{img_id}", False, str(e))


# ============================================================
# 16. AI Endpoints
# ============================================================
async def test_ai(token: str):
    print("\n" + "=" * 60)
    print("TEST 16: AI Endpoints (assistant chat, no Ollama dependency)")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        # AI assistant chat (doesn't need survey_id)
        try:
            r = await client.post(f"{API_PREFIX}/ai/assistant/chat", headers=headers, json={
                "message": "你好",
                "report_content": "测试报告内容",
            })
            # May fail if Ollama is not running, but endpoint should be reachable
            record("POST /ai/assistant/chat", r.status_code in (200, 500), f"status={r.status_code}")
        except Exception as e:
            record("POST /ai/assistant/chat", False, str(e))

        # AI assistant clear
        try:
            r = await client.post(f"{API_PREFIX}/ai/assistant/clear", headers=headers, json={
                "conversation_id": "test-conv-1",
            })
            record("POST /ai/assistant/clear", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("POST /ai/assistant/clear", False, str(e))

        # AI assistant list conversations
        try:
            r = await client.get(f"{API_PREFIX}/ai/assistant/conversations", headers=headers)
            record("GET /ai/assistant/conversations", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /ai/assistant/conversations", False, str(e))

        # AI reason (needs survey_id — will 404 with fake id)
        try:
            fake_id = str(uuid.uuid4())
            r = await client.post(f"{API_PREFIX}/ai/reason", headers=headers, json={
                "survey_id": fake_id,
            })
            record("POST /ai/reason (fake survey_id)", r.status_code == 404, f"status={r.status_code}")
        except Exception as e:
            record("POST /ai/reason (fake survey_id)", False, str(e))


# ============================================================
# 17. AI Text Generation
# ============================================================
async def test_ai_text(token: str):
    print("\n" + "=" * 60)
    print("TEST 17: AI Text Generation")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        endpoints = [
            ("usage-history", {"historyChange": "无变化", "usageStatus": "正常使用", "purposeInfo": "住宅"}),
            ("external-environment", {"surroundingEnvironment": "市区", "surroundingEnvironmentDesc": "周边环境良好"}),
            ("structure-condition", {"structureInfo": "砖混结构", "basicInfo": "6层住宅"}),
            ("remarks", {}),
            ("damage-summary", {"buildingProfile": {"structureType": "砖混"}, "componentChecks": []}),
            ("cause-analysis", {"buildingProfile": {"structureType": "砖混"}, "componentChecks": []}),
            ("conclusion", {"buildingProfile": {"structureType": "砖混"}, "componentChecks": []}),
            ("handling-suggestion", {"buildingProfile": {"structureType": "砖混"}, "componentChecks": []}),
            ("safety-level", {"buildingProfile": {"structureType": "砖混"}, "componentChecks": []}),
            ("main-test-content", {"buildingProfile": {"structureType": "砖混"}}),
            ("test-standards", {"mainTestContent": "结构检测"}),
            ("test-results", {"buildingProfile": {"structureType": "砖混"}, "mainTestContent": "结构检测", "testStandards": "GB标准", "componentChecks": []}),
            ("report-data", {"type": "usageHistory", "buildingProfile": {"structureType": "砖混"}, "componentChecks": []}),
            ("all-report-text", {"buildingProfile": {"structureType": "砖混"}, "componentChecks": []}),
        ]

        for endpoint, payload in endpoints:
            try:
                r = await client.post(f"{API_PREFIX}/ai/text/{endpoint}", headers=headers, json=payload)
                # 200 = success, 500 = Ollama not available
                record(f"POST /ai/text/{endpoint}", r.status_code in (200, 500), f"status={r.status_code}")
            except Exception as e:
                record(f"POST /ai/text/{endpoint}", False, str(e))


# ============================================================
# 18. Upload (auth required)
# ============================================================
async def test_upload(token: str):
    print("\n" + "=" * 60)
    print("TEST 18: Upload Endpoints")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Upload image without file — should be 422
        try:
            r = await client.post(f"{API_PREFIX}/upload/image", headers=headers)
            record("POST /upload/image (no file)", r.status_code == 422, f"status={r.status_code}")
        except Exception as e:
            record("POST /upload/image (no file)", False, str(e))

        # Upload file without file — should be 422
        try:
            r = await client.post(f"{API_PREFIX}/upload/file", headers=headers)
            record("POST /upload/file (no file)", r.status_code == 422, f"status={r.status_code}")
        except Exception as e:
            record("POST /upload/file (no file)", False, str(e))


# ============================================================
# 19. Users
# ============================================================
async def test_users(token: str):
    print("\n" + "=" * 60)
    print("TEST 19: Users")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        # List users
        try:
            r = await client.get(f"{API_PREFIX}/users/", headers=headers)
            record("GET /users/", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("GET /users/", False, str(e))

        # Get user by ID
        try:
            r = await client.get(f"{API_PREFIX}/users/1", headers=headers)
            record("GET /users/1", r.status_code in (200, 404), f"status={r.status_code}")
        except Exception as e:
            record("GET /users/1", False, str(e))

        # Update profile
        try:
            r = await client.patch(f"{API_PREFIX}/users/me", headers=headers, json={
                "nickname": "测试用户",
            })
            record("PATCH /users/me", r.status_code == 200, f"status={r.status_code}")
        except Exception as e:
            record("PATCH /users/me", False, str(e))


# ============================================================
# 20. Code Structure Verification (import checks)
# ============================================================
async def test_code_structure():
    print("\n" + "=" * 60)
    print("TEST 20: Code Structure Verification")
    print("=" * 60)

    # Config
    try:
        from app.core.config import get_settings
        s = get_settings()
        record("Config module", True, f"app_name={s.app_name}")
    except Exception as e:
        record("Config module", False, str(e))

    # Security
    try:
        from app.core.security import create_access_token, decode_access_token
        token = create_access_token("test-user")
        payload = decode_access_token(token)
        record("Security module", payload.get("sub") == "test-user", f"JWT sub={payload.get('sub')}")
    except Exception as e:
        record("Security module", False, str(e))

    # Exceptions
    try:
        from app.core.exceptions import AppException, AuthenticationError, NotFoundError, ValidationError, DuplicateError
        record("Exceptions module", True, "5 exception classes")
    except Exception as e:
        record("Exceptions module", False, str(e))

    # Models
    model_names = ["User", "Survey", "ComponentCheck", "ComponentTemplate",
                   "EvaluationStandard", "EvaluationStandardKnowledge",
                   "ReportSignature", "ReportTemplate", "StructuralTestResult", "TestImage"]
    model_modules = ["user", "survey", "component_check", "component_template",
                     "evaluation_standard", "evaluation_standard_knowledge",
                     "report_signature", "report_template", "structural_test_result", "test_image"]

    for name, module in zip(model_names, model_modules):
        try:
            mod = __import__(f"app.models.{module}", fromlist=[name])
            cls = getattr(mod, name)
            record(f"Model: {name}", True, f"table={cls.__tablename__}")
        except Exception as e:
            record(f"Model: {name}", False, str(e))

    # Endpoint modules
    endpoint_files = [
        'auth', 'users', 'surveys', 'components', 'component_templates',
        'evaluation_standards', 'evaluation_standard_knowledge', 'reports',
        'original_records', 'report_signatures', 'report_templates',
        'structural_test_results', 'test_images', 'ai', 'ai_text', 'upload'
    ]
    for f in endpoint_files:
        try:
            __import__(f'app.api.v1.endpoints.{f}', fromlist=['router'])
            record(f"Endpoint: {f}", True, "")
        except Exception as e:
            record(f"Endpoint: {f}", False, str(e))

    # Service modules
    service_files = [
        'survey_service', 'component_check_service', 'component_template_service',
        'evaluation_standard_service', 'evaluation_standard_knowledge_service',
        'report_service', 'original_record_service', 'pdf_service',
        'report_signature_service', 'structural_test_result_service', 'test_image_service'
    ]
    for f in service_files:
        try:
            __import__(f'app.services.{f}', fromlist=[''])
            record(f"Service: {f}", True, "")
        except Exception as e:
            record(f"Service: {f}", False, str(e))

    # Schema modules
    schema_modules = [
        'common', 'response', 'user', 'survey', 'component', 'component_check',
        'component_template', 'evaluation_standard', 'evaluation_standard_knowledge',
        'report_signature', 'report_template', 'structural_test_result', 'test_image'
    ]
    for s in schema_modules:
        try:
            __import__(f'app.schemas.{s}', fromlist=[''])
            record(f"Schema: {s}", True, "")
        except Exception as e:
            record(f"Schema: {s}", False, str(e))


# ============================================================
# Main
# ============================================================
async def main():
    print("=" * 60)
    print("房屋安全鉴定系统 — API 功能综合测试")
    print("=" * 60)

    # 1. Health check
    await test_health()

    # 2. Docs
    await test_docs()

    # 3. Auth (error handling)
    await test_auth()

    # 4. Generate token
    token = await get_auth_token()
    print(f"\n  Generated JWT token for authenticated tests")

    # 5. Surveys (create one for subsequent tests)
    # First create a survey to use in other tests
    survey_id = await test_surveys(token)

    # 6. Components
    await test_components(token, survey_id)

    # 7. Evaluation Standards
    await test_evaluation_standards(token)

    # 8. Evaluation Standard Knowledge
    await test_evaluation_standard_knowledge(token)

    # 9. Component Templates
    await test_component_templates(token)

    # 10. Report Templates
    await test_report_templates(token)

    # 11. Reports
    await test_reports(token, survey_id)

    # 12. Original Records
    await test_original_records(token, survey_id)

    # 13. Report Signatures
    await test_report_signatures(token, survey_id)

    # 14. Structural Test Results
    await test_structural_test_results(token, survey_id)

    # 15. Test Images
    await test_test_images(token, survey_id)

    # 16. AI
    await test_ai(token)

    # 17. AI Text
    await test_ai_text(token)

    # 18. Upload
    await test_upload(token)

    # 19. Users
    await test_users(token)

    # 20. Code structure
    await test_code_structure()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, p, _ in results if p)
    failed = sum(1 for _, p, _ in results if not p)
    total = len(results)

    # Group by category
    categories = {}
    for name, p, detail in results:
        if "/" in name:
            cat = name.split("/")[1] if len(name.split("/")) > 1 else name.split("/")[0]
        elif ":" in name:
            cat = name.split(":")[0].strip()
        else:
            cat = "other"
        cat = cat.strip()
        if cat not in categories:
            categories[cat] = {"pass": 0, "fail": 0}
        if p:
            categories[cat]["pass"] += 1
        else:
            categories[cat]["fail"] += 1

    print(f"\n  By category:")
    for cat, counts in categories.items():
        print(f"    {cat}: {counts['pass']} pass, {counts['fail']} fail")

    print(f"\n  TOTAL: {passed}/{total} passed, {failed} failed")

    if failed > 0:
        print(f"\n  Failed tests:")
        for name, p, detail in results:
            if not p:
                print(f"    [FAIL] {name} — {detail}")

    return failed == 0


if __name__ == "__main__":
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output.log")
    with open(log_path, "w", encoding="utf-8") as log_file:
        original_stdout = sys.stdout
        sys.stdout = log_file
        try:
            success = asyncio.run(main())
        finally:
            sys.stdout = original_stdout
    
    # Print summary to stdout
    with open(log_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Print last 30 lines
    lines = content.strip().split("\n")
    for line in lines[-30:]:
        print(line)
    
    sys.exit(0 if success else 1)
