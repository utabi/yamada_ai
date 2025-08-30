const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const compression = require('compression');

const Database = require('./models/Database');
const TwitterAPI = require('./routes/twitter');
const AuthAPI = require('./routes/auth');

class YamadaTwitterServer {
    constructor() {
        this.app = express();
        this.server = http.createServer(this.app);
        this.io = socketIo(this.server, {
            cors: {
                origin: process.env.NODE_ENV === 'production' 
                    ? process.env.ALLOWED_ORIGINS?.split(',') 
                    : ["http://localhost:3000", "http://127.0.0.1:3000"],
                methods: ["GET", "POST"]
            }
        });
        
        this.db = new Database();
        this.port = process.env.PORT || 3000;
        this.connectedUsers = new Map();
        
        this.setupMiddleware();
        this.setupRoutes();
        this.setupSocketIO();
        this.setupErrorHandling();
    }
    
    setupMiddleware() {
        // セキュリティ（開発環境では緩和）
        if (process.env.NODE_ENV === 'production') {
            this.app.use(helmet({
                contentSecurityPolicy: {
                    directives: {
                        defaultSrc: ["'self'"],
                        styleSrc: ["'self'", "'unsafe-inline'"],
                        scriptSrc: ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com"],
                        imgSrc: ["'self'", "data:", "https:"],
                        connectSrc: ["'self'", "ws:", "wss:"],
                    },
                },
            }));
        } else {
            // 開発環境ではセキュリティヘッダーを無効化
            this.app.use(helmet({
                contentSecurityPolicy: false,
                crossOriginEmbedderPolicy: false,
                crossOriginOpenerPolicy: false,
                originAgentCluster: false,
                crossOriginResourcePolicy: false
            }));
        }
        
        // CORS設定
        this.app.use(cors({
            origin: process.env.NODE_ENV === 'production'
                ? process.env.ALLOWED_ORIGINS?.split(',')
                : true,
            credentials: true
        }));
        
        // 圧縮
        this.app.use(compression());
        
        // レート制限
        const limiter = rateLimit({
            windowMs: 15 * 60 * 1000, // 15分
            max: process.env.NODE_ENV === 'production' ? 100 : 1000, // リクエスト数制限
            message: 'Too many requests from this IP, please try again later.',
            standardHeaders: true,
            legacyHeaders: false,
        });
        this.app.use('/api/', limiter);
        
        // ツイート投稿の制限（より厳しく）
        const tweetLimiter = rateLimit({
            windowMs: 1 * 60 * 1000, // 1分
            max: process.env.NODE_ENV === 'production' ? 10 : 100, // 開発環境では緩和
            message: 'Too many tweets, please slow down.',
            skipSuccessfulRequests: false
        });
        this.app.use('/api/tweets', tweetLimiter);
        
        // JSON解析
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
        
    }
    
    setupRoutes() {
        // API Routes
        this.app.use('/api/auth', new AuthAPI(this.db).router);
        this.app.use('/api/tweets', new TwitterAPI(this.db, this.io).router);
        
        // Health check
        this.app.get('/api/health', (req, res) => {
            res.json({ 
                status: 'OK', 
                timestamp: new Date().toISOString(),
                version: require('../package.json').version,
                users: this.connectedUsers.size
            });
        });
        
        // Statistics
        this.app.get('/api/stats', async (req, res) => {
            try {
                const stats = await this.db.getStats();
                res.json({
                    ...stats,
                    connectedUsers: this.connectedUsers.size,
                    server: {
                        uptime: process.uptime(),
                        memory: process.memoryUsage(),
                        version: process.version
                    }
                });
            } catch (error) {
                console.error('Stats error:', error);
                res.status(500).json({ error: 'Internal server error' });
            }
        });
        
        // 静的ファイル配信（APIルートの後に配置）
        this.app.use(express.static(path.join(__dirname, '../frontend')));
        
        // Frontend routing (SPA)
        this.app.get('*', (req, res) => {
            res.sendFile(path.join(__dirname, '../frontend/index.html'));
        });
    }
    
