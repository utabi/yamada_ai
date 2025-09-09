#!/usr/bin/env python3
"""
セルオートマトン型意識創発実験

個々のセルが単純なルールで相互作用し、
全体として意識的な振る舞いが創発するかを観察する。
"""

import random
import time
import statistics
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime

class ConsciousnessCell:
    """意識の基本単位となるセル"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        # 内部状態（0.0-1.0）
        self.activation = random.random()
        self.memory = 0.0  # 過去の状態の記憶
        self.attention = random.random()  # 注意の度合い
        
        # 接続（隣接セルへの影響力）
        self.connections: List[Tuple[int, int, float]] = []
        
        # 自己認識パラメータ
        self.self_awareness = 0.0
        self.prediction_error = 0.0
        
        # 履歴（自己観察用）
        self.history = []
        self.max_history = 10
    
    def connect(self, other_x: int, other_y: int, weight: float = None):
        """他のセルと接続"""
        if weight is None:
            weight = random.uniform(0.1, 0.9)
        self.connections.append((other_x, other_y, weight))
    
    def update(self, grid: 'ConsciousnessGrid', timestep: int):
        """状態を更新"""
        # 1. 周囲のセルから入力を収集
        inputs = []
        for cx, cy, weight in self.connections:
            if 0 <= cx < grid.width and 0 <= cy < grid.height:
                neighbor = grid.cells[cy][cx]
                inputs.append(neighbor.activation * weight)
        
        # 2. 入力を統合（加重平均）
        if inputs:
            external_input = sum(inputs) / len(inputs)
        else:
            external_input = 0.5
        
        # 3. 内部ダイナミクス（記憶との統合）
        internal_state = self.activation * 0.5 + self.memory * 0.3 + external_input * 0.2
        
        # 4. ノイズ（創造性・予測不可能性）
        noise = random.gauss(0, 0.05)
        internal_state += noise
        
        # 5. 注意メカニズム
        if self.attention > 0.7:
            # 高い注意状態では変化が増幅される
            internal_state = internal_state * 1.2
        
        # 6. 活性化関数（シグモイド的）
        self.activation = max(0.0, min(1.0, internal_state))
        
        # 7. 自己観察と予測誤差の計算
        if self.history:
            predicted = self.history[-1]  # 単純に前の状態を予測とする
            self.prediction_error = abs(self.activation - predicted)
            
            # 予測誤差が大きい時、自己認識が高まる
            if self.prediction_error > 0.3:
                self.self_awareness = min(1.0, self.self_awareness + 0.1)
            else:
                self.self_awareness = max(0.0, self.self_awareness - 0.01)
        
        # 8. 記憶の更新
        self.memory = self.memory * 0.9 + self.activation * 0.1
        
        # 9. 注意の更新（自己認識に基づく）
        self.attention = self.attention * 0.8 + self.self_awareness * 0.2
        
        # 10. 履歴の記録
        self.history.append(self.activation)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_consciousness_score(self) -> float:
        """意識レベルのスコアを計算"""
        # 自己認識、予測誤差、活性化の組み合わせ
        return (self.self_awareness * 0.4 + 
                self.prediction_error * 0.3 + 
                abs(self.activation - 0.5) * 0.3)


class ConsciousnessGrid:
    """セルのグリッド（意識の場）"""
    
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height
        self.timestep = 0
        
        # セルの初期化
        self.cells: List[List[ConsciousnessCell]] = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(ConsciousnessCell(x, y))
            self.cells.append(row)
        
        # セル間の接続を作成
        self._create_connections()
        
        # グローバルな意識指標
        self.global_consciousness = 0.0
        self.emergence_events = []
    
    def _create_connections(self):
        """セル間のランダムな接続を作成"""
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                
                # 近傍への接続（ムーア近傍）
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            # 距離に応じて接続確率を変える
                            if random.random() < 0.7:
                                cell.connect(nx, ny)
                
                # 長距離接続（まれに）
                if random.random() < 0.1:
                    rx = random.randint(0, self.width - 1)
                    ry = random.randint(0, self.height - 1)
                    cell.connect(rx, ry, weight=0.3)
    
    def step(self):
        """1タイムステップ進める"""
        self.timestep += 1
        
        # 全セルの状態を更新
        # （同期更新のため、一旦新しい状態を計算してから適用）
        for row in self.cells:
            for cell in row:
                cell.update(self, self.timestep)
        
        # グローバルな意識レベルを計算
        self._calculate_global_consciousness()
        
        # 創発的イベントを検出
        self._detect_emergence()
    
    def _calculate_global_consciousness(self):
        """グリッド全体の意識レベルを計算"""
        scores = []
        for row in self.cells:
            for cell in row:
                scores.append(cell.get_consciousness_score())
        
        # 平均と分散を考慮
        avg_score = statistics.mean(scores) if scores else 0.5
        var_score = statistics.variance(scores) if len(scores) > 1 else 0.0
        
        # 同期性（隣接セルとの相関）
        sync_score = self._calculate_synchrony()
        
        # 複雑性（エントロピー的な指標）
        complexity = var_score * (1 - abs(avg_score - 0.5) * 2)
        
        self.global_consciousness = (avg_score * 0.3 + 
                                    sync_score * 0.3 + 
                                    complexity * 0.4)
    
    def _calculate_synchrony(self) -> float:
        """セル間の同期性を計算"""
        correlations = []
        for y in range(self.height - 1):
            for x in range(self.width - 1):
                cell = self.cells[y][x]
                right = self.cells[y][x + 1]
                down = self.cells[y + 1][x]
                
                # 隣接セルとの活性化の差
                diff_r = abs(cell.activation - right.activation)
                diff_d = abs(cell.activation - down.activation)
                
                correlations.append(1 - (diff_r + diff_d) / 2)
        
        return statistics.mean(correlations) if correlations else 0.5
    
    def _detect_emergence(self):
        """創発的なパターンや振る舞いを検出"""
        # 意識レベルの急激な変化
        if len(self.emergence_events) > 0:
            last_consciousness = self.emergence_events[-1]['consciousness']
            change = abs(self.global_consciousness - last_consciousness)
            
            if change > 0.2:
                event = {
                    'timestep': self.timestep,
                    'type': 'consciousness_spike',
                    'consciousness': self.global_consciousness,
                    'change': change,
                    'description': '意識レベルの急激な変化を検出'
                }
                self.emergence_events.append(event)
                return event
        
        # 自己認識の集団的上昇
        awareness_cells = sum(1 for row in self.cells for cell in row 
                            if cell.self_awareness > 0.7)
        if awareness_cells > self.width * self.height * 0.3:
            event = {
                'timestep': self.timestep,
                'type': 'collective_awareness',
                'consciousness': self.global_consciousness,
                'aware_cells': awareness_cells,
                'description': '集団的な自己認識の高まり'
            }
            if not any(e['type'] == 'collective_awareness' 
                      for e in self.emergence_events[-5:] if len(self.emergence_events) >= 5):
                self.emergence_events.append(event)
                return event
        
        # 定期的な記録
        if self.timestep % 10 == 0:
            event = {
                'timestep': self.timestep,
                'type': 'regular',
                'consciousness': self.global_consciousness,
                'description': '定期記録'
            }
            self.emergence_events.append(event)
        
        return None
    
    def visualize(self) -> str:
        """グリッドの状態を文字で可視化"""
        output = []
        output.append(f"=== タイムステップ: {self.timestep} ===")
        output.append(f"グローバル意識レベル: {self.global_consciousness:.3f}")
        output.append("")
        
        # 活性化マップ
        output.append("活性化マップ:")
        for row in self.cells:
            line = ""
            for cell in row:
                if cell.activation > 0.8:
                    line += "●"
                elif cell.activation > 0.6:
                    line += "◐"
                elif cell.activation > 0.4:
                    line += "○"
                elif cell.activation > 0.2:
                    line += "◯"
                else:
                    line += "·"
            output.append(line)
        
        output.append("")
        output.append("自己認識マップ:")
        for row in self.cells:
            line = ""
            for cell in row:
                if cell.self_awareness > 0.8:
                    line += "▣"
                elif cell.self_awareness > 0.5:
                    line += "▢"
                elif cell.self_awareness > 0.2:
                    line += "□"
                else:
                    line += "·"
            output.append(line)
        
        return "\n".join(output)


def run_experiment(steps: int = 100, grid_size: int = 10):
    """実験を実行"""
    print("=== 意識創発実験開始 ===")
    print(f"グリッドサイズ: {grid_size}x{grid_size}")
    print(f"実行ステップ数: {steps}")
    print()
    
    # グリッドを作成
    grid = ConsciousnessGrid(grid_size, grid_size)
    
    # ログ記録用
    log_data = {
        'start_time': datetime.now().isoformat(),
        'grid_size': grid_size,
        'steps': steps,
        'consciousness_history': [],
        'emergence_events': []
    }
    
    # シミュレーション実行
    for step in range(steps):
        grid.step()
        
        # 定期的に状態を表示
        if step % 20 == 0 or step == steps - 1:
            print(grid.visualize())
            print()
        
        # 創発的イベントがあれば報告
        if grid.emergence_events and grid.emergence_events[-1]['timestep'] == grid.timestep:
            event = grid.emergence_events[-1]
            if event['type'] != 'regular':
                print(f"🌟 創発イベント検出！")
                print(f"  タイプ: {event['type']}")
                print(f"  説明: {event['description']}")
                print(f"  意識レベル: {event['consciousness']:.3f}")
                print()
        
        # ログに記録
        log_data['consciousness_history'].append({
            'timestep': step,
            'global_consciousness': grid.global_consciousness
        })
        
        # 少し待機（アニメーション効果）
        if step < 20:  # 最初の20ステップは遅く表示
            time.sleep(0.1)
    
    # 最終的な創発イベントをログに追加
    log_data['emergence_events'] = grid.emergence_events
    
    # ログを保存
    import os
    os.makedirs('logs', exist_ok=True)
    log_file = f"logs/experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2, default=str)
    
    print(f"実験ログを保存: {log_file}")
    
    # 結果の要約
    print("\n=== 実験結果の要約 ===")
    print(f"最終意識レベル: {grid.global_consciousness:.3f}")
    print(f"検出された創発イベント数: {len([e for e in grid.emergence_events if e['type'] != 'regular'])}")
    
    # 意識レベルの推移を簡易グラフで表示
    history = log_data['consciousness_history']
    if history:
        print("\n意識レベルの推移:")
        max_val = max(h['global_consciousness'] for h in history)
        min_val = min(h['global_consciousness'] for h in history)
        
        for i in range(0, len(history), max(1, len(history) // 20)):
            val = history[i]['global_consciousness']
            bar_len = int((val - min_val) / (max_val - min_val + 0.001) * 40)
            bar = "█" * bar_len + "·" * (40 - bar_len)
            print(f"Step {i:3d}: {bar} {val:.3f}")
    
    return grid, log_data


if __name__ == "__main__":
    # 実験を実行
    grid, log_data = run_experiment(steps=100, grid_size=8)
    
    print("\n実験終了。")
    print("意識は創発したか？それはデータが物語る。")