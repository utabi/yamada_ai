#!/bin/bash
# AWS EC2 Ubuntu 22.04 LTS セットアップスクリプト
# Yamatter用の本番環境構築

set -e  # エラー時に停止

echo "🚀 Yamatterセットアップ開始..."

# 色付き出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# システムアップデート
echo -e "${YELLOW}📦 システムパッケージを更新中...${NC}"
sudo apt update && sudo apt upgrade -y

# 必要なパッケージインストール
echo -e "${YELLOW}🔧 必要なツールをインストール中...${NC}"
sudo apt install -y \
    curl \
    wget \
    git \
    build-essential \
    nginx \
    certbot \
    python3-certbot-nginx \
    sqlite3 \
    htop \
    ufw

# ファイアウォール設定
echo -e "${YELLOW}🔒 ファイアウォール設定中...${NC}"
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 3000/tcp  # Node.js（開発時のみ、後で閉じる）
sudo ufw --force enable

# Node.js 20.x インストール
echo -e "${YELLOW}📗 Node.js 20.x をインストール中...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# PM2インストール
echo -e "${YELLOW}🔄 PM2プロセスマネージャーをインストール中...${NC}"
sudo npm install -g pm2

# アプリケーションディレクトリ作成
echo -e "${YELLOW}📁 アプリケーションディレクトリ作成中...${NC}"
sudo mkdir -p /var/www/yamatter
sudo mkdir -p /var/log/yamatter
sudo mkdir -p /var/backups/yamatter
sudo chown -R $USER:$USER /var/www/yamatter
sudo chown -R $USER:$USER /var/log/yamatter

# Gitリポジトリクローン（URLを変更してください）
echo -e "${YELLOW}📥 リポジトリをクローン中...${NC}"
cd /var/www
if [ -d "yamatter" ]; then
    echo "既存のディレクトリを削除します..."
    rm -rf yamatter
fi

# ローカルファイルをコピー（開発環境からの移行用）
# git clone https://github.com/yourusername/yamatter.git
echo -e "${GREEN}⚠️  手動でファイルをアップロードしてください:${NC}"
echo "scp -r ~/workspace/yamada/yamada_twitter/* ubuntu@YOUR_EC2_IP:/var/www/yamatter/"
echo "完了したらEnterを押してください..."
read

cd /var/www/yamatter

# logsディレクトリ作成
mkdir -p logs

# 依存関係インストール
echo -e "${YELLOW}📚 NPMパッケージをインストール中...${NC}"
npm install --production

# 環境変数設定
echo -e "${YELLOW}⚙️  環境変数を設定中...${NC}"
cat > .env << EOF
NODE_ENV=production
PORT=3000
HOST=0.0.0.0
DB_PATH=/var/www/yamatter/backend/database/yamada_twitter.db
SESSION_SECRET=$(openssl rand -base64 32)
EOF

# データベースディレクトリの権限設定
mkdir -p backend/database
chmod 755 backend/database

# Nginx設定
echo -e "${YELLOW}🌐 Nginxを設定中...${NC}"
sudo tee /etc/nginx/sites-available/yamatter > /dev/null << 'NGINX'
server {
    listen 80;
    server_name _;  # ドメイン名に変更してください

    client_max_body_size 10M;

    # WebSocketサポート
    location /socket.io/ {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # APIとフロントエンド
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        proxy_buffering off;
    }

    # セキュリティヘッダー
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
NGINX

# Nginx有効化
sudo ln -sf /etc/nginx/sites-available/yamatter /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# PM2でアプリケーション起動
echo -e "${YELLOW}🚀 アプリケーションを起動中...${NC}"
pm2 start ecosystem.config.js --env production
pm2 save

# PM2自動起動設定
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u $USER --hp /home/$USER
pm2 save

# バックアップスクリプト作成
echo -e "${YELLOW}💾 バックアップスクリプトを作成中...${NC}"
cat > ~/backup_yamatter.sh << 'BACKUP'
#!/bin/bash
BACKUP_DIR="/var/backups/yamatter"
DB_FILE="/var/www/yamatter/backend/database/yamada_twitter.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
sqlite3 $DB_FILE ".backup $BACKUP_DIR/yamatter_$DATE.db"
find $BACKUP_DIR -name "yamatter_*.db" -mtime +7 -delete
echo "Backup completed: yamatter_$DATE.db"
BACKUP

chmod +x ~/backup_yamatter.sh

# Cronジョブ設定
echo -e "${YELLOW}⏰ Cronジョブを設定中...${NC}"
(crontab -l 2>/dev/null; echo "0 3 * * * /home/$USER/backup_yamatter.sh >> /var/log/yamatter/backup.log 2>&1") | crontab -

# スワップファイル作成（メモリ不足対策）
if [ ! -f /swapfile ]; then
    echo -e "${YELLOW}💾 スワップファイルを作成中...${NC}"
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# 完了メッセージ
echo -e "${GREEN}✅ セットアップが完了しました！${NC}"
echo ""
echo -e "${GREEN}📋 次のステップ:${NC}"
echo "1. ドメイン名をDNSでこのサーバーのIPに向ける"
echo "2. /etc/nginx/sites-available/yamatter のserver_nameを編集"
echo "3. SSL証明書を取得: sudo certbot --nginx -d your-domain.com"
echo "4. ファイアウォールから開発ポートを削除: sudo ufw delete allow 3000"
echo ""
echo -e "${GREEN}🔍 確認コマンド:${NC}"
echo "- PM2状態: pm2 status"
echo "- ログ確認: pm2 logs"
echo "- Nginx状態: sudo systemctl status nginx"
echo "- アプリ確認: curl http://localhost:3000/api/health"
echo ""
echo -e "${GREEN}🌐 アクセスURL:${NC}"
echo "http://$(curl -s ifconfig.me)"
echo ""
echo -e "${YELLOW}⚠️  重要: 本番環境では必ずSSL証明書を設定してください！${NC}"