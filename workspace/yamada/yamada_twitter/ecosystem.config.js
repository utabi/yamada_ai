module.exports = {
  apps: [{
    name: 'yamatter',
    script: './backend/server.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000,
      HOST: '0.0.0.0'
    },
    env_development: {
      NODE_ENV: 'development',
      PORT: 3000,
      HOST: 'localhost'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    time: true,
    max_memory_restart: '500M',
    autorestart: true,
    watch: false,
    max_restarts: 10,
    min_uptime: '10s',
    // クラスター設定
    listen_timeout: 3000,
    kill_timeout: 5000,
    // 正常性チェック
    wait_ready: true,
    // CPU使用率監視
    cron_restart: '0 3 * * *' // 毎日午前3時に再起動
  }]
};