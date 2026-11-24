#!/usr/bin/env python3
"""
agy_ui.py - Interactive CLI Chat & Terminal UI chuyen biet cho agy
- Mo 1 lan la tro chuyen, luyen tap, go lenh / nhu CLI chuyen nghiep
- Ho tro ca che do chay lenh don le va REPL CLI Chat
"""

import sys
import json
import argparse
import shutil
import time
import random
import os
import sqlite3
from pathlib import Path
from datetime import datetime

# Dam bao terminal Windows khong bi loi font ky tu tieng Trung va dau bính âm
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


def setup_terminal_features():
    """Kích hoạt QuickEdit mode (copy/paste chuột) và Virtual Terminal Processing trên Windows."""
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            
            # Enable QuickEdit on STDIN
            hStdin = kernel32.GetStdHandle(-10)  # STD_INPUT_HANDLE
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(hStdin, ctypes.byref(mode)):
                ENABLE_QUICK_EDIT_MODE = 0x0040
                ENABLE_EXTENDED_FLAGS = 0x0080
                kernel32.SetConsoleMode(hStdin, mode.value | ENABLE_QUICK_EDIT_MODE | ENABLE_EXTENDED_FLAGS)
            
            # Enable Virtual Terminal Processing on STDOUT
            hStdout = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            out_mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(hStdout, ctypes.byref(out_mode)):
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                kernel32.SetConsoleMode(hStdout, out_mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
        except Exception:
            pass


setup_terminal_features()

BASE_DIR = Path(__file__).resolve().parent
PROGRESS_FILE = BASE_DIR / "progress.json"
DATA_FILE = BASE_DIR / "data" / "curriculum.json"
VOCAB_FILE = BASE_DIR / "data" / "vocab.json"
PROCESS_FILE = BASE_DIR / "process.md"
DICT_DB = BASE_DIR / "data" / "dictionary.db"

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[90m"


def get_terminal_width():
    try:
        w = shutil.get_terminal_size((80, 24)).columns
        return min(max(w, 60), 85)
    except Exception:
        return 75


def draw_box(title, lines, color=CYAN):
    w = get_terminal_width()
    top = f"{color}┌─ {BOLD}{title}{RESET}{color} " + "─" * max(0, w - len(title) - 6) + f"┐{RESET}"
    bottom = f"{color}└" + "─" * (w - 2) + f"┘{RESET}"

    print(top)
    for line in lines:
        if line == "---":
            print(f"{color}├" + "─" * (w - 2) + f"┤{RESET}")
        else:
            print(f"{color}│{RESET}  {line}")
    print(bottom)


def load_progress():
    if not PROGRESS_FILE.exists():
        return {
            "target_level": "A2_COLLOQUIAL",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_units": [],
            "chunk_stats": {},
            "history": []
        }
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"target_level": "A2", "chunk_stats": {}, "history": []}


def save_progress(progress):
    progress["updated_at"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def load_vocab():
    if not VOCAB_FILE.exists():
        return []
    try:
        with open(VOCAB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_vocab(vocab_list):
    VOCAB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(VOCAB_FILE, "w", encoding="utf-8") as f:
        json.dump(vocab_list, f, ensure_ascii=False, indent=2)


def query_dict_db(word, limit=5):
    """Tra cuu truc tiep tu co so du lieu 122k tu CVDICT offline."""
    if not DICT_DB.exists():
        return []
    try:
        conn = sqlite3.connect(DICT_DB)
        c = conn.cursor()
        w = word.strip()
        c.execute("""
            SELECT traditional, pinyin, han_viet, meaning 
            FROM words 
            WHERE traditional = ? OR simplified = ?
            LIMIT ?
        """, (w, w, limit))
        rows = c.fetchall()
        if not rows:
            like_q = f"%{w}%"
            c.execute("""
                SELECT traditional, pinyin, han_viet, meaning 
                FROM words 
                WHERE traditional LIKE ? OR meaning LIKE ? OR han_viet LIKE ?
                LIMIT ?
            """, (like_q, like_q, like_q, limit))
            rows = c.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def add_or_update_vocab(hanzi, pinyin="", han_viet="", meaning="", style="Đời sống", context=""):
    vocab = load_vocab()

    # Neu thieu thong tin, tu dong tra cuu tu dien 122k tu offline!
    if not pinyin or not meaning or not han_viet:
        dict_rows = query_dict_db(hanzi, limit=1)
        if dict_rows:
            d_trad, d_py, d_hv, d_mean = dict_rows[0]
            if not pinyin:
                pinyin = d_py
            if not han_viet:
                han_viet = d_hv
            if not meaning:
                meaning = d_mean

    for v in vocab:
        if v.get("hanzi") == hanzi:
            if pinyin:
                v["pinyin"] = pinyin
            if han_viet:
                v["han_viet"] = han_viet
            if meaning:
                v["meaning"] = meaning
            if context:
                v["context"] = context
            if style:
                v["style"] = style
            save_vocab(vocab)
            return v, False

    new_item = {
        "hanzi": hanzi,
        "pinyin": pinyin,
        "han_viet": han_viet,
        "meaning": meaning,
        "style": style,
        "context": context,
        "status": "new",
        "created_at": datetime.now().isoformat()
    }
    vocab.append(new_item)
    save_vocab(vocab)
    return new_item, True


def cmd_add_vocab(args):
    item, is_new = add_or_update_vocab(args.hanzi, args.pinyin, getattr(args, "han_viet", ""), args.meaning, args.style, args.context)
    if is_new:
        draw_box("LƯU TỪ MỚI THÀNH CÔNG", [
            f"Từ vựng   : {BOLD}{GREEN}{args.hanzi}{RESET}",
            f"Bính âm   : {CYAN}{item['pinyin']}{RESET}",
            f"Hán Việt  : {YELLOW}{item.get('han_viet') or 'Chưa có'}{RESET}",
            f"Ý nghĩa   : {item['meaning']}",
            f"Phong cách: {item['style']}",
            f"Ngữ cảnh  : {item['context'] or 'Chưa có'}",
            "---",
            f"{YELLOW}Từ này sẽ được tự động gài vào các phiên 10 câu tiếp theo!{RESET}"
        ], color=GREEN)
    else:
        draw_box("CẬP NHẬT TỪ VỰNG THÀNH CÔNG", [
            f"Đã cập nhật: {BOLD}{args.hanzi}{RESET} [{item.get('pinyin')}]",
            f"Hán Việt   : {YELLOW}{item.get('han_viet') or 'Chưa có'}{RESET}",
            f"Ý nghĩa    : {item.get('meaning')}"
        ], color=GREEN)


def cmd_list_vocab(args=None, status_filter=None):
    vocab = load_vocab()
    if not vocab:
        print("Chưa có từ vựng nào trong kho data/vocab.json.")
        return
    st_filter = (args.status.lower() if args and args.status else status_filter)
    lines = []
    for idx, v in enumerate(vocab, 1):
        st = v.get("status", "new")
        if st_filter and st != st_filter.lower():
            continue
        st_badge = f"{YELLOW}[MỚI]{RESET}" if st == "new" else (f"{CYAN}[ĐANG ÔN]{RESET}" if st == "learning" else f"{GREEN}[THUẦN THỤC]{RESET}")
        hv_str = f" [HV: {YELLOW}{v.get('han_viet', '')}{RESET}]" if v.get('han_viet') else ""
        lines.append(f"{idx}. {BOLD}{v['hanzi']}{RESET} [{v.get('pinyin', '')}]{hv_str} {st_badge}")
        lines.append(f"   Ý nghĩa : {v.get('meaning', '')} ({v.get('style', '')})")
        if v.get("context"):
            lines.append(f"   Ví dụ   : {DIM}{v.get('context')}{RESET}")
        lines.append("")
    draw_box("KHO TỪ VỰNG THỰC CHIẾN (data/vocab.json)", lines[:-1] if lines else ["Không có từ nào phù hợp."], color=CYAN)


def cmd_export_anki(args=None):
    """Xuat toan bo kho tu vung data/vocab.json sang dinh dang chuan Anki (TSV UTF-8)."""
    out_file = BASE_DIR / "data" / "anki_deck.tsv"
    if args and getattr(args, "output", None):
        out_file = Path(args.output)

    vocab = load_vocab()
    if not vocab:
        print("Kho từ vựng data/vocab.json đang trống.")
        return

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("#separator:Tab\n")
        f.write("#html:true\n")
        f.write("#tags column:5\n")
        f.write("#columns:Front\tBack\tPinyin\tHanViet\tTags\n")

        for v in vocab:
            hz = v.get("hanzi", "").strip()
            py = v.get("pinyin", "").strip()
            hv = v.get("han_viet", "").strip()
            mn = v.get("meaning", "").strip()
            ctx = v.get("context", "").strip()
            st = v.get("style", "Đời sống").strip()
            tag = f"chinese_a2 {v.get('status', 'new')}"

            front = f"<div style='font-family:Arial,sans-serif;font-size:32px;font-weight:bold;color:#00e5ff;text-align:center;'>{hz}</div>"
            back_parts = [
                f"<div style='font-family:Arial,sans-serif;font-size:16px;line-height:1.6;'>",
                f"<b>Bính âm:</b> <span style='color:#00ffff;'>{py}</span><br>",
            ]
            if hv:
                back_parts.append(f"<b>Hán Việt:</b> <span style='color:#ffcc00;font-weight:bold;'>{hv}</span><br>")
            back_parts.append(f"<b>Ý nghĩa:</b> {mn}<br>")
            back_parts.append(f"<b>Phong cách:</b> {st}")
            if ctx:
                back_parts.append(f"<hr style='border:0.5px solid #555;'><div style='font-style:italic;color:#dddddd;'>{ctx}</div>")
            back_parts.append("</div>")
            back = "".join(back_parts).replace("\t", " ").replace("\n", " ")

            f.write(f"{front}\t{back}\t{py}\t{hv}\t{tag}\n")

    lines = [
        f"{GREEN}✓ ĐÃ XUẤT THÀNH CÔNG {len(vocab)} TỪ RA FILE ANKI!{RESET}",
        f"Đường dẫn: {CYAN}{out_file}{RESET}",
        "---",
        f"{BOLD}Cách import vào Anki (Desktop hoặc Mobile):{RESET}",
        "1. Mở Anki -> Chọn 'File' -> 'Import'",
        "2. Chọn file 'data/anki_deck.tsv'",
        "3. Anki sẽ tự động nhận diện thẻ (Front/Back, Bính âm, Hán Việt, Ví dụ)!"
    ]
    draw_box("XUẤT FILE ANKI HOÀN TẤT", lines, color=GREEN)


def cmd_status(args=None):
    progress = load_progress()
    stats = progress.get("chunk_stats", {})
    weak = [k for k, v in stats.items() if v.get("fail", 0) > v.get("pass", 0)]
    strong = [k for k, v in stats.items() if v.get("pass", 0) > v.get("fail", 0)]
    vocab = load_vocab()
    new_v = [v['hanzi'] for v in vocab if v.get('status') == 'new']

    lines = [
        f"Mục tiêu : {progress.get('target_level', 'A2_COLLOQUIAL')}",
        f"Số lần tập: {len(progress.get('history', []))}",
        f"{YELLOW}Từ mới vừa nạp:{RESET} {', '.join(new_v) if new_v else 'Không có'}",
        f"{RED}Cần ôn lại (Yếu):{RESET} {', '.join(weak) if weak else 'Không có'}",
        f"{GREEN}Đã nhuần nhuyễn :{RESET} {', '.join(strong) if strong else 'Không có'}"
    ]
    draw_box("TRẠNG THÁI TIẾN ĐỘ HỌC", lines, color=CYAN)


def cmd_show_drill(args):
    lines = [
        f"{DIM}[Bối cảnh]:{RESET} {BOLD}{args.context}{RESET}",
        f"{DIM}[Đối phương]:{RESET} {BOLD}{args.hanzi}{RESET}",
    ]
    if args.pinyin:
        lines.append(f"              {CYAN}{args.pinyin}{RESET}")
    if args.meaning:
        lines.append(f"              {DIM}(Ý nghĩa: {args.meaning}){RESET}")
    lines.append("---")
    lines.append(f"{YELLOW}▶ PHẢN XẠ CỦA BẠN (Gõ Pinyin hoặc chữ Phồn thể):{RESET}")
    speaker_title = f"LƯỢT PHẢN XẠ THỰC CHIẾN ({args.speaker or 'Đài Loan'})"
    draw_box(speaker_title, lines, color=CYAN)


def cmd_show_result(args):
    is_pass = (args.verdict.lower() in ["pass", "true", "1", "dung", "correct"])
    status_text = f"{GREEN}✓ CHUẨN XÁC!{RESET}" if is_pass else f"{RED}✗ CHƯA CHUẨN!{RESET}"
    lines = [
        f"Đánh giá  : {status_text}",
        f"Bạn nói   : {BOLD}{args.user or '(trống)'}{RESET}",
        f"Người bản xứ : {BOLD}{GREEN if is_pass else YELLOW}{args.correct}{RESET}",
    ]
    if args.pinyin:
        lines.append(f"Bính âm   : {CYAN}{args.pinyin}{RESET}")
    if args.tips:
        lines.append(f"{DIM}Nhận xét  : {args.tips}{RESET}")
    draw_box("KẾT QUẢ ĐÁNH GIÁ PHẢN XẠ", lines, color=GREEN if is_pass else RED)


def cmd_show_explain(args):
    lines = [
        f"{BOLD}Chủ đề: {args.title}{RESET}",
        "---"
    ]
    for row in args.content.split("\\n"):
        lines.append(row.strip())
    lines.append("---")
    lines.append(f"{YELLOW}* Sẵn sàng phản xạ tiếp thì tiếp tục drill!{RESET}")
    draw_box("GIẢI THÍCH CHI TIẾT (TÁCH BIỆT KHỎI DRILL)", lines, color=YELLOW)


def cmd_record(args):
    progress = load_progress()
    is_pass = (args.result.lower() in ["pass", "true", "1", "correct", "dung"])
    stats = progress.setdefault("chunk_stats", {})
    entry = stats.setdefault(args.item, {"pass": 0, "fail": 0, "last_tested": None})
    if is_pass:
        entry["pass"] += 1
    else:
        entry["fail"] += 1
    entry["last_tested"] = datetime.now().isoformat()
    progress.setdefault("history", []).append({
        "time": datetime.now().isoformat(),
        "item": args.item,
        "result": "pass" if is_pass else "fail"
    })
    save_progress(progress)
    print(f"[ĐÃ LƯU]: {args.item} -> {'PASS' if is_pass else 'FAIL'}")


def cmd_session_prepare(args=None, count=10, quiet=False):
    out_file = BASE_DIR / "data" / "session_input.json"
    if args and getattr(args, "output", None):
        out_file = Path(args.output)
    if args and getattr(args, "count", None):
        count = args.count

    curriculum = {}
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            curriculum = json.load(f)

    progress = load_progress()
    stats = progress.get("chunk_stats", {})
    weak_items = set(k for k, v in stats.items() if v.get("fail", 0) >= v.get("pass", 0))

    vocab = load_vocab()
    # Kiem tra xem co tu vung nao con trong nghia hoac Han Viet khong
    empty_info = [v.get("hanzi") for v in vocab if not v.get("meaning") or not v.get("han_viet")]
    if empty_info and not quiet:
        print(f"{YELLOW}[Nhắc nhở]: Phát hiện {len(empty_info)} từ còn thiếu nghĩa/Hán Việt ({', '.join(empty_info)}). Agy sẽ tự động bù vào!{RESET}")

    vocab_candidates = []
    for v in vocab:
        if v.get("status") == "new":
            hv_hint = f" [HV: {v.get('han_viet')}]" if v.get('han_viet') else ""
            vocab_candidates.append({
                "context": f"Tình huống thực tế ({v.get('style', 'Khẩu ngữ')}): {v.get('context', 'Giao tiếp hàng ngày')}",
                "speaker": "Người bản xứ",
                "hanzi": f"Bạn muốn diễn đạt ý: '{v.get('meaning', '')}' bằng từ mới vừa nạp:",
                "pinyin": "",
                "meaning": v.get("context", ""),
                "target": v.get("hanzi", ""),
                "hint": f"{v.get('pinyin', '')}{hv_hint} - {v.get('meaning', '')}"
            })

    candidates = []
    for lvl in curriculum.get("levels", []):
        for unit in lvl.get("units", []):
            u_title = unit.get("title", "")
            for ch in unit.get("challenges", []):
                candidates.append({
                    "context": ch.get("situation", u_title),
                    "speaker": "Người bản xứ",
                    "hanzi": ch.get("situation", ""),
                    "pinyin": "",
                    "meaning": "",
                    "target": ch.get("correct", ""),
                    "hint": f"Gợi ý: {ch.get('pinyin', '')}"
                })
            for c in unit.get("chunks", []):
                candidates.append({
                    "context": f"Tình huống đời sống ({unit.get('context', u_title)})",
                    "speaker": "Đồng nghiệp / Bạn bè",
                    "hanzi": f"Bạn muốn nói: '{c.get('meaning', '')}' tự nhiên:",
                    "pinyin": "",
                    "meaning": c.get("vs_textbook", ""),
                    "target": c.get("chunk", ""),
                    "hint": f"{c.get('pinyin', '')} - {c.get('tips', '')}"
                })

    weak_candidates = [c for c in candidates if c["target"] in weak_items]
    other_candidates = [c for c in candidates if c["target"] not in weak_items]

    random.shuffle(vocab_candidates)
    random.shuffle(weak_candidates)
    random.shuffle(other_candidates)

    selected = vocab_candidates[:3] + weak_candidates[:4]
    remaining = count - len(selected)
    if remaining > 0:
        selected += other_candidates[:remaining]

    selected = selected[:count]
    random.shuffle(selected)
    for i, q in enumerate(selected, 1):
        q["id"] = i
        q["act"] = i
        if not q.get("act_title"):
            q["act_title"] = f"HỒI {i}/{len(selected)}"
        if not q.get("plot_progression"):
            q["plot_progression"] = q.get("context", "")

    session_data = {
        "session_id": datetime.now().strftime("session_%Y%m%d_%H%M%S"),
        "title": f"Phiên {len(selected)} câu phản xạ thực chiến",
        "story_arc": "Diễn biến thực tế đời sống 10 hồi kịch tính kết hợp từ mới & bài cũ",
        "created_at": datetime.now().isoformat(),
        "total_questions": len(selected),
        "questions": selected
    }

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

    if not quiet:
        lines = [
            f"Đã chuẩn bị xong {len(selected)} câu hỏi (gồm từ mới & bài cũ)!",
            f"File: {CYAN}{out_file}{RESET}",
            "---",
            f"Chạy luyện tập ngay bằng lệnh: {YELLOW}/run{RESET}"
        ]
        draw_box("CHUẨN BỊ PHIÊN THÀNH CÔNG", lines, color=GREEN)


def cmd_session_run(args=None):
    in_file = BASE_DIR / "data" / "session_input.json"
    out_file = BASE_DIR / "data" / "session_output.json"
    if args and getattr(args, "input_file", None):
        in_file = Path(args.input_file)
    if args and getattr(args, "output_file", None):
        out_file = Path(args.output_file)

    if not in_file.exists():
        cmd_session_prepare(count=10, quiet=True)

    try:
        with open(in_file, "r", encoding="utf-8") as f:
            session_data = json.load(f)
    except Exception as e:
        print(f"{RED}Lỗi đọc file {in_file}: {e}{RESET}")
        return

    questions = session_data.get("questions", [])
    if not questions:
        print(f"{RED}Không có câu hỏi nào trong {in_file}!{RESET}")
        return

    title = session_data.get("title", "PHIÊN PHẢN XẠ 10 CÂU")
    story_arc = session_data.get("story_arc", "")
    session_id = session_data.get("session_id", datetime.now().strftime("session_%Y%m%d_%H%M%S"))
    total_q = len(questions)

    queue_file = BASE_DIR / "data" / "session_queue.json"
    queue_count = 0
    if queue_file.exists():
        try:
            with open(queue_file, "r", encoding="utf-8") as qf:
                qd = json.load(qf)
                if isinstance(qd, list):
                    queue_count = len(qd)
        except Exception:
            pass

    intro_lines = [
        f"{BOLD}Chủ đề:{RESET} {title}",
    ]
    if queue_count > 0:
        intro_lines.append(f"{YELLOW}Hàng đợi bài sẵn:{RESET} Còn {BOLD}{queue_count}{RESET} bài tiếp theo sau bài này.")
    if story_arc:
        intro_lines.append(f"{YELLOW}Cốt truyện:{RESET} {BOLD}{story_arc}{RESET}")
    intro_lines.extend([
        f"{DIM}Quy mô:{RESET} {total_q} hồi/cảnh | {DIM}Quy tắc:{RESET} Phản xạ liền mạch theo diễn biến kịch bản.",
        "---",
        f"{YELLOW}Nhấn [Enter] để vào vai... (gõ ':q' để dừng giữa chừng){RESET}"
    ])
    banner_title = "CỐT TRUYỆN THỰC CHIẾN (STORY-DRIVEN SESSION)" if story_arc else "BẮT ĐẦU PHIÊN PHẢN XẠ THỰC CHIẾN"
    draw_box(banner_title, intro_lines, color=CYAN)
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        print("\nĐã hủy.")
        return

    responses = []
    t_session_start = time.perf_counter()
    session_start_time = datetime.now()

    for idx, q in enumerate(questions, 1):
        q_id = q.get("id", idx)
        act = q.get("act", idx)
        act_title = q.get("act_title") or q.get("scene_title") or f"HỒI {idx}/{total_q}"
        plot = q.get("plot_progression") or q.get("plot") or ""
        context = q.get("context", "")
        speaker = q.get("speaker", "Người bản xứ")
        hanzi = q.get("hanzi", "")
        pinyin = q.get("pinyin", "")
        meaning = q.get("meaning", "")
        hint = q.get("hint", "")
        target = q.get("target", "")

        lines = []
        if plot:
            lines.append(f"{YELLOW}▶ [Diễn biến]:{RESET} {BOLD}{plot}{RESET}")
        if context:
            lines.append(f"{DIM}[Bối cảnh]:{RESET} {context}")
        lines.append(f"{CYAN}[{speaker}]:{RESET} {BOLD}{hanzi}{RESET}")
        if pinyin:
            lines.append(f"              {CYAN}{pinyin}{RESET}")
        if meaning:
            lines.append(f"              {DIM}(Ý nghĩa: {meaning}){RESET}")
        if hint:
            lines.append(f"{DIM}[Gợi ý]:{RESET} {YELLOW}{hint}{RESET}")
        lines.append("---")
        lines.append(f"{YELLOW}▶ PHẢN XẠ CỦA BẠN (Gõ Pinyin hoặc Phồn thể rồi Enter):{RESET}")

        box_title = f"{act_title} ({speaker})" if ("HỒI" in act_title or "SCENE" in act_title.upper()) else f"[{idx}/{total_q}] {act_title} ({speaker})"
        draw_box(box_title, lines, color=CYAN)

        t_q_start = time.perf_counter()
        try:
            user_ans = input(f"{BOLD}Phản xạ [{idx}/{total_q}]: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nĐã ngắt phiên.")
            user_ans = ":q"

        t_spent = round(time.perf_counter() - t_q_start, 1)

        if user_ans.lower() == ":q":
            print(f"{YELLOW}Đã thoát sớm tại hồi {idx}.{RESET}")
            break

        responses.append({
            "id": q_id,
            "act": act,
            "act_title": act_title,
            "plot_progression": plot,
            "context": context,
            "speaker": speaker,
            "hanzi": hanzi,
            "target": target,
            "user_answer": user_ans,
            "time_spent_seconds": t_spent
        })
        print()

    total_duration = round(time.perf_counter() - t_session_start, 1)
    session_end_time = datetime.now()

    out_data = {
        "session_id": session_id,
        "title": title,
        "story_arc": story_arc,
        "started_at": session_start_time.isoformat(),
        "completed_at": session_end_time.isoformat(),
        "total_questions": len(responses),
        "duration_seconds": total_duration,
        "responses": responses
    }

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)

    # Luu lich su khong lo bi ghi de
    hist_dir = BASE_DIR / "data" / "history"
    hist_dir.mkdir(parents=True, exist_ok=True)
    with open(hist_dir / f"{session_id}_output.json", "w", encoding="utf-8") as hf:
        json.dump(out_data, hf, ensure_ascii=False, indent=2)

    # Tu dong nap bai tiep theo neu co hang doi
    queue_msg = ""
    if queue_file.exists():
        try:
            with open(queue_file, "r", encoding="utf-8") as qf:
                qd = json.load(qf)
            if isinstance(qd, list) and len(qd) > 0:
                next_session = qd.pop(0)
                with open(in_file, "w", encoding="utf-8") as inf:
                    json.dump(next_session, inf, ensure_ascii=False, indent=2)
                with open(queue_file, "w", encoding="utf-8") as qf:
                    json.dump(qd, qf, ensure_ascii=False, indent=2)
                queue_msg = f"Đã tự động nạp bài tiếp theo: {BOLD}{next_session.get('title')}{RESET} (Còn {len(qd)} bài sẵn)"
        except Exception:
            pass

    avg_spd = round(total_duration / len(responses), 1) if responses else 0
    done_lines = [
        f"{GREEN}✓ HOÀN THÀNH {len(responses)}/{total_q} CÂU HỎI!{RESET}",
        f"Tổng thời gian: {BOLD}{total_duration}s{RESET} (Trung bình: {avg_spd}s/câu)",
        f"File kết quả  : {CYAN}{out_file}{RESET}",
    ]
    if queue_msg:
        done_lines.extend([
            "---",
            f"{YELLOW}▶ [Hàng đợi]{RESET}: {queue_msg}",
            f"Bạn có thể gõ {YELLOW}/run{RESET} để làm bài tiếp ngay hoặc gõ {YELLOW},{RESET} để chấm bài vừa xong."
        ])
    done_lines.extend([
        "---",
        f"{BOLD}Bước tiếp theo:{RESET} Báo agy CLI {YELLOW}', (dấu phẩy)'{RESET} hoặc {YELLOW}'Chấm điểm phiên vừa làm'{RESET}",
        "để nhận phân tích chi tiết và cập nhật tiến độ."
    ])
    draw_box("KẾT THÚC PHIÊN LUYỆN TẬP", done_lines, color=GREEN)


def quick_drill_one():
    """Luyen nhanh 1 cau ngau nhien truc tiep trong CLI chat."""
    curriculum = {}
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            curriculum = json.load(f)
    
    candidates = []
    for lvl in curriculum.get("levels", []):
        for unit in lvl.get("units", []):
            for ch in unit.get("challenges", []):
                candidates.append((ch.get("situation", ""), ch.get("correct", ""), ch.get("pinyin", "")))
            for c in unit.get("chunks", []):
                candidates.append((f"Muốn nói: '{c.get('meaning')}' tự nhiên", c.get("chunk"), c.get("pinyin", "")))
    
    if not candidates:
        print(f"{YELLOW}Chưa có ngân hàng câu hỏi.{RESET}")
        return

    sit, correct, pinyin = random.choice(candidates)
    draw_box("DRILL NHANH 1 CÂU", [
        f"{DIM}[Tình huống]:{RESET} {BOLD}{sit}{RESET}",
        "---",
        f"{YELLOW}▶ Gõ câu phản xạ của bạn (Pinyin hoặc Phồn thể):{RESET}"
    ], color=CYAN)

    try:
        ans = input(f"{BOLD}Phản xạ: {RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if not ans:
        return

    print()
    norm_ans = ans.lower().replace(" ", "").replace("，", "").replace("。", "")
    norm_target = correct.lower().replace(" ", "").replace("，", "").replace("。", "")
    norm_pinyin = pinyin.lower().replace(" ", "").replace("，", "").replace("。", "")

    is_match = (norm_ans in norm_target) or (norm_target in norm_ans) or (norm_ans in norm_pinyin)
    verdict_text = f"{GREEN}✓ CHUẨN XÁC!{RESET}" if is_match else f"{YELLOW}○ GỢI Ý BẢN XỨ{RESET}"
    draw_box("KẾT QUẢ PHẢN XẠ", [
        f"Trạng thái : {verdict_text}",
        f"Bạn gõ     : {BOLD}{ans}{RESET}",
        f"Câu chuẩn  : {BOLD}{GREEN}{correct}{RESET} [{CYAN}{pinyin}{RESET}]"
    ], color=GREEN if is_match else YELLOW)


def show_process_profile():
    if PROCESS_FILE.exists():
        try:
            with open(PROCESS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                draw_box("HỒ SƠ TIẾN TRÌNH NGƯỜI HỌC (process.md)", [content], color=CYAN)
                return
        except Exception:
            pass
    print("Chưa có hồ sơ process.md.")


def lookup_word(query):
    vocab = load_vocab()
    q = query.strip().lower()
    matches = [v for v in vocab if q in v.get('hanzi', '').lower() or q in v.get('pinyin', '').lower() or q in v.get('meaning', '').lower() or q in v.get('han_viet', '').lower()]
    dict_matches = query_dict_db(query, limit=4)

    if matches or dict_matches:
        lines = []
        if matches:
            lines.append(f"{BOLD}[Từ trong kho cá nhân của bạn]:{RESET}")
            for m in matches:
                hv_str = f" | HV: {YELLOW}{m.get('han_viet')}{RESET}" if m.get('han_viet') else ""
                lines.append(f"• {BOLD}{m['hanzi']}{RESET} [{CYAN}{m.get('pinyin')}{RESET}]{hv_str} : {m.get('meaning')}")
                if m.get('context'):
                    lines.append(f"  Ví dụ: {DIM}{m.get('context')}{RESET}")
        if dict_matches:
            if matches:
                lines.append("---")
            lines.append(f"{BOLD}[Từ điển gốc CVDICT (122k từ offline)]:{RESET}")
            for trad, py, hv, mean in dict_matches:
                hv_str = f" | HV: {YELLOW}{hv}{RESET}" if hv else ""
                lines.append(f"• {BOLD}{trad}{RESET} [{CYAN}{py}{RESET}]{hv_str} : {mean}")
        draw_box(f"KẾT QUẢ TRA CỨU: '{query}'", lines, color=GREEN)
        return True
    return False


COMMAND_MAP = {
    "/run": "Bắt đầu làm phiên 10 câu phản xạ thực chiến",
    "/prep": "Soạn đề 10 câu mới từ kho từ mới & bài cũ",
    "/drill": "Thử sức phản xạ nhanh 1 câu ngẫu nhiên",
    "/vocab": "Xem kho từ vựng thực chiến (/vocab new/learning)",
    "/add": "Thêm từ mới (/add <từ> <pinyin> <nghĩa>)",
    "/anki": "Xuất kho từ vựng ra file Anki (.tsv)",
    "/status": "Xem thống kê tiến độ, từ yếu, từ đã thuộc",
    "/process": "Xem hồ sơ phong cách hiện tại (process.md)",
    "/clear": "Xóa màn hình",
    "/help": "Xem hướng dẫn chi tiết",
    "/exit": "Thoát chương trình"
}

SHORTCUT_MAP = {
    "1": "/run",
    "2": "/prep",
    "3": "/drill",
    "4": "/vocab",
    "5": "/status",
    "6": "/process",
    "7": "/help",
    "8": "/anki",
    "0": "/exit"
}


def show_suggestions(filter_text=""):
    lines = [
        f"{DIM}Bạn có thể gõ tên lệnh HOẶC bấm trực tiếp số thứ tự [1..8]:{RESET}",
        "---"
    ]
    matches = []
    f_clean = filter_text.strip().lower()

    num_keys = {"/run": "1", "/prep": "2", "/drill": "3", "/vocab": "4", "/status": "5", "/process": "6", "/help": "7", "/anki": "8", "/exit": "0"}

    for cmd, desc in COMMAND_MAP.items():
        if not f_clean or f_clean == "/" or f_clean in cmd or f_clean in desc.lower():
            matches.append((cmd, desc))

    if not matches:
        lines.append(f"{RED}Không tìm thấy lệnh nào khớp với '{filter_text}'{RESET}")
        lines.append(f"Gõ {YELLOW}/{RESET} để xem toàn bộ danh sách lệnh.")
    else:
        for cmd, desc in matches:
            num_badge = f"{GREEN}[{num_keys[cmd]}]{RESET} " if cmd in num_keys else "    "
            lines.append(f"{num_badge}{BOLD}{YELLOW}{cmd:<9}{RESET} : {desc}")

    lines.append("---")
    lines.append(f"{DIM}* Tra từ: Gõ trực tiếp chữ Hán, Pinyin, Hán Việt hoặc tiếng Việt.{RESET}")
    lines.append(f"{DIM}* Mẹo chuột: Tô đen text để tự copy, click chuột phải để dán nhanh!{RESET}")
    title = f"GỢI Ý LỆNH KHẢ DỤNG{f': {filter_text}' if filter_text and filter_text != '/' else ''}"
    draw_box(title, lines, color=CYAN)


def print_help():
    show_suggestions()


def interactive_prompt(prompt_str="- "):
    """
    Nhập liệu tương tác từng ký tự trên Windows bằng msvcrt.
    Khi gõ '/', menu gợi ý xuất hiện chuẩn phong cách CLI hiện đại:
    - 5 dòng lệnh hiển thị trong khung trượt mượt mà (không giật màn hình)
    - Phím Mũi tên Lên/Xuống (↑/↓) để di chuyển vệt sáng chọn lệnh
    - Phím Enter để chọn hoặc thực thi lệnh ngay lập tức
    - Phím Tab để hoàn thiện câu lệnh (autocomplete)
    - Tô đen để tự copy, click chuột phải để dán nhanh (QuickEdit)
    """
    try:
        import msvcrt
    except ImportError:
        return input(prompt_str).strip()

    if not sys.stdin.isatty():
        return input(prompt_str).strip()

    COMMAND_LIST = [
        ("/run", "Bắt đầu làm phiên 10 câu phản xạ thực chiến"),
        ("/prep", "Soạn đề 10 câu mới từ kho từ mới & bài cũ"),
        ("/sync", "Đồng bộ 2 chiều bài học với Git/điện thoại"),
        ("/drill", "Thử sức phản xạ nhanh 1 câu ngẫu nhiên"),
        ("/vocab", "Xem kho từ vựng thực chiến (/vocab new/learning)"),
        ("/add", "Thêm từ mới vào kho (/add <từ>)"),
        ("/anki", "Xuất kho từ vựng ra file Anki (.tsv)"),
        ("/status", "Xem thống kê tiến độ, từ yếu, từ đã thuộc"),
        ("/process", "Xem hồ sơ phong cách người học (process.md)"),
        ("/dict", "Tra cứu từ điển 122k từ offline (/dict <từ>)"),
        ("/clear", "Xóa màn hình terminal"),
        ("/help", "Xem hướng dẫn chi tiết các lệnh"),
        ("/exit", "Thoát chương trình"),
    ]

    buffer = ""
    selected_idx = 0
    scroll_offset = 0
    rendered_menu_lines = 0

    def clear_menu():
        nonlocal rendered_menu_lines
        if rendered_menu_lines > 0:
            for _ in range(rendered_menu_lines):
                sys.stdout.write("\033[1B\r\033[K")
            sys.stdout.write(f"\033[{rendered_menu_lines}A\r")
            rendered_menu_lines = 0
            sys.stdout.flush()

    def render():
        nonlocal rendered_menu_lines, selected_idx, scroll_offset

        # Vẽ lại dòng prompt chính
        sys.stdout.write(f"\r\033[K{prompt_str}{buffer}")

        # Chỉ hiện dropdown khi buffer bắt đầu bằng '/' và chưa chứa khoảng trắng
        show_menu = buffer.startswith("/") and (" " not in buffer)
        if not show_menu:
            clear_menu()
            sys.stdout.flush()
            return

        query = buffer.lower()
        matches = [item for item in COMMAND_LIST if item[0].startswith(query)]
        if not matches:
            matches = [item for item in COMMAND_LIST if query[1:] in item[0] or query[1:] in item[1].lower()]

        if not matches:
            clear_menu()
            sys.stdout.flush()
            return

        selected_idx = max(0, min(selected_idx, len(matches) - 1))
        VISIBLE_COUNT = 5

        # Cập nhật sliding window cuộn mượt 5 dòng
        if selected_idx < scroll_offset:
            scroll_offset = selected_idx
        elif selected_idx >= scroll_offset + VISIBLE_COUNT:
            scroll_offset = selected_idx - VISIBLE_COUNT + 1
        scroll_offset = max(0, min(scroll_offset, max(0, len(matches) - VISIBLE_COUNT)))

        visible = matches[scroll_offset : scroll_offset + VISIBLE_COUNT]
        items_above = scroll_offset
        items_below = max(0, len(matches) - (scroll_offset + len(visible)))

        w = get_terminal_width()
        divider_len = max(40, w - 1)
        max_desc = max(20, w - 38)

        lines_to_draw = []
        # Đường kẻ phân cách tinh tế
        lines_to_draw.append(f"{DIM}{'─' * divider_len}{RESET}")

        # Danh sách 5 dòng lệnh
        for i, (cmd, desc) in enumerate(visible):
            actual_idx = scroll_offset + i
            desc_str = desc if len(desc) <= max_desc else desc[:max_desc - 3] + "..."
            if actual_idx == selected_idx:
                lines_to_draw.append(f"{CYAN}- {cmd:<34}{RESET} {BOLD}{desc_str}{RESET}")
            else:
                lines_to_draw.append(f"  {cmd:<34} {DIM}{desc_str}{RESET}")

        # Dòng thông báo số lượng còn lại
        if items_above > 0 and items_below > 0:
            lines_to_draw.append(f"  {DIM}↑ {items_above} more · ↓ {items_below} more{RESET}")
        elif items_below > 0:
            lines_to_draw.append(f"  {DIM}↓ {items_below} more{RESET}")
        elif items_above > 0:
            lines_to_draw.append(f"  {DIM}↑ {items_above} more{RESET}")

        # Khoảng trống và dòng footer điều hướng
        lines_to_draw.append("")
        lines_to_draw.append(f"{CYAN}↑/↓{RESET} {DIM}Navigate ·{RESET} {CYAN}enter{RESET} {DIM}Select ·{RESET} {CYAN}tab{RESET} {DIM}Complete{RESET}")

        # Nếu là lần đầu tiên mở menu, cấp phát khoảng trống bên dưới để chống giật
        if rendered_menu_lines == 0:
            sys.stdout.write("\n" * len(lines_to_draw) + f"\033[{len(lines_to_draw)}A\r")

        # Vẽ từng dòng xuống dưới bằng ANSI cursor down
        for line in lines_to_draw:
            sys.stdout.write(f"\033[1B\r\033[K{line}")

        # Xóa các dòng thừa nếu menu bị co ngắn lại
        if rendered_menu_lines > len(lines_to_draw):
            for _ in range(rendered_menu_lines - len(lines_to_draw)):
                sys.stdout.write("\033[1B\r\033[K")

        total_drawn = max(rendered_menu_lines, len(lines_to_draw))
        rendered_menu_lines = len(lines_to_draw)

        # Trả con trỏ trở về dòng prompt chính
        sys.stdout.write(f"\033[{total_drawn}A\r{prompt_str}{buffer}")
        sys.stdout.flush()

    render()

    while True:
        try:
            ch = msvcrt.getwch()
        except Exception:
            return buffer.strip()

        # Phím đặc biệt (Mũi tên, Delete, etc.)
        if ch in ('\x00', '\xe0'):
            try:
                special = msvcrt.getwch()
            except Exception:
                special = ''
            
            show_menu = buffer.startswith("/") and (" " not in buffer)
            if show_menu:
                query = buffer.lower()
                matches = [item for item in COMMAND_LIST if item[0].startswith(query)]
                if not matches:
                    matches = [item for item in COMMAND_LIST if query[1:] in item[0] or query[1:] in item[1].lower()]

                if matches:
                    if special == 'H':  # Mũi tên Lên (Up)
                        selected_idx = (selected_idx - 1) % len(matches)
                        render()
                    elif special == 'P':  # Mũi tên Xuống (Down)
                        selected_idx = (selected_idx + 1) % len(matches)
                        render()
            continue

        # Phím Enter
        if ch in ('\r', '\n'):
            show_menu = buffer.startswith("/") and (" " not in buffer)
            if show_menu:
                query = buffer.lower()
                matches = [item for item in COMMAND_LIST if item[0].startswith(query)]
                if not matches:
                    matches = [item for item in COMMAND_LIST if query[1:] in item[0] or query[1:] in item[1].lower()]
                if matches:
                    buffer = matches[selected_idx][0]

            clear_menu()
            sys.stdout.write(f"\r\033[K{prompt_str}{buffer}\n")
            sys.stdout.flush()
            return buffer.strip()

        # Phím Tab (Autocomplete)
        if ch == '\t':
            show_menu = buffer.startswith("/") and (" " not in buffer)
            if show_menu:
                query = buffer.lower()
                matches = [item for item in COMMAND_LIST if item[0].startswith(query)]
                if not matches:
                    matches = [item for item in COMMAND_LIST if query[1:] in item[0] or query[1:] in item[1].lower()]
                if matches:
                    buffer = matches[selected_idx][0] + " "
                    selected_idx = 0
                    scroll_offset = 0
                    render()
            continue

        # Phím Backspace
        if ch == '\x08':
            if len(buffer) > 0:
                buffer = buffer[:-1]
                selected_idx = 0
                scroll_offset = 0
                render()
            continue

        # Phím Ctrl+C hoặc ESC
        if ch == '\x03':  # Ctrl+C
            clear_menu()
            sys.stdout.write("\n")
            sys.stdout.flush()
            return "/exit"
        if ch == '\x1b':  # ESC
            if buffer.startswith("/"):
                buffer = ""
                selected_idx = 0
                scroll_offset = 0
                render()
            continue

        # Ký tự thông thường (hỗ trợ nhập nhanh hoặc dán văn bản mượt mà)
        buffer += ch
        while msvcrt.kbhit():
            try:
                next_ch = msvcrt.getwch()
                if next_ch in ('\r', '\n'):
                    clear_menu()
                    sys.stdout.write(f"\r\033[K{prompt_str}{buffer}\n")
                    sys.stdout.flush()
                    return buffer.strip()
                elif next_ch == '\x08':
                    buffer = buffer[:-1]
                elif next_ch not in ('\x00', '\xe0'):
                    buffer += next_ch
            except Exception:
                break

        selected_idx = 0
        scroll_offset = 0
        render()


def cmd_sync():
    """Đồng bộ 2 chiều dữ liệu với Git (kéo bài làm từ điện thoại và đẩy đề mới lên)."""
    draw_box("ĐỒNG BỘ DỮ LIỆU VỚI GIT (MÁY TÍNH & ĐIỆN THOẠI)", [
        "1. Kéo kết quả mới nhất từ điện thoại về máy tính (git pull)",
        "2. Đẩy đề mới và từ vựng mới lên Git (git push)",
        "---",
        f"{YELLOW}Đang tiến hành đồng bộ...{RESET}"
    ], color=CYAN)

    print(f"\n{CYAN}▶ [1/2] Đang kéo (git pull) bài làm từ Git về máy tính...{RESET}")
    os.system("git pull --rebase")

    print(f"\n{CYAN}▶ [2/2] Đang lưu và đẩy (git push) dữ liệu mới lên Git...{RESET}")
    os.system("git add .")
    os.system('git commit -m "Auto: Đồng bộ từ máy tính (%date% %time%)"')
    os.system("git push")

    out_file = BASE_DIR / "data" / "session_output.json"
    lines = [
        f"{GREEN}✓ QUÁ TRÌNH ĐỒNG BỘ HOÀN TẤT!{RESET}",
        "---",
        f"• Nếu vừa làm bài xong từ điện thoại, bạn gõ {YELLOW}, (dấu phẩy){RESET} trong chat để Agy chấm bài ngay.",
        f"• Nếu vừa soạn bài mới, điện thoại của bạn chỉ cần chạy {CYAN}./hoc.sh{RESET} là có bài mới."
    ]
    draw_box("ĐỒNG BỘ THÀNH CÔNG", lines, color=GREEN)


def cmd_chat():
    """Giao diện Interactive CLI Chat REPL: mở 1 lần, gõ lệnh / hoặc chat trực tiếp."""
    w = get_terminal_width()
    print(f"\n{CYAN}{'═' * w}{RESET}")
    print(f"{BOLD}{GREEN}  AGY CHINESE COACH - CLI CHAT REPL (A2+ PHỒN THỂ){RESET}")
    print(f"{DIM}  Mở 1 lần - Phản xạ thực chiến, quản lý từ vựng, chạy phiên 10 câu.{RESET}")
    print(f"{CYAN}{'═' * w}{RESET}")
    print(f"Gõ {YELLOW}/{RESET} để hiện danh sách gợi ý ({CYAN}↑/↓{RESET} chọn, {GREEN}Enter{RESET} chạy, {CYAN}Tab{RESET} hoàn thiện), hoặc gõ từ để tra từ điển.\n")

    while True:
        try:
            user_input = interactive_prompt("- ")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{YELLOW}Tạm biệt! Hẹn gặp lại trong phiên học tiếp theo.{RESET}")
            break

        if not user_input:
            continue

        cmd_lower = user_input.lower()

        # Phím tắt số (1..8, 0)
        if cmd_lower in SHORTCUT_MAP:
            cmd_lower = SHORTCUT_MAP[cmd_lower]
            user_input = cmd_lower

        # Slash đơn lẻ hoặc gọi menu
        if cmd_lower in ["/", "/?", "help", "?", "menu", "gợi ý", "goi y"]:
            show_suggestions()
            print()
            continue

        # Thoát
        if cmd_lower in ["/exit", "/quit", "/q", ":q", "exit", "quit", "0"]:
            print(f"{YELLOW}Tạm biệt! Đã lưu toàn bộ tiến độ.{RESET}")
            break

        # Xóa màn hình
        elif cmd_lower in ["/clear", "/cls", "cls", "clear"]:
            os.system("cls" if os.name == "nt" else "clear")

        # Chạy phiên 10 câu
        elif cmd_lower in ["/run", "/session", "/r"]:
            cmd_session_run()

        # Soạn đề 10 câu mới
        elif cmd_lower in ["/prep", "/prepare", "/p"]:
            cmd_session_prepare(count=10)

        # Phản xạ nhanh 1 câu
        elif cmd_lower in ["/drill", "/d", "/reflex"]:
            quick_drill_one()

        # Tra từ điển 122k từ offline
        elif cmd_lower.startswith("/dict"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1 and parts[1].strip():
                lookup_word(parts[1].strip())
            else:
                print(f"{YELLOW}Cú pháp: /dict <chữ Hán | Pinyin | Hán Việt | tiếng Việt>{RESET}")

        # Xem từ vựng
        elif cmd_lower.startswith("/vocab") or cmd_lower.startswith("/v"):
            parts = user_input.split()
            st = parts[1] if len(parts) > 1 else None
            cmd_list_vocab(status_filter=st)

        # Xuất Anki
        elif cmd_lower in ["/anki", "/export-anki"]:
            cmd_export_anki()

        # Đồng bộ 2 chiều với Git (PC <-> Termux)
        elif cmd_lower in ["/sync"]:
            cmd_sync()

        # Đánh giá kết quả gần nhất
        elif cmd_lower in ["/eval", "/review"]:
            out_file = BASE_DIR / "data" / "session_output.json"
            if out_file.exists():
                print(f"{GREEN}File kết quả {out_file} đã sẵn sàng.{RESET}")
                print(f"Gõ {YELLOW}, (dấu phẩy){RESET} trong chat để Agy chấm điểm & phân tích chi tiết!")
            else:
                print(f"{YELLOW}Chưa có phiên làm bài nào. Gõ /run để làm bài trước nhé!{RESET}")

        # Thêm từ mới: /add <hanzi> [pinyin] [han_viet] [meaning]
        elif cmd_lower.startswith("/add") or cmd_lower.startswith("/a "):
            parts = user_input.split(maxsplit=4)
            if len(parts) < 2:
                print(f"{YELLOW}Cú pháp: /add <Chữ_Hán> [Bính_âm] [Hán_Việt] [Ý_nghĩa]{RESET}")
                print(f"{DIM}Ví dụ : /add 處理 chǔlǐ Xử_Lý giải quyết, xử lý{RESET}")
            else:
                hz = parts[1]
                py = parts[2] if len(parts) > 2 else ""
                hv = parts[3] if len(parts) > 3 else ""
                mn = parts[4] if len(parts) > 4 else ""
                item, is_new = add_or_update_vocab(hz, py, hv, mn)
                py_out = item.get("pinyin", "")
                hv_out = item.get("han_viet", "")
                mn_out = item.get("meaning", "")
                hv_display = f" [HV: {hv_out}]" if hv_out else ""
                print(f"{GREEN}✓ Đã lưu từ:{RESET} {BOLD}{hz}{RESET} [{py_out}]{hv_display} : {mn_out}")

        # Trạng thái tiến độ
        elif cmd_lower in ["/status", "/s"]:
            cmd_status()

        # Hồ sơ phong cách người học
        elif cmd_lower in ["/process"]:
            show_process_profile()

        # Trợ giúp
        elif cmd_lower in ["/help", "/h"]:
            show_suggestions()

        # Lệnh slash chưa nhận diện -> gợi ý fuzzy
        elif cmd_lower.startswith("/"):
            show_suggestions(cmd_lower)

        # Chat tự do hoặc tra cứu từ
        else:
            found = lookup_word(user_input)
            if not found:
                print(f"{DIM}Không tìm thấy từ '{user_input}'. Gõ {YELLOW}/{RESET} để chọn lệnh, hoặc gõ {YELLOW}1{RESET} để làm bài.{RESET}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Terminal UI & CLI Chat Engine for agy Chinese Coaching")
    subparsers = parser.add_subparsers(dest="command")

    # chat REPL
    subparsers.add_parser("chat", help="Khoi dong Interactive CLI Chat REPL")

    # add-vocab
    p_add = subparsers.add_parser("add-vocab", help="Them tu moi vao kho vocab.json")
    p_add.add_argument("--hanzi", required=True, help="Tu vung chu phon the")
    p_add.add_argument("--pinyin", default="", help="Binh am")
    p_add.add_argument("--han-viet", default="", help="Am Han Viet")
    p_add.add_argument("--meaning", default="", help="Dich nghia tieng Viet")
    p_add.add_argument("--style", default="Đời sống", help="Phong cach (vd: Khau ngu Dai, Tieu chuan, Cong so)")
    p_add.add_argument("--context", default="", help="Vi du cau thuc te")

    # export-anki
    p_anki = subparsers.add_parser("export-anki", help="Xuat kho tu vung ra file Anki (.tsv)")
    p_anki.add_argument("--output", default="", help="Duong dan file anki_deck.tsv (tuy chon)")

    # list-vocab
    p_list_v = subparsers.add_parser("list-vocab", help="Xem danh sach tu vung trong kho")
    p_list_v.add_argument("--status", choices=["new", "learning", "mastered"], help="Loc theo trang thai")

    # show-drill
    p_drill = subparsers.add_parser("show-drill", help="Hien thi the drill phan xa")
    p_drill.add_argument("--context", required=True, help="Boi canh tinh huong")
    p_drill.add_argument("--speaker", default="Người bản xứ", help="Ten doi phuong")
    p_drill.add_argument("--hanzi", required=True, help="Cau thoai bang chu phon the")
    p_drill.add_argument("--pinyin", default="", help="Binh am")
    p_drill.add_argument("--meaning", default="", help="Dich nghia")

    # show-result
    p_res = subparsers.add_parser("show-result", help="Hien thi the danh gia ket qua")
    p_res.add_argument("--verdict", required=True, choices=["pass", "fail", "true", "false"], help="pass hoac fail")
    p_res.add_argument("--user", default="", help="Cau tra loi cua hoc vien")
    p_res.add_argument("--correct", required=True, help="Cau chuan")
    p_res.add_argument("--pinyin", default="", help="Binh am cau chuan")
    p_res.add_argument("--tips", default="", help="Nhan xet thuc te")

    # show-explain
    p_exp = subparsers.add_parser("show-explain", help="Hien thi the giai thich doc lap")
    p_exp.add_argument("--title", required=True, help="Tieu de van de can giai thich")
    p_exp.add_argument("--content", required=True, help="Noi dung giai thich (dung \\n de xuong dong)")

    # record
    p_rec = subparsers.add_parser("record", help="Ghi nhan tien do")
    p_rec.add_argument("--item", required=True, help="Cum tu can ghi")
    p_rec.add_argument("--result", required=True, choices=["pass", "fail", "1", "0"], help="Ket qua")

    # status
    subparsers.add_parser("status", help="Xem trang thai tien do")

    # session-prepare
    p_prep = subparsers.add_parser("session-prepare", help="Tu dong tao file session_input.json 10 cau tu kho bai")
    p_prep.add_argument("--output", default="", help="Duong dan file session_input.json (tuy chon)")
    p_prep.add_argument("--count", type=int, default=10, help="So luong cau hoi (mac dinh 10)")

    # session-run
    p_run = subparsers.add_parser("session-run", help="Chay phien luyen tap phan xa lien tuc")
    p_run.add_argument("--input-file", default="", help="Duong dan file session_input.json (tuy chon)")
    p_run.add_argument("--output-file", default="", help="Duong dan file session_output.json (tuy chon)")

    args = parser.parse_args()

    # Neu chay khong co tham so -> mac dinh khoi dong CLI Chat REPL luon!
    if not args.command:
        cmd_chat()
        sys.exit(0)

    if args.command == "chat":
        cmd_chat()
    elif args.command == "add-vocab":
        cmd_add_vocab(args)
    elif args.command == "list-vocab":
        cmd_list_vocab(args)
    elif args.command == "show-drill":
        cmd_show_drill(args)
    elif args.command == "show-result":
        cmd_show_result(args)
    elif args.command == "show-explain":
        cmd_show_explain(args)
    elif args.command == "record":
        cmd_record(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "session-prepare":
        cmd_session_prepare(args)
    elif args.command == "session-run":
        cmd_session_run(args)
    elif args.command == "export-anki":
        cmd_export_anki(args)


if __name__ == "__main__":
    main()
