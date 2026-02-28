import streamlit as st
import os
import tempfile
from google import genai
from dotenv import load_dotenv

# Import functions from lecture_assistant
from lecture_assistant import transcribe_audio, generate_study_material

# Page Configuration
st.set_page_config(
    page_title="LectureSync AI",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    .stButton>button {
        width: 100%;
        background-image: linear-gradient(90deg, #ff7b72, #d2a8ff);
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(210, 168, 255, 0.3);
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(210, 168, 255, 0.5);
    }
    .title-text {
        text-align: center;
        margin-bottom: 2rem;
    }
    .gradient-text {
        background: linear-gradient(90deg, #ff7b72, #d2a8ff, #79c0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 3.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Initialize Gemini Client
client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing Gemini client: {e}")

# Main App UI
st.markdown("<div class='title-text'><h1><span class='gradient-text'>LectureSync AI</span></h1><p>Upload your lecture audio to instantly generate smart notes, flashcards, and quizzes automatically.</p></div>", unsafe_allow_html=True)

if not api_key:
    st.error("🚨 GEMINI_API_KEY is not set. Please add it to your `.env` file or Streamlit secrets.")
    st.stop()

uploaded_file = st.file_uploader("Upload Audio (MP3, WAV, M4A, OGG)", type=["mp3", "wav", "m4a", "ogg", "flac"])

if uploaded_file is not None:
    # Validate file size (e.g., max 50MB)
    if uploaded_file.size > 50 * 1024 * 1024:
        st.error("File size exceeds the 50MB limit. Please upload a smaller file.")
        st.stop()

    if st.button("✨ Generate Magic ✨"):
        with st.spinner("Processing audio... This might take a minute."):
            try:
                # Save uploaded file to a temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    temp_filepath = tmp_file.name

                st.info("Transcribing audio using Gemini...")
                # 1. Transcribe the audio
                transcript = transcribe_audio(client, temp_filepath)

                st.info("Generating study materials...")
                # 2. Generate Materials
                notes = generate_study_material(client, transcript, "notes")
                flashcards = generate_study_material(client, transcript, "flashcards")
                quiz = generate_study_material(client, transcript, "quiz")

                # Clean up temporary file
                os.unlink(temp_filepath)

                st.success("Generation Complete!")

                # Display Results in Tabs
                tab1, tab2, tab3, tab4 = st.tabs(["Study Notes", "Flashcards", "Quiz", "Raw Transcript"])

                with tab1:
                    st.markdown(notes)
                with tab2:
                    st.markdown(flashcards)
                with tab3:
                    st.markdown(quiz)
                with tab4:
                    with st.expander("Show Transcript"):
                        st.text(transcript)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                # Ensure cleanup if error happens
                if 'temp_filepath' in locals() and os.path.exists(temp_filepath):
                    os.unlink(temp_filepath)
