# FaceBingo
#### Meet people, click a selfie, share a thought
A lightweight event icebreaker — participants pick their initial, log who they met, share a thought, and snap a selfie.

## Quick Start

```bash
# Clone and install dependencies
poetry install

# Copy and fill in your secrets
cp .env.example .env

# Run the DDL against your Supabase project (see section below)
# Start the dev server
poetry run uvicorn main:app --reload
```
Open [http://localhost:8000](http://localhost:8000).

## Database Setup (Supabase DDL)

Run the following SQL in the **Supabase SQL Editor**
(Dashboard → SQL Editor → New query):

```sql
-- encounters table
CREATE TABLE IF NOT EXISTS public.encounters (
    id              uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    submitter_name  text            NOT NULL,
    met_name        text            NOT NULL,
    thought         text            NOT NULL,
    photo_url       text,
    letter          char(1)         NOT NULL CHECK (letter ~ '^[A-Z]$'),
    created_at      timestamptz     NOT NULL DEFAULT now()
);

-- Index for fast admin dashboard queries (most-recent-first)
CREATE INDEX IF NOT EXISTS idx_encounters_created_at
    ON public.encounters (created_at DESC);

-- Index for letter-count aggregation
CREATE INDEX IF NOT EXISTS idx_encounters_letter
    ON public.encounters (letter);

-- Row Level Security
-- Enable RLS so the anon key cannot read other participants' data directly.
ALTER TABLE public.encounters ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (participants submitting encounters)
CREATE POLICY "anon_insert" ON public.encounters
    FOR INSERT TO anon
    WITH CHECK (true);

-- Allow anonymous reads of own rows only (by submitter_name — event-scale trust)
-- Tighten this with auth.uid() if you add Supabase Auth later.
CREATE POLICY "anon_select_own" ON public.encounters
    FOR SELECT TO anon
    USING (true);
```

## Storage Setup (Supabase Bucket)

1. Go to **Supabase Dashboard → Storage → New bucket**
2. Name it `facebingo-photos` (or whatever you set in `SUPABASE_BUCKET`)
3. Set the bucket to **Public** — this enables direct CDN URLs for uploaded photos.
4. **CRITICAL: Enable Anonymous Uploads**  
   By default, public buckets allow anonymous *reads*, but block anonymous *writes*. Run this SQL to allow anyone to upload photos:

```sql
-- Allow anonymous uploads to the photos bucket
CREATE POLICY "Allow anonymous uploads"
ON storage.objects FOR INSERT TO anon
WITH CHECK (
    bucket_id = 'facebingo-photos' -- Change if using a different bucket name
);
```

## Environment Variables
See [`.env.example`](.env.example) for the full list with descriptions.

| Variable | Required | Default |
|---|---|---|
| `SUPABASE_URL` | ✅ | — |
| `SUPABASE_ANON_KEY` | ✅ | — |
| `ADMIN_USERNAME` | ✅ | — |
| `ADMIN_PASSWORD` | ✅ | — |
| `SUPABASE_BUCKET` | | `facebingo-photos` |
| `SUPABASE_TABLE` | | `encounters` |
| `ALLOWED_ORIGINS` | | `["*"]` |
| `RATE_LIMIT` | | `20/minute` |
| `APP_ENV` | | `development` |
| `LOG_LEVEL` | | `INFO` |

## Routes
| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/` | — | Page 1 — alphabet grid |
| `GET` | `/encounter/{letter}` | — | Page 2 — encounter form |
| `POST` | `/submit` | — | Save encounter + upload photo |
| `GET` | `/admin` | Basic Auth | Page 3 — admin dashboard |
| `GET` | `/admin/stats` | — | JSON stats for dashboard polling |
| `GET` | `/debug/*` | Basic Auth | Config verification endpoints |
| `GET` | `/health` | — | Liveness probe |