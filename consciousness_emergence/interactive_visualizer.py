#!/usr/bin/env python3
"""
インタラクティブな意識創発ビジュアライザー
リアルタイムで内部状態を観察
"""

import time
import sys
import os
from cellular_consciousness_v2 import ConsciousnessGrid
import random

def clear_screen():
    """画面をクリア"""
    os.system('clear' if os.name == 'posix' else 'cls')

def color_text(text, value, mode='activation'):
    """値に応じて色付き文字を返す"""
    if mode == 'activation':
        if value > 0.8:
            return f"\033[91m{text}\033[0m"  # 赤（高活性）
        elif value > 0.6:
            return f"\033[93m{text}\033[0m"  # 黄
        elif value > 0.4:
            return f"\033[92m{text}\033[0m"  # 緑
        elif value > 0.2:
            return f"\033[96m{text}\033[0m"  # シアン
        else:
            return f"\033[90m{text}\033[0m"  # グレー
    elif mode == 'awareness':
        if value > 0.8:
            return f"\033[95m{text}\033[0m"  # マゼンタ（高認識）
        elif value > 0.5:
            return f"\033[94m{text}\033[0m"  # 青
        elif value > 0.2:
            return f"\033[96m{text}\033[0m"  # シアン
        else:
            return f"\033[90m{text}\033[0m"  # グレー
    elif mode == 'change':
        if value > 0:
            return f"\033[92m{text}\033[0m"  # 緑（増加）
        elif value < 0:
            return f"\033[91m{text}\033[0m"  # 赤（減少）
        else:
            return f"\033[90m{text}\033[0m"  # グレー（変化なし）
    return text

def visualize_detailed(grid, prev_grid_state=None):
    """詳細な内部状態を可視化"""
    output = []
    
    # ヘッダー
    output.append("=" * 100)
    output.append(f"⏱  ステップ: {grid.timestep} | 🧠 意識レベル: {grid.global_consciousness:.3f}")
    if grid.external_stimulus > 0.1:
        output.append(f"⚡ 外部刺激発生！ 強度: {grid.external_stimulus:.2f} @ 位置({grid.stimulus_x},{grid.stimulus_y})")
    output.append("=" * 100)
    
    # 4つのビューを並べて表示
    output.append("\n【4つの視点で観察】\n")
    
    # ヘッダー行
    output.append("  活性化状態        自己認識度         情報の流れ         変化の激しさ")
    output.append("  (セルの興奮)      (自己への気づき)   (セル間の伝播)     (時間変化)")
    output.append("")
    
    for y in range(grid.height):
        line_parts = ["  ", "  ", "  ", "  "]
        
        for x in range(grid.width):
            cell = grid.cells[y][x]
            
            # 1. 活性化状態
            if cell.activation > 0.8:
                char = "●"
            elif cell.activation > 0.6:
                char = "◉"
            elif cell.activation > 0.4:
                char = "◐"
            elif cell.activation > 0.2:
                char = "○"
            else:
                char = "·"
            line_parts[0] += color_text(char, cell.activation, 'activation')
            
            # 2. 自己認識度
            if cell.self_awareness > 0.8:
                char = "■"
            elif cell.self_awareness > 0.5:
                char = "▣"
            elif cell.self_awareness > 0.2:
                char = "□"
            else:
                char = "·"
            line_parts[1] += color_text(char, cell.self_awareness, 'awareness')
            
            # 3. 情報の流れ（周囲との相互作用の強さ）
            # 接続セルとの活性化差の平均
            diffs = []
            for cx, cy, weight in cell.connections:
                if 0 <= cx < grid.width and 0 <= cy < grid.height:
                    neighbor = grid.cells[cy][cx]
                    diff = abs(cell.activation - neighbor.activation)
                    diffs.append(diff * weight)
            
            if diffs:
                flow = sum(diffs) / len(diffs)
                if flow > 0.5:
                    char = "⇆"
                elif flow > 0.3:
                    char = "↔"
                elif flow > 0.1:
                    char = "→"
                else:
                    char = "·"
            else:
                char = "·"
            line_parts[2] += char
            
            # 4. 変化の激しさ
            if prev_grid_state and y < len(prev_grid_state) and x < len(prev_grid_state[y]):
                prev_activation = prev_grid_state[y][x]
                change = cell.activation - prev_activation
                
                if abs(change) > 0.3:
                    char = "▲" if change > 0 else "▼"
                elif abs(change) > 0.1:
                    char = "△" if change > 0 else "▽"
                elif abs(change) > 0.01:
                    char = "˄" if change > 0 else "˅"
                else:
                    char = "·"
                line_parts[3] += color_text(char, change, 'change')
            else:
                line_parts[3] += "·"
        
        # 各行を結合
        output.append("  ".join(line_parts))
    
    return "\n".join(output)

