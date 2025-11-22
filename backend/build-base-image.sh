#!/bin/bash
# ============================================================================
# Build and Push Base Docker Image (ONE-TIME SETUP)
# ============================================================================
# This script builds the base image with heavy ML/AI dependencies
# Run this ONCE, then reuse the base image for fast deployments
#
# Usage:
#   1. Set your Docker Hub username below
#   2. Run: bash build-base-image.sh
#   3. Wait ~25-30 minutes (one-time only!)
# ============================================================================

set -e  # Exit on error

# ============================================================================
# CONFIGURATION
# ============================================================================
# Docker Hub username
DOCKER_USERNAME="choudharikiranv15"

# Image name and tag
IMAGE_NAME="dokguru-base"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

# ============================================================================
# COLOR OUTPUT
# ============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# ============================================================================
# VALIDATE CONFIGURATION
# ============================================================================
print_header "DokGuru Voice - Base Image Builder"

# Username validation removed - already configured with choudharikiranv15

# ============================================================================
# CHECK PREREQUISITES
# ============================================================================
print_header "Checking Prerequisites"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi
print_success "Docker is installed"

# Check if user is logged into Docker Hub
if ! docker info | grep -q "Username"; then
    print_warning "Not logged into Docker Hub"
    echo ""
    echo "Please login to Docker Hub:"
    echo "  docker login"
    echo ""
    read -p "Press Enter after logging in..."
fi

# Verify Dockerfile.base exists
if [ ! -f "Dockerfile.base" ]; then
    print_error "Dockerfile.base not found!"
    echo "Make sure you're running this script from the backend directory"
    exit 1
fi
print_success "Dockerfile.base found"

# ============================================================================
# BUILD BASE IMAGE
# ============================================================================
print_header "Building Base Image"

echo ""
echo "Image: ${FULL_IMAGE_NAME}"
echo "This will take approximately 25-30 minutes..."
echo ""

# Start timer
START_TIME=$(date +%s)

# Build the image
print_warning "Building... This is a one-time operation."
docker build \
    -f Dockerfile.base \
    -t "${FULL_IMAGE_NAME}" \
    --progress=plain \
    .

# Calculate build time
END_TIME=$(date +%s)
BUILD_TIME=$((END_TIME - START_TIME))
BUILD_TIME_MIN=$((BUILD_TIME / 60))
BUILD_TIME_SEC=$((BUILD_TIME % 60))

print_success "Base image built in ${BUILD_TIME_MIN}m ${BUILD_TIME_SEC}s"

# ============================================================================
# VERIFY IMAGE
# ============================================================================
print_header "Verifying Image"

# Check image size
IMAGE_SIZE=$(docker images "${FULL_IMAGE_NAME}" --format "{{.Size}}")
print_success "Image size: ${IMAGE_SIZE}"

# Test the image
echo "Testing image..."
docker run --rm "${FULL_IMAGE_NAME}" python -c "
import torch
import sentence_transformers
import chromadb
from gtts import gTTS
print('✓ All core dependencies working!')
print(f'PyTorch: {torch.__version__}')
print(f'Sentence Transformers: {sentence_transformers.__version__}')
"

print_success "Image verification passed"

# ============================================================================
# PUSH TO DOCKER HUB
# ============================================================================
print_header "Pushing to Docker Hub"

echo ""
read -p "Push image to Docker Hub? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Pushing to Docker Hub..."
    docker push "${FULL_IMAGE_NAME}"
    print_success "Image pushed successfully!"

    echo ""
    print_success "Base image is now available at: ${FULL_IMAGE_NAME}"
    echo ""
    echo "Next steps:"
    echo "  1. Update Dockerfile to use: FROM ${FULL_IMAGE_NAME}"
    echo "  2. Update render.yaml to use Docker deployment"
    echo "  3. Deploy to Render - builds will now take only 3-5 minutes!"
else
    print_warning "Skipped pushing to Docker Hub"
    echo ""
    echo "To push manually later, run:"
    echo "  docker push ${FULL_IMAGE_NAME}"
fi

# ============================================================================
# SUMMARY
# ============================================================================
print_header "Build Complete!"

echo ""
echo "Base Image: ${FULL_IMAGE_NAME}"
echo "Image Size: ${IMAGE_SIZE}"
echo "Build Time: ${BUILD_TIME_MIN}m ${BUILD_TIME_SEC}s"
echo ""
echo "This image includes:"
echo "  ✓ PyTorch (CPU)"
echo "  ✓ Sentence Transformers"
echo "  ✓ ChromaDB"
echo "  ✓ gTTS (Google TTS)"
echo "  ✓ Azure TTS"
echo "  ✓ Coqui TTS"
echo "  ✓ PDF processing libraries"
echo "  ✓ All LLM API clients"
echo ""
print_success "You only need to build this once!"
echo "Future deployments will reuse this image and complete in 3-5 minutes."
echo ""
