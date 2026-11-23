#!/usr/bin/env python3
"""
agy_chinese.py - Chuong trinh luyen phan xa Tieng Trung Phon The & Khau ngu Dai Loan (A2+)
Phuong phap: Hoc theo cum phan xa (Chunks & Frames) de truc tiep tu duy, khong dich tu tieng Viet.
Dung cho ca User tu luyen qua terminal va AGY truc tiep kiem tra, ghi tien do.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Dam bao terminal Windows hien thi tieng Trung va dau phat am chuan xac
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "curriculum.json"
PROGRESS_FILE = BASE_DIR / "progress.json"


def load_curriculum():
    if not DATA_FILE.exists():
        print(f"[Lỗi] Không tìm thấy dữ liệu bài học tại {DATA_FILE}")
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_progress():
    if not PROGRESS_FILE.exists():
        return {
            "target_level": "A2_COLLOQUIAL",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_units": [],
            "chunk_stats": {},  # chunk -> {"pass": int, "fail": int, "last_tested": iso}
            "history": []
        }
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(progress):
    progress["updated_at"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def rec_result(progress, item_name, pass_fail=True):
    stats = progress.setdefault("chunk_stats", {})
    entry = stats.setdefault(item_name, {"pass": 0, "fail": 0, "last_tested": None})
    if pass_fail:
        entry["pass"] += 1
    else:
        entry["fail"] += 1
    entry["last_tested"] = datetime.now().isoformat()
    progress.setdefault("history", []).append({
        "time": datetime.now().isoformat(),
        "item": item_name,
        "result": "pass" if pass_fail else "fail"
    })


def cmd_list(args):
    curriculum = load_curriculum()
    progress = load_progress()
    print("=== DANH SÁCH BÀI HỌC PHẢN XẠ ĐÀI LOAN (TRÌNH ĐỘ A2) ===\n")
    for lvl in curriculum.get("levels", []):
        print(f"CẤP ĐỘ: {lvl['level']} - {lvl['title']}")
        for unit in lvl.get("units", []):
            status = "✓ Đã học" if unit["id"] in progress.get("completed_units", []) else "○ Chưa học"
            chunk_cnt = len(unit.get("chunks", []))
            frame_cnt = len(unit.get("frames", []))
            print(f"  [{status}] {unit['id']}: {unit['title']} ({chunk_cnt} cụm khẩu ngữ, {frame_cnt} cấu trúc khung)")
        print()


def cmd_study(args):
    curriculum = load_curriculum()
    target_id = args.unit_id.upper() if args.unit_id else "A2_REACTIONS"

    unit_found = None
    for lvl in curriculum.get("levels", []):
        for unit in lvl.get("units", []):
            if unit["id"] == target_id:
                unit_found = unit
                break
        if unit_found:
            break

    if not unit_found:
        print(f"[!] Không tìm thấy bài học có mã: {args.unit_id}")
        return

    print("=" * 65)
    print(f" BÀI HỌC: {unit_found['id']} - {unit_found['title']}")
    print(f" Ngữ cảnh: {unit_found.get('context', '')}")
    print("=" * 65 + "\n")

    print("--- 1. CỤM KHẨU NGỮ CỬA MIỆNG (CHUNKS) ---")
    for c in unit_found.get("chunks", []):
        print(f"▶ {c['chunk']}   [{c['pinyin']}]")
        print(f"   Ý nghĩa  : {c['meaning']}")
        if "vs_textbook" in c:
            print(f"   Khác SGK : {c['vs_textbook']}")
        if "tips" in c:
            print(f"   Mẹo dùng : {c['tips']}")
        print()

    if unit_found.get("frames"):
        print("--- 2. CẤU TRÚC KHUNG PHẢN XẠ (SENTENCE FRAMES) ---")
        for f in unit_found.get("frames", []):
            print(f"★ Khung: {f['pattern']}  [{f['pinyin']}] -> {f['meaning']}")
            print(f"  Ví dụ : {f['example_hanzi']}")
            print(f"  Pinyin: {f['example_pinyin']}")
            print(f"  Nghĩa : {f['example_vn']}\n")


def normalize_input(text):
    return text.strip().lower().replace(" ", "").replace("，", "").replace("。", "").replace("！", "").replace("!", "").replace("？", "").replace("?", "")


def cmd_reflex(args):
    """Luyện phản xạ tình huống: Đưa ra ngữ cảnh thực tế, yêu cầu bắn ra câu chuẩn Đài."""
    curriculum = load_curriculum()
    progress = load_progress()

    target_id = args.unit_id.upper() if args.unit_id else None
    all_challenges = []
    for lvl in curriculum.get("levels", []):
        for unit in lvl.get("units", []):
            if target_id and unit["id"] != target_id:
                continue
            for ch in unit.get("challenges", []):
                all_challenges.append((unit["id"], ch))

    if not all_challenges:
        print("[!] Không tìm thấy thử thách phản xạ nào cho bài này.")
        return

    print(f"=== LUYỆN PHẢN XẠ THỰC CHIẾN ({len(all_challenges)} tình huống) ===")
    print("Quy tắc: Nhập chữ Phồn thể hoặc Pinyin (không dấu hoặc có dấu). Gõ 'q' để thoát.\n")

    score = 0
    for idx, (unit_id, ch) in enumerate(all_challenges, 1):
        print(f"Tình huống {idx}: {ch['situation']}")
        user_input = input("Phản xạ của bạn: ").strip()
        if user_input.lower() == 'q':
            print("\nĐã tạm dừng luyện phản xạ.")
            return

        norm_user = normalize_input(user_input)
        norm_correct = normalize_input(ch['correct'])
        acceptable = [norm_correct] + [normalize_input(a) for a in ch.get("acceptable", [])]

        is_correct = any(norm_user == acc or norm_user in acc or acc in norm_user for acc in acceptable)

        if is_correct and len(norm_user) > 0:
            print("✓ CHUẨN ĐÀI LOAN!")
            print(f"  Câu bản xứ: {ch['correct']} [{ch['pinyin']}]\n")
            score += 1
            rec_result(progress, ch['correct'], pass_fail=True)
        else:
            print("✗ CHƯA CHUẨN!")
            print(f"  Người Đài sẽ nói: {ch['correct']}")
            print(f"  Pinyin          : {ch['pinyin']}\n")
            rec_result(progress, ch['correct'], pass_fail=False)

    save_progress(progress)
    print(f"Hoàn thành: {score}/{len(all_challenges)} tình huống phản xạ đúng.")


def cmd_record(args):
    """Cho phep agy hoac script ghi nhan ket qua sau moi buoi tro chuyen."""
    progress = load_progress()
    is_pass = (args.result.lower() in ["pass", "true", "1", "correct", "dung"])
    rec_result(progress, args.item, pass_fail=is_pass)
    save_progress(progress)
    print(f"[OK] Đã ghi nhận: {args.item} -> {'ĐÚNG' if is_pass else 'CHƯA ĐẠT'}")


def cmd_report(args):
    curriculum = load_curriculum()
    progress = load_progress()

    stats = progress.get("chunk_stats", {})
    weak_items = [k for k, v in stats.items() if v.get("fail", 0) > v.get("pass", 0)]
    strong_items = [k for k, v in stats.items() if v.get("pass", 0) > v.get("fail", 0)]

    report_data = {
        "level": progress.get("target_level", "A2"),
        "total_drills_done": len(progress.get("history", [])),
        "weak_points": weak_items,
        "mastered_points": strong_items,
        "recent_history": progress.get("history", [])[-5:]
    }

    if args.json:
        print(json.dumps(report_data, ensure_ascii=False, indent=2))
    else:
        print("=== BÁO CÁO TIẾN ĐỘ PHẢN XẠ (A2 THỰC CHIẾN ĐÀI LOAN) ===")
        print(f"Mục tiêu: {report_data['level']}")
        print(f"Số lượt phản xạ đã tập: {report_data['total_drills_done']}")
        print(f"Cụm/Cấu trúc còn yếu: {', '.join(weak_items) if weak_items else 'Chưa có điểm yếu'}")
        print(f"Cụm/Cấu trúc đã thuần thục: {', '.join(strong_items) if strong_items else 'Chưa có'}")
        print("=========================================================")


def self_test():
    curr = load_curriculum()
    assert len(curr.get("levels", [])) > 0, "Curriculum thieu levels"
    prog = load_progress()
    rec_result(prog, "TEST_A2", pass_fail=True)
    assert "TEST_A2" in prog["chunk_stats"]
    del prog["chunk_stats"]["TEST_A2"]
    prog["history"] = [h for h in prog.get("history", []) if h["item"] != "TEST_A2"]
    save_progress(prog)
    print("[TEST] Self-check A2 reflex engine PASSED.")


def main():
    parser = argparse.ArgumentParser(description="Chương trình luyện phản xạ khẩu ngữ Đài Loan A2+")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="Danh sách các cụm phản xạ theo chủ đề")
    
    p_study = subparsers.add_parser("study", help="Học các cụm phản xạ và cấu trúc khung")
    p_study.add_argument("unit_id", nargs="?", default="A2_REACTIONS", help="Mã bài học")

    p_reflex = subparsers.add_parser("reflex", help="Luyện phản xạ tình huống (nhập Pinyin hoặc Hanzi)")
    p_reflex.add_argument("unit_id", nargs="?", help="Mã bài học cụ thể")

    p_rec = subparsers.add_parser("record", help="Ghi nhận kết quả sau buổi roleplay")
    p_rec.add_argument("--item", required=True, help="Cụm từ hoặc câu")
    p_rec.add_argument("--result", required=True, choices=["pass", "fail", "1", "0"], help="pass hoặc fail")

    p_rep = subparsers.add_parser("report", help="Báo cáo tiến độ và điểm yếu")
    p_rep.add_argument("--json", action="store_true", help="Xuất JSON cho AI đọc")

    subparsers.add_parser("test", help="Chạy kiểm thử nội bộ")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "list":
        cmd_list(args)
    elif args.command == "study":
        cmd_study(args)
    elif args.command == "reflex":
        cmd_reflex(args)
    elif args.command == "record":
        cmd_record(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "test":
        self_test()


if __name__ == "__main__":
    main()
