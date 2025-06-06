from flask import Flask, request, jsonify, send_file
import requests
import threading
import os

app = Flask(__name__)

# ✅ Arka planda video indirme işlemi
def download_and_process(video_url):
    try:
        response = requests.get(video_url)
        if response.status_code != 200:
            print("❌ Failed to download video")
            return

        with open("video.mp4", "wb") as f:
            f.write(response.content)

        print("✅ Video saved successfully.")

        # (İsteğe bağlı) Video işleme aşamaları burada çağrılabilir.
        # transcript = transcribe_audio("video.mp4")
        # start, duration = find_best_segment(transcript)
        # final_path = edit_video("video.mp4", start, duration)

    except Exception as e:
        print("🔥 Background error:", str(e))

# ✅ Anasayfa testi
@app.route("/")
def home():
    return "RenderClip is running!", 200

# ✅ Zapier'den gelen POST isteğini al
@app.route("/upload-url", methods=["POST"])
def upload_url():
    try:
        data = request.get_json(force=True)
        print("DEBUG - Incoming JSON:", data)

        video_url = data.get("url")
        if not video_url:
            return jsonify({"error": "Missing 'url' field"}), 400

        thread = threading.Thread(target=download_and_process, args=(video_url,))
        thread.start()

        return jsonify({"status": "Processing started"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Videoyu indirmek için: /download
@app.route("/download", methods=["GET"])
def download():
    try:
        return send_file("video.mp4", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Render için port tanımı
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
