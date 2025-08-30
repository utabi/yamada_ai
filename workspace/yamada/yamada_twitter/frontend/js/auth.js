/**
 * 山田Twitter認証システム
 * デバイスフィンガープリンティング + Cookie/LocalStorage
 * パスワード不要、ニックネームのみでユーザー識別
 */

class YamadaAuth {
    constructor() {
        this.client = null;
        this.deviceId = null;
        this.userData = {
            nickname: '',
            deviceId: '',
            createdAt: '',
            lastActive: ''
        };
        
        this.init();
    }
    
    /**
     * 初期化 - ClientJSライブラリが読み込まれてから実行
     */
    async init() {
        try {
            // ClientJSが利用可能になるまで待機
            await this.waitForClientJS();
            
            // デバイスIDを生成
            this.generateDeviceId();
            
            // 既存ユーザーをチェック
            this.loadUserData();
            
            console.log('山田Twitter認証システム初期化完了', {
                deviceId: this.deviceId,
                hasUser: !!this.userData.nickname
            });
            
        } catch (error) {
            console.error('認証システム初期化エラー:', error);
            // フォールバック: シンプルなランダムIDを使用
            this.deviceId = this.generateFallbackId();
        }
    }
    
    /**
     * ClientJSライブラリの読み込み待機
     */
    waitForClientJS() {
        return new Promise((resolve, reject) => {
            let attempts = 0;
            const maxAttempts = 50; // 5秒間待機
            
            const checkClientJS = () => {
                if (typeof ClientJS !== 'undefined') {
                    this.client = new ClientJS();
                    resolve();
                } else if (attempts < maxAttempts) {
                    attempts++;
                    setTimeout(checkClientJS, 100);
                } else {
                    reject(new Error('ClientJSライブラリの読み込みに失敗'));
                }
            };
            
            checkClientJS();
        });
    }
    
    /**
     * デバイス固有IDの生成
     */
    generateDeviceId() {
        if (!this.client) {
            this.deviceId = this.generateFallbackId();
            return;
        }
        
        try {
            // デバイスフィンガープリント生成
            const fingerprint = this.client.getFingerprint();
            
            // 追加のデバイス情報を取得（ClientJSの実際のAPIに合わせて修正）
            const deviceInfo = {
                userAgent: this.client.getUserAgent() || navigator.userAgent,
                language: this.client.getLanguage() || navigator.language,
                screen: `${screen.width}x${screen.height}`,
                timezone: this.client.getTimeZone() || Intl.DateTimeFormat().resolvedOptions().timeZone,
                platform: this.client.getOS() || navigator.platform
            };
            
            // より安定したIDを生成するため複数の情報を組み合わせ
            const combinedInfo = fingerprint + JSON.stringify(deviceInfo);
            this.deviceId = this.hashString(combinedInfo);
            
            console.log('デバイスID生成完了:', {
                deviceId: this.deviceId,
                fingerprint: fingerprint,
                deviceInfo: deviceInfo
            });
            
        } catch (error) {
            console.error('デバイスID生成エラー:', error);
            this.deviceId = this.generateFallbackId();
        }
    }
    
    /**
     * フォールバックID生成（ClientJS失敗時）
     */
    generateFallbackId() {
        const randomPart = Math.random().toString(36).substr(2, 9);
        const timePart = Date.now().toString(36);
        const navigatorPart = navigator.userAgent.slice(-10).replace(/\W/g, '');
        
        return this.hashString(randomPart + timePart + navigatorPart);
    }
    
    /**
     * 文字列をハッシュ化
     */
    hashString(str) {
        let hash = 0;
        if (str.length === 0) return hash.toString();
        
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // 32bit integerに変換
        }
        
