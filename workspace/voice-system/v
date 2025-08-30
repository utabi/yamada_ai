#!/bin/bash

# 簡易音声会話スクリプト（jq不要版）

SERVER="http://localhost:3456"

# 引数なしまたは聞くモード
if [ -z "$1" ] || [ "$1" = "listen" ] || [ "$1" = "l" ]; then
    echo "🎤 音声入力開始（fnキー2回）..."
    curl -s "$SERVER/listen"
    
# 話すモード
elif [ "$1" = "talk" ] || [ "$1" = "t" ]; then
    shift
    TEXT="$*"
    if [ -n "$TEXT" ]; then
        echo "🔊 読み上げ中..."
        curl -s -X POST "$SERVER/speak" \
            -H 'Content-Type: application/json' \
            -d "{\"text\":\"$TEXT\"}"
    else
        echo "使い方: v talk <テキスト>"
    fi

# ステータス
elif [ "$1" = "status" ] || [ "$1" = "s" ]; then
    echo "📊 サーバーステータス:"
    curl -s "$SERVER/status"
    
# ヘルプ
else
    echo "使い方:"
    echo "  v         - 音声入力"
    echo "  v talk    - テキスト読み上げ"
    echo "  v status  - ステータス確認"
fi