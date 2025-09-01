#!/bin/bash

# Git Push Helper - 複数リポジトリを安全に管理
# 使い方: ./git_push_helper.sh [yamada|yamatter|both]

push_yamada_ai() {
    echo "🤖 Pushing yamada_ai repository..."
    cd /Users/claude
    
    # 現在のremote URLを確認
    current_url=$(git remote get-url origin)
    if [[ "$current_url" != *"yamada_ai.git" ]]; then
        echo "⚠️  Wrong remote URL detected! Fixing..."
        git remote set-url origin https://github.com/utabi/yamada_ai.git
    fi
    
    echo "📍 Current directory: $(pwd)"
    echo "🔗 Remote URL: $(git remote get-url origin)"
    
    # git status確認
    git status
    
    read -p "Continue with push? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main
        echo "✅ yamada_ai pushed successfully!"
    else
        echo "❌ Push cancelled"
    fi
}

push_yamatter() {
    echo "🐦 Pushing yamatter-deploy repository..."
    cd /Users/claude/workspace/yamatter-deploy
    
    # 現在のremote URLを確認
    current_url=$(git remote get-url origin)
    if [[ "$current_url" != *"yamatter.git" ]]; then
        echo "⚠️  Wrong remote URL detected! Fixing..."
        git remote set-url origin git@github.com:utabi/yamatter.git
    fi
    
    echo "📍 Current directory: $(pwd)"
    echo "🔗 Remote URL: $(git remote get-url origin)"
    
    # git status確認
    git status
    
    read -p "Continue with push? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main
        echo "✅ yamatter-deploy pushed successfully!"
    else
        echo "❌ Push cancelled"
    fi
}

# メイン処理
case "$1" in
    yamada)
        push_yamada_ai
        ;;
    yamatter)
        push_yamatter
        ;;
    both)
        push_yamada_ai
        echo "---"
        push_yamatter
        ;;
    *)
        echo "📚 Git Repository Push Helper"
        echo "Usage: $0 [yamada|yamatter|both]"
        echo ""
        echo "Repositories:"
        echo "  yamada   - Push yamada_ai (/Users/claude)"
        echo "  yamatter - Push yamatter-deploy (/Users/claude/workspace/yamatter-deploy)"
        echo "  both     - Push both repositories"
        echo ""
        echo "Current status:"
        echo "  yamada_ai: $(cd /Users/claude && git remote get-url origin 2>/dev/null || echo 'Not configured')"
        echo "  yamatter:  $(cd /Users/claude/workspace/yamatter-deploy && git remote get-url origin 2>/dev/null || echo 'Not configured')"
        ;;
esac