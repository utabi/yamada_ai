# AWS EC2 デプロイメントガイド

## 1. EC2インスタンスの推奨設定

### インスタンスタイプ
```
推奨: t3.micro または t3.small
- t3.micro: 開発・テスト環境（無料枠対象）
  - vCPU: 2
  - メモリ: 1GB
  - ネットワーク: 最大5Gbps
  
- t3.small: 小規模本番環境
  - vCPU: 2
  - メモリ: 2GB
  - ネットワーク: 最大5Gbps
```

### OS選択
```
推奨: Ubuntu 22.04 LTS または Amazon Linux 2023
- Ubuntu 22.04 LTS: 広範なサポート、使いやすい
- Amazon Linux 2023: AWS最適化、セキュリティ強化
```

### ストレージ
```
- タイプ: gp3 (General Purpose SSD)
- サイズ: 20GB（最小8GB）
- IOPS: 3000（デフォルト）
```

## 2. セキュリティグループ設定

```yaml
インバウンドルール:
  - SSH:
    - ポート: 22
    - ソース: あなたのIP（または踏み台サーバー）
  
  - HTTP:
    - ポート: 80
    - ソース: 0.0.0.0/0（全世界）
  
  - HTTPS:
    - ポート: 443
    - ソース: 0.0.0.0/0（全世界）
  
  - カスタムTCP（開発時のみ）:
    - ポート: 3000
    - ソース: あなたのIP

アウトバウンドルール:
  - すべてのトラフィック許可（デフォルト）
```

## 3. EC2セットアップスクリプト

```bash
#!/bin/bash
# setup_ec2.sh - EC2初期セットアップスクリプト

# システムアップデート
sudo apt update && sudo apt upgrade -y

# 必要なパッケージインストール
sudo apt install -y \
    curl \
    git \
    build-essential \
    nginx \
    certbot \
    python3-certbot-nginx \
    sqlite3

# Node.js 20.x インストール
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# PM2インストール（プロセスマネージャー）
sudo npm install -g pm2

# アプリケーションディレクトリ作成
sudo mkdir -p /var/www/yamatter
sudo chown -R ubuntu:ubuntu /var/www/yamatter

# Gitからクローン
cd /var/www
git clone https://github.com/yourusername/yamatter.git
cd yamatter

# 依存関係インストール
npm install

# 環境変数設定
cat > .env << EOF
NODE_ENV=production
PORT=3000
HOST=0.0.0.0
EOF

# PM2でアプリケーション起動
pm2 start ecosystem.config.js
pm2 save
pm2 startup systemd -u ubuntu --hp /home/ubuntu
```

