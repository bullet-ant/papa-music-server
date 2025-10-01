from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import logging
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("papa-music.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load environment variables for configuration
YOUTUBE_COOKIES_PATH = os.getenv("YOUTUBE_COOKIES_PATH")

app = FastAPI()

# Log startup
logger.info("=" * 80)
logger.info("Papa Music Server Starting...")
logger.info(f"Startup time: {datetime.now().isoformat()}")
logger.info(f"Cookies configured: {bool(YOUTUBE_COOKIES_PATH)}")
if YOUTUBE_COOKIES_PATH:
    cookies_exist = Path(YOUTUBE_COOKIES_PATH).exists()
    logger.info(f"Cookies file exists: {cookies_exist}")
    if not cookies_exist:
        logger.warning(f"Cookies file not found at: {YOUTUBE_COOKIES_PATH}")
logger.info("=" * 80)

# Allow CORS for frontend
logger.info("Configuring CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured successfully")


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] Incoming request: {request.method} {request.url.path}")
    logger.info(
        f"[{request_id}] Client: {request.client.host if request.client else 'Unknown'}"
    )
    logger.info(f"[{request_id}] Headers: {dict(request.headers)}")

    start_time = datetime.now()

    try:
        response = await call_next(request)
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"[{request_id}] Response status: {response.status_code}")
        logger.info(f"[{request_id}] Duration: {duration:.3f}s")
        return response
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"[{request_id}] Request failed after {duration:.3f}s: {str(e)}")
        logger.exception(f"[{request_id}] Exception details:")
        raise


class ExtractRequest(BaseModel):
    url: str


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "name": "Papa Music API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "/": "API information",
            "/health": "Health check",
            "/extract": "Extract audio from YouTube URL (POST)",
        },
    }


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    try:
        # Check if yt-dlp is available
        result = subprocess.run(
            ["yt-dlp", "--version"], capture_output=True, text=True, timeout=5
        )
        yt_dlp_version = result.stdout.strip()
        logger.info(f"yt-dlp version: {yt_dlp_version}")

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "yt_dlp_available": True,
            "yt_dlp_version": yt_dlp_version,
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "yt_dlp_available": False,
            "error": str(e),
        }


