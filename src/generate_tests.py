import os
import json
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("AI_API_KEY")
API_URL = os.getenv("API_URL", "https://localhost:7000")

PROMPT = f"""
Ban la Senior QA Automation Engineer.
Dua tren Swagger endpoint: POST {API_URL}/api/Auth/login
Yeu cau kiem thu dang nhap:
1. Truong email: bat buoc, dung dinh dang email.
2. Truong password: bat buoc, toi thieu 8 ky tu.

Hay tao 4 test cases kiem thu bien va truong hop am (Negative & Boundary Cases).
Chi tra ve JSON array thuan tuy theo mau:
[
  {{
    "test_id": "TC_AI_01",
    "title": "Sai mat khau",
    "payload": {{"email": "student@sv.ute.udn.vn", "password": "WrongPassword@123"}},
    "expected_status": 400
  }}
]
"""

FALLBACK_CASES = [
    {
        "test_id": "TC_AI_01",
        "title": "Dung email sai mat khau",
        "payload": {"email": "student@sv.ute.udn.vn", "password": "WrongPassword@123"},
        "expected_status": 400
    },
    {
        "test_id": "TC_AI_02",
        "title": "Email khong ton tai",
        "payload": {"email": "ghost_account_9999@sv.ute.udn.vn", "password": "Password@123"},
        "expected_status": 404
    },
    {
        "test_id": "TC_AI_03",
        "title": "De trong email va mat khau",
        "payload": {"email": "", "password": ""},
        "expected_status": 400
    },
    {
        "test_id": "TC_AI_04",
        "title": "Email sai dinh dang",
        "payload": {"email": "abc_invalid_email", "password": "Password@123"},
        "expected_status": 400
    }
]

def generate_cases():
    print("[*] Dang ket noi Gemini API de sinh test cases...")
    client = genai.Client(api_key=API_KEY)
    
    # Danh sach cac model thu lan luot neu co model bi qua tai (503)
    candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    for model_name in candidate_models:
        try:
            print(f"[*] Thu goi model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=PROMPT
            )
            raw_text = response.text.strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0]
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0]
            print(f"[+] Ket noi thanh cong voi {model_name}!")
            return json.loads(raw_text.strip())
        except Exception as e:
            print(f"[-] Model {model_name} bao ban/loi ({e.__class__.__name__}), dang chuyen model tiep theo...")
            time.sleep(1)

    print("[!] Tat ca cac model online deu ban. Tu dong dung bo test case tieu chuan de khong ngat quang quy trinh.")
    return FALLBACK_CASES

if __name__ == "__main__":
    cases = generate_cases()
    output_path = "tests/generated_test_cases.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    print(f"[+] Thanh cong! Da luu {len(cases)} ca kiem thu vao {output_path}")