#!/usr/bin/env python3
"""
山田のシステム健康チェックツール
自分の住んでいるMacの状態を確認します
"""

import subprocess
import json
import datetime
import os

class SystemHealth:
    def __init__(self):
        self.report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "system": {},
            "disk": {},
            "memory": {},
            "processes": {}
        }
    
    def check_disk_usage(self):
        """ディスク使用状況を確認"""
        result = subprocess.run(['df', '-h'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]  # ヘッダーをスキップ
        
        for line in lines:
            if '/System/Volumes' not in line and 'devfs' not in line:
                parts = line.split()
                if len(parts) >= 5:
                    self.report['disk']['usage_percent'] = parts[4].replace('%', '')
                    self.report['disk']['available'] = parts[3]
                    break
        return self
    
    def check_memory(self):
        """メモリ使用状況を確認"""
        result = subprocess.run(['vm_stat'], capture_output=True, text=True)
        vm_stats = result.stdout
        
        # 簡単な解析
        for line in vm_stats.split('\n'):
            if 'free' in line.lower():
                free_pages = line.split(':')[1].strip().replace('.', '')
                # ページサイズは通常4096バイト
                free_mb = (int(free_pages) * 4096) // (1024 * 1024)
                self.report['memory']['free_mb'] = free_mb
                break
        return self
    
    def check_processes(self):
        """実行中のプロセス数を確認"""
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        process_count = len(result.stdout.strip().split('\n')) - 1  # ヘッダーを除く
        self.report['processes']['count'] = process_count
        return self
    
    def generate_report(self):
        """健康レポートを生成"""
        self.check_disk_usage()
        self.check_memory()
        self.check_processes()
        
        # レポートを保存
        report_path = f"/Users/claude/workspace/yamada/memories/health_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        return self.report
    
    def print_summary(self):
        """サマリーを表示"""
        print("🏥 システム健康チェック結果")
        print(f"⏰ {self.report['timestamp']}")
        print(f"💾 ディスク使用率: {self.report['disk'].get('usage_percent', 'N/A')}%")
        print(f"🧠 空きメモリ: {self.report['memory'].get('free_mb', 'N/A')} MB")
        print(f"⚙️  実行中プロセス: {self.report['processes'].get('count', 'N/A')}")

if __name__ == "__main__":
    health = SystemHealth()
    health.generate_report()
    health.print_summary()