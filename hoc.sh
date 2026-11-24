#!/usr/bin/env bash
# Script tự động học trên điện thoại (Termux / Linux)
# Sử dụng: ./hoc.sh

echo "=================================================="
echo "  [1/3] Đang cập nhật bài mới từ Git về máy..."
echo "=================================================="
git fetch origin main 2>/dev/null
if ! git pull --rebase origin main 2>/dev/null; then
    echo "[!] Phát hiện thay đổi cục bộ, đang dọn để nạp bài mới nhất..."
    git stash >/dev/null 2>&1
    git pull --rebase origin main || git reset --hard origin/main
fi

echo ""
echo "=================================================="
echo "  [2/3] Bắt đầu phiên 10 câu phản xạ thực chiến"
echo "=================================================="
python agy_ui.py session-run

echo ""
echo "=================================================="
echo "  [3/3] Đang lưu và đẩy kết quả lên Git..."
echo "=================================================="
git add -A

if git diff --staged --quiet; then
    echo "[✓] Không có dữ liệu mới cần đồng bộ."
else
    git commit -m "Auto: Hoàn thành bài từ điện thoại ($(date +'%Y-%m-%d %H:%M'))"
    git push origin main || echo "[!] Chưa thể đẩy lên Git (kiểm tra lại mạng hoặc quyền push)."
    echo ""
    echo "=================================================="
    echo "  [✓] ĐÃ ĐỒNG BỘ XONG! Về máy tính chỉ cần gõ ','"
    echo "      để Agy chấm điểm & phân tích chi tiết."
    echo "=================================================="
fi
