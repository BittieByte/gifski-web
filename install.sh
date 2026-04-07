#!/bin/bash
set -e

log() {
  echo "[*] $1"
}

check_docker() {
  if command -v docker &> /dev/null; then
    log "Docker CLI found"
  else
    curl -fsSL https://get.docker.com | sh
  fi
}

check_docker_compose() {
  if docker compose version &> /dev/null; then
    log "Docker Compose found"
  elif command -v docker-compose &> /dev/null; then
    log "Legacy docker-compose found"
  else
    sudo apt-get update && sudo apt-get install -y docker-compose-plugin
  fi
}

get_install_dir() {
  read -p "Enter installation path (default: ~/gifski-web): " INSTALL_DIR
  INSTALL_DIR=${INSTALL_DIR:-"$HOME/gifski-web"}
  mkdir -p "$INSTALL_DIR/uploads"
  echo "$INSTALL_DIR"
}

build_and_start_container() {
  docker compose build --no-cache
  docker compose up -d
}

main() {
  log "Starting Gifski Web Optimizer Installer..."

  check_docker
  check_docker_compose

  INSTALL_DIR=$(get_install_dir)
  cd "$INSTALL_DIR"

  log "Building Docker container..."
  build_and_start_container

  log "Gifski Web Optimizer is running!"
  echo "Open your browser at: http://localhost:5000"
  echo "Uploaded files are stored in: $INSTALL_DIR/uploads"
  echo "To stop the service: docker compose down"
}

main
