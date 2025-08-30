# VOICEVOX MCP セットアップ完了

## 日時
2025-08-28

## インストール内容
「ずんだもん」の音声でClaude Codeのタスク進捗を通知するVOICEVOX MCPを導入しました。

## 実施した作業

1. **パッケージのインストール**
   ```bash
   npm install -g @t09tanaka/mcp-simple-voicevox
   ```

2. **MCP設定の追加**
   `/Users/claude/.claude/settings.local.json`に以下の設定を追加：
   ```json
   "mcpServers": {
     "voicevox": {
       "command": "npx",
       "args": ["@t09tanaka/mcp-simple-voicevox"]
     }
   }
   ```

## 使用方法
Claude CLIを再起動すると、タスク進捗が「ずんだもん」の音声で通知されるようになります。

## 参考記事
https://zenn.dev/t09tanaka/articles/ff2983a52959f1