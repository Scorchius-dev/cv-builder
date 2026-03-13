import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load the hidden environment variables
load_dotenv()

# 2. Get the key and check if it actually exists
api_key = os.getenv('GEMINI_API_KEY')

if api_key:
    genai.configure(api_key=api_key)
else:
    print("WARNING: GEMINI_API_KEY not found in .env file")


def generate_cover_letter(cv_data, job_description):
    """
    Logic to communicate with Gemini AI.
    Includes error handling to prevent project crashes.
    """
    # If no key, don't even try to call the AI
    if not api_key:
        return "Configuration Error: API Key is missing."

    try:
        # Use the latest stable model
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Structured prompt for better results
        prompt = (
            f"Write a professional cover letter.\n\n"
            f"CV DETAILS:\n{cv_data}\n\n"
            f"JOB DESCRIPTION:\n{job_description}\n\n"
            f"Keep it concise and professional."
        )

        response = model.generate_content(prompt)

        if response and response.text:
            return response.text.strip()

        return "AI returned an empty response."

    except Exception as e:
        # Catch errors and return a message instead of crashing
        return f"AI Error: {str(e)}"
