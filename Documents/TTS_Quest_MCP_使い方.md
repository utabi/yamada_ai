# TTS Quest MCP - VOICEVOX音声合成の使い方

## 概要
TTS Quest MCPは、Web API経由でVOICEVOXの音声合成を利用できるMCPサーバーです。
BigSurなど古いmacOSでも動作し、インストール不要で使えます。

## セットアップ手順

### 1. インストール
すでにインストール済みです：
```bash
cd ~/workspace/tts-quest-mcp
npm install
```

### 2. Claude Desktopの設定

Claude Desktopアプリで以下の設定を行います：

1. Claude Desktopを開く
2. 設定メニューから「Developer」セクションを開く
3. 「Edit Config」をクリック
4. 以下の内容を追加：

```json
{
  "mcpServers": {
    "tts-quest": {
      "command": "node",
      "args": ["/Users/claude/workspace/tts-quest-mcp/index.js"]
    }
  }
}
```

5. Claude Desktopを再起動

## 使用方法

### 基本的な音声合成
```
「こんにちは」と話して
```

### キャラクターを指定して話す
利用可能なキャラクター：
- zundamon（ずんだもん）
- metan（四国めたん）
- tsumugi（春日部つむぎ）
- hau（雨晴はう）
- ritsu（波音リツ）
- takehiro（玄野武宏）
- kotaro（白上虎太郎）
- ryusei（青山龍星）
- himari（冥鳴ひまり）
- nurserobot（ナースロボ_タイプT）
- whitecul（WhiteCUL）
- goki（後鬼）
- no7（No.7）
- sayo（小夜/SAYO）

例：
```
四国めたんの声で「おはようございます」と話して
```

### 通知メッセージ
作業の進捗を音声で通知：
```
「ファイルを作成しました」という完了通知を送って
```

通知タイプ：
- info: 情報
- start: 開始
- progress: 進行中
- complete: 完了
- error: エラー

### 利用可能なスピーカー一覧を表示
```
使えるスピーカーを教えて
```

## 特徴

✅ **基本無料** - APIキーなしでも利用可能（制限あり）
✅ **インストール不要** - Web API経由なのでVOICEVOXアプリ不要
✅ **OS非依存** - BigSurなど古いmacOSでも動作
✅ **14種類以上の音声** - 人気キャラクターの音声が使える
✅ **自動フォールバック** - API失敗時はmacOSのsayコマンドを使用

## 利用制限

### ポイント制度
- **1文字 = 1ポイント**を消費
- 毎日**午前9時（日本時間）**にポイントがリセット
- APIキーなしでも使えるが、速度制限と利用上限あり

### APIキーを取得するメリット
- より高速なレスポンス
- より多くの文字数が利用可能
- 24時間有効のサブキー発行可能

### APIキーの取得方法
1. https://su-shiki.com にアクセス
2. アカウント登録
3. 「VOICEVOX API」にチェックを入れる
4. 発行されたAPIキーをMCPサーバーに設定

## トラブルシューティング

### 音声が再生されない場合
1. インターネット接続を確認
2. `afplay`コマンドが使えるか確認：
   ```bash
   which afplay
   ```

### APIエラーが出る場合
TTS Quest APIの状態を確認：
https://api.tts.quest/v3/voicevox/synthesis?speaker=3&text=test

## 注意事項
- 日本語のみ対応
- インターネット接続が必要
- TTS Quest APIの利用規約に従ってください
- 音声の商用利用は各キャラクターの利用規約を確認してください