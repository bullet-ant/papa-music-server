# YouTube Bot Detection Workarounds

This document explains how to handle YouTube's bot detection when running Papa Music on cloud servers like Digital Ocean.

## The Problem

YouTube actively blocks automated tools like yt-dlp, especially when running on:
- Cloud servers (AWS, Digital Ocean, GCP, etc.)
- VPS providers
- Datacenter IPs

They detect this through:
- User-agent strings
- Missing browser headers
- IP reputation
- Request patterns

## Current Solutions Implemented

### 1. Custom User-Agent & Headers
The server now sends realistic browser headers:
- Chrome 120 User-Agent
- Standard Accept headers
- Accept-Language
- Sec-Fetch headers

### 2. Request Throttling
- `--sleep-requests 1`: Adds 1 second delay between requests
- `--extractor-retries 3`: Retries up to 3 times on failure

### 3. Increased Timeout
- Timeout increased from 30s to 45s to accommodate delays

## Additional Solutions (If Still Blocked)

### Option 1: Use Cookies (Recommended)

Export cookies from your logged-in YouTube session:

1. **Install Browser Extension**:
   - Chrome/Edge: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. **Export YouTube Cookies**:
   - Go to youtube.com
   - Log in to your account
   - Click the extension icon
   - Export cookies.txt

3. **Upload to Server**:
   ```bash
   scp cookies.txt user@your-server:/path/to/papa-music/server/
   ```

4. **Update main.py** to use cookies:
   ```python
   yt_dlp_command = [
       "yt-dlp",
       "--dump-json",
       "--cookies", "cookies.txt",  # Add this line
       "--user-agent", "...",
       # ... rest of command
   ]
   ```

### Option 2: Use Proxy/VPN

Route traffic through residential proxies:

```python
yt_dlp_command = [
    "yt-dlp",
    "--dump-json",
    "--proxy", "http://proxy-server:port",
    # ... rest of command
]
```

**Proxy Services**:
- BrightData
- Oxylabs
- SmartProxy
- Residential proxies work better than datacenter

### Option 3: Use OAuth

Use YouTube's official API for metadata (requires API key):

```python
# For metadata only, still need yt-dlp for stream URLs
from googleapiclient.discovery import build

youtube = build('youtube', 'v3', developerKey='YOUR_API_KEY')
request = youtube.videos().list(part='snippet', id=video_id)
response = request.execute()
```

### Option 4: Update yt-dlp Frequently

YouTube changes their detection frequently:

```bash
# Update yt-dlp
pip install --upgrade yt-dlp

# Or in Docker
docker exec papa-music-server pip install --upgrade yt-dlp
```

### Option 5: Use IPv6

Some providers have better IPv6 reputation:

```bash
# Force IPv6
yt-dlp --force-ipv6 URL
```

Update command:
```python
yt_dlp_command = [
    "yt-dlp",
    "--force-ipv6",  # Add this
    # ... rest
]
```

### Option 6: Rotate User-Agents

Vary the user-agent on each request:

```python
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

user_agent = random.choice(USER_AGENTS)
```

### Option 7: Use SponsorBlock Segments API

For some metadata, use alternative APIs:
- [SponsorBlock API](https://sponsor.ajay.app/)
- [Invidious API](https://docs.invidious.io/)
- [Piped API](https://piped-docs.kavin.rocks/)

## Testing

### Test if you're blocked:
```bash
# From your server
yt-dlp --dump-json "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Common Error Messages:
- "Sign in to confirm you're not a bot"
- "This video is unavailable"
- "Video unavailable. This video is not available"
- HTTP Error 403: Forbidden

## Recommended Strategy

**For Production (Ranked by Effectiveness)**:

1. **Use cookies.txt** (Most effective, free)
   - Export from your own YouTube account
   - Update every few weeks

2. **Keep yt-dlp updated** (Essential)
   - Check weekly for updates
   - YouTube blocks old versions

3. **Use residential proxy** (Most reliable, costs money)
   - Rotate IPs
   - Looks like real user traffic

4. **Combine multiple methods**:
   - Cookies + Updated yt-dlp
   - Proxy + Cookies + Headers

## Emergency Fallback

If all else fails, you can:
1. Run the server on a home network (better IP reputation)
2. Use a different video source (Vimeo, Dailymotion, etc.)
3. Use YouTube's official API for metadata (limited quota)
4. Implement a hybrid approach (official API + yt-dlp)

## Monitoring

Add monitoring for bot detection:

```python
if "Sign in to confirm" in result.stderr or "bot" in result.stderr.lower():
    logger.error(f"[{request_id}] Bot detection triggered!")
    # Send alert, rotate proxy, update cookies, etc.
```

## Legal Considerations

- Using cookies: Check YouTube's Terms of Service
- Using proxies: Ensure compliance with regulations
- Rate limiting: Don't abuse the service
- Consider YouTube API: Official, but has quota limits

## References

- [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp)
- [yt-dlp wiki on extractors](https://github.com/yt-dlp/yt-dlp/wiki)
- [YouTube bot detection thread](https://github.com/yt-dlp/yt-dlp/issues)
