import os
import json
import requests
import urllib3
import pytest
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
API_URL = os.getenv("API_URL", "https://localhost:7000").rstrip("/")
VALID_EMAIL = os.getenv("VALID_EMAIL", "")
VALID_PASSWORD = os.getenv("VALID_PASSWORD", "")
CASES_FILE = ROOT / "tests" / "generated_test_cases.json"
EVIDENCE_DIR = ROOT / "evidence"
FAILURES_FILE = EVIDENCE_DIR / "failures.json"

if not CASES_FILE.exists():
    pytest.skip("Chua co generated_test_cases.json. Hay chay src/generate_tests.py truoc.", allow_module_level=True)

CASES = json.loads(CASES_FILE.read_text(encoding="utf-8"))

KNOWN_TOKENS = ("<VALID_EMAIL>", "<VALID_PASSWORD>")


def resolve(v):
    if isinstance(v, str):
        return v.replace("<VALID_EMAIL>", VALID_EMAIL).replace("<VALID_PASSWORD>", VALID_PASSWORD)
    return v


def has_unknown_token(inp):
    for v in inp.values():
        if isinstance(v, str) and v.startswith("<") and v.endswith(">") and v not in KNOWN_TOKENS:
            return v
    return None


def record_failure(case, status, body, errors):
    EVIDENCE_DIR.mkdir(exist_ok=True)
    data = json.loads(FAILURES_FILE.read_text(encoding="utf-8")) if FAILURES_FILE.exists() else []
    masked = {k: ("***" if k.lower() == "password" else v) for k, v in case["input"].items()}
    data.append({
        "id": case["id"], "title": case["title"], "rationale": case.get("rationale"),
        "input": masked,
        "expected_http_status": case.get("expected_http_status"),
        "expected_error_kind": case.get("expected_error_kind"),
        "expected_message_contains": case.get("expected_message_contains"),
        "actual_http_status": status,
        "actual_body": body,
        "errors": errors,
        "timestamp": datetime.now().isoformat(),
    })
    FAILURES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_login_api_case(case):
    unknown = has_unknown_token(case["input"])
    if unknown:
        pytest.skip(
            f"Bo qua: AI dung token khong xac dinh '{unknown}'. "
            f"Ly do: khong co du lieu mau phu hop trong DB (xem AI_WORKLOG.md)"
        )

    payload = {k: resolve(v) for k, v in case["input"].items()}
    resp = requests.post(f"{API_URL}/api/Auth/login", json=payload, verify=False, timeout=15)
    try:
        body = resp.json()
    except ValueError:
        body = {"_raw": resp.text[:300]}
    status = resp.status_code
    errors = []

    if status >= 500:
        errors.append(f"Server loi {status} (loi phia server, khong xu ly duoc dau vao)")

    exp_status = case.get("expected_http_status")
    if isinstance(exp_status, int) and status != exp_status:
        errors.append(f"HTTP status: mong doi {exp_status}, thuc te {status}")

    kind = case.get("expected_error_kind")
    if kind == "business":
        if not isinstance(body, dict) or "success" not in body:
            errors.append(f"Mong doi dinh dang loi nghiep vu (co truong 'success'), thuc te body khong co: {body}")
    elif kind == "validation":
        if not isinstance(body, dict) or "errors" not in body:
            errors.append(f"Mong doi dinh dang validation (co truong 'errors'), thuc te body khong co: {body}")

    needle = case.get("expected_message_contains")
    if needle:
        message = json.dumps(body, ensure_ascii=False) if isinstance(body, dict) else str(body)
        if needle.casefold() not in message.casefold():
            errors.append(f"Noi dung: mong doi chua '{needle}', thuc te '{message[:200]}'")

    if errors:
        record_failure(case, status, body, errors)

    assert not errors, " | ".join(errors)