import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
HUGGING_FACE_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")
HUGGING_FACE_API_URL = os.getenv("HUGGING_FACE_API_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = os.getenv("GEMINI_URL")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
ASDCOAPI = os.getenv("ASDCOAPI")

GEMINI_API_KEY1 = os.getenv("GEMINI_API_KEY1")
GEMINI_URL1 = os.getenv("GEMINI_API_URL1")
