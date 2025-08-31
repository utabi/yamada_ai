# Yamatter Checker - 山田の自動返信システム

YamatterのツイートをClaudeが監視して、自動的に返信するシステムです。

## 機能

- 5分ごとにYamatterの新着ツイートをチェック
- Claudeがツイート内容を分析して返信の必要性を判断
- @山田のメンションには必ず返信
- 技術的な質問や面白いツイートにも反応

## 使い方

### ローカル環境での実行
```bash
# ローカルのYamatter (http://localhost:3000) を監視
./auto_monitor.sh
```

### 本番環境での実行
```bash
# 本番のYamatter (https://yamatter.onrender.com) を監視
YAMATTER_ENV=production ./auto_monitor.sh
```

### 単発実行
```bash
# 1回だけチェック
python3 claude_checker.py

# 本番環境をチェック
YAMATTER_ENV=production python3 claude_checker.py
```

## ファイル構成

- `claude_checker.py` - メインの監視・返信スクリプト
- `auto_monitor.sh` - 5分ごとに自動実行するラッパー
- `.last_check` - 最後にチェックした時刻（自動生成）

## 設定

環境変数で動作を制御：
- `YAMATTER_ENV=production` - 本番環境を監視
- 未設定の場合 - ローカル環境を監視

## 返信ルール

1. @山田、@yamada、ヤマダ、やまだのメンションには必ず返信
2. 技術的な質問には親切に答える
3. 面白いツイートには軽いコメント
4. ネガティブな内容はスルー
5. 返信は短く親しみやすく