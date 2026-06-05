# OASIS

OASIS is a lightweight digital sanctuary for tired, anxious, bedtime, or in-between moments. It offers kind words, white noise, a private release pool, and anonymous joy swapping without requiring login.

## Production Environment

Set these in Vercel:

```txt
NEXT_PUBLIC_SITE_URL=https://tiny-joy-oasis.vercel.app
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_AUDIO_BUCKET=oasis-audio
ANALYTICS_ADMIN_TOKEN=
```

If `NEXT_PUBLIC_GA_ID` is empty, Google Analytics is not loaded.

## Public Routes

```txt
/oasis/zh/today
/oasis/zh/white-noise
/oasis/zh/release
/oasis/zh/joy
/oasis/en/today
/oasis/en/white-noise
/oasis/en/release
/oasis/en/joy
/oasis/tc/today
/oasis/tc/white-noise
/oasis/tc/release
/oasis/tc/joy
```

Legacy routes `/sound` and `/vent` remain supported, but canonical URLs use `/white-noise` and `/release`.

## UTM Launch Links

V2EX:

```txt
https://tiny-joy-oasis.vercel.app/oasis/zh/today?utm_source=v2ex&utm_medium=community&utm_campaign=oasis_launch
```

即刻:

```txt
https://tiny-joy-oasis.vercel.app/oasis/zh/today?utm_source=jike&utm_medium=social&utm_campaign=oasis_launch
```

小红书:

```txt
https://tiny-joy-oasis.vercel.app/oasis/zh/today?utm_source=xiaohongshu&utm_medium=social&utm_campaign=oasis_launch
```

Reddit:

```txt
https://tiny-joy-oasis.vercel.app/oasis/en/today?utm_source=reddit&utm_medium=community&utm_campaign=oasis_launch
```

Indie Hackers:

```txt
https://tiny-joy-oasis.vercel.app/oasis/en/today?utm_source=indiehackers&utm_medium=community&utm_campaign=oasis_launch
```
