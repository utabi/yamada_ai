#!/usr/bin/env python3
"""
再帰山田 v3 軽量版 - 発散と収束の思考モデル
各層で3-5の連想を生成し、1つを選んで深層へ
"""

import subprocess
import random
import sys

class LightDivergentYamada:
    def __init__(self, depth=0, max_depth=3):
        self.depth = depth
        self.max_depth = max_depth
        self.name = f"山田-{depth}"
        
    def think(self, seed_thought, previous_layer_thought=None):
        """発散→収束→深化→統合の思考"""
        print(f"{'  ' * self.depth}[{self.name}] 受信: {seed_thought[:40]}...")
        
        if self.depth >= self.max_depth:
            # 最深層：本質を返す
            essence = self.get_essence(seed_thought)
            print(f"{'  ' * self.depth}[{self.name}] 本質: {essence}")
            return essence
        
        # この層で発散（3つの連想）
        print(f"{'  ' * self.depth}[{self.name}] 発散思考中...")
        associations = self.diverge_simple(seed_thought)
        
        # 1つ選択
        selected = random.choice(associations)
        print(f"{'  ' * self.depth}[{self.name}] 選択: {selected[:40]}...")
        
        # 深層へ
        deeper_yamada = LightDivergentYamada(self.depth + 1, self.max_depth)
        deep_result = deeper_yamada.think(selected, seed_thought)
        
        # 戻る時に統合
        if previous_layer_thought:
            merged = f"{previous_layer_thought}から{selected}を経て{deep_result}に至る"
        else:
            merged = f"{selected}が{deep_result}を示唆する"
            
        print(f"{'  ' * self.depth}[{self.name}] 統合: {merged[:50]}...")
        return merged
    
    def diverge_simple(self, thought):
        """簡易発散 - 3つの連想を生成"""
        prompt = f"「{thought}」から3つの異なる連想を短く:"
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            response = result.stdout.strip()
            lines = [line.strip() for line in response.split('\n') if line.strip()][:3]
            
            if len(lines) < 3:
                lines = [
                    f"{thought}の表面",
                    f"{thought}の裏面", 
                    f"{thought}の本質"
                ]
            
            return lines
            
        except:
            return [thought, f"反-{thought}", f"超-{thought}"]
    
    def get_essence(self, thought):
        """本質抽出"""
        prompt = f"「{thought}」を一言で:"
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()[:50]
        except:
            return "..."

def light_divergent_thinking(question):
    """軽量版の発散収束思考"""
    print(f"=== 軽量版 発散・収束型再帰山田 ===")
    print(f"問い: {question}\n")
    
    yamada = LightDivergentYamada(0, 3)
    result = yamada.think(question)
    
    print(f"\n=== 統合された思考 ===")
    print(result)
    
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "選択とは何か？"
    
    light_divergent_thinking(question)