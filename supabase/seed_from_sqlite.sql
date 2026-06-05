-- Generated from local SQLite by scripts/export_oasis_supabase_assets.py
-- Run after supabase/schema.sql if you want to migrate current local entries.

insert into public.oasis_joy_entries (lang, text, created_at)
values
  ('en', 'A stranger held the elevator and smiled like they had all the time in the world.', '2026-06-04T16:41:18+0800'),
  ('en', 'The first sip of tea was exactly the right temperature.', '2026-06-04T16:41:18+0800'),
  ('en', 'A patch of sunlight landed on my notebook and stayed there.', '2026-06-04T16:41:18+0800'),
  ('zh', '今天路过一家面包店，刚好闻到热面包出炉的味道。', '2026-06-04T16:41:18+0800'),
  ('zh', '有人很认真地听我把一句话说完。', '2026-06-04T16:41:18+0800'),
  ('zh', '午后的光落在杯子边缘，看起来像一个小小的奖励。', '2026-06-04T16:41:18+0800'),
  ('tc', '今天路過一家麵包店，剛好聞到熱麵包出爐的味道。', '2026-06-04T16:41:18+0800'),
  ('tc', '有人很認真地聽我把一句話說完。', '2026-06-04T16:41:18+0800'),
  ('tc', '午後的光落在杯子邊緣，看起來像一個小小的獎勵。', '2026-06-04T16:41:18+0800'),
  ('en', 'A tiny test joy appeared while the page was loading.', '2026-06-04T16:41:50+0800'),
  ('zh', '按照指定视觉稿重构后，页面变得更轻了。', '2026-06-04T16:56:26+0800'),
  ('zh', '种的番茄熟了', '2026-06-04T17:23:58+0800')
on conflict (lang, text) do nothing;

insert into public.oasis_audio_assets (sound_key, label, bucket, object_path, mime_type, source_url)
values
  ('cat', 'Cat Purr', 'oasis-audio', 'cat.wav', 'audio/wav', 'https://upload.wikimedia.org/wikipedia/commons/6/6e/Cat_purring_panting.ogg'),
  ('fire', 'Woodfire', 'oasis-audio', 'fire.wav', 'audio/wav', 'https://assets.mixkit.co/active_storage/sfx/2432/2432-84.wav'),
  ('leaves', 'Autumn Leaves', 'oasis-audio', 'leaves.wav', 'audio/wav', 'https://assets.mixkit.co/active_storage/sfx/1204/1204-84.wav'),
  ('rain', 'Soft Rain', 'oasis-audio', 'rain.wav', 'audio/wav', 'https://assets.mixkit.co/active_storage/sfx/2448/2448-84.wav')
on conflict (sound_key) do update set label = excluded.label, bucket = excluded.bucket, object_path = excluded.object_path, mime_type = excluded.mime_type, source_url = excluded.source_url, updated_at = now();
