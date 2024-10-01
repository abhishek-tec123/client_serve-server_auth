import os
import logging
import warnings
import time

from dotenv import load_dotenv
import google.generativeai as genai
import google.generativeai.types.generation_types

from controller.pdf_utils import get_text_from_pdf, get_text_chunks
from controller.vector_store_utils import get_vector_store
from controller.qa_utils import user_input

# Suppress warnings
warnings.filterwarnings("ignore")

# Load environment variables from .env file
load_dotenv()

# Configure Google API key for generative AI
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def answer_question_from_pdf(pdf_file, user_question):
    """
    Extracts text from a PDF file, splits it into chunks, generates embeddings,
    and answers a user question using a question-answering model.

    Args:
    - pdf_file (str): Path to the PDF file.
    - user_question (str): Question asked by the user.

    Returns:
    - dict: Contains the filename, user question, and the answer.
      If an error occurs during any step, an error message is returned instead.

    Raises:
    - FileNotFoundError: If the specified PDF file does not exist.
    - Exception: For any other unexpected errors during PDF processing,
      text splitting, embedding generation, or question answering.

    Note:
    This function uses Google Generative AI for embeddings and question answering.
    """
    text = get_text_from_pdf(pdf_file)
    if not text:
        return {
            "file": pdf_file,
            "question": user_question,
            "answer": "Error: Unable to extract text from the PDF."
        }

    text_chunks = get_text_chunks(text)
    if not text_chunks:
        return {
            "file": pdf_file,
            "question": user_question,
            "answer": "Error: Failed to split text into chunks."
        }

    vector_store = get_vector_store(text_chunks)
    if not vector_store:
        return {
            "file": pdf_file,
            "question": user_question,
            "answer": "Error: Failed to create vector store."
        }

    answer = user_input(user_question, vector_store)
    return {
        "file": pdf_file,
        "question": user_question,
        "answer": answer
    }

def answer_question_from_pdf_with_retry(pdf_file, user_question):
    """
    Handles retries for answering questions from PDF files with exponential backoff
    in case of failures.

    Args:
    - pdf_file (str): Path to the PDF file.
    - user_question (str): Question asked by the user.

    Returns:
    - dict: Contains the filename, user question, and the answer.
      If an error occurs during any step or maximum retry attempts are reached,
      an appropriate error message is returned.
    """
    retry_attempts = 3
    current_attempt = 1
    while current_attempt <= retry_attempts:
        try:
            return answer_question_from_pdf(pdf_file, user_question)
        except google.generativeai.types.generation_types.StopCandidateException:
            logging.error("An error occurred: StopCandidateException")
            return {
                "file": pdf_file,
                "question": user_question,
                "answer": "An error occurred: StopCandidateException"
            }
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            if current_attempt == retry_attempts:
                return {
                    "file": pdf_file,
                    "question": user_question,
                    "answer": "An error occurred: Maximum retry attempts reached"
                }
            else:
                wait_time = 2 ** current_attempt  # Exponential backoff
                logging.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                current_attempt += 1

# if __name__ == "__main__":
#     pdf_file_path = "path/to/your/pdf/file.pdf"
#     user_question = "Your question here"
#     result = answer_question_from_pdf_with_retry(pdf_file_path, user_question)
#     output = {
#         "file": pdf_file_path,
#         "question": user_question,
#         "answer": result['answer']
#     }
