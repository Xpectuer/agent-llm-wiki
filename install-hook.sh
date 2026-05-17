#!/usr/bin/env bash
set -euo pipefail

echo "Installing pre-commit hooks..."

if ! command -v pre-commit &> /dev/null; then
    echo "pre-commit not found. Installing..."
    pip install pre-commit
fi

pre-commit install
pre-commit install --hook-type commit-msg 2>/dev/null || true

echo "Pre-commit hooks installed successfully."
echo "Run 'pre-commit run --all-files' to check all files now."
