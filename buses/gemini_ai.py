import os

from dotenv import load_dotenv
from google import genai

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

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
