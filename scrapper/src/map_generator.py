"""
Geocode extracted places and generate Google Maps-compatible exports (KML + CSV).
"""

import os
import csv
import json
import time
from pathlib import Path

import simplekml
from geopy.geocoders import Nominatim, GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


def rating_to_color(rating) -> str:
    """Convert a 1-10 rating to a KML color (aaBBGGRR format) from red to green."""
    try:
        score = int(rating)
    except (TypeError, ValueError):
        return "ff888888"  # Gray for unknown
    score = max(1, min(10, score))
    # Interpolate from red (1) -> yellow (5) -> green (10)
    t = (score - 1) / 9  # 0.0 to 1.0
    if t <= 0.5:
        # Red to yellow: R=255, G goes 0->255
        r, g, b = 255, int(255 * (t * 2)), 0
    else:
        # Yellow to green: R goes 255->0, G=255
        r, g, b = int(255 * (1 - (t - 0.5) * 2)), 255, 0
    # KML color format is aaBBGGRR (alpha, blue, green, red)
    return f"ff{b:02x}{g:02x}{r:02x}"

# Icon mapping for Google My Maps (when importing KML)
TYPE_ICONS = {
    "restaurant": "🍽️",
    "café": "☕",
    "bar": "🍺",
    "temple": "⛩️",
    "parc": "🌳",
    "magasin": "🛍️",
    "attraction": "📸",
    "quartier": "📍",
    "hôtel": "🏨",
}

def rating_to_stars(rating) -> str:
    """Convert a 1-10 numeric rating to a star display."""
    try:
        score = int(rating)
    except (TypeError, ValueError):
        return ""
    score = max(1, min(10, score))
    full = score // 2
    half = score % 2
    return "⭐" * full + ("½" if half else "")


def get_geocoder(google_api_key: str | None = None):
    """Create a geocoder - Google if key available, otherwise Nominatim."""
    key = google_api_key or os.getenv("GOOGLE_GEOCODING_API_KEY")
    if key:
        return GoogleV3(api_key=key)
    # Nominatim is free but rate-limited (1 req/sec)
    return Nominatim(user_agent="tev-louis-japan-map")


def geocode_place(geocoder, place: dict) -> tuple[float, float] | None:
    """
    Attempt to geocode a place. Tries multiple strategies:
    1. Full address if available
    2. Name + city
    3. Area + city
    """
    queries = []

    # Strategy 1: Full address
    if place.get("address"):
        queries.append(place["address"])

    # Strategy 2: Name + city
    name = place.get("name", "")
    city = place.get("city", "")
    area = place.get("area", "")

    if name and city:
        queries.append(f"{name}, {city}, Japan")
    if name and area:
        queries.append(f"{name}, {area}, {city}, Japan")

    # Strategy 3: Area + city (fallback for general areas)
    if area and city:
        queries.append(f"{area}, {city}, Japan")

    for query in queries:
        try:
            location = geocoder.geocode(query)
            if location:
                return (location.latitude, location.longitude)
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"    Geocoding error for '{query}': {e}")
            time.sleep(2)
        except Exception as e:
            print(f"    Unexpected geocoding error for '{query}': {e}")

        time.sleep(1)  # Rate limiting

    return None


def geocode_all_places(
    places: list[dict],
    google_api_key: str | None = None,
) -> list[dict]:
    """Geocode all places, adding lat/lng to each."""
    geocoder = get_geocoder(google_api_key)

    geocoded = 0
    failed = 0

    for i, place in enumerate(places):
        name = place.get("name", "unknown")
        print(f"  [{i + 1}/{len(places)}] Geocoding: {name}...")

        coords = geocode_place(geocoder, place)
        if coords:
            place["latitude"] = coords[0]
            place["longitude"] = coords[1]
            geocoded += 1
            print(f"    -> {coords[0]:.4f}, {coords[1]:.4f}")
        else:
            place["latitude"] = None
            place["longitude"] = None
            failed += 1
            print(f"    -> Could not geocode")

    print(f"\nGeocoded: {geocoded}/{len(places)} ({failed} failed)")
    return places


