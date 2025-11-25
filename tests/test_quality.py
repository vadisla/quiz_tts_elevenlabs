from quiz_tts_elevenlabs import text_to_speech, create_output_folder, get_output_filename, preprocess_text

print("--- Testing Preprocessing ---")
t1 = "Мне 25 лет"
t2 = "Это короткое предложение"
t3 = "А это вопрос?"

print(f"Original: '{t1}' -> Processed: '{preprocess_text(t1)}'")
print(f"Original: '{t2}' -> Processed: '{preprocess_text(t2)}'")
print(f"Original: '{t3}' -> Processed: '{preprocess_text(t3)}'")

print("\n--- Generating Audio Test ---")
folder = create_output_folder()
fname = folder / "test_quality_25.mp3"
text_to_speech("Мне 25 лет", fname)
print(f"Generated: {fname}")
