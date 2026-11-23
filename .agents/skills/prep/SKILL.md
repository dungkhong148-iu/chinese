---
name: prep
description: Soạn phiên 10 câu phản xạ thực chiến mới kết hợp từ vựng mới và bài cũ còn yếu
---

# /prep - Soạn phiên 10 câu mới

Khi người dùng gọi lệnh `/prep`:
1. Chạy `python agy_ui.py session-prepare --count 10`.
2. Kiểm tra file `data/session_input.json`.
3. Báo ngắn gọn cho người dùng:
   "Đã soạn xong 10 câu mới vào data/session_input.json. Mở terminal gõ `python agy_ui.py` rồi chọn `/run` (hoặc phím 1) để bắt đầu luyện tập!"
