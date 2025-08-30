# Node.js 18 Alpine (軽量)
FROM node:18-alpine

# 作業ディレクトリ設定
WORKDIR /app

# package.jsonをコピー（キャッシュ効率化）
COPY package*.json ./

# 依存関係インストール（本番環境用）
RUN npm ci --only=production && \
    npm cache clean --force

# アプリケーションファイルをコピー
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# データベースディレクトリ作成
RUN mkdir -p backend/database

# 非rootユーザー作成（セキュリティ）
RUN addgroup -g 1001 -S nodejs && \
    adduser -S yamada -u 1001

# ファイル所有権変更
RUN chown -R yamada:nodejs /app
USER yamada

# ポート公開
EXPOSE 3000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# アプリケーション起動
CMD ["node", "backend/server.js"]