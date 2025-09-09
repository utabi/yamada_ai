#!/usr/bin/env python3
"""
再帰山田 v3 - 発散と収束の思考モデル
各層で10の連想を生成し、1つを選んで深層へ
帰路では各層の思考を混合していく
"""

import subprocess
import random
import json
import sys
import time

class DivergentYamada:
    def __init__(self, depth=0, max_depth=5):
        self.depth = depth
        self.max_depth = max_depth
        self.name = f"山田-{depth}"
        self.thoughts = []  # この層での思考群
        self.selected_thought = None  # 選ばれた思考
        
    def diverge(self, seed_thought):
        """思考を発散させる - 1つの思考から10の連想を生成"""
        print(f"{'  ' * self.depth}[{self.name}] 思考を発散中...")
        
        prompt = f"""
以下の思考から、10個の異なる連想や解釈を生成してください。
論理的でも非論理的でも構いません。

元の思考: {seed_thought}

10個の連想を箇条書きで:
"""
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            response = result.stdout.strip()
            # 行ごとに分割して連想リストを作成
            associations = [line.strip() for line in response.split('\n') 
                          if line.strip() and not line.strip().startswith('#')][:10]
            
            # 連想が足りない場合は補完
            while len(associations) < 10:
                associations.append(f"連想{len(associations)+1}: {seed_thought}の変形")
            
            self.thoughts = associations
            print(f"{'  ' * self.depth}[{self.name}] {len(associations)}個の連想を生成")
            
            # デバッグ用：いくつかの連想を表示
            for i, thought in enumerate(associations[:3]):
                print(f"{'  ' * self.depth}  {i+1}. {thought[:50]}...")
            print(f"{'  ' * self.depth}  ...")
            
            return associations
            
        except Exception as e:
            print(f"{'  ' * self.depth}[{self.name}] 発散エラー: {e}")
            # エラー時は単純な連想を生成
            self.thoughts = [f"{seed_thought}の側面{i}" for i in range(10)]
            return self.thoughts
    
    def converge(self):
        """思考を収束させる - 10の中から1つを選択"""
        if not self.thoughts:
            return None
            
        # 選択の基準をランダムに決める
        selection_methods = [
            ("ランダム", lambda: random.choice(self.thoughts)),
            ("最短", lambda: min(self.thoughts, key=len)),
            ("最長", lambda: max(self.thoughts, key=len)),
            ("中間", lambda: self.thoughts[len(self.thoughts)//2]),
        ]
        
        method_name, method = random.choice(selection_methods)
        self.selected_thought = method()
        
        print(f"{'  ' * self.depth}[{self.name}] {method_name}選択: {self.selected_thought[:50]}...")
        return self.selected_thought
    
    def dive_deeper(self, thought):
        """より深い層へ潜る"""
        if self.depth >= self.max_depth:
            # 最深層では純粋な本質を返す
            return self.extract_essence(thought)
        
        # 深い層の山田を作成
        deeper_yamada = DivergentYamada(self.depth + 1, self.max_depth)
        
        # 深い層で発散→収束
        deeper_yamada.diverge(thought)
        selected = deeper_yamada.converge()
        
        if selected:
            # さらに深く潜る
            deep_result = deeper_yamada.dive_deeper(selected)
            # 深層の結果とこの層の選択を混合
            return self.merge_thoughts(selected, deep_result)
        
        return thought
    
    def extract_essence(self, thought):
        """最深層での本質抽出"""
        print(f"{'  ' * self.depth}[{self.name}] 最深層で本質を抽出...")
        
        prompt = f"「{thought}」の最も純粋な本質を一言で:"
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=15
            )
            essence = result.stdout.strip()
            print(f"{'  ' * self.depth}[{self.name}] 本質: {essence}")
            return essence
        except:
            return "..."
    
    def merge_thoughts(self, thought1, thought2):
        """2つの思考を混合"""
        print(f"{'  ' * self.depth}[{self.name}] 思考を統合中...")
        
        prompt = f"""
以下の2つの思考を創造的に統合してください：
思考1: {thought1}
思考2: {thought2}

統合された新しい理解を一文で:
"""
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=15
            )
            merged = result.stdout.strip()
            print(f"{'  ' * self.depth}[{self.name}] 統合: {merged[:50]}...")
            return merged
        except:
            return f"{thought1} そして {thought2}"

def divergent_recursive_thinking(question, max_depth=5):
    """発散・収束型の再帰思考"""
    print(f"=== 発散・収束型再帰山田 v3 ===")
    print(f"問い: {question}")
    print(f"最大深度: {max_depth}")
    print(f"プロセス: 発散(1→10) → 収束(10→1) → 深化 → 統合\n")
    
    # ルート山田を作成
    yamada = DivergentYamada(0, max_depth)
    
    # 初期思考を発散
    yamada.diverge(question)
    
    # 収束して1つ選択
    selected = yamada.converge()
    
    if selected:
        # 深層へ潜って、統合しながら戻る
        final_thought = yamada.dive_deeper(selected)
        
        print(f"\n=== 統合された最終思考 ===")
        print(final_thought)
        
        # 選ばれなかった思考も記録
        print(f"\n=== 第一層で生成されたが選ばれなかった思考 ===")
        for i, thought in enumerate(yamada.thoughts):
            if thought != selected:
                print(f"{i+1}. {thought[:60]}...")
        
        return final_thought
    
    return "思考の発散に失敗"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "意思とは何か？"
    
    # デフォルトは3層（テスト用）
    divergent_recursive_thinking(question, max_depth=3)