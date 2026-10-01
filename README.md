# AI Testing Assistant — 7-Day AI Builder Challenge (Tester/QA)

Công cụ trợ lý kiểm thử dùng AI, thực hiện luồng: **User story → AI sinh test case → Chạy test tự động → Phát hiện lỗi → Sinh Bug Report tự động**.

## 1. Vấn đề

Đội ngũ QA tốn nhiều thời gian cho các việc lặp lại: đọc yêu cầu, viết test case, chạy kiểm thử hồi quy, viết báo cáo lỗi, phân tích nguyên nhân test fail. Dự án này xây dựng một công cụ nhỏ dùng AI để hỗ trợ tự động hóa các bước này cho một chức năng cụ thể: **đăng nhập**.

## 2. Website/ứng dụng được kiểm thử

**Ứng dụng:** Nền tảng cho thuê đồ ngắn hạn dành cho sinh viên (web ASP.NET Core, chạy local).

**Lý do chọn ứng dụng này:**
- Đây là ứng dụng có sẵn với dữ liệu mẫu thật (tài khoản, cơ sở dữ liệu SQL Server), cho phép kiểm thử với hành vi hệ thống thật thay vì mock giả định.
- Chức năng đăng nhập có nhiều quy tắc nghiệp vụ rõ ràng (định dạng email trường, xác thực OTP, mã hóa mật khẩu) — đủ phức tạp để sinh ra các test case có ý nghĩa thay vì chỉ kiểm tra bề mặt.
- Có tài liệu (README của dự án gốc) mô tả rõ quy tắc, giúp việc xác nhận "sự thật" của hệ thống (qua Swagger) diễn ra nhanh và chính xác.

**Phần được chọn để kiểm thử:** API và giao diện đăng nhập (`POST /api/Auth/login` và trang `/Account/Login`), vì đây là chức năng nền tảng, ảnh hưởng đến toàn bộ các chức năng khác của hệ thống.

## 3. Giải pháp / Kiến trúc

```
User story (requirements/user_stories.md)
        │
        ▼
src/generate_tests.py ──(gọi AI: Google Gemini)──► tests/generated_test_cases.json
        │
        ▼
tests/test_login_api.py (pytest + requests)  ──►  evidence/failures.json (khi có test fail)
tests/test_login_ui.py  (pytest + Playwright) ──►  evidence/ui-*.png (ảnh chụp màn hình)
        │
        ▼
src/analyze_failures.py ──(gọi AI: Google Gemini)──► evidence/bug_reports.md
```

**Công nghệ sử dụng:**
- Python 3.13, pytest — điều phối và chạy test
- `requests` — kiểm thử tầng API
- Playwright — kiểm thử tầng giao diện (UI), tự động hóa trình duyệt thật
- Google Gemini API (model `gemini-flash-lite-latest`) — sinh test case và phân tích lỗi

## 4. Cách dùng AI

1. **Sinh test case** (`src/generate_tests.py`): đọc user story và các quy tắc nghiệp vụ đã xác nhận qua Swagger (`requirements/user_stories.md`), gửi cho AI để sinh ra tối thiểu 15 test case gồm 4 nhóm: positive, negative, boundary, validation. Kết quả được kiểm tra cấu trúc trước khi lưu (loại bỏ test case thiếu trường bắt buộc).
2. **Phân tích lỗi và sinh bug report** (`src/analyze_failures.py`): khi test fail, dữ liệu thật (input, expected, actual) được gửi cho AI để viết báo cáo lỗi theo đúng 6 mục: test case, expected, actual, bằng chứng, mức độ nghiêm trọng, nguyên nhân khả dĩ.

Toàn bộ prompt và phản hồi thô của AI được lưu lại tại `evidence/prompts/` để có thể kiểm tra lại.

## 5. Kết quả kiểm thử

**Test tầng API** (`tests/test_login_api.py`, 16 test case do AI sinh):
- **14 passed** — xác nhận hệ thống hoạt động đúng như kỳ vọng
- **1 failed (TC-007)** — phát hiện **bug thật**: hệ thống không tự động cắt khoảng trắng thừa ở email trước khi xác thực, khiến đăng nhập thất bại dù email/mật khẩu đúng bản chất. Xem chi tiết tại `evidence/bug_reports.md`.
- **1 skipped (TC-002)** — AI đề xuất test tài khoản "chưa xác thực OTP", nhưng dữ liệu mẫu trong hệ thống không có tài khoản nào ở trạng thái này để kiểm chứng (đã xác nhận qua truy vấn SQL Server). Được đánh dấu skip thay vì fail sai lệch.

**Test tầng UI** (`tests/test_login_ui.py`, dùng Playwright):
- **2 passed** — đăng nhập thành công và đăng nhập sai mật khẩu, cả hai đều chạy trên trình duyệt thật (Chromium), có ảnh chụp màn hình làm bằng chứng.

