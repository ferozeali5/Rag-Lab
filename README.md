# rag-lab

Minimal RAG pipeline: ingest -> chunk -> embed -> store in pgvector on Supabase -> query.
Built around a small sample of Pregusta-style menu data so nothing real is at stake while learning.

## Setup
1. `python3 -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in:
   - Supabase DB connection details (Settings -> Database -> Connection info, use the **direct** connection on port 5432, not the pooler, for this simple script)
   - `ANTHROPIC_API_KEY`
   - `VOYAGE_API_KEY` (free tier at https://dash.voyageai.com/ - Anthropic's API has no embeddings endpoint of its own, so Voyage is the standard pairing)
4. In the Supabase SQL editor, run `schema.sql` to create the `vector` extension and the `chunks` table.

## Run
```
python ingest.py      # embeds data/pregusta_menu_sample.json, inserts into chunks
python query.py "what's a good spicy vegetarian option?"
```

You should see the top-matching dish(es) by cosine similarity, then a Claude-generated
answer grounded only in that retrieved context.

## Next steps once this works
- Swap `data/pregusta_menu_sample.json` for a real export from Pregusta's own parsed menu data
- Try a harder question that needs 2+ chunks to answer, see if top_k=3 is enough
- Note what broke / what clicked below

## Notes / what broke / what clicked
-
