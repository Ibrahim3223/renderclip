import whisper
import subprocess

def transcribe_audio(video_path):
    model = whisper.load_model("tiny")
    return model.transcribe(video_path)

def find_best_segment(transcript):
    segments = transcript["segments"]
    best = max(segments, key=lambda x: x["avg_logprob"])
    return best["start"], best["end"] - best["start"]

def edit_video(video_path, start, duration):
    output_path = "final.mp4"
    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-ss", str(start),
        "-t", str(duration),
        "-c", "copy", output_path
    ]
    subprocess.run(command, check=True)
    return output_path