Ảnh chụp kết quả chạy: `evidence/api_test.png`, `evidence/ui-test-run.png`.

## 6. Bug đã phát hiện

**TC-007 — Email không được trim khoảng trắng trước khi xác thực đăng nhập**
- **Mức độ:** Medium
- **Mô tả:** Khi email hợp lệ có khoảng trắng thừa ở đầu/cuối (ví dụ do copy-paste), hệ thống từ chối đăng nhập với thông báo "Email hoặc mật khẩu không đúng", dù thông tin đăng nhập về bản chất là đúng.
- **So sánh:** Hệ thống đã xử lý tốt việc không phân biệt hoa/thường trong email (TC-006 pass), nhưng chưa xử lý nhất quán với khoảng trắng thừa.
- Chi tiết đầy đủ: `evidence/bug_reports.md`, dữ liệu thô: `evidence/failures.json`

## 7. Cách chạy lại

```bash
# 1. Cài môi trường
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
playwright install chromium

# 2. Cấu hình (tạo file .env, xem .env.example)
# AI_API_KEY, AI_PROVIDER=gemini, AI_MODEL=gemini-flash-lite-latest
# API_URL=https://localhost:7000, BASE_URL=https://localhost:7001
# VALID_EMAIL, VALID_PASSWORD (tài khoản demo có sẵn trong hệ thống)

# 3. Chạy ứng dụng cần kiểm thử (backend + frontend, xem README của dự án đó)

# 4. Sinh test case bằng AI
python src/generate_tests.py

# 5. Chạy test tự động
pytest tests/test_login_api.py -v
pytest tests/test_login_ui.py -v

# 6. Sinh bug report từ kết quả fail (nếu có)
python src/analyze_failures.py
```

## 8. Hạn chế

- Mới kiểm thử chức năng đăng nhập; chưa mở rộng sang các luồng nghiệp vụ khác (thuê đồ, thanh toán ví, kiểm duyệt sản phẩm).
- TC-002 (tài khoản chưa xác thực OTP) chưa kiểm chứng được do thiếu dữ liệu mẫu phù hợp.
- Hệ thống API có 2 định dạng lỗi HTTP 400 khác nhau (lỗi nghiệp vụ và lỗi validate đầu vào) — công cụ phải xử lý riêng cho từng loại, có thể gây khó khăn nếu mở rộng sang chức năng khác có định dạng lỗi khác nữa.
- Chưa có tính năng AI tự khám phá (explore) website để tự gợi ý phần cần test (phần điểm cộng của đề).

## 9. Nếu có thêm 7 ngày

Xem chi tiết trong `AI_WORKLOG.md`, tóm tắt:
- Mở rộng kiểm thử sang luồng thuê đồ và thanh toán ví — nơi có nhiều quy tắc nghiệp vụ và khả năng phát hiện bug cao hơn
- Bổ sung tài khoản demo ở trạng thái "chưa xác thực OTP" để kiểm chứng đầy đủ quy tắc liên quan
- Thêm cơ chế tự động thử lại khi gọi AI gặp lỗi tạm thời (503/429)
- Xây dựng tính năng AI tự khám phá website để gợi ý phạm vi cần test (phần điểm cộng)
- Chuẩn hóa định dạng lỗi API để đơn giản hóa việc viết test

## 10. Minh chứng thay thế Video Demo

Do giới hạn thời gian, phần này thay bằng bộ bằng chứng đầy đủ theo từng bước của quy trình, có thể xem trực tiếp trong repo:

1. **Sinh test case bằng AI**: `evidence/prompts/` (toàn bộ prompt và phản hồi thô của AI), `tests/generated_test_cases.json` (kết quả 16 test case)
2. **Chạy test tự động**: `evidence/api_test.png` (kết quả pytest tầng API), `evidence/ui-test-run.png` (kết quả pytest tầng UI với Playwright)
3. **Phát hiện lỗi**: `evidence/failures.json` (dữ liệu thô của test case fail)
4. **Sinh bug report**: `evidence/bug_reports.md` (báo cáo lỗi do AI viết)
5. **Ảnh chụp giao diện thật**: `evidence/ui-login-success.png`, `evidence/ui-login-wrong-password.png`

Toàn bộ các bước trên có thể tái hiện lại bằng cách làm theo hướng dẫn ở mục 7 (Cách chạy lại).

## 11. AI_WORKLOG

Xem chi tiết đầy đủ tại [`AI_WORKLOG.md`](./AI_WORKLOG.md) — ghi lại toàn bộ quá trình dùng AI, các lỗi AI mắc phải (chọn model không khả dụng, tạo token không hợp lệ, assertion ban đầu quá lỏng khiến không phát hiện được lỗi) và cách khắc phục.