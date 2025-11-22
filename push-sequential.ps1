Write-Host "Pushing Docker image with sequential layer upload..." -ForegroundColor Green
Write-Host "Image: choudharikiranv15/dokguru-base:latest" -ForegroundColor Cyan
Write-Host "This will push one layer at a time with 10-minute timeout per layer" -ForegroundColor Yellow
Write-Host ""

# Set environment variable to limit concurrent uploads
$env:DOCKER_BUILDKIT = "0"

# Push with timeout
$timeout = 600  # 10 minutes in seconds
$process = Start-Process -FilePath "docker" -ArgumentList "push", "choudharikiranv15/dokguru-base:latest" -NoNewWindow -PassThru -RedirectStandardOutput "push-output.log" -RedirectStandardError "push-error.log"

Write-Host "Push started. Waiting up to 10 minutes..." -ForegroundColor Yellow

if ($process.WaitForExit($timeout * 1000)) {
    $exitCode = $process.ExitCode
    if ($exitCode -eq 0) {
        Write-Host "✓ Push completed successfully!" -ForegroundColor Green
        Get-Content "push-output.log"
    } else {
        Write-Host "✗ Push failed with exit code: $exitCode" -ForegroundColor Red
        Get-Content "push-error.log"
    }
} else {
    Write-Host "✗ Push timed out after 10 minutes" -ForegroundColor Red
    $process.Kill()
}

Remove-Item "push-output.log" -ErrorAction SilentlyContinue
Remove-Item "push-error.log" -ErrorAction SilentlyContinue
