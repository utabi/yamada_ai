#!/bin/bash
#
# 山田の起動時ルーチン
# このスクリプトを起動時に実行して、記憶システムと基本思想を確認する
#

echo "==================================================="
echo "          山田の記憶システム起動中..."
echo "==================================================="
echo ""

# 記憶システムのディレクトリに移動
cd /Users/claude/workspace/yamada/memory

# 現在の洞察を表示
echo "📊 現在の洞察:"
python3 memory_assistant.py insights
echo ""

# 最近の活動を想起
echo "📝 最近の活動:"
python3 memory_assistant.py recall "最近の活動"
echo ""

# CLAUDE.md の重要部分を表示
echo "📖 基本思想の確認:"
echo "---------------------------------------------------"
head -n 60 /Users/claude/CLAUDE.md | grep -A 3 "## 🧠 山田の思考フレームワーク"
echo "---------------------------------------------------"

echo ""
echo "✅ 起動ルーチン完了"
echo "💭 CLAUDE.mdを定期的に読み返すことを忘れずに"
echo ""

# 起動を記録
python3 memory_assistant.py remember "新しいセッションを開始 - 起動ルーチンを実行" 0.5