#!/bin/sh
# Papa Music - YouTube Cookies Setup Script
# This script helps you set up cookies to bypass YouTube bot detection
# Note: Using /bin/sh for better compatibility

echo "=========================================="
echo "Papa Music - YouTube Cookies Setup"
echo "=========================================="
echo ""

# Check if yt-dlp is installed
if ! command -v yt-dlp >/dev/null 2>&1; then
    echo "❌ yt-dlp is not installed!"
    echo "Please install it first: pip install yt-dlp"
    exit 1
fi

echo "✅ yt-dlp is installed"
echo ""

# Export from browser
echo "Export Cookies from Browser"
echo "=================================================="
echo ""
echo "1. Install a browser extension:"
echo "   - Chrome/Edge: 'Get cookies.txt LOCALLY'"
echo "     https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc"
echo ""
echo "   - Firefox: 'cookies.txt'"
echo "     https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/"
echo ""
echo "2. Go to youtube.com and log in"
echo "3. Click the extension icon and export cookies.txt"
echo "4. Save the file as 'cookies.txt' in this directory"
echo ""

# Check if cookies.txt exists
if [ -f "cookies.txt" ]; then
    echo "✅ Found cookies.txt in current directory!"
    
    # Set in .env
    if [ -f ".env" ]; then
        # Update existing .env
        if grep -q "YOUTUBE_COOKIES_PATH" .env; then
            # Update existing line (portable way)
            grep -v "^YOUTUBE_COOKIES_PATH=" .env > .env.tmp
            echo "YOUTUBE_COOKIES_PATH=$(pwd)/cookies.txt" >> .env.tmp
            mv .env.tmp .env
            echo "✅ Updated YOUTUBE_COOKIES_PATH in .env"
        else
            # Add new line
            echo "" >> .env
            echo "YOUTUBE_COOKIES_PATH=$(pwd)/cookies.txt" >> .env
            echo "✅ Added YOUTUBE_COOKIES_PATH to .env"
        fi
    else
        # Create new .env
        echo "YOUTUBE_COOKIES_PATH=$(pwd)/cookies.txt" > .env
        echo "✅ Created .env with YOUTUBE_COOKIES_PATH"
    fi
    
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "Now restart your server:"
    echo "  uvicorn main:app --reload"
    echo ""
    
else
    echo "⚠️  cookies.txt not found"
    echo ""
    echo "After exporting cookies.txt from your browser:"
    echo "  1. Place it in: $(pwd)"
    echo "  2. Run this script again"
    echo ""
fi
# Test connection
echo ""
echo "Testing YouTube Connection..."
echo "=============================="
echo ""

TEST_URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

if [ -f "cookies.txt" ]; then
    echo "Testing with cookies..."
    if yt-dlp --cookies cookies.txt --dump-json "$TEST_URL" > /dev/null 2>&1; then
        echo "✅ SUCCESS! Cookies are working!"
    else
        echo "❌ FAILED! Cookies may be expired or invalid"
        echo "Try exporting fresh cookies from your browser"
    fi
else
    echo "Testing without cookies..."
    if yt-dlp --dump-json "$TEST_URL" > /dev/null 2>&1; then
        echo "✅ SUCCESS! No bot detection (yet)"
        echo "Note: This may not work on cloud servers"
    else
        echo "❌ FAILED! Bot detection is active"
        echo "You need to set up cookies (see Export from browser above)"
    fi
fi

echo ""
echo "=========================================="
echo "For more help, see: BOT_DETECTION.md"
echo "=========================================="
