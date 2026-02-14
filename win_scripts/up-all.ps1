$ErrorActionPreference = "Stop"

$TeamPort = @{
  1  = 9101
  2  = 9106
  3  = 9111
  4  = 9116
  5  = 9121
  6  = 9126
  7  = 9131
  8  = 9136
  9  = 9141
  10 = 9146
  11 = 9151
  12 = 9156
  13 = 9161
}

Write-Host "Starting core..."
docker network inspect app404_net *> $null; if ($LASTEXITCODE -ne 0) { docker network create app404_net | Out-Null }
docker compose up -d --build

foreach ($t in 1..13) {
  $composePath = "..\team$t\docker-compose.yml"
  if (Test-Path $composePath) {
    $env:TEAM_PORT = "$($TeamPort[$t])"
    Write-Host ("Starting team{0} on port {1} ..." -f $t, $env:TEAM_PORT)
    docker compose -f $composePath up -d --build
  } else {
    Write-Host ("Skipping team{0} (no docker-compose.yml)" -f $t)
  }
}

Write-Host "Done."
Write-Host "Core: http://localhost:8000/"
foreach ($t in 1..13) {
  if ($TeamPort.ContainsKey($t)) {
    Write-Host ("Team{0}: http://localhost:{1}/" -f $t, $TeamPort[$t])
  }
}
