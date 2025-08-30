# SuperWhisper設定確認手順

## ⚠️ Option+Spaceが動作しない場合の対処法

### 1. SuperWhisperが起動しているか確認

**確認方法:**
- メニューバー（画面上部）にSuperWhisperのアイコン（マイクのアイコン）があるか確認
- ない場合：
  1. Finder → アプリケーション → SuperWhisper をダブルクリック
  2. または Spotlight（Cmd+Space）で「SuperWhisper」を検索して起動

### 2. 初回設定の確認

**SuperWhisperを初めて起動した場合:**

1. **Welcome画面**
   - 「Continue」をクリック

2. **権限の許可（重要！）**
   - **Microphone Access（マイクアクセス）**: 「Open System Settings」→ 許可
   - **Accessibility（アクセシビリティ）**: 「Open System Settings」→ 許可
   
   両方の権限が必須です！

3. **ホットキー設定**
   - デフォルトは Option+Space
   - 競合する場合は変更可能

### 3. メニューバーから設定確認

1. **メニューバーのSuperWhisperアイコンをクリック**
2. **「Settings」または「Preferences」を選択**
3. **確認項目:**
   - Hotkey: 設定されているか
   - Mode: 「Type to active app」が選択されているか
   - Language: Japanese が含まれているか

### 4. システム環境設定での権限確認

**手動で確認する方法:**

1. **Appleメニュー → システム環境設定**
2. **セキュリティとプライバシー**
3. **プライバシー タブ**

**確認項目:**

#### マイク
- SuperWhisper にチェック ✓

#### アクセシビリティ
- SuperWhisper にチェック ✓

### 5. ホットキーの競合確認

**他のアプリと競合している可能性:**

1. **システム環境設定 → キーボード → ショートカット**
2. Option+Space を使っている他のショートカットがないか確認
3. 競合があれば無効化するか、SuperWhisperのホットキーを変更

### 6. 代替ホットキーの設定

**SuperWhisperのホットキー変更方法:**

1. メニューバーのSuperWhisperアイコン → Settings
2. Hotkey セクション
3. 「Record Shortcut」をクリック
4. 新しいキーコンビネーション（例：Ctrl+Shift+Space）を押す

### 7. 手動で音声入力を開始

**ホットキーが動作しない場合の代替方法:**

1. メニューバーのSuperWhisperアイコンをクリック
2. 「Start Listening」を選択
3. 話す

### 8. アプリの再起動

1. メニューバーのSuperWhisperアイコン → Quit
2. アプリケーションフォルダから再度起動
3. 権限を再確認

## 🔧 それでも動作しない場合

### Macを再起動
- 権限設定が正しく適用されない場合があるため

### SuperWhisperを再インストール
1. アプリケーションフォルダからSuperWhisperを削除
2. App Storeから再インストール

## 📝 動作確認方法

1. テキストエディタ（メモ帳など）を開く
2. カーソルをテキスト入力エリアに置く
3. 設定したホットキーを押す
4. マイクアイコンや録音インジケータが表示される
5. 話す
6. テキストが自動入力される