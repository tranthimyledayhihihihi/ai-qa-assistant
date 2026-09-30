# Test Strategy

## Phạm vi kiểm thử
Chức năng đăng nhập (`POST /api/Auth/login` và trang `/Account/Login`) của ứng dụng thuê đồ ngắn hạn.

## Mức độ kiểm thử
- **Tầng API**: kiểm thử trực tiếp endpoint, không phụ thuộc giao diện — nhanh, ổn định, dễ mở rộng số lượng test case.
- **Tầng UI**: kiểm thử qua trình duyệt thật bằng Playwright — xác nhận luồng người dùng thực tế hoạt động đúng.

## Loại test
- Positive: đăng nhập với thông tin hợp lệ
- Negative: sai mật khẩu, email không tồn tại, sai cả hai
- Boundary: độ dài email/mật khẩu ở giá trị biên, viết hoa/thường, khoảng trắng thừa
- Validation: dữ liệu rỗng, sai định dạng, tấn công SQL Injection cơ bản

## Công cụ
- pytest — điều phối test
- requests — gọi API trực tiếp
- Playwright (Chromium) — tự động hóa trình duyệt cho tầng UI
- Google Gemini API — sinh test case và phân tích lỗi

## Tiêu chí Pass/Fail
- **Pass**: mã HTTP trả về đúng như kỳ vọng, và (nếu có) nội dung phản hồi đúng định dạng và nội dung mong đợi.
- **Fail**: sai lệch giữa kỳ vọng và thực tế ở mã HTTP, định dạng lỗi, hoặc nội dung thông báo.
- **Skip**: khi AI sinh test case dùng dữ liệu không có sẵn trong hệ thống (ví dụ tài khoản chưa xác thực OTP không tồn tại trong dữ liệu mẫu) — tránh báo Fail sai lệch.

## Rủi ro và giới hạn
- Môi trường test chạy local (không phải môi trường staging/production), có thể khác biệt hành vi khi deploy thật.
- Dữ liệu mẫu có sẵn giới hạn (7 tài khoản), không đủ để kiểm chứng mọi quy tắc nghiệp vụ (ví dụ tài khoản chưa xác thực OTP).
- Test phụ thuộc vào kết quả AI sinh ra; mọi test case đều được rà soát thủ công trước khi tin dùng (xem AI_WORKLOG.md).