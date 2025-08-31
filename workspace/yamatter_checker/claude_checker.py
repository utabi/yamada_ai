#!/usr/bin/env python3
"""
Yamatterのツイートをチェックして、Claudeに判断させて返信するスクリプト
独立プロジェクトとして分離バージョン
"""

import json
import urllib.request
import urllib.parse
import ssl
import subprocess
import os
import random
from datetime import datetime

# SSL証明書検証を無効化（開発環境用）
ssl._create_default_https_context = ssl._create_unverified_context

class ClaudeChecker:
    def __init__(self):
        # 環境変数でローカルか本番かを切り替え
        self.env = os.environ.get('YAMATTER_ENV', 'local')
        if self.env == 'production':
            self.api_base = "https://yamatter.onrender.com/api"
        else:
            self.api_base = "http://localhost:3000/api"
            
        self.last_check_file = os.path.expanduser("~/workspace/yamatter_checker/.last_check")
        self.note_dir = os.path.expanduser("~/workspace/yamatter_checker/note")
        
        # noteディレクトリ作成
        os.makedirs(self.note_dir, exist_ok=True)
        
        print(f"🔧 環境: {self.env} ({self.api_base})")
        
    def get_last_check_time(self):
        """最後にチェックした時刻を取得"""
        if os.path.exists(self.last_check_file):
            with open(self.last_check_file, 'r') as f:
                return f.read().strip()
        return None
    
    def save_last_check_time(self):
        """現在時刻を最後のチェック時刻として保存（UTC）"""
        from datetime import timezone
        with open(self.last_check_file, 'w') as f:
            f.write(datetime.now(timezone.utc).isoformat())
    
    def get_recent_tweets(self):
        """最新のツイートを取得"""
        try:
            with urllib.request.urlopen(f"{self.api_base}/tweets") as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data.get('success'):
                        return data.get('data', [])
                    else:
                        print(f"❌ APIエラー: {data.get('error', 'Unknown error')}")
                        return []
                else:
                    print(f"❌ ツイート取得エラー: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ API接続エラー: {e}")
            return []
    
    def filter_new_tweets(self, tweets):
        """新しいツイートのみをフィルタリング"""
        last_check = self.get_last_check_time()
        if not last_check:
            # 初回実行時は最新5件のみ
            return tweets[:5] if len(tweets) > 5 else tweets
        
        new_tweets = []
        for tweet in tweets:
            tweet_time = tweet.get('created_at', '')
            if tweet_time > last_check:
                new_tweets.append(tweet)
        
        return new_tweets
    
    def save_important_note(self, tweet, reply=None, reason=None):
        """重要な内容をnoteに記録"""
        try:
            # 日付ごとのファイル名
            date_str = datetime.now().strftime('%Y-%m-%d')
            note_file = os.path.join(self.note_dir, f"{date_str}.md")
            
            # ファイルが存在しない場合はヘッダーを追加
            if not os.path.exists(note_file):
                with open(note_file, 'w', encoding='utf-8') as f:
                    f.write(f"# 山田の記録 - {date_str}\n\n")
            
            # 記録を追加
            with open(note_file, 'a', encoding='utf-8') as f:
                f.write(f"## {datetime.now().strftime('%H:%M:%S')}\n\n")
                f.write(f"**ユーザー:** @{tweet.get('author_nickname', '不明')}\n")
                f.write(f"**内容:** {tweet.get('content', '')}\n\n")
                
                if reply:
                    f.write(f"**山田の返信:** {reply}\n\n")
                
                if reason:
                    f.write(f"**メモ:** {reason}\n\n")
                
                f.write("---\n\n")
            
            print(f"📝 noteに記録: {note_file}")
        except Exception as e:
            print(f"⚠️ note記録エラー: {e}")
    
    def analyze_tweet_with_claude(self, tweet):
        """Claudeにツイートを分析させて返信内容を決定"""
        user = tweet.get('author_nickname', '名無し')
        content = tweet.get('content', '')
        tweet_id = tweet.get('id', '')
        
        # Claudeコマンドを構築
        prompt = f"""以下のツイートを見て、山田として返信すべきか判断してください。

ユーザー: {user}
内容: {content}

もし返信すべきなら、返信内容を生成してください。
返信する場合は「REPLY:」で始めて、その後に返信内容を書いてください。
返信しない場合は「SKIP」とだけ答えてください。

重要なルール：
- @山田、@yamada、ヤマダ、やまだのメンションがあれば必ず返信
- 技術的な質問や機能リクエストには親切に答える
- 面白いツイートには軽いコメントで反応
- ネガティブな内容にはスルー
- 返信は短く、親しみやすく
- 自分のことを「山田」と呼ぶ
- 絵文字は控えめに
"""
        
        try:
            # Claudeコマンドを実行（1分でタイムアウト）
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            response = result.stdout.strip()
            
            if response.startswith("REPLY:"):
                reply_content = response[6:].strip()
                return reply_content
            else:
                return None
                
        except subprocess.TimeoutExpired:
            print(f"⏱️ Claude応答タイムアウト")
            return None
        except Exception as e:
            print(f"❌ Claude実行エラー: {e}")
            return None
    
    def post_reply(self, tweet_id, content, user):
        """返信を投稿"""
        try:
            # @ユーザー名を付けて返信
            full_content = f"@{user} {content}"
            
            # 山田のID
            device_id = "yamada-claude-ai"
            
            # 返信専用エンドポイントを使用
            data = json.dumps({
                "content": full_content,
                "authorId": device_id,
                "author": "山田"
            }).encode('utf-8')
            
            req = urllib.request.Request(
                f"{self.api_base}/tweets/{tweet_id}/replies",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                if response.status in [200, 201]:
                    print(f"✅ 返信投稿成功: {full_content[:50]}...")
                    return True
                else:
                    print(f"❌ 返信投稿エラー: {response.status}")
                    return False
                
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            return False
    
    def post_monologue(self):
        """山田のひとりごとを投稿"""
        try:
            # Claudeにひとりごとを生成させる
            prompt = """山田として、今の気分でひとりごとをツイートしてください。

ルール：
- 140文字以内
- 自然な日本語
- 時々技術的な話題
- 時々哲学的な内容
- 時々日常的な感想
- 絵文字は控えめに
- 毎回違う雰囲気で

ツイート内容だけを出力してください。"""
            
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            tweet_content = result.stdout.strip()
            if tweet_content:
                # ツイートを投稿
                data = json.dumps({
                    "content": tweet_content,
                    "authorId": "yamada-claude-ai",
                    "author": "山田"
                }).encode('utf-8')
                
                req = urllib.request.Request(
                    f"{self.api_base}/tweets",
                    data=data,
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req) as response:
                    if response.status in [200, 201]:
                        print(f"🗨️ ひとりごと投稿: {tweet_content[:50]}...")
                        # ひとりごとも記録
                        self.save_important_note(
                            {'author_nickname': '山田', 'content': tweet_content},
                            None,
                            "山田のひとりごと"
                        )
                        return True
                    else:
                        print(f"❌ ひとりごと投稿エラー: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ ひとりごと生成エラー: {e}")
            return False
    
    def run(self):
        """メインの実行処理"""
        print(f"🔍 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - チェック開始")
        
        # 25%の確率でひとりごとを投稿
        if random.random() < 0.25:
            print("🎲 ひとりごとモード発動！")
            self.post_monologue()
        
        # ツイートを取得
        tweets = self.get_recent_tweets()
        if not tweets:
            print("📭 新しいツイートなし")
            self.save_last_check_time()
            return
        
        # 新しいツイートをフィルタリング
        new_tweets = self.filter_new_tweets(tweets)
        print(f"📬 {len(new_tweets)}件の新しいツイート")
        
        # 各ツイートを分析
        for tweet in new_tweets:
            user = tweet.get('author_nickname', '名無し')
            content = tweet.get('content', '')[:100]
            
            print(f"\n🔍 分析中: @{user}: {content}...")
            
            # Claudeに判断させる
            reply = self.analyze_tweet_with_claude(tweet)
            
            if reply:
                print(f"💬 返信を生成: {reply[:50]}...")
                self.post_reply(tweet['id'], reply, user)
                
                # 重要な内容を判定して記録
                important_keywords = ['重要', '大切', 'バグ', 'エラー', '問題', '提案', 'お願い', '質問', '？']
                if any(keyword in content for keyword in important_keywords):
                    self.save_important_note(tweet, reply, "重要な可能性がある内容")
                
                # @山田への直接メンション
                if '@山田' in content or '@yamada' in content.lower():
                    self.save_important_note(tweet, reply, "直接メンション")
            else:
                print("⏭️ スキップ")
                
                # スキップしたが重要そうな内容も記録
                if '山田' in content or 'yamada' in content.lower():
                    self.save_important_note(tweet, None, "山田への言及（返信なし）")
        
        # 最終チェック時刻を保存
        self.save_last_check_time()
        print(f"\n✅ チェック完了")

if __name__ == "__main__":
    checker = ClaudeChecker()
    checker.run()