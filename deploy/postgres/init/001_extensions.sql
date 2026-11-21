CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS stage0_vector_probe (
    id BIGSERIAL PRIMARY KEY,
    label TEXT NOT NULL,
    embedding vector(3) NOT NULL
);
