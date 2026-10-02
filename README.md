# FaceBingo
#### Meet People, Click a Selfie, Share a Thought
A lightweight event icebreaker where the participants pick their initial, log who they met, share a thought, and snap a selfie.

Powered by FastAPI and Supabase API

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
Set up the database by executing the sql script at `seed.sql` which consists of the required
DDL commands and sequence to set up the initial architecture.

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