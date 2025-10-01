# Papa Music Server

This is the backend server for the Papa Music audio downloader web app. It exposes a FastAPI REST API to extract direct audio stream URLs from video links (e.g., YouTube) using yt-dlp.

## Features
- FastAPI REST API with comprehensive logging
- `/extract` endpoint: Accepts a video URL, returns available audio streams (format, bitrate, filesize, direct URL)
- `/health` endpoint: Health check with yt-dlp availability status
- Filters out non-audio and invalid streams
- CORS enabled for frontend integration
- Docker-ready for easy deployment
- Extensive request/response logging for debugging

## Logging

The server includes comprehensive logging to help diagnose issues:

- **Log File**: `papa-music.log` (automatically created)
- **Console Output**: All logs are also printed to stdout
- **Request IDs**: Each request gets a unique ID for tracking
- **Logged Information**:
  - Server startup/shutdown
  - All incoming requests (method, path, client, headers)
  - Request duration
  - URL parsing and sanitization
  - yt-dlp command execution and output
  - Audio stream filtering process
  - Errors with full stack traces

### Viewing Logs

```sh
# Tail the log file
tail -f papa-music.log

# View recent errors
grep ERROR papa-music.log

# View a specific request by ID
grep "20250101_123456_789012" papa-music.log
```

## Setup

### Important: YouTube Bot Detection ⚠️

When running on cloud servers (Digital Ocean, AWS, etc.), YouTube may block requests. See [BOT_DETECTION.md](BOT_DETECTION.md) for solutions.

**Quick Fix:**
```sh
# Run the setup script
chmod +x setup-cookies.sh
./setup-cookies.sh

# Follow the instructions to export cookies from your browser
```

### Local Development
1. Create a virtual environment:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   
   This includes:
   - `fastapi` - Web framework
   - `uvicorn` - ASGI server
   - `pydantic` - Data validation
   - `yt-dlp` - YouTube downloader
   - `python-dotenv` - Load environment variables from .env file
   
3. **(Optional) Configure environment variables:**
   ```sh
   cp .env.example .env
   # Edit .env to add cookies path, proxy, etc.
   ```
4. Run the server:
   ```sh
   uvicorn main:app --reload
   ```

### Docker
1. Build the Docker image:
   ```sh
   docker build -t papa-music-server .
   ```
2. Run the container:
   ```sh
   docker run -d --name papa-music-server -p 8000:8000 papa-music-server
   ```

### Docker with Cookies (Recommended for Cloud)
```sh
# Build
docker build -t papa-music-server .

# Run with cookies mounted
docker run -d \
  --name papa-music-server \
  -p 8000:8000 \
  -v $(pwd)/cookies.txt:/app/cookies.txt \
  -e YOUTUBE_COOKIES_PATH=/app/cookies.txt \
  papa-music-server
```

## Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Optional: Path to YouTube cookies file (helps bypass bot detection)
YOUTUBE_COOKIES_PATH=/path/to/cookies.txt
```

## API Usage

### Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check with yt-dlp status
- `POST /extract` - Extract audio streams from YouTube URL

### Examples

#### Health Check
```sh
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-01T12:34:56.789",
  "yt_dlp_available": true,
  "yt_dlp_version": "2024.09.27"
}
```

#### Extract Audio
- `POST /extract`
  - Request body: 
  ```json
   {
      "url": "https://www.youtube.com/watch?v=..." 
   }
  ```
  - Response: 
  ```json
   {
      "audio_streams": [
         {
            "format": "webm",
            "bitrate": 51.895,
            "filesize": 2110199,
            "url": "https://..."
         },
         {
            "format": "m4a",
            "bitrate": 129.0,
            "filesize": 5242880,
            "url": "https://..."
         },
      ], 
      "title": "...", 
      "thumbnail": "..." 
   }
  ```

## Deployment & Updates
- Use Watchtower for automatic Docker container updates
- Rebuild and push image to update yt-dlp

## License
MIT
