# Bug Reports
Sinh tu dong luc 2026-09-30T08:50:46.834289

## TC-007 - Dang nhap voi khoang trang thua trong email

Dưới đây là báo cáo lỗi (Bug Report) dựa trên dữ liệu được cung cấp:

- **Ten/Noi dung test case:** TC-007 - Đăng nhập với khoảng trắng thừa trong email
- **Ket qua mong muon (Expected):** HTTP status 200, phản hồi chứa thông báo "Đăng nhập thành công"
- **Ket qua thuc te (Actual):** HTTP status 400, phản hồi trả về `{"success": false, "message": "Email hoặc mật khẩu không đúng"}`
- **Bang chung (mo ta ngan, tham chieu evidence/failures.json va anh chup Swagger neu co):** Hệ thống trả về mã lỗi HTTP 400 và thông báo thất bại khi đầu vào email có chứa khoảng trắng thừa ở đầu và cuối (` 23115053122327@sv.ute.udn.vn `), theo ghi nhận tại `failures.json` vào lúc `2026-09-29T17:21:48.682846`.
- **De xuat muc do nghiem trong (Severity: Critical/High/Medium/Low) kem ly do 1 cau:** Severity: Medium vì lỗi này làm gián đoạn trải nghiệm người dùng khi nhập liệu có vô tình dính khoảng trắng nhưng không ảnh hưởng đến toàn bộ hệ thống.
- **Nguyen nhan kha di (Possible cause):** Hệ thống chưa thực hiện việc tự động cắt bỏ khoảng trắng thừa (trim) ở đầu và cuối chuỗi email trước khi tiến hành xác thực thông tin đăng nhập.

---
