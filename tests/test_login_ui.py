import os
import pytest
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "https://localhost:7001")

@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        # Chạy ở chế độ headless và bỏ qua lỗi SSL localhost
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        yield context
        browser.close()

def test_ui_login_validation_and_wrong_password(browser_context):
    page = browser_context.new_page()
    page.goto(f"{BASE_URL}/Account/Login", wait_until="networkidle")

    # 1. Thử bấm Submit khi để trống form
    submit_btn = page.locator("button[type='submit'], input[type='submit']")
    submit_btn.first.click()

    # 2. Nhập định dạng email không hợp lệ
    email_input = page.locator("input[name='Email'], input[type='email'], #Email, #Input_Email").first
    pass_input = page.locator("input[name='Password'], input[type='password'], #Password, #Input_Password").first

    email_input.fill("email_khong_hop_le")
    pass_input.fill("Password@123")
    submit_btn.first.click()

    # 3. Nhập đúng tài khoản nhưng sai mật khẩu
    email_input.fill("student@sv.ute.udn.vn")
    pass_input.fill("SaiMatKhau@999")
    submit_btn.first.click()

    # Kiểm tra: người dùng vẫn ở trang Login hoặc có hiển thị thông báo lỗi
    assert "/Account/Login" in page.url or page.locator(".text-danger, .validation-summary-errors, .alert-danger").count() > 0
    page.close()