"""
Use Google Gemini to extract place information from video descriptions and transcripts.
"""

import os
import json
import re
from google import genai

EXTRACTION_PROMPT = """\
Tu es un assistant spécialisé dans l'extraction d'informations sur des lieux à partir de vidéos YouTube francophones sur le Japon.

Voici les informations d'une vidéo de la chaîne "Tev & Louis" :

**Titre** : {title}

**Description** :
{description}

**Transcription** :
{transcript}

---

Analyse ces informations et extrais TOUS les lieux mentionnés (restaurants, cafés, temples, parcs, magasins, quartiers remarquables, attractions, etc.).

Pour chaque lieu, donne :
1. **name** : Le nom du lieu (en japonais si possible, sinon en français/anglais)
2. **name_fr** : Le nom en français s'il est différent
3. **type** : Le type de lieu (restaurant, café, temple, parc, magasin, attraction, quartier, hôtel, bar, etc.)
4. **address** : L'adresse exacte si mentionnée dans la description ou la transcription
5. **city** : La ville (Tokyo, Osaka, Kyoto, etc.)
6. **area** : Le quartier si mentionné (Shibuya, Shinjuku, Asakusa, etc.)
7. **rating** : Une note de 1 à 10 reflétant l'avis de Tev et Louis (1 = ils ont détesté, 5 = neutre/pas d'avis marqué, 10 = coup de cœur absolu). Déduis la note à partir de leur ton, leurs mots et leur enthousiasme
8. **summary** : Un résumé en 1-2 phrases de ce qu'ils en ont dit
9. **quotes** : 1-2 citations courtes marquantes de la vidéo sur ce lieu (en français)
10. **price_range** : Fourchette de prix si mentionnée (€, €€, €€€, €€€€)
11. **tags** : Tags pertinents (ex: ramen, sushi, street-food, vue, incontournable, secret, etc.)

IMPORTANT :
- N'extrais que les lieux réels et spécifiques, pas les mentions génériques
- Si l'adresse est dans la description, copie-la exactement
- Si le lieu est juste mentionné en passant sans vraie recommandation, inclus-le quand même mais note-le
- Réponds UNIQUEMENT en JSON valide, sous forme d'un tableau d'objets
- Si aucun lieu n'est trouvé, réponds avec un tableau vide []

Réponds avec le JSON uniquement, sans markdown ni commentaires :
"""


def extract_places_from_video(
    video: dict,
    api_key: str | None = None,
    model: str = "gemini-2.0-flash",
) -> list[dict]:
    """
    Extract place information from a single video using Gemini.

    Args:
        video: Dict with keys title, description, transcript, url
        api_key: Gemini API key (falls back to env var)
        model: Gemini model to use

    Returns:
        List of place dicts
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY is required")

    client = genai.Client(api_key=key)

    transcript_text = video.get("transcript") or "(Transcription non disponible)"
    # Truncate very long transcripts to stay within context limits
    if len(transcript_text) > 30000:
        transcript_text = transcript_text[:30000] + "\n... (tronqué)"

    prompt = EXTRACTION_PROMPT.format(
        title=video["title"],
        description=video["description"],
        transcript=transcript_text,
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    response_text = response.text.strip()

    # Parse JSON response
    try:
        places = json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from the response if it's wrapped in markdown
        json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
        if json_match:
            places = json.loads(json_match.group())
        else:
            print(f"  WARNING: Could not parse response for '{video['title']}'")
            print(f"  Response: {response_text[:200]}...")
            return []

    # Attach video metadata to each place
    for place in places:
        place["source_video"] = {
            "title": video["title"],
            "url": video.get("url", ""),
            "published_at": video.get("published_at", ""),
        }

    return places


def extract_places_from_videos(
    videos: list[dict],
    api_key: str | None = None,
    model: str = "gemini-2.0-flash",
    cache_path: str | None = None,
) -> list[dict]:
    """
    Extract places from all videos.

    Args:
        videos: List of video dicts from youtube_scraper
        api_key: Gemini API key
        model: Gemini model to use
        cache_path: Path to cache extracted places

    Returns:
        List of all extracted place dicts
    """
    # Check cache
    if cache_path:
        from pathlib import Path
        if Path(cache_path).exists():
            print(f"Loading cached places from {cache_path}")
            with open(cache_path) as f:
                return json.load(f)

    all_places = []

    for i, video in enumerate(videos):
        print(f"[{i + 1}/{len(videos)}] Extracting places from: {video['title'][:60]}...")

        places = extract_places_from_video(video, api_key=api_key, model=model)
        print(f"  -> Found {len(places)} places")

        all_places.extend(places)

    # Deduplicate by name + city
    seen = set()
    unique_places = []
    for place in all_places:
        dedup_key = (place.get("name", "").lower(), place.get("city", "").lower())
        if dedup_key not in seen:
            seen.add(dedup_key)
            unique_places.append(place)
        else:
            # Merge: keep the one with more info, add video source
            for existing in unique_places:
                existing_key = (existing.get("name", "").lower(), existing.get("city", "").lower())
                if existing_key == dedup_key:
                    # Add this video as an additional source
                    if "additional_sources" not in existing:
                        existing["additional_sources"] = []
                    existing["additional_sources"].append(place.get("source_video", {}))
                    break

    print(f"\nTotal: {len(all_places)} place mentions -> {len(unique_places)} unique places")

    # Cache results
    if cache_path:
        from pathlib import Path
        Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(unique_places, f, ensure_ascii=False, indent=2)
        print(f"Cached {len(unique_places)} places to {cache_path}")

    return unique_places


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    # Test with sample data
    sample_video = {
        "title": "ON TESTE LE MEILLEUR RAMEN DE TOKYO 🍜",
        "description": """On a testé le meilleur ramen de Tokyo selon les japonais !

📍 Fuunji (風雲児)
Adresse : 〒151-0053 Tokyo, Shibuya City, Yoyogi, 2-14-3
Google Maps : https://maps.google.com/...

📍 Ichiran Shibuya
Adresse : 〒150-0042 Tokyo, Shibuya, Dogenzaka, 1-22-7

Merci d'avoir regardé !""",
        "transcript": "Salut tout le monde, aujourd'hui on va tester les meilleurs ramen de Tokyo. On commence par Fuunji, c'est un restaurant de tsukemen qui est incroyable. Honnêtement c'est le meilleur tsukemen que j'ai mangé de ma vie. Le bouillon est super concentré, les nouilles sont parfaites. Ensuite on est allés chez Ichiran, c'est plus classique mais c'est toujours bon, le tonkotsu est correct mais rien d'exceptionnel.",
        "url": "https://www.youtube.com/watch?v=example",
        "published_at": "2024-01-15T10:00:00Z",
    }

    places = extract_places_from_video(sample_video)
    print(json.dumps(places, ensure_ascii=False, indent=2))
