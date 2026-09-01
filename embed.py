"""text -> vector, using Voyage AI (Anthropic's recommended embeddings partner).

Anthropic's own API doesn't expose an embeddings endpoint, so the standard
pairing for a Claude-based RAG stack is Voyage for embeddings + Claude for
generation. voyage-2 outputs 1024-dim vectors, matching schema.sql.
"""
import os
from dotenv import load_dotenv
import voyageai

load_dotenv()

_client = voyageai.Client(api_key=os.environ["VOYAGE_API_KEY"])


def embed_text(text: str, input_type: str = "document") -> list[float]:
    """input_type: 'document' when embedding content to store, 'query' when embedding a question."""
    result = _client.embed([text], model="voyage-2", input_type=input_type)
    return result.embeddings[0]


def embed_batch(texts: list[str], input_type: str = "document") -> list[list[float]]:
    result = _client.embed(texts, model="voyage-2", input_type=input_type)
    return result.embeddings


if __name__ == "__main__":
    vec = embed_text("Chicken shawarma wrap with garlic sauce and pickles")
    print(f"Embedded 1 string -> vector of length {len(vec)}")
    print(vec[:5], "...")
