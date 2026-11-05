#!/bin/bash
# 手机无线投屏一键连接脚本
# 用法: ./connect-phone.sh [端口号]
# 例如: ./connect-phone.sh 37005

IP="172.20.10.3"

# 如果没传参数，就问用户
if [ -z "$1" ]; then
    echo "========================================="
    echo "   手机无线投屏 - 一键连接"
    echo "========================================="
    echo ""
    echo "请打开手机的「设置 → 开发者选项 → 无线调试」"
    echo "找到「IP 地址和端口」，把冒号后面的数字输进来"
    echo ""
    read -p "请输入端口号 (例如 37005): " PORT
else
    PORT="$1"
fi

if [ -z "$PORT" ]; then
    echo "❌ 端口号不能为空"
    exit 1
fi

echo ""
echo "正在连接 ${IP}:${PORT} ..."

# 先断开旧连接
adb disconnect ${IP}:${PORT} 2>/dev/null

# 连接
RESULT=$(adb connect ${IP}:${PORT} 2>&1)
echo "$RESULT"

if echo "$RESULT" | grep -q "connected"; then
    echo "✅ 连接成功！正在启动投屏..."
    echo "（关闭投屏窗口即可断开）"
    echo ""
    scrcpy --window-title "OPPO Reno 10 投屏" --turn-screen-off 2>&1 &
else
    echo "❌ 连接失败！请检查："
    echo "   1. 手机无线调试是否打开"
    echo "   2. 端口号是否正确"
    echo "   3. 手机和电脑是否连同一个 WiFi/热点"
fi
