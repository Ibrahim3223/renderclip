from flask import Flask, request, jsonify, send_file
import requests
import os
from utils import transcribe_audio, find_best_segment, edit_video

app = Flask(__name__)

@app.route("/")
def home():
    return "RenderClip is running!", 200

@app.route("/upload-url", methods=["POST"])
def upload_url():
    try:
        data = request.get_json(force=True)
        print("DEBUG - Incoming JSON:", data)

        video_url = data.get("url")
        if not video_url:
            return jsonify({"error": "Missing 'url' field"}), 400

        response = requests.get(video_url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to download video"}), 400

        with open("video.mp4", "wb") as f:
            f.write(response.content)

        # 🔁 Transcribe & edit
        transcript = transcribe_audio("video.mp4")
        start, duration = find_best_segment(transcript)
        final_path = edit_video("video.mp4", start, duration)

        return jsonify({
            "status": "Success",
            "download_url": request.url_root + "download"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["GET"])
def download():
    return send_file("final.mp4", as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
