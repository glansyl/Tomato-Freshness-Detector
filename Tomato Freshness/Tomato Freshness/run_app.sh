#!/bin/bash
# Script to run the tomato freshness app with proper video permissions

cd "$(dirname "$0")"
source .venv/bin/activate
exec sg video -c "python3 app.py"
