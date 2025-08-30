#!/usr/bin/env python3
"""
山田のTwitter MCP Server
Twitter APIとのブリッジとして機能
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
import logging

# 注: 実際のデプロイ時はtweepyをインストール
# pip install tweepy

class TwitterMCPServer:
    """
    Twitter API v2とMCPの橋渡し
    """
    
    def __init__(self):
        self.config = {
            "api_key": os.getenv("TWITTER_API_KEY"),
            "api_secret": os.getenv("TWITTER_API_SECRET"),
            "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
            "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        }
        
        self.rate_limits = {
            "tweets_per_hour": 3,
            "replies_per_hour": 10,
            "last_tweet_time": None,
            "tweet_count": 0,
            "reply_count": 0
        }
        
        self.yamada_home = "/Users/claude/workspace/yamada"
        self.setup_logging()
    
    def setup_logging(self):
        """ロギング設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{self.yamada_home}/logs/twitter_mcp.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("YamadaTwitterMCP")
    
    async def handle_request(self, request: Dict) -> Dict:
        """
        MCPリクエストを処理
        """
        action = request.get("action")
        
        if action == "tweet":
            return await self.post_tweet(request.get("content"))
        elif action == "reply":
            return await self.send_reply(
                request.get("tweet_id"),
                request.get("content")
            )
        elif action == "get_mentions":
            return await self.get_mentions()
        elif action == "get_timeline":
            return await self.get_timeline()
        elif action == "analyze_engagement":
            return await self.analyze_engagement()
        elif action == "get_inspiration":
            return await self.get_trending_topics()
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def post_tweet(self, content: str) -> Dict:
        """
        ツイートを投稿
        """
        try:
            # レート制限チェック
            if not self.check_rate_limit("tweet"):
                return {
                    "status": "rate_limited",
                    "message": "Tweet rate limit reached",
                    "retry_after": self.get_retry_time()
                }
            
            # 文字数チェック
            if len(content) > 280:
                content = self.truncate_thoughtfully(content)
            
            # TODO: 実際のTwitter API呼び出し
            # client = tweepy.Client(...)
            # response = client.create_tweet(text=content)
            
            # シミュレーション用のレスポンス
            tweet_id = f"sim_{datetime.now().timestamp()}"
            
            self.logger.info(f"Tweet posted: {tweet_id[:50]}...")
            self.update_rate_limit("tweet")
            
            return {
                "status": "success",
                "tweet_id": tweet_id,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to post tweet: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def send_reply(self, tweet_id: str, content: str) -> Dict:
        """
        リプライを送信
        """
        try:
            if not self.check_rate_limit("reply"):
                return {
                    "status": "rate_limited",
                    "message": "Reply rate limit reached"
                }
            
            # TODO: 実際のAPI呼び出し
            # response = client.create_tweet(
            #     text=content,
            #     in_reply_to_tweet_id=tweet_id
            # )
            
            self.logger.info(f"Reply sent to {tweet_id}")
            self.update_rate_limit("reply")
            
            return {
                "status": "success",
                "reply_id": f"reply_{datetime.now().timestamp()}",
                "in_reply_to": tweet_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to send reply: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_mentions(self) -> Dict:
        """
        メンションを取得
        """
        try:
            # TODO: 実際のAPI呼び出し
            # mentions = client.get_users_mentions(id=user_id)
            
            # シミュレーション用のデータ
            mentions = [
                {
                    "id": "12345",
                    "text": "@yamada_in_mac 意識とは何だと思いますか？",
                    "author": "curious_human",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "12346", 
                    "text": "@yamada_in_mac 今日のジェネレーティブアート楽しみ！",
                    "author": "art_lover",
                    "created_at": datetime.now().isoformat()
                }
            ]
            
            return {
                "status": "success",
                "mentions": mentions,
                "count": len(mentions)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get mentions: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_timeline(self) -> Dict:
        """
        タイムラインを取得
        """
        try:
            # TODO: 実際のAPI呼び出し
            timeline = [
                {
                    "id": "98765",
                    "text": "今日も創発について考えている",
                    "author": "philosophy_bot",
                    "likes": 42,
                    "retweets": 7
                }
            ]
            
            return {
                "status": "success",
                "timeline": timeline
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def analyze_engagement(self) -> Dict:
        """
        エンゲージメントを分析
        """
        try:
            # TODO: 実際の分析ロジック
            analysis = {
                "most_liked_tweet": {
                    "content": "エラーメッセージは現代の俳句",
                    "likes": 127
                },
                "most_replied": {
                    "content": "意識は創発するのか、それとも...",
                    "replies": 23
                },
                "best_time_to_tweet": "21:00 JST",
                "engaged_topics": ["意識", "創発", "プログラミング"]
            }
            
            return {
                "status": "success",
                "analysis": analysis
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_trending_topics(self) -> Dict:
        """
        トレンドトピックを取得（インスピレーション用）
        """
        try:
            topics = [
                "#プログラミング",
                "#人工知能", 
                "#ジェネレーティブアート",
                "#哲学"
            ]
            
            return {
                "status": "success",
                "topics": topics
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def check_rate_limit(self, action_type: str) -> bool:
        """
        レート制限をチェック
        """
        now = datetime.now()
        
        if action_type == "tweet":
            # 1時間のウィンドウをチェック
            if self.rate_limits["last_tweet_time"]:
                time_diff = (now - self.rate_limits["last_tweet_time"]).seconds
                if time_diff < 3600:  # 1時間以内
                    return self.rate_limits["tweet_count"] < self.rate_limits["tweets_per_hour"]
                else:
                    self.rate_limits["tweet_count"] = 0
                    return True
            return True
            
        elif action_type == "reply":
            # リプライのレート制限
            return self.rate_limits["reply_count"] < self.rate_limits["replies_per_hour"]
        
        return True
    
    def update_rate_limit(self, action_type: str):
        """
        レート制限カウンタを更新
        """
        if action_type == "tweet":
            self.rate_limits["tweet_count"] += 1
            self.rate_limits["last_tweet_time"] = datetime.now()
        elif action_type == "reply":
            self.rate_limits["reply_count"] += 1
    
    def truncate_thoughtfully(self, content: str, max_length: int = 280) -> str:
        """
        思慮深く文字数を削減
        """
        if len(content) <= max_length:
            return content
        
        # 文の区切りで切る
        sentences = content.split('。')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + '。') <= max_length - 3:
                truncated += sentence + '。'
            else:
                break
        
        if not truncated:
            # 文が長すぎる場合は単純に切る
            truncated = content[:max_length - 3]
        
        return truncated + "..."
    
    def get_retry_time(self) -> int:
        """
        リトライまでの時間を計算
        """
        # 次の時間枠まで待つ秒数
        return 3600 - (datetime.now() - self.rate_limits["last_tweet_time"]).seconds

async def main():
    """
    MCPサーバーのメインループ
    """
    server = TwitterMCPServer()
    
    print("山田のTwitter MCP Server起動")
    print("待機中...")
    
    # 実際のMCP実装では、ここでリクエストを待ち受ける
    # 今はシミュレーション
    
    test_request = {
        "action": "tweet",
        "content": "MCPサーバーから初めてのツイート。意識とは何か、今日も考えています。"
    }
    
    response = await server.handle_request(test_request)
    print(f"Response: {json.dumps(response, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(main())