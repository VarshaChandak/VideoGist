import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

load_dotenv()  # Load environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing the important points in less than 250 words.
Please provide the summary of the text given here: """

# Function to extract transcript details
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript

    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

# Helper function to extract video id
def extract_video_id(url):
    """Extract the video ID from YouTube URL."""
    parsed_url = urlparse(url)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    if parsed_url.hostname in ("www.youtube.com", "youtube.com"):
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query)["v"][0]
        if parsed_url.path.startswith("/embed/"):
            return parsed_url.path.split("/")[2]
        if parsed_url.path.startswith("/v/"):
            return parsed_url.path.split("/")[2]
    raise ValueError("Invalid YouTube URL format")

# Function to generate summary using Gemini
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit UI
st.title("🎬 YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    try:
        video_id = extract_video_id(youtube_link)
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except Exception as e:
        st.error(f"Invalid YouTube link: {e}")

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## ✍️ Detailed Notes:")
        st.markdown(summary)
