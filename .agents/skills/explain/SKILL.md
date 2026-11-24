---
name: explain
description: Giải bài tập (trong session_input.json hoặc câu bất kỳ) và giải thích ngữ pháp, từ vựng Phồn thể, Hán-Việt, sắc thái bản xứ theo phong cách Caveman: ngắn gọn, đi thẳng vào trọng tâm.
---

# /explain - Giải bài & Giải thích trọng tâm (Caveman Mode)

Khi người dùng gọi `/explain` hoặc nhờ giải bài / giải thích (vd: "giải câu 3", "tại sao dùng chữ này", "câu này nói sao"):

## Nguyên tắc trình bày (Caveman-style)
- **Không rào đón, không dài dòng.** Bỏ toàn bộ lời chào, khen ngợi, giải thích vòng vo.
- **Đáp án trước, lý do sau.** Mỗi ý tối đa 1-2 dòng, dùng gạch đầu dòng.
- **Bắt buộc**: Luôn có **Chữ Phồn thể (繁體字) + Pinyin + Âm Hán Việt** cho từ khóa.
- **Phong cách**: Chấp nhận cả Đài Loan lẫn Phổ thông (chỉ cần Phồn thể + tự nhiên).

## Quy trình
1. **Lấy ngữ cảnh**:
   - Nếu hỏi theo số câu/hồi -> đọc `data/session_input.json` (và `data/session_output.json` nếu cần đối chiếu).
   - Nếu hỏi từ/câu ngoài -> phân tích trực tiếp (có thể tra `data/dictionary.db` nếu cần xác minh nghĩa/Hán-Việt).
2. **Xuất kết quả đúng 4 mục gọn**:
   - **Chốt câu**: `<Chữ Phồn thể>` [`<Pinyin>`] — `<Nghĩa tiếng Việt>` *(ghi chú nếu Đài Loan / Tiêu chuẩn khác nhau)*.
   - **Từ khóa + Hán-Việt**: Liệt kê 2–4 từ lõi (`Từ [Pinyin] (Hán-Việt): nghĩa`).
   - **Cấu trúc / Lý do (1-2 dòng)**: Giải thích tại sao ghép vậy, khác gì thói quen dịch từng chữ tiếng Việt.
   - **Lưu ý bản xứ (1 dòng)**: Ngữ điệu, bối cảnh dùng, hoặc bẫy sai phổ biến.
