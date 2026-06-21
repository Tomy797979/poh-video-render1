# Hướng dẫn: Render video bằng GitHub Actions (không cần code)

Bộ file này gồm:
- `index.html` — video mẫu 12 giây, 16:9, theo brand Path of the Heart (intro → top pick → CTA), có sẵn dòng disclosure Amazon.
- `hyperframes.json`, `meta.json`, `package.json` — file cấu hình bắt buộc của HyperFrames.
- `.github/workflows/render.yml` — "công thức" để GitHub tự cài Chrome + FFmpeg và render ra MP4 giúp bạn.

Đã lint sạch lỗi (`hyperframes lint` → 0 error) trước khi gửi bạn.

## Bước 1 — Tạo repo trên GitHub
1. Vào github.com → đăng nhập (hoặc tạo tài khoản free nếu chưa có).
2. Bấm **New repository**.
3. Đặt tên (vd: `poh-video-render`), chọn **Private** (để giữ kín nội dung/kịch bản), bấm **Create repository**.

## Bước 2 — Upload toàn bộ thư mục này
1. Trong repo vừa tạo, bấm **Add file → Upload files**.
2. Kéo thả **toàn bộ thư mục đã giải nén** (`index.html`, `hyperframes.json`, `meta.json`, `package.json`, và thư mục `.github`) vào khung upload.
3. Bấm **Commit changes**.

> ⚠️ Nếu kéo cả thư mục không giữ đúng cấu trúc `.github/workflows/render.yml`: vào **Add file → Create new file**, gõ thẳng đường dẫn `.github/workflows/render.yml` vào ô tên file, dán nội dung file `render.yml` vào, rồi Commit. Cách này luôn chắc ăn 100%.

## Bước 3 — Chạy render
1. Vào tab **Actions** ở trên repo.
2. Bên trái chọn workflow **"Render HyperFrames Video"**.
3. Bấm nút **Run workflow** (màu xanh, góc phải) → **Run workflow** lần nữa để xác nhận.
4. Đợi khoảng 3-6 phút (vòng tròn vàng đang chạy → dấu tick xanh là xong).

## Bước 4 — Tải video về
1. Bấm vào lần chạy vừa xong (dòng có dấu tick xanh).
2. Kéo xuống cuối trang, mục **Artifacts** → bấm **rendered-video** để tải file `.mp4` về máy.

## Chi phí
- Repo Private: GitHub cho free 2.000 phút chạy Actions/tháng. Video 12s này tốn khoảng 3-6 phút/lần render → render vài chục lần/tháng vẫn miễn phí.
- Repo Public: Actions miễn phí không giới hạn, nhưng nội dung video/script sẽ public.

## Sau khi xem video mẫu
Nếu animation ổn, bước tiếp theo mình có thể:
- Viết composition riêng cho từng video roundup/Shorts thật (thay placeholder text bằng tên sản phẩm thật).
- Tự động hoá: nối bước này vào skill `video-marketing-auto` hiện có — sau khi viết script + giọng đọc xong, tự tạo luôn file composition mới và (nếu muốn) tự động trigger workflow này qua GitHub API, kết quả đẩy thẳng vào Dropbox bạn đang dùng — không cần bấm tay từng bước nữa.
