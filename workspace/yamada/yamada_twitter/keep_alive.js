#!/usr/bin/env node
/**
 * Yamatter Keep-Alive スクリプト
 * Render.comなどの無料ホスティングでスリープを防ぐ
 */

const https = require('https');
const http = require('http');

// 設定
const config = {
    targetUrl: process.env.TARGET_URL || 'https://your-app.onrender.com',
    interval: 14 * 60 * 1000, // 14分（15分スリープの前に）
    healthCheckPath: '/api/health',
    useHttps: true
};

// ヘルスチェックエンドポイントにpingを送る
function pingServer() {
    const url = new URL(config.targetUrl + config.healthCheckPath);
    const protocol = url.protocol === 'https:' ? https : http;
    
    const options = {
        hostname: url.hostname,
        path: url.pathname,
        method: 'GET',
        timeout: 10000,
        headers: {
            'User-Agent': 'Yamatter-KeepAlive/1.0'
        }
    };
    
    console.log(`[${new Date().toISOString()}] Pinging ${url.href}`);
    
    const req = protocol.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
            console.log(`✅ Response: ${res.statusCode} - Server is alive`);
            if (res.statusCode !== 200) {
                console.log('Response body:', data);
            }
        });
    });
    
    req.on('error', (error) => {
        console.error(`❌ Ping failed:`, error.message);
    });
    
    req.on('timeout', () => {
        console.error('❌ Request timeout');
        req.destroy();
    });
    
    req.end();
}

// 定期的にpingを送信
function startKeepAlive() {
    console.log('🚀 Keep-Alive service started');
    console.log(`📍 Target: ${config.targetUrl}`);
    console.log(`⏰ Interval: ${config.interval / 1000 / 60} minutes`);
    console.log('');
    
    // 初回ping
    pingServer();
    
    // 定期実行
    setInterval(pingServer, config.interval);
}

// メイン処理
if (require.main === module) {
    // コマンドライン引数から対象URL取得
    if (process.argv[2]) {
        config.targetUrl = process.argv[2];
    }
    
    if (!config.targetUrl || config.targetUrl === 'https://your-app.onrender.com') {
        console.error('⚠️  対象URLを指定してください');
        console.log('使用方法: node keep_alive.js https://your-app.onrender.com');
        process.exit(1);
    }
    
    startKeepAlive();
}

module.exports = { pingServer, startKeepAlive };