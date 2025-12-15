import os
import sys
import argparse
import csv
import requests
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import save

# Load environment variables from .env file
load_dotenv()

DEFAULT_VOICE_ID = "yfwJfbXlpnn3qMSjFykp" # ANDRew

# Voice mapping for different languages
VOICE_MAP = {
    'ru': 'yfwJfbXlpnn3qMSjFykp',  # ANDRew (Russian)
    'pl': 'eJLcDj3fKW65V8WhDqPI',  # Polish male voice
    'lt': 'pNInz6obpgDQGcFmaJgB'   # Adam (Lithuanian)
}

def get_desktop_path():
    """Returns the path to the user's Desktop."""
    return Path.home() / "Desktop"

def create_output_folder(custom_name: str = None):
    """Creates a folder on the Desktop with the current date and optional custom name."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    if custom_name:
        # Sanitize custom name for filesystem
        safe_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in custom_name)
        folder_name = f"voice_{safe_name}_{date_str}"
    else:
        folder_name = f"voice_{date_str}"
    path = get_desktop_path() / folder_name
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_output_filename(folder_path):
    """Generates a timestamped filename in the given folder."""
    timestamp = datetime.now().strftime("%H-%M-%S")
    return folder_path / f"audio_{timestamp}.mp3"

import pandas as pd
import io

# ... (previous imports and constants)

def parse_quiz_sheet(url: str, sheet_name: str = "Верстка", rounds_count: int = 7, questions_per_round: int = 7, voice: str = DEFAULT_VOICE_ID):
    """
    Parses the quiz sheet and generates audio for questions, intros, and answers.
    Structure:
    - Starts at row 3 (index 2).
    - Block of `questions_per_round` rows.
    - 1 empty row skip.
    - Repeat for `rounds_count`.
    - Columns: J (Question), M (Intro), N (Answer).
    """
    try:
        # 1. Download Sheet
        if "/d/" not in url:
            print("❌ Invalid Google Sheet URL.")
            return

        # Fix export URL for XLSX
        export_url = url.replace("/edit", "/export").replace("?usp=sharing", "?format=xlsx")
        if "format=xlsx" not in export_url:
             export_url += "?format=xlsx"
        
        print(f"Downloading data from Sheet (XLSX)...")
        response = requests.get(export_url)
        response.raise_for_status()
        
        # 2. Load into Pandas using openpyxl
        # sheet_name argument allows us to pick the specific sheet!
        excel_file = pd.ExcelFile(io.BytesIO(response.content))
        
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        except ValueError as e:
            print(f"❌ Sheet '{sheet_name}' not found. Available sheets: {excel_file.sheet_names}")
            return


        # Extract document title from Google Sheets HTML page
        try:
            # Get the document ID from URL
            doc_id = url.split("/d/")[1].split("/")[0]
            html_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/edit"
            html_response = requests.get(html_url)
            
            # Extract title from HTML (it's in the <title> tag)
            import re
            title_match = re.search(r'<title>(.+?)</title>', html_response.text)
            if title_match:
                # Google Sheets adds " - Google Sheets" to the title, remove it
                doc_title = title_match.group(1).replace(" - Google Таблицы", "").replace(" - Google Sheets", "").strip()
            else:
                doc_title = "GoogleSheet"
        except Exception as e:
            print(f"⚠️ Could not extract document title: {e}")
            doc_title = "GoogleSheet"


        # 3. Define Column Indices (0-based)
        # J is 10th letter -> index 9
        # M is 13th letter -> index 12
        # N is 14th letter -> index 13
        COL_Q = 9
        COL_INTRO = 12
        COL_ANSWER = 13
        
        # 4. Iterate Rounds
        current_row = 2 # Start at J3 (row 3 -> index 2)
        
        folder_path = create_output_folder(doc_title)
        print(f"📂 Output folder: {folder_path}")

        for round_num in range(1, rounds_count + 1):
            print(f"\n--- Round {round_num} ---")
            
            for q_num in range(1, questions_per_round + 1):
                # Check if row exists
                if current_row >= len(df):
                    print("⚠️ End of sheet reached unexpectedly.")
                    break
                
                # Extract text
                # Use .iloc for safe access, handle NaN
                def get_text(col_idx):
                    if col_idx >= df.shape[1]: return ""
                    val = df.iloc[current_row, col_idx]
                    return str(val).strip() if pd.notna(val) else ""

                q_text = get_text(COL_Q)
                intro_text = get_text(COL_INTRO)
                answer_text = get_text(COL_ANSWER)
                
                # Generate Audio if text exists
                # Filename format: round_{r}_q_{q}_{type}.mp3
                
                if q_text:
                    fname = folder_path / f"round_{round_num}_q_{q_num}_question.mp3"
                    print(f"  🔊 Question {q_num}: {q_text[:30]}...")
                    text_to_speech(q_text, fname, voice)
                
                # Combine Intro (M) and Answer (N)
                combined_answer = ""
                if intro_text and answer_text:
                    combined_answer = f"{intro_text} {answer_text}"
                elif intro_text:
                    combined_answer = intro_text
                elif answer_text:
                    combined_answer = answer_text
                    
                if combined_answer:
                    fname = folder_path / f"round_{round_num}_q_{q_num}_answer.mp3"
                    print(f"  🔊 Answer {q_num} (Merged): {combined_answer[:30]}...")
                    text_to_speech(combined_answer, fname, voice)

                current_row += 1
            
            # Smart seek: Find the next row where Column J (index 9) is not empty
            # But we must be careful not to skip valid questions if we are just starting a new round.
            # The logic above iterates `questions_per_round` times. After that, we need to skip empty rows until we hit text again.
            
            print("  ... Seeking next round ...")
            while current_row < len(df):
                q_val = df.iloc[current_row, COL_Q]
                if pd.notna(q_val):
                    val_str = str(q_val).strip()
                    # Check if it has content AND is not a header row (like "ТУР 7")
                    if val_str and not val_str.lower().startswith(("тур", "round")):
                        # Found text! This is likely the start of the next round.
                        break
                current_row += 1

    except Exception as e:
        print(f"❌ Error parsing sheet: {e}")

import re
from num2words import num2words
from elevenlabs import VoiceSettings

# ... (previous imports and constants)

def preprocess_text(text: str) -> str:
    """
    Preprocesses text to improve TTS quality:
    1. Converts numbers to Russian words.
    2. Enforces terminal punctuation for better intonation.
    """
    if not text:
        return ""
        
    # 1. Convert numbers to words (Russian)
    # Find all numbers and replace them
    # def replace_num(match):
    #     return num2words(match.group(), lang='ru')
    
    # text = re.sub(r'\d+', replace_num, text)
    
    # 2. Enforce terminal punctuation
    # If text doesn't end with . ! or ?, add a period.
    if text and text[-1] not in ".!?":
        # Check for common question words (Russian)
        question_words = ["кто", "что", "где", "когда", "почему", "как", "зачем", "сколько", "какой", "чей", "чья", "чье", "чьи"]
        first_word = text.split()[0].lower().strip(".,!?") if text.split() else ""
        
        if first_word in question_words:
            text += "?"
        else:
            text += "."
        
    return text

def text_to_speech(text: str, output_filename: Path, voice: str = DEFAULT_VOICE_ID):
    """
    Converts text to speech using ElevenLabs API and saves to a file.
    """
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable not set.")
        return

    try:
        # Preprocess text for better quality
        processed_text = preprocess_text(text)
        # print(f"DEBUG: Processed text: '{processed_text}'") 

        client = ElevenLabs(api_key=api_key)
        
        # Resolve voice (simplified for speed in loop)
        # We assume DEFAULT_VOICE_ID is correct or passed correctly
        
        # Dynamic settings: Improve intonation for questions
        # Default settings
        stability = 0.65
        style = 0.0
        
        # If it's a question, allow more variability
        if "?" in processed_text:
            # print("  Mood: Question 🤔")
            stability = 0.50  # Lower stability = more emotion/range
            style = 0.35      # Higher style = more expressive

        voice_settings = VoiceSettings(
            stability=stability, 
            similarity_boost=0.75,
            style=style,
            use_speaker_boost=True
        )
        
        audio = client.text_to_speech.convert(
            text=processed_text,
            voice_id=voice,
            model_id="eleven_multilingual_v2",
            voice_settings=voice_settings
        )
        
        save(audio, str(output_filename))
        # print(f"✅ Saved: {output_filename.name}") # Reduced verbosity
        
    except Exception as e:
        print(f"❌ TTS Error: {e}")

def process_text_file(file_path: str, voice: str = DEFAULT_VOICE_ID):
    """
    Processes a text file by splitting it into paragraphs and generating audio for each.
    Paragraphs are detected by empty lines (double newline).
    """
    try:
        # Read the file
        file_path = file_path.strip().strip("'\"").replace(r'\ ', ' ')  # Remove quotes and unescape spaces
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            print(f"❌ File not found: {file_path}")
            return
            
        print(f"📄 Reading file: {path_obj.name}")
        
        with open(path_obj, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by empty lines (one or more blank lines)
        paragraphs = re.split(r'\n\s*\n', content)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        if not paragraphs:
            print("❌ No text found in file.")
            return
        
        print(f"Found {len(paragraphs)} paragraph(s)")
        
        # Get base filename (without extension)
        base_name = path_obj.stem
        
        # Generate audio for each paragraph
        folder = create_output_folder()
        print(f"📂 Output folder: {folder}")
        
        for i, para in enumerate(paragraphs, 1):
            fname = folder / f"{base_name}_paragraph_{i}.mp3"
            print(f"  🔊 Paragraph {i}/{len(paragraphs)}: {para[:50]}...")
            text_to_speech(para, fname, voice)
        
        print(f"✅ Generated {len(paragraphs)} audio file(s)")
        
    except Exception as e:
        print(f"❌ Error processing text file: {e}")

def select_language():
    """
    Prompts user to select a language and returns the corresponding voice ID.
    """
    print("\n🌍 Select language / Wybierz język / Pasirinkite kalbą:")
    print("1. Русский (Russian)")
    print("2. Polski (Polish)")
    print("3. Lietuvių (Lithuanian)")
    
    while True:
        choice = input("Language (1-3): ").strip()
        if choice == "1":
            return VOICE_MAP['ru']
        elif choice == "2":
            return VOICE_MAP['pl']
        elif choice == "3":
            return VOICE_MAP['lt']
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")

def interactive_menu():
    """Runs the interactive CLI menu."""
    # Select language once at the start
    selected_voice = select_language()
    
    while True:
        print("\n--- 🎙️ ElevenLabs TTS CLI ---")
        print("1. Read from text file")
        print("2. Parse Quiz from Google Sheet")
        print("3. Exit")
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == "1":
            print("\n📁 Drag and drop your text file here (or paste the path):")
            file_path = input("File path: ").strip()
            if file_path:
                process_text_file(file_path, voice=selected_voice)
        elif choice == "2":
            url = input("Enter Google Sheet URL: ").strip()
            if url:
                try:
                    r_count = int(input("Rounds count (default 7): ") or 7)
                    q_count = int(input("Questions per round (default 7): ") or 7)
                    parse_quiz_sheet(url, rounds_count=r_count, questions_per_round=q_count, voice=selected_voice)
                except ValueError:
                    print("Invalid number.")
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

def main():
    parser = argparse.ArgumentParser(description="ElevenLabs Text-to-Speech Converter")
    parser.add_argument("text", nargs="?", help="Text to convert to speech")
    parser.add_argument("-s", "--sheet", help="Google Sheet URL to parse (Quiz Mode)")
    parser.add_argument("-v", "--voice", default=DEFAULT_VOICE_ID, help=f"Voice ID or name (default: {DEFAULT_VOICE_ID})")
    
    args = parser.parse_args()

    if args.sheet:
        # If CLI args used, use defaults for rounds/questions or add more args?
        # For simplicity, let's use defaults 7/7 if running from CLI non-interactively
        parse_quiz_sheet(args.sheet)
    elif args.text:
        text_to_speech(args.text, get_output_filename(create_output_folder()), args.voice)
    else:
        # Interactive mode
        interactive_menu()

if __name__ == "__main__":
    main()
