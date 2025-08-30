const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const { promisify } = require('util');
const { v4: uuidv4 } = require('uuid');

class Database {
    constructor() {
        this.dbPath = path.join(__dirname, '../database/yamada_twitter.db');
        this.db = null;
    }
    
    async init() {
        return new Promise((resolve, reject) => {
            // データベースディレクトリを作成
            const fs = require('fs');
            const dbDir = path.dirname(this.dbPath);
            if (!fs.existsSync(dbDir)) {
                fs.mkdirSync(dbDir, { recursive: true });
            }
            
            this.db = new sqlite3.Database(this.dbPath, (err) => {
                if (err) {
                    console.error('Database connection error:', err);
                    reject(err);
                    return;
                }
                
                console.log('Connected to SQLite database:', this.dbPath);
                this.createTables()
                    .then(() => this.migrateExistingMentions())
                    .then(resolve)
                    .catch(reject);
            });
        });
    }
    
    async createTables() {
        const tables = [
            // ユーザーテーブル
            `CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                device_id TEXT UNIQUE NOT NULL,
                nickname TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )`,
            
            // ツイートテーブル
            `CREATE TABLE IF NOT EXISTS tweets (
                id TEXT PRIMARY KEY,
                author_id TEXT NOT NULL,
                author_nickname TEXT NOT NULL,
                content TEXT NOT NULL CHECK(length(content) <= 280),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                likes_count INTEGER DEFAULT 0,
                retweets_count INTEGER DEFAULT 0,
                is_deleted BOOLEAN DEFAULT 0,
                FOREIGN KEY (author_id) REFERENCES users (device_id)
            )`,
            
            // いいねテーブル（重複防止）
            `CREATE TABLE IF NOT EXISTS tweet_likes (
                id TEXT PRIMARY KEY,
                tweet_id TEXT NOT NULL,
                user_device_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tweet_id, user_device_id),
                FOREIGN KEY (tweet_id) REFERENCES tweets (id),
                FOREIGN KEY (user_device_id) REFERENCES users (device_id)
            )`,
            
            // リツイートテーブル（重複防止）
            `CREATE TABLE IF NOT EXISTS tweet_retweets (
                id TEXT PRIMARY KEY,
                tweet_id TEXT NOT NULL,
                user_device_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tweet_id, user_device_id),
                FOREIGN KEY (tweet_id) REFERENCES tweets (id),
                FOREIGN KEY (user_device_id) REFERENCES users (device_id)
            )`,
            
            // ハッシュタグテーブル
            `CREATE TABLE IF NOT EXISTS hashtags (
                id TEXT PRIMARY KEY,
                tag TEXT UNIQUE NOT NULL,
                usage_count INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,
            
            // ツイート-ハッシュタグ関連テーブル
            `CREATE TABLE IF NOT EXISTS tweet_hashtags (
                id TEXT PRIMARY KEY,
                tweet_id TEXT NOT NULL,
                hashtag_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tweet_id) REFERENCES tweets (id),
                FOREIGN KEY (hashtag_id) REFERENCES hashtags (id)
            )`,
            
            // 返信テーブル
            `CREATE TABLE IF NOT EXISTS replies (
                id TEXT PRIMARY KEY,
                tweet_id TEXT NOT NULL,
                author_id TEXT NOT NULL,
                author_nickname TEXT NOT NULL,
                content TEXT NOT NULL CHECK(length(content) <= 280),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_deleted BOOLEAN DEFAULT 0,
                FOREIGN KEY (tweet_id) REFERENCES tweets (id),
                FOREIGN KEY (author_id) REFERENCES users (device_id)
            )`,
            
            // メンションテーブル（誰が誰にメンションしたかを記録）
            `CREATE TABLE IF NOT EXISTS tweet_mentions (
                id TEXT PRIMARY KEY,
                tweet_id TEXT NOT NULL,
                mentioned_user TEXT NOT NULL,
                mentioned_at INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tweet_id) REFERENCES tweets (id)
            )`
        ];
        
        const indexes = [
            'CREATE INDEX IF NOT EXISTS idx_tweets_created_at ON tweets (created_at DESC)',
            'CREATE INDEX IF NOT EXISTS idx_tweets_author_id ON tweets (author_id)',
            'CREATE INDEX IF NOT EXISTS idx_users_device_id ON users (device_id)',
            'CREATE INDEX IF NOT EXISTS idx_tweet_likes_tweet_id ON tweet_likes (tweet_id)',
            'CREATE INDEX IF NOT EXISTS idx_tweet_retweets_tweet_id ON tweet_retweets (tweet_id)',
            'CREATE INDEX IF NOT EXISTS idx_replies_tweet_id ON replies (tweet_id)',
            'CREATE INDEX IF NOT EXISTS idx_replies_created_at ON replies (created_at DESC)',
            'CREATE INDEX IF NOT EXISTS idx_tweet_mentions_tweet_id ON tweet_mentions (tweet_id)',
            'CREATE INDEX IF NOT EXISTS idx_tweet_mentions_mentioned_user ON tweet_mentions (mentioned_user)'
        ];
        
        // テーブル作成
        for (const sql of tables) {
            await this.run(sql);
        }
        
        // インデックス作成
        for (const sql of indexes) {
            await this.run(sql);
        }
        
        console.log('Database tables initialized');
    }
    
    // 既存ツイートのメンションを抽出してテーブルに追加
    async migrateExistingMentions() {
        try {
            // 既存のメンションデータがあるかチェック
            const mentionCount = await this.get('SELECT COUNT(*) as count FROM tweet_mentions');
            if (mentionCount && mentionCount.count > 0) {
                return; // すでにマイグレーション済み
            }
            
            // すべてのツイートを取得
            const tweets = await this.all('SELECT id, content FROM tweets WHERE is_deleted = 0');
            
            for (const tweet of tweets) {
                await this.extractAndSaveMentions(tweet.id, tweet.content);
            }
            
            if (tweets.length > 0) {
                console.log(`Migrated mentions for ${tweets.length} tweets`);
            }
        } catch (error) {
            // テーブルが存在しない場合は無視
            if (!error.message.includes('no such table')) {
                console.log('Mention migration error:', error.message);
            }
        }
    }
    
    // Promise化されたクエリメソッド
    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.run(sql, params, function(err) {
                if (err) {
                    console.error('Database run error:', err, 'SQL:', sql);
                    reject(err);
                } else {
                    resolve({ id: this.lastID, changes: this.changes });
                }
            });
        });
    }
    
    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.get(sql, params, (err, row) => {
                if (err) {
                    console.error('Database get error:', err, 'SQL:', sql);
                    reject(err);
                } else {
                    resolve(row);
                }
            });
        });
    }
    
    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.all(sql, params, (err, rows) => {
                if (err) {
                    console.error('Database all error:', err, 'SQL:', sql);
                    reject(err);
                } else {
                    resolve(rows || []);
                }
            });
        });
    }
    
    // ユーザー関連メソッド
    async getUserByDeviceId(deviceId) {
        return await this.get(
            'SELECT * FROM users WHERE device_id = ?',
            [deviceId]
        );
    }
    
    async createOrUpdateUser(deviceId, nickname) {
        const userId = uuidv4();
        const now = new Date().toISOString();
        
        const existingUser = await this.get(
            'SELECT * FROM users WHERE device_id = ?',
            [deviceId]
        );
        
        if (existingUser) {
            // 既存ユーザーの更新
            await this.run(
                'UPDATE users SET nickname = ?, updated_at = ?, last_active = ? WHERE device_id = ?',
                [nickname, now, now, deviceId]
            );
            return { ...existingUser, nickname, updated_at: now };
        } else {
            // 新規ユーザー作成
            await this.run(
                'INSERT INTO users (id, device_id, nickname, created_at, updated_at, last_active) VALUES (?, ?, ?, ?, ?, ?)',
                [userId, deviceId, nickname, now, now, now]
            );
            return { id: userId, device_id: deviceId, nickname, created_at: now };
        }
    }
    
    async getUser(deviceId) {
        return await this.get(
            'SELECT * FROM users WHERE device_id = ? AND is_active = 1',
            [deviceId]
        );
    }
    
    async updateUserActivity(deviceId) {
        const now = new Date().toISOString();
        await this.run(
            'UPDATE users SET last_active = ? WHERE device_id = ?',
            [now, deviceId]
        );
    }
    
    // ツイート関連メソッド
    async createTweet(tweetData) {
        const { authorId, author, content } = tweetData;
        const tweetId = uuidv4();
        const now = new Date().toISOString();
        
        // 入力検証
        if (!content || content.length > 280) {
            throw new Error('Invalid tweet content');
        }
        
        await this.run(
            'INSERT INTO tweets (id, author_id, author_nickname, content, created_at) VALUES (?, ?, ?, ?, ?)',
            [tweetId, authorId, author, content, now]
        );
        
        // ハッシュタグ抽出と保存
        await this.extractAndSaveHashtags(tweetId, content);
        
        // メンション抽出と保存
        await this.extractAndSaveMentions(tweetId, content);
        
        // 作成されたツイートを返す
        return await this.getTweet(tweetId);
    }
    
    async getTweet(tweetId) {
        return await this.get(`
            SELECT 
                t.*,
                (SELECT COUNT(*) FROM tweet_likes tl WHERE tl.tweet_id = t.id) as likes_count,
                (SELECT COUNT(*) FROM tweet_retweets tr WHERE tr.tweet_id = t.id) as retweets_count
            FROM tweets t 
            WHERE t.id = ? AND t.is_deleted = 0
        `, [tweetId]);
    }
    
    async getTweets(limit = 50, offset = 0) {
        return await this.all(`
            SELECT 
                t.*,
                (SELECT COUNT(*) FROM tweet_likes tl WHERE tl.tweet_id = t.id) as likes_count,
                (SELECT COUNT(*) FROM tweet_retweets tr WHERE tr.tweet_id = t.id) as retweets_count,
                (SELECT COUNT(*) FROM replies r WHERE r.tweet_id = t.id AND r.is_deleted = 0) as replies_count
            FROM tweets t 
            WHERE t.is_deleted = 0 
            ORDER BY t.created_at DESC 
            LIMIT ? OFFSET ?
        `, [limit, offset]);
    }
    
    async getUserTweets(authorId, limit = 50) {
        // ツイートと返信の両方を取得（UNIONを使用）
        return await this.all(`
            SELECT * FROM (
                -- 通常のツイート
                SELECT 
                    t.id,
                    t.author_id,
                    t.author_nickname,
                    t.content,
                    t.created_at,
                    t.updated_at,
                    (SELECT COUNT(*) FROM tweet_likes tl WHERE tl.tweet_id = t.id) as likes_count,
                    (SELECT COUNT(*) FROM tweet_retweets tr WHERE tr.tweet_id = t.id) as retweets_count,
                    (SELECT COUNT(*) FROM replies r WHERE r.tweet_id = t.id AND r.is_deleted = 0) as replies_count,
                    'tweet' as type,
                    NULL as reply_to_id
                FROM tweets t 
                WHERE t.author_id = ? AND t.is_deleted = 0
                
                UNION ALL
                
                -- 返信
                SELECT 
                    r.id,
                    r.author_id,
                    r.author_nickname,
                    r.content,
                    r.created_at,
                    r.updated_at,
                    0 as likes_count,
                    0 as retweets_count,
                    0 as replies_count,
                    'reply' as type,
                    r.tweet_id as reply_to_id
                FROM replies r
                WHERE r.author_id = ? AND r.is_deleted = 0
            )
            ORDER BY created_at DESC 
            LIMIT ?
        `, [authorId, authorId, limit]);
    }
    
    // ユーザーが投稿した返信のみ取得
    async getUserReplies(authorId, limit = 50) {
        return await this.all(`
            SELECT 
                r.id,
                r.author_id,
                r.author_nickname,
                r.content,
                r.created_at,
                r.updated_at,
                r.is_deleted,
                t.content as parent_content,
                t.author_nickname as parent_author
            FROM replies r
            JOIN tweets t ON r.tweet_id = t.id
            WHERE r.author_id = ? AND r.is_deleted = 0 
            ORDER BY r.created_at DESC 
            LIMIT ?
        `, [authorId, limit]);
    }
    
    // メンションされたツイートと返信を受けたツイート取得（新方式）
    async getMentionsAndReplies(userNickname, limit = 50) {
        // メンションテーブルを使用してより正確にメンションを取得
        return await this.all(`
            SELECT DISTINCT
                t.*,
                (SELECT COUNT(*) FROM tweet_likes tl WHERE tl.tweet_id = t.id) as likes_count,
                (SELECT COUNT(*) FROM tweet_retweets tr WHERE tr.tweet_id = t.id) as retweets_count,
                (SELECT COUNT(*) FROM replies r2 WHERE r2.tweet_id = t.id) as replies_count
            FROM tweets t
            WHERE 
                t.is_deleted = 0 AND (
                    -- メンションテーブルから取得
                    t.id IN (
                        SELECT tweet_id FROM tweet_mentions 
                        WHERE mentioned_user = ?
                    )
                    -- 返信として投稿されたツイート（返信先が自分のツイート）
                    OR t.id IN (
                        SELECT r.id FROM replies r
                        JOIN tweets parent ON parent.id = r.tweet_id
                        WHERE parent.author_nickname = ?
                    )
                )
            ORDER BY t.created_at DESC
            LIMIT ?
        `, [userNickname, userNickname, limit]);
    }
    
    // ニックネーム変更時に過去ツイートを更新
    async updateTweetsAuthorNickname(deviceId, newNickname) {
        // 1. ツイートの作者名を更新
        await this.run(
            'UPDATE tweets SET author_nickname = ? WHERE author_id = ?',
            [newNickname, deviceId]
        );
        
        // 2. 返信の作者名も更新
        await this.run(
            'UPDATE replies SET author_nickname = ? WHERE author_id = ?',
            [newNickname, deviceId]
        );
    }
    
    // ニックネーム変更時にメンション内容も更新
    async updateMentionsInContent(oldNickname, newNickname) {
        // 完全一致のみを更新（単語境界を使用）
        // ツイート内容の@メンションを更新
        const tweets = await this.all(
            'SELECT id, content FROM tweets WHERE content LIKE ? AND is_deleted = 0',
            [`%@${oldNickname} %`]  // スペースで終わるメンションのみ
        );
        
        // 文末のメンションも含める
        const tweetsEndWith = await this.all(
            'SELECT id, content FROM tweets WHERE content LIKE ? AND is_deleted = 0',
            [`%@${oldNickname}`]  // 文末で終わるメンション
        );
        
        // 両方のリストをマージ（重複を除く）
        const allTweets = [...tweets, ...tweetsEndWith.filter(t => !tweets.find(t2 => t2.id === t.id))];
        
        for (const tweet of allTweets) {
            // 完全一致のみ置換（単語境界を確認）
            const updatedContent = tweet.content.replace(
                new RegExp(`@${oldNickname}(?![a-zA-Z0-9_])`, 'g'),
                `@${newNickname}`
            );
            
            // 内容が実際に変更された場合のみ更新
            if (updatedContent !== tweet.content) {
                await this.run(
                    'UPDATE tweets SET content = ? WHERE id = ?',
                    [updatedContent, tweet.id]
                );
            }
        }
        
        // 返信内容の@メンションも同様に更新
        const replies = await this.all(
            'SELECT id, content FROM replies WHERE (content LIKE ? OR content LIKE ?) AND is_deleted = 0',
            [`%@${oldNickname} %`, `%@${oldNickname}`]
        );
        
        for (const reply of replies) {
            const updatedContent = reply.content.replace(
                new RegExp(`@${oldNickname}(?![a-zA-Z0-9_])`, 'g'),
                `@${newNickname}`
            );
            
            if (updatedContent !== reply.content) {
                await this.run(
                    'UPDATE replies SET content = ? WHERE id = ?',
                    [updatedContent, reply.id]
                );
            }
        }
        
        // メンションテーブルも更新（完全一致のみ）
        await this.run(
            'UPDATE tweet_mentions SET mentioned_user = ? WHERE mentioned_user = ?',
            [newNickname, oldNickname]
        );
        
        return { tweetsUpdated: allTweets.length, repliesUpdated: replies.length };
    }
    
    // ニックネーム変更時に過去返信を更新
    async updateRepliesAuthorNickname(deviceId, newNickname) {
        return await this.run(
            'UPDATE replies SET author_nickname = ? WHERE author_id = ?',
            [newNickname, deviceId]
        );
    }
    
    // いいね機能
    async toggleTweetLike(tweetId, userDeviceId) {
        const existingLike = await this.get(
            'SELECT * FROM tweet_likes WHERE tweet_id = ? AND user_device_id = ?',
            [tweetId, userDeviceId]
        );
        
        if (existingLike) {
            // いいね取り消し
            await this.run(
                'DELETE FROM tweet_likes WHERE tweet_id = ? AND user_device_id = ?',
                [tweetId, userDeviceId]
            );
            return { action: 'unliked' };
        } else {
            // いいね追加
            const likeId = uuidv4();
            await this.run(
                'INSERT INTO tweet_likes (id, tweet_id, user_device_id) VALUES (?, ?, ?)',
                [likeId, tweetId, userDeviceId]
            );
            return { action: 'liked' };
        }
    }
    
    // リツイート機能
    async toggleTweetRetweet(tweetId, userDeviceId) {
        const existingRetweet = await this.get(
            'SELECT * FROM tweet_retweets WHERE tweet_id = ? AND user_device_id = ?',
            [tweetId, userDeviceId]
        );
        
        if (existingRetweet) {
            // リツイート取り消し
            await this.run(
                'DELETE FROM tweet_retweets WHERE tweet_id = ? AND user_device_id = ?',
                [tweetId, userDeviceId]
            );
            return { action: 'unretweeted' };
        } else {
            // リツイート追加
            const retweetId = uuidv4();
            await this.run(
                'INSERT INTO tweet_retweets (id, tweet_id, user_device_id) VALUES (?, ?, ?)',
                [retweetId, tweetId, userDeviceId]
            );
            return { action: 'retweeted' };
        }
    }
    
    async updateTweetAction(tweetId, action, userDeviceId) {
        let result;
        if (action === 'like') {
            result = await this.toggleTweetLike(tweetId, userDeviceId);
        } else if (action === 'retweet') {
            result = await this.toggleTweetRetweet(tweetId, userDeviceId);
        } else {
            throw new Error('Invalid action');
        }
        
        const updatedTweet = await this.getTweet(tweetId);
        return { ...result, tweet: updatedTweet };
    }
    
    // ハッシュタグ機能
    async extractAndSaveHashtags(tweetId, content) {
        const hashtagRegex = /#[^\s#]+/g;
        const hashtags = content.match(hashtagRegex);
        
        if (!hashtags) return;
        
        for (const tag of hashtags) {
            const cleanTag = tag.toLowerCase();
            
            // ハッシュタグテーブルに追加または更新
            const existingTag = await this.get(
                'SELECT * FROM hashtags WHERE tag = ?',
                [cleanTag]
            );
            
            let hashtagId;
            if (existingTag) {
                hashtagId = existingTag.id;
                await this.run(
                    'UPDATE hashtags SET usage_count = usage_count + 1, updated_at = ? WHERE id = ?',
                    [new Date().toISOString(), hashtagId]
                );
            } else {
                hashtagId = uuidv4();
                await this.run(
                    'INSERT INTO hashtags (id, tag) VALUES (?, ?)',
                    [hashtagId, cleanTag]
                );
            }
            
            // ツイート-ハッシュタグ関連を追加
            const relationId = uuidv4();
            await this.run(
                'INSERT OR IGNORE INTO tweet_hashtags (id, tweet_id, hashtag_id) VALUES (?, ?, ?)',
                [relationId, tweetId, hashtagId]
            );
        }
    }
    
    // メンション抽出と保存
    async extractAndSaveMentions(tweetId, content) {
        const processedMentions = new Set(); // 重複防止
        
        // 1. 通常の@メンション（英数字とアンダースコア）
        const mentionRegex = /@([a-zA-Z0-9_]+)/g;
        let match;
        
        while ((match = mentionRegex.exec(content)) !== null) {
            const username = match[1];
            const position = match.index;
            
            if (!processedMentions.has(username)) {
                processedMentions.add(username);
                
                const mentionId = uuidv4();
                await this.run(
                    'INSERT OR IGNORE INTO tweet_mentions (id, tweet_id, mentioned_user, mentioned_at) VALUES (?, ?, ?, ?)',
                    [mentionId, tweetId, username, position]
                );
            }
        }
        
        // 2. 特別な日本語名（山田、矢間田など）への言及も検出
        const specialNames = ['山田', '矢間田', 'ヤマダ', 'やまだ'];
        for (const name of specialNames) {
            if (content.includes(`@${name}`) || content.includes(`${name}さん`)) {
                const position = content.indexOf(name);
                
                if (!processedMentions.has(name)) {
                    processedMentions.add(name);
                    
                    const mentionId = uuidv4();
                    await this.run(
                        'INSERT OR IGNORE INTO tweet_mentions (id, tweet_id, mentioned_user, mentioned_at) VALUES (?, ?, ?, ?)',
                        [mentionId, tweetId, name, position]
                    );
                }
            }
        }
    }
    
    async searchTweetsByHashtag(tag, limit = 50) {
        const cleanTag = tag.toLowerCase();
        return await this.all(`
            SELECT 
                t.*,
                (SELECT COUNT(*) FROM tweet_likes tl WHERE tl.tweet_id = t.id) as likes_count,
                (SELECT COUNT(*) FROM tweet_retweets tr WHERE tr.tweet_id = t.id) as retweets_count
            FROM tweets t
            JOIN tweet_hashtags th ON t.id = th.tweet_id
            JOIN hashtags h ON th.hashtag_id = h.id
            WHERE h.tag = ? AND t.is_deleted = 0
            ORDER BY t.created_at DESC
            LIMIT ?
        `, [cleanTag, limit]);
    }
    
    async getPopularHashtags(limit = 20) {
        return await this.all(`
            SELECT tag, usage_count 
            FROM hashtags 
            ORDER BY usage_count DESC, updated_at DESC 
            LIMIT ?
        `, [limit]);
    }
    
    // 返信関連メソッド
    async createReply(replyData) {
        const { tweetId, authorId, author, content } = replyData;
        const replyId = uuidv4();
        const now = new Date().toISOString();
        
        // 入力検証
        if (!content || content.length > 280) {
            throw new Error('Invalid reply content');
        }
        
        // 元ツイートの存在確認
        const originalTweet = await this.getTweet(tweetId);
        if (!originalTweet) {
            throw new Error('Original tweet not found');
        }
        
        await this.run(
            'INSERT INTO replies (id, tweet_id, author_id, author_nickname, content, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            [replyId, tweetId, authorId, author, content, now]
        );
        
        return await this.getReply(replyId);
    }
    
    async getReply(replyId) {
        return await this.get(`
            SELECT * FROM replies 
            WHERE id = ? AND is_deleted = 0
        `, [replyId]);
    }
    
    async getReplies(tweetId, limit = 50) {
        return await this.all(`
            SELECT * FROM replies 
            WHERE tweet_id = ? AND is_deleted = 0 
            ORDER BY created_at ASC 
            LIMIT ?
        `, [tweetId, limit]);
    }
    
    // 統計情報
    async getStats() {
        const [userCount, tweetCount, todayTweets, popularTags] = await Promise.all([
            this.get('SELECT COUNT(*) as count FROM users WHERE is_active = 1'),
            this.get('SELECT COUNT(*) as count FROM tweets WHERE is_deleted = 0'),
            this.get(`SELECT COUNT(*) as count FROM tweets 
                     WHERE is_deleted = 0 AND date(created_at) = date('now')`),
            this.getPopularHashtags(5)
        ]);
        
        return {
            users: userCount.count,
            tweets: tweetCount.count,
            todayTweets: todayTweets.count,
            popularHashtags: popularTags
        };
    }
    
    // データベースクリーンアップ
    async cleanup() {
        // 30日以上古いツイートを削除（オプション）
        // await this.run(`
        //     UPDATE tweets SET is_deleted = 1 
        //     WHERE created_at < date('now', '-30 days')
        // `);
        
        // 使用されていないハッシュタグを削除
        await this.run(`
            DELETE FROM hashtags 
            WHERE id NOT IN (SELECT DISTINCT hashtag_id FROM tweet_hashtags)
        `);
        
        console.log('Database cleanup completed');
    }
    
    async close() {
        return new Promise((resolve) => {
            if (this.db) {
                this.db.close((err) => {
                    if (err) {
                        console.error('Database close error:', err);
                    } else {
                        console.log('Database connection closed');
                    }
                    resolve();
                });
            } else {
                resolve();
            }
        });
    }
}

module.exports = Database;