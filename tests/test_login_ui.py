import os
import re
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
BASE_URL = os.getenv("BASE_URL", "https://localhost:7001").rstrip("/")
VALID_EMAIL = os.getenv("VALID_EMAIL", "")
VALID_PASSWORD = os.getenv("VALID_PASSWORD", "")
EVIDENCE_DIR = ROOT / "evidence"


def _screenshot(page, name):
    EVIDENCE_DIR.mkdir(exist_ok=True)
    page.screenshot(path=str(EVIDENCE_DIR / f"ui-{name}.png"))


def _do_login(page, email, password):
    page.goto(BASE_URL + "/")
    page.locator("a.btn-login").click()
    page.get_by_role("textbox", name=re.compile("EMAIL")).fill(email)
    # O mat khau la textbox thu 2 tren form (khong dung 'name' vi no la placeholder che dau)
    page.locator("input[type='password']").fill(password)
    page.get_by_role("button", name="Đăng nhập ngay").click()
    page.wait_for_timeout(1500)


def test_ui_login_success():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        try:
            _do_login(page, VALID_EMAIL, VALID_PASSWORD)
            _screenshot(page, "login-success")
            # Dang nhap thanh cong: khong con nut "Dang nhap", co loi chao mung
            assert page.get_by_text("Chào mừng").first.is_visible(timeout=5000), \
                "Khong thay loi chao mung sau khi dang nhap - dang nhap UI that bai"
        finally:
            context.close()
            browser.close()


def test_ui_login_wrong_password():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        try:
            _do_login(page, VALID_EMAIL, "SaiMatKhau123")
            _screenshot(page, "login-wrong-password")
            # Dang nhap that bai: van con o mat khau tren trang (chua chuyen huong)
            assert page.locator("input[type='password']").is_visible(timeout=5000), \
                "Trang da chuyen huong du dang nhap sai mat khau - co the la bug bao mat"
        finally:
            context.close()
            browser.close()