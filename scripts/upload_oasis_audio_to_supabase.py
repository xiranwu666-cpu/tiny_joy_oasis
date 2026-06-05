#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO_DIR = ROOT / "supabase" / "audio"


def upload_file(supabase_url, service_key, bucket, path):
    object_name = path.name
    endpoint = f"{supabase_url.rstrip('/')}/storage/v1/object/{bucket}/{object_name}"
    data = path.read_bytes()
    request = Request(
        endpoint,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {service_key}",
            "apikey": service_key,
            "Content-Type": "audio/wav",
            "x-upsert": "true",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Upload failed for {object_name}: {error.code} {body}") from error


def main():
    parser = argparse.ArgumentParser(description="Upload OASIS audio files to Supabase Storage.")
    parser.add_argument("--audio-dir", default=str(DEFAULT_AUDIO_DIR))
    parser.add_argument("--bucket", default=os.environ.get("SUPABASE_AUDIO_BUCKET", "oasis-audio"))
    args = parser.parse_args()

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_key:
        raise SystemExit("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY before uploading.")

    audio_dir = Path(args.audio_dir).resolve()
    files = sorted(audio_dir.glob("*.wav"))
    if not files:
        raise SystemExit(f"No .wav files found in {audio_dir}. Run export_oasis_supabase_assets.py first.")

    for path in files:
        status, _body = upload_file(supabase_url, service_key, args.bucket, path)
        print(f"Uploaded {path.name} -> {args.bucket}/{path.name} ({status})")


if __name__ == "__main__":
    main()
