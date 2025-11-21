#!/bin/bash

# Vercel Ignore Build Script
# This script checks if only frontend files have changed
# If no frontend changes, skip the build (exit 0)
# If frontend changes detected, proceed with build (exit 1)

echo "Checking for frontend changes..."

# Check if frontend directory has changes
if git diff HEAD^ HEAD --quiet -- frontend/; then
  echo "✓ No frontend changes detected - skipping Vercel build"
  exit 0
else
  echo "✓ Frontend changes detected - proceeding with Vercel build"
  exit 1
fi
