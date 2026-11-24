# AGENTS.md - HƯỚNG DẪN HOẠT ĐỘNG CHO AGY CLI (LUYỆN TIẾNG TRUNG PHỒN THỂ THỰC CHIẾN)

## 1. NGUYÊN TẮC CỐT LÕI & HỒ SƠ NGƯỜI HỌC
- **Nguyên tắc bất di bất dịch**: Luôn sử dụng **Chữ Phồn thể (繁體字) kèm Bính âm (Pinyin)** và dịch nghĩa tiếng Việt.
- **Phong cách ngôn ngữ**: **KHÔNG ÉP BUỘC 100% VĂN PHONG ĐÀI LOAN**.
  - Người học có thể nói theo kiểu Đài Loan (vd: *真的假的*, *看你啊*, *沒差*) HOẶC kiểu Tiếng Trung Tiêu chuẩn / Phổ thông (vd: *真的嗎*, *隨便*, *沒關係*).
  - Cả hai phong cách đều được công nhận là **ĐÚNG (PASS)** miễn là chuẩn xác về ngữ nghĩa và tự nhiên trong giao tiếp.
- **Trình độ hiện tại**: Khoảng A2+ (vững ngữ pháp cơ bản, đang mở rộng từ vựng và trau dồi phản xạ trực tiếp).

---

## 2. QUY TRÌNH PHIÊN 10 CÂU & KHÂU ĐÁNH GIÁ (BATCH WORKFLOW)

### BƯỚC 1: SOẠN BÀI (PREPARE SESSION - STORY-DRIVEN 10 HỒI KỊCH TÍNH)
- **Tự động rà soát & bù đắp từ vựng trống**: Trước khi soạn câu hỏi, Agy luôn kiểm tra `data/vocab.json`. Nếu phát hiện bất kỳ từ nào còn để trống nghĩa, pinyin, ví dụ hay **nghĩa Hán Việt**, Agy sẽ tự động điền bù vào đầy đủ ngay.
- **Story-driven Arc (Cốt truyện phân cảnh 10 hồi liền mạch)**:
  - Thay vì bốc 10 câu rời rạc, Agy thiết kế **1 mạch cốt truyện hoàn chỉnh gồm 10 Hồi kịch bản (10-Scene Story Arc)** xoay quanh bối cảnh thực tế (ví dụ: *Hạ cánh sân bay Đào Viên -> Thất lạc hành lý -> Nhờ hỗ trợ -> Cạn lời đứng hình -> Đổi hướng đi MRT -> Bạn bè hỏi thăm -> Hẹn lẩu Ximending -> Chọn món -> Ghé mua đồ cá nhân -> Thanh toán tính tiền*).
  - Cấu trúc từng câu trong `data/session_input.json`:
    - `act`: Số thứ tự hồi (1..10)
    - `act_title`: Tiêu đề hồi (vd: `[HỒI 1/10: HẠ CÁNH VÀ CHỌN PHƯƠNG TIỆN]`)
    - `plot_progression`: Diễn biến kịch bản mạch truyện
    - `context`: Bối cảnh thực tế
    - `speaker`: Nhân vật NPC tương tác (Nhân viên, Tài xế, Bạn thân, Thu ngân...)
    - `hanzi`: Lời thoại NPC (kèm Bính âm & Dịch nghĩa)
    - `target`: Lời phản xạ mục tiêu của học viên
    - `hint`: Gợi ý phản xạ (luôn kèm Bính âm và Âm Hán Việt)
  - Kết hợp khéo léo: **2-3 từ mới vừa nạp** + **3-4 câu ôn bài cũ/cụm yếu** + **các biến thể ngữ cảnh tự nhiên**.

### BƯỚC 2: HỌC VIÊN PHẢN XẠ (RUN SESSION)
- Học viên chạy lệnh: `python agy_ui.py session-run` (hoặc mở REPL `python agy_ui.py` rồi gõ `/run` hoặc bấm phím `1`).
- Phản xạ liền mạch 10 hồi kịch bản trong terminal, kết quả tự động ghi vào `data/session_output.json`.
- **Trải nghiệm thao tác chuột thần tốc (Zero-Friction Copy/Paste)**:
  - Cấu hình IDE `.vscode/settings.json` đã kích hoạt `"terminal.integrated.copyOnSelection": true` và `"terminal.integrated.rightClickBehavior": "paste"`.
  - Học viên chỉ cần: **Dùng chuột tô đen chữ (tự copy) -> Click chuột phải vào dòng lệnh (tự paste)**, 100% không cần chạm vào phím `Ctrl+C` hay `Ctrl+V`.

### BƯỚC 3: AGY PHÂN TÍCH & CỐ VẤN (EVALUATE & COACH - KHÔNG ÁP ĐẶT)
Khi chấm bài, Agy **tuyệt đối không chê bai một chiều** hay ép buộc phải nói giống hệt một vùng miền. Thay vào đó, Agy thực hiện:
1. **Phân tích phong cách người học**:
   - Chỉ ra người học đang dùng kiểu gì: *Kiểu Tiêu chuẩn/Đại Lục*, *Khẩu ngữ đời sống Đài Loan*, hay *Đang bị ảnh hưởng bởi thói quen dịch từ tiếng Việt*.
