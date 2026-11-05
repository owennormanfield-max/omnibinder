-- Omnibinder Picks: per-user saved state (run once in Supabase SQL editor)
create table if not exists public.picks (
  user_id uuid primary key references auth.users(id) on delete cascade,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
alter table public.picks enable row level security;
create policy "picks: own row" on public.picks for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
