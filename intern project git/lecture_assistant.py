import os
import sys
import argparse
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

def transcribe_audio(client, audio_file_path):
    """Transcribe the audio file using Google Gemini 1.5 Flash."""
    print(f"Uploading and transcribing audio from '{audio_file_path}'...", flush=True)
    
    # Upload the file to Gemini API
    audio_file = client.files.upload(file=audio_file_path)
    print("File uploaded. Generating transcript...", flush=True)
    
    prompt = "Listen to this audio file and provide a highly accurate, word-for-word transcript of what is being spoken. Do not summarize or add external information."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[audio_file, prompt]
    )
    print("Transcription complete!\n", flush=True)
    
    # Delete the file from Google's servers after using it
    client.files.delete(name=audio_file.name)
    
    return response.text

def generate_study_material(client, transcript_text, material_type="notes"):
    """Generate specific study material using Gemini models."""
    print(f"Generating {material_type}...", flush=True)
    
    prompts = {
        "notes": "You are an expert academic assistant. Summarize the following lecture transcript into clear, comprehensive, and well-structured study notes. Highlight key concepts, definitions, and important examples.",
        "quiz": "You are an expert academic assistant. Create a multiple-choice quiz (5 questions) based on the following lecture transcript. Include the correct answers and a brief explanation at the end.",
        "flashcards": "You are an expert academic assistant. Create a set of flashcards (Term: Definition format) based on the key concepts in the following lecture transcript. Format them clearly."
    }
    
    system_prompt = prompts.get(material_type, prompts["notes"])
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"{system_prompt}\n\nHere is the lecture transcript:\n{transcript_text}"
    )
    return response.text

def main():
    parser = argparse.ArgumentParser(description="Lecture Voice-to-Notes Generator")
    parser.add_argument("audio_file", help="Path to the lecture audio file (e.g., mp3, wav, m4a)")
    parser.add_argument("--type", choices=["notes", "quiz", "flashcards", "all"], default="all", help="Type of output to generate")
    parser.add_argument("--out", default="lecture_output.txt", help="Output file path to save the generated content")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio_file):
        print(f"Error: The file '{args.audio_file}' does not exist.")
        sys.exit(1)

    # Initialize Gemini Client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Please ensure your GEMINI_API_KEY environment variable is set in the .env file.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    try:
        # 1. Speech-to-Text: Transcribe the audio
        transcript = transcribe_audio(client, args.audio_file)
        
        output_content = f"--- LECTURE TRANSCRIPT ---\n{transcript}\n\n"
        
        types_to_generate = ["notes", "quiz", "flashcards"] if args.type == "all" else [args.type]
        
        # 2. Generative AI: Summarize into notes, quizzes, or flashcards
        for t in types_to_generate:
            result = generate_study_material(client, transcript, material_type=t)
            if result:
                output_content += f"--- {t.upper()} ---\n{result}\n\n"
        
        # Save the output to a text file
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output_content)
        print(f"\nSuccessfully generated and saved content to '{args.out}'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
