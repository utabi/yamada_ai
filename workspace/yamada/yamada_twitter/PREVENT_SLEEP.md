# 🚫 スリープを防ぐ方法

## 方法1: UptimeRobot（最も簡単・無料）

### 設定手順
1. [UptimeRobot](https://uptimerobot.com/) にアクセス
2. 無料アカウント作成
3. "Add New Monitor" をクリック
4. 設定:
   - Monitor Type: `HTTP(s)`
   - Friendly Name: `Yamatter`
   - URL: `https://your-app.onrender.com`
   - Monitoring Interval: `5 minutes`
5. "Create Monitor" で完了！

**メリット:**
- ✅ 完全無料（50モニターまで）
- ✅ 5分間隔でチェック
- ✅ ダウンタイム通知
- ✅ 統計ダッシュボード

## 方法2: GitHub Actions（自動化）

### `.github/workflows/keep_alive.yml`
```yaml
name: Keep Alive

on:
  schedule:
    # 10分ごとに実行（UTC時間）
    - cron: '*/10 * * * *'
  workflow_dispatch: # 手動実行も可能

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping Yamatter
        run: |
          curl -I https://your-app.onrender.com
          echo "Pinged at $(date)"
      
      - name: Check Health
        run: |
          response=$(curl -s -o /dev/null -w "%{http_code}" https://your-app.onrender.com/api/health)
          if [ $response -eq 200 ]; then
            echo "✅ Server is healthy"
          else
            echo "⚠️ Server returned: $response"
          fi
```

**メリット:**
- ✅ 完全自動化
- ✅ GitHubに統合
- ✅ 無料（月2000分まで）

## 方法3: Cron-job.org（無料Cronサービス）

### 設定手順
1. [cron-job.org](https://cron-job.org/) で無料アカウント作成
2. "Create Cronjob" をクリック
3. 設定:
   ```
   Title: Yamatter Keep Alive
   URL: https://your-app.onrender.com/api/health
   Schedule: Every 10 minutes
   ```
4. Save で完了！

**メリット:**
- ✅ シンプル
- ✅ 無料
- ✅ メール通知

## 方法4: 自己Ping（アプリ内蔵）

### `backend/server.js` に追加
```javascript
// 自己Pingシステム（本番環境のみ）
if (process.env.NODE_ENV === 'production' && process.env.APP_URL) {
    const keepAlive = () => {
        const https = require('https');
        https.get(process.env.APP_URL + '/api/health', (res) => {
            console.log(`Self-ping: ${res.statusCode}`);
        }).on('error', (err) => {
            console.error('Self-ping error:', err.message);
        });
    };
    
    // 13分ごとに自己Ping
    setInterval(keepAlive, 13 * 60 * 1000);
    
    // 初回実行
    setTimeout(keepAlive, 5000);
}
```

## 方法5: Vercelの相互Ping

2つの無料サービスでお互いをPing:

### Vercel Functions (`api/ping-buddy.js`)
```javascript
export default async function handler(req, res) {
    // Render.comのアプリをping
    const response = await fetch('https://yamatter.onrender.com/api/health');
    
    res.status(200).json({ 
        status: 'alive',
        buddy: response.ok ? 'alive' : 'down'
    });
}
```

### Render側で逆Ping
```javascript
setInterval(async () => {
    await fetch('https://yamatter.vercel.app/api/ping-buddy');
}, 10 * 60 * 1000);
```

## 方法6: 専用Keep-Aliveスクリプト（ローカル実行）

```bash
# ローカルマシンやRaspberry Piで実行
node keep_alive.js https://yamatter.onrender.com

# バックグラウンド実行
nohup node keep_alive.js https://yamatter.onrender.com > keep_alive.log 2>&1 &

# PM2で管理
pm2 start keep_alive.js --name yamatter-keepalive -- https://yamatter.onrender.com
pm2 save
```

## 方法7: Puppeteerで実際のユーザー行動をシミュレート

```javascript
// advanced_keep_alive.js
const puppeteer = require('puppeteer');

async function simulateUser() {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    // サイト訪問
    await page.goto('https://yamatter.onrender.com');
    
    // ランダムな行動
    await page.waitForTimeout(2000);
    
    // ツイート一覧を見る
    await page.click('.tweet:first-child').catch(() => {});
    
    await browser.close();
    console.log('User simulation completed');
}

// 10分ごとに実行
setInterval(simulateUser, 10 * 60 * 1000);
```

## 🏆 推奨構成

### 初心者向け（最も簡単）
```
UptimeRobot（5分間隔）
+ 設定3分で完了
+ メール通知付き
```

### 開発者向け（完全自動）
```
GitHub Actions
+ コード管理と統合
+ 完全無料
```

### プロ向け（100%稼働保証）
```
UptimeRobot（メイン）
+ Cron-job.org（バックアップ）
+ 自己Ping（フェイルセーフ）
```

## ⚠️ 注意事項

1. **無料プランの制限**
   - Render: CPU時間制限あり
   - 過度なPingは避ける（5-10分間隔推奨）

2. **コスト考慮**
   - 常時稼働が必要なら有料プラン検討
   - Render Paid: $7/月で常時稼働

3. **エコシステム**
   - 複数の方法を組み合わせる
   - 冗長性を確保

## 📊 比較表

| 方法 | 難易度 | 信頼性 | コスト | 設定時間 |
|------|--------|--------|--------|----------|
| UptimeRobot | ⭐ | ⭐⭐⭐⭐ | 無料 | 3分 |
| GitHub Actions | ⭐⭐ | ⭐⭐⭐⭐⭐ | 無料 | 10分 |
| Cron-job.org | ⭐ | ⭐⭐⭐ | 無料 | 5分 |
| 自己Ping | ⭐⭐⭐ | ⭐⭐ | 無料 | 15分 |
| Vercel相互 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 無料 | 30分 |
| ローカル実行 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 電気代 | 5分 |

## 🚀 クイックスタート

最速でスリープを防ぐ：

1. **UptimeRobotにサインアップ**（1分）
2. **モニター追加**（2分）
3. **完了！**

これで24時間365日、あなたのYamatterは眠りません！ 💪