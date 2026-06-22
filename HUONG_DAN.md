# Hướng dẫn: Upload video review thật vào repo `poh-video-render`

Bộ file này khác bản test trước ở chỗ: **nội dung thật** (sách Simple
Christian, The Happi Pabi) + **giọng đọc thật** (workflow tự sinh bằng AI
giọng đọc local, không cần bạn thu âm) + **animation tự canh khớp** theo
đúng độ dài giọng đọc thật, không phải số ước lượng.

Đã test kỹ trước khi gửi:
- `hyperframes lint` → 0 lỗi
- `hyperframes compositions` → xác nhận cơ chế ghép audio-animation hoạt
  động đúng (test với audio giả nhiều độ dài khác nhau, animation luôn
  khớp chính xác).

## Bước 1 — Upload vào repo CŨ (không cần tạo repo mới)
1. Vào repo `poh-video-render` đã tạo lần trước.
2. **Xoá file `index.html` cũ** (mở file → icon thùng rác góc phải → Commit).
3. **Add file → Upload files** → kéo thả các file/thư mục sau:
   - `index.html` (bản mới)
   - `assets/` (4 file narration-*.txt)
   - `scripts/` (build_timing.py)
   - `METADATA.md`, `SCRIPT.md`
4. Commit changes.

## Bước 2 — Cập nhật workflow
File `.github/workflows/render.yml` lần này **khác hẳn** bản cũ (có thêm
bước sinh giọng đọc) — thay bằng cách:
1. Vào `.github/workflows/render.yml` trong repo → bấm icon bút chì (Edit).
2. Xoá hết nội dung cũ, dán nội dung file `render.yml` mới (trong zip) vào.
3. Commit changes.

## Bước 3 — Chạy
1. Tab **Actions** → chọn workflow **"Render Amazon Review Video"**.
2. **Run workflow** → **Run workflow** (xác nhận).
3. Lần này lâu hơn bản test một chút (~6-10 phút thay vì 3-6 phút) vì có
   thêm 4 bước sinh giọng đọc AI. Đợi tới dấu ✓ xanh.

## Bước 4 — Tải về
- Cuộn xuống cuối trang chạy → **Artifacts** → có 2 file:
  - **amazon-review-video** → video MP4 hoàn chỉnh (có giọng đọc + animation khớp)
  - **narration-audio** → 4 file giọng đọc riêng (phòng khi muốn nghe lại/chỉnh)
- Nhớ: tải về là `.zip`, giải nén ra mới thấy file thật bên trong.

## Trước khi đăng video thật lên YouTube
- `METADATA.md` có sẵn title/description/tags/thumbnail text — nhưng
  mình **chưa lấy được giá và số sao thật** của sản phẩm (Amazon chặn bot
  đọc trang), nên script chỉ nói "check current price", không nêu số cụ
  thể. Bạn tự mở trang Amazon kiểm tra giá trước khi đăng, ghi vào
  description nếu muốn.
- Giọng đọc dùng giọng nữ ấm mặc định (`af_heart`) của engine local trong
  HyperFrames — nếu muốn đổi giọng khác, sửa cờ `-v` trong workflow (các
  giọng khác: `af_nova`, `af_sky`, `am_adam`, `am_michael`...).

## Nếu muốn video dài hơn / roundup nhiều sản phẩm
Cấu trúc 4-đoạn audio + 4-cảnh này nhân rộng được — báo mình, mình viết
thêm narration + scene cho từng sản phẩm tiếp theo, đẩy vào đúng pattern
này (audio chain + scene chain tự canh khớp, không phải tính tay).
