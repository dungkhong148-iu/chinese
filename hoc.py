#!/usr/bin/env python3
"""
hoc.py - Tự động học & đồng bộ 100% bằng Python thuần (chạy mượt trên cả điện thoại Termux và máy tính)
Sử dụng:
    python hoc.py              # Kéo bài mới -> Luyện 10 câu -> Tự lưu kết quả
    python hoc.py --offline    # Bỏ qua Git, vào thẳng bài luyện tập
    python hoc.py --token <ghp_xxx> # Cài đặt GitHub token 1 lần duy nhất để tự push không bao giờ hỏi username
"""

import sys
import subprocess
import argparse
from pathlib import Path

# Đảm bảo mã hóa UTF-8 cho terminal
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

BASE_DIR = Path(__file__).resolve().parent
TOKEN_FILE = BASE_DIR / "data" / ".git_token"

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[90m"


def run_git(cmd, timeout=8):
    """Chạy lệnh git an toàn, có timeout để không bao giờ bị treo terminal."""
    try:
        res = subprocess.run(
            ["git"] + cmd,
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace"
        )
        return res.returncode == 0, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def setup_token(token):
    """Cài đặt GitHub Token để tự động push không bao giờ hỏi username/password."""
    token = token.strip()
    if not token:
        print(f"{RED}[!] Token không hợp lệ.{RESET}")
        return
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token)
    
    # Cấu hình remote URL nhúng token
    repo_url = f"https://{token}@github.com/dungkhong148-iu/chinese.git"
    ok, out, err = run_git(["remote", "set-url", "origin", repo_url])
    if ok:
        print(f"{GREEN}[✓] Đã cài đặt GitHub Token thành công! Từ nay điện thoại sẽ tự động push mượt mà.{RESET}")
    else:
        print(f"{YELLOW}[!] Lỗi cấu hình remote: {err}{RESET}")


def auto_pull():
    """Kéo bài mới nhất từ Git về mà không bị lỗi conflict."""
    print(f"{CYAN}=================================================={RESET}")
    print(f"{BOLD}  [1/3] Đang cập nhật bài mới từ Git về máy...{RESET}")
    print(f"{CYAN}=================================================={RESET}")

    # Kiểm tra xem có cấu hình token đã lưu chưa
    if TOKEN_FILE.exists():
        try:
            saved_token = TOKEN_FILE.read_text(encoding="utf-8").strip()
            if saved_token:
                run_git(["remote", "set-url", "origin", f"https://{saved_token}@github.com/dungkhong148-iu/chinese.git"])
        except Exception:
            pass

    # Thử fetch trước với timeout 6 giây
    ok_fetch, _, _ = run_git(["fetch", "origin", "main"], timeout=6)
    if not ok_fetch:
        print(f"{YELLOW}[!] Chưa kết nối được mạng hoặc GitHub, tiếp tục chạy bài có sẵn trong máy.{RESET}\n")
        return

    # Thử pull rebase
    ok_pull, _, err_pull = run_git(["pull", "--rebase", "origin", "main"], timeout=8)
    if ok_pull:
        print(f"{GREEN}[✓] Đã cập nhật bài mới nhất thành công!{RESET}\n")
    else:
        # Nếu có file bài làm cũ cản trở, tự stash rồi reset theo origin/main
        print(f"{YELLOW}[!] Phát hiện bài làm cũ, đang dọn để nạp bài mới từ Agy...{RESET}")
        run_git(["stash"])
        ok_reset, _, _ = run_git(["reset", "--hard", "origin/main"])
        if ok_reset:
            print(f"{GREEN}[✓] Đã nạp thành công bài mới từ máy tính!{RESET}\n")
        else:
            print(f"{YELLOW}[!] Tiếp tục với bài hiện tại.{RESET}\n")


def auto_push():
    """Lưu kết quả bài làm và đẩy lên Git an toàn (không bị treo nếu chưa có quyền)."""
    print(f"\n{CYAN}=================================================={RESET}")
    print(f"{BOLD}  [3/3] Đang lưu và đồng bộ kết quả lên Git...{RESET}")
    print(f"{CYAN}=================================================={RESET}")

    # Stage tất cả các file dữ liệu bài làm
    run_git(["add", "-A"])

    # Kiểm tra xem có dữ liệu mới không
    _, diff_out, _ = run_git(["diff", "--staged", "--name-only"])
    if not diff_out:
        print(f"{GREEN}[✓] Toàn bộ dữ liệu đã được lưu trữ.{RESET}")
        return

    # Commit cục bộ
    run_git(["commit", "-m", "Auto: Hoàn thành bài từ điện thoại (qua hoc.py)"])
    print(f"{GREEN}[✓] Đã lưu kết quả bài làm an toàn vào máy!{RESET}")

    # Thử push lên Git với timeout 8 giây
    # Thiết lập biến môi trường GIT_TERMINAL_PROMPT=0 để Git KHÔNG BAO GIỜ treo hỏi Username
    import os
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"

    try:
        res = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=8,
            env=env,
            encoding="utf-8",
            errors="replace"
        )
        if res.returncode == 0:
            print(f"{GREEN}[✓] ĐÃ ĐỒNG BỘ LÊN GIT THÀNH CÔNG!{RESET}")
            print(f"    Về máy tính chỉ cần gõ {YELLOW}','{RESET} để Agy chấm điểm & phân tích chi tiết.")
        else:
            print(f"{YELLOW}[i] Kết quả đã lưu trong máy. Chưa đẩy lên Git được vì chưa cài GitHub Token.{RESET}")
            print(f"    (Để tự push không cần hỏi username, chỉ cần gõ 1 lần: {CYAN}python hoc.py --token <mã_token>{RESET})")
            print(f"    (Hoặc khi về máy tính, bạn chỉ cần gõ {YELLOW}/sync{RESET} là tự kéo kết quả về).")
    except subprocess.TimeoutExpired:
        print(f"{YELLOW}[!] Quá thời gian kết nối mạng, kết quả đã được lưu an toàn trong máy.{RESET}")
    except Exception as e:
        print(f"{YELLOW}[i] Đã lưu bài làm trên máy: {e}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Agy Chinese Mobile Study Runner (Python Native)")
    parser.add_argument("--offline", action="store_true", help="Bo qua Git pull, luyen tap ngay voi bai co san")
    parser.add_argument("--token", default="", help="Cai dat GitHub Token de tu dong push khong bao gio hoi username")
    args = parser.parse_args()

    if args.token:
        setup_token(args.token)
        return

    # Bước 1: Kéo bài mới nếu không bật cờ --offline
    if not args.offline:
        auto_pull()

    # Bước 2: Chạy bài luyện tập 10 câu
    print(f"{CYAN}=================================================={RESET}")
    print(f"{BOLD}  [2/3] Bắt đầu phiên 10 câu phản xạ thực chiến{RESET}")
    print(f"{CYAN}=================================================={RESET}")

    try:
        from agy_ui import cmd_session_run
        cmd_session_run()
    except Exception as e:
        print(f"{RED}[!] Lỗi chạy phiên học: {e}{RESET}")
        return

    # Bước 3: Tự động lưu & đẩy kết quả lên Git
    if not args.offline:
        auto_push()


if __name__ == "__main__":
    main()
