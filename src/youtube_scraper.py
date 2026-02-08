"""
Fetch all videos from a YouTube channel, including descriptions and transcripts.
"""

import os
import json
import time
from pathlib import Path
from googleapiclient.discovery import build
import subprocess
import tempfile


def get_youtube_client(api_key: str | None = None):
    """Create a YouTube Data API client."""
    key = api_key or os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise ValueError("YOUTUBE_API_KEY is required. Set it in .env or pass it directly.")
    return build("youtube", "v3", developerKey=key)


def get_channel_id_from_handle(youtube, handle: str) -> str:
    """Resolve a @handle to a channel ID."""
    # Remove @ prefix if present
    handle = handle.lstrip("@")
    request = youtube.search().list(
        part="snippet",
        q=handle,
        type="channel",
        maxResults=1,
    )
    response = request.execute()
    if response["items"]:
        return response["items"][0]["snippet"]["channelId"]
    raise ValueError(f"Could not find channel for handle: @{handle}")


def fetch_all_video_ids(youtube, channel_id: str) -> list[str]:
    """Fetch all video IDs from a channel using the uploads playlist."""
    # Get the uploads playlist ID
    request = youtube.channels().list(part="contentDetails", id=channel_id)
    response = request.execute()

    if not response["items"]:
        raise ValueError(f"Channel {channel_id} not found")

    uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    video_ids = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request.execute()

        for item in response["items"]:
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids


def fetch_video_details(youtube, video_ids: list[str]) -> list[dict]:
    """Fetch title, description, and publish date for a batch of video IDs."""
    videos = []

    # YouTube API allows max 50 IDs per request
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        request = youtube.videos().list(
            part="snippet",
            id=",".join(batch),
        )
        response = request.execute()

        for item in response["items"]:
            videos.append(
                {
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "published_at": item["snippet"]["publishedAt"],
                    "url": f"https://www.youtube.com/watch?v={item['id']}",
                }
            )

    return videos


def fetch_transcript(
    video_id: str,
    languages: list[str] | None = None,
    cookies_browser: str | None = None,
) -> str | None:
    """Fetch transcript for a video using yt-dlp. Returns None if unavailable."""
    if languages is None:
        languages = ["fr", "en", "ja"]

    url = f"https://www.youtube.com/watch?v={video_id}"
    sub_langs = ",".join(languages)

    with tempfile.TemporaryDirectory() as tmpdir:
        out_template = os.path.join(tmpdir, "sub")
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs", sub_langs,
            "--sub-format", "json3",
            "--output", out_template,
            "--no-warnings",
            "--quiet",
        ]
        if cookies_browser:
            cmd.extend(["--cookies-from-browser", cookies_browser])
        cmd.append(url)

        try:
            subprocess.run(cmd, capture_output=True, timeout=30, check=False)
        except subprocess.TimeoutExpired:
            print(f"    yt-dlp timed out for {video_id}")
            return None

        # Look for downloaded subtitle files (yt-dlp names them sub.LANG.json3)
        for lang in languages:
            sub_file = Path(tmpdir) / f"sub.{lang}.json3"
            if sub_file.exists():
                return _parse_json3_subs(sub_file)

        # Fallback: check for any subtitle file
        for f in Path(tmpdir).glob("sub.*.json3"):
            return _parse_json3_subs(f)

        print(f"    No subtitles found for {video_id}")
        return None


def _parse_json3_subs(path: Path) -> str:
    """Parse a json3 subtitle file into plain text."""
    with open(path) as f:
        data = json.load(f)

    texts = []
    for event in data.get("events", []):
        segs = event.get("segs")
        if segs:
            line = "".join(seg.get("utf8", "") for seg in segs).strip()
            if line and line != "\n":
                texts.append(line)

    return " ".join(texts)


def scrape_channel(
    channel_id: str | None = None,
    handle: str | None = None,
    api_key: str | None = None,
    include_transcripts: bool = True,
    max_videos: int | None = None,
    cache_path: str | None = None,
    cookies_browser: str | None = None,
) -> list[dict]:
    """
    Main function: scrape all videos from a channel.

    Args:
        channel_id: YouTube channel ID (e.g. UCbRFfPqfBHqoz2ABGPDSgLg)
        handle: YouTube handle (e.g. @TevLouis) - used if channel_id not provided
        api_key: YouTube Data API key (falls back to env var)
        include_transcripts: Whether to also fetch transcripts
        max_videos: Limit number of videos (for testing)
        cache_path: Path to cache results as JSON
        cookies_browser: Browser name for yt-dlp cookies (e.g. "chrome", "firefox")

    Returns:
        List of video dicts with keys: video_id, title, description,
        published_at, url, transcript
    """
    # Load partial cache if it exists (resume support)
    cached_videos = {}
    if cache_path and Path(cache_path).exists():
        with open(cache_path) as f:
            for v in json.load(f):
                cached_videos[v["video_id"]] = v
        print(f"Loaded {len(cached_videos)} cached videos from {cache_path}")

    youtube = get_youtube_client(api_key)

    # Resolve handle to channel ID if needed
    if not channel_id:
        if not handle:
            raise ValueError("Either channel_id or handle must be provided")
        print(f"Resolving handle @{handle}...")
        channel_id = get_channel_id_from_handle(youtube, handle)
        print(f"  -> Channel ID: {channel_id}")

    # Fetch all video IDs
    print(f"Fetching video list for channel {channel_id}...")
    video_ids = fetch_all_video_ids(youtube, channel_id)
    print(f"  Found {len(video_ids)} videos")

    if max_videos:
        video_ids = video_ids[:max_videos]
        print(f"  Limited to {max_videos} videos")

    # Fetch video details (only for uncached videos)
    uncached_ids = [vid for vid in video_ids if vid not in cached_videos]
    if uncached_ids:
        print(f"Fetching details for {len(uncached_ids)} new videos...")
        new_videos = fetch_video_details(youtube, uncached_ids)
        for v in new_videos:
            cached_videos[v["video_id"]] = v
    else:
        print("All video details already cached")

    # Build ordered list from video_ids
    videos = [cached_videos[vid] for vid in video_ids if vid in cached_videos]

    # Fetch transcripts (skip videos that already have one)
    if include_transcripts:
        print("Fetching transcripts...")
        for i, video in enumerate(videos):
            if "transcript" in video:
                print(f"  [{i + 1}/{len(videos)}] {video['title'][:60]}... (cached)")
                continue
            print(f"  [{i + 1}/{len(videos)}] {video['title'][:60]}...")
            video["transcript"] = fetch_transcript(video["video_id"], cookies_browser=cookies_browser)
            # Save after each transcript so progress isn't lost
            if cache_path:
                _save_cache(cache_path, videos)
            time.sleep(0.5)
    else:
        for video in videos:
            if "transcript" not in video:
                video["transcript"] = None

    # Final cache save
    if cache_path:
        _save_cache(cache_path, videos)
        print(f"Cached {len(videos)} videos to {cache_path}")

    return videos


def _save_cache(cache_path: str, data: list[dict]):
    """Save data to cache file."""
    Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    videos = scrape_channel(
        handle="TevLouis",
        include_transcripts=True,
        max_videos=5,  # Start small for testing
        cache_path="output/videos_cache.json",
    )

    for v in videos:
        has_transcript = "yes" if v["transcript"] else "no"
        print(f"  {v['title'][:70]} | transcript: {has_transcript}")
