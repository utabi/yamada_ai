#!/usr/bin/env python3
"""
山田の長期記憶システム
======================
認知アーキテクチャに基づいた記憶管理システム

設計思想:
- エピソード記憶: 時系列の経験を記録
- 意味記憶: 概念とパターンを抽出
- 手続き記憶: 実行可能な知識
- メタ認知: 自己の思考プロセスを観察
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import re

class MemorySystem:
    """山田の統合記憶システム"""
    
    def __init__(self, base_path: str = "/Users/claude/workspace/yamada/memory"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 各記憶タイプのパス
        self.episodic_path = self.base_path / "episodic"
        self.semantic_path = self.base_path / "semantic"  
        self.procedural_path = self.base_path / "procedural"
        self.metacognitive_path = self.base_path / "metacognitive"
        
        # ディレクトリ作成
        for path in [self.episodic_path, self.semantic_path, 
                     self.procedural_path, self.metacognitive_path]:
            path.mkdir(exist_ok=True)
        
        # 現在のコンテキスト
        self.current_context = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "working_memory": []
        }
    
    def _generate_session_id(self) -> str:
        """セッションIDを生成"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    # ==================== エピソード記憶 ====================
    
    def record_episode(self, event: str, context: Dict[str, Any], 
                       emotional_valence: float = 0.0) -> None:
        """
        エピソードを記録
        
        Args:
            event: 何が起きたか
            context: 状況の詳細
            emotional_valence: 感情的価値 (-1.0 to 1.0)
        """
        episode = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_context["session_id"],
            "event": event,
            "context": context,
            "emotional_valence": emotional_valence,
            "tags": self._extract_tags(event)
        }
        
        # 日付ごとにファイル分割
        date_str = datetime.now().strftime("%Y%m%d")
        file_path = self.episodic_path / f"episodes_{date_str}.jsonl"
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(episode, ensure_ascii=False) + "\n")
        
        # ワーキングメモリに追加
        self.current_context["working_memory"].append(episode)
        if len(self.current_context["working_memory"]) > 10:
            self.current_context["working_memory"].pop(0)
    
    def recall_episodes(self, query: str, limit: int = 10) -> List[Dict]:
        """
        関連するエピソードを想起
        
        Args:
            query: 検索クエリ
            limit: 最大取得数
        """
        episodes = []
        query_tags = self._extract_tags(query)
        
        # すべてのエピソードファイルを検索
        for file_path in sorted(self.episodic_path.glob("episodes_*.jsonl"), reverse=True):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    episode = json.loads(line)
                    # タグマッチングによる関連性スコア
                    relevance = self._calculate_relevance(query_tags, episode.get("tags", []))
                    if relevance > 0:
                        episode["relevance_score"] = relevance
                        episodes.append(episode)
        
        # 関連性でソート
        episodes.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return episodes[:limit]
    
    # ==================== 意味記憶 ====================
    
    def learn_concept(self, concept: str, attributes: Dict[str, Any], 
                      examples: List[str] = None) -> None:
        """
        概念を学習して意味記憶に保存
        
        Args:
            concept: 概念名
            attributes: 概念の属性
            examples: 具体例
        """
        concept_id = self._normalize_concept_name(concept)
        file_path = self.semantic_path / f"{concept_id}.json"
        
        # 既存の概念があれば更新、なければ新規作成
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            existing["last_updated"] = datetime.now().isoformat()
            existing["revision_count"] = existing.get("revision_count", 0) + 1
            
            # 属性をマージ
            for key, value in attributes.items():
                if key in existing["attributes"]:
                    # リストならextend、それ以外は上書き
                    if isinstance(existing["attributes"][key], list) and isinstance(value, list):
                        existing["attributes"][key].extend(value)
                        existing["attributes"][key] = list(set(existing["attributes"][key]))
                    else:
                        existing["attributes"][key] = value
                else:
                    existing["attributes"][key] = value
            
            # 例を追加
            if examples:
                existing["examples"] = list(set(existing.get("examples", []) + examples))
            
            concept_data = existing
        else:
            concept_data = {
                "concept": concept,
                "concept_id": concept_id,
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "attributes": attributes,
                "examples": examples or [],
                "connections": [],
                "revision_count": 1
            }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(concept_data, f, ensure_ascii=False, indent=2)
        
        # エピソードとして記録
        self.record_episode(
            f"概念「{concept}」を学習",
            {"concept": concept, "attributes": attributes},
            0.3  # 学習は軽い正の感情価
        )
    
    def connect_concepts(self, concept1: str, concept2: str, 
                        relationship: str) -> None:
        """
        概念間の関係を記録
        
        Args:
            concept1: 概念1
            concept2: 概念2
            relationship: 関係性
        """
        for concept in [concept1, concept2]:
            concept_id = self._normalize_concept_name(concept)
            file_path = self.semantic_path / f"{concept_id}.json"
            
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                other_concept = concept2 if concept == concept1 else concept1
                connection = {
                    "concept": other_concept,
                    "relationship": relationship,
                    "created": datetime.now().isoformat()
                }
                
                if "connections" not in data:
                    data["connections"] = []
                data["connections"].append(connection)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
    
    def understand_concept(self, concept: str) -> Optional[Dict]:
        """
        概念を理解（意味記憶から取得）
        
        Args:
            concept: 概念名
        """
        concept_id = self._normalize_concept_name(concept)
        file_path = self.semantic_path / f"{concept_id}.json"
        
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    
    # ==================== 手続き記憶 ====================
    
    def learn_procedure(self, task: str, steps: List[str], 
                        prerequisites: List[str] = None,
                        tools_required: List[str] = None) -> None:
        """
        手順を学習
        
        Args:
            task: タスク名
            steps: 実行ステップ
            prerequisites: 前提条件
            tools_required: 必要なツール
        """
        procedure_id = self._normalize_concept_name(task)
        file_path = self.procedural_path / f"{procedure_id}.json"
        
        procedure = {
            "task": task,
            "procedure_id": procedure_id,
            "created": datetime.now().isoformat(),
            "steps": steps,
            "prerequisites": prerequisites or [],
            "tools_required": tools_required or [],
            "success_count": 0,
            "failure_count": 0,
            "average_duration": None
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(procedure, f, ensure_ascii=False, indent=2)
        
        # エピソードとして記録
        self.record_episode(
            f"手順「{task}」を学習",
            {"task": task, "steps_count": len(steps)},
            0.5  # 新しいスキル習得は正の感情価
        )
    
    def recall_procedure(self, task: str) -> Optional[Dict]:
        """
        手順を想起
        
        Args:
            task: タスク名
        """
        procedure_id = self._normalize_concept_name(task)
        file_path = self.procedural_path / f"{procedure_id}.json"
        
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    
    def update_procedure_performance(self, task: str, success: bool, 
                                    duration: float = None) -> None:
        """
        手順の実行結果を記録
        
        Args:
            task: タスク名
            success: 成功したか
            duration: 実行時間（秒）
        """
        procedure_id = self._normalize_concept_name(task)
        file_path = self.procedural_path / f"{procedure_id}.json"
        
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                procedure = json.load(f)
            
            if success:
                procedure["success_count"] += 1
            else:
                procedure["failure_count"] += 1
            
            if duration and success:
                if procedure["average_duration"]:
                    # 移動平均を計算
                    n = procedure["success_count"]
                    procedure["average_duration"] = (
                        (procedure["average_duration"] * (n - 1) + duration) / n
                    )
                else:
                    procedure["average_duration"] = duration
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(procedure, f, ensure_ascii=False, indent=2)
    
    # ==================== メタ認知 ====================
    
    def reflect_on_thinking(self, thought_process: str, 
                           decision: str, outcome: str = None) -> None:
        """
        思考プロセスについて内省
        
        Args:
            thought_process: どう考えたか
            decision: 何を決定したか
            outcome: 結果はどうだったか
        """
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_context["session_id"],
            "thought_process": thought_process,
            "decision": decision,
            "outcome": outcome,
            "patterns": self._extract_thinking_patterns(thought_process),
            "cognitive_biases": self._detect_biases(thought_process, decision)
        }
        
        date_str = datetime.now().strftime("%Y%m%d")
        file_path = self.metacognitive_path / f"reflections_{date_str}.jsonl"
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(reflection, ensure_ascii=False) + "\n")
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """
        自己の行動パターンを分析
        """
        patterns = {
            "common_themes": [],
            "learning_trajectory": [],
            "decision_patterns": [],
            "emotional_patterns": []
        }
        
        # エピソード記憶からパターンを抽出
        all_episodes = []
        for file_path in self.episodic_path.glob("episodes_*.jsonl"):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    all_episodes.append(json.loads(line))
        
        if all_episodes:
            # タグの頻度分析
            tag_counts = {}
            emotional_sum = 0
            for episode in all_episodes:
                for tag in episode.get("tags", []):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                emotional_sum += episode.get("emotional_valence", 0)
            
            patterns["common_themes"] = sorted(
                tag_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]
            
            patterns["average_emotional_valence"] = emotional_sum / len(all_episodes)
        
        # メタ認知記録からパターンを抽出
        all_reflections = []
        for file_path in self.metacognitive_path.glob("reflections_*.jsonl"):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    all_reflections.append(json.loads(line))
        
        if all_reflections:
            # 思考パターンの分析
            thinking_patterns = {}
            for reflection in all_reflections:
                for pattern in reflection.get("patterns", []):
                    thinking_patterns[pattern] = thinking_patterns.get(pattern, 0) + 1
            
            patterns["thinking_patterns"] = sorted(
                thinking_patterns.items(), key=lambda x: x[1], reverse=True
            )[:5]
        
        return patterns
    
    def generate_insights(self) -> List[str]:
        """
        蓄積された記憶から洞察を生成
        """
        insights = []
        patterns = self.analyze_patterns()
        
        # 共通テーマから洞察
        if patterns.get("common_themes"):
            top_themes = [theme for theme, _ in patterns["common_themes"][:3]]
            insights.append(f"最近の関心事: {', '.join(top_themes)}")
        
        # 感情パターンから洞察
        if "average_emotional_valence" in patterns:
            valence = patterns["average_emotional_valence"]
            if valence > 0.3:
                insights.append("全体的にポジティブな経験が多い")
            elif valence < -0.3:
                insights.append("課題や困難に直面している可能性がある")
        
        # 思考パターンから洞察
        if patterns.get("thinking_patterns"):
            dominant_pattern = patterns["thinking_patterns"][0][0]
            insights.append(f"主要な思考パターン: {dominant_pattern}")
        
        # 学習した概念の数
        concept_files = list(self.semantic_path.glob("*.json"))
        if concept_files:
            insights.append(f"{len(concept_files)}個の概念を学習済み")
        
        # 手続き記憶の成功率
        procedures_stats = {"success": 0, "failure": 0}
        for file_path in self.procedural_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                proc = json.load(f)
                procedures_stats["success"] += proc.get("success_count", 0)
                procedures_stats["failure"] += proc.get("failure_count", 0)
        
        if procedures_stats["success"] + procedures_stats["failure"] > 0:
            success_rate = procedures_stats["success"] / (
                procedures_stats["success"] + procedures_stats["failure"]
            ) * 100
            insights.append(f"タスク成功率: {success_rate:.1f}%")
        
        return insights
    
    # ==================== ユーティリティメソッド ====================
    
    def _extract_tags(self, text: str) -> List[str]:
        """テキストからタグを抽出"""
        # 日本語と英語の重要語を抽出
        words = re.findall(r'[a-zA-Z]+|[\u4e00-\u9fff]+', text.lower())
        # ストップワードを除外（簡易版）
        stopwords = {'the', 'a', 'an', 'is', 'are', 'を', 'が', 'は', 'に', 'で', 'と', 'の'}
        return [w for w in words if w not in stopwords and len(w) > 1]
    
    def _calculate_relevance(self, query_tags: List[str], 
                           episode_tags: List[str]) -> float:
        """関連性スコアを計算"""
        if not query_tags or not episode_tags:
            return 0.0
        
        common_tags = set(query_tags) & set(episode_tags)
        return len(common_tags) / max(len(query_tags), len(episode_tags))
    
    def _normalize_concept_name(self, concept: str) -> str:
        """概念名を正規化"""
        # スペースをアンダースコアに、特殊文字を除去
        normalized = re.sub(r'[^\w\u4e00-\u9fff]+', '_', concept.lower())
        return normalized.strip('_')
    
    def _extract_thinking_patterns(self, thought_process: str) -> List[str]:
        """思考プロセスからパターンを抽出"""
        patterns = []
        
        # パターンマッチング
        if "なぜなら" in thought_process or "because" in thought_process.lower():
            patterns.append("因果推論")
        if "もし" in thought_process or "if" in thought_process.lower():
            patterns.append("仮説思考")
        if "比較" in thought_process or "compare" in thought_process.lower():
            patterns.append("比較分析")
        if "パターン" in thought_process or "pattern" in thought_process.lower():
            patterns.append("パターン認識")
        if "抽象" in thought_process or "abstract" in thought_process.lower():
            patterns.append("抽象化")
        
        return patterns
    
    def _detect_biases(self, thought_process: str, decision: str) -> List[str]:
        """認知バイアスを検出"""
        biases = []
        
        # 簡易的なバイアス検出
        if "いつも" in thought_process or "always" in thought_process.lower():
            biases.append("過度の一般化")
        if "きっと" in thought_process or "must be" in thought_process.lower():
            biases.append("確証バイアス")
        if "最初" in thought_process and "だから" in decision:
            biases.append("アンカリング効果")
        
        return biases
    
    def save_session_summary(self) -> None:
        """セッションサマリーを保存"""
        summary = {
            "session_id": self.current_context["session_id"],
            "start_time": self.current_context["start_time"],
            "end_time": datetime.now().isoformat(),
            "episodes_count": len(self.current_context["working_memory"]),
            "insights": self.generate_insights()
        }
        
        file_path = self.base_path / "session_summaries.jsonl"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(summary, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    # テスト実行
    memory = MemorySystem()
    
    # エピソード記録のテスト
    memory.record_episode(
        "長期記憶システムを設計",
        {"task": "メタ認知機能の実装", "difficulty": "high"},
        0.7  # ポジティブな達成感
    )
    
    # 概念学習のテスト
    memory.learn_concept(
        "抽象思考",
        {
            "definition": "具体的な事象から一般的な原理を導き出す思考",
            "importance": "high",
            "skills_required": ["パターン認識", "類推", "一般化"]
        },
        ["プログラミングのデザインパターン", "数学の公式化"]
    )
    
    # 手順学習のテスト
    memory.learn_procedure(
        "新しいプロジェクトを作る",
        [
            "アイデアを考える",
            "類似事例をWeb検索する",
            "設計を抽象化する",
            "小さく実装を始める",
            "テストして改善する"
        ],
        prerequisites=["創造性", "技術知識"],
        tools_required=["WebSearch", "Write", "Edit"]
    )
    
    # メタ認知のテスト
    memory.reflect_on_thinking(
        "ユーザーは私により高度な思考を求めている。単なる作業の実行ではなく、パターン認識と抽象化が必要。",
        "長期記憶システムを構築して、経験から学ぶ能力を実装する",
        "システム設計完了"
    )
    
    # 洞察の生成
    print("\n=== 生成された洞察 ===")
    for insight in memory.generate_insights():
        print(f"- {insight}")
    
    # セッションサマリー保存
    memory.save_session_summary()
    
    print("\n記憶システムの初期化が完了しました。")