import os
import sys
from elevenlabs.client import ElevenLabs
from elevenlabs import save

def text_to_speech(text: str, output_filename: str = "output.mp3"):
    """
    Converts text to speech using ElevenLabs API and saves to a file.
    """
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable not set.")
        print("Please set it using: export ELEVENLABS_API_KEY='your_key'")
        sys.exit(1)

    try:
        client = ElevenLabs(api_key=api_key)
        
        print(f"Generating audio for: '{text}'...")
        audio = client.generate(
            text=text,
            voice="Rachel",
            model="eleven_multilingual_v2"
        )
        
        save(audio, output_filename)
        print(f"Audio saved to {output_filename}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
    else:
        input_text = "Hello! This is a test of the ElevenLabs text to speech API."
        
    text_to_speech(input_text)
