#!/usr/bin/env python3
import os
import requests
import subprocess
import tempfile
from pathlib import Path

# APIキーを環境変数から取得
API_KEY = os.getenv('TTS_QUEST_API_KEY')
API_URL = "https://api.tts.quest/v3/voicevox/synthesis"

# デフォルト設定（冥鳴ひまり）
DEFAULT_SPEAKER = 14
DEFAULT_SPEED = 1.0

def speak(text, speaker=DEFAULT_SPEAKER, speed=DEFAULT_SPEED):
    """TTS Quest APIを使用してテキストを音声に変換して再生"""
    
    print(f"🔊 読み上げ中: {text}")
    
    # APIリクエスト
    params = {
        'key': API_KEY,
        'speaker': speaker,
        'speed': speed,
        'text': text
    }
    
    try:
        # APIを呼び出してURLを取得
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        
        # JSONレスポンスを解析
        import json
        data = json.loads(response.text)
        
        if not data.get('success'):
            print(f"❌ API エラー: {data}")
            return False
        
        # MP3ファイルをダウンロード
        mp3_url = data.get('mp3DownloadUrl')
        if not mp3_url:
            print(f"❌ MP3 URLが見つかりません")
            return False
        
        # 音声生成を待つ（最大10秒）
        import time
        for i in range(10):
            audio_response = requests.get(mp3_url)
            if audio_response.status_code == 200:
                break
            elif audio_response.status_code == 404:
                print(f"⏳ 音声生成中... ({i+1}秒)")
                time.sleep(1)
            else:
                audio_response.raise_for_status()
        
        if audio_response.status_code != 200:
            print(f"❌ 音声ファイルの取得に失敗しました")
            return False
        
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(audio_response.content)
            temp_file = f.name
        
        # macOSで再生
        subprocess.run(['afplay', temp_file], check=True)
        
        # 一時ファイルを削除
        os.unlink(temp_file)
        
        print("✅ 再生完了")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ エラー: {e}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ 再生エラー: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSONパースエラー: {e}")
        return False

def listen():
    """macOSの音声入力を使用"""
    print("🎤 音声入力を開始します...")
    print("（fnキーを2回押して音声入力を開始してください）")
    
    # macOSの音声入力を起動
    script = '''
    tell application "System Events"
        key code 63 -- fn key
        delay 0.1
        key code 63 -- fn key again
    end tell
    '''
    subprocess.run(['osascript', '-e', script])
    
    print("音声入力が起動しました。話し終わったらEnterキーを押してください。")
    text = input()
    return text

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # テスト読み上げ
            speak("こんにちは！TTS Questの音声合成テストです。冥鳴ひまりの声で話しています。")
        elif sys.argv[1] == "listen":
            # 音声入力
            text = listen()
            print(f"入力されたテキスト: {text}")
        else:
            # コマンドラインから渡されたテキストを読み上げ
            text = " ".join(sys.argv[1:])
            speak(text)
    else:
        print("使い方:")
        print("  python tts_quest_test.py test       - テスト読み上げ")
        print("  python tts_quest_test.py listen     - 音声入力")
        print("  python tts_quest_test.py <テキスト>  - 指定テキストを読み上げ")