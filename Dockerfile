FROM python:3.12-slim
RUN apt-get update && apt-get install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*
RUN GIFSKI_VERSION=1.33.0-1 && curl -fsSL "https://github.com/ImageOptim/gifski/releases/download/1.33.0/gifski_${GIFSKI_VERSION}_amd64.deb" -o /tmp/gifski.deb && dpkg -i /tmp/gifski.deb || apt-get install -f -y && rm /tmp/gifski.deb
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
EXPOSE 5000
CMD ["python", "-m", "app"]
