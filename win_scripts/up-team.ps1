param(
  [Parameter(Mandatory=$true)]
  [int]$Team
)

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

if (-not $TeamPort.ContainsKey($Team)) {
  throw "Invalid team number: $Team"
}
docker compose up -d --build

$composePath = "..\team$Team\docker-compose.yml"
if (-not (Test-Path $composePath)) {
  throw "Missing $composePath"
}

$env:TEAM_PORT = "$($TeamPort[$Team])"
Write-Host ("Starting team{0} on port {1} ..." -f $Team, $env:TEAM_PORT)
docker compose -f $composePath up -d --build
Write-Host ("Team{0}: http://localhost:{1}/" -f $Team, $TeamPort[$Team])