def build_description(place: dict) -> str:
    """Build a rich description for a map pin."""
    parts = []

    place_type = place.get("type", "lieu")
    icon = TYPE_ICONS.get(place_type, "📍")
    parts.append(f"{icon} {place_type.capitalize()}")

    if place.get("rating") is not None:
        stars = rating_to_stars(place["rating"])
        parts.append(f"Note: {place['rating']}/10 {stars}")

    if place.get("summary"):
        parts.append(f"\n{place['summary']}")

    if place.get("quotes"):
        if isinstance(place["quotes"], list):
            for q in place["quotes"]:
                parts.append(f'💬 "{q}"')
        else:
            parts.append(f'💬 "{place["quotes"]}"')

    if place.get("price_range"):
        parts.append(f"Prix: {place['price_range']}")

    if place.get("address"):
        parts.append(f"📍 {place['address']}")

    if place.get("tags"):
        tags = place["tags"] if isinstance(place["tags"], list) else [place["tags"]]
        parts.append(f"Tags: {', '.join(tags)}")

    source = place.get("source_video", {})
    if source:
        parts.append(f"\n🎥 Vidéo: {source.get('title', '')}")
        if source.get("url"):
            parts.append(source["url"])

    additional = place.get("additional_sources", [])
    for src in additional:
        parts.append(f"🎥 Aussi dans: {src.get('title', '')}")

    return "\n".join(parts)


def generate_kml(places: list[dict], output_path: str) -> str:
    """
    Generate a KML file for Google My Maps import.

    Args:
        places: List of geocoded place dicts
        output_path: Where to save the KML file

    Returns:
        Path to the generated KML file
    """
    kml = simplekml.Kml(name="Tev & Louis - Japan Recommendations")

    # Create folders by type
    folders = {}

    for place in places:
        if place.get("latitude") is None:
            continue

        place_type = place.get("type", "autre")

        # Get or create folder for this type
        if place_type not in folders:
            folders[place_type] = kml.newfolder(
                name=f"{TYPE_ICONS.get(place_type, '📍')} {place_type.capitalize()}"
            )

        folder = folders[place_type]

        name = place.get("name", "Unknown")
        name_fr = place.get("name_fr")
        if name_fr and name_fr != name:
            display_name = f"{name} ({name_fr})"
        else:
            display_name = name

        point = folder.newpoint(
            name=display_name,
            coords=[(place["longitude"], place["latitude"])],
        )
        point.description = build_description(place)

        # Set icon color based on rating (red=bad, green=great)
        color = rating_to_color(place.get("rating"))
        point.style.iconstyle.color = color

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    kml.save(output_path)
    print(f"KML saved to {output_path}")
    return output_path


def generate_csv(places: list[dict], output_path: str) -> str:
    """
    Generate a CSV file for Google My Maps import.
    Google My Maps can import CSV with columns: name, description, latitude, longitude.

    Args:
        places: List of geocoded place dicts
        output_path: Where to save the CSV file

    Returns:
        Path to the generated CSV file
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name",
            "Description",
            "Latitude",
            "Longitude",
            "Type",
            "City",
            "Area",
            "Rating",
            "Price Range",
            "Tags",
            "Video URL",
            "Video Title",
        ])

        for place in places:
            if place.get("latitude") is None:
                continue

            tags = place.get("tags", [])
            if isinstance(tags, list):
                tags = ", ".join(tags)

            source = place.get("source_video", {})

            writer.writerow([
                place.get("name", ""),
                place.get("summary", ""),
                place.get("latitude", ""),
                place.get("longitude", ""),
                place.get("type", ""),
                place.get("city", ""),
                place.get("area", ""),
                place.get("rating", ""),
                place.get("price_range", ""),
                tags,
                source.get("url", ""),
                source.get("title", ""),
            ])

    print(f"CSV saved to {output_path}")
    return output_path


def generate_json(places: list[dict], output_path: str) -> str:
    """Save the full place data as JSON for further processing."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, indent=2)
    print(f"JSON saved to {output_path}")
    return output_path


if __name__ == "__main__":
    # Test with sample data
    sample_places = [
        {
            "name": "Fuunji (風雲児)",
            "name_fr": "Fuunji",
            "type": "restaurant",
            "address": "〒151-0053 Tokyo, Shibuya City, Yoyogi, 2-14-3",
            "city": "Tokyo",
            "area": "Shibuya",
            "rating": "très positif",
            "summary": "Le meilleur tsukemen de Tokyo selon Tev et Louis",
            "quotes": ["C'est le meilleur tsukemen que j'ai mangé de ma vie"],
            "price_range": "€€",
            "tags": ["ramen", "tsukemen", "incontournable"],
            "source_video": {
                "title": "ON TESTE LE MEILLEUR RAMEN DE TOKYO",
                "url": "https://youtube.com/watch?v=example",
            },
            "latitude": 35.6837,
            "longitude": 139.7020,
        }
    ]

    generate_kml(sample_places, "output/test_map.kml")
    generate_csv(sample_places, "output/test_map.csv")
    generate_json(sample_places, "output/test_places.json")