@app.post("/extract")
async def extract_audio(req: ExtractRequest):
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] New extraction request received")
    logger.info(f"[{request_id}] Raw URL: {req.url}")

    # Sanitize URL to remove playlist and other parameters
    from urllib.parse import urlparse, parse_qs, urlunparse

    try:
        parsed_url = urlparse(req.url)
        logger.info(
            f"[{request_id}] Parsed URL - Scheme: {parsed_url.scheme}, Netloc: {parsed_url.netloc}, Path: {parsed_url.path}"
        )

        query_params = parse_qs(parsed_url.query)
        logger.info(f"[{request_id}] Query parameters: {query_params}")

        # Keep only the 'v' parameter for YouTube URLs
        if "v" in query_params:
            video_id = query_params["v"][0]
            logger.info(f"[{request_id}] Extracted video ID: {video_id}")
            sanitized_query = f"v={video_id}"
            sanitized_url = urlunparse(
                (
                    parsed_url.scheme,
                    parsed_url.netloc,
                    parsed_url.path,
                    "",
                    sanitized_query,
                    "",
                )
            )
            logger.info(f"[{request_id}] Sanitized URL: {sanitized_url}")
        else:
            sanitized_url = req.url
            logger.warning(f"[{request_id}] No 'v' parameter found, using original URL")

        # Run yt-dlp to get audio formats with anti-bot measures
        logger.info(f"[{request_id}] Starting yt-dlp extraction...")

        # Build command with anti-bot measures
        yt_dlp_command = [
            "yt-dlp",
            "--dump-json",
            "--extractor-retries",
            "3",
            "--sleep-requests",
            "1",
        ]

        # Add cookies if configured
        if YOUTUBE_COOKIES_PATH and Path(YOUTUBE_COOKIES_PATH).exists():
            yt_dlp_command.extend(["--cookies", YOUTUBE_COOKIES_PATH])
            logger.info(f"[{request_id}] Using cookies from: {YOUTUBE_COOKIES_PATH}")
        else:
            logger.warning(
                f"[{request_id}] No cookies configured - may face bot detection"
            )

        # Add the URL
        yt_dlp_command.append(sanitized_url)

        logger.info(f"[{request_id}] Command: yt-dlp {' '.join(yt_dlp_command)}")

        result = subprocess.run(
            yt_dlp_command,
            capture_output=True,
            text=True,
            check=True,
            timeout=45,  # Increased timeout due to sleep-requests
        )

        logger.info(f"[{request_id}] yt-dlp command completed successfully")
        logger.debug(f"[{request_id}] stdout length: {len(result.stdout)} characters")

        if result.stderr:
            logger.warning(f"[{request_id}] yt-dlp stderr: {result.stderr[:500]}")

        info = json.loads(result.stdout)
        logger.info(f"[{request_id}] JSON parsed successfully")
        logger.info(f"[{request_id}] Video title: {info.get('title', 'N/A')}")
        logger.info(
            f"[{request_id}] Total formats available: {len(info.get('formats', []))}"
        )

        # Filter audio formats
        # Filter only valid audio streams
        valid_formats = {"webm", "m4a", "mp3", "aac", "opus", "ogg"}
        logger.info(f"[{request_id}] Valid audio formats: {valid_formats}")

        all_formats = info.get("formats", [])
        logger.info(f"[{request_id}] Processing {len(all_formats)} formats...")

        audio_count = 0
        for idx, f in enumerate(all_formats):
            if f.get("vcodec") == "none":
                audio_count += 1
                logger.debug(
                    f"[{request_id}] Audio format #{audio_count}: ext={f.get('ext')}, abr={f.get('abr')}, vcodec={f.get('vcodec')}, has_url={bool(f.get('url'))}"
                )

        logger.info(f"[{request_id}] Found {audio_count} audio-only formats")

        audio_streams = [
            {
                "format": f.get("ext"),
                "bitrate": f.get("abr", 0),
                "filesize": f.get("filesize"),
                "url": f.get("url"),
            }
            for f in all_formats
            if (
                f.get("vcodec") == "none"
                and f.get("ext") in valid_formats
                and f.get("abr", 0) > 0
                and f.get("url")
            )
        ]

        logger.info(
            f"[{request_id}] Filtered to {len(audio_streams)} valid audio streams"
        )

        for idx, stream in enumerate(audio_streams):
            logger.info(
                f"[{request_id}] Stream #{idx + 1}: {stream['format']} @ {stream['bitrate']}kbps, size: {stream['filesize']}"
            )

        if not audio_streams:
            logger.error(f"[{request_id}] No valid audio streams found after filtering")
            raise HTTPException(status_code=404, detail="No valid audio streams found")

        response = {
            "audio_streams": audio_streams,
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
        }

        logger.info(
            f"[{request_id}] Extraction successful - returning {len(audio_streams)} streams"
        )
        logger.info(f"[{request_id}] Request completed successfully")
        return response

    except subprocess.TimeoutExpired:
        logger.error(f"[{request_id}] yt-dlp command timed out after 45 seconds")
        raise HTTPException(status_code=408, detail="Extraction timed out")
    except subprocess.CalledProcessError as e:
        logger.error(
            f"[{request_id}] yt-dlp command failed with return code {e.returncode}"
        )
        logger.error(f"[{request_id}] stderr: {e.stderr}")
        logger.error(f"[{request_id}] stdout: {e.stdout}")
        raise HTTPException(status_code=400, detail="Extraction failed or invalid URL")
    except json.JSONDecodeError as e:
        logger.error(f"[{request_id}] Failed to parse JSON from yt-dlp output")
        logger.error(f"[{request_id}] JSON error: {str(e)}")
        logger.error(
            f"[{request_id}] Raw output (first 1000 chars): {result.stdout[:1000]}"
        )
        raise HTTPException(status_code=500, detail="Failed to parse video information")
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {type(e).__name__}: {str(e)}")
        logger.exception(f"[{request_id}] Full traceback:")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
