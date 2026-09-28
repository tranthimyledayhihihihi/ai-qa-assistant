import os
import requests
import urllib3
import pytest
from dotenv import load_dotenv

# Tắt cảnh báo SSL do chạy https trên localhost (self-signed cert)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

API_URL = os.getenv("API_URL", "https://localhost:7000")
LOGIN_ENDPOINT = f"{API_URL}/api/Auth/login"

class TestLoginApi:

    def test_wrong_password(self):
        """TC_API_01: Đúng email nhưng sai mật khẩu -> Mong đợi 400 hoặc 401"""
        payload = {
            "email": "student@sv.ute.udn.vn",
            "password": "WrongPassword@999"
        }
        res = requests.post(LOGIN_ENDPOINT, json=payload, verify=False, timeout=5)
        assert res.status_code in [400, 401], f"Status thực tế: {res.status_code}"

    def test_nonexistent_email(self):
        """TC_API_02: Email không tồn tại -> Mong đợi 400, 401 hoặc 404"""
        payload = {
            "email": "notfound_user_99999@sv.ute.udn.vn",
            "password": "Password@123"
        }
        res = requests.post(LOGIN_ENDPOINT, json=payload, verify=False, timeout=5)
        assert res.status_code in [400, 401, 404], f"Status thực tế: {res.status_code}"

    def test_empty_credentials(self):
        """TC_API_03: Để trống email và mật khẩu -> Mong đợi 400 Bad Request"""
        payload = {"email": "", "password": ""}
        res = requests.post(LOGIN_ENDPOINT, json=payload, verify=False, timeout=5)
        assert res.status_code == 400, f"Mong đợi 400 nhưng trả về: {res.status_code}"

    def test_invalid_email_format(self):
        """TC_API_04: Email sai định dạng (ví dụ 'abc') -> Mong đợi 400 Bad Request"""
        payload = {
            "email": "abc_invalid_format",
            "password": "Password@123"
        }
        res = requests.post(LOGIN_ENDPOINT, json=payload, verify=False, timeout=5)
        assert res.status_code == 400, f"Mong đợi 400 nhưng trả về: {res.status_code}"