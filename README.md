# gifski-web

A self-hosted web interface for [gifski](https://gif.ski/) — convert videos and GIFs into high-quality, optimized GIFs through a simple browser UI.

Built with Flask, powered by `gifski` + `ffmpeg`, and designed to run behind Docker.

---

## Features

- **Video → GIF conversion** — upload a video file and gifski-web extracts frames via `ffmpeg`, then encodes them into a high-quality GIF
- **GIF re-optimization** — pass an existing GIF directly to gifski for re-encoding and size reduction
- **Full gifski control** — quality, FPS, width, height, motion quality, lossy quality, loop repeat, fixed color, matte color, and frame sort options are all exposed in the UI
- **Drag-and-drop upload** — drop a file onto the upload zone or click to browse
- **Size reduction stats** — see original size, optimized size, and percentage reduction on the result page
- **Preview before download** — the result page displays the finished GIF inline
- **Input sanitization** — all form values are validated server-side before being passed to subprocesses

---

## Screenshots

> Upload page with basic and advanced options, and the result page showing size stats + GIF preview.
<img width="722" height="655" alt="2026-04-07_21-19-44" src="https://github.com/user-attachments/assets/72d9ed73-078a-4064-8ad0-f2d6daa3c5a7" />
<img width="716" height="682" alt="2026-04-07_21-31-14" src="https://github.com/user-attachments/assets/f6a46396-66b1-4c96-9c77-8a1a4722179f" />

---

## Requirements

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

That's it. `gifski` and `ffmpeg` are installed inside the container — nothing needs to be on your host machine.

---

## Quick Start

### Option 1: Automated install script

```bash
git clone https://github.com/BittieByte/gifski-web.git
cd gifski-web
chmod +x install.sh
./install.sh
```

The script will:
1. Check for (or install) Docker and Docker Compose
2. Prompt you for an installation directory (default: `~/gifski-web`)
3. Tear down any existing container with the same name
4. Build the image from source and start the container

Once complete, open **http://localhost:5000** in your browser.

### Option 2: Manual Docker Compose

```bash
git clone https://github.com/BittieByte/gifski-web.git
cd gifski-web
mkdir -p uploads
docker compose up -d
```

Then open **http://localhost:5000**.

---

## Usage

1. Open the web UI at `http://localhost:5000`
2. Drag and drop (or click to select) a video or GIF file
3. Adjust options as needed (see below)
4. Click **Optimize**
5. Preview the result, view size stats, and download the GIF

### Options

| Option | Description | Default |
|---|---|---|
| **Quality** | Overall GIF quality (1–100) | `90` |
| **FPS** | Output frames per second — lower = smaller file | original |
| **Width** | Output width in pixels | original |
| **Height** | Output height in pixels | original |
| **Fast** | ~2× faster encoding at a slight quality cost | off |
| **Extra Quality** | Slower encoding for higher quality | off |
| **Motion Quality** | How accurately motion between frames is preserved (1–100) | — |
| **Lossy Quality** | Allow compression artifacts for smaller output (1–100) | — |
| **Repeat** | Loop count: `0` = infinite, `-1` = no loop | — |
| **Fixed Color** | Reserve a specific hex color in the palette (`#RRGGBB`) | — |
| **Matte Color** | Background color for transparency compositing (`#RRGGBB`) | — |
| **No Sort** | Keep frames in the exact order provided | off |

If neither width nor height is specified, the original media dimensions are used automatically — preventing gifski's default downscaling behavior.

---

## Docker Details

The image uses a two-stage build:

- **Stage 1 (builder):** Compiles `gifski` from source using the Rust toolchain on `debian:bookworm-slim`, with `RUSTFLAGS="-C target-cpu=native"` for optimized output
- **Stage 2 (runtime):** `python:3.12-slim` with `ffmpeg` installed; copies the compiled `gifski` binary from the builder stage

Uploaded files are stored in the `./uploads` directory, which is bind-mounted from the host so files persist across container restarts.

```yaml
# docker-compose.yml (summary)
ports:
  - "5000:5000"
volumes:
  - ./uploads:/app/uploads
restart: unless-stopped
```

### Useful commands

```bash
# Stop the container
docker compose down

# View logs
docker compose logs -f

# Rebuild after code changes
docker compose build --no-cache && docker compose up -d
```

---

## Tech Stack

- **Backend:** Python / Flask
- **GIF encoding:** [gifski](https://gif.ski/) (compiled from source)
- **Frame extraction:** [ffmpeg](https://ffmpeg.org/) / ffprobe
- **Frontend:** [Tailwind CSS](https://tailwindcss.com/) + [Alpine.js](https://alpinejs.dev/)
- **Container:** Docker (multi-stage build)

---
