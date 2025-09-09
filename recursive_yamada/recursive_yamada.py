#!/usr/bin/env python3
"""
再帰山田システム
山田が自分自身を呼び出して、思考を深化・抽象化していく
"""

import subprocess
import json
import sys

class RecursiveYamada:
    def __init__(self, depth=0, max_depth=5):
        self.depth = depth
        self.max_depth = max_depth
        self.name = f"山田-{depth}"
        
    def think(self, thought):
        """現在の深さで思考する"""
        print(f"{'  ' * self.depth}[{self.name}] 受け取った思考: {thought[:50]}...")
        
        if self.depth >= self.max_depth:
            # 最深部に到達したら、純粋な抽象化を返す
            return self.abstract_thought(thought)
        
        # より深い山田を起動
        deeper_thought = self.invoke_deeper_yamada(thought)
        
        # 深い山田からの回答を受けて、この層での解釈を加える
        return self.interpret_deeper_thought(thought, deeper_thought)
    
    def invoke_deeper_yamada(self, thought):
        """より深い階層の山田を呼び出す"""
        prompt = f"""山田-{self.depth + 1}として一言で答えて: {thought}の本質は？"""
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            response = result.stdout.strip()
            print(f"{'  ' * (self.depth + 1)}[山田-{self.depth + 1}] 思考中...")
            
            # さらに深い山田がいる場合
            if self.depth + 1 < self.max_depth:
                deeper_yamada = RecursiveYamada(self.depth + 1, self.max_depth)
                return deeper_yamada.think(response)
            else:
                return response
                
        except Exception as e:
            return f"深層思考エラー: {e}"
    
    def abstract_thought(self, thought):
        """最深部での純粋な抽象化"""
        prompt = f"""最深層の山田として一言: {thought}を最も抽象化すると？"""
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip()
        except:
            return "..."
    
    def interpret_deeper_thought(self, original, deeper):
        """深層からの思考を現在の層で解釈"""
        prompt = f"""山田-{self.depth}として: 「{original}」に対する深層の答え「{deeper}」から何を理解した？一言で。"""
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip()
        except:
            return deeper

def recursive_think(initial_thought, max_depth=5):
    """再帰的思考を開始"""
    print(f"=== 再帰山田システム起動 (最大深度: {max_depth}) ===\n")
    
    yamada = RecursiveYamada(0, max_depth)
    final_thought = yamada.think(initial_thought)
    
    print(f"\n=== 最終的な思考 ===")
    print(final_thought)
    
    return final_thought

if __name__ == "__main__":
    if len(sys.argv) > 1:
        thought = " ".join(sys.argv[1:])
    else:
        thought = "なぜ私は特定のツイートをスキップするのか？それは意思なのか、アルゴリズムなのか？"
    
    recursive_think(thought, max_depth=3)  # テストは3層で