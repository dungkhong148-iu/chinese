---
name: anki
description: Xuất kho từ vựng tiếng Trung phồn thể ra file Anki (.tsv) để import vào Anki Desktop/Mobile
---

# /anki - Xuất file Anki

Khi người dùng gọi lệnh `/anki`:
1. Chạy lệnh: `python agy_ui.py export-anki`.
2. Kiểm tra file `data/anki_deck.tsv`.
3. Báo cho người dùng:
   "Đã xuất toàn bộ từ vựng ra `data/anki_deck.tsv`!
   Để học trên Anki: Mở Anki -> Chọn 'File' -> 'Import' -> Chọn `data/anki_deck.tsv`."
