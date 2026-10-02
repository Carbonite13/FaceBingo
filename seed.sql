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