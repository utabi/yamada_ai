# 🚀 山田Twitter デプロイメントガイド

## 📋 事前準備

### 必要なもの
- Node.js 18以上
- Docker & Docker Compose
- ドメイン名（本番環境）
- SSL証明書（本番環境）

## 🔧 デプロイ手順

### 1. 開発環境での動作確認

```bash
# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev

# ブラウザで確認
open http://localhost:3000
```

### 2. Docker本番環境セットアップ

```bash
# 1. 環境変数設定
cp .env.example .env.production
vi .env.production  # 本番環境用に設定を変更

# 2. Dockerイメージビルド
docker-compose build

# 3. 本番環境起動（Nginxなし）
docker-compose up -d

# 4. 本番環境起動（Nginxあり）
docker-compose --profile production up -d
```

### 3. クラウドサービス別デプロイ

#### A. DigitalOcean App Platform
```bash
# 1. GitHubリポジトリをDigitalOceanに接続
# 2. App Platform設定:
#    - Runtime: Node.js 18
#    - Build Command: npm install
#    - Run Command: npm start
#    - Port: 3000
#    - Environment Variables: .env.productionの内容を設定
```

#### B. Railway
```bash
# 1. Railway CLI インストール
npm install -g @railway/cli

# 2. Railway ログイン
railway login

# 3. プロジェクト作成・デプロイ
railway init
railway up
```

#### C. Heroku
```bash
# 1. Heroku CLI インストール
# 2. プロジェクト作成
heroku create yamada-twitter-app

# 3. 環境変数設定
heroku config:set NODE_ENV=production
heroku config:set ALLOWED_ORIGINS=https://yamada-twitter-app.herokuapp.com

# 4. デプロイ
git push heroku main
```

#### D. AWS EC2
```bash
# 1. EC2インスタンス作成（Ubuntu 20.04+）
# 2. サーバーセットアップ
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker

# 3. プロジェクトアップロード
scp -r yamada_twitter ubuntu@your-server-ip:~/

# 4. デプロイ
cd yamada_twitter
sudo docker-compose --profile production up -d
```

#### E. VPS（さくらのVPS、Vultr等）
```bash
# 1. サーバー基本設定
sudo apt update && sudo apt upgrade -y
sudo ufw allow 22,80,443/tcp
sudo ufw enable

# 2. Docker & Node.js インストール
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. プロジェクト設定
git clone https://github.com/your-username/yamada-twitter.git
cd yamada-twitter
cp .env.example .env.production

# 4. SSL証明書取得（Let's Encrypt）
sudo apt install certbot -y
sudo certbot certonly --standalone -d your-domain.com

# 5. デプロイ
sudo docker-compose --profile production up -d
```

## 🌍 ドメイン・SSL設定

### Let's Encrypt SSL証明書取得
```bash
# 1. Certbot インストール
sudo apt install certbot python3-certbot-nginx -y

# 2. 証明書取得
sudo certbot certonly --standalone \
  -d yamada-twitter.example.com \
  -d www.yamada-twitter.example.com

# 3. nginx.confのSSLパス更新
# ssl_certificate /etc/letsencrypt/live/yamada-twitter.example.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/yamada-twitter.example.com/privkey.pem;

# 4. 自動更新設定
sudo crontab -e
# 以下を追加: 0 3 * * 0 certbot renew --quiet && docker-compose restart nginx
```

## 📊 監視・ログ

### ヘルスチェック
```bash
# アプリケーション状態確認
curl http://your-domain.com/api/health

# Docker コンテナ状態確認
docker-compose ps
docker-compose logs yamada-twitter
```

### ログ確認
```bash
# アプリケーションログ
docker-compose logs -f yamada-twitter

# Nginxログ
docker-compose logs -f nginx

# システムログ
journalctl -u docker.service
```

### パフォーマンス監視
```bash
# リソース使用量確認
docker stats

# データベースサイズ確認
du -h backend/database/yamada_twitter.db

# アクティブ接続数確認
ss -tulpn | grep :3000
```

## 🔒 セキュリティ設定

### ファイアウォール設定
```bash
# UFW設定（Ubuntu）
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 定期バックアップ
```bash
# データベースバックアップスクリプト作成
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp backend/database/yamada_twitter.db "backup/yamada_twitter_$DATE.db"
find backup/ -name "*.db" -mtime +7 -delete

# Cron設定
0 2 * * * /path/to/backup.sh
```

## 🚨 トラブルシューティング

### よくある問題

#### 1. ポート3000が使用中
```bash
# プロセス確認・停止
lsof -ti:3000 | xargs kill -9
```

#### 2. データベース権限エラー
```bash
# 権限修正
sudo chown -R 1001:1001 backend/database/
```

#### 3. WebSocket接続エラー
```bash
# nginx.confのWebSocket設定確認
# proxy_set_header Upgrade $http_upgrade;
# proxy_set_header Connection "upgrade";
```

#### 4. CORS エラー
```bash
# .env.productionの ALLOWED_ORIGINS を確認
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### ログ確認コマンド集
```bash
# 全体ログ
docker-compose logs

# 特定サービスログ（最新100行）
docker-compose logs --tail=100 yamada-twitter

# エラーログのみ
docker-compose logs | grep -i error

# リアルタイム監視
docker-compose logs -f
```

## 📈 運用保守

### 定期メンテナンス
- データベースクリーンアップ: 週1回
- ログローテーション: 日1回
- セキュリティアップデート: 月1回
- バックアップ確認: 週1回

### アップデート手順
```bash
# 1. バックアップ
cp -r yamada_twitter yamada_twitter_backup

# 2. 最新コード取得
git pull origin main

# 3. 依存関係更新
npm update

# 4. 再ビルド・デプロイ
docker-compose build
docker-compose up -d
```

---

## 📞 サポート

デプロイで問題が発生した場合は、以下の情報と一緒にGitHub Issuesに報告してください：

- OS・環境情報
- エラーログ
- 実行したコマンド
- 期待する動作

**🚀 Happy Deployment!**