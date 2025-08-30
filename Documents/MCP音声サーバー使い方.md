# MCP音声サーバー 使い方
作成日: 2025年8月28日

## 🎯 概要
Model Context Protocol (MCP) を使用した音声入出力サーバーです。
HTTPとWebSocket両方で通信可能。

## 🚀 サーバー起動

### 起動コマンド
```bash
node ~/mcp-voice-server.js
```

### 現在のステータス
- ✅ **サーバー稼働中**
- HTTP: http://localhost:3456
- WebSocket: ws://localhost:3457

## 📡 使い方

### 1. テキストを音声で読み上げる
```bash
curl -X POST http://localhost:3456/speak \
  -H 'Content-Type: application/json' \
  -d '{"text":"読み上げたいテキスト"}'
```

### 2. 音声入力を受け付ける
```bash
curl http://localhost:3456/listen
```
- 音声入力ダイアログが表示される
- fnキー2回で音声入力
- 結果がJSONで返される

### 3. サーバーステータス確認
```bash
curl http://localhost:3456/status
```

## 🔌 WebSocket接続

### 接続
```javascript
const ws = new WebSocket('ws://localhost:3457');
```

### メッセージ送信
```javascript
// 音声読み上げ
ws.send(JSON.stringify({ type: 'speak', text: 'こんにちは' }));

// 音声入力
ws.send(JSON.stringify({ type: 'listen' }));
```

## 🎤 Claude Codeとの連携

残念ながら、現在のClaude CodeにはMCP音声拡張が組み込まれていません。
しかし、以下の方法で連携可能：

### 方法1: curlコマンドで直接操作
```bash
# 私の返答を読み上げ
curl -X POST http://localhost:3456/speak -H 'Content-Type: application/json' -d '{"text":"返答内容"}'

# 音声入力して私に送信
curl http://localhost:3456/listen
```

### 方法2: ブラウザ拡張を作成
WebSocketで接続してリアルタイム連携

### 方法3: ローカルプロキシ
Claude Codeの入出力を監視して自動的に音声変換

## 💡 便利なエイリアス

`.bash_profile`に追加：
```bash
# 音声読み上げ
alias say-claude='function _say() { curl -X POST http://localhost:3456/speak -H "Content-Type: application/json" -d "{\"text\":\"$*\"}"; }; _say'

# 音声入力
alias hear-claude='curl http://localhost:3456/listen | jq -r .text'
```

使い方：
```bash
say-claude こんにちは、テストです
hear-claude
```

## 🔧 トラブルシューティング

### サーバーが起動しない
```bash
# プロセス確認
ps aux | grep mcp-voice-server

# ポート確認
lsof -i :3456
```

### 音声が出ない
- 音量設定を確認
- `say`コマンドが動作するか確認

### 音声入力できない
- システム環境設定で音声入力を有効化
- fnキー設定を確認

## 📝 まとめ

MCPサーバーは稼働中です。以下のコマンドで音声会話が可能：

1. **私の返答を読み上げる:**
   ```bash
   curl -X POST http://localhost:3456/speak -H 'Content-Type: application/json' -d '{"text":"ここに私の返答"}'
   ```

2. **あなたの音声を入力:**
   ```bash
   curl http://localhost:3456/listen
   ```

完全な自動連携にはClaude側のMCP対応が必要ですが、
現在でもコマンドで効率的に音声会話できます！