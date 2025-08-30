# TTS Quest APIキー設定方法

## APIキーが必要な理由
- **無料枠の制限を超えて使いたい場合**
- **より高速なレスポンスが必要な場合**
- **1日の利用文字数を増やしたい場合**

## APIキーの取得方法

### 方法1: su-shiki.comから取得（推奨）
1. https://su-shiki.com にアクセス
2. アカウント登録
3. **「VOICEVOX API」にチェックを入れる**（重要！）
4. APIキーが発行される

### 方法2: TTS Quest公式から取得
GitHubのREADMEに記載されている方法に従って取得
https://github.com/ts-klassen/ttsQuestV3Voicevox

## APIキーの設定方法

### 方法1: 環境変数で設定（推奨）

#### ターミナルで一時的に設定
```bash
export TTS_QUEST_API_KEY="your-api-key-here"
```

#### 永続的に設定（.zshrcに追加）
```bash
echo 'export TTS_QUEST_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 方法2: Claude Desktopの設定で指定

Claude Desktopの設定ファイルを編集：
```json
{
  "mcpServers": {
    "tts-quest": {
      "command": "node",
      "args": ["/Users/claude/workspace/tts-quest-mcp/index.js"],
      "env": {
        "TTS_QUEST_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 方法3: .envファイルで設定

1. プロジェクトフォルダに`.env`ファイルを作成：
```bash
cd ~/workspace/tts-quest-mcp
echo 'TTS_QUEST_API_KEY=your-api-key-here' > .env
```

2. dotenvパッケージをインストール：
```bash
npm install dotenv
```

3. index.jsの最初に追加：
```javascript
require('dotenv').config();
```

## APIキーの確認

設定が正しいか確認：
```bash
echo $TTS_QUEST_API_KEY
```

## 注意事項

### セキュリティ
- **APIキーは絶対に公開しない**
- GitHubにコミットしない（.gitignoreに.envを追加）
- 他人と共有しない

### 利用制限
- APIキーがあってもポイント制限あり
- 1文字 = 1ポイント消費
- 毎日午前9時（日本時間）にリセット

### トラブルシューティング

#### APIキーが無効と表示される
- キーが正しくコピーされているか確認
- 「VOICEVOX API」にチェックを入れて登録したか確認
- SHA256ハッシュの登録が必要な場合がある

#### 速度が改善されない
- APIキーが正しく環境変数に設定されているか確認
- Claude Desktopを再起動

## 現在の設定状況

現在、APIキーは**設定されていません**。
無料枠で利用中です。

APIキーを取得して設定すると：
- ✅ より多くの文字数が利用可能
- ✅ レスポンス速度が向上
- ✅ 安定した利用が可能

## お問い合わせ

APIキーに関する詳細は：
- su-shiki.com: webmaster@su-shiki.com
- TTS Quest GitHub: https://github.com/ts-klassen/ttsQuestV3Voicevox