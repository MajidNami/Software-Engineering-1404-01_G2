# Deploy Frontend Script for Team4
# This script builds the frontend and deploys it to Django static/templates

Write-Host '🚀 Starting Team4 Frontend Deployment...' -ForegroundColor Cyan

# Change to frontend directory
Set-Location '$PSScriptRoot\front'

# Build the frontend
Write-Host '`n📦 Building frontend...' -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host '❌ Build failed!' -ForegroundColor Red
    exit 1
}

Write-Host '✅ Build completed successfully!' -ForegroundColor Green

# The build output is already in static/team4/ (configured in vite.config.ts)
# We just need to copy index.html to templates

# Copy index.html to templates
Write-Host '`n📄 Copying index.html to templates...' -ForegroundColor Yellow
if (Test-Path "$PSScriptRoot\static\team4\index.html") {
    # Ensure templates directory exists
    if (-not (Test-Path "$PSScriptRoot\templates\team4")) {
        New-Item -ItemType Directory -Path "$PSScriptRoot\templates\team4" -Force | Out-Null
    }
    
    # Copy index.html directly (paths are already correct from Vite build)
    Copy-Item "$PSScriptRoot\static\team4\index.html" -Destination "$PSScriptRoot\templates\team4\index.html" -Force
    Write-Host '✅ index.html copied to templates/team4/' -ForegroundColor Green
} else {
    Write-Host '❌ index.html not found in static/team4!' -ForegroundColor Red
    exit 1
}

Write-Host '`n✨ Deployment completed successfully!'
Write-Host '   Static files: static/team4/assets/' 
Write-Host '   Template: templates/team4/index.html' 
Write-Host '   You can now run Django server to see changes at http://localhost:8000/team4/'
