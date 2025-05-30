import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

model="gemini-2.0-flash"

def ask_gemini(question):

    try:
        response = client.models.generate_content(
            model=model, contents=question
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"
