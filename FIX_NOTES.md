# Sửa lỗi: thiếu giọng đọc + thiếu hình ảnh Amazon

## Lỗi 1a: Giọng đọc bị cắt cụt (đã sửa)

**Nguyên nhân thật:** Engine TTS tích hợp của HyperFrames (Kokoro-82M) có
giới hạn đã biết — nó KHÔNG tự chia nhỏ đoạn văn dài, và khi đưa cả đoạn
~100 từ vào, nó chỉ đọc vài giây đầu rồi dừng lại, không báo lỗi gì (đây là
hạn chế ai dùng Kokoro cũng gặp, có ghi trong nhiều issue của cộng đồng).

**Cách sửa:** Chia 4 đoạn lớn thành 24 câu/cụm ngắn (dưới 22 từ mỗi cụm),
gọi TTS riêng cho từng cụm.

## Lỗi 1b: Chỉ nghe được voice-01 (~6s), phần còn lại im lặng (đã sửa)

**Nguyên nhân:** Sau khi chia thành 24 file audio ngắn, lúc đầu mình ghép
chúng vào composition bằng cách nối tiếp 24 thẻ `<audio>` riêng biệt. Phần
xử lý bên trong của engine render khi ghép NHIỀU file audio rời rạc trên
cùng 1 track có vẻ chỉ xử lý đúng file đầu tiên, các file sau bị bỏ qua.

**Cách sửa:** Thay vì để engine tự ghép 24 file rời rạc lúc render, giờ
**gộp sẵn cả 24 file thành 1 file âm thanh duy nhất bằng ffmpeg** ngay
trong workflow (bước mới "Concatenate narration chunks into a single audio
file"), rồi chỉ đưa **1 thẻ `<audio>` duy nhất** vào composition. Cách này
loại bỏ hoàn toàn khả năng lỗi ở bước ghép nhiều clip.

Đã test lại: ghép 24 file audio giả → tổng thời lượng khớp chính xác với
tính toán → lint 0 lỗi → composition chỉ còn 6 phần tử (gọn hơn nhiều, ít
khả năng lỗi hơn).

**Cần thay 2 file** trong repo (build_timing.py giữ nguyên, KHÔNG cần
thay lại file này):
1. `.github/workflows/render.yml` — thêm bước "Concatenate narration
   chunks into a single audio file" sau bước tạo 24 file âm thanh.
2. `index.html` — 24 thẻ `<audio>` rút gọn còn đúng 1 thẻ duy nhất trỏ
   tới `narration-full.wav`.

(Nếu bạn chưa từng thêm 24 file `narration-01.txt`..`narration-24.txt`
vào `assets/` từ vòng sửa trước, vẫn cần làm bước đó trước — xem lại phần
checklist ở tin nhắn trước.)

## Lỗi 2: Hình ảnh — ĐÃ TỰ ĐỘNG HOÁ

Workflow giờ tự tải ảnh bìa thật từ URL Amazon (lấy thẻ `og:image` trên
trang sản phẩm), lưu vào `assets/cover.jpg`, hiển thị bên trái Scene 1.

- URL Amazon giờ là **input của workflow** — khi bấm "Run workflow" sẽ
  thấy 1 ô để dán URL (mặc định đã điền sẵn link cuốn Simple Christian).
  Lần sau làm sản phẩm khác chỉ cần đổi URL ở đây, không cần sửa file.
- Nếu Amazon chặn request (datacenter IP của GitHub đôi khi bị chặn khác
  với máy cá nhân) → tự động dùng 1 khối màu plum thay thế, KHÔNG làm
  hỏng video, chỉ là không có ảnh thật lần đó. Bước "Report cover image
  status" trong log sẽ ghi rõ ảnh thật hay ảnh dự phòng.
- Đây là cách lấy ảnh không chính thức (đọc thẳng trang sản phẩm) — không
  phải API chính thức của Amazon. Về lâu dài, khi tài khoản Associate của
  bạn đủ điều kiện (cần có giao dịch qua link affiliate), Amazon Product
  Advertising API sẽ là cách lấy ảnh ổn định, đúng quy định hơn. Báo mình
  khi đủ điều kiện, mình chuyển sang dùng API đó.

## Về "tự động hoá hoàn toàn"

Phần **cơ học** (ảnh, giọng đọc, ghép animation, render) giờ tự động hết
qua workflow này. Phần **viết script** (research sản phẩm, viết lời thoại)
mình đề xuất vẫn giữ người (mình) review trước khi đưa vào pipeline —
để tránh script tự sinh bịa thông tin sản phẩm khi không có ai kiểm tra.
Nếu bạn vẫn muốn tự động hoá luôn cả bước viết script (paste URL → ra
video hoàn chỉnh không cần duyệt), báo mình, đó là làm được nhưng nên cân
nhắc rủi ro thông tin sai trước khi bật full-auto.