        return Math.abs(hash).toString(36);
    }
    
    /**
     * ユーザーデータを読み込み
     */
    loadUserData() {
        try {
            // LocalStorageから読み込み
            const stored = localStorage.getItem(`yamada_user_${this.deviceId}`);
            
            if (stored) {
                this.userData = JSON.parse(stored);
                this.userData.lastActive = new Date().toISOString();
                this.saveUserData();
                
                console.log('既存ユーザーデータ読み込み:', this.userData);
                return true;
            }
            
            // Cookieからも確認（フォールバック）
            const cookieData = this.getCookie(`yamada_user`);
            if (cookieData) {
                this.userData = JSON.parse(decodeURIComponent(cookieData));
                this.userData.lastActive = new Date().toISOString();
                this.saveUserData();
                
                console.log('Cookieからユーザーデータ復元:', this.userData);
                return true;
            }
            
        } catch (error) {
            console.error('ユーザーデータ読み込みエラー:', error);
        }
        
        return false;
    }
    
    /**
     * ユーザーデータを保存
     */
    saveUserData() {
        try {
            this.userData.deviceId = this.deviceId;
            this.userData.lastActive = new Date().toISOString();
            
            // LocalStorageに保存
            localStorage.setItem(`yamada_user_${this.deviceId}`, JSON.stringify(this.userData));
            
            // Cookieにも保存（7日間有効）
            this.setCookie('yamada_user', encodeURIComponent(JSON.stringify(this.userData)), 7);
            
            console.log('ユーザーデータ保存完了:', this.userData);
            
        } catch (error) {
            console.error('ユーザーデータ保存エラー:', error);
        }
    }
    
    /**
     * ニックネーム設定/変更
     */
    async setNickname(nickname) {
        if (!nickname || nickname.trim().length === 0) {
            throw new Error('ニックネームが空です');
        }
        
        if (nickname.length > 20) {
            throw new Error('ニックネームは20文字以内にしてください');
        }
        
        const cleanNickname = nickname.trim();
        
        // サーバーに送信して更新
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    deviceId: this.deviceId,
                    nickname: cleanNickname
                })
            });
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'ニックネーム設定に失敗しました');
            }
            
            // ローカルストレージも更新
            if (!this.userData.createdAt) {
                this.userData.createdAt = new Date().toISOString();
            }
            
            this.userData.nickname = cleanNickname;
            this.saveUserData();
            
            console.log('ニックネーム設定:', cleanNickname);
            
            return true;
        } catch (error) {
            console.error('ニックネーム設定エラー:', error);
            throw error;
        }
    }
    
    /**
     * ユーザー認証状態チェック
     */
    isAuthenticated() {
        return !!(this.deviceId && this.userData.nickname);
    }
    
    /**
     * 現在のユーザー情報取得
     */
    getCurrentUser() {
        if (!this.isAuthenticated()) {
            return null;
        }
        
        return {
            deviceId: this.deviceId,
            nickname: this.userData.nickname,
            createdAt: this.userData.createdAt,
            lastActive: this.userData.lastActive
        };
    }
    
    /**
     * ログアウト（データ削除）
     */
    logout() {
        try {
            localStorage.removeItem(`yamada_user_${this.deviceId}`);
            this.setCookie('yamada_user', '', -1); // Cookieを削除
            
            this.userData = {
                nickname: '',
                deviceId: '',
                createdAt: '',
                lastActive: ''
            };
            
            console.log('ログアウト完了');
            return true;
            
        } catch (error) {
            console.error('ログアウトエラー:', error);
            return false;
        }
    }
    
    /**
     * Cookie操作ヘルパー
     */
    setCookie(name, value, days) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
    }
    
    getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }
    
    /**
     * デバイス情報取得（デバッグ用）
     */
    getDeviceInfo() {
        if (!this.client) return null;
        
        return {
            fingerprint: this.client.getFingerprint(),
            userAgent: this.client.getUserAgent() || navigator.userAgent,
            language: this.client.getLanguage() || navigator.language,
            screen: `${screen.width}x${screen.height}`,
            timezone: this.client.getTimeZone() || Intl.DateTimeFormat().resolvedOptions().timeZone,
            os: this.client.getOS() || navigator.platform,
            browser: this.client.getBrowser() || 'unknown',
            device: this.client.getDevice() || 'unknown'
        };
    }
}

// グローバルに公開
window.YamadaAuth = YamadaAuth;