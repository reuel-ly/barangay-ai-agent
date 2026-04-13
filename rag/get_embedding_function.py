# from langchain_community.embeddings import BedrockEmbeddings
from langchain_ollama import OllamaEmbeddings
from rag.settings import EMBEDDING_MODEL

def get_embedding_function():
    """
    Returns the embedding function used by Chroma.
    """
    
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL  # must be an embedding model
    )

    return embeddings