@echo off
REM ============================================================================
REM Windows Script to Build Docker Base Image
REM ============================================================================
REM For Windows users who prefer batch files over bash
REM ============================================================================

echo ========================================
echo DokGuru Voice - Base Image Builder
echo Docker Hub: choudharikiranv15
echo ========================================
echo.

REM Check if Docker is running
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Login to Docker Hub
echo Please login to Docker Hub...
docker login
if errorlevel 1 (
    echo ERROR: Docker login failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Building base image...
echo This will take 25-30 minutes
echo ========================================
echo.

REM Build the base image
docker build -f Dockerfile.base -t choudharikiranv15/dokguru-base:latest .

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build successful!
echo ========================================
echo.

REM Get image size
for /f "tokens=*" %%i in ('docker images choudharikiranv15/dokguru-base:latest --format "{{.Size}}"') do set IMAGE_SIZE=%%i
echo Image size: %IMAGE_SIZE%
echo.

REM Test the image
echo Testing image...
docker run --rm choudharikiranv15/dokguru-base:latest python -c "import torch; import sentence_transformers; print('OK - All dependencies working!')"

if errorlevel 1 (
    echo WARNING: Image test failed
) else (
    echo [OK] Image test passed
)

echo.
echo ========================================
echo Push to Docker Hub?
echo ========================================
choice /C YN /M "Push image to Docker Hub (Y/N)"

if errorlevel 2 goto :skip_push
if errorlevel 1 goto :do_push

:do_push
echo.
echo Pushing to Docker Hub...
docker push choudharikiranv15/dokguru-base:latest

if errorlevel 1 (
    echo ERROR: Push failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Image pushed to Docker Hub
echo ========================================
echo.
echo Image: choudharikiranv15/dokguru-base:latest
echo View at: https://hub.docker.com/r/choudharikiranv15/dokguru-base
echo.
echo Next steps:
echo   1. Update render.yaml (already done)
echo   2. Push to Git
echo   3. Deploy on Render
echo   4. Enjoy 3-5 minute builds!
echo.
pause
exit /b 0

:skip_push
echo.
echo Skipped pushing to Docker Hub
echo.
echo To push later, run:
echo   docker push choudharikiranv15/dokguru-base:latest
echo.
pause
exit /b 0
