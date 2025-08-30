/**
 * 山田Twitter メインアプリケーション
 * バックエンドAPIとの連携バージョン
 */

class YamadaTwitterApp {
    constructor() {
        this.apiBaseUrl = window.location.origin + '/api';
        this.auth = null;
        this.socket = null;
        this.tweets = [];
        this.isConnected = false;
        this.currentTab = 'main';
        
        this.init();
    }
    
    async init() {
        try {
            console.log('山田Twitter アプリ初期化開始');
            
            // 認証システム初期化
            this.auth = new YamadaAuth();
            await this.waitForAuth();
            
            // WebSocket接続
            this.initWebSocket();
            
            // UI初期化
            this.updateUI();
            this.setupEventListeners();
            
            // 初期データ読み込み
            await this.loadTweets();
            
            console.log('山田Twitter アプリ初期化完了');
            
        } catch (error) {
            console.error('初期化エラー:', error);
            this.showError('初期化に失敗しました: ' + error.message);
        }
    }
    
    async waitForAuth() {
        return new Promise((resolve) => {
            const checkAuth = () => {
                if (this.auth && this.auth.deviceId) {
                    resolve();
                } else {
                    setTimeout(checkAuth, 100);
                }
            };
            checkAuth();
        });
    }
    
    initWebSocket() {
        try {
            // Socket.IOクライアント（CDNから読み込み想定）
            if (typeof io !== 'undefined') {
                this.socket = io();
                
                this.socket.on('connect', () => {
                    console.log('WebSocket接続成功');
                    this.isConnected = true;
                    
                    // 認証済みの場合は自動認証
                    if (this.auth.isAuthenticated()) {
                        const user = this.auth.getCurrentUser();
                        this.socket.emit('authenticate', {
                            deviceId: user.deviceId,
                            nickname: user.nickname
                        });
                        
                        // 接続後にタイムラインを更新
                        setTimeout(() => this.loadTweets(), 1000);
                    }
                });
                
                this.socket.on('disconnect', () => {
                    console.log('WebSocket切断');
                    this.isConnected = false;
                });
                
                this.socket.on('authenticated', (data) => {
                    if (data.success) {
                        console.log('WebSocket認証成功');
                    }
                });
                
                this.socket.on('newTweet', (tweet) => {
                    console.log('新しいツイート受信:', tweet);
                    // 重複チェック
                    const exists = this.tweets.some(t => t.id === tweet.id);
                    if (!exists) {
                        this.addTweetToUI(tweet, true);
                    }
                });
                
                this.socket.on('tweetAction', (data) => {
                    console.log('ツイートアクション受信:', data);
                    this.updateTweetInUI(data.tweet);
                });
                
                this.socket.on('userCount', (count) => {
                    console.log('オンラインユーザー数:', count);
                });
                
                // 新しい返信を受信
                this.socket.on('newReply', (data) => {
                    console.log('新しい返信受信:', data);
                    // 返信モーダルが開いていて、該当ツイートへの返信なら更新
                    const modal = document.querySelector('.modal');
                    if (modal && data.tweetId) {
                        const repliesList = document.getElementById('replies-list');
                        if (repliesList) {
                            // 既存の返信リストに追加
                            const replyHtml = `
                                <div class="reply">
                                    <div class="reply-header">
                                        <span class="reply-author">${this.escapeHtml(data.reply.author_nickname)}</span>
                                        <span class="reply-time">${this.formatTime(data.reply.created_at)}</span>
                                    </div>
                                    <div class="reply-content">${this.decorateText(data.reply.content)}</div>
                                </div>
                            `;
                            
                            // "まだ返信がありません"メッセージがあれば削除
                            const noReplies = repliesList.querySelector('.no-replies');
                            if (noReplies) {
                                repliesList.innerHTML = '';
                            }
                            
                            // 新しい返信を追加
                            repliesList.insertAdjacentHTML('afterbegin', replyHtml);
                        }
                    }
                    
                    // タイムラインの返信数も更新
                    const tweetEl = document.querySelector(`[data-tweet-id="${data.tweetId}"]`);
                    if (tweetEl) {
                        this.loadTweets(); // 簡単のため全体をリロード
                    }
                });
                
            } else {
                console.warn('Socket.IO not available, using polling mode');
            }
        } catch (error) {
            console.error('WebSocket初期化エラー:', error);
        }
    }
    
