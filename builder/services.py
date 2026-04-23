"""AI service helpers for generating tailored cover letters."""

import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv('GEMINI_API_KEY')
_client = genai.Client(api_key=_api_key) if _api_key else None

if not _api_key:
    print('WARNING: GEMINI_API_KEY not found in .env file')


def generate_cover_letter(cv_data, job_description):
    """Generate a job-specific cover letter from CV data + job description."""

    if not _client:
        return (
            'Configuration Error: GEMINI_API_KEY is missing '
            'from your .env file.'
        )

    prompt = (
        'You are an expert cover letter writer. '
        'Write a professional, personalised cover letter tailored '
        'to the specific job below. Use the candidate\'s real '
        'details and achievements — do not invent facts.\n\n'
        f'CANDIDATE CV:\n{cv_data}\n\n'
        f'JOB DESCRIPTION:\n{job_description}\n\n'
        'INSTRUCTIONS:\n'
        '- Write in first person, confident and professional tone\n'
        '- Open with a hook that specifically references the role '
        'and company — avoid "I am writing to apply"\n'
        '- Highlight 2\u20133 specific experiences or achievements '
        'from the CV that match the requirements\n'
        '- Show genuine enthusiasm for the company and role\n'
        '- Close with a clear, proactive call to action\n'
        '- 3\u20134 paragraphs, under 400 words\n'
        '- Output the BODY PARAGRAPHS ONLY\n'
        '- Do not include date, addresses, greeting, sign-off, '
        'or signature lines'
    )

    try:
        # Keep model choice explicit so it is easy to swap in one place later.
        response = _client.models.generate_content(
            model='gemini-3.1-flash',
            contents=prompt,
        )
        if response and response.text:
            return response.text.strip()
        return 'AI returned an empty response.'
    except Exception as exc:
        return f'AI Error: {exc}'
