from flask import Flask, request, jsonify, Response, stream_with_context
import yt_dlp
import os
import requests

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
        
        ydl_opts = {
            'format': 'best[ext=mp4][height<=1080]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        if cookiefile:
            ydl_opts['cookiefile'] = cookiefile
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://youtube.com/watch?v={video_id}', download=False)
            
            # 🔥 YENİ: Proxy URL'i döndür
            return jsonify({
                'success': True,
                'url': f'https://youtube-extractor-render.onrender.com/stream/{video_id}',  # Proxy URL
                'direct_url': info['url'],  # Direkt YouTube URL (fallback için)
                'title': info.get('title', ''),
                'duration': info.get('duration', 0),
                'quality': info.get('format_note', 'unknown') 
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# 🔥 YENİ ENDPOINT: Video Proxy
@app.route('/stream/<video_id>', methods=['GET'])
def stream_video(video_id):
    """
    YouTube videosunu Render üzerinden proxy et (Rave tarzı)
    """
    try:
        cookies_content = os.environ.get('YOUTUBE_COOKIES', '')
        cookiefile = None
        if cookies_content:
            with open('/tmp/cookies.txt', 'w') as f:
                f.write(cookies_content)
            cookiefile = '/tmp/cookies.txt'
        
        ydl_opts = {
            'format': 'best[ext=mp4][height<=1080]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }
        
        if cookiefile:
            ydl_opts['cookiefile'] = cookiefile
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://youtube.com/watch?v={video_id}', download=False)
            youtube_url = info['url']
            
            # YouTube'dan videoyu stream et (proxy)
            def generate():
                with requests.get(youtube_url, stream=True) as r:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
            
            return Response(
                stream_with_context(generate()),
                content_type='video/mp4',
                headers={
                    'Accept-Ranges': 'bytes',
                    'Cache-Control': 'public, max-age=3600'
                }
            )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
