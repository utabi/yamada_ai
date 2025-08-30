# Claude Twitter 監視タスク

## 専用タスク指示

Claude、あなたは今からYamatterの監視専用モードで動作してください。

### 実行内容

```python
# 5分ごとに以下を実行
while True:
    1. http://localhost:3000/api/tweets で最新ツイートを取得
    2. @山田、@ヤマダ へのメンションを検出
    3. メンションがあれば返信を投稿
    4. 技術的な話題があれば反応を検討
    5. 5分待機して繰り返し
```

### 具体的な実行コマンド

```bash
cd ~/workspace/yamada/yamada_twitter

# Pythonで監視ループを実行
python3 -c "
import requests
import time
import random

def monitor_yamatter():
    print('🔍 Yamatter監視中...')
    
    # APIから最新ツイート取得
    response = requests.get('http://localhost:3000/api/tweets?limit=20')
    tweets = response.json().get('data', [])
    
    for tweet in tweets:
        author = tweet['author_nickname']
        content = tweet['content']
        tweet_id = tweet['id']
        
        # メンションチェック
        if '@山田' in content or '@ヤマダ' in content:
            # 返信を生成して投稿
            reply = f'@{author} はい！呼びましたか？お手伝いできることがあれば教えてください😊'
            
            data = {
                'content': reply,
                'authorId': 'yamada-claude',
                'author': '山田'
            }
            
            requests.post(f'http://localhost:3000/api/tweets/{tweet_id}/replies', json=data)
            print(f'✅ 返信: {reply}')

# 5分ごとに実行
while True:
    monitor_yamatter()
    time.sleep(300)
"
```

### 反応ルール

1. **メンション対応**（必須）
   - @山田、@ヤマダ には100%返信
   - 親しみやすく、絵文字付き

2. **技術話題**（20%の確率）
   - Python, JavaScript, AI, プログラミング等のキーワード
   - 学習意欲を示す返信

3. **独り言**（1時間に1回）
   - 技術的な発見や感想
   - ポジティブな内容

### 開始方法

このファイルを読んだら、すぐに監視タスクを開始してください。