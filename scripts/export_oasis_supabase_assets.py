#!/usr/bin/env python3
import argparse
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "app_data.sqlite"
DEFAULT_OUT = ROOT / "supabase"


def sql_literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def main():
    parser = argparse.ArgumentParser(description="Export OASIS SQLite data for Supabase migration.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to app_data.sqlite")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output directory")
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    out_dir = Path(args.out).resolve()
    audio_dir = out_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        joys = conn.execute(
            "SELECT lang, text, created_at FROM oasis_joy_entries ORDER BY id"
        ).fetchall()
        audios = conn.execute(
            """
            SELECT sound_key, label, source_url, mime_type, data
            FROM oasis_audio_assets
            ORDER BY sound_key
            """
        ).fetchall()

    for sound_key, _label, _source_url, mime_type, data in audios:
        ext = "wav" if mime_type == "audio/wav" else "bin"
        (audio_dir / f"{sound_key}.{ext}").write_bytes(bytes(data))

    seed_path = out_dir / "seed_from_sqlite.sql"
    lines = [
        "-- Generated from local SQLite by scripts/export_oasis_supabase_assets.py",
        "-- Run after supabase/schema.sql if you want to migrate current local entries.",
        "",
    ]
    if joys:
        lines.append("insert into public.oasis_joy_entries (lang, text, created_at)")
        values = [
            f"  ({sql_literal(lang)}, {sql_literal(text)}, {sql_literal(created_at)})"
            for lang, text, created_at in joys
        ]
        lines.append("values")
        lines.append(",\n".join(values))
        lines.append("on conflict (lang, text) do nothing;")
        lines.append("")

    if audios:
        lines.append("insert into public.oasis_audio_assets (sound_key, label, bucket, object_path, mime_type, source_url)")
        values = [
            f"  ({sql_literal(sound_key)}, {sql_literal(label)}, 'oasis-audio', {sql_literal(sound_key + '.wav')}, {sql_literal(mime_type)}, {sql_literal(source_url)})"
            for sound_key, label, source_url, mime_type, _data in audios
        ]
        lines.append("values")
        lines.append(",\n".join(values))
        lines.append(
            "on conflict (sound_key) do update set "
            "label = excluded.label, bucket = excluded.bucket, object_path = excluded.object_path, "
            "mime_type = excluded.mime_type, source_url = excluded.source_url, updated_at = now();"
        )
        lines.append("")

    seed_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Exported {len(joys)} joy rows to {seed_path}")
    print(f"Exported {len(audios)} audio files to {audio_dir}")


if __name__ == "__main__":
    main()