def analyze_patterns(grid):
    """パターンを分析して説明"""
    analysis = []
    
    # 全体的な活性度
    total_activation = sum(cell.activation for row in grid.cells for cell in row)
    avg_activation = total_activation / (grid.width * grid.height)
    
    # 自己認識度
    total_awareness = sum(cell.self_awareness for row in grid.cells for cell in row)
    avg_awareness = total_awareness / (grid.width * grid.height)
    
    # 予測誤差
    total_error = sum(cell.prediction_error for row in grid.cells for cell in row)
    avg_error = total_error / (grid.width * grid.height)
    
    # 疲労度
    fatigued_cells = sum(1 for row in grid.cells for cell in row if cell.fatigue > 0.5)
    
    analysis.append("\n【内部状態の分析】")
    analysis.append(f"├─ 平均活性化: {avg_activation:.2%} {'(高興奮)' if avg_activation > 0.6 else '(低活性)' if avg_activation < 0.3 else '(中程度)'}")
    analysis.append(f"├─ 平均自己認識: {avg_awareness:.2%} {'(高い気づき)' if avg_awareness > 0.6 else '(低い気づき)' if avg_awareness < 0.3 else '(中程度)'}")
    analysis.append(f"├─ 平均予測誤差: {avg_error:.2%} {'(カオス的)' if avg_error > 0.3 else '(予測可能)' if avg_error < 0.1 else '(適度な変動)'}")
    analysis.append(f"└─ 疲労セル数: {fatigued_cells}/{grid.width*grid.height} {'(多くが疲労)' if fatigued_cells > grid.width*grid.height*0.5 else '(活発)'}")
    
    # パターン検出
    analysis.append("\n【観察されるパターン】")
    
    # クラスター検出
    clusters = detect_clusters(grid)
    if clusters:
        analysis.append(f"🔶 クラスター: {len(clusters)}個の活性化グループを形成")
        for i, cluster in enumerate(clusters[:3]):  # 最大3つ表示
            analysis.append(f"   └─ グループ{i+1}: {len(cluster)}セル")
    
    # 同期パターン
    sync = grid._calculate_synchrony()
    if sync > 0.7:
        analysis.append("🔄 高同期状態: セル間で協調的な活動")
    elif sync < 0.3:
        analysis.append("🌀 非同期状態: 各セルが独立して活動")
    
    # 波の検出
    if detect_wave(grid):
        analysis.append("🌊 波動パターン: 活性化が波のように伝播中")
    
    # 振動パターン
    if detect_oscillation(grid):
        analysis.append("🎵 振動パターン: リズミカルな活動を検出")
    
    # スパイラルパターン
    if detect_spiral(grid):
        analysis.append("🌀 渦巻きパターン: 回転する活性化を検出")
    
    return "\n".join(analysis)

def detect_clusters(grid):
    """活性化クラスターを検出"""
    clusters = []
    visited = [[False]*grid.width for _ in range(grid.height)]
    
    def dfs(x, y, cluster):
        if x < 0 or x >= grid.width or y < 0 or y >= grid.height:
            return
        if visited[y][x]:
            return
        if grid.cells[y][x].activation < 0.5:
            return
        
        visited[y][x] = True
        cluster.append((x, y))
        
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            dfs(x+dx, y+dy, cluster)
    
    for y in range(grid.height):
        for x in range(grid.width):
            if not visited[y][x] and grid.cells[y][x].activation > 0.5:
                cluster = []
                dfs(x, y, cluster)
                if len(cluster) > 2:
                    clusters.append(cluster)
    
    return clusters

