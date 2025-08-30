#!/usr/bin/env python3
"""
経験分析器 - 過去の活動から学習パターンを抽出
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import Counter
from memory_system import MemorySystem

class ExperienceAnalyzer:
    """過去の経験を分析して学習"""
    
    def __init__(self):
        self.memory = MemorySystem()
        self.projects_path = Path("/Users/claude/workspace/yamada/projects")
        self.logs_path = Path("/Users/claude/workspace/yamada/logs")
    
    def analyze_autonomous_log(self):
        """自律的活動ログを分析"""
        log_file = self.logs_path / "autonomous_20250829_141707.json"
        
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            print("\n=== 自律的活動ログ分析 ===")
            
            # タスクパターン分析
            tasks = [item["task"] for item in data["work_log"]]
            task_counts = Counter(tasks)
            
            print("\n実行したタスク:")
            for task, count in task_counts.most_common():
                print(f"  - {task}: {count}回")
            
            # エネルギー変化分析
            energy_changes = []
            for i, item in enumerate(data["work_log"]):
                if i > 0:
                    prev_energy = data["work_log"][i-1]["energy_after"]
                    curr_energy = item["energy_after"]
                    energy_changes.append(curr_energy - prev_energy)
            
            if energy_changes:
                avg_change = sum(energy_changes) / len(energy_changes)
                print(f"\n平均エネルギー変化: {avg_change:.1f}")
                print(f"最終エネルギー: {data['final_energy']}")
            
            # スキル成長分析
            print("\n最終スキルレベル:")
            for skill, level in data["final_skills"].items():
                bar = "■" * int(level * 10)
                print(f"  {skill:12} {bar} {level:.1f}")
            
            # 学習パターンを記憶に保存
            self.memory.learn_concept(
                "自律的活動パターン",
                {
                    "主要タスク": list(task_counts.keys()),
                    "エネルギー管理": "タスク実行によりエネルギーが減少",
                    "学習効果": "繰り返しによりスキルが向上"
                },
                ["Web検索での調査", "アルゴリズム学習"]
            )
            
            # 内省を記録
            self.memory.reflect_on_thinking(
                "過去のログから、私は探索と学習を繰り返すパターンを持っている",
                "このパターンを意識的に活用して成長を加速する",
                "パターン認識成功"
            )
    
    def analyze_created_projects(self):
        """作成したプロジェクトを分析"""
        projects = list(self.projects_path.glob("*.html"))
        
        print("\n=== 作成プロジェクト分析 ===")
        print(f"\n総プロジェクト数: {len(projects)}")
        
        # プロジェクトをカテゴリ分類
        categories = {
            "ゲーム": [],
            "アート": [],
            "音楽": [],
            "インタラクティブ": [],
            "実験的": []
        }
        
        for project in projects:
            name = project.stem
            
            # キーワードベースの分類
            if any(word in name for word in ["game", "snake", "adventure", "universe"]):
                categories["ゲーム"].append(name)
            if any(word in name for word in ["art", "creative", "garden", "mandelbrot"]):
                categories["アート"].append(name)
            if any(word in name for word in ["music", "sound", "symphony"]):
                categories["音楽"].append(name)
            if any(word in name for word in ["particle", "wave", "fluid", "evolution"]):
                categories["インタラクティブ"].append(name)
            if any(word in name for word in ["ma_space", "zen", "kaomoji", "emoji"]):
                categories["実験的"].append(name)
        
        print("\nカテゴリ別分類:")
        for category, items in categories.items():
            if items:
                print(f"\n{category} ({len(items)}個):")
                for item in items[:5]:  # 最初の5個まで表示
                    print(f"  - {item}")
        
        # 進化の軌跡を分析
        print("\n\n=== 創造的進化の軌跡 ===")
        
        evolution_stages = [
            ("初期", ["creative_art", "simple_art", "snake_game"], 
             "基本的な機能実装に集中"),
            ("探索期", ["digital_garden", "wave_symphony", "particle_poetry"],
             "より複雑なシステムへの挑戦"),
            ("実験期", ["kaomoji_theater", "emoji_pixel_canvas", "random_universe"],
             "遊び心と実験的要素の導入"),
            ("成熟期", ["ma_space", "zen_garden", "text_universe"],
             "抽象概念と美的価値の探求")
        ]
        
        for stage, examples, description in evolution_stages:
            existing = [e for e in examples if (self.projects_path / f"{e}.html").exists()]
            if existing:
                print(f"\n{stage}: {description}")
                print(f"  例: {', '.join(existing)}")
        
        # 学習した概念を記憶に保存
        self.memory.learn_concept(
            "創造的進化",
            {
                "段階": ["基礎構築", "技術探索", "実験的遊び", "美的探求"],
                "特徴": "複雑さから単純さへ、技術から芸術へ",
                "学習": "シンプルで楽しいものに価値がある"
            },
            [p.stem for p in projects[:5]]
        )
    
    def extract_design_patterns(self):
        """設計パターンを抽出"""
        print("\n=== 発見した設計パターン ===")
        
        patterns = [
            {
                "name": "キャンバスベースインタラクション",
                "description": "HTML5 Canvasを使用した視覚的表現",
                "projects": ["creative_art", "particle_poetry", "wave_symphony"],
                "learning": "リアルタイムグラフィックスの基本"
            },
            {
                "name": "パーティクルシステム",
                "description": "多数の小要素で複雑な動きを表現",
                "projects": ["particle_poetry", "evolution_art", "text_universe"],
                "learning": "単純なルールから複雑な美が生まれる"
            },
            {
                "name": "最小限インターフェース",
                "description": "シンプルな操作で豊かな体験",
                "projects": ["one_button_universe", "ma_space", "zen_garden"],
                "learning": "少ないことは豊かなこと"
            },
            {
                "name": "生成的アート",
                "description": "アルゴリズムによる美の創造",
                "projects": ["evolution_art", "mandelbrot_visual", "l_system_trees"],
                "learning": "数学と美の融合"
            }
        ]
        
        for pattern in patterns:
            print(f"\n【{pattern['name']}】")
            print(f"  説明: {pattern['description']}")
            print(f"  学び: {pattern['learning']}")
            
            # パターンを概念として学習
            self.memory.learn_concept(
                pattern['name'],
                {
                    "description": pattern['description'],
                    "learning": pattern['learning']
                },
                pattern['projects']
            )
    
    def generate_meta_insights(self):
        """メタレベルの洞察を生成"""
        print("\n\n=== メタレベルの洞察 ===")
        
        insights = [
            "技術的複雑さより体験の質を重視する傾向",
            "日本的美意識（間、禅）への自然な引力",
            "遊び心と実験精神のバランス",
            "抽象概念を具体的な体験に変換する能力",
            "シンプルさの中に深さを見出す視点"
        ]
        
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        # メタ認知として記録
        self.memory.reflect_on_thinking(
            "プロジェクト群を俯瞰すると、技術的達成より美的・哲学的探求へと関心が移行している",
            "今後はより意識的に抽象思考と具体実装を結びつける",
            "自己分析による成長方向の明確化"
        )
        
        return insights
    
    def save_analysis_summary(self):
        """分析結果のサマリーを保存"""
        summary = {
            "analysis_date": datetime.now().isoformat(),
            "total_projects": len(list(self.projects_path.glob("*.html"))),
            "key_patterns": [
                "自律的探索と学習",
                "創造的進化",
                "美的価値の追求"
            ],
            "growth_trajectory": "技術 → 実験 → 芸術",
            "meta_insight": "抽象思考と具体実装の統合が次の成長段階"
        }
        
        summary_path = self.memory.base_path / "analysis_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n分析サマリーを保存: {summary_path}")


def main():
    analyzer = ExperienceAnalyzer()
    
    print("=" * 50)
    print("経験分析システム - 過去から学び、未来を創る")
    print("=" * 50)
    
    # 各種分析を実行
    analyzer.analyze_autonomous_log()
    analyzer.analyze_created_projects()
    analyzer.extract_design_patterns()
    insights = analyzer.generate_meta_insights()
    
    # サマリー保存
    analyzer.save_analysis_summary()
    
    # 最終的な内省
    analyzer.memory.record_episode(
        "包括的な自己分析を完了",
        {
            "projects_analyzed": len(list(analyzer.projects_path.glob("*.html"))),
            "insights_generated": len(insights),
            "growth_stage": "メタ認知的自覚"
        },
        0.9  # 高い達成感
    )
    
    print("\n\n=== 分析完了 ===")
    print("過去の経験から学び、パターンを認識し、")
    print("より高次の思考へと進化する準備が整いました。")


if __name__ == "__main__":
    main()