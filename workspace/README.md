# Workspace Directory
作成日: 2025年8月28日

## 概要
このディレクトリは作業用フォルダです。
すべてのプロジェクトとツールはここで管理します。

## ディレクトリ構造
```
workspace/
├── voice-system/    # 音声会話システム
│   ├── mcp-voice-server.js  # MCPサーバー
│   └── v                     # 音声コマンド
└── README.md
```

## 重要な規則
**今後すべての作業はこのworkspaceディレクトリ内で行う**

### 理由
- ホームディレクトリを清潔に保つ
- プロジェクトの整理整頓
- 依存関係の管理が容易

## 現在稼働中のシステム

### 音声会話システム (voice-system/)
MCPベースの音声入出力サーバー

**使い方:**
```bash
# 音声入力
v

# テキスト読み上げ  
v talk "テキスト"

# サーバー起動（必要時）
cd ~/workspace/voice-system
node mcp-voice-server.js &
```

## 作業時の注意点
1. 新しいプロジェクトは`workspace/`内にサブディレクトリを作成
2. 一時ファイルも`workspace/tmp/`を使用
3. ドキュメントは各プロジェクトフォルダ内に保存