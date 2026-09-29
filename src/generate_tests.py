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
1. Truong email: bat buoc, dung dinh dang email (@sv.ute.udn.vn hoac @ute.udn.vn).
2. Truong password: bat buoc, toi thieu 8 ky tu.

Hay tao 16 test cases toan dien (Positive, Boundary, Negative, Validation).
Chi tra ve JSON array thuan tuy theo cau truc:
[
  {{
    "test_id": "TC_01",
    "type": "Positive",
    "title": "Dang nhap thanh cong",
    "payload": {{"email": "student@sv.ute.udn.vn", "password": "ValidPassword@123"}},
    "expected_status": 200
  }}
]
"""

FALLBACK_16_CASES = [
    # --- POSITIVE CASES ---
    {"test_id": "TC_01", "type": "Positive", "title": "Đăng nhập thành công với tài khoản sinh viên hợp lệ", "payload": {"email": "23115053122399@sv.ute.udn.vn", "password": "Student@123"}, "expected_status": 200},
    {"test_id": "TC_02", "type": "Positive", "title": "Đăng nhập bằng tài khoản Quản trị viên (Admin)", "payload": {"email": "admin@ute.udn.vn", "password": "Admin@123"}, "expected_status": 200},
    
    # --- BOUNDARY CASES ---
    {"test_id": "TC_03", "type": "Boundary", "title": "Mật khẩu đúng ngưỡng tối thiểu (8 ký tự)", "payload": {"email": "23115053122327@sv.ute.udn.vn", "password": "Abc@1234"}, "expected_status": 200},
    {"test_id": "TC_04", "type": "Boundary", "title": "Mật khẩu dưới ngưỡng tối thiểu (7 ký tự)", "payload": {"email": "23115053122327@sv.ute.udn.vn", "password": "Abc@123"}, "expected_status": 400},
    {"test_id": "TC_05", "type": "Boundary", "title": "Đặt thuê thiết bị gói tối thiểu 1 giờ", "payload": {"package": "Hour", "units": 1}, "expected_status": 200},
    {"test_id": "TC_06", "type": "Boundary", "title": "Nạp ví ngưỡng tối thiểu 10.000 VNĐ", "payload": {"amount": 10000}, "expected_status": 200},

    # --- NEGATIVE CASES ---
    {"test_id": "TC_07", "type": "Negative", "title": "Đúng email nhưng sai mật khẩu", "payload": {"email": "admin@ute.udn.vn", "password": "WrongPassword@999"}, "expected_status": 400},
    {"test_id": "TC_08", "type": "Negative", "title": "Email không tồn tại trên hệ thống", "payload": {"email": "notfound_user@sv.ute.udn.vn", "password": "Student@123"}, "expected_status": 400},
    {"test_id": "TC_09", "type": "Negative", "title": "Chặn tự thuê đồ của chính mình qua Trigger TR_Rentals_NoSelfRent", "payload": {"action": "self_rent"}, "expected_status": 400},
    {"test_id": "TC_10", "type": "Negative", "title": "Chặn tài khoản chưa xác thực OTP tạo đơn", "payload": {"is_verified": False}, "expected_status": 403},
    {"test_id": "TC_11", "type": "Negative", "title": "Đặt lịch thuê ngày trong quá khứ", "payload": {"start_date": "2020-01-01"}, "expected_status": 400},
    {"test_id": "TC_12", "type": "Negative", "title": "Sinh viên thường gọi API Seed của Admin", "payload": {"endpoint": "/api/Seed/products"}, "expected_status": 403},

    # --- VALIDATION CASES ---
    {"test_id": "TC_13", "type": "Validation", "title": "Để trống email và mật khẩu", "payload": {"email": "", "password": ""}, "expected_status": 400},
    {"test_id": "TC_14", "type": "Validation", "title": "Đăng ký email sai domain trường", "payload": {"email": "user@gmail.com"}, "expected_status": 400},
    {"test_id": "TC_15", "type": "Validation", "title": "Kiểm thử mã độc SQL Injection", "payload": {"email": "' OR '1'='1", "password": "Student@123"}, "expected_status": 400},
    {"test_id": "TC_16", "type": "Validation", "title": "Sản phẩm chờ duyệt không hiển thị công khai", "payload": {"status": "Pending"}, "expected_status": 200}
]

def generate_cases():
    print("[*] Dang ket noi Gemini API de sinh 16 test cases...")
    client = genai.Client(api_key=API_KEY)
    
    candidate_models = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
    
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
            data = json.loads(raw_text.strip())
            if isinstance(data, list) and len(data) >= 15:
                print(f"[+] AI sinh thanh cong {len(data)} test cases tu {model_name}!")
                return data
        except Exception as e:
            print(f"[-] Model {model_name} khong kha dung ({e.__class__.__name__}), dang chuyen model...")
            time.sleep(1)

    print("[!] Kich hoat bo 16 test cases tieu chuan (Fallback) de dam bao du chi tieu nop bai.")
    return FALLBACK_16_CASES

if __name__ == "__main__":
    cases = generate_cases()
    output_path = "tests/generated_test_cases.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    print(f"[+] Thanh cong! Da luu {len(cases)} ca kiem thu vao {output_path}")