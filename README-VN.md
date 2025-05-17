# Pharos Testnet Scripts 🚀

Bộ script Python này được thiết kế để tương tác với Pharos Testnet, một mạng thử nghiệm blockchain tiên tiến dành cho các ứng dụng phi tập trung. Script chính, main.py, cung cấp giao diện dòng lệnh (CLI) thân thiện, hỗ trợ thực hiện các thao tác như triển khai hợp đồng thông minh, swap token và thêm thanh khoản. Được xây dựng bằng web3.py, các script này tận dụng thực thi không đồng bộ và cung cấp giao diện song ngữ (Tiếng Việt/Tiếng Anh) hiện đại.

🔗 Faucet: [Pharos Testnet Faucet](https://testnet.pharosnetwork.xyz/)

## ✨ Tính năng

### Tính năng chung

- **Hỗ trợ đa tài khoản**: Thực hiện các thao tác trên nhiều ví bằng khóa riêng từ file `pvkey.txt`.
- **Giao diện CLI màu sắc**: Sử dụng `colorama` để tạo đầu ra sinh động với viền và màu sắc.
- **Thực thi không đồng bộ**: Tận dụng `asyncio` để tương tác blockchain hiệu quả.
- **Xử lý lỗi mạnh mẽ**: Phát hiện và báo cáo lỗi giao dịch blockchain và RPC.
- **Hỗ trợ song ngữ**: Hỗ trợ đầu ra bằng tiếng Anh và tiếng Việt tùy theo lựa chọn người dùng.
- **Hỗ trợ proxy**: Tùy chọn sử dụng proxy qua file `proxies.txt` cho các yêu cầu mạng.

### Các Script Bao Gồm

1. **Check-in Hàng ngày**: Thực hiện check-in hàng ngày để nhận phần thưởng trên Pharos Testnet.
2. **Triển khai Hợp đồng Token**: Triển khai hợp đồng thông minh ERC20 trên Pharos Testnet.
3. **Gửi Token ERC20**: Chuyển token ERC20 đến các địa chỉ ngẫu nhiên hoặc trong addressERC20.txt.
4. **Triển khai Hợp đồng NFT**: Triển khai hợp đồng thông minh NFT để tạo tài sản số độc nhất.
5. **Gửi Giao dịch (TX)**: Gửi giao dịch đến các địa chỉ ngẫu nhiên hoặc trong address.txt.
6. **Swap Token**: Hoán đổi token (PHRS, USDC, USDT) thông qua Zenith DEX trên Pharos Testnet.
7. **Thêm Thanh khoản**: Cung cấp thanh khoản cho các cặp token (PHRS, USDC, USDT) trên Zenith DEX.


## 🛠️ Yêu cầu trước khi sử dụng

Đảm bảo các yêu cầu sau được cài đặt và cấu hình:

- **Python**: Phiên bản 3.8 trở lên.
- **pip**: Trình quản lý gói Python.
- **Các gói phụ thuộc**: Cài đặt qua `pip install -r requirements.txt`. Các gói cần thiết bao gồm: ( `web3.py`, `colorama`, `asyncio`, `eth-account`, `aiohttp_socks` and `inquirer` ).
- **pvkey.txt**: File chứa khóa riêng (mỗi dòng một khóa) để tự động hóa ví.
- **Pharos Testnet RPC**: Truy cập qua điểm cuối RPC công khai (e.g., https://testnet.dplabs-internal.com or Pharos-specific RPC).
- **proxies.txt** (tùy chọn): Địa chỉ proxy cho các yêu cầu mạng.


## 📦 Cài đặt

Thực hiện các bước sau để thiết lập dự án:

1. **Clone this repository:**
- Mở cmd hoặc Shell, sau đó chạy lệnh:
```sh
git clone https://github.com/thog9/Pharos-testnet.git
```
```sh
cd Pharos-testnet
```
2. **Install Dependencies:**
- Mở cmd hoặc Shell, sau đó chạy lệnh:
```sh
pip install -r requirements.txt
```
3. **Prepare Input Files:**
- Mở `pvkey.txt`: Thêm khóa riêng của bạn (mỗi dòng một khóa) vào thư mục gốc.
```sh
nano pvkey.txt
```

- Tạo các file `address.txt`, `addressERC20.txt`, `contractNFT.txt`, `contractERC20.txt`, hoặc `proxies.txt` cho các thao tác cụ thể:
```sh
nano address.txt
nano addressERC20.txt
nano contractNFT.txt
nano contractERC20.txt
nano proxies.txt
```
4. **Run:**
- Mở cmd hoặc Shell, sau đó chạy lệnh:
```sh
python main.py
```
- Chọn ngôn ngữ (Tiếng Việt/Tiếng Anh).

## 📬 Liên hệ

Kết nối với chúng tôi để được hỗ trợ hoặc cập nhật:

- **Telegram**: [thog099](https://t.me/thog099)
- **Channel**: [CHANNEL](https://t.me/thogairdrops)
- **Group**: [GROUP CHAT](https://t.me/thogchats)
- **X**: [Thog](https://x.com/thog099) 

----

## ☕ Hỗ trợ chúng tôi:
Yêu thích các script này? Hãy mời chúng tôi một ly cà phê!

🔗 BUYMECAFE: [BUY ME CAFE](https://buymecafe.vercel.app/)
