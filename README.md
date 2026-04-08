# gifski-web

> A self-hosted web UI for [gifski](https://gif.ski/) — convert videos and GIFs into high-quality, optimized GIFs through your browser. No CLI required.

![Docker](https://img.shields.io/badge/docker-compose-0074d9?style=flat-square&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/python-3.12-1D9E75?style=flat-square&logo=python&logoColor=white)
![gifski](https://img.shields.io/badge/gifski-latest-2ea44f?style=flat-square)
![ffmpeg](https://img.shields.io/badge/ffmpeg-bundled-BA7517?style=flat-square&logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-888?style=flat-square)

---

## Screenshots

<div align="center">
  <img src="https://github.com/user-attachments/assets/72d9ed73-078a-4064-8ad0-f2d6daa3c5a7" width="48%" alt="Upload page" />
  &nbsp;
  <img src="https://github.com/user-attachments/assets/f6a46396-66b1-4c96-9c77-8a1a4722179f" width="48%" alt="Result page" />
</div>

<div align="center">
  <sub>Upload page with basic and advanced options &nbsp;·&nbsp; Result page with size stats and GIF preview</sub>
</div>

---

## Features

| Feature | Description |
|---|---|
| **Video → GIF** | Upload any video; ffmpeg extracts frames and gifski encodes a high-quality GIF |
| **GIF re-optimization** | Pass an existing GIF directly through gifski to reduce file size |
| **Full gifski control** | Quality, FPS, dimensions, motion quality, lossy encoding, loop count, palette, and more |
| **Size reduction stats** | See original size, optimized size, and % reduction on the result page |
| **Drag-and-drop upload** | Drop a file onto the upload zone or click to browse |
| **Inline preview** | View the finished GIF in the browser before downloading |
| **Input sanitization** | All form values are validated server-side before being passed to subprocesses |

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

---

## Options

> If neither width nor height is specified, the original media dimensions are used — preventing gifski's default downscaling behavior.

### Basic

| Option | Description | Default |
|---|---|---|
| `quality` | Overall GIF quality (1–100) | `90` |
| `fps` | Output frames per second — lower = smaller file | original |
| `width` | Output width in pixels | original |
| `height` | Output height in pixels | original |
| `fast` | ~2× faster encoding at a slight quality cost | off |
| `extra_quality` | Slower encoding for higher quality output | off |

### Advanced

| Option | Description | Default |
|---|---|---|
| `motion_quality` | How accurately motion between frames is preserved (1–100) | — |
| `lossy_quality` | Allow compression artifacts for smaller output (1–100) | — |
| `repeat` | Loop count: `0` = infinite, `-1` = no loop | — |
| `fixed_color` | Reserve a specific hex color in the palette (`#RRGGBB`) | — |
| `matte` | Background color for transparency compositing (`#RRGGBB`) | — |
| `no_sort` | Keep frames in the exact order provided | off |

---

## Docker Details

The image uses a two-stage build:

**Stage 1 — builder** (`debian:bookworm-slim`)
- Installs the Rust toolchain
- Compiles `gifski` from source with `RUSTFLAGS="-C target-cpu=native"` for optimized output

**Stage 2 — runtime** (`python:3.12-slim`)
- Copies the compiled `gifski` binary from stage 1
- Installs `ffmpeg` and `ffprobe`
- Runs the Flask app on port `5000`

Uploaded files are stored in `./uploads`, bind-mounted from the host so files persist across container restarts.

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

| Layer | Technology |
|---|---|
| Backend | [Python](https://python.org) / [Flask](https://flask.palletsprojects.com/) |
| GIF encoding | [gifski](https://gif.ski/) (compiled from source) |
| Frame extraction | [ffmpeg](https://ffmpeg.org/) / ffprobe |
| Frontend | [Tailwind CSS](https://tailwindcss.com/) + [Alpine.js](https://alpinejs.dev/) |
| Container | Docker (multi-stage build) |

---

<div align="center">
  <sub>Built with gifski + ffmpeg · Powered by Flask · Containerized with Docker</sub>
</div>
