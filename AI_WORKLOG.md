# AI_WORKLOG

## Công cụ AI đã dùng
- **Google Gemini API (`gemini-2.5-flash` / `gemini-3.8-flash`)**: Sinh bộ ca kiểm thử biên (Boundary & Negative cases) từ đặc tả Swagger endpoint `POST /api/Auth/login`.
- **Trợ lý AI lập trình**: Hỗ trợ khung kịch bản kiểm thử tự động với `pytest`, `requests` và `playwright`.

## AI hỗ trợ việc gì
- Tự động sinh danh sách dữ liệu kiểm thử (test payloads) cho trường hợp sai định dạng email, thiếu mật khẩu, và tài khoản không tồn tại.
- Viết khung boilerplate code cho Playwright UI test và Pytest API test.
- Tiết kiệm thời gian thiết kế ca kiểm thử ban đầu (ước tính tiết kiệm ~4 giờ).

## Kết quả AI sai và cách tôi sửa (Tư duy kiểm chứng)
| Lần | AI đưa ra gì | Sai ở đâu | Tôi đã sửa thế nào |
|---|---|---|---|
| 1 | AI sinh mã model `gemini-2.5-flash` cũ | Model đã ngưng hỗ trợ người dùng mới (lỗi 404 NOT_FOUND) và API trả mã lỗi 503 khi mạng quá tải | Đổi sang `gemini-3.8-flash` đồng thời viết hàm `generate_cases()` có danh sách dự phòng (Fallback Cases) để quy trình test không bị gián đoạn |
| 2 | AI dự đoán để trống email/password sẽ trả về mã `401 Unauthorized` | Swagger thực tế trả về `400 Bad Request` do DataAnnotations Validation của ASP.NET Core chặn trước khi vào logic chứng thực | Sửa lại mã mong đợi trong assertion thành `assert res.status_code == 400` |
| 3 | AI tạo selector cứng cho nút bấm login là `#login-button` | Form Razor View thực tế dùng thẻ `<button type="submit">` không có ID cố định | Đổi selector sang dạng linh hoạt `button[type='submit'], input[type='submit']` |
| 4 | AI sinh script Playwright thiếu xử lý chứng chỉ số cục bộ | Ứng dụng chạy trên HTTPS localhost dùng chứng chỉ tự ký (self-signed), script mặc định bị crash | Bổ sung tham số `ignore_https_errors=True` vào context của trình duyệt |

## Nếu có thêm 7 ngày
- Mở rộng tự động hóa sang các module: Quản lý thiết bị thuê, duyệt đơn nghỉ phép đa cấp (admin và khách hàng cùng duyệt), và quản lý hợp đồng/giao dịch.
- Tích hợp pipeline CI/CD trên GitHub Actions để tự động kích hoạt `pytest` mỗi khi có Pull Request mới.
- Thêm kiểm thử tải nhẹ (load testing) cho API đăng nhập bằng Locust.