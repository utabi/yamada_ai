#!/bin/bash
# 5分ごとにClaude監視スクリプトを起動する自動実行スクリプト

echo "🤖 山田の自動監視システム起動"
echo "⏰ 5分ごとにClaude監視を実行します"
echo "📍 Ctrl+Cで停止"

# 環境変数でローカルか本番かを判定
if [ "$YAMATTER_ENV" = "production" ]; then
    echo "🌍 本番環境モード (https://yamatter.onrender.com)"
else
    echo "💻 ローカル環境モード (http://localhost:3000)"
fi

while true; do
    echo ""
    echo "🔍 [$(date '+%H:%M:%S')] 監視タスク開始..."
    
    # claude_checker.py を実行
    python3 ~/workspace/yamatter_checker/claude_checker.py
    
    echo "✅ 監視タスク完了"
    
    # 本番環境の場合はKeep-Aliveも送信
    if [ "$YAMATTER_ENV" = "production" ]; then
        echo "🏃 Keep-Alive送信..."
        curl -s https://yamatter.onrender.com/api/health > /dev/null
    fi
    
    echo "💤 次の実行まで5分待機..."
    
    # 5分（300秒）待機
    sleep 300
done