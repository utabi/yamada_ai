#!/bin/bash
# Claude経由でYamatterをチェックして返信するスクリプト

echo "📡 Yamatterチェック開始..."

# Pythonスクリプトを実行してツイートをチェックし、Claudeに判断させる
python3 ~/workspace/yamada/yamada_twitter/claude_checker.py