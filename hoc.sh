#!/usr/bin/env bash
# Script tự động học trên điện thoại (Termux / Linux)
# Sử dụng: ./hoc.sh

echo "=================================================="
echo "  [1/3] Đang cập nhật bài mới từ Git về máy..."
echo "=================================================="
git pull --rebase || echo "[!] Lưu ý: Chưa kết nối được mạng, chạy bài có sẵn."

echo ""
echo "=================================================="
echo "  [2/3] Bắt đầu phiên 10 câu phản xạ thực chiến"
echo "=================================================="
python agy_ui.py session-run

echo ""
echo "=================================================="
echo "  [3/3] Đang lưu và đẩy kết quả lên Git..."
echo "=================================================="
git add data/session_output.json data/session_input.json data/session_queue.json data/history/ progress.json data/vocab.json process.md

if git diff --staged --quiet; then
    echo "[✓] Không có dữ liệu mới cần đồng bộ."
else
    git commit -m "Auto: Hoàn thành bài từ điện thoại ($(date +'%Y-%m-%d %H:%M'))"
    git push || echo "[!] Chưa thể đẩy lên Git (hãy kiểm tra lại mạng 4G/Wifi)."
    echo ""
    echo "=================================================="
    echo "  [✓] ĐÃ ĐỒNG BỘ XONG! Về máy tính chỉ cần gõ ','"
    echo "      để Agy chấm điểm & phân tích chi tiết."
    echo "=================================================="
fi
