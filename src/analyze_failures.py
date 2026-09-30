import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from google import genai

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
API_KEY = os.getenv("AI_API_KEY")
MODEL = os.getenv("AI_MODEL", "gemini-flash-lite-latest")
FAILURES_FILE = ROOT / "evidence" / "failures.json"
OUT_FILE = ROOT / "evidence" / "bug_reports.md"

SYSTEM = (
    "Ban la QA Lead viet bao cao loi (bug report) sup tich, khach quan, "
    "chi dua tren du lieu duoc cung cap, khong suy doan them."
)

TEMPLATE = """Dua tren ket qua test that bai sau, viet bao cao loi bang tieng Viet gom dung cac muc:
- Ten/Noi dung test case
- Ket qua mong muon (Expected)
- Ket qua thuc te (Actual)
- Bang chung (mo ta ngan, tham chieu evidence/failures.json va anh chup Swagger neu co)
- De xuat muc do nghiem trong (Severity: Critical/High/Medium/Low) kem ly do 1 cau
- Nguyen nhan kha di (Possible cause) - chi suy luan hop ly tu du lieu, khong bia

Du lieu:
{data}
"""


def main():
    if not FAILURES_FILE.exists():
        print("Chua co evidence/failures.json. Hay chay pytest truoc.")
        sys.exit(0)
    failures = json.loads(FAILURES_FILE.read_text(encoding="utf-8"))
    if not failures:
        print("Khong co failure nao de phan tich.")
        sys.exit(0)
    if not API_KEY or API_KEY == "your-key-here":
        print("LOI: chua co AI_API_KEY hop le."); sys.exit(1)

    client = genai.Client(api_key=API_KEY)
    reports = [f"# Bug Reports\nSinh tu dong luc {datetime.now().isoformat()}\n"]
    for f in failures:
        prompt = TEMPLATE.format(data=json.dumps(f, ensure_ascii=False, indent=2))
        try:
            resp = client.models.generate_content(model=MODEL, contents=[SYSTEM, prompt])
            text = resp.text
        except Exception as e:
            print(f"LOI khi phan tich {f['id']}: {e}")
            text = f"(Khong goi duoc AI: {e})\n\nDu lieu tho:\n```json\n{json.dumps(f, ensure_ascii=False, indent=2)}\n```"
        reports.append(f"## {f['id']} - {f['title']}\n\n{text}\n\n---\n")
        time.sleep(2)

    OUT_FILE.write_text("\n".join(reports), encoding="utf-8")
    print(f"Da luu {len(failures)} bug report vao {OUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()