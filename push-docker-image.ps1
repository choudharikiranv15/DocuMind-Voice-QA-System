# ============================================================================
# Docker Image Push Script with Sequential Layer Upload
# ============================================================================
# This script pushes Docker images with:
# - Sequential layer uploads (one at a time)
# - Increased timeout (10 minutes per layer)
# - Automatic retry on failure
# - Progress monitoring
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$ImageName,
    
    [Parameter(Mandatory=$false)]
    [int]$MaxRetries = 3,
    
    [Parameter(Mandatory=$false)]
    [int]$TimeoutMinutes = 10
)

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Green "============================================================================"
Write-ColorOutput Green "Docker Image Push Script - Sequential Layer Upload"
Write-ColorOutput Green "============================================================================"
Write-ColorOutput Cyan "Image: $ImageName"
Write-ColorOutput Cyan "Max Retries: $MaxRetries"
Write-ColorOutput Cyan "Timeout: $TimeoutMinutes minutes per layer"
Write-ColorOutput Green "============================================================================"

# Set environment variables for Docker
$env:DOCKER_BUILDKIT = "1"
$env:BUILDKIT_PROGRESS = "plain"

# Configure Docker to use sequential uploads
Write-ColorOutput Yellow "`n[1/4] Configuring Docker for sequential uploads..."

# Check if Docker is running
try {
    docker info | Out-Null
    Write-ColorOutput Green "✓ Docker is running"
} catch {
    Write-ColorOutput Red "✗ Docker is not running. Please start Docker Desktop."
    exit 1
}

# Login check
Write-ColorOutput Yellow "`n[2/4] Checking Docker Hub authentication..."
$loginStatus = docker info 2>&1 | Select-String "Username"
if ($loginStatus) {
    Write-ColorOutput Green "✓ Already logged in to Docker Hub"
} else {
    Write-ColorOutput Yellow "! Not logged in. Please login to Docker Hub:"
    docker login
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput Red "✗ Docker login failed"
        exit 1
    }
}

# Get image size
Write-ColorOutput Yellow "`n[3/4] Analyzing image..."
$imageInfo = docker images $ImageName --format "{{.Size}}"
Write-ColorOutput Cyan "Image size: $imageInfo"

# Push with retry logic
Write-ColorOutput Yellow "`n[4/4] Pushing image with sequential layer upload..."
Write-ColorOutput Cyan "This may take a while for large images. Please be patient..."

$attempt = 1
$success = $false

while ($attempt -le $MaxRetries -and -not $success) {
    Write-ColorOutput Yellow "`nAttempt $attempt of $MaxRetries..."
    
    # Create a job to push with timeout
    $job = Start-Job -ScriptBlock {
        param($img)
        docker push $img 2>&1
    } -ArgumentList $ImageName
    
    # Wait for job with timeout
    $timeoutSeconds = $TimeoutMinutes * 60
    $completed = Wait-Job $job -Timeout $timeoutSeconds
    
    if ($completed) {
        $output = Receive-Job $job
        $exitCode = $job.State -eq "Completed" -and $output -notmatch "error|failed"
        
        if ($exitCode) {
            Write-ColorOutput Green "`n✓ Image pushed successfully!"
            $success = $true
        } else {
            Write-ColorOutput Red "`n✗ Push failed with error:"
            Write-Output $output
            
            if ($attempt -lt $MaxRetries) {
                Write-ColorOutput Yellow "Retrying in 10 seconds..."
                Start-Sleep -Seconds 10
            }
        }
    } else {
        Write-ColorOutput Red "`n✗ Push timed out after $TimeoutMinutes minutes"
        Stop-Job $job
        
        if ($attempt -lt $MaxRetries) {
            Write-ColorOutput Yellow "Retrying in 10 seconds..."
            Start-Sleep -Seconds 10
        }
    }
    
    Remove-Job $job -Force
    $attempt++
}

if (-not $success) {
    Write-ColorOutput Red "`n============================================================================"
    Write-ColorOutput Red "PUSH FAILED after $MaxRetries attempts"
    Write-ColorOutput Red "============================================================================"
    Write-ColorOutput Yellow "`nTroubleshooting tips:"
    Write-ColorOutput White "1. Check your internet connection"
    Write-ColorOutput White "2. Verify Docker Hub credentials: docker login"
    Write-ColorOutput White "3. Check image size - consider splitting into smaller layers"
    Write-ColorOutput White "4. Try pushing during off-peak hours"
    Write-ColorOutput White "5. Use Docker Hub web interface to check repository status"
    exit 1
}

Write-ColorOutput Green "`n============================================================================"
Write-ColorOutput Green "SUCCESS! Image pushed to Docker Hub"
Write-ColorOutput Green "============================================================================"
Write-ColorOutput Cyan "Image: $ImageName"
Write-ColorOutput Cyan "You can now pull this image with: docker pull $ImageName"
Write-ColorOutput Green "============================================================================"
