import os
from flask import Flask, render_template, request, send_file
import yt_dlp

app = Flask(__name__)

# Fungsi untuk mengunduh video TikTok
def download_tiktok_video(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_filename = ydl.prepare_filename(info_dict)
        return video_filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if url:
            try:
                video_file = download_tiktok_video(url)
                return send_file(video_file, as_attachment=True)
            except Exception as e:
                return f"Error: {str(e)}"
    return render_template('index.html')

if __name__ == "__main__":
    port = os.getenv('PORT', 5000)  # Menggunakan port yang disediakan oleh Render
    app.run(host='0.0.0.0', port=port)  # Memastikan aplikasi mendengarkan di port yang benar
