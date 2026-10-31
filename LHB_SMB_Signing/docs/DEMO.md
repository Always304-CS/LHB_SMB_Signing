# Trình tự demo

## 1. Mở đầu

“Em sẽ kiểm chứng lỗi Samba vẫn chấp nhận yêu cầu đọc không ký dù đã cấu hình bắt buộc ký, sau đó đối chiếu sau khi vá.”

## 2. Kiểm tra trên máy chủ

Với bản cài riêng:

```bash
/usr/local/samba/sbin/smbd -V
pgrep -a smbd
sudo ss -lntp 'sport = :445'
/usr/local/samba/bin/testparm -s
```

Nếu chạy trong Docker, thay TEN_CONTAINER bằng tên thật:

```bash
docker ps
docker exec TEN_CONTAINER /usr/local/samba/sbin/smbd -V
docker exec TEN_CONTAINER /usr/local/samba/bin/testparm -s
```

Nếu smbd khởi chạy bằng tệp cấu hình riêng, truyền đúng tệp đó cho testparm. Không khởi chạy thêm một bản Samba hệ thống cạnh container.

“Đây là phiên bản thực tế và cấu hình yêu cầu ký. Cấu hình chưa đủ chứng minh việc thực thi; tiếp theo em kiểm tra lưu lượng.”

## 3. Bắt gói trên Kali

Mở Wireshark, chọn giao diện đi tới máy chủ, bắt gói trước khi kết nối. Bộ lọc hiển thị:

```text
ip.addr == 192.168.8.153 && tcp.port == 445
```

## 4. Truy cập bằng smbclient

```bash
smbclient //192.168.8.153/Confidential_Data -U student -m SMB3 --option='client signing=disabled' --option='client ipc signing=disabled'
```

Trong dấu nhắc smbclient:

```text
ls
get SMB_SIGNING_TEST.txt /tmp/SMB_SIGNING_TEST.txt
quit
```

`-m SMB3` đặt mức tối đa, không cố định dialect. Hai tùy chọn disabled không bảo đảm yêu cầu thực tế không ký. Xác minh trực tiếp trên bản bắt gói.

## 5. Đối chiếu Wireshark

Thương lượng:

```text
smb2.cmd == 0
```

Chọn Negotiate Response từ máy chủ: xem dialect và Security Mode → Signing Required. Kiểm tra lại nếu máy chủ không công bố yêu cầu như dự kiến; không suy ra chỉ từ cấu hình.

Yêu cầu đọc:

```text
smb2.cmd == 8 && smb2.flags.response == 0
```

Mở Header → Flags → Signed và Signature. Ghép phản hồi bằng Message ID.

- Trước vá: nếu Read Request không ký nhưng đọc thành công, đó là minh chứng lỗi thực thi.
- Sau vá: nếu Read Request có ký và đọc thành công, đó là phiên truy cập tuân thủ; chưa trực tiếp chứng minh từ chối gói không ký.

## 6. Phép thử bổ sung sau vá

Từ thư mục repository:

```bash
python3 scripts/test_signing.py --server 192.168.8.153 --user student
```

Kiểm tra đọc có ký thành công, nhấn Enter để gửi yêu cầu không ký. Dự kiến nhận STATUS_ACCESS_DENIED (0xc0000022), hoặc cần phân tích thêm nếu máy chủ đóng kết nối.

```text
smb2.cmd == 8
```

“Cùng tài khoản và tệp, yêu cầu có ký thành công, yêu cầu chủ động bỏ ký bị từ chối. Kết quả cho thấy việc bắt buộc ký được thực thi trong phép thử này.”

## 7. Lưu minh chứng

Lưu ảnh phiên bản, cấu hình, cờ Signed/Signature của request và phản hồi tương ứng. Không dùng số gói cố định vì mỗi lần bắt gói có số khác nhau. Ghi phiên bản smbclient, Impacket và ngày thử. Không đăng mật khẩu, khóa phiên hoặc bản bắt gói chưa được rà soát.
