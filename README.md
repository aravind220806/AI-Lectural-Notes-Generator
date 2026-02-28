# Lecture Voice-to-Notes Generator

This Python program converts spoken lectures (audio files) into text using OpenAI's Whisper Speech-to-Text AI, and then summarizes the content into clear study notes, quizzes, or flashcards using OpenAI's Generative AI models (GPT-4o-mini).

## Features
- **Speech-to-Text**: High-accuracy transcription of lecture audio (Supports mp3, wav, m4a, etc.).
- **Smart Summarization**: Generates well-structured study notes.
- **Quiz Generation**: Creates a 5-question multiple-choice quiz with answers.
- **Flashcards Generation**: Extracts key terms and definitions into study flashcards.

## Prerequisites

1. Python 3.7+
2. An OpenAI API Key

## Setup

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key as an environment variable. You can do this by creating a `.env` file in the same directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

Run the script from your terminal:

```bash
python lecture_assistant.py path/to/your/lecture_audio.mp3
```

### Options

You can specify what type of content you want to generate using the `--type` flag (choices are `notes`, `quiz`, `flashcards`, or `all`). By default, it generates `all`.

You can also specify the output file name using the `--out` flag.

**Example: Generate only flashcards and save to `biology_flashcards.txt`**
```bash
python lecture_assistant.py my_biology_lecture.mp3 --type flashcards --out biology_flashcards.txt
```
