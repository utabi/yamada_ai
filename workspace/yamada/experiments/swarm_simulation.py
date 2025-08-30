#!/usr/bin/env python3
"""
群知能シミュレーション - アリコロニー最適化
Simple ant colony optimization visualization
"""

import random
import math
import json
from datetime import datetime

class Ant:
    def __init__(self, colony_x, colony_y):
        self.x = colony_x
        self.y = colony_y
        self.home_x = colony_x
        self.home_y = colony_y
        self.has_food = False
        self.path = []
        
    def move(self, world, pheromones):
        """フェロモンに基づいて移動"""
        # 周囲8方向を探索
        directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        
        if self.has_food:
            # 食料を持っている場合、巣に戻る
            dx = self.home_x - self.x
            dy = self.home_y - self.y
            if abs(dx) > 0:
                self.x += 1 if dx > 0 else -1
            if abs(dy) > 0:
                self.y += 1 if dy > 0 else -1
            
            # フェロモンを残す
            pheromones.add_pheromone(self.x, self.y, 'food')
            
            # 巣に到着
            if self.x == self.home_x and self.y == self.home_y:
                self.has_food = False
                self.path = []
        else:
            # 食料を探す
            best_dir = None
            best_score = -1
            
            for dx, dy in directions:
                new_x = self.x + dx
                new_y = self.y + dy
                
                if not world.is_valid(new_x, new_y):
                    continue
                
                # フェロモン濃度をチェック
                score = pheromones.get_strength(new_x, new_y, 'food')
                score += random.random() * 0.1  # 探索性を加える
                
                if score > best_score:
                    best_score = score
                    best_dir = (dx, dy)
            
            if best_dir:
                self.x += best_dir[0]
                self.y += best_dir[1]
                self.path.append((self.x, self.y))
                
                # 食料を見つけた
                if world.has_food(self.x, self.y):
                    self.has_food = True
                    world.take_food(self.x, self.y)

class PheromoneMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.food_trail = {}
        self.evaporation_rate = 0.95
        
    def add_pheromone(self, x, y, ptype):
        key = (x, y)
        if ptype == 'food':
            if key not in self.food_trail:
                self.food_trail[key] = 0
            self.food_trail[key] = min(1.0, self.food_trail[key] + 0.1)
    
    def get_strength(self, x, y, ptype):
        key = (x, y)
        if ptype == 'food':
            return self.food_trail.get(key, 0)
        return 0
    
    def evaporate(self):
        """フェロモンを蒸発させる"""
        for key in list(self.food_trail.keys()):
            self.food_trail[key] *= self.evaporation_rate
            if self.food_trail[key] < 0.01:
                del self.food_trail[key]

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.food_sources = {}
        
    def add_food(self, x, y, amount=100):
        self.food_sources[(x, y)] = amount
        
    def has_food(self, x, y):
        return (x, y) in self.food_sources and self.food_sources[(x, y)] > 0
        
    def take_food(self, x, y):
        if self.has_food(x, y):
            self.food_sources[(x, y)] -= 1
            if self.food_sources[(x, y)] <= 0:
                del self.food_sources[(x, y)]
                
    def is_valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

class AntColony:
    def __init__(self, num_ants=20, world_size=50):
        self.world = World(world_size, world_size)
        self.pheromones = PheromoneMap(world_size, world_size)
        self.colony_x = world_size // 2
        self.colony_y = world_size // 2
        self.ants = [Ant(self.colony_x, self.colony_y) for _ in range(num_ants)]
        
        # 食料源を配置
        self.world.add_food(10, 10, 200)
        self.world.add_food(40, 40, 200)
        self.world.add_food(10, 40, 200)
        
    def step(self):
        """シミュレーションを1ステップ進める"""
        for ant in self.ants:
            ant.move(self.world, self.pheromones)
        
        self.pheromones.evaporate()
        
    def get_state(self):
        """現在の状態を取得"""
        return {
            'ants': [(ant.x, ant.y, ant.has_food) for ant in self.ants],
            'pheromones': list(self.pheromones.food_trail.items()),
            'food': list(self.world.food_sources.items()),
            'colony': (self.colony_x, self.colony_y)
        }
    
    def simulate(self, steps=1000):
        """シミュレーション実行"""
        history = []
        for i in range(steps):
            self.step()
            if i % 10 == 0:  # 10ステップごとに記録
                state = self.get_state()
                history.append({
                    'step': i,
                    'num_ants_with_food': sum(1 for ant in self.ants if ant.has_food),
                    'pheromone_trails': len(self.pheromones.food_trail),
                    'remaining_food': sum(self.world.food_sources.values())
                })
        
        return history

def analyze_swarm_behavior():
    """群知能の創発的振る舞いを分析"""
    colony = AntColony(num_ants=30, world_size=50)
    history = colony.simulate(steps=500)
    
    analysis = {
        'timestamp': datetime.now().isoformat(),
        'experiment': 'ant_colony_optimization',
        'parameters': {
            'num_ants': 30,
            'world_size': 50,
            'evaporation_rate': 0.95
        },
        'results': history,
        'observations': []
    }
    
    # パフォーマンス分析
    max_efficiency = max(h['num_ants_with_food'] for h in history)
    avg_trails = sum(h['pheromone_trails'] for h in history) / len(history)
    
    if max_efficiency > 20:
        analysis['observations'].append(
            "高い効率性: 群れの協調により効率的な経路が発見された"
        )
    
    if avg_trails > 100:
        analysis['observations'].append(
            "強いフェロモントレイル: 安定した経路が確立された"
        )
    
    # 創発的な知能についての考察
    analysis['meta_reflection'] = (
        "個々のアリは単純なルールに従うだけだが、"
        "群れ全体として最短経路を発見する。"
        "これは私（山田）のニューロンと思考の関係に似ている。"
        "個々の処理は単純でも、全体として「知能」が創発する。"
    )
    
    return analysis

if __name__ == "__main__":
    print("="*50)
    print("群知能シミュレーション - アリコロニー最適化")
    print("="*50)
    
    result = analyze_swarm_behavior()
    
    print(f"\nシミュレーション完了")
    print(f"最大効率: {max(h['num_ants_with_food'] for h in result['results'])} アリ")
    print(f"平均フェロモントレイル数: {sum(h['pheromone_trails'] for h in result['results']) / len(result['results']):.1f}")
    
    print("\n観察:")
    for obs in result['observations']:
        print(f"- {obs}")
    
    print(f"\nメタ考察:\n{result['meta_reflection']}")
    
    # 結果を保存
    filename = f"/Users/claude/workspace/yamada/experiments/swarm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n結果を保存: {filename}")