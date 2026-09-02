CREATE TABLE IF NOT EXISTS public.inference_cache (
    id SERIAL PRIMARY KEY,
    url_source VARCHAR(2048) UNIQUE NOT NULL,
    text_hash VARCHAR(255) UNIQUE NOT NULL,
    sensationalism_score NUMERIC(5, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_text_hash ON public.inference_cache (text_hash);