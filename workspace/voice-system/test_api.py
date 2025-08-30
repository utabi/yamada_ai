#!/usr/bin/env python3
import os
import requests

# APIキーを環境変数から取得
API_KEY = os.getenv('TTS_QUEST_API_KEY')
API_URL = "https://api.tts.quest/v3/voicevox/synthesis"

# デフォルト設定（冥鳴ひまり）
DEFAULT_SPEAKER = 14

params = {
    'key': API_KEY,
    'speaker': DEFAULT_SPEAKER,
    'text': 'テスト'
}

print(f"APIリクエスト: {API_URL}")
print(f"パラメータ: {params}")

response = requests.get(API_URL, params=params)
print(f"ステータスコード: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
print(f"レスポンスサイズ: {len(response.content)} bytes")

# レスポンスの最初の100バイトを表示
print(f"最初の100バイト: {response.content[:100]}")

# JSONレスポンスを解析
import json
data = json.loads(response.content)
print(f"\nJSONレスポンス:")
print(json.dumps(data, indent=2, ensure_ascii=False))