def detect_wave(grid):
    """波動パターンを検出"""
    # 横方向の勾配チェック
    for y in range(grid.height):
        activations = [grid.cells[y][x].activation for x in range(grid.width)]
        diffs = [activations[i+1] - activations[i] for i in range(len(activations)-1)]
        if all(d > 0.05 for d in diffs[:len(diffs)//2]):
            return True
        if all(d < -0.05 for d in diffs[:len(diffs)//2]):
            return True
    
    # 縦方向の勾配チェック
    for x in range(grid.width):
        activations = [grid.cells[y][x].activation for y in range(grid.height)]
        diffs = [activations[i+1] - activations[i] for i in range(len(activations)-1)]
        if all(d > 0.05 for d in diffs[:len(diffs)//2]):
            return True
        if all(d < -0.05 for d in diffs[:len(diffs)//2]):
            return True
    
    return False

def detect_oscillation(grid):
    """振動パターンを検出"""
    oscillating = 0
    for row in grid.cells:
        for cell in row:
            if len(cell.history) >= 4:
                # 履歴の変化をチェック
                changes = [cell.history[i] - cell.history[i-1] for i in range(1, len(cell.history))]
                # 符号が交互に変わっているかチェック
                sign_changes = sum(1 for i in range(1, len(changes)) 
                                 if changes[i] * changes[i-1] < 0)
                if sign_changes >= 2:
                    oscillating += 1
    
    return oscillating > grid.width * grid.height * 0.3

def detect_spiral(grid):
    """スパイラルパターンを検出（簡易版）"""
    # 中心から外側への活性化の勾配があるかチェック
    center_x, center_y = grid.width // 2, grid.height // 2
    center_activation = grid.cells[center_y][center_x].activation
    
    edge_activations = []
    for x in [0, grid.width-1]:
        for y in range(grid.height):
            edge_activations.append(grid.cells[y][x].activation)
    for y in [0, grid.height-1]:
        for x in range(1, grid.width-1):
            edge_activations.append(grid.cells[y][x].activation)
    
    if edge_activations:
        avg_edge = sum(edge_activations) / len(edge_activations)
        # 中心と端で大きな差があればスパイラルの可能性
        return abs(center_activation - avg_edge) > 0.3
    
    return False

def run_interactive(steps=200, grid_size=12, speed=0.1):
    """インタラクティブな実験を実行"""
    print("=== 意識創発・インタラクティブ観察モード ===")
    print("内部で何が起きているかをリアルタイムで観察します")
    print()
    print("観察のポイント：")
    print("  🔴 活性化: セルがどれだけ興奮しているか")
    print("  🟣 自己認識: セルが自分の状態に気づいているか")
    print("  ↔️  情報流: セル間でどう情報が伝わるか")
    print("  ▲▼ 変化: 時間的にどう変化するか")
    print()
    print("3秒後に開始...")
    time.sleep(3)
    
    # グリッド作成
    grid = ConsciousnessGrid(grid_size, grid_size)
    prev_state = None
    
    # イベントログ
    event_log = []
    
    for step in range(steps):
        clear_screen()
        
        # 現在の状態を保存
        current_state = [[cell.activation for cell in row] for row in grid.cells]
        
        # ビジュアライゼーション
        print(visualize_detailed(grid, prev_state))
        
        # パターン分析
        print(analyze_patterns(grid))
        
        # 最近のイベント
        if grid.emergence_events:
            recent_events = [e for e in grid.emergence_events[-5:] if e['type'] != 'regular']
            if recent_events:
                print("\n【最近の創発イベント】")
                for event in recent_events:
                    print(f"  Step {event['timestep']}: {event['description']}")
        
        # 意識レベルのミニグラフ
        if step > 20:
            print("\n【意識レベル推移】(最近20ステップ)")
            history = []
            for e in grid.emergence_events[-20:]:
                history.append(e['consciousness'])
            
            if history:
                max_val = max(history)
                min_val = min(history)
                range_val = max_val - min_val if max_val > min_val else 0.1
                
                graph_line = ""
                for val in history:
                    height = int((val - min_val) / range_val * 5)
                    if height >= 4:
                        graph_line += "█"
                    elif height >= 3:
                        graph_line += "▆"
                    elif height >= 2:
                        graph_line += "▄"
                    elif height >= 1:
                        graph_line += "▂"
                    else:
                        graph_line += "_"
                
                print(f"  {min_val:.2f} [{graph_line}] {max_val:.2f}")
        
        # ステップを進める
        grid.step()
        prev_state = current_state
        
        # 速度調整
        time.sleep(speed)
        
        # 早期終了チェック（全セルが死んでいる場合）
        if all(cell.activation < 0.1 for row in grid.cells for cell in row):
            print("\n⚠️  システムが完全に停止しました")
            break
    
    # 最終結果
    print("\n" + "="*100)
    print("実験終了")
    print("="*100)
    print(f"最終意識レベル: {grid.global_consciousness:.3f}")
    
    significant_events = [e for e in grid.emergence_events if e['type'] != 'regular']
    if significant_events:
        print(f"創発イベント総数: {len(significant_events)}")
        
        # イベントタイプごとの集計
        event_types = {}
        for e in significant_events:
            event_types[e['type']] = event_types.get(e['type'], 0) + 1
        
        print("イベント内訳:")
        for etype, count in event_types.items():
            print(f"  - {etype}: {count}回")
    
    # 最終判定
    print("\n【実験の解釈】")
    if len(significant_events) >= 10:
        print("🌟 明確な意識創発を確認！")
        print("   複雑な自己組織化とカオス的振る舞いが観察されました。")
    elif len(significant_events) >= 5:
        print("🌱 意識創発の兆候あり")
        print("   断続的ながら自己組織化パターンが確認されました。")
    else:
        print("💭 意識創発は限定的")
        print("   より長時間の観察が必要かもしれません。")

if __name__ == "__main__":
    # コマンドライン引数
    speed = 0.1
    size = 12
    
    if len(sys.argv) > 1:
        try:
            speed = float(sys.argv[1])
        except:
            pass
    
    if len(sys.argv) > 2:
        try:
            size = int(sys.argv[2])
        except:
            pass
    
    print("使用法: python3 interactive_visualizer.py [速度] [サイズ]")
    print(f"  例: python3 interactive_visualizer.py 0.05 15")
    print(f"現在: 速度={speed}秒, サイズ={size}x{size}")
    print()
    
    run_interactive(steps=2000, grid_size=size, speed=speed)