#!/bin/bash
# Start script for Render
export PYTHONPATH="${PYTHONPATH}:/opt/render/project/src"
cd backend
uvicorn app.main:app --host 0.0.0.0 --port $PORT

