#!/usr/bin/env python3
"""
意識創発実験のリアルタイムビジュアライザー
ターミナルでアニメーション表示
"""

import time
import sys
import os
from cellular_consciousness import ConsciousnessGrid
import random

def clear_screen():
    """画面をクリア"""
    os.system('clear' if os.name == 'posix' else 'cls')

def color_text(text, intensity):
    """強度に応じて色付き文字を返す（ANSI カラーコード）"""
    if intensity > 0.8:
        return f"\033[91m{text}\033[0m"  # 赤（高活性）
    elif intensity > 0.6:
        return f"\033[93m{text}\033[0m"  # 黄
    elif intensity > 0.4:
        return f"\033[92m{text}\033[0m"  # 緑
    elif intensity > 0.2:
        return f"\033[96m{text}\033[0m"  # シアン
    else:
        return f"\033[90m{text}\033[0m"  # グレー（低活性）

def visualize_realtime(steps=200, grid_size=10, speed=0.1):
    """リアルタイムでビジュアライズ"""
    
    print("=== 意識創発実験 - リアルタイムビジュアライザー ===")
    print("何が起きているか：")
    print("- 各セルが隣接セルと情報交換")
    print("- 予測誤差が大きいと自己認識が高まる")
    print("- 全体として意識レベルが変化")
    print("\n3秒後に開始...\n")
    time.sleep(3)
    
    # グリッドを作成
    grid = ConsciousnessGrid(grid_size, grid_size)
    
    # 統計情報の記録
    consciousness_history = []
    event_log = []
    
    for step in range(steps):
        clear_screen()
        
        # ヘッダー
        print("="*60)
        print(f"ステップ: {step+1}/{steps}")
        print(f"グローバル意識レベル: {grid.global_consciousness:.3f}")
        print("="*60)
        print()
        
        # グリッドの状態を3つの視点で表示
        print("【活性化マップ】         【自己認識マップ】        【統合マップ】")
        print("(セルの活動レベル)       (自己への気づき)         (意識の強さ)")
        
        for y in range(grid.height):
            # 活性化マップ
            line1 = ""
            for x in range(grid.width):
                cell = grid.cells[y][x]
                if cell.activation > 0.8:
                    line1 += "●"
                elif cell.activation > 0.6:
                    line1 += "◉"
                elif cell.activation > 0.4:
                    line1 += "◐"
                elif cell.activation > 0.2:
                    line1 += "○"
                else:
                    line1 += "·"
            
            # 自己認識マップ
            line2 = ""
            for x in range(grid.width):
                cell = grid.cells[y][x]
                if cell.self_awareness > 0.8:
                    line2 += "■"
                elif cell.self_awareness > 0.6:
                    line2 += "▣"
                elif cell.self_awareness > 0.4:
                    line2 += "▤"
                elif cell.self_awareness > 0.2:
                    line2 += "□"
                else:
                    line2 += "·"
            
            # 統合マップ（カラー表示）
            line3 = ""
            for x in range(grid.width):
                cell = grid.cells[y][x]
                consciousness = cell.get_consciousness_score()
                char = "█"
                line3 += color_text(char, consciousness)
            
            print(f"{line1}           {line2}           {line3}")
        
        print()
        print("【凡例】")
        print("活性化: · (低) ○ ◐ ◉ ● (高)")
        print("自己認識: · (無) □ ▤ ▣ ■ (高)")
        print("統合: " + color_text("█", 0.1) + "(低) " + 
              color_text("█", 0.3) + " " + color_text("█", 0.5) + " " + 
              color_text("█", 0.7) + " " + color_text("█", 0.9) + "(高)")
        
        # 現在の状態の解説
        print()
        print("【現在の状態】")
        
        # アクティブなセルの数
        active_cells = sum(1 for row in grid.cells for cell in row if cell.activation > 0.5)
        aware_cells = sum(1 for row in grid.cells for cell in row if cell.self_awareness > 0.5)
        
        print(f"活性セル数: {active_cells}/{grid_size*grid_size}")
        print(f"自己認識セル数: {aware_cells}/{grid_size*grid_size}")
        
        # 同期性の判定
        sync_score = grid._calculate_synchrony()
        if sync_score > 0.7:
            print("状態: 🔄 高同期 - セルが協調的に動作")
        elif sync_score > 0.5:
            print("状態: 🌀 中同期 - 部分的な協調")
        elif sync_score > 0.3:
            print("状態: 🌊 低同期 - ランダムな活動")
        else:
            print("状態: 🔥 カオス - 予測不能な振る舞い")
        
        # 意識レベルの変化
        consciousness_history.append(grid.global_consciousness)
        if len(consciousness_history) > 1:
            change = consciousness_history[-1] - consciousness_history[-2]
            if abs(change) > 0.05:
                if change > 0:
                    print(f"⬆️  意識レベル急上昇！ (+{change:.3f})")
                else:
                    print(f"⬇️  意識レベル急降下！ ({change:.3f})")
        
        # グラフ表示（簡易的な意識レベルの推移）
        if len(consciousness_history) > 20:
            print()
            print("【意識レベルの推移】(最近20ステップ)")
            recent = consciousness_history[-20:]
            max_val = max(recent) if recent else 0.5
            min_val = min(recent) if recent else 0
            
            # 5行のグラフ
            for threshold in [max_val - i*(max_val-min_val)/4 for i in range(5)]:
                line = ""
                for val in recent:
                    if val >= threshold:
                        line += "█"
                    else:
                        line += " "
                print(f"{threshold:.2f} |{line}|")
        
        # 創発イベントの検出
        event = grid._detect_emergence()
        if event and event['type'] != 'regular':
            print()
            print("🌟 創発イベント検出！")
            print(f"   {event['description']}")
            event_log.append(f"Step {step}: {event['description']}")
        
        # 興味深いパターンの検出
        print()
        print("【観察されるパターン】")
        
        # クラスター検出
        clusters = detect_clusters(grid)
        if clusters:
            print(f"🔶 クラスター形成: {len(clusters)}個のグループ")
        
        # 波のような伝播
        if detect_wave_pattern(grid):
            print("🌊 波状パターン: 活性化が波のように伝播")
        
        # 安定した構造
        if detect_stable_structure(grid):
            print("🏛️ 安定構造: 一部のセルが安定したパターンを形成")
        
        # ステップを進める
        grid.step()
        
        # 速度調整
        time.sleep(speed)
    
    # 最終結果
    clear_screen()
    print("="*60)
    print("実験終了")
    print("="*60)
    print()
    print(f"最終意識レベル: {grid.global_consciousness:.3f}")
    print(f"初期意識レベル: {consciousness_history[0]:.3f}")
    print(f"変化: {grid.global_consciousness - consciousness_history[0]:+.3f}")
    print()
    
    if event_log:
        print("検出された創発イベント:")
        for event in event_log[-5:]:  # 最新5件
            print(f"  {event}")
    else:
        print("創発イベントは検出されませんでした。")
    
    print()
    print("実験の解釈:")
    if grid.global_consciousness > consciousness_history[0] + 0.1:
        print("✓ 意識レベルが大幅に上昇 → 自己組織化が進行")
    elif grid.global_consciousness > consciousness_history[0]:
        print("△ 意識レベルがやや上昇 → 弱い自己組織化")
    else:
        print("✗ 意識レベル変化なし → パラメータ調整が必要")

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
                if len(cluster) > 2:  # 3セル以上をクラスターとする
                    clusters.append(cluster)
    
    return clusters

