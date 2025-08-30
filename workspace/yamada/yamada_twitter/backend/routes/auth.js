const express = require('express');
const { body, validationResult } = require('express-validator');

class AuthAPI {
    constructor(database) {
        this.db = database;
        this.router = express.Router();
        this.setupRoutes();
    }
    
    setupRoutes() {
        // ユーザー登録・ログイン
        this.router.post('/register', [
            body('deviceId')
                .isString()
                .notEmpty()
                .withMessage('Device ID is required'),
            body('nickname')
                .isString()
                .trim()
                .isLength({ min: 1, max: 20 })
                .withMessage('Nickname must be 1-20 characters')
                .matches(/^[a-zA-Z0-9_\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3400-\u4DBF]+$/)
                .withMessage('ニックネームに使用できない文字が含まれています。@や特殊文字は使用できません。')
        ], this.registerUser.bind(this));
        
        // ユーザー情報取得
        this.router.get('/user/:deviceId', this.getUser.bind(this));
        
        // ユーザー情報更新
        this.router.put('/user/:deviceId', [
            body('nickname')
                .isString()
                .trim()
                .isLength({ min: 1, max: 20 })
                .withMessage('Nickname must be 1-20 characters')
                .matches(/^[a-zA-Z0-9_\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3400-\u4DBF]+$/)
                .withMessage('ニックネームに使用できない文字が含まれています。@や特殊文字は使用できません。')
        ], this.updateUser.bind(this));
        
        // アクティビティ更新
        this.router.post('/activity/:deviceId', this.updateActivity.bind(this));
        
        // デバイス検証
        this.router.post('/verify', [
            body('deviceId')
                .isString()
                .notEmpty()
                .withMessage('Device ID is required')
        ], this.verifyDevice.bind(this));
    }
    
