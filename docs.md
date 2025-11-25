# Quiz TTS ElevenLabs

A Python CLI tool for generating audio from text and Google Sheets using ElevenLabs API. It is structured for easy usage and extension.

## Setup

1.  **Environment**:
    The project uses a virtual environment located in `venv/`.
    Activate it:
    ```bash
    source venv/bin/activate
    ```

2.  **Dependencies**:
    Dependencies are listed in `requirements.txt`.
    Install them:
    ```bash
    pip install -r requirements.txt
    ```

3.  **API Key**:
    You must set the `ELEVENLABS_API_KEY` environment variable.
    ```bash
    export ELEVENLABS_API_KEY='your_api_key'
    ```

## Features

- **Interactive Menu**: Run `voice` (or `python quiz_tts_elevenlabs.py`) without arguments.
- **Text File Processing**:
    - Drag-and-drop support for text files.
    - Automatically splits text by paragraphs (empty lines).
    - Saves each paragraph as a separate audio file: `{filename}_paragraph_{n}.mp3`.
- **Google Sheets Quiz Mode**:
    - Parses a specific sheet structure (Questions in Col J, Intro in Col M, Answer in Col N).
    - Merges Intro and Answer into a single file.
    - Saves files to `~/Desktop/voice_YYYY-MM-DD/`.
- **Voice Selection**: Defaults to "ANDRew", configurable via `-v`.
- **Quality Improvements**:
    - Automatic conversion of numerals to Russian words (25 → "двадцать пять").
    - Enforced terminal punctuation for better intonation.
    - Optimized voice stability (0.65) for consistent, natural speech.

## Setup Alias

Run the script from the `quiz_tts_elevenlabs` directory.

1. Run the setup script:
   ```bash
   ./setup_alias.sh
   ```
2. Restart your terminal or run `source ~/.zshrc`.
3. Type `voice` to start!

## Usage

### Interactive Mode
```bash
voice
```
Select option 2 for Google Sheets Quiz parsing.

### Command Line
```bash
# Simple text
voice "Hello world"

# Parse Google Sheet (defaults to 7 rounds, 7 questions)
voice -s "https://docs.google.com/spreadsheets/d/..."
```

### Manual Run
```bash
python quiz_tts_elevenlabs.py "Hello world"
```

## Development Log

- **Initial Setup**: Created project structure, initialized git, set up venv.
- **Implementation**: Created `main.py` with `argparse` for CLI support.
