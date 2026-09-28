# Chiến lược kiểm thử (Test Strategy)

## 1. Phạm vi kiểm thử (Scope)
- **Hệ thống mục tiêu**: Module Xác thực người dùng (Authentication) của Ứng dụng Quản lý thuê thiết bị.
- **Thành phần**:
  - API Backend: `POST /api/Auth/login` (chạy tại `https://localhost:7000`)
  - Giao diện người dùng Web: `/Account/Login` (chạy tại `https://localhost:7001`)

## 2. Loại kiểm thử áp dụng
- **API Testing (Functional & Negative)**: Kiểm tra mã trạng thái HTTP (200, 400, 401, 404) và thông điệp lỗi trả về qua `requests` + `pytest`.
- **UI Functional Testing**: Kiểm tra hành vi validate form, tương tác nút bấm và điều hướng lỗi qua `playwright`.
- **Boundary & Negative Testing**: Kiểm thử các trường hợp dữ liệu rỗng, email sai cú pháp, mật khẩu không đúng độ dài.

## 3. Công cụ & Môi trường
- **Ngôn ngữ**: Python 3.13
- **Test Framework**: `pytest`, `requests`, `playwright`
- **Hỗ trợ AI**: Google GenAI SDK (`google-genai`)
- **Trình duyệt**: Chromium Headless

## 4. Tiêu chí Pass / Fail
- **Pass**: 100% ca kiểm thử API và UI thực thi không báo lỗi cú pháp; backend trả đúng mã HTTP 400 cho validation sai; UI không bị crash/văng lỗi 500 khi người dùng nhập dữ liệu biên.
- **Fail**: Bất kỳ ca kiểm thử nào nhận phản hồi HTTP 500 (Internal Server Error) hoặc giao diện không chặn được dữ liệu rỗng.

## 5. Rủi ro & Giải pháp giảm thiểu
- **Môi trường localhost dùng HTTPS tự ký**: Tắt cảnh báo SSL bằng `urllib3.disable_warnings` và cờ `ignore_https_errors=True`.
- **Dịch vụ AI bên ngoài quá tải**: Triển khai cơ chế Fallback Test Cases ngay trong script để việc chạy kiểm thử luôn liên tục.