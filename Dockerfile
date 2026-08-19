FROM python:3.11-slim

# ffmpeg is required by discord.py's voice client
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

# Restart-on-crash is handled by the host (docker run --restart or
# docker-compose "restart: always"), not inside the container itself.
CMD ["python", "bot.py"]
