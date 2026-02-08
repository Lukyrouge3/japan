#!/usr/bin/env python3
"""
Tev & Louis Japan Map Generator
================================
Automatically extracts places from Tev & Louis YouTube videos
and generates a Google Maps-compatible map.

Usage:
    python main.py                     # Full pipeline (all videos)
    python main.py --max-videos 10     # Limit to 10 videos (for testing)
    python main.py --skip-transcripts  # Skip transcript fetching (faster)
    python main.py --no-cache          # Ignore cached data
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from src.youtube_scraper import scrape_channel
from src.place_extractor import extract_places_from_videos
from src.map_generator import geocode_all_places, generate_kml, generate_csv, generate_json


DEFAULT_CHANNEL_HANDLE = "TevLouis"
OUTPUT_DIR = "output"


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Google Map from Tev & Louis YouTube videos"
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=None,
        help="Limit number of videos to process (for testing)",
    )
    parser.add_argument(
        "--skip-transcripts",
        action="store_true",
        help="Skip fetching transcripts (only use descriptions)",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Ignore cached data and re-fetch everything",
    )
    parser.add_argument(
        "--channel",
        default=DEFAULT_CHANNEL_HANDLE,
        help=f"YouTube channel handle (default: {DEFAULT_CHANNEL_HANDLE})",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Gemini model to use for extraction (default: gemini-2.0-flash)",
    )
    parser.add_argument(
        "--output-dir",
        default=OUTPUT_DIR,
        help=f"Output directory (default: {OUTPUT_DIR})",
    )
    args = parser.parse_args()

    load_dotenv()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    videos_cache = str(output_dir / "videos_cache.json") if not args.no_cache else None
    places_cache = str(output_dir / "places_cache.json") if not args.no_cache else None

    # ── Step 1: Scrape YouTube channel ──────────────────────────────
    print("=" * 60)
    print("STEP 1: Fetching videos from YouTube")
    print("=" * 60)

    videos = scrape_channel(
        handle=args.channel,
        include_transcripts=not args.skip_transcripts,
        max_videos=args.max_videos,
        cache_path=videos_cache,
    )
    print(f"\n-> {len(videos)} videos fetched\n")

    # ── Step 2: Extract places using Gemini ─────────────────────────
    print("=" * 60)
    print("STEP 2: Extracting places with Gemini AI")
    print("=" * 60)

    places = extract_places_from_videos(
        videos,
        model=args.model,
        cache_path=places_cache,
    )
    print(f"\n-> {len(places)} unique places extracted\n")

    # ── Step 3: Geocode places ──────────────────────────────────────
    print("=" * 60)
    print("STEP 3: Geocoding addresses")
    print("=" * 60)

    places = geocode_all_places(places)

    geocoded_count = sum(1 for p in places if p.get("latitude") is not None)
    print(f"\n-> {geocoded_count}/{len(places)} places geocoded\n")

    # ── Step 4: Generate map files ──────────────────────────────────
    print("=" * 60)
    print("STEP 4: Generating map files")
    print("=" * 60)

    generate_kml(places, str(output_dir / "tev_louis_japan.kml"))
    generate_csv(places, str(output_dir / "tev_louis_japan.csv"))
    generate_json(places, str(output_dir / "tev_louis_japan.json"))

    # ── Summary ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"  Videos processed:  {len(videos)}")
    print(f"  Places found:      {len(places)}")
    print(f"  Places geocoded:   {geocoded_count}")
    print(f"\nOutput files:")
    print(f"  KML (Google My Maps): {output_dir / 'tev_louis_japan.kml'}")
    print(f"  CSV (spreadsheet):    {output_dir / 'tev_louis_japan.csv'}")
    print(f"  JSON (raw data):      {output_dir / 'tev_louis_japan.json'}")
    print(f"\nTo import into Google My Maps:")
    print(f"  1. Go to https://www.google.com/maps/d/")
    print(f"  2. Create a new map")
    print(f"  3. Import -> Upload the KML or CSV file")
    print(f"  4. Enjoy your Tev & Louis Japan map! 🗾")


if __name__ == "__main__":
    main()
