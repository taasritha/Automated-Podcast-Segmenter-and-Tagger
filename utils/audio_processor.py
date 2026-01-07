from pydub import AudioSegment
import os

def process_audio(input_path, output_path="processed_audio.mp3"):
    """
    Performs basic audio processing using pydub:
    - Loads the audio file
    - Converts to mono
    - Normalizes volume
    - Trims silence (optional)
    - Exports processed version as MP3
    
    Args:
        input_path (str): Path to the input audio file
        output_path (str): Path to save processed output file
    
    Returns:
        str: Path to the processed audio file
    """
    try:
        print(f"🎧 Loading audio from: {input_path}")
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1)

        # Normalize volume
        target_dBFS = -20.0
        change_in_dBFS = target_dBFS - audio.dBFS
        audio = audio.apply_gain(change_in_dBFS)

        if len(audio) > 10000:
            audio = audio[5000:-5000]
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        audio.export(output_path, format="mp3")

        print(f"Processed audio saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"Audio processing error: {e}")
        return None
