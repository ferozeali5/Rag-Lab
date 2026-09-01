"""question -> similarity search -> top match (+ optional Claude answer)."""
import os
import sys

import psycopg2
from dotenv import load_dotenv

from embed import embed_text
from ingest import get_conn

load_dotenv()


def search(question: str, top_k: int = 3):
    q_vec = embed_text(question, input_type="query")
    conn = get_conn()
    cur = conn.cursor()
    # <=> is pgvector's cosine-distance operator (smaller = more similar)
    cur.execute(
        """
        select content, metadata, embedding <=> %s::vector as distance
        from chunks
        order by embedding <=> %s::vector
        limit %s
        """,
        (q_vec, q_vec, top_k),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def ask_claude(question: str, context_chunks: list[str]) -> str:
    from anthropic import Anthropic

    client = Anthropic()  # reads ANTHROPIC_API_KEY from env
    context = "\n\n".join(context_chunks)
    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                f"Answer the question using ONLY this menu context. "
                f"If the context doesn't cover it, say so.\n\n"
                f"Context:\n{context}\n\nQuestion: {question}"
            ),
        }],
    )
    return resp.content[0].text


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What's a good spicy vegetarian option?"
    results = search(question)

    print(f"Question: {question}\n")
    print("Top matches:")
    for content, metadata, distance in results:
        print(f"  [{distance:.4f}] {metadata} -> {content}")

    print("\nClaude's answer:")
    print(ask_claude(question, [r[0] for r in results]))
