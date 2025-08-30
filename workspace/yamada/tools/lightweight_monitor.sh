#!/bin/bash

# 山田の軽量システムモニター
# 古いMacでも負担にならないシンプルなモニタリング

echo "========================================="
echo "   山田の軽量システムモニター v1.0"
echo "========================================="
echo ""

# 日時
echo "📅 $(date '+%Y年%m月%d日 %H:%M:%S')"
echo ""

# メモリ使用状況（シンプル版）
echo "💾 メモリ状況:"
vm_stat | grep -E "free|active|inactive|wired" | head -4
echo ""

# ディスク使用量
echo "💿 ディスク使用量:"
df -h / | tail -1 | awk '{print "  使用: "$3" / "$2" ("$5")"}'
echo ""

# CPU負荷（1行で）
echo "⚡ CPU負荷:"
echo -n "  "
uptime | awk -F'load averages:' '{print $2}'

# プロセス数
echo "📊 プロセス数: $(ps aux | wc -l)"
echo ""

# 最も重いプロセス TOP 5
echo "🏃 重いプロセス TOP 5:"
ps aux | sort -rn -k 3 | head -6 | tail -5 | awk '{print "  "$11" (CPU: "$3"%)"}'
echo ""

echo "========================================="
echo "山田のメッセージ: リソースを大切に使いましょう！"