# 音声入力システム - Zenn記事対応版
作成日: 2025年8月28日

## 📖 Zenn記事の要点

記事で紹介されていたSuperWhisperの主要機能:
- ローカル処理でプライバシー保護
- 自動クリップボード保存
- 技術用語の自動変換（例: ゲットユーザーアイディー → getUserId）

## 🎯 実装した機能

### 1. macOS標準音声入力の活用
**設定済み項目:**
- `defaults write com.apple.HIToolbox AppleDictationAutoEnable -bool true`
- 音声入力を有効化

### 2. 作成したツール

#### A. 基本音声入力起動 (`voice_dictation.sh`)
```bash
~/voice_dictation.sh
```
- fnキー押下をシミュレート
- 3秒カウントダウン後に音声入力起動

#### B. スマート音声入力 (`smart_voice_input.py`)
```bash
python3 ~/smart_voice_input.py
```
- 連続音声入力モード
- 技術用語の自動変換
- クリップボード自動保存
- 入力履歴記録

#### C. 簡単音声入力 (`easy_voice.sh`)
```bash
~/easy_voice.sh
# またはエイリアス
v
```
- GUIダイアログで簡単入力
- 自動クリップボード保存

## 🚀 使い方

### 方法1: システム環境設定から有効化
1. システム環境設定 → キーボード → 音声入力
2. 音声入力をオン
3. ショートカットを設定（fnキー2回など）

### 方法2: コマンドで起動
```bash
# 音声入力を起動
~/voice_dictation.sh

# スマート音声入力（技術用語変換付き）
python3 ~/smart_voice_input.py

# 簡単GUI入力
v
```

## 🔧 技術用語の自動変換

`smart_voice_input.py`では以下の変換を自動実行:

| 音声入力 | 変換後 |
|---------|--------|
| ゲットユーザーアイディー | getUserId |
| セットタイムアウト | setTimeout |
| コンソールログ | console.log |
| ドキュメントゲットエレメントバイアイディー | document.getElementById |

## 📝 設定確認コマンド

```bash
# 音声入力設定の確認
defaults read com.apple.HIToolbox AppleDictationAutoEnable

# マイク権限のリセット（必要時）
tccutil reset Microphone
```

## ⚠️ トラブルシューティング

### fnキーが動作しない場合
- システム環境設定で音声入力のショートカットを確認
- Touch Bar搭載Macの場合は設定が異なる可能性

### 音声入力が起動しない場合
1. プライバシー設定でマイクアクセスを確認
2. 音声入力を一度オフにしてから再度オン
3. Macを再起動

## 💡 SuperWhisperとの比較

| 機能 | SuperWhisper | 本実装 |
|------|-------------|--------|
| ローカル処理 | ✅ | ✅ (拡張音声入力使用時) |
| クリップボード保存 | ✅ | ✅ |
| 技術用語変換 | ✅ | ✅ (基本的な変換) |
| 料金 | 有料 | 無料 |

## 🎉 まとめ

Zenn記事で紹介されていた音声入力の主要機能を、macOS標準機能とカスタムスクリプトで実現しました。SuperWhisperには及ばない部分もありますが、基本的な音声入力作業には十分対応できます。