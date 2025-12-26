import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

genai.configure(api_key=GOOGLE_API_KEY)

def get_model(model_name="gemini-flash-latest"):
    """
    Returns a configured GenerativeModel instance.
    """
    return genai.GenerativeModel(model_name)

def generate_text(prompt, model_name="gemini-flash-latest", temperature=0.7):
    """
    Simple wrapper to generate text from a prompt.
    """
    model = get_model(model_name)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature
        )
    )
    return response.text

import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

async def generate_text_async(prompt, model_name="gemini-flash-latest", temperature=0.7):
    """
    Asynchronous wrapper for generate_text.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        executor, 
        generate_text, 
        prompt, 
        model_name, 
        temperature
    )
