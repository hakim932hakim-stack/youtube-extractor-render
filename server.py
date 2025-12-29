from flask import Flask, request, jsonify, redirect
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
            'extract_flat': False,
        }
        
        if cookiefile:
            ydl_opts['cookiefile'] = cookiefile
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://youtube.com/watch?v={video_id}', download=False)
            
            return jsonify({
                'success': True,
                'url': info['url'],  # Direkt YouTube URL (eski sistem)
                'title': info.get('title', ''),
                'duration': info.get('duration', 0),
                'quality': info.get('format_note', 'unknown') 
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
