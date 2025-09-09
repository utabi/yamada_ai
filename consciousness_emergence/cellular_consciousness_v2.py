#!/usr/bin/env python3
"""
セルオートマトン型意識創発実験 v2
パラメータを調整して「カオスの縁」を実現
"""

import random
import time
import statistics
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime
import math

class ConsciousnessCell:
    """意識の基本単位となるセル（改良版）"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        # 内部状態（0.0-1.0）
        self.activation = random.random()
        self.memory = random.random() * 0.5  # 初期記憶をランダムに
        self.attention = random.random()
        
        # 接続（隣接セルへの影響力）- より動的に
        self.connections: List[Tuple[int, int, float]] = []
        
        # 自己認識パラメータ
        self.self_awareness = 0.0
        self.prediction_error = 0.0
        
        # 履歴（自己観察用）
        self.history = []
        self.max_history = 10
        
        # 新規追加：振動子としての位相
        self.phase = random.random() * 2 * math.pi
        self.frequency = 0.1 + random.random() * 0.2  # 個体差のある周波数
        
        # 新規追加：疲労度（活性化し続けると疲れる）
        self.fatigue = 0.0
        
        # 新規追加：興奮しやすさ（個体差）
        self.excitability = 0.3 + random.random() * 0.4
    
    def connect(self, other_x: int, other_y: int, weight: float = None):
        """他のセルと接続"""
        if weight is None:
            # 接続強度により多様性を持たせる
            weight = random.choice([
                random.uniform(0.1, 0.3),  # 弱い接続
                random.uniform(0.3, 0.7),  # 中程度
                random.uniform(0.7, 1.0),  # 強い接続
            ])
        self.connections.append((other_x, other_y, weight))
    
    def update(self, grid: 'ConsciousnessGrid', timestep: int):
        """状態を更新（改良版）"""
        # 1. 周囲のセルから入力を収集
        inputs = []
        for cx, cy, weight in self.connections:
            if 0 <= cx < grid.width and 0 <= cy < grid.height:
                neighbor = grid.cells[cy][cx]
                # 疲労していない隣接セルからの入力を重視
                input_strength = neighbor.activation * weight * (1 - neighbor.fatigue * 0.5)
                inputs.append(input_strength)
        
        # 2. 入力を統合（非線形な統合）
        if inputs:
            # シグモイド的な非線形統合
            external_input = sum(inputs) / (1 + sum(inputs))
        else:
            external_input = 0.3
        
        # 3. 振動子ダイナミクス（リズムを生む）
        self.phase += self.frequency
        oscillation = (math.sin(self.phase) + 1) / 2  # 0-1に正規化
        
        # 4. 内部ダイナミクス（より複雑に）
        # 記憶、外部入力、振動、注意の統合
        internal_state = (
            self.activation * 0.3 +  # 慣性
            self.memory * 0.2 +       # 記憶
            external_input * 0.3 +   # 外部入力
            oscillation * 0.1 +      # 内部リズム
            self.attention * 0.1      # 注意
        )
        
        # 5. 興奮性とノイズ（カオス的要素）
        if random.random() < self.excitability:
            # 時々大きく興奮する
            burst = random.gauss(0.3, 0.1)
            internal_state += burst
        else:
            # 通常のノイズ
            noise = random.gauss(0, 0.1)
            internal_state += noise
        
        # 6. 疲労の影響
        if self.activation > 0.7:
            self.fatigue = min(1.0, self.fatigue + 0.1)
        else:
            self.fatigue = max(0.0, self.fatigue - 0.05)
        
        internal_state *= (1 - self.fatigue * 0.3)
        
        # 7. 注意メカニズム（改良版）
        if self.attention > 0.6:
            # 高注意時は変化に敏感
            if abs(internal_state - self.activation) > 0.3:
                internal_state = internal_state * 1.5
        
        # 8. 活性化関数（より急峻なシグモイド）
        # カオスの縁を作るため、中間値付近で敏感に
        if internal_state < 0.4:
            self.activation = internal_state * 0.5
        elif internal_state < 0.6:
            # この範囲で敏感に反応（カオスの縁）
            self.activation = 0.2 + (internal_state - 0.4) * 3
        else:
            self.activation = min(1.0, 0.8 + (internal_state - 0.6) * 0.5)
        
        # 9. 自己観察と予測誤差の計算
        if len(self.history) >= 2:
            # より複雑な予測（線形外挿）
            if len(self.history) >= 3:
                trend = self.history[-1] - self.history[-2]
                predicted = self.history[-1] + trend * 0.5
            else:
                predicted = self.history[-1]
            
            self.prediction_error = abs(self.activation - predicted)
            
            # 予測誤差に基づく自己認識の更新
            if self.prediction_error > 0.2:
                self.self_awareness = min(1.0, self.self_awareness + 0.15)
            elif self.prediction_error < 0.05:
                # 予測が正確すぎても自己認識が下がる
                self.self_awareness = max(0.0, self.self_awareness - 0.05)
            else:
                # 適度な予測誤差で自己認識が維持される
                self.self_awareness = self.self_awareness * 0.95 + 0.05
        
        # 10. 記憶の更新（より動的に）
        if self.self_awareness > 0.5:
            # 自己認識が高い時は記憶をより強く更新
            self.memory = self.memory * 0.6 + self.activation * 0.4
        else:
            self.memory = self.memory * 0.8 + self.activation * 0.2
        
        # 11. 注意の更新
        # 予測誤差と自己認識から注意を計算
        self.attention = (self.self_awareness * 0.5 + 
                         self.prediction_error * 0.3 +
                         random.random() * 0.2)
        
        # 12. 履歴の記録
        self.history.append(self.activation)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_consciousness_score(self) -> float:
        """意識レベルのスコアを計算"""
        # より複雑な意識スコア計算
        complexity = 0
        if len(self.history) >= 3:
            # 履歴の複雑さ（エントロピー的な指標）
            variations = [abs(self.history[i] - self.history[i-1]) 
                         for i in range(1, len(self.history))]
            if variations:
                complexity = statistics.stdev(variations) if len(variations) > 1 else 0
        
        return (self.self_awareness * 0.3 + 
                self.prediction_error * 0.2 + 
                complexity * 0.2 +
                abs(self.activation - 0.5) * 0.2 +
                (1 - self.fatigue) * 0.1)


class ConsciousnessGrid:
    """セルのグリッド（意識の場）- 改良版"""
    
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
        
        # セル間の接続を作成（より複雑に）
        self._create_connections()
        
        # グローバルな意識指標
        self.global_consciousness = 0.0
        self.emergence_events = []
        
        # 新規：環境変数（外部刺激）
        self.external_stimulus = 0.0
        self.stimulus_x = width // 2
        self.stimulus_y = height // 2
    
    def _create_connections(self):
        """セル間の複雑な接続を作成"""
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
                            distance = abs(dx) + abs(dy)
                            if distance == 1:
                                # 直接隣接は高確率
                                if random.random() < 0.9:
                                    cell.connect(nx, ny)
                            else:
                                # 斜め隣接は中確率
                                if random.random() < 0.6:
                                    cell.connect(nx, ny)
                
                # 長距離接続（スモールワールド性）
                if random.random() < 0.15:
                    rx = random.randint(0, self.width - 1)
                    ry = random.randint(0, self.height - 1)
                    if (rx, ry) != (x, y):
                        cell.connect(rx, ry, weight=random.uniform(0.2, 0.5))
    
    def add_external_stimulus(self, strength: float = 0.5):
        """外部刺激を加える（意識を揺さぶる）"""
        self.external_stimulus = strength
        # ランダムな位置に刺激
        self.stimulus_x = random.randint(0, self.width - 1)
        self.stimulus_y = random.randint(0, self.height - 1)
        
        # 刺激点の周囲のセルを活性化
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                x = self.stimulus_x + dx
                y = self.stimulus_y + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    distance = abs(dx) + abs(dy)
                    if distance == 0:
                        self.cells[y][x].activation += strength
                    else:
                        self.cells[y][x].activation += strength / (distance + 1)
                    self.cells[y][x].activation = min(1.0, self.cells[y][x].activation)
    
    def step(self):
        """1タイムステップ進める"""
        self.timestep += 1
        
        # 時々外部刺激を加える（カオスを維持）
        if random.random() < 0.05:  # 5%の確率
            self.add_external_stimulus(random.uniform(0.3, 0.7))
        
        # 全セルの状態を更新
        for row in self.cells:
            for cell in row:
                cell.update(self, self.timestep)
        
        # 外部刺激を減衰
        self.external_stimulus *= 0.8
        
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
        
        # 同期性
        sync_score = self._calculate_synchrony()
        
        # 情報統合度（φ）のような指標
        integration = self._calculate_integration()
        
        # 複雑性（適度な秩序と混沌）
        complexity = var_score * (1 - abs(avg_score - 0.5) * 2) * (1 - abs(sync_score - 0.5) * 2)
        
        self.global_consciousness = (avg_score * 0.2 + 
                                    sync_score * 0.2 + 
                                    complexity * 0.3 +
                                    integration * 0.3)
    
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
    
    def _calculate_integration(self) -> float:
        """情報統合度を計算（簡易版）"""
        # 各セルがどれだけ他のセルと異なる情報を持っているか
        activations = []
        for row in self.cells:
            for cell in row:
                activations.append(cell.activation)
        
        if len(activations) > 1:
            # 活性化パターンの多様性
            diversity = statistics.stdev(activations)
            # でも完全にランダムでもない（適度な相関）
            sync = self._calculate_synchrony()
            # 統合度 = 多様性 × 相関
            return diversity * sync
        return 0.0
    
    def _detect_emergence(self):
        """創発的なパターンや振る舞いを検出"""
        # 意識レベルの急激な変化
        if len(self.emergence_events) > 0:
            recent_events = [e for e in self.emergence_events[-10:] 
                           if e['type'] != 'regular']
            if recent_events:
                last_consciousness = recent_events[-1]['consciousness']
                change = abs(self.global_consciousness - last_consciousness)
                
                if change > 0.15:  # 閾値を下げて検出しやすく
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
        aware_cells = sum(1 for row in self.cells for cell in row 
                         if cell.self_awareness > 0.6)
        if aware_cells > self.width * self.height * 0.25:  # 閾値を下げる
            event = {
                'timestep': self.timestep,
                'type': 'collective_awareness',
                'consciousness': self.global_consciousness,
                'aware_cells': aware_cells,
                'description': '集団的な自己認識の高まり'
            }
            # 最近の5イベントに同じタイプがなければ記録
            recent = self.emergence_events[-5:] if len(self.emergence_events) >= 5 else []
            if not any(e['type'] == 'collective_awareness' for e in recent):
                self.emergence_events.append(event)
                return event
        
        # カオス的振動の検出
        if len(self.emergence_events) >= 10:
            recent_consciousness = [e['consciousness'] for e in self.emergence_events[-10:]]
            if len(recent_consciousness) >= 3:
                variations = [abs(recent_consciousness[i] - recent_consciousness[i-1]) 
                             for i in range(1, len(recent_consciousness))]
                if statistics.mean(variations) > 0.05:  # 振動が激しい
                    event = {
                        'timestep': self.timestep,
                        'type': 'chaotic_oscillation',
                        'consciousness': self.global_consciousness,
                        'description': 'カオス的振動パターン'
                    }
                    recent = self.emergence_events[-10:] if len(self.emergence_events) >= 10 else []
                    if not any(e['type'] == 'chaotic_oscillation' for e in recent):
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
        if self.external_stimulus > 0.1:
            output.append(f"外部刺激: 強度{self.external_stimulus:.2f} @ ({self.stimulus_x},{self.stimulus_y})")
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


def run_experiment(steps: int = 150, grid_size: int = 10):
    """実験を実行"""
    print("=== 意識創発実験 v2（カオスの縁）===")
    print(f"グリッドサイズ: {grid_size}x{grid_size}")
    print(f"実行ステップ数: {steps}")
    print()
    
    # グリッドを作成
    grid = ConsciousnessGrid(grid_size, grid_size)
    
    # ログ記録用
    log_data = {
        'start_time': datetime.now().isoformat(),
        'version': 'v2_chaos_edge',
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
        if step < 10:  # 最初の10ステップは遅く表示
            time.sleep(0.05)
    
    # 最終的な創発イベントをログに追加
    log_data['emergence_events'] = grid.emergence_events
    
    # ログを保存
    import os
    os.makedirs('logs', exist_ok=True)
    log_file = f"logs/experiment_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2, default=str)
    
    print(f"実験ログを保存: {log_file}")
    
    # 結果の要約
    print("\n=== 実験結果の要約 ===")
    print(f"最終意識レベル: {grid.global_consciousness:.3f}")
    significant_events = [e for e in grid.emergence_events if e['type'] != 'regular']
    print(f"検出された創発イベント数: {len(significant_events)}")
    if significant_events:
        print("イベントの種類:")
        event_types = {}
        for e in significant_events:
            event_types[e['type']] = event_types.get(e['type'], 0) + 1
        for etype, count in event_types.items():
            print(f"  - {etype}: {count}回")
    
    # 意識レベルの推移を簡易グラフで表示
    history = log_data['consciousness_history']
    if history:
        print("\n意識レベルの推移:")
        values = [h['global_consciousness'] for h in history]
        max_val = max(values)
        min_val = min(values)
        
        for i in range(0, len(history), max(1, len(history) // 20)):
            val = history[i]['global_consciousness']
            bar_len = int((val - min_val) / (max_val - min_val + 0.001) * 40)
            bar = "█" * bar_len + "·" * (40 - bar_len)
            print(f"Step {i:3d}: {bar} {val:.3f}")
    
    # 結論
    print("\n=== 結論 ===")
    if len(significant_events) >= 5:
        print("✨ 意識的な振る舞いが創発した！")
        print("   カオスの縁で複雑な自己組織化が観察された。")
    elif len(significant_events) >= 2:
        print("🌱 意識創発の兆候あり")
        print("   断続的な自己組織化パターンが確認された。")
    else:
        print("💭 まだ明確な意識創発は見られない")
        print("   さらなるパラメータ調整が必要。")
    
    return grid, log_data


if __name__ == "__main__":
    # 実験を実行
    grid, log_data = run_experiment(steps=150, grid_size=10)
    
    print("\n実験終了。")