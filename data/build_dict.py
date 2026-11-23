import sqlite3
import csv
import ast
import re
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "dictionary.db"
CVDICT_FILE = BASE_DIR / "CVDICT.u8"
HANVIET_FILE = BASE_DIR / "hanviet.csv"

def build():
    t0 = time.time()
    print("1. Đang nạp bảng Hán Việt...")
    hv_map = {}
    with open(HANVIET_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 2:
                ch = row[0]
                try:
                    readings = ast.literal_eval(row[1])
                    if ch not in hv_map:
                        hv_map[ch] = []
                    for r in readings:
                        if r not in hv_map[ch]:
                            hv_map[ch].append(r)
                except Exception:
                    pass

    def get_hanviet(word):
        res = []
        for c in word:
            if c in hv_map and hv_map[c]:
                res.append(hv_map[c][0].capitalize())
            else:
                res.append(c)
        return " ".join(res)

    print(f"   Đã nạp {len(hv_map)} chữ Hán đơn kèm âm Hán Việt.")

    print("2. Đang tạo cơ sở dữ liệu SQLite...")
    if DB_FILE.exists():
        DB_FILE.unlink()

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            traditional TEXT NOT NULL,
            simplified TEXT NOT NULL,
            pinyin TEXT,
            han_viet TEXT,
            meaning TEXT
        )
    """)

    print("3. Đang xử lý 122,591 mục từ từ CVDICT.u8...")
    line_pattern = re.compile(r"^(\S+)\s+(\S+)\s+\[(.*?)\]\s+/(.*)/$")
    records = []

    with open(CVDICT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = line_pattern.match(line)
            if m:
                trad, simp, pinyin, meaning_raw = m.groups()
                meaning = meaning_raw.replace("/", "; ").strip("; ")
                hv = get_hanviet(trad)
                records.append((trad, simp, pinyin, hv, meaning))

    print(f"   Đang lưu {len(records)} từ vào database...")
    c.executemany("""
        INSERT INTO words (traditional, simplified, pinyin, han_viet, meaning)
        VALUES (?, ?, ?, ?, ?)
    """, records)

    print("4. Đang tạo index tìm kiếm siêu tốc...")
    c.execute("CREATE INDEX idx_trad ON words(traditional);")
    c.execute("CREATE INDEX idx_simp ON words(simplified);")
    c.execute("CREATE INDEX idx_pinyin ON words(pinyin);")
    c.execute("CREATE INDEX idx_hanviet ON words(han_viet);")

    conn.commit()
    conn.close()

    db_size = round(DB_FILE.stat().st_size / (1024 * 1024), 2)
    print(f"[THÀNH CÔNG] Cơ sở dữ liệu từ điển: {DB_FILE} ({db_size} MB) hoàn tất trong {round(time.time() - t0, 2)}s!")

if __name__ == "__main__":
    build()
