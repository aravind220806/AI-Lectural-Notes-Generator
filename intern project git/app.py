import os
import secrets
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from google import genai
from dotenv import load_dotenv

# Import functions from lecture_assistant
from lecture_assistant import transcribe_audio, generate_study_material

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB max file size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Gemini Client globally if key is available
api_key = os.getenv("GEMINI_API_KEY")
client = None

if api_key:
    client = genai.Client(api_key=api_key)
else:
    print("Warning: Gemini API key could not be initialized. Please set GEMINI_API_KEY in .env.")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3', 'wav', 'm4a', 'ogg', 'flac'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_audio():
    global client
    # Try to reinitialize in case .env was updated
    if not client:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            client = genai.Client(api_key=api_key)
        else:
            return jsonify({"error": "Gemini API key is missing or invalid on the server. Please set it in your .env file."}), 500

    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided."}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = secrets.token_hex(8) + "_" + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)
        
        try:
            # 1. Transcribe the audio
            transcript = transcribe_audio(client, filepath)
            
            # 2. Generate Materials
            notes = generate_study_material(client, transcript, "notes")
            quiz = generate_study_material(client, transcript, "quiz")
            flashcards = generate_study_material(client, transcript, "flashcards")
            
            # Clean up the uploaded file after processing
            os.remove(filepath)
            
            return jsonify({
                "success": True,
                "transcript": transcript,
                "notes": notes,
                "quiz": quiz,
                "flashcards": flashcards
            })
            
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            error_msg = str(e)
            print(f"API Error: {error_msg}", flush=True)
            return jsonify({"error": f"Transcription Failed: {error_msg}"}), 500
            
    else:
        return jsonify({"error": "Invalid file type. Supported types: mp3, wav, m4a, ogg, flac"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
