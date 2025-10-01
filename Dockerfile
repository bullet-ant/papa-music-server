# Use official Python image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install yt-dlp system-wide for subprocess
RUN pip install --upgrade yt-dlp

# Copy app code
COPY main.py ./

COPY cookies.txt ./
COPY setup-cookies.sh ./
RUN sh setup-cookies.sh

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