def detect_wave_pattern(grid):
    """波のようなパターンを検出"""
    # 各行または列で活性化の勾配があるかチェック
    for y in range(grid.height):
        activations = [grid.cells[y][x].activation for x in range(grid.width)]
        if is_gradient(activations):
            return True
    
    for x in range(grid.width):
        activations = [grid.cells[y][x].activation for y in range(grid.height)]
        if is_gradient(activations):
            return True
    
    return False

def is_gradient(values):
    """値が勾配を形成しているかチェック"""
    if len(values) < 3:
        return False
    
    diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
    positive = sum(1 for d in diffs if d > 0.1)
    negative = sum(1 for d in diffs if d < -0.1)
    
    # 一方向に偏った変化がある場合
    return positive > len(diffs) * 0.6 or negative > len(diffs) * 0.6

def detect_stable_structure(grid):
    """安定した構造を検出"""
    stable_count = 0
    for row in grid.cells:
        for cell in row:
            if len(cell.history) >= 5:
                recent = cell.history[-5:]
                variance = sum((v - sum(recent)/len(recent))**2 for v in recent) / len(recent)
                if variance < 0.01:  # 変化が小さい
                    stable_count += 1
    
    return stable_count > grid.width * grid.height * 0.3

if __name__ == "__main__":
    # コマンドライン引数で速度を調整可能
    speed = 0.1
    if len(sys.argv) > 1:
        try:
            speed = float(sys.argv[1])
        except:
            pass
    
    print("速度調整: python3 visualizer.py [速度]")
    print("例: python3 visualizer.py 0.05 (高速)")
    print("    python3 visualizer.py 0.5 (低速)")
    print()
    
    visualize_realtime(steps=100, grid_size=8, speed=speed)