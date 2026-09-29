import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from google import genai

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
API_KEY = os.getenv("AI_API_KEY")
MODEL = os.getenv("AI_MODEL", "gemini-3.8-flash")
STORY_FILE = ROOT / "requirements" / "user_stories.md"
OUT_FILE = ROOT / "tests" / "generated_test_cases.json"
PROMPT_DIR = ROOT / "evidence" / "prompts"

SYSTEM = (
    "Ban la QA Engineer 5 nam kinh nghiem, chuyen thiet ke test case cho API. "
    "Chi tra ve JSON hop le, khong giai thich them, khong dung markdown."
)

USER_TMPL = """## Boi canh
API can kiem thu: POST /api/Auth/login
Body: {{"email": "...", "password": "..."}}
Chi kiem thu chuc nang DANG NHAP. Khong sinh test cho tinh nang khac (thue do, vi, OTP, admin...).

## Su that da xac nhan (KHONG duoc tu suy dien them)
{story}

## Nhiem vu
Sinh dung {n} test case cho POST /api/Auth/login, gom:
- positive: it nhat 2 (dang nhap dung)
- negative: it nhat 5 (sai mat khau, email khong ton tai...)
- boundary: it nhat 4 (do dai email/mat khau...)
- validation: it nhat 5 (thieu truong, sai dinh dang, SQL injection thu vao truong email...)

## Dinh dang dau ra: mot mang JSON, moi phan tu co dung cac truong
{{
  "id": "TC-001",
  "group": "positive" | "negative" | "boundary" | "validation",
  "title": "tieu de ngan",
  "rationale": "1 cau: vi sao test nay quan trong",
  "input": {{"email": "...", "password": "..."}},
  "expected_http_status": so nguyen hoac null (dung null neu KHONG chac chan),
  "expected_error_kind": "business" | "validation" | null,
  "expected_message_contains": "chuoi con mong doi" hoac null,
  "priority": "High" | "Medium" | "Low",
  "needs_confirmation": true hoac false
}}

Ghi chu ve expected_error_kind:
- "business": loi nghiep vu (sai mat khau, tai khoan khong ton tai) -> body co truong success/message
- "validation": loi validate dau vao (thieu truong, sai dinh dang) -> body co truong errors, KHONG co success/message

## Rang buoc
- Voi tai khoan dung, dung dung chuoi "<VALID_EMAIL>" va "<VALID_PASSWORD>".
- Chi dua tren "Su that da xac nhan" o tren. Neu khong chac ket qua, dat expected_http_status=null, expected_error_kind=null, expected_message_contains=null, needs_confirmation=true.
- KHONG bia them tinh nang khong lien quan den dang nhap.
- Chi tra ve mang JSON, khong markdown."""

REQUIRED = ["id", "group", "title", "rationale", "input",
            "expected_http_status", "expected_error_kind",
            "expected_message_contains", "priority", "needs_confirmation"]


def extract_json(text):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    return json.loads(t)


def validate(cases):
    if not isinstance(cases, list):
        raise ValueError("AI khong tra ve mot mang JSON")
    clean, seen = [], set()
    for i, c in enumerate(cases, 1):
        if not isinstance(c, dict):
            print(f"  ! Bo #{i}: khong phai object"); continue
        missing = [k for k in REQUIRED if k not in c]
        if missing:
            print(f"  ! Bo {c.get('id', f'#{i}')}: thieu {missing}"); continue
        if c["group"] not in ("positive", "negative", "boundary", "validation"):
            print(f"  ! Bo {c['id']}: group sai"); continue
        if not isinstance(c.get("input"), dict) or "email" not in c["input"] or "password" not in c["input"]:
            print(f"  ! Bo {c['id']}: input phai co email va password"); continue
        if c["id"] in seen:
            print(f"  ! Bo {c['id']}: trung id"); continue
        seen.add(c["id"])
        clean.append(c)
    return clean


def main():
    if not API_KEY or API_KEY == "your-key-here":
        print("LOI: chua co AI_API_KEY hop le trong .env"); sys.exit(1)

    story = STORY_FILE.read_text(encoding="utf-8")
    prompt = USER_TMPL.format(story=story.strip(), n=18)

    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (PROMPT_DIR / f"generate-{stamp}-prompt.md").write_text(
        f"# SYSTEM\n{SYSTEM}\n\n# USER\n{prompt}\n", encoding="utf-8")

    print(f"Dang goi model {MODEL} de sinh test case...")
    client = genai.Client(api_key=API_KEY)
    try:
        resp = client.models.generate_content(model=MODEL, contents=[SYSTEM, prompt])
        raw = resp.text
    except Exception as e:
        print(f"LOI khi goi AI: {e}")
        print("KHONG tu tao test case gia. Hay thu lai lenh nay sau vai giay.")
        sys.exit(1)

    (PROMPT_DIR / f"generate-{stamp}-raw.txt").write_text(raw, encoding="utf-8")

    try:
        cases = validate(extract_json(raw))
    except Exception as e:
        print(f"LOI: khong doc duoc JSON hop le tu AI: {e}")
        print(f"Xem noi dung tho tai: evidence/prompts/generate-{stamp}-raw.txt")
        sys.exit(1)

    groups = {}
    for c in cases:
        groups[c["group"]] = groups.get(c["group"], 0) + 1
    print(f"Hop le: {len(cases)} test case, theo nhom: {groups}")
    if len(cases) < 15:
        print("CANH BAO: de yeu cau toi thieu 15 test case co y nghia.")
    for g in ("positive", "negative", "boundary", "validation"):
        if not groups.get(g):
            print(f"CANH BAO: thieu nhom '{g}'")

    OUT_FILE.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Da luu: {OUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()