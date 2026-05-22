#!/bin/bash
set -e
cd "$(dirname "$0")"

PYTHON=/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
export DYLD_LIBRARY_PATH=/opt/homebrew/lib

echo ""
echo "  NEXUS × UNC  —  Partnership Report Engine"
echo "  ─────────────────────────────────────────"

# Start Ollama if not running
if ! curl -s --max-time 2 http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo "  Starting Ollama…"
  ollama serve > /tmp/ollama_nexus.log 2>&1 &
  sleep 3
fi

# Check for a usable model
MODEL=$("$PYTHON" -c "
from backend.pipeline.generator import get_available_model
m = get_available_model()
print(m if m else '')
" 2>/dev/null)

if [ -z "$MODEL" ]; then
  echo ""
  echo "  ⚠  No local model found."
  echo "  → Run this once to download one (≈5 GB, then free forever):"
  echo "     ollama pull llama3.1:8b"
  echo ""
else
  echo "  ✓  Model ready: $MODEL"
fi

echo "  → http://localhost:5050"
echo ""

exec "$PYTHON" app.py
