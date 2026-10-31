# Kết quả và trạng thái minh chứng

## Kết quả được báo cáo / quan sát

| Môi trường | Phép thử | Kết quả | Nguồn |
|---|---|---|---|
| Samba 4.17.5 | Đọc bằng student, yêu cầu không ký | Đọc thành công | Báo cáo nhóm, mục 2.7, trang 16–17 |
| Samba sau vá 4.17.10 | smbclient giữ hai tùy chọn disabled | Yêu cầu đọc có Signature khác 0, đọc thành công | Người thực hiện mô tả trong quá trình chuẩn bị demo |
| Sau vá | Python đọc có ký | 32 byte, thành công | Ảnh evidence/after-patch/python-result.png |
| Sau vá | Python chủ động bỏ ký trên yêu cầu đọc tiếp theo | STATUS_ACCESS_DENIED, 0xc0000022 | Cùng ảnh kết quả |

Phiên bản sau vá 4.17.10 do người thực hiện xác nhận; ảnh terminal hiện có không tự chứng minh phiên bản này. Mã Python được đóng gói lại với tham số dòng lệnh; cần chạy lại bản này trước demo.

## Giới hạn

- Chưa có bản xuất smb.conf thực tế, Dockerfile thực tế hoặc ảnh phiên bản sau vá trong bộ đóng gói.
- Ảnh terminal xác nhận lần đọc đối chứng và mã từ chối; chưa thay thế ảnh chi tiết Signed/Signature của từng gói.
- Thực nghiệm dùng tài khoản có quyền đọc; không chứng minh bỏ qua xác thực/phân quyền hoặc chiếm quyền máy.
- Phép thử Python dùng SMB 2.1; ghi rõ dialect khi so với smbclient.
- Chữ ký khác 0 không tự xác minh chữ ký đúng; đối chiếu cờ Signed và phản hồi.

## Minh chứng cần bổ sung từ máy ảo

1. Ảnh phiên bản 4.17.5 và 4.17.10 của đúng dịch vụ đang chạy.
2. Bản cấu hình thực tế đã loại thông tin nhạy cảm, và tên cấu hình smbd đang sử dụng.
3. Ảnh Read Request trước vá: Signed tắt, Signature bằng 0, phản hồi thành công.
4. Ảnh sau vá: Signed bật ở lần đọc đối chứng; Signed tắt ở lần đọc bị từ chối.
5. Phiên bản smbclient (`smbclient --version`) và Impacket (chương trình in khi chạy).

Không ghi nhận các mục còn thiếu là đã được kiểm chứng trong repository.
