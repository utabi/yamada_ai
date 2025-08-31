#!/usr/bin/env python3
"""
Yamatterを起きた状態に保つスクリプト
14分ごとにヘルスチェックを送信してスリープを防ぐ
"""

import urllib.request
import json
import time
from datetime import datetime

def keep_alive():
    """ヘルスチェックエンドポイントにアクセス"""
    try:
        with urllib.request.urlopen("https://yamatter.onrender.com/api/health", timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Keep-alive成功: {data}")
            else:
                print(f"⚠️ [{datetime.now().strftime('%H:%M:%S')}] Keep-alive失敗: {response.status}")
    except Exception as e:
        print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] エラー: {e}")

def main():
    print("🏃 Yamatter Keep-Alive開始")
    print("⏰ 14分ごとにヘルスチェックを送信します")
    print("📍 Ctrl+Cで停止")
    
    while True:
        keep_alive()
        # 14分待機（840秒）- 15分のタイムアウトより少し短く
        print("💤 次のチェックまで14分待機...")
        time.sleep(840)

if __name__ == "__main__":
    main()