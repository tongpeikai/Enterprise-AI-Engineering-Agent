$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$composeFile = "$projectRoot/deploy/compose.stage10-lite.yml"
$envFile = "$projectRoot/.env"
if (-not (Test-Path $envFile)) { throw "Create $envFile from .env.example first." }
docker compose --env-file $envFile -f $composeFile up -d --build
docker compose --env-file $envFile -f $composeFile ps
