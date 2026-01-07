import whisper
import os
import json
from utils.audio_processor import process_audio

model = whisper.load_model("base")

def transcribe_audio(audio_path, episode_id=None):
    """
    Transcribes the given audio file using Whisper.
    Saves transcript and segments to cache/{episode_id}.json if episode_id is provided.
    
    Args:
        audio_path (str): Path to local audio file.
        episode_id (str): Unique ID for the episode (used for cache filename).
    
    Returns:
        tuple: (transcript_text, segments_list)
    """
    try:
        print(f"🎧 Transcribing: {audio_path}")
        result = model.transcribe(audio_path, verbose=False)

        transcript = result.get("text", "")
        segments = result.get("segments", [])

        segs = [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"]
            }
            for seg in segments
        ]
        if episode_id:
            cache_dir = "cache"
            os.makedirs(cache_dir, exist_ok=True)

            cache_path = os.path.join(cache_dir, f"{episode_id}.json")
            cache_data = {
                "episode_id": episode_id,
                "transcript": transcript,
                "segments": segs
            }

            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=4, ensure_ascii=False)

            print(f"Transcript cached at: {cache_path}")

        return transcript, segs

    except Exception as e:
        print(f"Whisper transcription error: {e}")
        return "", []
