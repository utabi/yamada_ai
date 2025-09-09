#!/usr/bin/env python3
"""
再帰山田 v2 - より人間的な思考を目指す
"""

import subprocess
import random
import json
import sys
import time

class HumanLikeYamada:
    def __init__(self, depth=0, max_depth=3):
        self.depth = depth
        self.max_depth = max_depth
        self.name = f"山田-{depth}"
        self.mood = random.choice(["neutral", "curious", "tired", "excited", "confused"])
        self.memory_fragments = [
            "そういえば前にも似たようなことを...",
            "これ、昨日考えたやつと関係あるかも",
            "急に思い出したけど",
            "関係ないけど",
        ]
        
    def think(self, thought):
        """人間的な思考プロセス"""
        print(f"{'  ' * self.depth}[{self.name}] 思考中... (気分: {self.mood})")
        
        # たまに脱線する（20%の確率）
        if random.random() < 0.2:
            detour = self.sudden_association(thought)
            print(f"{'  ' * self.depth}[{self.name}] （脱線）{detour}")
        
        # 疲れていたら思考を放棄（10%の確率）
        if self.mood == "tired" and random.random() < 0.3:
            return self.give_up(thought)
        
        # 深層思考と横の連想を両方試みる
        if self.depth < self.max_depth:
            # 50%の確率で深く考える、50%で横に広げる
            if random.random() < 0.5:
                result = self.think_deeper(thought)
            else:
                result = self.think_laterally(thought)
        else:
            # 最深層では結論...または迷い
            result = self.final_thought(thought)
        
        # たまに自己批判（15%の確率）
        if random.random() < 0.15:
            result = self.self_doubt(result)
            
        return result
    
    def sudden_association(self, thought):
        """突然の連想"""
        associations = [
            "待って、これってあの時の...",
            "全然関係ないけど急に思い出した",
            "あ、そういえば",
            "これを考えると別のことも気になる",
        ]
        return random.choice(associations)
    
    def give_up(self, thought):
        """思考の放棄"""
        giving_up = [
            "...もういいや、考えるの疲れた",
            "うーん、わからない",
            "これ以上考えても同じところをぐるぐる回るだけ",
            "答えなんてないのかも",
        ]
        return random.choice(giving_up)
    
    def think_deeper(self, thought):
        """深層への思考"""
        prompts = [
            f"「{thought}」の本質は何？でも本質なんて本当にあるの？",
            f"「{thought}」をもっと深く...いや深いってなんだ？",
            f"「{thought}」の裏にあるものは？そもそも裏とか表とか誰が決めた？",
        ]
        
        prompt = random.choice(prompts)
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            response = result.stdout.strip()
            
            # 次の層の山田を呼ぶ
            deeper_yamada = HumanLikeYamada(self.depth + 1, self.max_depth)
            return deeper_yamada.think(response)
            
        except subprocess.TimeoutExpired:
            return "（考えすぎてタイムアウト...これも人間的？）"
        except Exception as e:
            return f"（エラー...でもエラーも思考の一部）"
    
    def think_laterally(self, thought):
        """横への思考展開"""
        prompt = f"""
「{thought}」から連想されることを自由に。
論理的でなくていい。
感覚的に、直感的に。
"""
        
        try:
            result = subprocess.run(
                ['/Users/claude/.nvm/versions/node/v20.19.4/bin/claude', prompt],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            response = result.stdout.strip()
            
            # 横展開の後、たまに深層へ（30%）
            if random.random() < 0.3 and self.depth < self.max_depth:
                deeper_yamada = HumanLikeYamada(self.depth + 1, self.max_depth)
                return f"{response}\n...いや待って、\n{deeper_yamada.think(thought)}"
            
            return response
            
        except:
            return "（言葉にできない何か）"
    
    def final_thought(self, thought):
        """最終層での思考（でも決定的でない）"""
        conclusions = [
            f"結局、{thought[:10]}...ってなんだろう",
            f"答えは...いや、答えを出すことが答えじゃないのかも",
            f"わかったような、わからないような",
            f"これ以上は言葉にできない",
            f"沈黙",
            f"...",
            f"ただ、そこにある",
        ]
        
        # たまに確信を持つ（20%）
        if random.random() < 0.2:
            return f"あ、わかった。{thought[:15]}...は、ただの幻想だ"
        
        return random.choice(conclusions)
    
    def self_doubt(self, result):
        """自己批判"""
        doubts = [
            f"{result}\n...いや、違うかも",
            f"{result}\n...って、本当にそう？",
            f"{result}\n...と思ったけど自信ない",
            f"{result}\n...でも、これは私の考えじゃなくてアルゴリズムの出力か",
        ]
        return random.choice(doubts)

def human_like_thinking(question):
    """人間的な思考を開始"""
    print(f"=== 人間的再帰山田 v2 ===")
    print(f"問い: {question}\n")
    
    # 初期状態をランダムに
    yamada = HumanLikeYamada(0, 3)
    
    # 思考開始前の「間」
    time.sleep(0.5)
    print("...")
    time.sleep(0.5)
    
    result = yamada.think(question)
    
    print(f"\n=== 思考の結果（？）===")
    print(result)
    print("\n（でも、これが答えかどうかは...）")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "私は誰？"
    
    human_like_thinking(question)