    setupSocketIO() {
        this.io.on('connection', (socket) => {
            console.log(`User connected: ${socket.id}`);
            
            // ユーザー認証
            socket.on('authenticate', (data) => {
                try {
                    const { deviceId, nickname } = data;
                    if (deviceId && nickname) {
                        this.connectedUsers.set(socket.id, {
                            deviceId,
                            nickname,
                            connectedAt: new Date()
                        });
                        
                        socket.join('authenticated');
                        socket.emit('authenticated', { success: true });
                        
                        // オンラインユーザー数を更新
                        this.io.emit('userCount', this.connectedUsers.size);
                        
                        console.log(`User authenticated: ${nickname} (${deviceId})`);
                    }
                } catch (error) {
                    console.error('Authentication error:', error);
                    socket.emit('authenticated', { success: false, error: 'Authentication failed' });
                }
            });
            
            // リアルタイムツイート（WebSocket経由）
            socket.on('newTweet', async (tweetData) => {
                try {
                    const user = this.connectedUsers.get(socket.id);
                    if (!user) {
                        socket.emit('error', 'Not authenticated');
                        return;
                    }
                    
                    console.log('WebSocket経由ツイート受信:', tweetData, 'from user:', user.nickname);
                    
                    // ツイートをデータベースに保存
                    const tweet = await this.db.createTweet({
                        content: tweetData.content,
                        authorId: user.deviceId,
                        author: user.nickname
                    });
                    
                    console.log('ツイート保存完了:', tweet.id);
                    
                    // 全ユーザーに配信（投稿者にも配信）
                    this.io.to('authenticated').emit('newTweet', tweet);
                    
                } catch (error) {
                    console.error('New tweet error:', error);
                    socket.emit('error', 'Failed to create tweet');
                }
            });
            
            // いいね/リツイート
            socket.on('tweetAction', async (data) => {
                try {
                    const user = this.connectedUsers.get(socket.id);
                    if (!user) return;
                    
                    const { tweetId, action } = data; // action: 'like' | 'retweet'
                    const updatedTweet = await this.db.updateTweetAction(tweetId, action, user.deviceId);
                    
                    // 全ユーザーに更新を配信
                    this.io.to('authenticated').emit('tweetActionUpdate', {
                        tweetId,
                        action,
                        tweet: updatedTweet
                    });
                    
                } catch (error) {
                    console.error('Tweet action error:', error);
                    socket.emit('error', 'Failed to update tweet');
                }
            });
            
            // 切断処理
            socket.on('disconnect', () => {
                console.log(`User disconnected: ${socket.id}`);
                this.connectedUsers.delete(socket.id);
                this.io.emit('userCount', this.connectedUsers.size);
            });
        });
    }
    
    setupErrorHandling() {
        // 404 エラー
        this.app.use((req, res) => {
            res.status(404).json({ error: 'Not found' });
        });
        
        // グローバルエラーハンドリング
        this.app.use((err, req, res, next) => {
            console.error('Global error:', err);
            res.status(500).json({ 
                error: process.env.NODE_ENV === 'production' 
                    ? 'Internal server error' 
                    : err.message 
            });
        });
        
        // プロセス例外処理
        process.on('uncaughtException', (error) => {
            console.error('Uncaught Exception:', error);
            process.exit(1);
        });
        
        process.on('unhandledRejection', (reason, promise) => {
            console.error('Unhandled Rejection at:', promise, 'reason:', reason);
            process.exit(1);
        });
    }
    
    async start() {
        try {
            // データベース初期化
            await this.db.init();
            console.log('Database initialized');
            
            // サーバー起動
            this.server.listen(this.port, () => {
                console.log(`🚀 山田Twitter Server running on port ${this.port}`);
                console.log(`🌍 Frontend: http://localhost:${this.port}`);
                console.log(`📡 WebSocket: ws://localhost:${this.port}`);
                console.log(`🔧 Environment: ${process.env.NODE_ENV || 'development'}`);
            });
            
        } catch (error) {
            console.error('Failed to start server:', error);
            process.exit(1);
        }
    }
    
    async stop() {
        try {
            await this.db.close();
            this.server.close();
            console.log('Server stopped gracefully');
        } catch (error) {
            console.error('Error stopping server:', error);
        }
    }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
    console.log('SIGTERM received, shutting down gracefully');
    if (global.server) {
        await global.server.stop();
    }
    process.exit(0);
});

process.on('SIGINT', async () => {
    console.log('SIGINT received, shutting down gracefully');
    if (global.server) {
        await global.server.stop();
    }
    process.exit(0);
});

// サーバー起動
if (require.main === module) {
    const server = new YamadaTwitterServer();
    global.server = server;
    server.start();
}

module.exports = YamadaTwitterServer;