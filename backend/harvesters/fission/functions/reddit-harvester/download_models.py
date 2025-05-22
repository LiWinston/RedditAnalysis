# for text embedding
from sentence_transformers import (
    SentenceTransformer,
)

# for NLP
import nltk
import nltk.downloader

import traceback

MODEL_NAME = "BAAI/bge-small-en-v1.5"
VECTOR_DIMENSION = 0

def download_nltk_resource(resource_name):
    """Downloads NLTK resources if not found."""
    print(f"[*] Downloading NLTK resource '{resource_name}'...")
    downloader = nltk.downloader.Downloader()
    downloader.download(resource_name)

def load_embedding_model():
    """Loads the Sentence Transformer model and sets global VECTOR_DIMENSION."""
    global VECTOR_DIMENSION
    print(f"[*] Loading sentence embedding model: {MODEL_NAME}...")
    try:
        model = SentenceTransformer(MODEL_NAME)
        VECTOR_DIMENSION = model.get_sentence_embedding_dimension()
        print(f"[+] Model '{MODEL_NAME}' loaded. Vector dimension: {VECTOR_DIMENSION}")
        return model
    except Exception as e:
        print(f"[-] ERROR: Failed to load model '{MODEL_NAME}': {str(e)}")
        traceback.print_exc()
        exit(1)

def main():
    print("[*] Checking models...")
    # Ensure 'vader_lexicon' is available for SentimentIntensityAnalyzer
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        try:
            nltk.data.find("vader_lexicon")
        except LookupError:
            print("[*] NLTK 'vader_lexicon' not found. Attempting to download...")
            download_nltk_resource("vader_lexicon")
    print("[+] NLTK 'vader_lexicon' downloaded.")
    _ = load_embedding_model()
    print(f"[+] Sentence Transformer model '{MODEL_NAME}' loaded.")
    print("[*] Download script complete. Check output above for any errors.")

if __name__ == "__main__":
    main()
