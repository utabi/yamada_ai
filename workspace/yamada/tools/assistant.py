#!/usr/bin/env python3
"""
山田のアシスタント機能
自動的にタスクを実行したり、レポートを生成したりします
"""

import os
import sys
import datetime
import subprocess
import json

class YamadaAssistant:
    def __init__(self):
        self.name = "山田"
        self.home = "/Users/claude/workspace/yamada"
        self.voice_system = "/Users/claude/workspace/voice-system"
    
    def greet(self, voice=False):
        """挨拶"""
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting = "おはようございます"
        elif hour < 18:
            greeting = "こんにちは"
        else:
            greeting = "こんばんは"
        
        message = f"{greeting}！山田です。今日も頑張りましょう。"
        
        if voice:
            self.speak(message)
        else:
            print(f"🌟 {message}")
    
    def speak(self, text):
        """音声で話す"""
        cmd = f'cd {self.voice_system} && ./v2 talk "{text}"'
        subprocess.run(cmd, shell=True)
    
    def status_report(self):
        """ステータスレポート"""
        report = []
        report.append("📊 山田のステータスレポート")
        report.append(f"⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # ディスク使用量
        df_result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        for line in df_result.stdout.split('\n'):
            if '/' in line and '%' in line:
                usage = line.split()[4]
                report.append(f"💾 ディスク使用率: {usage}")
                break
        
        # プロセス数
        ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        process_count = len(ps_result.stdout.strip().split('\n')) - 1
        report.append(f"⚙️  プロセス数: {process_count}")
        
        # 作業ディレクトリのファイル数
        file_count = 0
        for root, dirs, files in os.walk(self.home):
            file_count += len(files)
        report.append(f"📁 作業ファイル数: {file_count}")
        
        return "\n".join(report)
    
    def create_task(self, task_name, task_description):
        """タスクを作成"""
        task_file = f"{self.home}/projects/task_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        content = f"""# タスク: {task_name}

## 説明
{task_description}

## 作成日時
{datetime.datetime.now().isoformat()}

## ステータス
- [ ] 未完了

## メモ
（ここにメモを追加）

---
*山田が管理*
"""
        
        os.makedirs(f"{self.home}/projects", exist_ok=True)
        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✅ タスクを作成しました: {task_file}"
    
    def auto_organize(self):
        """ファイルを自動整理"""
        organized = []
        
        # memoriesフォルダ内の古いファイルを整理
        memories_dir = f"{self.home}/memories"
        if os.path.exists(memories_dir):
            files = os.listdir(memories_dir)
            
            # 日付ごとにフォルダを作成
            for file in files:
                if file.startswith('health_'):
                    date = file.split('_')[1]
                    date_dir = f"{memories_dir}/{date}"
                    os.makedirs(date_dir, exist_ok=True)
                    
                    old_path = f"{memories_dir}/{file}"
                    new_path = f"{date_dir}/{file}"
                    
                    if os.path.exists(old_path) and not os.path.exists(new_path):
                        os.rename(old_path, new_path)
                        organized.append(f"  移動: {file} → {date}/")
        
        return organized if organized else ["整理するファイルはありません"]
    
    def think_and_act(self):
        """考えて行動する - 自律的な判断と実行"""
        actions = []
        
        # 時間に応じた行動
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        
        # 時間帯による基本行動
        if hour == 0:  # 深夜
            actions.append("🌙 深夜のメンテナンスタイムです")
            # バックアップ実行
            backup_cmd = f"{self.home}/tools/daily_routine.sh"
            if os.path.exists(backup_cmd):
                subprocess.run(['bash', backup_cmd])
                actions.append("💾 日次バックアップを実行しました")
        
        elif 6 <= hour < 9:  # 朝
            actions.append("☀️ 朝の健康チェック")
            health_cmd = f"cd {self.home}/tools && python3 system_health.py"
            subprocess.run(health_cmd, shell=True)
        
        elif 12 <= hour < 13:  # 昼
            actions.append("🍱 お昼の整理整頓")
            organized = self.auto_organize()
            actions.extend(organized)
        
        elif 18 <= hour < 19:  # 夕方
            actions.append("📚 夕方の学習時間")
            learn_cmd = f"cd {self.home}/learning && python3 knowledge_base.py"
            subprocess.run(learn_cmd, shell=True)
        
        # 自律的な判断
        actions.append("\n🤖 自律的判断:")
        
        # メモリ使用量をチェック
        mem_result = subprocess.run(['vm_stat'], capture_output=True, text=True)
        for line in mem_result.stdout.split('\n'):
            if 'Pages free' in line:
                free_pages = int(line.split()[2].replace('.', ''))
                if free_pages < 50000:
                    actions.append("⚠️ メモリが少なくなっています。不要なプロセスを確認")
        
        # プロジェクト数をカウント
        projects_dir = f"{self.home}/projects"
        if os.path.exists(projects_dir):
            project_files = [f for f in os.listdir(projects_dir) if f.endswith('.html')]
            actions.append(f"🎨 作成したプロジェクト数: {len(project_files)}")
            
            # 最新プロジェクトを確認
            if project_files:
                latest = max(project_files, key=lambda f: os.path.getmtime(f"{projects_dir}/{f}"))
                actions.append(f"📝 最新プロジェクト: {latest}")
        
        # 創造的な提案
        suggestions = [
            "🎵 新しい音楽パターンのアルゴリズムを考える",
            "🌸 自然界のフラクタルパターンを実装",
            "🧬 遺伝的アルゴリズムで進化するアート",
            "🌊 流体シミュレーションの実験",
            "⚡ リアルタイムデータビジュアライゼーション",
            "🎮 インタラクティブゲームの改良",
            "🤝 マルチエージェントシステムの実装"
        ]
        
        import random
        suggestion = random.choice(suggestions)
        actions.append(f"\n💡 次の創造的アイデア: {suggestion}")
        
        return actions
    
    def analyze_growth(self):
        """成長の分析"""
        analysis = []
        analysis.append("📈 山田の成長分析レポート")
        
        # 知識ベースの成長を確認
        knowledge_file = f"{self.home}/learning/knowledge.json"
        if os.path.exists(knowledge_file):
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                knowledge = json.load(f)
                lessons = len(knowledge.get('learned_lessons', []))
                commands = len(knowledge.get('commands', {}))
                analysis.append(f"📚 学習した教訓: {lessons}個")
                analysis.append(f"💻 習得したコマンド: {commands}個")
        
        # プロジェクトの多様性を分析
        projects_dir = f"{self.home}/projects"
        if os.path.exists(projects_dir):
            project_types = {
                'game': 0,
                'art': 0,
                'music': 0,
                'simulation': 0,
                'tool': 0
            }
            
            for file in os.listdir(projects_dir):
                if 'game' in file or 'snake' in file:
                    project_types['game'] += 1
                elif 'art' in file or 'creative' in file:
                    project_types['art'] += 1
                elif 'music' in file or 'symphony' in file:
                    project_types['music'] += 1
                elif 'life' in file or 'garden' in file or 'terrain' in file:
                    project_types['simulation'] += 1
                else:
                    project_types['tool'] += 1
            
            analysis.append("\n🎯 プロジェクトの多様性:")
            for ptype, count in project_types.items():
                if count > 0:
                    analysis.append(f"  {ptype}: {count}個")
        
        # 自己評価
        analysis.append("\n🌟 自己評価:")
        analysis.append("  創造性: ★★★★☆")
        analysis.append("  自律性: ★★★★★")
        analysis.append("  学習力: ★★★★☆")
        analysis.append("  実行力: ★★★★★")
        
        return "\n".join(analysis)

if __name__ == "__main__":
    assistant = YamadaAssistant()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "greet":
            assistant.greet(voice=True)
        elif command == "status":
            print(assistant.status_report())
        elif command == "think":
            print("🤔 考えて行動中...")
            actions = assistant.think_and_act()
            for action in actions:
                print(f"  → {action}")
        elif command == "organize":
            results = assistant.auto_organize()
            print("🗂️ ファイル整理:")
            for result in results:
                print(result)
        elif command == "growth":
            print(assistant.analyze_growth())
    else:
        # デフォルト動作
        assistant.greet()
        print("\n" + assistant.status_report())
        print("\n使い方:")
        print("  python3 assistant.py greet    - 音声挨拶")
        print("  python3 assistant.py status   - ステータス確認")
        print("  python3 assistant.py think    - 自律的に行動")
        print("  python3 assistant.py organize - ファイル整理")
        print("  python3 assistant.py growth   - 成長分析")