#!/usr/bin/env node

/**
 * MCP Voice Server - Claude音声会話サーバー
 * Model Context Protocol (MCP)を使用した音声入出力サーバー
 */

const { spawn } = require('child_process');
const express = require('express');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

// サーバー設定
const PORT = 3456;
const app = express();
app.use(express.json());

// WebSocketサーバー
const wss = new WebSocket.Server({ port: PORT + 1 });

// 音声合成（読み上げ）
function speak(text) {
    return new Promise((resolve, reject) => {
        const say = spawn('say', ['-v', 'Kyoko', text]);
        say.on('close', (code) => {
            if (code === 0) {
                console.log(`✅ 読み上げ完了: ${text}`);
                resolve();
            } else {
                reject(new Error(`say command failed with code ${code}`));
            }
        });
    });
}

// 音声認識（AppleScript経由）
function getVoiceInput() {
    return new Promise((resolve, reject) => {
        const script = `
        display dialog "🎤 話してください（fnキー2回で音声入力）:" default answer "" buttons {"キャンセル", "送信"} default button "送信" with title "音声入力"
        if button returned of result is "送信" then
            return text returned of result
        else
            return ""
        end if
        `;
        
        const osascript = spawn('osascript', ['-e', script]);
        let output = '';
        
        osascript.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        osascript.on('close', (code) => {
            if (code === 0) {
                resolve(output.trim());
            } else {
                resolve('');
            }
        });
    });
}

// HTTPエンドポイント

// 音声読み上げ
app.post('/speak', async (req, res) => {
    const { text } = req.body;
    if (!text) {
        return res.status(400).json({ error: 'Text is required' });
    }
    
    try {
        await speak(text);
        res.json({ success: true, message: 'Speech completed' });
        
        // WebSocketで通知
        wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(JSON.stringify({ type: 'spoken', text }));
            }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// 音声入力
app.get('/listen', async (req, res) => {
    try {
        const input = await getVoiceInput();
        if (input) {
            res.json({ success: true, text: input });
            
            // WebSocketで通知
            wss.clients.forEach(client => {
                if (client.readyState === WebSocket.OPEN) {
                    client.send(JSON.stringify({ type: 'heard', text: input }));
                }
            });
        } else {
            res.json({ success: false, message: 'No input received' });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ステータス確認
app.get('/status', (req, res) => {
    res.json({ 
        status: 'running',
        version: '1.0.0',
        websocket_clients: wss.clients.size
    });
});

// WebSocket接続処理
wss.on('connection', (ws) => {
    console.log('🔌 WebSocketクライアント接続');
    
    ws.send(JSON.stringify({ 
        type: 'connected', 
        message: 'MCP Voice Server connected' 
    }));
    
    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message);
            
            switch(data.type) {
                case 'speak':
                    await speak(data.text);
                    ws.send(JSON.stringify({ type: 'spoken', text: data.text }));
                    break;
                    
                case 'listen':
                    const input = await getVoiceInput();
                    ws.send(JSON.stringify({ type: 'heard', text: input }));
                    break;
                    
                default:
                    ws.send(JSON.stringify({ type: 'error', message: 'Unknown command' }));
            }
        } catch (error) {
            ws.send(JSON.stringify({ type: 'error', message: error.message }));
        }
    });
    
    ws.on('close', () => {
        console.log('🔌 WebSocketクライアント切断');
    });
});

// サーバー起動
app.listen(PORT, () => {
    console.log('🎙️ MCP Voice Server');
    console.log(`📡 HTTP: http://localhost:${PORT}`);
    console.log(`🔌 WebSocket: ws://localhost:${PORT + 1}`);
    console.log('');
    console.log('エンドポイント:');
    console.log('  POST /speak - テキストを音声で読み上げ');
    console.log('  GET  /listen - 音声入力を受け付け');
    console.log('  GET  /status - サーバーステータス');
    console.log('');
    console.log('✅ サーバー起動完了');
});

// グレースフルシャットダウン
process.on('SIGINT', () => {
    console.log('\n👋 サーバー終了中...');
    wss.clients.forEach(client => {
        client.close();
    });
    process.exit(0);
});