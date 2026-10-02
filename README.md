# FaceBingo
#### Meet People, Click a Selfie, Share a Thought
A lightweight event icebreaker where the participants pick their initial, log who they met, share a thought, and snap a selfie.

## Quick Start

```bash
# Clone and install dependencies
poetry install

# Copy and fill in your secrets
cp .env.example .env

# Run the DDL against your Supabase project (see section below)
# Start the dev server
poetry run uvicorn main:app --reload

# If interface needs to be accessible across the network
# use the flags --host and --port
# potery run uvicorn <module>:<app-generator> --host <interface-ip> --port <port-number>
poetry run uvicorn main:app --reload --host 0.0.0.0 --port $port
```
> Open [https://facebingo-rosy.vercel.app](FaceBingo - App).

## Database Setup
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

-- Allow anonymous reads of own rows only (by submitter_name - event-scale trust)
-- Tighten this with auth.uid() if you add Supabase Auth later.
CREATE POLICY "anon_select_own" ON public.encounters
    FOR SELECT TO anon
    USING (true);

-- Allow anonymous uploads to the photos bucket
CREATE POLICY "Allow anonymous uploads"
ON storage.objects FOR INSERT TO anon
WITH CHECK (
    -- Change if using a different bucket name
    bucket_id = 'facebingo-photos' 
);

-- Create a table for registered users
CREATE TABLE IF NOT EXISTS public.users (
    id              uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    name            text            NOT NULL UNIQUE,
    additional_metadata jsonb       DEFAULT '{}'::jsonb,
    created_at      timestamptz     NOT NULL DEFAULT now()
);

-- Enable RLS for users
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_insert_users" ON public.users FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "anon_update_users" ON public.users FOR UPDATE TO anon USING (true);
CREATE POLICY "anon_select_users" ON public.users FOR SELECT TO anon USING (true);
```

## Environment Variables
See [`.env.example`](.env.example) for the full list with descriptions.

| Variable | Required | Default |
|---|---|---|
| `SUPABASE_URL` | Yes | — |
| `SUPABASE_ANON_KEY` | Yes | — |
| `ADMIN_USERNAME` | Yes | —|
| `ADMIN_PASSWORD` | Yes | — |
| `SUPABASE_BUCKET` | No | `facebingo-photos` |
| `SUPABASE_TABLE` | No | `encounters` |
| `ALLOWED_ORIGINS` | No | `["*"]` |
| `RATE_LIMIT` | No | `20/minute` |
| `APP_ENV` | No | `development` |
| `LOG_LEVEL` | No | `INFO` |

## Routes
| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/` | — | Page 1 — alphabet grid |
| `GET` | `/encounter/{letter}` | — | Page 2 — encounter form |
| `POST` | `/submit` | — | Save encounter + upload photo |
| `GET` | `/timed-out` | — | Page for paused submissions |
| `GET` | `/public` | — | Page 4 — public live event feed |
| `POST` | `/api/register` | — | Register a user profile |
| `GET` | `/users` | — | View all registered users |
| `GET` | `/admin` | Basic Auth | Page 3 — admin dashboard |
| `GET` | `/admin/stats` | — | JSON stats for dashboard polling |
| `GET` | `/admin/status` | Basic Auth | Get submissions status |
| `POST` | `/admin/status` | Basic Auth | Toggle submissions status |
| `DELETE` | `/admin/encounters/{id}` | Basic Auth | Delete an encounter record and its photo |
| `DELETE` | `/admin/users/{id}` | Basic Auth | Delete a registered user |
| `GET` | `/debug/*` | Basic Auth | Config verification endpoints |
| `GET` | `/health` | — | Liveness probe |

Further documentation on routes can be found at `docs/apidocs.yaml`