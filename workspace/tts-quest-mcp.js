#!/usr/bin/env node

const https = require('https');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * TTS Quest APIを使用した音声合成MCPサーバー
 * https://api.tts.quest/v3/voicevox/synthesis
 */
class TtsQuestMCP {
  constructor() {
    // VOICEVOXのスピーカーID
    this.speakers = {
      'ずんだもん': 3,
      '四国めたん': 2, 
      '春日部つむぎ': 14,
      '雨晴はう': 10,
      '波音リツ': 9,
      '玄野武宏': 11,
      '白上虎太郎': 12,
      '青山龍星': 13,
      '冥鳴ひまり': 14,
      'ナースロボ_タイプT': 47,
      'WhiteCUL': 52,
      '後鬼': 53,
      'No.7': 54,
      '小夜/SAYO': 46,
    };
    
    this.currentSpeaker = 3; // デフォルトはずんだもん
    this.tempDir = '/tmp/tts_quest_audio';
    
    // 一時ディレクトリ作成
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir, { recursive: true });
    }
  }

  /**
   * テキストを音声合成してストリーミング再生
   */
  async speak(text, speakerId = null) {
    const speaker = speakerId || this.currentSpeaker;
    const encodedText = encodeURIComponent(text);
    const apiUrl = `https://api.tts.quest/v3/voicevox/synthesis?speaker=${speaker}&text=${encodedText}`;
    
    console.log(`[TTS] Speaking: "${text}" (Speaker ID: ${speaker})`);
    
    return new Promise((resolve, reject) => {
      https.get(apiUrl, (response) => {
        let data = '';
        
        response.on('data', (chunk) => {
          data += chunk;
        });
        
        response.on('end', async () => {
          try {
            const result = JSON.parse(data);
            
            if (result.success === false) {
              console.error('API Error:', result);
              reject(new Error(result.errorMessage || 'API Error'));
              return;
            }
            
            // MP3ストリーミングURLを取得
            const mp3Url = result.mp3StreamingUrl;
            
            if (!mp3Url) {
              reject(new Error('No streaming URL in response'));
              return;
            }
            
            // MP3をダウンロードして再生
            await this.playAudioFromUrl(mp3Url);
            resolve();
            
          } catch (error) {
            console.error('Error parsing response:', error);
            reject(error);
          }
        });
      }).on('error', (error) => {
        console.error('Request error:', error);
        reject(error);
      });
    });
  }

  /**
   * URLから音声をダウンロードして再生
   */
  async playAudioFromUrl(url) {
    return new Promise((resolve, reject) => {
      const filename = path.join(this.tempDir, `tts_${Date.now()}.mp3`);
      const file = fs.createWriteStream(filename);
      
      https.get(url, (response) => {
        response.pipe(file);
        
        file.on('finish', () => {
          file.close();
          
          // macOSのafplayコマンドで再生
          exec(`afplay "${filename}"`, (error) => {
            // 再生後にファイル削除
            fs.unlink(filename, () => {});
            
            if (error) {
              console.error('Playback error:', error);
              reject(error);
            } else {
              resolve();
            }
          });
        });
      }).on('error', (error) => {
        fs.unlink(filename, () => {});
        reject(error);
      });
    });
  }

  /**
   * MCPからの通知を処理
   */
  async notify(message, type = 'info') {
    const prefixes = {
      'start': '作業を開始します。',
      'progress': '',
      'complete': '完了しました。',
      'error': 'エラーが発生しました。',
      'info': ''
    };

    const text = `${prefixes[type] || ''}${message}`;
    console.log(`[${new Date().toISOString()}] ${type}: ${message}`);
    
    try {
      await this.speak(text);
    } catch (error) {
      console.error('Failed to speak:', error);
      // フォールバックとしてmacOSのsayコマンドを使用
      exec(`say -v Kyoko "${text}"`);
    }
  }

  /**
   * スピーカーを変更
   */
  setSpeaker(speakerNameOrId) {
    if (typeof speakerNameOrId === 'number') {
      this.currentSpeaker = speakerNameOrId;
    } else if (this.speakers[speakerNameOrId]) {
      this.currentSpeaker = this.speakers[speakerNameOrId];
    } else {
      console.error(`Unknown speaker: ${speakerNameOrId}`);
    }
  }

  /**
   * 利用可能なスピーカーをリスト
   */
  listSpeakers() {
    console.log('Available speakers:');
    for (const [name, id] of Object.entries(this.speakers)) {
      console.log(`  ${name}: ${id}`);
    }
  }
}

// テスト実行
if (require.main === module) {
  const mcp = new TtsQuestMCP();
  
  console.log('Testing TTS Quest API...');
  mcp.listSpeakers();
  
  const testMessages = [
    { msg: 'こんにちは、TTS Questのテストです', type: 'info' },
    { msg: 'ファイルの作成を開始します', type: 'start' },
    { msg: '処理中です', type: 'progress' },
    { msg: 'すべての処理が完了しました', type: 'complete' },
  ];

  // 順番にテスト
  (async () => {
    for (const { msg, type } of testMessages) {
      try {
        await mcp.notify(msg, type);
        // 少し待つ
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        console.error('Test failed:', error);
      }
    }
    console.log('Test completed!');
  })();
}

module.exports = TtsQuestMCP;