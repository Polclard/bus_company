import os

from google import genai

from bus_company import settings

client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

model="gemini-2.0-flash"

def ask_gemini(question):

    try:
        response = client.models.generate_content(
            model=model, contents=question
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"
