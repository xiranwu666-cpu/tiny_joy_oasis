# OASIS Formal Deployment

OASIS is not a static-only site once joy swapping, audio assets, and analytics are enabled. The recommended production version uses:

- Vercel Functions for lightweight API routes and SEO HTML rendering
- Supabase Postgres for joy swapping and traffic analytics
- Supabase Storage for audio assets

## Recommended Production Path: Vercel + Supabase

This is now the preferred formal launch architecture.

- Vercel serves OASIS pages and lightweight API functions.
- Supabase Postgres stores joy entries and traffic analytics.
- Supabase Storage stores audio files.
- The browser keeps calling the same local-looking API paths:
  - `/api/oasis/joy`
  - `/api/oasis/audio/fire`
  - `/api/oasis/analytics/pageview`

### 1. Create Supabase Project

In Supabase:

1. Create a new project.
2. Open SQL Editor.
3. Run [supabase/schema.sql](./supabase/schema.sql).
4. Run [supabase/seed_from_sqlite.sql](./supabase/seed_from_sqlite.sql) if you want to migrate current local joy entries.
5. Upload audio files from [supabase/audio](./supabase/audio) into the `oasis-audio` Storage bucket.

You can upload audio manually in the Supabase dashboard, or use:

```bash
SUPABASE_URL="https://your-project.supabase.co" \
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key" \
python3 scripts/upload_oasis_audio_to_supabase.py
```

### 2. Deploy to Vercel

1. Push this folder to GitHub.
2. Import the repo in Vercel.
3. Add environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_AUDIO_BUCKET=oasis-audio`
   - `ANALYTICS_ADMIN_TOKEN` optional, protects `/api/oasis/analytics/summary`
4. Deploy.
5. Add your custom domain in Vercel.
6. Point DNS to Vercel as instructed in the Vercel dashboard.

The included [vercel.json](./vercel.json) routes:

- `/` -> OASIS Chinese homepage
- `/oasis/zh/today`, `/oasis/en/today`, `/oasis/tc/today` -> SEO-rendered OASIS pages
- `/oasis/sitemap.xml` -> generated sitemap
- `/robots.txt` -> generated robots file
- `/admin/analytics.html` -> simple internal analytics dashboard

### 3. Vercel + Supabase Production Checks

After deploy, verify:

- `/oasis/zh/today` loads
- `/oasis/en/today` loads
- `/oasis/tc/today` loads
- `/oasis/sitemap.xml` contains all language routes
- `/api/oasis/joy?lang=zh` returns JSON
- `/api/oasis/audio/fire` redirects to Supabase Storage
- `/api/oasis/analytics/summary?token=YOUR_TOKEN` returns recent pageview stats if `ANALYTICS_ADMIN_TOKEN` is set
- `/admin/analytics.html` can load analytics with the same token

## Previous Option: Docker + SQLite

If you prefer not to use Supabase, the Docker + SQLite route below still works.

## Docker + SQLite on Render

Render is the easiest formal launch path for this project.

1. Push this folder to a GitHub repository.
2. In Render, create a new Blueprint or Web Service from the repository.
3. Use the included `render.yaml`.
4. Confirm the persistent disk:
   - name: `oasis-data`
   - mount path: `/data`
   - size: `1GB` or higher
5. Confirm environment variables:
   - `DB_PATH=/data/app_data.sqlite`
   - `PORT=8000`
6. Deploy.
7. Add a custom domain in Render.
8. Point your DNS record to the Render target shown in the dashboard.

Important: without a persistent disk, SQLite data will be lost during redeploys.

## Alternative: Fly.io

Fly.io is a strong option for SQLite because it supports app volumes.

1. Edit `fly.toml` and change `app = "oasis-digital-sanctuary"` to a globally unique app name.
2. Login with `fly auth login`.
3. Create the app and volume:

```bash
fly apps create your-oasis-app-name
fly volumes create oasis_data --region nrt --size 1
```

4. Deploy:

```bash
fly deploy
```

5. Add your domain:

```bash
fly certs add yourdomain.com
```

6. Follow Fly's DNS instructions for the shown records.

## Alternative: VPS

For full control, use a small VPS and Docker.

```bash
docker build -t oasis .
docker run -d \
  --name oasis \
  -e DB_PATH=/data/app_data.sqlite \
  -e PORT=8000 \
  -v oasis-data:/data \
  -p 8000:8000 \
  oasis
```

Then put Caddy or Nginx in front of it for HTTPS and your domain.

## Production Checks

After launch, verify:

- `/api/health` returns JSON
- `/oasis/zh/today` loads
- `/oasis/en/today` loads
- `/oasis/tc/today` loads
- `/oasis/sitemap.xml` contains all language routes
- `/api/oasis/audio/fire` returns `audio/wav`
- joy swap POST/GET still works after redeploy

## Traffic Monitoring Options

Use both platform-level and product-level monitoring.

Platform-level:

- Render/Fly/VPS logs
- uptime checks
- CPU, memory, restart count, response errors

Product-level:

- First-party analytics in Supabase for page views, language, route, referrer, user agent, and rough device type
- Plausible for privacy-friendly public analytics
- GA4 if SEO/search acquisition reporting matters more than privacy simplicity
- PostHog if you later want funnels and product events

This codebase now includes first-party endpoints:

- `POST /api/oasis/analytics/pageview`
- `GET /api/oasis/analytics/summary`
- table: `oasis_pageviews`

That keeps analytics self-owned and avoids cookie banners if no personal identifiers are stored.
