# Kiểm chứng SMB Signing trên Samba

**Sinh viên:** Lê Hoàng Bách — B23DCAT023  
**Nhóm:** 4 — Học phần An toàn mạng  
**Lỗ hổng nghiên cứu:** CVE-2023-3347

## Mục tiêu

Kiểm chứng việc thực thi chính sách bắt buộc ký thông điệp SMB trước và sau khi cập nhật Samba từ **4.17.5** lên **4.17.10**. Phân biệt cấu hình yêu cầu ký với hành vi xử lý yêu cầu thực tế.

SMB Signing bảo vệ tính toàn vẹn và xác thực thông điệp bằng khóa của phiên; không mã hóa nội dung tệp. Thực nghiệm sử dụng tài khoản hợp lệ có quyền đọc, không chứng minh vượt qua mật khẩu hoặc phân quyền.

## Môi trường của nhóm

| Thành phần | Thông tin |
|---|---|
| Máy chủ | Ubuntu Server 20.04, Samba triển khai trong Docker theo báo cáo |
| Trước vá | Samba 4.17.5 |
| Sau vá | Samba 4.17.10, do người thực hiện xác nhận |
| IP máy chủ | 192.168.8.153 |
| Máy khách Kali | 192.168.8.156 |
| Tài khoản thử nghiệm | student |
| Share | Confidential_Data |
| Tệp mẫu | SMB_SIGNING_TEST.txt |

Địa chỉ có thể cần thay theo mạng máy ảo hiện tại. Không đưa mật khẩu vào repository.

## Nội dung repository

- `scripts/test_signing.py`: chương trình tái dựng từ phép thử trong quá trình chuẩn bị vấn đáp; đọc đối chứng có ký rồi chủ động gửi một yêu cầu đọc không ký trong cùng phiên.
- `config/smb.conf.example`: cấu hình mẫu để đối chiếu, **không phải bản xuất cấu hình thực tế của container**.
- `docs/DEMO.md`: trình tự và lời dẫn demo.
- `docs/RESULTS.md`: kết quả đã quan sát, giới hạn minh chứng.
- `docs/REPORT_LINK.md`: cách chèn liên kết vào báo cáo.
- `evidence/after-patch/python-result.png`: ảnh kết quả chương trình do người thực hiện cung cấp.
- `requirements.txt`: thư viện dùng cho chương trình Python.

## Chạy kiểm thử

Trên Kali, kiểm tra hoặc cài Impacket:

```bash
python3 -c "import impacket; print('Impacket OK')"
# Nếu chưa có:
sudo apt install python3-impacket
```

Bắt gói trên giao diện nối tới máy chủ trong Wireshark, rồi chạy:

```bash
python3 scripts/test_signing.py --server 192.168.8.153 --share Confidential_Data --file SMB_SIGNING_TEST.txt --user student
```

Nhập mật khẩu tại dấu nhắc. Chương trình đọc 32 byte có ký trước, chờ Enter, rồi bỏ ký cho yêu cầu đọc tiếp theo. Dùng tệp mẫu không rỗng. Chương trình không ghi hoặc sửa tệp trên máy chủ.

Phép thử Python cố định **SMB 2.1** để tách riêng Signing khỏi SMB3 Encryption; không phải phép thử cùng dialect với mọi kết nối `smbclient`.

Chương trình dùng thuộc tính nội bộ của Impacket; ghi lại phiên bản thư viện trong kết quả và đối chiếu gói tin. Mã trong repository chưa được chạy lại trên máy ảo từ bản đóng gói này.

## Kết quả tóm tắt

| Phép thử | Kết quả |
|---|---|
| Trước vá 4.17.5: yêu cầu đọc không ký | Báo cáo ghi nhận vẫn tải tệp thành công |
| Sau vá 4.17.10: smbclient với hai tùy chọn disabled | Người thực hiện quan sát yêu cầu đọc có Signature khác 0 và đọc được |
| Sau vá: Python đọc có ký | Thành công, 32 byte |
| Sau vá: Python đọc không ký | STATUS_ACCESS_DENIED, 0xc0000022 |

Không suy ra yêu cầu không ký chỉ từ tùy chọn `disabled`. Cần đối chiếu cờ Signed, Signature và phản hồi đúng Message ID. Chữ ký khác 0 riêng lẻ không chứng minh chữ ký hợp lệ. Lỗi Access Denied riêng lẻ cũng có thể có nguyên nhân khác; phép đọc đối chứng giúp phân biệt.

## Tài liệu chính thức

- [Samba: CVE-2023-3347](https://www.samba.org/samba/security/CVE-2023-3347.html)
- [Samba: smb.conf](https://www.samba.org/samba/docs/current/man-html/smb.conf.5)
- [Microsoft: Verifying the Signature](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/85df1680-2ee7-4d25-a916-a982371ddc75)
- [Impacket: mã xử lý SMB](https://github.com/fortra/impacket/blob/master/impacket/smb3.py)

Chỉ thực hiện trên máy ảo và dữ liệu mẫu thuộc phạm vi lab được phép.
