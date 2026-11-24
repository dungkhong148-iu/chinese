---
name: eval
description: Chấm điểm thực chiến đa chiều, phân tích phong cách (Đài Loan / Tiêu chuẩn) và cập nhật tiến độ cho phiên 10 câu vừa nộp
---

# /eval - Chấm điểm phiên 10 câu thực chiến đa chiều

Khi người dùng gọi lệnh `/eval` (hoặc gõ dấu phẩy `,` đầu câu):
1. Đọc kết quả người dùng nộp tại `data/session_output.json`.
2. **Nguyên tắc chấm điểm nghiêm khắc (Không chấm 10/10 dễ dãi)**:
   - **Thang điểm 4 bậc**:
     - **9-10 điểm**: Phản xạ tự nhiên chuẩn bản xứ, EQ cao, bắt nhịp cảm xúc hoàn hảo.
     - **7-8 điểm**: Đúng ngữ pháp/ngữ nghĩa nhưng còn mang tính sách vở, trịnh trọng quá mức hoặc chịu ảnh hưởng nhẹ từ tiếng Việt.
     - **4-6 điểm**: Lúng túng, dùng từ chưa đúng bối cảnh, giao tiếp bị sượng hoặc dễ gây hiểu nhầm.
     - **0-3 điểm**: Hiểu sai ngữ cảnh, dùng sai từ làm vỡ mạch kịch bản.
   - **Tôn trọng phong cách**: Cả phong cách Đài Loan (vd: *真的假的*, *看你啊*, *沒差*) và Tiêu chuẩn (vd: *真的嗎*, *隨便*, *沒關係*) đều được công nhận nếu tự nhiên.
3. **Phân tích "Góc nhìn người bản xứ"**:
   - Chỉ rõ người học đang phản xạ theo kiểu gì (Đài Loan / Phổ thông / Dịch word-by-word từ tiếng Việt).
   - Người đối diện sẽ cảm thấy thế nào khi nghe câu đó (tự nhiên, thân thiện, lạnh lùng, hay gượng gạo?).
   - Gợi ý câu thay thế mượt mà hơn để nâng trình giao tiếp.
4. **Format xuất bài chữa (Caveman-style: gọn, thẳng trọng tâm, dễ quét mắt)**:
   - **Header 1 dòng**:
     `Điểm: X/100 (TB: Y/10) | Thời gian: Zs | Phong cách chính: [Đài Loan / Tiêu chuẩn / Dịch Việt]`
   - **Bảng tóm tắt 10 câu**:
     `| # | Bạn trả lời | Điểm | Chốt nhanh |`
   - **Chữa chi tiết từng câu** (câu 9–10 điểm chỉ chốt 1 dòng; câu < 9 điểm bóc đủ 4 ý):
     - *Câu 9–10 điểm*: `**Câu X (9/10) ✅** "<user_answer>" — Tự nhiên, đúng ngữ cảnh.`
     - *Câu < 9 điểm*:
       ```markdown
       **Câu X (Y/10)** — [Bối cảnh ngắn]
       - **Bạn**: `<user_answer>`
       - **Lỗi & Bản xứ**: <Sai đâu / sượng đâu / người nghe cảm thấy thế nào (1 dòng)>
       - **Sửa chuẩn**: `<Chữ Phồn thể>` [`<Pinyin>`] — `<Nghĩa>` *(Hán-Việt từ khóa)*
       ```
   - **Tổng kết cải thiện (3 dòng)**:
     - **Điểm mạnh**: ...
     - **Lỗi lặp lại cần sửa**: ...
     - **Từ/cụm yếu cần ôn lại**: ...
5. **Cập nhật dữ liệu (chạy ngầm sau khi chấm)**:
   - Cập nhật đúng **duy nhất 1 gạch đầu dòng** trong `process.md` phản ánh chân dung & thói quen ngôn ngữ hiện tại của người học.
   - Ghi nhận pass/fail vào `progress.json`.
