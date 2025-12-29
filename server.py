from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract():
    try:
        data = request.json
        video_id = data.get('videoId')
        
        if not video_id:
            return jsonify({'success': False, 'error': 'videoId required'}), 400
        
        # Cookies'i environment variable'dan al
        cookies_content = os.environ.get('YOUTUBE_COOKIES', '')
        
        # Geçici cookies.txt oluştur
        cookiefile = None
        if cookies_content:
            with open('/tmp/cookies.txt', 'w') as f:
                f.write(cookies_content)
            cookiefile = '/tmp/cookies.txt'
        
        # GÜNCELLENMİŞ AYARLAR (NATIVE PLAYER İÇİN OPTİMİZE EDİLDİ)
        ydl_opts = {
            # 1. Öncelik: MP4 formatında, video+ses birleşik, max 1080p
            # 2. Öncelik: Herhangi bir MP4
            # Bu, 1080p yoksa 720p, yoksa 360p verir ama kesinlikle MP4 verir.
            'format': 'best[ext=mp4][height<=1080]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        if cookiefile:
            ydl_opts['cookiefile'] = cookiefile
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://youtube.com/watch?v={video_id}', download=False)
            
            return jsonify({
                'success': True,
                'url': info['url'],
                'title': info.get('title', ''),
                'duration': info.get('duration', 0)
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
