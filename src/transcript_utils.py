"""Transcript utilities for YouTube video processing via Apify.

Handles video ID extraction, synchronous Apify API calls, and transcript formatting.
"""

import re
import requests
from typing import Dict, List, Tuple, Any
from urllib.parse import urlparse, parse_qs
from src import config


def extract_video_id_from_url(youtube_url: str) -> str:
    """Extract video ID from YouTube URL.

    For now, returns URL as-is since Apify Actor accepts full URLs.
    Keep this function for future flexibility if we need actual ID extraction.

    Args:
        youtube_url: YouTube video URL

    Returns:
        YouTube URL (unchanged for now)
    """
    return youtube_url


def normalize_youtube_url(raw_url: str) -> str:
    """
    Accepts any reasonable YouTube URL (watch, youtu.be, shorts, with or without extra params)
    and returns a canonical:
        https://www.youtube.com/watch?v=VIDEO_ID

    Raises RuntimeError if a valid 11-char video ID cannot be extracted.
    """
    if not raw_url:
        raise RuntimeError("Empty YouTube URL")

    url = raw_url.strip()

    # Add scheme if missing
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    path = parsed.path or ""
    query = parse_qs(parsed.query or "")

    video_id = None

    # youtu.be/dQw4w9WgXcQ
    if "youtu.be" in host:
        video_id = path.lstrip("/")

    # youtube.com
    elif "youtube.com" in host:
        # /watch?v=ID
        if path.startswith("/watch"):
            video_id = query.get("v", [None])[0]
        # /shorts/ID
        elif path.startswith("/shorts/"):
            parts = path.split("/")
            if len(parts) >= 3:
                video_id = parts[2]
        # /embed/ID
        elif path.startswith("/embed/"):
            parts = path.split("/")
            if len(parts) >= 3:
                video_id = parts[2]

    if not video_id or len(video_id) != 11:
        raise RuntimeError(
            f"Invalid YouTube URL format. Must contain an 11-character video ID: {raw_url!r}"
        )

    return f"https://www.youtube.com/watch?v={video_id}"


def seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS.xx timestamp format.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string
    """
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:05.2f}"


def call_apify_actor(youtube_url: str, language: str = "en") -> Dict[str, Any]:
    """Call Apify Actor to get YouTube transcript with normalized URL.

    Args:
        youtube_url: YouTube video URL (any format)
        language: Language code for transcript (default: "en")

    Returns:
        Raw response data from Apify Actor

    Raises:
        RuntimeError: If API call fails or returns invalid data
    """
    config.validate_config()

    # Normalize the YouTube URL to canonical format
    canonical_url = normalize_youtube_url(youtube_url)

    # Build the synchronous endpoint URL
    url = (
        f"https://api.apify.com/v2/acts/"
        f"{config.APIFY_ACTOR_ID}/run-sync-get-dataset-items"
        f"?token={config.APIFY_TOKEN}"
    )

    # Prepare payload with canonical URL
    payload = {
        "youtube_url": canonical_url,
        "language": (language or "en").strip(),
    }

    try:
        # Call the synchronous endpoint that returns dataset items directly
        response = requests.post(url, json=payload, timeout=300)

        if response.status_code >= 400:
            raise RuntimeError(
                f"Failed to call Apify Actor ({response.status_code}): {response.text}"
            )

        items = response.json()

        if not isinstance(items, list) or not items:
            raise RuntimeError(
                f"Apify Actor returned no items or unexpected payload: {items}"
            )

        item = items[0]  # Single video response

        # Check status if available
        status = item.get("status", "")
        if status and status != "success":
            message = item.get("message", "Unknown error")
            raise RuntimeError(f"Apify Actor failed: {message}")

        # Validate transcript exists
        transcript = item.get("transcript", [])
        if not transcript:
            raise RuntimeError(
                f"No transcript available for video: {canonical_url}. "
                f"Video may not have captions or may be private/restricted."
            )

        return item

    except requests.RequestException as e:
        raise RuntimeError(f"Failed to call Apify Actor: {e}")
    except (KeyError, ValueError) as e:
        raise RuntimeError(f"Unexpected response format from Apify Actor: {e}")


def flatten_transcript(item: Dict[str, Any]) -> str:
    """Convert Apify transcript data to formatted text.

    Builds a transcript string with timestamp ranges for each segment:
    Format: [MM:SS.xx–MM:SS.xx] transcript text

    Args:
        item: Apify Actor response item containing transcript data

    Returns:
        Formatted transcript string

    Raises:
        RuntimeError: If transcript format is invalid
    """
    try:
        transcript_segments = item["transcript"]

        if not isinstance(transcript_segments, list):
            raise RuntimeError("Transcript is not in expected list format")

        lines = []
        for segment in transcript_segments:
            if not isinstance(segment, dict):
                continue

            text = segment.get("text", "").strip()
            start = segment.get("start", 0)
            end = segment.get("end", 0)

            if not text:
                continue

            start_ts = seconds_to_timestamp(start)
            end_ts = seconds_to_timestamp(end)

            lines.append(f"[{start_ts}–{end_ts}] {text}")

        return "\n".join(lines)

    except KeyError as e:
        raise RuntimeError(f"Missing required field in transcript data: {e}")


def get_transcript_from_youtube(youtube_url: str, language: str = "en") -> Tuple[str, Dict[str, Any]]:
    """Get formatted transcript and metadata from YouTube URL.

    Main function that orchestrates the full process:
    1. Call Apify Actor synchronously using run-sync-get-dataset-items
    2. Format transcript text
    3. Extract metadata

    Args:
        youtube_url: YouTube video URL
        language: Language code for transcript

    Returns:
        Tuple of (formatted_transcript_text, metadata_dict)

    Raises:
        RuntimeError: If any step in the process fails
    """
    # Get raw data from Apify
    item = call_apify_actor(youtube_url, language)

    # Build formatted transcript
    transcript_text = flatten_transcript(item)

    # Extract metadata
    metadata = {
        "title": item.get("title", ""),
        "channel_name": item.get("channel_name", ""),
        "video_id": item.get("video_id", ""),
        "url": item.get("url", youtube_url),
        "duration_seconds": item.get("duration_seconds", 0),
        "thumbnail": item.get("thumbnail", ""),
        "language": item.get("language", language),
        "view_count": item.get("view_count", 0),
        "like_count": item.get("like_count", 0),
        "comment_count": item.get("comment_count", 0),
        "published_at": item.get("published_at", ""),
        "is_auto_generated": item.get("is_auto_generated", False)
    }

    return transcript_text, metadata