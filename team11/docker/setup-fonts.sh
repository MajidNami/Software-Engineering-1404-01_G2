#!/usr/bin/env bash
set -euo pipefail

mkdir -p /app/fonts

if [ -f /app/presentation/fonts/Vazirmatn-Regular.ttf ]; then
  cp /app/presentation/fonts/*.ttf /app/fonts/
fi
