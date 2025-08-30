#!/usr/bin/env node

const { exec } = require('child_process');

// MCPサーバーとして簡易的な音声通知を実装
class SimpleSayMCP {
  constructor() {
    this.voice = 'Kyoko'; // 日本語音声
  }

  speak(text) {
    // 英単語をカタカナに変換する簡易マッピング
    const replacements = {
      'completed': '完了しました',
      'started': '開始しました',
      'processing': '処理中です',
      'error': 'エラーです',
      'success': '成功しました',
      'failed': '失敗しました',
      'file': 'ファイル',
      'directory': 'ディレクトリ',
      'created': '作成しました',
      'updated': '更新しました',
      'deleted': '削除しました',
      'found': '見つかりました',
      'not found': '見つかりません',
      'running': '実行中です',
      'stopped': '停止しました',
      'building': 'ビルド中です',
      'installing': 'インストール中です',
      'testing': 'テスト中です',
    };

    let processedText = text.toLowerCase();
    for (const [eng, jpn] of Object.entries(replacements)) {
      processedText = processedText.replace(new RegExp(eng, 'g'), jpn);
    }

    // sayコマンドで音声出力
    exec(`say -v ${this.voice} "${processedText}"`, (error) => {
      if (error) {
        console.error('Speech error:', error);
      }
    });
  }

  // MCPからの通知を受け取る
  notify(message, type = 'info') {
    const prefix = {
      'start': '作業を',
      'progress': '',
      'complete': '作業が',
      'error': 'エラー: ',
      'info': ''
    };

    const text = `${prefix[type] || ''}${message}`;
    console.log(`[${new Date().toISOString()}] ${type}: ${message}`);
    this.speak(text);
  }
}

// スタンドアロンで実行する場合のテスト
if (require.main === module) {
  const mcp = new SimpleSayMCP();
  
  // テストメッセージ
  const testMessages = [
    { msg: 'タスクを開始します', type: 'start' },
    { msg: 'ファイルを作成中です', type: 'progress' },
    { msg: '処理が完了しました', type: 'complete' },
  ];

  // 3秒ごとにテストメッセージを再生
  let index = 0;
  const interval = setInterval(() => {
    if (index < testMessages.length) {
      const { msg, type } = testMessages[index];
      mcp.notify(msg, type);
      index++;
    } else {
      clearInterval(interval);
      console.log('テスト完了');
    }
  }, 3000);
}

module.exports = SimpleSayMCP;