-- Run this in the Supabase SQL editor (or via psql) once per project.

create extension if not exists vector;

create table if not exists chunks (
    id bigserial primary key,
    content text not null,
    embedding vector(1024),
    metadata jsonb default '{}'::jsonb,  -- e.g. {"dish": "Chicken Shawarma", "source": "menu_sample.json"}
    created_at timestamptz default now()
);

-- Approximate nearest-neighbor index (cosine distance). ivfflat needs some rows
-- to be useful; fine to add this after your first ingest too.
create index if not exists chunks_embedding_idx
    on chunks using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);
