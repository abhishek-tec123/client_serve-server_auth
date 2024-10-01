import logging
import PyPDF2

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

def get_text_chunks(text, chunk_size=10000, chunk_overlap=1000):
    """
    Splits a given text into manageable chunks for processing.

    Args:
    - text (str): Input text to be split into chunks.
    - chunk_size (int): Size of each chunk.
    - chunk_overlap (int): Overlap between chunks.

    Returns:
    - list: List of text chunks.
      If the input text is empty or None, an empty list is returned.
    """
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_text(text)
    return chunks
