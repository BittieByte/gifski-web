# ---------- Stage 1: Build gifski ----------
FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y \
    curl build-essential pkg-config libssl-dev ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

# Install rustup
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable

ENV RUSTFLAGS="-C target-cpu=native"

RUN cargo install gifski
RUN strip /usr/local/cargo/bin/gifski

# ---------- Stage 2: Python runtime ----------
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy gifski binary from builder
COPY --from=builder /usr/local/cargo/bin/gifski /usr/local/bin/gifski

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY app.py .

EXPOSE 5000
CMD ["python", "app.py"]
