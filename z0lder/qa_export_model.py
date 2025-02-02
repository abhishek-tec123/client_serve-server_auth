"""
ISO QA Export Script

This script processes PDF documents in a specified folder, extracts text, 
and provides answers to user queries using a question-answering model.

"""

import os
import logging
import warnings
import time

from dotenv import load_dotenv
import PyPDF2

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

import google.generativeai as genai
import google.generativeai.types.generation_types

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
    - str: Answer to the user's question. If an error occurs during any step,
      an error message is returned instead.

    Raises:
    - FileNotFoundError: If the specified PDF file does not exist.
    - Exception: For any other unexpected errors during PDF processing,
      text splitting, embedding generation, or question answering.

    Note:
    This function uses Google Generative AI for embeddings and question answering.
    """
    text = get_text_from_pdf(pdf_file)
    if not text:
        return "Error: Unable to extract text from the PDF."

    text_chunks = get_text_chunks(text)
    if not text_chunks:
        return "Error: Failed to split text into chunks."

    vector_store = get_vector_store(text_chunks)
    if not vector_store:
        return "Error: Failed to create vector store."

    return user_input(user_question, vector_store)

def get_text_from_pdf(pdf_file):
    """
    Extracts text content from a PDF file using PyPDF2.

    Args:
    - pdf_file (str): Path to the PDF file.

    Returns:
    - str: Extracted text content from the PDF.
      If the file cannot be found or an error occurs during extraction,
      an empty string is returned.
    """
    text = ""
    try:
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages):
                text += page.extract_text()
    except FileNotFoundError as e:
        logging.error(f"File '{pdf_file}' not found: {e}")
    except Exception as e:
        logging.error(f"An error occurred while reading the file: {e}")
    return text

def get_text_chunks(text):
    """
    Splits a given text into manageable chunks for processing.

    Args:
    - text (str): Input text to be split into chunks.

    Returns:
    - list: List of text chunks.
      If the input text is empty or None, an empty list is returned.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=1000
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    """
    Generates embeddings for text chunks and creates a vector store using FAISS.

    Args:
    - text_chunks (list): List of text chunks for which embeddings are to be generated.

    Returns:
    - FAISS: Vector store containing embeddings for the input text chunks.
      If an error occurs during embedding generation or vector store creation,
      None is returned.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    if not embeddings:
        logging.error("Failed to generate embeddings.")
        return None

    if not text_chunks:
        logging.error("No text chunks provided.")
        return None

    try:
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    except Exception as e:
        logging.error(f"Failed to create vector store: {e}")
        return None

    vector_store.save_local("faiss_index")
    return vector_store

def user_input(user_question, vector_store):
    """
    Processes user input, performs a similarity search, and generates a response
    using a question-answering model.

    Args:
    - user_question (str): Question asked by the user.
    - vector_store (FAISS): Vector store containing embeddings of text chunks.

    Returns:
    - str: Answer generated by the question-answering model in response to the
      user's question. If the answer is not found in the document or an error occurs,
      an appropriate message is returned.

    Note:
    This function uses Google Generative AI for question answering.
    """
    prompt_template = """
    You are an AI assistant that provides helpful answers to user queries.\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer: 
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    search = vector_store.similarity_search(user_question)
    response = chain({"input_documents": search, "question": user_question}, return_only_outputs=True)

    if response:
        answer_text = response['output_text']
        logging.info(f"\nQuestion: {user_question}\n")
        logging.info(f"\nAnswer: {answer_text}\n")
    else:
        answer_text = "Not found in document."
        logging.warning(f"Question: {user_question}, Answer: {answer_text}")

    return clean_text(answer_text)

def clean_text(output_text):
    """
    Cleans and formats the output text for readability.

    Args:
    - output_text (str): Text to be cleaned and formatted.

    Returns:
    - str: Cleaned and formatted text.
    """
    cleaned_text = output_text.strip()
    cleaned_text = '\n'.join(line for line in cleaned_text.splitlines() if line.strip())
    return cleaned_text

def answer_question_from_pdf_with_retry(pdf_file, user_question):
    """
    Handles retries for answering questions from PDF files with exponential backoff
    in case of failures.

    Args:
    - pdf_file (str): Path to the PDF file.
    - user_question (str): Question asked by the user.

    Returns:
    - str: Answer to the user's question. If an error occurs during any step or
      maximum retry attempts are reached, an appropriate error message is returned.
    """
    retry_attempts = 3
    current_attempt = 1
    while current_attempt <= retry_attempts:
        try:
            return answer_question_from_pdf(pdf_file, user_question)
        except google.generativeai.types.generation_types.StopCandidateException:
            logging.error("An error occurred: StopCandidateException")
            return "An error occurred: StopCandidateException"
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            if current_attempt == retry_attempts:
                return "An error occurred: Maximum retry attempts reached"
            else:
                wait_time = 2 ** current_attempt  # Exponential backoff
                logging.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                current_attempt += 1

def main():
    """
    Main function to process multiple PDF files in a directory (`docs_folder`).
    """
    docs_folder = "/Users/macbook/Desktop/llm-deployment_scrty/app/docs"
    for filename in os.listdir(docs_folder):
        if filename.endswith(".pdf"):
            pdf_file = os.path.join(docs_folder, filename)
            user_question = "What is the main idea?"
            answer = answer_question_from_pdf_with_retry(pdf_file, user_question)
            # logging.info(f"File: {pdf_file}, Question: {user_question}, Answer: {answer}")

if __name__ == "__main__":
    main()
