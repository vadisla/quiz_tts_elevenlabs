# Quiz TTS ElevenLabs

A Python CLI tool for generating audio from text files and Google Sheets using the ElevenLabs API.

## Features

- 🎙️ **Interactive CLI Menu** - Easy-to-use command-line interface
- 📄 **Text File Processing** - Drag-and-drop support with automatic paragraph splitting
- 📊 **Google Sheets Quiz Mode** - Parse quiz data and generate audio for questions and answers
- 🔊 **High-Quality TTS** - Uses ElevenLabs API with optimized voice settings
- 🔢 **Smart Text Processing** - Automatic numeral-to-word conversion for Russian
- 📁 **Organized Output** - Saves files to dated folders on Desktop

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/vadisla/quiz-tts-elevenlabs.git
   cd quiz-tts-elevenlabs
   ```

2. Create virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

3. Set up your ElevenLabs API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

## Usage

### Interactive Mode
```bash
python quiz_tts_elevenlabs.py
```

### Command Line
```bash
# Simple text
python quiz_tts_elevenlabs.py "Hello world"

# Parse Google Sheet
python quiz_tts_elevenlabs.py -s "https://docs.google.com/spreadsheets/d/..."
```

### Alias Setup
For quick access, add an alias to your shell:
```bash
alias voice="/path/to/venv/bin/python /path/to/quiz_tts_elevenlabs.py"
```

## Requirements

- Python 3.8+
- ElevenLabs API key
- Dependencies listed in `requirements.txt`

## License

MIT
