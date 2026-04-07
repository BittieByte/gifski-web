#!/bin/bash
set -e

CONTAINER_NAME="gifski-web"

log() {
  echo "[*] $1"
}

check_docker() {
  if command -v docker &> /dev/null; then
    log "Docker CLI found"
  else
    log "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
  fi
}

check_docker_compose() {
  if docker compose version &> /dev/null; then
    log "Docker Compose found"
  elif command -v docker-compose &> /dev/null; then
    log "Legacy docker-compose found"
  else
    log "Installing Docker Compose plugin..."
    sudo apt-get update && sudo apt-get install -y docker-compose-plugin
  fi
}

get_install_dir() {
  read -p "Enter installation path (default: ~/gifski-web): " INSTALL_DIR
  INSTALL_DIR=${INSTALL_DIR:-"$HOME/gifski-web"}
  mkdir -p "$INSTALL_DIR/uploads"
  echo "$INSTALL_DIR"
}

teardown_existing() {
  log "Checking for existing container '$CONTAINER_NAME'..."

  if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log "Found existing container. Stopping..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true

    log "Removing container..."
    docker rm "$CONTAINER_NAME" 2>/dev/null || true

    log "Old container removed."
  else
    log "No existing container found. Proceeding fresh."
  fi
}

build_and_start_container() {
  log "Building image (no cache)..."
  docker compose build --no-cache

  log "Starting new container..."
  docker compose up -d

  # Verify it came up
  if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log "Container '$CONTAINER_NAME' is up and running."
  else
    echo "[!] Container did not start as expected. Check 'docker compose logs'."
    exit 1
  fi
}

main() {
  log "Starting Gifski Web Optimizer Installer..."
  check_docker
  check_docker_compose

  INSTALL_DIR=$(get_install_dir)
  cd "$INSTALL_DIR"

  teardown_existing
  build_and_start_container

  log "Gifski Web Optimizer is running!"
  echo ""
  echo "  URL:     http://localhost:5000"
  echo "  Uploads: $INSTALL_DIR/uploads"
  echo "  Stop:    docker compose down"
  echo "  Logs:    docker compose logs -f"
}

main
