import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()
    page.goto("https://localhost:7001/")
    page.get_by_role("link", name=" Đăng nhập").click()
    page.get_by_role("textbox", name="EMAIL / MÃ SỐ SINH VIÊN (MSSV)").click()
    page.get_by_role("textbox", name="EMAIL / MÃ SỐ SINH VIÊN (MSSV)").fill("23115053122327@sv.ute.udn.vn")
    page.get_by_role("textbox", name="••••••••").click()
    page.get_by_role("textbox", name="••••••••").press("CapsLock")
    page.get_by_role("textbox", name="••••••••").fill("S")
    page.get_by_role("textbox", name="••••••••").press("CapsLock")
    page.get_by_role("textbox", name="••••••••").fill("Student@123")
    page.get_by_role("button").first.click()
    page.get_by_role("button", name="Đăng nhập ngay ").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
