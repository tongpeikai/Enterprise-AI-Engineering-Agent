$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
docker compose --env-file "$projectRoot/.env" -f "$projectRoot/deploy/compose.stage10-lite.yml" down
