import logging
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

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