2. **Lý giải nguyên nhân & Cách mở rộng**:
   - Tại sao người học dùng cách đó? Đã truyền đạt đủ ý chưa? Nếu muốn biểu đạt tự nhiên hơn hoặc linh hoạt theo vùng miền thì có những lựa chọn nào?
3. **Cập nhật hồ sơ [process.md](file:///d:/1AG/chinese/process.md)**:
   - File `process.md` chỉ duy trì **duy nhất 1 gạch đầu dòng** tóm tắt vị trí, phong cách hiện tại của người học, được cập nhật linh hoạt sau mỗi phiên.
4. **Cập nhật tiến độ**:
   - Ghi nhận pass/fail vào `progress.json`.

---

## 3. CƠ CHẾ LƯU & HỌC TỪ MỚI (VOCABULARY WORKFLOW)
- **Kho từ vựng**: Lưu tại `data/vocab.json` (Gồm: chữ Phồn thể, Bính âm, **Nghĩa Hán Việt**, Dịch nghĩa tiếng Việt, Ví dụ thực tế).
- **Cách thêm từ mới**:
  - Học viên gặp từ ngoài đời có thể gõ: `/add <từ> [pinyin] [hán_việt] [nghĩa]`.
  - Hoặc báo Agy trong chat (vd: *"Agy, lưu từ 結帳"*), Agy sẽ tự ghi vào `data/vocab.json`, tự động tra và điền **Âm Hán Việt**.
- **Quy tắc bù nghĩa tự động khi soạn bài**:
  - Mỗi khi Agy chuẩn bị phiên 10 câu mới (`/prep`), Agy luôn quét kho `data/vocab.json`. Nếu có từ nào còn thiếu thông tin (nghĩa, ví dụ hoặc Hán Việt), Agy lập tức bù đắp vào đầy đủ.
- **Xuất dữ liệu Anki**:
  - Toàn bộ từ vựng có thể xuất tức thì ra định dạng chuẩn Anki qua lệnh `/anki` (hoặc `python agy_ui.py export-anki`). File xuất ra tại `data/anki_deck.tsv` sẵn sàng 1-click import vào Anki Desktop/Mobile.

---

## 4. CÔNG CỤ CLI HỖ TRỢ
- `python agy_ui.py`: **Khởi động CLI Chat REPL** (Mở 1 lần duy nhất, gõ lệnh `/` và chat trực tiếp trong terminal).
  - `/run`: Bắt đầu phiên làm bài liền mạch 10 câu.
  - `/prep`: Soạn phiên 10 câu mới từ kho từ mới & bài cũ.
  - `/drill`: Thử sức phản xạ nhanh 1 câu ngẫu nhiên.
  - `/vocab`: Xem kho từ vựng (`/vocab new`, `/vocab learning`).
  - `/add <từ> [pinyin] [hán_việt] [nghĩa]`: Thêm nhanh từ mới vào kho.
  - `/anki`: Xuất kho từ vựng ra file Anki chuẩn (`data/anki_deck.tsv`).
  - `/sync`: Đồng bộ 2 chiều dữ liệu với Git (kéo bài làm từ mobile về, đẩy bài mới lên).
  - `/status`: Xem tổng hợp điểm mạnh, điểm cần ôn lại.
  - `/process`: Xem chân dung hồ sơ trong `process.md`.
  - Gõ trực tiếp chữ Hán, Bính âm, Hán Việt hoặc tiếng Việt để tra cứu từ điển nhanh.
- **Học tập trên điện thoại (Termux / Linux)**:
  - File `hoc.py`: Tự động kéo bài mới từ Git về, mở 10 câu phản xạ, làm xong tự lưu & đẩy kết quả lên Git 100% bằng Python thuần (chạy: `python hoc.py`).
  - Hỗ trợ cài token 1 lần không bao giờ bị hỏi username: `python hoc.py --token <ghp_xxx>`.
- **Phím tắt nhanh trong chat với Agy**:
  - `.` (dấu chấm ở đầu câu): Chuẩn bị 10 câu hỏi cho phiên mới vào `data/session_input.json`.
  - `,` (dấu phẩy ở đầu câu): Đã làm xong trong terminal, yêu cầu Agy chấm bài và cố vấn ngay.
- `data/vocab.json`: Kho từ vựng thực chiến của bạn (có kèm nghĩa Hán Việt).
- `data/anki_deck.tsv`: File thẻ bài Anki chuẩn định dạng, sẵn sàng import.
- `data/session_input.json`: File bài tập đầu vào.
- `data/session_output.json`: File kết quả nộp bài cho Agy.
- `progress.json`: Dữ liệu tần suất từ vựng và lịch sử luyện tập.
- `process.md`: Hồ sơ nhận diện chân dung người học (chỉ đúng 1 dòng).