    // ユーザー登録・ログイン
    async registerUser(req, res) {
        try {
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                console.log('Validation errors:', errors.array());
                return res.status(400).json({ 
                    success: false,
                    error: errors.array()[0].msg,
                    errors: errors.array() 
                });
            }
            
            const { deviceId, nickname } = req.body;
            
            // ニックネームの重複チェック（オプション）
            const existingNickname = await this.db.get(
                'SELECT id FROM users WHERE nickname = ? AND device_id != ? AND is_active = 1',
                [nickname, deviceId]
            );
            
            if (existingNickname) {
                return res.status(409).json({ 
                    success: false,
                    error: 'Nickname already exists',
                    code: 'NICKNAME_EXISTS'
                });
            }
            
            // XSS対策: ニックネームのエスケープ
            const sanitizedNickname = this.escapeHtml(nickname);
            
            // 既存ユーザーのニックネームを取得
            const existingUser = await this.db.getUserByDeviceId(deviceId);
            const oldNickname = existingUser?.nickname;
            
            // ユーザー作成・更新
            const user = await this.db.createOrUpdateUser(deviceId, sanitizedNickname);
            
            // ニックネームが変更された場合、過去ツイートも更新
            if (oldNickname && oldNickname !== sanitizedNickname) {
                await this.db.updateTweetsAuthorNickname(deviceId, sanitizedNickname);
                await this.db.updateRepliesAuthorNickname(deviceId, sanitizedNickname);
                // ツイート内容の@メンションも更新
                const mentionUpdates = await this.db.updateMentionsInContent(oldNickname, sanitizedNickname);
                console.log(`Updated mentions: ${mentionUpdates.tweetsUpdated} tweets, ${mentionUpdates.repliesUpdated} replies`);
            }
            
            // レスポンス（機密情報は除外）
            const safeUser = {
                deviceId: user.device_id,
                nickname: user.nickname,
                createdAt: user.created_at,
                updatedAt: user.updated_at
            };
            
            res.status(user.created_at === user.updated_at ? 201 : 200).json({ 
                success: true,
                data: safeUser,
                message: user.created_at === user.updated_at 
                    ? 'User registered successfully' 
                    : 'User updated successfully'
            });
            
        } catch (error) {
            console.error('Register user error:', error);
            res.status(500).json({ 
                success: false,
                error: 'Failed to register user' 
            });
        }
    }
    
    // ユーザー情報取得
    async getUser(req, res) {
        try {
            const { deviceId } = req.params;
            
            if (!deviceId) {
                return res.status(400).json({ 
                    success: false,
                    error: 'Device ID is required' 
                });
            }
            
            // deviceIdまたはnicknameで検索
            let user = await this.db.getUser(deviceId);
            
            // device_idで見つからない場合はnicknameで検索
            if (!user) {
                user = await this.db.get(
                    'SELECT * FROM users WHERE nickname = ? AND is_active = 1',
                    [deviceId]
                );
            }
            
            if (!user) {
                return res.status(404).json({ 
                    success: false,
                    error: 'User not found',
                    code: 'USER_NOT_FOUND'
                });
            }
            
            // アクティビティ更新
            await this.db.updateUserActivity(deviceId);
            
            // 機密情報を除外したレスポンス
            const safeUser = {
                deviceId: user.device_id,
                nickname: user.nickname,
                createdAt: user.created_at,
                lastActive: user.last_active
            };
            
            res.json({ 
                success: true,
                data: safeUser 
            });
            
        } catch (error) {
            console.error('Get user error:', error);
            res.status(500).json({ 
                success: false,
                error: 'Failed to retrieve user' 
            });
        }
    }
    
    // ユーザー情報更新
    async updateUser(req, res) {
        try {
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({ 
                    success: false,
                    errors: errors.array() 
                });
            }
            
            const { deviceId } = req.params;
            const { nickname } = req.body;
            
            // ユーザー存在確認
            const existingUser = await this.db.getUser(deviceId);
            if (!existingUser) {
                return res.status(404).json({ 
                    success: false,
                    error: 'User not found' 
                });
            }
            
            // ニックネームの重複チェック
            const duplicateUser = await this.db.get(
                'SELECT id FROM users WHERE nickname = ? AND device_id != ? AND is_active = 1',
                [nickname, deviceId]
            );
            
            if (duplicateUser) {
                return res.status(409).json({ 
                    success: false,
                    error: 'Nickname already exists',
                    code: 'NICKNAME_EXISTS'
                });
            }
            
            // XSS対策
            const sanitizedNickname = this.escapeHtml(nickname);
            
            // ユーザー情報更新
            const updatedUser = await this.db.createOrUpdateUser(deviceId, sanitizedNickname);
            
            const safeUser = {
                deviceId: updatedUser.device_id,
                nickname: updatedUser.nickname,
                updatedAt: updatedUser.updated_at
            };
            
            res.json({ 
                success: true,
                data: safeUser,
                message: 'User updated successfully' 
            });
            
        } catch (error) {
            console.error('Update user error:', error);
            res.status(500).json({ 
                success: false,
                error: 'Failed to update user' 
            });
        }
    }
    
    // アクティビティ更新
    async updateActivity(req, res) {
        try {
            const { deviceId } = req.params;
            
            if (!deviceId) {
                return res.status(400).json({ 
                    success: false,
                    error: 'Device ID is required' 
                });
            }
            
            // ユーザー存在確認
            const user = await this.db.getUser(deviceId);
            if (!user) {
                return res.status(404).json({ 
                    success: false,
                    error: 'User not found' 
                });
            }
            
            await this.db.updateUserActivity(deviceId);
            
            res.json({ 
                success: true,
                message: 'Activity updated successfully',
                timestamp: new Date().toISOString()
            });
            
        } catch (error) {
            console.error('Update activity error:', error);
            res.status(500).json({ 
                success: false,
                error: 'Failed to update activity' 
            });
        }
    }
    
    // デバイス検証
    async verifyDevice(req, res) {
        try {
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({ 
                    success: false,
                    errors: errors.array() 
                });
            }
            
            const { deviceId } = req.body;
            
            const user = await this.db.getUser(deviceId);
            
            res.json({ 
                success: true,
                data: {
                    deviceId,
                    exists: !!user,
                    user: user ? {
                        deviceId: user.device_id,
                        nickname: user.nickname,
                        lastActive: user.last_active
                    } : null
                }
            });
            
        } catch (error) {
            console.error('Verify device error:', error);
            res.status(500).json({ 
                success: false,
                error: 'Failed to verify device' 
            });
        }
    }
    
    // ヘルパーメソッド
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }
    
    // ニックネーム検証
    isValidNickname(nickname) {
        // 日本語、英数字のみ許可
        const regex = /^[a-zA-Z0-9\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3400-\u4DBF]+$/;
        return regex.test(nickname) && nickname.length >= 1 && nickname.length <= 20;
    }
}

module.exports = AuthAPI;