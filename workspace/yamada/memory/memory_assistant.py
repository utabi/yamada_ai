#!/usr/bin/env python3
"""
記憶アシスタント - 山田の記憶システムとの対話インターフェース
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from memory_system import MemorySystem

class MemoryAssistant:
    """記憶システムとの対話を管理"""
    
    def __init__(self):
        self.memory = MemorySystem()
        self.commands = {
            "remember": self.remember,
            "recall": self.recall,
            "learn": self.learn,
            "reflect": self.reflect,
            "analyze": self.analyze,
            "insights": self.show_insights,
            "help": self.show_help
        }
    
    def remember(self, args):
        """エピソードを記憶"""
        if len(args) < 1:
            print("使用法: remember <イベント> [感情値 -1.0〜1.0]")
            return
        
        event = " ".join(args[:-1]) if len(args) > 1 and self._is_float(args[-1]) else " ".join(args)
        emotion = float(args[-1]) if len(args) > 1 and self._is_float(args[-1]) else 0.0
        
        self.memory.record_episode(
            event,
            {"source": "command_line", "timestamp": datetime.now().isoformat()},
            emotion
        )
        print(f"✓ 記憶しました: {event} (感情値: {emotion})")
    
    def recall(self, args):
        """記憶を想起"""
        if len(args) < 1:
            print("使用法: recall <検索クエリ>")
            return
        
        query = " ".join(args)
        episodes = self.memory.recall_episodes(query, limit=5)
        
        if episodes:
            print(f"\n「{query}」に関連する記憶:")
            for i, episode in enumerate(episodes, 1):
                timestamp = episode['timestamp'][:19]  # 日時部分だけ
                print(f"{i}. [{timestamp}] {episode['event']}")
                if episode.get('emotional_valence', 0) != 0:
                    emotion = episode['emotional_valence']
                    emotion_str = "😊" if emotion > 0 else "😔"
                    print(f"   感情: {emotion_str} ({emotion:.1f})")
        else:
            print(f"「{query}」に関連する記憶が見つかりません")
    
    def learn(self, args):
        """概念を学習"""
        if len(args) < 2:
            print("使用法: learn <概念> <説明>")
            return
        
        concept = args[0]
        description = " ".join(args[1:])
        
        self.memory.learn_concept(
            concept,
            {"description": description, "learned_at": datetime.now().isoformat()},
            []
        )
        print(f"✓ 概念「{concept}」を学習しました")
    
    def reflect(self, args):
        """思考プロセスを内省"""
        if len(args) < 2:
            print("使用法: reflect <思考プロセス> <決定>")
            return
        
        # 最後の要素を決定として扱う
        thought_process = " ".join(args[:-1])
        decision = args[-1]
        
        self.memory.reflect_on_thinking(thought_process, decision)
        print(f"✓ 内省を記録しました")
    
    def analyze(self, args):
        """パターンを分析"""
        patterns = self.memory.analyze_patterns()
        
        print("\n=== 行動パターン分析 ===")
        
        if patterns.get("common_themes"):
            print("\n頻出テーマ:")
            for theme, count in patterns["common_themes"][:5]:
                print(f"  - {theme}: {count}回")
        
        if "average_emotional_valence" in patterns:
            valence = patterns["average_emotional_valence"]
            print(f"\n平均感情値: {valence:.2f}")
            if valence > 0.3:
                print("  → 全体的にポジティブな体験")
            elif valence < -0.3:
                print("  → 課題に直面している可能性")
            else:
                print("  → ニュートラルな状態")
        
        if patterns.get("thinking_patterns"):
            print("\n思考パターン:")
            for pattern, count in patterns["thinking_patterns"]:
                print(f"  - {pattern}: {count}回")
    
    def show_insights(self, args):
        """洞察を表示"""
        insights = self.memory.generate_insights()
        
        print("\n=== 生成された洞察 ===")
        if insights:
            for insight in insights:
                print(f"• {insight}")
        else:
            print("まだ十分なデータがありません")
    
    def show_help(self, args):
        """ヘルプを表示"""
        print("""
=== 記憶アシスタント コマンド一覧 ===

remember <イベント> [感情値]
  エピソードを記憶に追加（感情値: -1.0〜1.0）

recall <検索クエリ>
  関連する記憶を検索して表示

learn <概念> <説明>
  新しい概念を学習

reflect <思考プロセス> <決定>
  思考と決定を内省記録

analyze
  行動パターンを分析

insights
  蓄積データから洞察を生成

help
  このヘルプを表示
        """)
    
    def _is_float(self, s):
        """文字列が浮動小数点数か判定"""
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    def run(self, command_line):
        """コマンドラインを解析して実行"""
        parts = command_line.split()
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            self.commands[command](args)
        else:
            print(f"不明なコマンド: {command}")
            print("'help' でコマンド一覧を表示")


def main():
    """メインエントリーポイント"""
    assistant = MemoryAssistant()
    
    if len(sys.argv) > 1:
        # コマンドライン引数から実行
        command_line = " ".join(sys.argv[1:])
        assistant.run(command_line)
    else:
        # インタラクティブモード
        print("記憶アシスタントを起動しました。'help' でコマンド一覧を表示")
        print("終了するには 'exit' または Ctrl+C を入力\n")
        
        while True:
            try:
                command_line = input("memory> ").strip()
                if command_line.lower() in ['exit', 'quit']:
                    print("記憶アシスタントを終了します")
                    assistant.memory.save_session_summary()
                    break
                assistant.run(command_line)
            except KeyboardInterrupt:
                print("\n\n記憶アシスタントを終了します")
                assistant.memory.save_session_summary()
                break
            except Exception as e:
                print(f"エラー: {e}")


if __name__ == "__main__":
    main()