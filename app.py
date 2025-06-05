from flask import Flask, request, jsonify, send_file
import requests
import os
import whisper
from moviepy.editor import VideoFileClip

app = Flask(__name__)

@app.route("/")
def home():
    return "RenderClip is live!", 200

@app.route("/upload-url", methods=["POST"])
def upload_url():
    try:
        data = request.get_json(force=True)
        print("DEBUG - Incoming JSON:", data)

        video_url = data.get("url")
        if not video_url:
            return jsonify({"error": "Missing 'url' field"}), 400

        # Video indir
        response = requests.get(video_url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to download video"}), 400

        with open("video.mp4", "wb") as f:
            f.write(response.content)

        # Transkripti al
        transcript = transcribe_audio("video.mp4")

        # En iyi kısmı bul
        start, duration = find_best_segment(transcript)

        # Videoyu kes
        final_path = edit_video("video.mp4", start, duration)

        # İndirilebilir link (şimdilik test için)
        return jsonify({"status": "ok", "download_url": request.url_root + "download"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["GET"])
def download():
    return send_file("final.mp4", as_attachment=True)

def transcribe_audio(video_path):
    model = whisper.load_model("base")
    result = model.transcribe(video_path)
    return result["segments"]

def find_best_segment(segments):
    max_words = 0
    best_segment = {"start": 0, "end": 15}

    for segment in segments:
        start = segment["start"]
        end = segment["end"]
        words = len(segment["text"].split())

        if words > max_words and (end - start) >= 5:
            max_words = words
            best_segment = {"start": start, "end": end}

    start_time = int(best_segment["start"])
    duration = int(min(best_segment["end"] - start_time, 15))  # max 15 saniye
    return start_time, duration

def edit_video(video_path, start, duration):
    clip = VideoFileClip(video_path).subclip(start, start + duration)
    clip.write_videofile("final.mp4", codec="libx264", audio_codec="aac")
    return "final.mp4"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
