#!/usr/bin/env node

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { CallToolRequestSchema, ListToolsRequestSchema } = require('@modelcontextprotocol/sdk/types.js');
const https = require('https');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * TTS Quest Voice MCP Server
 * VOICEVOXの音声をWeb API経由で再生するMCPサーバー
 */
class TtsQuestMcpServer {
  constructor() {
    this.server = new Server(
      {
        name: 'tts-quest-mcp',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // VOICEVOXのスピーカー設定
    this.speakers = {
      'zundamon': 3,
      'metan': 2,
      'tsumugi': 14,
      'hau': 10,
      'ritsu': 9,
      'takehiro': 11,
      'kotaro': 12,
      'ryusei': 13,
      'himari': 14,
      'nurserobot': 47,
      'whitecul': 52,
      'goki': 53,
      'no7': 54,
      'sayo': 46,
    };
    
    this.currentSpeaker = 14; // デフォルトは冥鳴ひまり
    this.tempDir = '/tmp/tts_quest_audio';
    
    // APIキー（環境変数から取得）
    this.apiKey = process.env.TTS_QUEST_API_KEY || null;
    
    // 一時ディレクトリ作成
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir, { recursive: true });
    }

    this.setupHandlers();
  }

  setupHandlers() {
    // ツール一覧を返す
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'speak',
          description: 'Text to speech using VOICEVOX via TTS Quest API',
          inputSchema: {
            type: 'object',
            properties: {
              text: {
                type: 'string',
                description: 'Text to speak in Japanese',
              },
              speaker: {
                type: 'string',
                description: 'Speaker name (optional): zundamon, metan, tsumugi, etc.',
              },
            },
            required: ['text'],
          },
        },
        {
          name: 'notify',
          description: 'Send notification with voice',
          inputSchema: {
            type: 'object',
            properties: {
              message: {
                type: 'string',
                description: 'Notification message',
              },
              type: {
                type: 'string',
                description: 'Notification type: info, start, progress, complete, error',
                enum: ['info', 'start', 'progress', 'complete', 'error'],
              },
            },
            required: ['message'],
          },
        },
        {
          name: 'list_speakers',
          description: 'List available VOICEVOX speakers',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
      ],
    }));

    // ツール実行を処理
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      switch (request.params.name) {
        case 'speak':
          return await this.handleSpeak(request.params.arguments);
        case 'notify':
          return await this.handleNotify(request.params.arguments);
        case 'list_speakers':
          return this.handleListSpeakers();
        default:
          throw new Error(`Unknown tool: ${request.params.name}`);
      }
    });
  }

  async handleSpeak(args) {
    const { text, speaker } = args;
    const speakerId = speaker ? (this.speakers[speaker] || this.currentSpeaker) : this.currentSpeaker;
    
    try {
      const audioUrl = await this.synthesize(text, speakerId);
      await this.playAudioFromUrl(audioUrl);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ Spoke: "${text}" (Speaker: ${this.getSpeakerName(speakerId)})`,
          },
        ],
      };
    } catch (error) {
      // フォールバックとしてmacOSのsayコマンドを使用
      exec(`say -v Kyoko "${text}"`);
      
      return {
        content: [
          {
            type: 'text',
            text: `⚠️ TTS API failed, used fallback: "${text}"`,
          },
        ],
      };
    }
  }

  async handleNotify(args) {
    const { message, type = 'info' } = args;
    
    const prefixes = {
      'start': '作業を開始します。',
      'progress': '',
      'complete': '完了しました。',
      'error': 'エラーが発生しました。',
      'info': ''
    };

    const text = `${prefixes[type] || ''}${message}`;
    
    try {
      const audioUrl = await this.synthesize(text, this.currentSpeaker);
      await this.playAudioFromUrl(audioUrl);
      
      return {
        content: [
          {
            type: 'text',
            text: `🔔 ${type.toUpperCase()}: ${message}`,
          },
        ],
      };
    } catch (error) {
      exec(`say -v Kyoko "${text}"`);
      
      return {
        content: [
          {
            type: 'text',
            text: `⚠️ Notification (fallback): ${message}`,
          },
        ],
      };
    }
  }

  handleListSpeakers() {
    const speakerList = Object.entries(this.speakers)
      .map(([name, id]) => `• ${name} (ID: ${id})`)
      .join('\n');
    
    return {
      content: [
        {
          type: 'text',
          text: `Available VOICEVOX Speakers:\n${speakerList}\n\nCurrent speaker: ${this.getSpeakerName(this.currentSpeaker)}`,
        },
      ],
    };
  }

  getSpeakerName(id) {
    for (const [name, speakerId] of Object.entries(this.speakers)) {
      if (speakerId === id) return name;
    }
    return `ID: ${id}`;
  }

  async synthesize(text, speakerId) {
    const encodedText = encodeURIComponent(text);
    let apiUrl = `https://api.tts.quest/v3/voicevox/synthesis?speaker=${speakerId}&text=${encodedText}`;
    
    // APIキーがある場合は追加
    if (this.apiKey) {
      apiUrl += `&key=${this.apiKey}`;
    }
    
    return new Promise((resolve, reject) => {
      https.get(apiUrl, (response) => {
        let data = '';
        
        response.on('data', (chunk) => {
          data += chunk;
        });
        
        response.on('end', () => {
          try {
            const result = JSON.parse(data);
            
            if (result.success === false) {
              reject(new Error(result.errorMessage || 'API Error'));
              return;
            }
            
            resolve(result.mp3StreamingUrl);
          } catch (error) {
            reject(error);
          }
        });
      }).on('error', reject);
    });
  }

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
            fs.unlink(filename, () => {});
            
            if (error) {
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

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('TTS Quest MCP Server running...');
  }
}

// メイン実行
if (require.main === module) {
  const server = new TtsQuestMcpServer();
  server.run().catch(console.error);
}

module.exports = TtsQuestMcpServer;