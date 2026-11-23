---
name: vocab
description: Xem, tra cứu và thêm từ vựng mới vào kho thực chiến data/vocab.json
---

# /vocab - Quản lý từ vựng thực chiến

Khi người dùng gọi lệnh `/vocab`:
1. Nếu có tham số từ mới (ví dụ `/vocab add 搞定 gǎodìng xong xuôi`), chạy `python agy_ui.py add-vocab ...`
2. Nếu gọi `/vocab`, chạy `python agy_ui.py list-vocab` để xuất danh sách từ vựng.
