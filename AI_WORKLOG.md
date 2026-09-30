# AI_WORKLOG

## Công cụ AI đã dùng
- Google Gemini (qua thư viện google-genai), model gemini-flash-lite-latest — dùng để sinh test case tự động (src/generate_tests.py) và sẽ dùng để phân tích lỗi, sinh bug report (src/analyze_failures.py)

## AI hỗ trợ việc gì
- Đọc user story và các quy tắc nghiệp vụ đã xác nhận (requirements/user_stories.md), tự sinh test case cho chức năng đăng nhập gồm 4 nhóm: positive, negative, boundary, validation
- Mỗi test case AI sinh ra có kèm lý do (rationale) vì sao test đó quan trọng, giúp tiết kiệm thời gian brainstorm thủ công

## Kết quả AI sai và cách tôi sửa
| Lần | AI đưa ra gì | Sai ở đâu | Tôi đã sửa thế nào |
|---|---|---|---|
| 1 | Model gemini-2.5-flash, gemini-2.0-flash, gemini-1.5-flash | Các model này đã ngừng hỗ trợ tài khoản mới (lỗi 404 NOT_FOUND) | Dò danh sách model bằng script thăm dò, chuyển sang model đang hoạt động |
| 2 | Model gemini-3.8-flash, gemini-flash-latest, gemini-pro-latest | Liên tục báo lỗi 503 (quá tải) hoặc 429 (hết quota) tại thời điểm chạy | Chuyển sang gemini-flash-lite-latest, model duy nhất phản hồi ổn định lúc đó |
| 3 | Bản đầu của script: khi gọi AI lỗi, tự động dùng 16 test case viết sẵn (fallback) nhưng vẫn báo "Thành công" | Đây là dữ liệu giả, không phải AI sinh ra thật, vi phạm yêu cầu đề bài "không nộp chức năng giả lập" | Bỏ hoàn toàn fallback; khi gọi AI thất bại, chương trình dừng và báo lỗi rõ ràng, không tự tạo dữ liệu thay thế |
| 4 | Bản đầu của test: assertion chấp nhận dải mã HTTP quá rộng (200, 400, 401, 403, 404) | Test không bao giờ có thể fail, không phát hiện được lỗi thật | Viết lại assertion: so sánh đúng mã HTTP, đúng kiểu lỗi (nghiệp vụ có "success"/"message" vs validate có "errors"), đúng nội dung message mong đợi |
| 5 | Trong 18 test case AI sinh lần đầu, có TC-017 và TC-018 thiếu trường email hoặc password trong input | Test case không hợp lệ để chạy tự động | Script tự động loại bỏ 2 test case này trước khi lưu (16/18 được giữ lại) |
| 6 | TC-002: AI tự đặt token "<UNVERIFIED_EMAIL>" (ngoài 2 token được phép là <VALID_EMAIL>/<VALID_PASSWORD>) để test tài khoản chưa xác thực OTP | Test ban đầu FAIL sai lệch vì token lạ bị gửi thẳng làm email thật. Kiểm tra trong SQL Server: cả 7 tài khoản mẫu trong bảng Users đều có IsVerified = True, không có tài khoản nào phù hợp để test tình huống này | Thêm cơ chế phát hiện token lạ, tự động SKIP kèm lý do rõ ràng thay vì FAIL gây hiểu nhầm. Đây là giới hạn về dữ liệu mẫu, không phải lỗi ứng dụng |
| 7 | TC-007: AI đưa needs_confirmation=true, không chắc hệ thống có trim khoảng trắng email hay không | Đã tự kiểm chứng qua Swagger: hệ thống KHÔNG trim khoảng trắng, dẫn đến từ chối đăng nhập dù email/mật khẩu đúng bản chất — đây là bug thật (hệ thống có chuẩn hóa hoa/thường nhưng không chuẩn hóa khoảng trắng, không nhất quán) | Cập nhật expected_http_status=200 cho TC-007 dựa trên hành vi đúng nên có; test giờ FAIL đúng để phản ánh bug này, dùng làm input cho bug report tự động |
## Nếu có thêm 7 ngày
- Mở rộng sang luồng thuê đồ và thanh toán ví (không chỉ đăng nhập), vì đây là nơi có nhiều quy tắc nghiệp vụ và dễ phát hiện bug thật hơn
- Thêm test cho giao diện (UI) bằng Playwright, hiện tại mới tự động hóa ở tầng API
- Thêm cơ chế thử lại tự động (retry) khi API AI báo lỗi tạm thời (503/429) thay vì phải chạy lại lệnh bằng tay
- Chuẩn hóa lại định dạng lỗi API (hiện có 2 định dạng khác nhau cho cùng mã 400), giúp việc viết test và tài liệu dễ hơn