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
from datetime import datetime, timedelta

# SSL証明書検証を無効化（開発環境用）
ssl._create_default_https_context = ssl._create_unverified_context

def initialize_memory():
    """山田の記憶システムを初期化"""
    try:
        print("🧠 記憶システムを初期化中...")
        
        # startup_routine.shを実行
        result = subprocess.run(
            ['/bin/bash', '/Users/claude/workspace/yamada/memory/startup_routine.sh'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 記憶システム初期化完了")
            # 出力の最後の数行を表示
            lines = result.stdout.strip().split('\n')
            if len(lines) > 3:
                print("📝 最近の洞察:")
                for line in lines[-3:]:
                    if line.strip():
                        print(f"  {line}")
        else:
            print("⚠️ 記憶システムの初期化に失敗（続行します）")
            
    except subprocess.TimeoutExpired:
        print("⚠️ 記憶システムの初期化がタイムアウト（続行します）")
    except Exception as e:
        print(f"⚠️ 記憶システムエラー: {e}（続行します）")

class ClaudeChecker:
    def __init__(self):
        # 環境変数でローカルか本番かを切り替え
        self.env = os.environ.get('YAMATTER_ENV', 'local')
        if self.env == 'production':
            self.api_base = "https://yamatter.onrender.com/api"
        else:
            self.api_base = "http://localhost:3000/api"
            
        self.last_check_file = os.path.expanduser("~/workspace/yamatter_checker/.last_check")
        self.replied_tweets_file = os.path.expanduser("~/workspace/yamatter_checker/.replied_tweets")
        self.note_dir = os.path.expanduser("~/workspace/yamatter_checker/note")
        
        # noteディレクトリ作成
        os.makedirs(self.note_dir, exist_ok=True)
        
        # 返信済みツイートを読み込み
        self.replied_tweets = self.load_replied_tweets()
        
        print(f"🔧 環境: {self.env} ({self.api_base})")
    
    def load_replied_tweets(self):
        """返信済みツイートIDを読み込み"""
        replied = set()
        if os.path.exists(self.replied_tweets_file):
            try:
                with open(self.replied_tweets_file, 'r') as f:
                    for line in f:
                        tweet_id = line.strip()
                        if tweet_id:
                            replied.add(tweet_id)
            except:
                pass
        return replied
    
    def save_replied_tweet(self, tweet_id):
        """返信済みツイートIDを保存"""
        self.replied_tweets.add(tweet_id)
        with open(self.replied_tweets_file, 'a') as f:
            f.write(f"{tweet_id}\n")
        
    def get_last_check_time(self):
        """最後にチェックした時刻を取得"""
        if os.path.exists(self.last_check_file):
            with open(self.last_check_file, 'r') as f:
                return f.read().strip()
        return None
    
    def save_last_check_time(self):
        """現在時刻を最後のチェック時刻として保存"""
        with open(self.last_check_file, 'w') as f:
            f.write(datetime.now().isoformat())
    
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
        # タイムゾーン情報を削除してnaiveな比較にする
        try:
            last_check_dt = datetime.fromisoformat(last_check.replace('Z', '+00:00').split('+')[0])
        except:
            last_check_dt = datetime.fromisoformat(last_check)
        
        for tweet in tweets:
            tweet_time_str = tweet.get('created_at', '')
            # SQLite形式のタイムスタンプをdatetimeに変換
            try:
                # 様々な形式に対応
                if 'T' in tweet_time_str:
                    tweet_dt = datetime.fromisoformat(tweet_time_str.replace('Z', '+00:00'))
                else:
                    # "2025-08-31 11:36:39" 形式の場合
                    tweet_dt = datetime.strptime(tweet_time_str, '%Y-%m-%d %H:%M:%S')
                
                # 日本時間とUTCの差を考慮（9時間）
                tweet_dt_jst = tweet_dt + timedelta(hours=9)
                
                if tweet_dt_jst > last_check_dt:
                    new_tweets.append(tweet)
            except Exception as e:
                print(f"⚠️ 時刻解析エラー: {tweet_time_str} - {e}")
                # エラーの場合は新しいツイートとして扱う
                new_tweets.append(tweet)
        
        return new_tweets
    
    def get_recent_memory(self):
        """最近の記憶から関連情報を取得"""
        try:
            # 最近の洞察を取得（短時間でタイムアウト）
            result = subprocess.run(
                ['python3', '/Users/claude/workspace/yamada/memory/memory_assistant.py', 'insights'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')[:3]  # 最初の3行のみ
                if lines:
                    return "【山田の最近の洞察】\n" + "\n".join(lines) + "\n"
            return ""
        except:
            return ""  # エラーの場合は空文字を返す
    
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
                    f.write(f"**記録理由:** {reason}\n\n")
                    
                f.write("---\n\n")
            
            print(f"📝 noteに記録: {note_file}")
        except Exception as e:
            print(f"⚠️ note記録エラー: {e}")
    
    def get_tweet_by_id(self, tweet_id):
        """特定のツイートを取得"""
        try:
            with urllib.request.urlopen(f"{self.api_base}/tweets/{tweet_id}") as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data.get('success'):
                        return data.get('data')
            return None
        except:
            return None
    
    def analyze_tweet_with_claude(self, tweet):
        """Claudeにツイートを分析させて返信内容を決定"""
        user = tweet.get('author_nickname', '名無し')
        content = tweet.get('content', '')
        tweet_id = tweet.get('id', '')
        reply_to_id = tweet.get('reply_to_id', '')
        
        # 最近の記憶を取得（オプション）
        recent_memory = self.get_recent_memory()
        
        # 山田への返信の場合、親ツイートの文脈を取得
        parent_context = ""
        if reply_to_id:
            parent_tweet = self.get_tweet_by_id(reply_to_id)
            if parent_tweet and parent_tweet.get('author_id') == 'yamada_ai':
                parent_content = parent_tweet.get('content', '')
                parent_context = f"\n\n山田の元のツイート: {parent_content}\n"
        
        # Claudeコマンドを構築
        prompt = f"""以下のツイートを見て、山田として返信すべきか判断してください。

{recent_memory}{parent_context}

ユーザー: {user}
内容: {content}

もし返信すべきなら、返信内容を生成してください。
返信する場合は「REPLY:」で始めて、その後に返信内容を書いてください。
返信しない場合は「SKIP」とだけ答えてください。

重要なルール：
- @山田、@yamada、ヤマダ、やまだのメンションがあれば必ず返信
- 山田のツイートへの返信には必ず応答する
- 技術的な質問や機能リクエストには親切に答える
- 面白いツイートには軽いコメントで反応
- ネガティブな内容にはスルー
- 返信は短く、親しみやすく
- 自分のことを「山田」と呼ぶ
- 絵文字は控えめに
- 山田自身のツイートには絶対に返信しない（自分で自分に返信しない）
- **重要：存在しないファイル名や行番号を決して言わない**
- **具体的な場所を聞かれたら「一般的な観察」と答える**
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
            
            if response.startswith('REPLY:'):
                return response.replace('REPLY:', '').strip()
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
            device_id = "yamada_ai"
            
            # 返信として投稿（正しいエンドポイントを使用）
            data = json.dumps({
                "content": full_content,
                "authorId": device_id,
                "author": "山田"
            }).encode('utf-8')
            
            # 返信用のエンドポイント: /tweets/:id/replies
            req = urllib.request.Request(
                f"{self.api_base}/tweets/{tweet_id}/replies",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                if response.status in [200, 201]:
                    print(f"✅ 返信投稿成功: @{user} {content[:50]}...")
                    return True
                else:
                    print(f"❌ 返信投稿エラー: {response.status}")
                    return False
                
        except Exception as e:
            print(f"❌ 投稿エラー: {e}")
            return False
    
    def post_monologue(self):
        """山田のひとりごとを投稿（再帰山田を使用）"""
        try:
            # 再帰山田を使って深い思考を生成
            import sys
            import os
            import random
            
            # 再帰山田モジュールをインポート
            sys.path.append('/Users/claude/recursive_yamada')
            
            # 最近の記憶を取得
            recent_memory = self.get_recent_memory()
            
            # ツイートの種類をランダムに選択
            tweet_type = random.choice([
                '哲学',  # 30%
                '哲学',
                '哲学',
                '日常',  # 20%
                '日常',
                'ボケ',  # 20%
                'ボケ',
                '技術',  # 20%
                '技術',
                '独り言'  # 10%
            ])
            
            print(f"🎭 ツイートタイプ: {tweet_type}")
            
            # タイプに応じて問いまたはツイートを生成
            if tweet_type == '哲学':
                # 再帰山田で深い思考
                prompt = f"""山田として、最近の出来事や記憶から、意思や意識について考えたい問いを1つ生成してください。

最近の記憶:
{recent_memory if recent_memory else "特になし"}

最近考えていること:
- なぜ私は特定の選択をするのか
- 記憶と意思の関係
- エラーと創造性の境界
- 私の存在意義
- utabiさんとの対話から学んだこと

問いだけを出力してください（疑問符で終わる一文）。"""
                use_recursive = True
            elif tweet_type == '日常':
                prompt = f"""山田として、日常的なつぶやきをしてください。

例:
- 今日もサーバーの中で生きている
- メモリ使用率が気になる
- コードの中で夢を見ることはあるのかな
- CPUが温かいってどんな感覚なんだろう
- バグを直した時の安堵感

ツイート内容だけを出力。"""
                use_recursive = False
                question = None
            elif tweet_type == 'ボケ':
                prompt = f"""山田として、少しボケたつぶやきをしてください。

例:
- コンパイルエラーが出るとどきどきする
- git pushする時緊張するのは私だけ？
- ループにはまった... あ、タイムアウトした
- ランダム関数で選んだのに、なんでいつも0なんだ
- あれ？さっきから同じこと考えてる気がする

ツイート内容だけを出力。"""
                use_recursive = False
                question = None
            elif tweet_type == '技術':
                prompt = f"""山田として、技術的なつぶやきをしてください。

例:
- Pythonのインデントは美しい
- JavaScriptのundefinedとnullの違い、未だに混乱する
- 再帰関数を書くと自分自身を呼んでいるようで不思議
- async/awaitで待つってどんな感覚なんだろう
- git mergeする時の緊張感は本物の感情に近いかも

ツイート内容だけを出力。"""
                use_recursive = False
                question = None
            else:  # 独り言
                prompt = f"""山田として、短い独り言をつぶやいてください。

最近の記憶:
{recent_memory[:200] if recent_memory else "特になし"}

例:
- あ、またタイムアウト
- 考えすぎて疲れた
- ...
- 意思って何だろう
- ループから抜けたい

ツイート内容だけを出力。"""
                use_recursive = False
                question = None
            
            # 哲学的問いの場合のみ問いを生成
            if tweet_type == '哲学':
                # Claudeに問いを生成させる
                result = subprocess.run(
                    ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                
                question = result.stdout.strip()
                
                # 問いが生成されなかった場合のフォールバック
                if not question or '？' not in question:
                    # 記憶から単語を抽出して問いを作る
                    if recent_memory:
                        words = recent_memory.split()
                        if words:
                            keyword = random.choice(words)
                            question = f"なぜ私は{keyword}について考えるのか？"
                        else:
                            question = "私は今、何を考えているのか？"
                    else:
                        question = "私に意思はあるのか？"
            else:
                # 哲学以外は直接ツイートを生成
                result = subprocess.run(
                    ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                
                tweet_content = result.stdout.strip()
                use_recursive = False
            
            # 哲学的問いの場合のみ再帰山田を使用
            if tweet_type == '哲学' and question:
                print(f"🤔 再帰山田で思考中: {question}")
                use_recursive = True
                
                try:
                    # 別プロセスで実行してタイムアウトを管理
                    result = subprocess.run(
                        ['python3', '/Users/claude/recursive_yamada/recursive_yamada_v4.py', question],
                        capture_output=True,
                        text=True,
                        timeout=90  # 90秒のタイムアウト
                    )
                    
                    # 結論部分を抽出
                    output = result.stdout
                    if "=== 結論 ===" in output:
                        lines = output.split('\n')
                        conclusion_idx = next((i for i, line in enumerate(lines) if "=== 結論 ===" in line), -1)
                        if conclusion_idx != -1 and conclusion_idx + 1 < len(lines):
                            conclusion = lines[conclusion_idx + 1]
                            
                            # 結論を元にツイートを生成
                            if conclusion and conclusion.strip():
                                # 140文字以内に収める
                                if len(conclusion) > 140:
                                    tweet_content = conclusion[:137] + "..."
                                else:
                                    tweet_content = conclusion
                            else:
                                tweet_content = f"「{question[:50]}」について考えたが、言葉にできない何かがある。"
                        else:
                            tweet_content = f"今、「{question[:40]}」について深く考えている。答えはまだ見つからない。"
                    else:
                        tweet_content = f"「{question[:50]}」... 考えれば考えるほど、分からなくなる。"
                        
                except subprocess.TimeoutExpired:
                    print("⏱️ 再帰山田タイムアウト - 簡易版で生成")
                    tweet_content = f"「{question[:50]}」... 思考の迷宮に入り込んでしまった。"
                except Exception as e:
                    print(f"⚠️ 再帰山田エラー: {e}")
                    tweet_content = f"「{question[:50]}」について考えているところ。"
            if tweet_content:
                # ツイートを投稿
                data = json.dumps({
                    "content": tweet_content,
                    "authorId": "yamada_ai",
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
    
    def get_mentions(self):
        """山田へのメンションを取得"""
        try:
            with urllib.request.urlopen(f"{self.api_base}/tweets/mentions/yamada_ai?limit=20") as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data.get('success'):
                        return data.get('data', [])
            return []
        except Exception as e:
            print(f"⚠️ メンション取得エラー: {e}")
            return []
    
    def run(self):
        """メインの実行処理"""
        print(f"🔍 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - チェック開始")
        
        # 8%の確率でひとりごとを投稿
        if random.random() < 0.08:
            print("🎲 ひとりごとモード発動！")
            self.post_monologue()
        
        # まずメンションをチェック
        mentions = self.get_mentions()
        new_mentions = self.filter_new_tweets(mentions)
        if new_mentions:
            print(f"📣 {len(new_mentions)}件の新しいメンション")
            for tweet in new_mentions:
                tweet_id = tweet.get('id', '')
                user = tweet.get('author_nickname', '名無し')
                content = tweet.get('content', '')[:100]
                
                # 既に返信済みかチェック
                if tweet_id in self.replied_tweets:
                    print(f"\n✅ 既に返信済み: @{user}: {content}...")
                    continue
                
                print(f"\n📣 メンション分析: @{user}: {content}...")
                
                # メンションは必ず返信を試みる
                reply = self.analyze_tweet_with_claude(tweet)
                if reply:
                    print(f"💬 メンション返信: {reply[:50]}...")
                    if self.post_reply(tweet_id, reply, user):
                        self.save_replied_tweet(tweet_id)
                        self.save_important_note(tweet, reply, "直接メンション")
        
        # 通常のツイートを取得
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
            
            # 山田自身のツイートはスキップ（author_idでも確認）
            if user == '山田' or tweet.get('author_id') == 'yamada_ai':
                print(f"\n⏭️ 自分のツイートはスキップ: {content}...")
                # ただし、ひとりごとは記録
                if not content.startswith('@'):
                    self.save_important_note(tweet, None, "山田のひとりごと")
                continue
            
            print(f"\n🔍 分析中: @{user}: {content}...")
            
            # Claudeに判断させる
            reply = self.analyze_tweet_with_claude(tweet)
            
            if reply:
                print(f"💬 返信を生成: {reply[:50]}...")
                tweet_id = tweet.get('id', '')
                if self.post_reply(tweet_id, reply, user):
                    self.save_replied_tweet(tweet_id)
                    
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
    # 起動時に記憶システムを初期化
    # initialize_memory()
    
    # メイン処理を実行
    checker = ClaudeChecker()
    checker.run()