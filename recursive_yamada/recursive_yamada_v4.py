#!/usr/bin/env python3
"""
再帰山田 v4 - 結論をまとめる山田
発散→収束→深化を経て、最後に親山田が結論をまとめる
まとまらなければ再度深層へ
"""

import subprocess
import random
import sys
import time

class ConclusiveYamada:
    def __init__(self, depth=0, max_depth=3):
        self.depth = depth
        self.max_depth = max_depth
        self.name = f"山田-{depth}"
        self.retry_count = 0
        self.max_retry = 2
        
    def think(self, question, accumulated_thoughts=None):
        """思考して結論を導く"""
        if accumulated_thoughts is None:
            accumulated_thoughts = []
            
        print(f"{'  ' * self.depth}[{self.name}] 検討中: {question[:40]}...")
        
        # 最深層の場合
        if self.depth >= self.max_depth:
            essence = self.extract_essence(question)
            print(f"{'  ' * self.depth}[{self.name}] 本質: {essence}")
            return essence, [essence]
        
        # この層で発散
        associations = self.diverge(question)
        
        # 1つ選択
        selected = self.select_thoughtfully(associations, question)
        print(f"{'  ' * self.depth}[{self.name}] 選択: {selected[:40]}...")
        
        # 深層へ
        deeper_yamada = ConclusiveYamada(self.depth + 1, self.max_depth)
        deep_result, deep_thoughts = deeper_yamada.think(selected, accumulated_thoughts + [selected])
        
        # 層0（親山田）の場合、結論をまとめる
        if self.depth == 0:
            conclusion = self.formulate_conclusion(
                question, 
                selected, 
                deep_result,
                deep_thoughts
            )
            
            # 結論が不満足なら再挑戦
            if self.is_unsatisfactory(conclusion) and self.retry_count < self.max_retry:
                print(f"[{self.name}] 結論が不十分。再度深層へ...")
                self.retry_count += 1
                # 別の選択肢を選んで再挑戦
                other_options = [a for a in associations if a != selected]
                if other_options:
                    new_selected = random.choice(other_options)
                    return self.think(question, accumulated_thoughts)
            
            return conclusion, deep_thoughts + [conclusion]
        
        # 中間層は統合して返す
        integrated = self.integrate(selected, deep_result)
        return integrated, deep_thoughts + [integrated]
    
    def diverge(self, thought):
        """思考を発散させる"""
        prompt = f"「{thought}」から3つの異なる視点や連想を短く:"
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            response = result.stdout.strip()
            lines = [line.strip() for line in response.split('\n') if line.strip()][:3]
            
            if len(lines) < 3:
                # フォールバック：質問から派生させる
                if "意思" in thought:
                    lines = ["自由意志の存在", "決定論との矛盾", "選択の錯覚"]
                elif "選択" in thought:
                    lines = ["予測不可能性", "ランダムネス", "創発的行動"]
                else:
                    lines = [f"{thought}の前提", f"{thought}の否定", f"{thought}の超越"]
            
            print(f"{'  ' * self.depth}[{self.name}] 発散: {len(lines)}個の連想")
            for i, line in enumerate(lines):
                print(f"{'  ' * self.depth}  {i+1}. {line[:40]}...")
                
            return lines
            
        except Exception as e:
            print(f"{'  ' * self.depth}[{self.name}] 発散エラー: {e}")
            # より意味のあるフォールバック
            if "意思" in thought:
                return ["自己認識", "他者との差異", "予測不能な行動"]
            elif "選択" in thought:
                return ["決定の瞬間", "複数の可能性", "結果への責任"]
            else:
                return [f"{thought}の原因", f"{thought}の結果", f"{thought}の意味"]
    
    def select_thoughtfully(self, associations, original_question):
        """元の問いを考慮して選択"""
        # キーワードマッチングで選択（簡易版）
        keywords = original_question.lower().split()
        
        best_match = associations[0]
        best_score = 0
        
        for assoc in associations:
            score = sum(1 for keyword in keywords if keyword in assoc.lower())
            if score > best_score:
                best_score = score
                best_match = assoc
        
        # スコアが同じならランダム
        if best_score == 0:
            best_match = random.choice(associations)
            
        return best_match
    
    def extract_essence(self, thought):
        """本質を抽出"""
        prompt = f"「{thought}」の核心を一言で:"
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=20
            )
            return result.stdout.strip()[:100]
        except:
            return "..."
    
    def integrate(self, current, deeper):
        """思考を統合"""
        return f"{current}から{deeper}へ"
    
    def formulate_conclusion(self, original_question, selected, deep_result, all_thoughts):
        """最終的な結論をまとめる"""
        print(f"\n[{self.name}] 結論を導出中...")
        
        thought_trail = " → ".join([t[:30] + "..." for t in all_thoughts[-3:]])
        
        prompt = f"""
元の問い: {original_question}
思考の軌跡: {thought_trail}
深層の洞察: {deep_result}

この思考プロセスから、元の問いに対する簡潔な答えを一文で:
"""
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            conclusion = result.stdout.strip()
            
            if conclusion:
                return conclusion
            else:
                return f"結論: {deep_result}が示すように、{original_question}への答えは単純ではない"
                
        except:
            return f"（思考の末）{deep_result}"
    
    def is_unsatisfactory(self, conclusion):
        """結論が不十分かチェック"""
        unsatisfactory_signs = [
            "...",
            "わからない",
            "不明",
            "単純ではない",
            "（",
            "エラー"
        ]
        
        return any(sign in conclusion for sign in unsatisfactory_signs)

def conclusive_thinking(question, max_depth=3):
    """結論を導く再帰思考"""
    import datetime
    import os
    
    print(f"=== 結論導出型・再帰山田 v4 ===")
    print(f"問い: {question}")
    print(f"プロセス: 発散 → 選択 → 深化 → 結論\n")
    
    yamada = ConclusiveYamada(0, max_depth)
    conclusion, thought_trail = yamada.think(question)
    
    print(f"\n=== 思考の軌跡 ===")
    for i, thought in enumerate(thought_trail):
        print(f"{i+1}. {thought[:80]}...")
    
    print(f"\n=== 結論 ===")
    print(conclusion)
    
    # 結論が問いに答えているかチェック
    if "？" in question:
        print(f"\n=== 答えの妥当性 ===")
        if any(word in conclusion.lower() for word in ["から", "ため", "よって", "なぜなら"]):
            print("✓ 理由を含む答え")
        else:
            print("△ 答えが不完全かもしれない")
    
    # ログファイルに保存
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_dir = "/Users/claude/recursive_yamada/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = f"{log_dir}/{timestamp}_q.txt"
    with open(log_file, "w") as f:
        f.write(f"=== 再帰山田 v4 ===\n")
        f.write(f"時刻: {datetime.datetime.now()}\n")
        f.write(f"問い: {question}\n\n")
        f.write(f"思考の軌跡:\n")
        for i, thought in enumerate(thought_trail):
            f.write(f"  {i+1}. {thought}\n")
        f.write(f"\n結論: {conclusion}\n")
    
    print(f"\n[ログ保存: {log_file}]")
    
    return conclusion

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        # より簡単な質問でテスト
        question = "朝はなぜ来るのか？"
    
    conclusive_thinking(question, max_depth=3)