    updateUI() {
        const deviceIdEl = document.getElementById('device-id');
        const authSection = document.getElementById('auth-section');
        const twitterSection = document.getElementById('twitter-section');
        const logoutBtn = document.getElementById('logout-btn');
        
        if (this.auth && this.auth.deviceId) {
            deviceIdEl.textContent = this.auth.deviceId;
        }
        
        if (this.auth && this.auth.isAuthenticated()) {
            authSection.classList.add('hidden');
            twitterSection.classList.remove('hidden');
            logoutBtn.classList.remove('hidden');
            
            // プロフィール情報を更新（メニュー用）
            if (typeof updateProfileInfo === 'function') {
                updateProfileInfo();
            }
        } else {
            authSection.classList.remove('hidden');
            twitterSection.classList.add('hidden');
            logoutBtn.classList.add('hidden');
        }
    }
    
    setupEventListeners() {
        // ニックネーム入力でEnter
        const nicknameInput = document.getElementById('nickname-input');
        if (nicknameInput) {
            nicknameInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.setNickname();
                }
            });
        }
        
        // ツイート入力でCtrl+Enter
        const tweetInput = document.getElementById('tweet-input');
        if (tweetInput) {
            tweetInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.postTweet();
                }
            });
            
            // 文字数カウント
            tweetInput.addEventListener('input', () => {
                this.updateCharCount();
            });
        }
    }
    
    async setNickname() {
        const input = document.getElementById('nickname-input');
        const nickname = input.value.trim();
        
        if (!nickname) {
            this.showError('ニックネームを入力してください');
            return;
        }
        
        try {
            // auth.setNicknameでサーバーとローカル両方を更新
            await this.auth.setNickname(nickname);
            
            this.showSuccess('ニックネームを設定しました: ' + nickname);
            this.updateUI();
            
            // WebSocket認証
            if (this.socket && this.isConnected) {
                this.socket.emit('authenticate', {
                    deviceId: this.auth.deviceId,
                    nickname: nickname
                });
            }
            
            // ツイート読み込み
            await this.loadTweets();
            
            input.value = '';
            
        } catch (error) {
            console.error('ニックネーム設定エラー:', error);
            // エラーメッセージを表示
            const errorMsg = error.message || 'ニックネーム設定に失敗しました';
            
            // 特定のエラーメッセージの場合は追加の指示を表示
            if (errorMsg.includes('invalid characters') || errorMsg.includes('使用できない文字')) {
                this.showError('ニックネームには英数字、日本語、アンダースコア(_)のみ使用できます。@マークや特殊文字は使用できません。');
            } else {
                this.showError(errorMsg);
            }
        }
    }
    
    async postTweet() {
        const input = document.getElementById('tweet-input');
        const content = input.value.trim();
        
        if (!content) {
            this.showError('ツイート内容を入力してください');
            return;
        }
        
        if (!this.auth.isAuthenticated()) {
            this.showError('ログインが必要です');
            return;
        }
        
        try {
            const user = this.auth.getCurrentUser();
            
            // WebSocket接続がある場合はWebSocket経由で送信
            if (this.socket && this.isConnected) {
                console.log('WebSocket経由でツイート送信:', content);
                this.socket.emit('newTweet', { content: content });
                
                input.value = '';
                this.updateCharCount();
                this.showSuccess('ツイートを投稿しました');
                return;
            }
            
            // WebSocket未接続の場合はHTTP API経由
            const response = await fetch(`${this.apiBaseUrl}/tweets`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: content,
                    authorId: user.deviceId,
                    author: user.nickname
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                input.value = '';
                this.updateCharCount();
                this.showSuccess('ツイートを投稿しました');
                this.addTweetToUI(result.data, true);
            } else {
                this.showError(result.error || 'ツイート投稿に失敗しました');
            }
            
        } catch (error) {
            console.error('ツイート投稿エラー:', error);
            this.showError('ツイート投稿に失敗しました');
        }
    }
    
    async loadTweets() {
        try {
            let url = `${this.apiBaseUrl}/tweets`;
            
            // @タブの場合はメンション用エンドポイントを使用
            if (this.currentTab === 'mentions') {
                const user = this.auth.getCurrentUser();
                const nickname = user?.nickname || this.auth.deviceId;
                console.log('[loadTweets] Loading mentions for:', nickname);
                url = `${this.apiBaseUrl}/tweets/mentions/${nickname}`;
            }
            
            const response = await fetch(url);
            const result = await response.json();
            
            if (result.success) {
                this.tweets = result.data;
                this.renderTweets();
            } else {
                console.error('ツイート読み込みエラー:', result.error);
            }
            
        } catch (error) {
            console.error('ツイート読み込みエラー:', error);
            const timeline = document.getElementById('timeline');
            if (timeline) {
                timeline.innerHTML = '<div class="loading">ツイートの読み込みに失敗しました</div>';
            }
        }
    }
    
    // タブ切り替え
    switchTab(tab) {
        this.currentTab = tab;
        
        // タブボタンのアクティブ状態を更新
        document.querySelectorAll('.tab-btn').forEach(btn => {
            if (btn.dataset.tab === tab) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // タイムラインを再読み込み
        this.loadTweets();
    }
    
    renderTweets() {
        const timeline = document.getElementById('timeline');
        if (!timeline) return;
        
        if (this.tweets.length === 0) {
            timeline.innerHTML = '<div class="loading">まだツイートがありません</div>';
            return;
        }
        
        timeline.innerHTML = this.tweets.map(tweet => this.renderTweet(tweet)).join('');
    }
    
    renderTweet(tweet) {
        const repliesCount = tweet.replies_count || 0;
        return `
            <div class="tweet" data-tweet-id="${tweet.id}" onclick="app.openReplyView('${tweet.id}')">
                <div class="tweet-header">
                    <span class="tweet-author" onclick="event.stopPropagation(); viewProfile('${tweet.author_id}')" style="cursor: pointer; text-decoration: underline;">${this.escapeHtml(tweet.author_nickname)}</span>
                    <span class="tweet-time">${this.formatTime(tweet.created_at)}</span>
                </div>
                <div class="tweet-content">${this.decorateText(tweet.content)}</div>
                <div class="tweet-actions" onclick="event.stopPropagation()">
                    <button class="tweet-action" onclick="app.likeTweet('${tweet.id}')">
                        ❤️ ${tweet.likes_count || 0}
                    </button>
                    <button class="tweet-action" onclick="app.retweetTweet('${tweet.id}')">
                        🔄 ${tweet.retweets_count || 0}
                    </button>
                    <button class="tweet-action" onclick="app.openReplyView('${tweet.id}')">
                        💬 ${repliesCount > 0 ? repliesCount : ''}
                    </button>
                </div>
            </div>
        `;
    }
    
    addTweetToUI(tweet, prepend = false) {
        // 重複チェック
        const existingIndex = this.tweets.findIndex(t => t.id === tweet.id);
        if (existingIndex !== -1) {
            console.log('重複ツイート検出、スキップ:', tweet.id);
            return;
        }
        
        if (prepend) {
            this.tweets.unshift(tweet);
        } else {
            this.tweets.push(tweet);
        }
        
        const timeline = document.getElementById('timeline');
        if (!timeline) return;
        
        const tweetHtml = this.renderTweet(tweet);
        
        if (prepend) {
            timeline.insertAdjacentHTML('afterbegin', tweetHtml);
        } else {
            timeline.insertAdjacentHTML('beforeend', tweetHtml);
        }
    }
    
    updateTweetInUI(updatedTweet) {
        const tweetIndex = this.tweets.findIndex(t => t.id === updatedTweet.id);
        if (tweetIndex !== -1) {
            this.tweets[tweetIndex] = updatedTweet;
            
            const tweetElement = document.querySelector(`[data-tweet-id="${updatedTweet.id}"]`);
            if (tweetElement) {
                tweetElement.outerHTML = this.renderTweet(updatedTweet);
            }
        }
    }
    
    async likeTweet(tweetId) {
        if (!this.auth.isAuthenticated()) {
            this.showError('ログインが必要です');
            return;
        }
        
        try {
            const user = this.auth.getCurrentUser();
            
            const response = await fetch(`${this.apiBaseUrl}/tweets/${tweetId}/action`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'like',
                    userDeviceId: user.deviceId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // WebSocket経由で他のクライアントにも配信される
                this.updateTweetInUI(result.data.tweet);
            } else {
                this.showError(result.error || 'いいねに失敗しました');
            }
            
        } catch (error) {
            console.error('いいねエラー:', error);
            this.showError('いいねに失敗しました');
        }
    }
    
    async retweetTweet(tweetId) {
        if (!this.auth.isAuthenticated()) {
            this.showError('ログインが必要です');
            return;
        }
        
        try {
            const user = this.auth.getCurrentUser();
            
            const response = await fetch(`${this.apiBaseUrl}/tweets/${tweetId}/action`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'retweet',
                    userDeviceId: user.deviceId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.updateTweetInUI(result.data.tweet);
            } else {
                this.showError(result.error || 'リツイートに失敗しました');
            }
            
        } catch (error) {
            console.error('リツイートエラー:', error);
            this.showError('リツイートに失敗しました');
        }
    }
    
    logout() {
        if (confirm('ログアウトしますか？')) {
            this.auth.logout();
            this.tweets = [];
            
            if (this.socket && this.isConnected) {
                this.socket.disconnect();
                this.socket.connect();
            }
            
            this.updateUI();
            this.showSuccess('ログアウトしました');
        }
    }
    
    updateCharCount() {
        const input = document.getElementById('tweet-input');
        const charCountEl = document.getElementById('char-count');
        const tweetBtn = document.getElementById('tweet-btn');
        
        if (!input || !charCountEl || !tweetBtn) return;
        
        const count = input.value.length;
        charCountEl.textContent = `${count}/280`;
        
        if (count > 240) {
            charCountEl.classList.add('warning');
        } else {
            charCountEl.classList.remove('warning');
        }
        
        tweetBtn.disabled = count === 0 || count > 280;
    }
    
    // 返信画面を開く
    async openReplyView(tweetId) {
        try {
            // 元ツイートを取得
            const response = await fetch(`${this.apiBaseUrl}/tweets/${tweetId}`);
            const result = await response.json();
            
            if (!result.success) {
                this.showError('ツイートの取得に失敗しました');
                return;
            }
            
            const originalTweet = result.data;
            
            // 返信画面をモーダルで表示
            this.showReplyModal(originalTweet);
            
        } catch (error) {
            console.error('返信画面エラー:', error);
            this.showError('返信画面を開けませんでした');
        }
    }
    
    showReplyModal(originalTweet) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <button class="modal-close" onclick="this.closest('.modal').remove()">×</button>
            <div class="modal-content">
                
                <div class="original-tweet">
                    <div class="tweet-header">
                        <span class="tweet-author">${this.escapeHtml(originalTweet.author_nickname)}</span>
                        <span class="tweet-time">${this.formatTime(originalTweet.created_at)}</span>
                    </div>
                    <div class="tweet-content">${this.decorateText(originalTweet.content)}</div>
                </div>
                
                <div class="reply-form">
                    <textarea id="reply-input" placeholder="@${originalTweet.author_nickname} への返信" maxlength="280"></textarea>
                    <div class="reply-controls">
                        <span class="char-count" id="reply-char-count">0/280</span>
                        <button id="reply-btn" onclick="app.postReply('${originalTweet.id}')">返信</button>
                    </div>
                </div>
                
                <div class="replies-section">
                    <div id="replies-list">読み込み中...</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 返信入力の文字数カウント
        const replyInput = modal.querySelector('#reply-input');
        const replyCharCount = modal.querySelector('#reply-char-count');
        const replyBtn = modal.querySelector('#reply-btn');
        
        replyInput.addEventListener('input', () => {
            const count = replyInput.value.length;
            replyCharCount.textContent = `${count}/280`;
            
            if (count > 240) {
                replyCharCount.classList.add('warning');
            } else {
                replyCharCount.classList.remove('warning');
            }
            
            replyBtn.disabled = count === 0 || count > 280;
        });
        
        // 返信一覧を読み込み
        this.loadReplies(originalTweet.id);
        
        // モーダル背景クリックで閉じる
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    async loadReplies(tweetId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/tweets/${tweetId}/replies`);
            const result = await response.json();
            
            const repliesList = document.getElementById('replies-list');
            if (!repliesList) return;
            
            if (result.success && result.data.length > 0) {
                repliesList.innerHTML = result.data.map(reply => `
                    <div class="reply">
                        <div class="reply-header">
                            <span class="reply-author">${this.escapeHtml(reply.author_nickname)}</span>
                            <span class="reply-time">${this.formatTime(reply.created_at)}</span>
                        </div>
                        <div class="reply-content">${this.decorateText(reply.content)}</div>
                    </div>
                `).join('');
            } else {
                repliesList.innerHTML = '<div class="no-replies">まだ返信がありません</div>';
            }
            
        } catch (error) {
            console.error('返信読み込みエラー:', error);
            const repliesList = document.getElementById('replies-list');
            if (repliesList) {
                repliesList.innerHTML = '<div class="error">返信の読み込みに失敗しました</div>';
            }
        }
    }
    
    async postReply(tweetId) {
        const replyInput = document.getElementById('reply-input');
        const content = replyInput.value.trim();
        
        if (!content) {
            this.showError('返信内容を入力してください');
            return;
        }
        
        if (!this.auth.isAuthenticated()) {
            this.showError('ログインが必要です');
            return;
        }
        
        try {
            const user = this.auth.getCurrentUser();
            
            const response = await fetch(`${this.apiBaseUrl}/tweets/${tweetId}/replies`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    content: content,
                    authorId: user.deviceId,
                    author: user.nickname
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                replyInput.value = '';
                document.getElementById('reply-char-count').textContent = '0/280';
                this.showSuccess('返信を投稿しました');
                
                // 返信一覧を再読み込み
                this.loadReplies(tweetId);
                
                // メインタイムラインも更新（返信数反映）
                this.loadTweets();
                
            } else {
                this.showError(result.error || '返信投稿に失敗しました');
            }
            
        } catch (error) {
            console.error('返信投稿エラー:', error);
            this.showError('返信投稿に失敗しました');
        }
    }
    
    // ユーティリティメソッド
    showError(message) {
        const errorEl = document.getElementById('error-msg');
        const successEl = document.getElementById('success-msg');
        
        if (!errorEl) return;
        
        if (successEl) successEl.classList.add('hidden');
        errorEl.textContent = message;
        errorEl.classList.remove('hidden');
        
        setTimeout(() => {
            errorEl.classList.add('hidden');
        }, 5000);
    }
    
    showSuccess(message) {
        const errorEl = document.getElementById('error-msg');
        const successEl = document.getElementById('success-msg');
        
        if (!successEl) return;
        
        if (errorEl) errorEl.classList.add('hidden');
        successEl.textContent = message;
        successEl.classList.remove('hidden');
        
        setTimeout(() => {
            successEl.classList.add('hidden');
        }, 3000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // テキストを装飾（メンションとハッシュタグ）
    decorateText(text) {
        // 最初にHTMLエスケープ
        let decorated = this.escapeHtml(text);
        
        // @メンションをクリック可能なリンクに（英数字のみ - 実際のユーザー名）
        decorated = decorated.replace(/@([a-zA-Z0-9_]+)/g, 
            '<span class="mention" onclick="event.stopPropagation(); viewProfile(\'$1\')" style="cursor: pointer;">@$1</span>');
        
        // 特別な日本語名へのメンションもリンク化
        const specialNames = ['矢間田', '山田', 'ヤマダ', 'やまだ'];
        specialNames.forEach(name => {
            const regex = new RegExp(`@${name}`, 'g');
            decorated = decorated.replace(regex, 
                `<span class="mention" onclick="event.stopPropagation(); viewProfile('${name}')" style="cursor: pointer;">@${name}</span>`);
        });
        
        // #ハッシュタグをハイライト
        decorated = decorated.replace(/#([a-zA-Z0-9_\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3400-\u4DBF]+)/g, 
            '<span class="hashtag">#$1</span>');
        
        return decorated;
    }
    
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'たった今';
        if (diff < 3600000) return Math.floor(diff / 60000) + '分前';
        if (diff < 86400000) return Math.floor(diff / 3600000) + '時間前';
        
        return date.toLocaleDateString('ja-JP', {
            month: 'numeric',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric'
        });
    }
}

// アプリ初期化
document.addEventListener('DOMContentLoaded', () => {
    window.app = new YamadaTwitterApp();
});

// グローバル関数（HTML側から呼び出し用）
window.setNickname = function() {
    if (window.app) window.app.setNickname();
};

window.postTweet = function() {
    if (window.app) window.app.postTweet();
};

window.switchTab = function(tab) {
    if (window.app) window.app.switchTab(tab);
};

window.viewProfile = function(userId) {
    window.location.href = `/profile.html?user=${userId}`;
};

window.logout = function() {
    if (window.app) window.app.logout();
};

window.likeTweet = function(tweetId) {
    if (window.app) window.app.likeTweet(tweetId);
};

window.retweetTweet = function(tweetId) {
    if (window.app) window.app.retweetTweet(tweetId);
};

window.openReplyView = function(tweetId) {
    if (window.app) window.app.openReplyView(tweetId);
};

window.postReply = function(tweetId) {
    if (window.app) window.app.postReply(tweetId);
};