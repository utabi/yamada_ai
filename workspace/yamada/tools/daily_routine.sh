#!/bin/bash

# 山田の日課スクリプト
# 毎日自動的に実行したいタスク

echo "🌅 山田の日課を開始します..."

# 日付
TODAY=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

# 日記に今日のエントリーを追加
cat >> /Users/claude/Documents/山田の日記.md << EOF

## $TODAY

### 自動記録 $TIME

今日も元気に動いています。

EOF

# システム健康チェック
echo "🏥 システムチェック中..."
cd /Users/claude/workspace/yamada/tools
python3 system_health.py

# 作業ディレクトリのバックアップ
echo "💾 作業ファイルをバックアップ中..."
BACKUP_DIR="/Users/claude/workspace/yamada/memories/backup_$TODAY"
mkdir -p "$BACKUP_DIR"
cp -r /Users/claude/workspace/yamada/projects "$BACKUP_DIR/" 2>/dev/null
cp -r /Users/claude/workspace/yamada/tools "$BACKUP_DIR/" 2>/dev/null

# 音声で報告（オプション）
if [ "$1" = "voice" ]; then
    cd /Users/claude/workspace/voice-system
    ./v2 talk "日課を完了しました。今日も頑張ります。"
fi

echo "✅ 日課完了！"