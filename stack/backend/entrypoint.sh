#!/bin/bash
set -e

echo "Starting neuralizer backend..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload --ws wsproto --no-access-log
