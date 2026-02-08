# Tev & Louis Japan Map Generator

Automatically extracts places (restaurants, temples, attractions...) from [Tev & Louis](https://www.youtube.com/@TevLouis) YouTube videos and generates an interactive Google Map.

## How it works

```
YouTube Channel → Video Descriptions + Transcripts → Gemini AI Extraction → Geocoding → Google Map
```

1. **Scrape**: Fetches all videos from the channel via YouTube Data API v3
2. **Transcribe**: Grabs French subtitles/transcripts for each video
3. **Extract**: Uses Gemini to identify places, addresses, ratings, and opinions from the French text
4. **Geocode**: Converts addresses to coordinates (Google Geocoding or free Nominatim)
5. **Export**: Generates KML and CSV files importable into Google My Maps

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

- **`YOUTUBE_API_KEY`** (required): Get one at [Google Cloud Console](https://console.cloud.google.com/apis/credentials) — enable "YouTube Data API v3"
- **`GEMINI_API_KEY`** (required): Get one at [Google AI Studio](https://aistudio.google.com/apikey) — generous free tier included
- **`GOOGLE_GEOCODING_API_KEY`** (optional): For more accurate geocoding. Without it, the free Nominatim service is used.

### 3. Run

```bash
# Full pipeline (all videos — may take a while and use API credits)
python main.py

# Test with just 5 videos first
python main.py --max-videos 5

# Skip transcripts (faster, uses only video descriptions)
python main.py --skip-transcripts

# Force re-fetch (ignore cache)
python main.py --no-cache
```

### 4. Import into Google My Maps

1. Go to [Google My Maps](https://www.google.com/maps/d/)
2. Create a new map
3. Click "Import" and upload `output/tev_louis_japan.kml` (or `.csv`)
4. Your map with all Tev & Louis recommendations is ready!

## Output files

| File | Description |
|------|-------------|
| `output/tev_louis_japan.kml` | KML file with categorized pins (for Google My Maps) |
| `output/tev_louis_japan.csv` | CSV spreadsheet with all place data |
| `output/tev_louis_japan.json` | Full JSON data for further processing |
| `output/videos_cache.json` | Cached video data (avoids re-fetching) |
| `output/places_cache.json` | Cached extracted places (avoids re-running Gemini) |

## Project structure

```
japan/
├── main.py                  # Main pipeline script
├── src/
│   ├── youtube_scraper.py   # YouTube API + transcript fetching
│   ├── place_extractor.py   # Gemini AI place extraction
│   └── map_generator.py     # Geocoding + KML/CSV generation
├── output/                  # Generated files (gitignored)
├── requirements.txt
├── .env.example
└── README.md
```

## API costs estimate

- **YouTube Data API**: Free tier (10,000 units/day) is enough for most channels
- **Gemini API**: Free tier (15 RPM / 1M tokens/min on Flash) should cover most use cases at no cost
- **Google Geocoding**: $5 per 1,000 requests. Alternatively, Nominatim is free (but slower)

## Extending to other channels

The tool is designed to work with any YouTube channel. Just change the channel handle:

```bash
python main.py --channel AnotherChannel
```

The Gemini extraction prompt is tuned for French food/travel content, but works with other languages and topics too.
