# tools/ (không bắt buộc, có thể xoá khỏi repo)

`build_assets.py` sinh lại toàn bộ file trong `assets/` (chữ được chuyển thành path nên không phụ thuộc font).

```bash
pip install pillow fonttools
# tải 2 font: Unbounded[wght].ttf và SpaceGrotesk[wght].ttf (Google Fonts, OFL) vào cùng thư mục
python build_assets.py ../assets source/blackhole_disk.png source/blackhole_duo.png
```

Ảnh trong `source/` là hai ảnh mô phỏng hố đen bạn cung cấp. Hãy kiểm tra nguồn và giấy phép của chúng
(nếu là ảnh NASA thì thường dùng tự do kèm ghi công) trước khi công khai.
