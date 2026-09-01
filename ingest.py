"""real content -> embedded rows in Supabase's `chunks` table.

Reads data/pregusta_menu_sample.json (swap in a real Pregusta menu export
whenever you have one - the point of using menu data is that nothing's at
stake while you're learning the pipeline).
"""
import json
import os

import psycopg2
from dotenv import load_dotenv

from embed import embed_batch

load_dotenv()

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "pregusta_menu_sample.json")


def get_conn():
    return psycopg2.connect(
        host=os.environ["SUPABASE_DB_HOST"],
        port=os.environ["SUPABASE_DB_PORT"],
        dbname=os.environ["SUPABASE_DB_NAME"],
        user=os.environ["SUPABASE_DB_USER"],
        password=os.environ["SUPABASE_DB_PASSWORD"],
    )


def chunk_dish(dish: dict) -> str:
    """One dish -> one chunk of text. Simple 1 dish = 1 chunk chunking strategy
    to start; revisit if you need finer granularity later."""
    parts = [dish["name"]]
    if dish.get("description"):
        parts.append(dish["description"])
    if dish.get("cuisine"):
        parts.append(f"Cuisine: {dish['cuisine']}")
    if dish.get("price"):
        parts.append(f"Price: {dish['price']}")
    return ". ".join(parts)


def main():
    with open(DATA_PATH) as f:
        dishes = json.load(f)

    texts = [chunk_dish(d) for d in dishes]
    print(f"Chunked {len(texts)} dishes. Embedding...")
    vectors = embed_batch(texts, input_type="document")

    conn = get_conn()
    cur = conn.cursor()
    for dish, text, vec in zip(dishes, texts, vectors):
        cur.execute(
            "insert into chunks (content, embedding, metadata) values (%s, %s, %s)",
            (text, vec, json.dumps({"dish": dish["name"]})),
        )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(texts)} rows into chunks.")


if __name__ == "__main__":
    main()
