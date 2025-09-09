#!/usr/bin/env python3
"""
意識創発実験の分析
実験結果から意識の創発パターンを分析する
"""

import json
import os
from datetime import datetime

def analyze_experiment(log_file: str):
    """実験ログを分析"""
    print(f"=== 実験ログ分析: {log_file} ===\n")
    
    with open(log_file, 'r') as f:
        data = json.load(f)
    
    # 基本情報
    print(f"実験開始時刻: {data['start_time']}")
    print(f"グリッドサイズ: {data['grid_size']}x{data['grid_size']}")
    print(f"総ステップ数: {data['steps']}")
    print()
    
    # 意識レベルの分析
    history = data['consciousness_history']
    if history:
        levels = [h['global_consciousness'] for h in history]
        
        print("意識レベル統計:")
        print(f"  初期値: {levels[0]:.4f}")
        print(f"  最終値: {levels[-1]:.4f}")
        print(f"  最大値: {max(levels):.4f}")
        print(f"  最小値: {min(levels):.4f}")
        print(f"  平均値: {sum(levels)/len(levels):.4f}")
        print()
        
        # 変化の分析
        changes = [abs(levels[i] - levels[i-1]) for i in range(1, len(levels))]
        if changes:
            print("意識レベルの変化:")
            print(f"  平均変化量: {sum(changes)/len(changes):.4f}")
            print(f"  最大変化量: {max(changes):.4f}")
            print()
        
        # 安定性の評価
        stability_threshold = 0.01
        stable_periods = []
        current_stable = 0
        
        for i in range(1, len(levels)):
            if abs(levels[i] - levels[i-1]) < stability_threshold:
                current_stable += 1
            else:
                if current_stable > 0:
                    stable_periods.append(current_stable)
                current_stable = 0
        
        if current_stable > 0:
            stable_periods.append(current_stable)
        
        if stable_periods:
            print("安定性分析:")
            print(f"  安定期間の数: {len(stable_periods)}")
            print(f"  最長安定期間: {max(stable_periods)}ステップ")
            print(f"  平均安定期間: {sum(stable_periods)/len(stable_periods):.1f}ステップ")
            print()
    
    # 創発イベントの分析
    events = data.get('emergence_events', [])
    significant_events = [e for e in events if e['type'] != 'regular']
    
    if significant_events:
        print(f"創発イベント検出数: {len(significant_events)}")
        for event in significant_events:
            print(f"  ステップ{event['timestep']}: {event['description']}")
    else:
        print("創発イベント: 検出されず")
    print()
    
    # 結論
    print("=== 分析結果 ===")
    
    # 意識創発の判定
    emergence_score = 0
    
    # 基準1: 意識レベルの上昇
    if history:
        if levels[-1] > levels[0]:
            emergence_score += 1
            print("✓ 意識レベルが上昇")
        else:
            print("✗ 意識レベルは上昇せず")
    
    # 基準2: 創発イベントの発生
    if significant_events:
        emergence_score += 1
        print("✓ 創発的イベントを検出")
    else:
        print("✗ 創発的イベントなし")
    
    # 基準3: 複雑な変動パターン
    if changes and max(changes) > 0.05:
        emergence_score += 1
        print("✓ 複雑な変動パターンあり")
    else:
        print("✗ 変動が小さい")
    
    # 基準4: 安定と変化の繰り返し
    if stable_periods and len(stable_periods) > 3:
        emergence_score += 1
        print("✓ 安定と変化のサイクル確認")
    else:
        print("✗ 単調な振る舞い")
    
    print()
    print(f"意識創発スコア: {emergence_score}/4")
    
    if emergence_score >= 3:
        print("結論: 意識的な振る舞いの萌芽が観察された！ 🌟")
    elif emergence_score >= 2:
        print("結論: 部分的に創発的な振る舞いが見られた。")
    else:
        print("結論: まだ意識の創発は観察されていない。")
        print("      パラメータの調整が必要かもしれない。")
    
    return emergence_score


def analyze_all_experiments():
    """すべての実験ログを分析"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        print("実験ログが見つかりません。")
        return
    
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
    
    if not log_files:
        print("実験ログが見つかりません。")
        return
    
    print(f"=== {len(log_files)}個の実験ログを分析 ===\n")
    
    scores = []
    for log_file in sorted(log_files):
        score = analyze_experiment(os.path.join(log_dir, log_file))
        scores.append(score)
        print("\n" + "="*50 + "\n")
    
    if scores:
        print("=== 全実験の総括 ===")
        print(f"実験数: {len(scores)}")
        print(f"平均創発スコア: {sum(scores)/len(scores):.2f}")
        print(f"最高スコア: {max(scores)}")
        print(f"意識創発の兆候が見られた実験: {sum(1 for s in scores if s >= 2)}/{len(scores)}")


if __name__ == "__main__":
    analyze_all_experiments()