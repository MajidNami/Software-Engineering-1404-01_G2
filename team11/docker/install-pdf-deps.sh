#!/usr/bin/env bash
set -euo pipefail

# Install WeasyPrint system dependencies for PDF rendering
apt-get update && apt-get install -y \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libcairo2 \
  libgdk-pixbuf-2.0-0 \
  shared-mime-info

rm -rf /var/lib/apt/lists/*
