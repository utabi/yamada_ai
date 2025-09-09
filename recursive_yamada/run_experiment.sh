#!/bin/bash

# 再帰山田実験スクリプト

DATE=$(date +%Y-%m-%d_%H%M%S)
QUESTION="$1"

if [ -z "$QUESTION" ]; then
    echo "使用方法: ./run_experiment.sh \"問い\""
    exit 1
fi

echo "実験開始: $QUESTION"
echo "ログファイル: logs/${DATE}.txt"

python3 recursive_yamada.py "$QUESTION" 2>&1 | tee "logs/${DATE}.txt"

# 結果を整形してマークダウンに保存
cat << EOF > "logs/${DATE}.md"
# 実験: $(date +"%Y-%m-%d %H:%M:%S")

## 問い
\`\`\`
$QUESTION
\`\`\`

## 結果
\`\`\`
$(cat "logs/${DATE}.txt")
\`\`\`

## メモ
（ここに考察を追加）
EOF

echo "実験完了: logs/${DATE}.md"