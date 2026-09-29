# User story: Đăng nhập
Là sinh viên, tôi có thể đăng nhập bằng email và mật khẩu.

## Quy tắc đã biết chắc
- Email trường có đuôi @sv.ute.udn.vn
- Tài khoản chưa xác thực OTP (IsVerified = 0) không được thực hiện giao dịch thuê/mua

## Quy tắc đã xác nhận qua Swagger (POST /api/Auth/login)
- Đăng nhập đúng -> HTTP 200, body: {"success": true, "message": "Đăng nhập thành công", "data": {...kèm token...}}
- Sai mật khẩu hoặc email không tồn tại -> HTTP 400, body: {"success": false, "message": "Email hoặc mật khẩu không đúng"}
- Để trống password -> HTTP 400, body dạng ASP.NET validation: {"errors": {"Password": ["Mật khẩu là bắt buộc"]}} (KHÔNG có trường success/message)
- Email sai định dạng hoặc không có đuôi @sv.ute.udn.vn -> HTTP 400, body dạng ASP.NET validation: {"errors": {"Email": ["Email không hợp lệ", "Email phải có đuôi @sv.ute.udn.vn (ví dụ: 23115053122326@sv.ute.udn.vn)"]}}

## Lưu ý quan trọng
Có 2 định dạng lỗi 400 khác nhau tùy loại lỗi:
1. Lỗi nghiệp vụ (sai mật khẩu, tài khoản không tồn tại): có trường "success" và "message"
2. Lỗi validate đầu vào (thiếu trường, sai định dạng): theo khuôn mẫu ASP.NET, có trường "errors", KHÔNG có "success"/"message"

## Chưa xác nhận (AI không được tự bịa)
- Mật khẩu tối thiểu bao nhiêu ký tự
- Có giới hạn số lần đăng nhập sai không (khóa tài khoản)