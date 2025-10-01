from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExtractRequest(BaseModel):
    url: str


@app.post("/extract")
async def extract_audio(req: ExtractRequest):
    # Sanitize URL to remove playlist and other parameters
    from urllib.parse import urlparse, parse_qs, urlunparse

    parsed_url = urlparse(req.url)
    query_params = parse_qs(parsed_url.query)

    # Keep only the 'v' parameter for YouTube URLs
    if "v" in query_params:
        sanitized_query = f"v={query_params['v'][0]}"
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
    else:
        sanitized_url = req.url

    # Run yt-dlp to get audio formats
    print(f"Extracting audio from URL: {sanitized_url}")
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", sanitized_url],
            capture_output=True,
            text=True,
            check=True,
        )
        info = json.loads(result.stdout)
        # Filter audio formats
        # Filter only valid audio streams
        valid_formats = {"webm", "m4a", "mp3", "aac", "opus", "ogg"}
        audio_streams = [
            {
                "format": f.get("ext"),
                "bitrate": f.get("abr", 0),
                "filesize": f.get("filesize"),
                "url": f.get("url"),
            }
            for f in info.get("formats", [])
            if (
                f.get("vcodec") == "none"
                and f.get("ext") in valid_formats
                and f.get("abr", 0) > 0
                and f.get("url")
            )
        ]
        if not audio_streams:
            raise HTTPException(status_code=404, detail="No valid audio streams found")
        return {
            "audio_streams": audio_streams,
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
        }
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=400, detail="Extraction failed or invalid URL")
