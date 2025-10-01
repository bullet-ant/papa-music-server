# Papa Music Server

This is the backend server for the Papa Music audio downloader web app. It exposes a FastAPI REST API to extract direct audio stream URLs from video links (e.g., YouTube) using yt-dlp.

## Features
- FastAPI REST API
- `/extract` endpoint: Accepts a video URL, returns available audio streams (format, bitrate, filesize, direct URL)
- Filters out non-audio and invalid streams
- CORS enabled for frontend integration
- Docker-ready for easy deployment

## Setup

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
3. Run the server:
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

## API Usage
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
      "audio_streams": [...], 
      "title": "...", 
      "thumbnail": "..." 
   }
  ```

## Deployment & Updates
- Use Watchtower for automatic Docker container updates
- Rebuild and push image to update yt-dlp

## License
MIT