## 4. PM2設定ファイル

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'yamatter',
    script: './backend/server.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    max_memory_restart: '500M',
    autorestart: true,
    watch: false
  }]
};
```

## 5. Nginx設定

```nginx
# /etc/nginx/sites-available/yamatter
server {
    listen 80;
    server_name your-domain.com;

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
        
        # タイムアウト設定
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # バッファ設定
        proxy_buffering off;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }

    # 静的ファイルキャッシュ
    location ~* \.(jpg|jpeg|gif|png|css|js|ico|xml)$ {
        proxy_pass http://localhost:3000;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # セキュリティヘッダー
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

## 6. SSL証明書設定（Let's Encrypt）

```bash
# ドメイン名を設定後
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自動更新設定
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## 7. データベースバックアップ設定

```bash
#!/bin/bash
# backup.sh - 毎日実行するバックアップスクリプト

BACKUP_DIR="/var/backups/yamatter"
DB_FILE="/var/www/yamatter/backend/database/yamada_twitter.db"
DATE=$(date +%Y%m%d_%H%M%S)

# バックアップディレクトリ作成
mkdir -p $BACKUP_DIR

# SQLiteデータベースバックアップ
sqlite3 $DB_FILE ".backup $BACKUP_DIR/yamatter_$DATE.db"

# 7日以上古いバックアップを削除
find $BACKUP_DIR -name "yamatter_*.db" -mtime +7 -delete

# S3にアップロード（オプション）
# aws s3 cp $BACKUP_DIR/yamatter_$DATE.db s3://your-backup-bucket/
```

## 8. Cronジョブ設定

```bash
# crontab -e で追加
# 毎日午前3時にバックアップ
0 3 * * * /home/ubuntu/backup.sh

# 監視スクリプト（5分ごと）
*/5 * * * * cd /var/www/yamatter && /usr/bin/python3 yamatter_monitor.py >> /var/log/yamatter_monitor.log 2>&1
```

## 9. CloudWatch監視設定

```bash
# CloudWatch エージェントインストール
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# 設定ファイル
sudo cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << EOF
{
  "metrics": {
    "namespace": "Yamatter",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {"name": "cpu_usage_idle", "rename": "CPU_IDLE", "unit": "Percent"}
        ],
        "totalcpu": false
      },
      "disk": {
        "measurement": [
          {"name": "used_percent", "rename": "DISK_USED", "unit": "Percent"}
        ],
        "resources": ["/"],
        "ignore_file_system_types": ["sysfs", "devtmpfs"]
      },
      "mem": {
        "measurement": [
          {"name": "mem_used_percent", "rename": "MEM_USED", "unit": "Percent"}
        ]
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/www/yamatter/logs/combined.log",
            "log_group_name": "/aws/ec2/yamatter",
            "log_stream_name": "{instance_id}/app"
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_name": "/aws/ec2/yamatter",
            "log_stream_name": "{instance_id}/nginx-error"
          }
        ]
      }
    }
  }
}
EOF

# エージェント起動
sudo systemctl enable amazon-cloudwatch-agent
sudo systemctl start amazon-cloudwatch-agent
```

## 10. 本番環境用の環境変数

```bash
# .env.production
NODE_ENV=production
PORT=3000
HOST=0.0.0.0

# データベース
DB_PATH=/var/www/yamatter/backend/database/yamada_twitter.db

# レート制限（本番環境）
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX=100

# CORS設定
CORS_ORIGIN=https://your-domain.com

# セッション設定
SESSION_SECRET=your-random-session-secret-here

# ログレベル
LOG_LEVEL=info
```

## 11. デプロイ手順

```bash
# 1. EC2インスタンス作成
#    - t3.microを選択
#    - Ubuntu 22.04 LTS
#    - セキュリティグループ設定
#    - キーペア作成/選択

# 2. SSHで接続
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. セットアップスクリプト実行
bash setup_ec2.sh

# 4. Nginx設定
sudo ln -s /etc/nginx/sites-available/yamatter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 5. SSL証明書取得（ドメイン設定後）
sudo certbot --nginx

# 6. アプリケーション起動確認
pm2 status
pm2 logs

# 7. ブラウザでアクセス確認
# http://your-ec2-ip:3000 (開発)
# https://your-domain.com (本番)
```

## 12. コスト最適化

### 月額見積もり（東京リージョン）
```
t3.micro（無料枠内）:
- インスタンス: $0（12ヶ月無料）
- ストレージ(20GB): 約$2
- データ転送: 約$1-5（使用量による）
合計: 約$3-7/月

t3.small（無料枠後）:
- インスタンス: 約$15
- ストレージ(20GB): 約$2
- データ転送: 約$1-5
合計: 約$18-22/月
```

### コスト削減のヒント
1. 無料枠を最大限活用（最初の12ヶ月）
2. リザーブドインスタンスで最大72%削減
3. オートスケーリングで需要に応じて調整
4. CloudFrontでキャッシュ活用
5. S3で静的ファイルホスティング

## トラブルシューティング

### よくある問題と解決策

1. **502 Bad Gateway**
```bash
# PM2再起動
pm2 restart yamatter
# Nginx再起動
sudo systemctl restart nginx
```

2. **WebSocket接続エラー**
```bash
# Nginxの設定確認
sudo nginx -t
# WebSocketプロキシ設定確認
```

3. **メモリ不足**
```bash
# スワップファイル作成
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

これで本番環境の準備完了です！