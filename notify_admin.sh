#!/bin/bash

# Claude管理者通知スクリプト
# 用途: 重要なメッセージを管理者に通知

# 通知機能
send_notification() {
    local title="$1"
    local message="$2"
    local sound="${3:-Glass}"
    
    osascript -e "display notification \"$message\" with title \"$title\" sound name \"$sound\""
}

# デスクトップメッセージ作成
create_desktop_message() {
    local title="$1"
    local content="$2"
    local timestamp=$(date "+%Y年%m月%d日 %H:%M:%S")
    
    cat > ~/Desktop/Claude_重要通知_$(date +%Y%m%d_%H%M%S).txt << EOF
=====================================
$title
=====================================
日時: $timestamp

$content

=====================================
[このメッセージはClaudeから自動生成されました]
EOF
}

# ログファイル記録
log_message() {
    local message="$1"
    local logfile=~/Documents/claude_communication_log.txt
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message" >> "$logfile"
}

# メイン処理
main() {
    local action="$1"
    local title="$2"
    local message="$3"
    
    case "$action" in
        notify)
            send_notification "$title" "$message"
            ;;
        desktop)
            create_desktop_message "$title" "$message"
            ;;
        log)
            log_message "$title: $message"
            ;;
        all)
            send_notification "$title" "$message"
            create_desktop_message "$title" "$message"
            log_message "$title: $message"
            ;;
        *)
            echo "使用方法: $0 {notify|desktop|log|all} \"タイトル\" \"メッセージ\""
            exit 1
            ;;
    esac
}

# 引数チェック
if [ $# -lt 3 ]; then
    echo "使用方法: $0 {notify|desktop|log|all} \"タイトル\" \"メッセージ\""
    exit 1
fi

main "$@"