import os
import time
from google.api_core.exceptions import ResourceExhausted
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def read_text_file(file_path):
    """Reads the content of a text file and returns it as a string."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def chunk_text(text, chunk_size=1000):
    """Chunks the given text into smaller pieces of specified size."""
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]

def summarize_chunk(llm, chunk, retries=3, delay=1):
    """Summarizes a single chunk of text using the given LLM, with retry logic."""
    prompt = f"Please provide a well-defined summary of the following text:\n TEXT: {chunk}"
    for attempt in range(retries):
        try:
            response = llm.generate_content(prompt)
            return response.text
        except ResourceExhausted as e:
            print(f"Error processing chunk: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
    raise Exception("Max retries exceeded")

def smry_function(file_path, chunk_size=5000):
    """Summarizes the content of a text file, chunk by chunk."""
    print("Reading the text...")
    text = read_text_file(file_path)

    print("Processing the text...")
    chunks = list(chunk_text(text, chunk_size))

    summaries = []
    llm = genai.GenerativeModel("gemini-pro")

    print("Summarizing the text...")
    for i, chunk in enumerate(chunks):
        try:
            summary = summarize_chunk(llm, chunk)
            summaries.append(summary)
            print(f"Chunk {i+1}/{len(chunks)} summarized.")
            time.sleep(1)  # Add delay between requests to avoid rate limit
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")
            continue

    final_summary = " ".join(summaries)
    return final_summary
