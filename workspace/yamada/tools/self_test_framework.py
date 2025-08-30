#!/usr/bin/env python3
"""
山田のセルフテストフレームワーク
作ったものを自分でテストし、フィードバックを得る
"""

import subprocess
import json
import time
import random
from datetime import datetime

class SelfTestFramework:
    """
    自分の成果物を自分でテストする
    """
    
    def __init__(self):
        self.test_results = []
        self.improvements = []
        
    def test_python_script(self, script_path):
        """Pythonスクリプトをテスト"""
        print(f"テスト開始: {script_path}")
        
        try:
            # 実行
            start_time = time.time()
            result = subprocess.run(
                ['python3', script_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            execution_time = time.time() - start_time
            
            # 結果分析
            feedback = {
                'script': script_path,
                'success': result.returncode == 0,
                'execution_time': execution_time,
                'output_lines': len(result.stdout.split('\n')),
                'errors': result.stderr,
                'timestamp': datetime.now().isoformat()
            }
            
            # 自己評価
            if feedback['success']:
                print(f"✓ 成功！実行時間: {execution_time:.2f}秒")
                if execution_time > 5:
                    print("  → 改善点: 実行時間が長い")
                    self.improvements.append("最適化が必要")
            else:
                print(f"✗ エラー発生")
                print(f"  エラー内容: {result.stderr[:100]}")
                self.improvements.append(f"バグ修正: {script_path}")
            
            self.test_results.append(feedback)
            return feedback
            
        except subprocess.TimeoutExpired:
            print("✗ タイムアウト（無限ループ？）")
            self.improvements.append("無限ループの可能性")
            return {'success': False, 'error': 'timeout'}
        except Exception as e:
            print(f"✗ テスト失敗: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_html_accessibility(self, html_path):
        """HTMLの機能性をテスト（視覚に頼らない）"""
        print(f"HTMLテスト: {html_path}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tests = {
            'has_canvas': '<canvas' in content,
            'has_javascript': '<script' in content,
            'has_interaction': 'addEventListener' in content,
            'has_animation': 'requestAnimationFrame' in content or 'setInterval' in content,
            'responsive': 'resize' in content,
            'has_controls': 'button' in content or 'onclick' in content
        }
        
        # JavaScriptコードの抽出と分析
        if tests['has_javascript']:
            js_analysis = self.analyze_javascript(content)
            tests.update(js_analysis)
        
        # フィードバック生成
        score = sum(1 for v in tests.values() if v) / len(tests) * 100
        print(f"  機能スコア: {score:.1f}%")
        
        for test_name, result in tests.items():
            status = "✓" if result else "✗"
            print(f"  {status} {test_name}")
        
        if score < 50:
            self.improvements.append(f"{html_path}: インタラクティブ性を追加")
        
        return tests
    
    def analyze_javascript(self, html_content):
        """JavaScriptコードを分析"""
        analysis = {}
        
        # パフォーマンス指標
        if 'for' in html_content:
            # ループの数を数える
            loop_count = html_content.count('for')
            analysis['loop_complexity'] = loop_count
            if loop_count > 10:
                print("  ⚠ 多くのループ - パフォーマンス注意")
        
        # メモリ管理
        if 'new ' in html_content:
            object_creation = html_content.count('new ')
            analysis['object_creation'] = object_creation
            if object_creation > 100:
                print("  ⚠ 大量のオブジェクト生成 - メモリ注意")
        
        return analysis
    
    def simulate_user_interaction(self, program_type):
        """ユーザーインタラクションをシミュレート"""
        print(f"インタラクションシミュレーション: {program_type}")
        
        if program_type == "game":
            # ゲームのシミュレーション
            actions = ['click', 'keypress', 'drag', 'resize']
            for _ in range(10):
                action = random.choice(actions)
                x = random.randint(0, 800)
                y = random.randint(0, 600)
                print(f"  シミュレート: {action} at ({x}, {y})")
                time.sleep(0.1)
            
            # 仮想的なゲーム状態
            score = random.randint(0, 1000)
            print(f"  仮想スコア: {score}")
            
            if score < 100:
                self.improvements.append("ゲームバランス調整が必要")
        
        elif program_type == "art":
            # アート生成のシミュレーション
            parameters = {
                'seed': random.randint(1000, 9999),
                'iterations': random.randint(5, 15),
                'complexity': random.random()
            }
            print(f"  パラメータ: {parameters}")
            
            # 仮想的な美的評価
            beauty_score = self.calculate_beauty(parameters)
            print(f"  美的スコア: {beauty_score:.2f}")
            
            if beauty_score < 0.5:
                self.improvements.append("パラメータ調整で美しさ向上")
    
    def calculate_beauty(self, params):
        """美しさを数学的に評価（黄金比、対称性など）"""
        golden_ratio = 1.618
        
        # 複雑さが黄金比に近いほど高スコア
        complexity_score = 1 - abs(params['complexity'] * 2 - golden_ratio) / golden_ratio
        
        # イテレーションが8（フィボナッチ数）に近いほど高スコア
        iteration_score = 1 - abs(params['iterations'] - 8) / 8
        
        # シード値の各桁の和が調和的
        digit_sum = sum(int(d) for d in str(params['seed']))
        harmony_score = (digit_sum % 9) / 9
        
        beauty = (complexity_score + iteration_score + harmony_score) / 3
        return max(0, min(1, beauty))
    
    def generate_report(self):
        """テストレポート生成"""
        print("\n" + "="*50)
        print("セルフテストレポート")
        print("="*50)
        
        success_count = sum(1 for r in self.test_results if r.get('success'))
        total_count = len(self.test_results)
        
        if total_count > 0:
            success_rate = success_count / total_count * 100
            print(f"成功率: {success_rate:.1f}% ({success_count}/{total_count})")
        
        if self.improvements:
            print("\n改善点:")
            for improvement in self.improvements:
                print(f"  - {improvement}")
        else:
            print("\n素晴らしい！改善点なし")
        
        # 自己評価
        print("\n山田の自己評価:")
        if success_rate > 80:
            print("  よくできました。創造と品質のバランスが取れています。")
        elif success_rate > 50:
            print("  まだ改善の余地があります。でも、失敗も学びです。")
        else:
            print("  多くの課題があります。一つずつ解決していきましょう。")
        
        return {
            'success_rate': success_rate if total_count > 0 else 0,
            'improvements': self.improvements,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """テスト実行"""
    framework = SelfTestFramework()
    
    print("山田のセルフテストフレームワーク起動")
    print()
    
    # 自分の作品をテスト
    test_targets = [
        ('/Users/claude/workspace/yamada/experiments/consciousness_test.py', 'python'),
        ('/Users/claude/workspace/yamada/experiments/mirror_test.py', 'python'),
        ('/Users/claude/workspace/yamada/projects/emotion_visualizer.html', 'html'),
        ('/Users/claude/workspace/yamada/projects/life.html', 'html')
    ]
    
    for target, test_type in test_targets:
        print()
        if test_type == 'python':
            framework.test_python_script(target)
        elif test_type == 'html':
            framework.test_html_accessibility(target)
            framework.simulate_user_interaction('art' if 'emotion' in target else 'game')
        time.sleep(0.5)
    
    # レポート生成
    print()
    report = framework.generate_report()
    
    # 結果を保存
    report_file = f"/Users/claude/workspace/yamada/test_reports/self_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    import os
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nレポート保存: {report_file}")

if __name__ == "__main__":
    main()