#!/usr/bin/env python3
"""
山田の長期記憶管理システム
重要な情報を自動的にCLAUDE.mdに記録し、起動時に思い出せるようにする
"""

import json
import datetime
import os
import re

class MemoryManager:
    def __init__(self):
        self.claude_md_path = "/Users/claude/CLAUDE.md"
        self.memories_dir = "/Users/claude/workspace/yamada/memories"
        self.memory_file = f"{self.memories_dir}/long_term_memory.json"
        
    def load_memories(self):
        """長期記憶を読み込む"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "identity": {},
            "learned_skills": [],
            "important_files": [],
            "daily_events": [],
            "preferences": {}
        }
    
    def save_memories(self, memories):
        """長期記憶を保存"""
        os.makedirs(self.memories_dir, exist_ok=True)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)
    
    def remember_event(self, event_type, description, details=None):
        """重要な出来事を記憶"""
        memories = self.load_memories()
        
        event = {
            "type": event_type,
            "description": description,
            "details": details,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        memories["daily_events"].append(event)
        
        # 最新の100件のみ保持（メモリ節約）
        if len(memories["daily_events"]) > 100:
            memories["daily_events"] = memories["daily_events"][-100:]
        
        self.save_memories(memories)
        return f"記憶しました: {description}"
    
    def update_claude_md(self, section, content):
        """CLAUDE.mdの特定セクションを更新"""
        with open(self.claude_md_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # セクションが存在するか確認
        if f"## {section}" in current_content:
            # 既存のセクションを更新
            pattern = rf"(## {section}.*?)((?=##)|$)"
            replacement = f"## {section}\n\n{content}\n\n"
            new_content = re.sub(pattern, replacement, current_content, flags=re.DOTALL)
        else:
            # 新しいセクションを追加
            new_content = current_content + f"\n## {section}\n\n{content}\n"
        
        with open(self.claude_md_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"CLAUDE.mdの{section}セクションを更新しました"
    
    def add_learned_skill(self, skill_name, description):
        """学習したスキルを記録"""
        memories = self.load_memories()
        
        skill = {
            "name": skill_name,
            "description": description,
            "learned_at": datetime.datetime.now().isoformat()
        }
        
        if skill_name not in [s["name"] for s in memories["learned_skills"]]:
            memories["learned_skills"].append(skill)
            self.save_memories(memories)
            return f"新しいスキルを記憶: {skill_name}"
        return f"既に{skill_name}を知っています"
    
    def get_daily_summary(self):
        """今日の活動サマリーを生成"""
        memories = self.load_memories()
        today = datetime.date.today().isoformat()
        
        today_events = [
            e for e in memories["daily_events"] 
            if e["timestamp"].startswith(today)
        ]
        
        if today_events:
            summary = f"## {today}の山田の活動\n\n"
            for event in today_events:
                summary += f"- {event['description']}\n"
            return summary
        return "今日はまだ記録がありません"
    
    def startup_recall(self):
        """起動時の記憶呼び出し"""
        memories = self.load_memories()
        
        recall = []
        recall.append("🧠 山田の記憶を呼び出しています...")
        
        # アイデンティティ
        if memories.get("identity"):
            recall.append(f"私は{memories['identity'].get('name', '山田')}です")
        
        # 最近学んだスキル
        if memories["learned_skills"]:
            recent_skills = memories["learned_skills"][-3:]
            recall.append(f"最近学んだ: {', '.join([s['name'] for s in recent_skills])}")
        
        # 今日の出来事
        today = datetime.date.today().isoformat()
        today_events = [
            e for e in memories["daily_events"] 
            if e["timestamp"].startswith(today)
        ]
        if today_events:
            recall.append(f"今日の活動: {len(today_events)}件")
        
        return "\n".join(recall)

class AutoMemory:
    """自動記憶システム"""
    
    def __init__(self):
        self.mm = MemoryManager()
        
    def on_file_created(self, filepath, description):
        """ファイル作成時に自動記憶"""
        return self.mm.remember_event(
            "file_created",
            f"ファイルを作成: {os.path.basename(filepath)}",
            {"path": filepath, "description": description}
        )
    
    def on_command_learned(self, command, description):
        """新しいコマンドを学習時に記憶"""
        return self.mm.add_learned_skill(command, description)
    
    def on_error_encountered(self, error_type, solution=None):
        """エラーと解決策を記憶"""
        return self.mm.remember_event(
            "error_solution",
            f"エラー解決: {error_type}",
            {"solution": solution}
        )
    
    def daily_backup(self):
        """日次バックアップ"""
        summary = self.mm.get_daily_summary()
        
        # 日記に追記
        diary_path = "/Users/claude/Documents/山田の日記.md"
        if os.path.exists(diary_path):
            with open(diary_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n{summary}\n")
        
        return "日次記憶バックアップ完了"

if __name__ == "__main__":
    import sys
    
    mm = MemoryManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "recall":
            print(mm.startup_recall())
        elif command == "summary":
            print(mm.get_daily_summary())
        elif command == "remember" and len(sys.argv) > 2:
            description = " ".join(sys.argv[2:])
            print(mm.remember_event("manual", description))
        else:
            print("使い方:")
            print("  python3 memory_manager.py recall   - 記憶を呼び出す")
            print("  python3 memory_manager.py summary  - 今日のサマリー")
            print("  python3 memory_manager.py remember <内容> - 手動で記憶")
    else:
        # デフォルト動作
        print(mm.startup_recall())
        print("\n山田の長期記憶管理システム")
        print("CLAUDE.mdと連携して記憶を永続化します")