# launchdサービス設定ガイド

## セットアップ方法

### 1. plistファイルをコピー
```bash
# 監視サービス
cp com.yamada.monitor.plist.backup ~/Library/LaunchAgents/com.yamada.monitor.plist

# Keep-Aliveサービス
cp com.yamada.keepalive.plist.backup ~/Library/LaunchAgents/com.yamada.keepalive.plist
```

### 2. サービスを起動
```bash
# 監視サービスを起動
launchctl load ~/Library/LaunchAgents/com.yamada.monitor.plist

# Keep-Aliveサービスを起動
launchctl load ~/Library/LaunchAgents/com.yamada.keepalive.plist
```

### 3. 状態確認
```bash
# サービス状態を確認
launchctl list | grep yamada

# ログを確認
tail -f ~/workspace/yamatter_checker/monitor.log
tail -f ~/workspace/yamatter_checker/keepalive.log
```

## サービス管理

### 停止
```bash
launchctl unload ~/Library/LaunchAgents/com.yamada.monitor.plist
launchctl unload ~/Library/LaunchAgents/com.yamada.keepalive.plist
```

### 再起動
```bash
# 停止してから起動
launchctl unload ~/Library/LaunchAgents/com.yamada.monitor.plist
launchctl load ~/Library/LaunchAgents/com.yamada.monitor.plist
```

## トラブルシューティング

### claudeコマンドが見つからない場合
plistファイル内のPATHに以下を追加：
```xml
<key>PATH</key>
<string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:/Users/claude/.nvm/versions/node/v20.19.4/bin</string>
```

### SSL証明書エラーの場合
claude_checker.pyに以下を追加済み：
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

## 自動起動の仕組み

- **com.yamada.monitor**: 5分ごとにYamatterをチェックして返信
- **com.yamada.keepalive**: 14分ごとにヘルスチェック（スリープ防止）

両サービスは：
- システム起動時に自動開始
- クラッシュ時に自動再起動
- 24時間365日稼働