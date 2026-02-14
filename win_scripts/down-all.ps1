$ErrorActionPreference = "Continue"

foreach ($t in 1..13) {
  $composePath = "..\team$t\docker-compose.yml"
  if (Test-Path $composePath) {
    Write-Host ("Stopping team{0}..." -f $t)
    docker compose -f $composePath down
  }
}

Write-Host "Stopping core..."
docker compose down
Write-Host "Done."
