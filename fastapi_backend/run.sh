#!/bin/bash
# Quick start script for FastAPI backend

set -e

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."

# Default values
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8001}"
DEBUG="${DEBUG:-false}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dev)
      DEBUG=true
      shift
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --host)
      HOST="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--dev] [--host HOST] [--port PORT]"
      exit 1
      ;;
  esac
done

# Start the server
if [ "$DEBUG" = "true" ]; then
  echo "Starting FastAPI backend in development mode..."
  uvicorn fastapi_backend.main:app --host "$HOST" --port "$PORT" --reload
else
  echo "Starting FastAPI backend in production mode..."
  uvicorn fastapi_backend.main:app --host "$HOST" --port "$PORT"
fi
