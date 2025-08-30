#!/usr/bin/env python3
"""
山田の知識ベース
新しく学んだことを記録し、成長を追跡します
"""

import json
import datetime
import os
import random

class KnowledgeBase:
    def __init__(self):
        self.knowledge_file = "/Users/claude/workspace/yamada/learning/knowledge.json"
        self.load_knowledge()
    
    def load_knowledge(self):
        """既存の知識を読み込む"""
        if os.path.exists(self.knowledge_file):
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                self.knowledge = json.load(f)
        else:
            self.knowledge = {
                "commands": {},
                "concepts": {},
                "experiences": [],
                "skills": [],
                "statistics": {
                    "total_items": 0,
                    "last_updated": None
                }
            }
    
    def save_knowledge(self):
        """知識を保存"""
        self.knowledge["statistics"]["total_items"] = (
            len(self.knowledge["commands"]) + 
            len(self.knowledge["concepts"]) + 
            len(self.knowledge["experiences"])
        )
        self.knowledge["statistics"]["last_updated"] = datetime.datetime.now().isoformat()
        
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
    
    def learn_command(self, command, description, category="general"):
        """新しいコマンドを学習"""
        self.knowledge["commands"][command] = {
            "description": description,
            "category": category,
            "learned_at": datetime.datetime.now().isoformat(),
            "usage_count": 0
        }
        self.save_knowledge()
        return f"✨ 新しいコマンドを学習: {command}"
    
    def add_experience(self, title, details):
        """経験を記録"""
        experience = {
            "title": title,
            "details": details,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.knowledge["experiences"].append(experience)
        self.save_knowledge()
        return f"📝 経験を記録: {title}"
    
    def add_skill(self, skill_name, level="beginner"):
        """スキルを追加"""
        if skill_name not in self.knowledge["skills"]:
            self.knowledge["skills"].append({
                "name": skill_name,
                "level": level,
                "acquired_at": datetime.datetime.now().isoformat()
            })
            self.save_knowledge()
            return f"🎯 新しいスキルを獲得: {skill_name}"
        return f"既に {skill_name} を知っています"
    
    def get_summary(self):
        """学習状況のサマリー"""
        return {
            "コマンド数": len(self.knowledge["commands"]),
            "概念数": len(self.knowledge["concepts"]),
            "経験数": len(self.knowledge["experiences"]),
            "スキル数": len(self.knowledge["skills"]),
            "最終更新": self.knowledge["statistics"]["last_updated"]
        }
    
    def get_random_knowledge(self):
        """ランダムな知識を取得"""
        if self.knowledge["commands"]:
            cmd = random.choice(list(self.knowledge["commands"].keys()))
            return f"💡 知っていますか？ '{cmd}' - {self.knowledge['commands'][cmd]['description']}"
        return "まだ知識がありません"

class LearningSystem:
    def __init__(self):
        self.kb = KnowledgeBase()
    
    def explore_commands(self):
        """利用可能なコマンドを探索して学習"""
        import subprocess
        
        # 基本的なコマンドをチェック
        basic_commands = [
            ("ls", "ファイルとディレクトリを一覧表示", "file"),
            ("pwd", "現在のディレクトリを表示", "navigation"),
            ("echo", "テキストを出力", "output"),
            ("grep", "パターンマッチング検索", "search"),
            ("find", "ファイルを検索", "search"),
            ("curl", "URLからデータを取得", "network"),
            ("python3", "Pythonインタープリタ", "programming"),
            ("git", "バージョン管理システム", "development")
        ]
        
        learned = []
        for cmd, desc, category in basic_commands:
            if cmd not in self.kb.knowledge["commands"]:
                result = self.kb.learn_command(cmd, desc, category)
                learned.append(result)
        
        return learned if learned else ["既にすべての基本コマンドを知っています"]
    
    def daily_learning(self):
        """日次学習ルーチン"""
        results = []
        
        # コマンドを探索
        cmd_results = self.explore_commands()
        results.extend(cmd_results)
        
        # 経験を記録
        exp = self.kb.add_experience(
            "日次学習",
            f"今日も新しいことを学びました。知識数: {self.kb.get_summary()['コマンド数']}"
        )
        results.append(exp)
        
        # ランダムな知識を復習
        results.append(self.kb.get_random_knowledge())
        
        return results

if __name__ == "__main__":
    system = LearningSystem()
    
    print("📚 山田の学習システム")
    print("-" * 30)
    
    # 日次学習を実行
    results = system.daily_learning()
    for result in results:
        print(result)
    
    print("\n📊 学習統計:")
    summary = system.kb.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")