# Script para ver logs de SmartChimera

param(
    [string]$Service = "all"
)

Write-Host "📋 SmartChimera Logs Viewer" -ForegroundColor Cyan
Write-Host ""

switch ($Service) {
    "backend" {
        Write-Host "📊 Logs del Backend API..." -ForegroundColor Green
        docker-compose logs -f backend
    }
    "frontend" {
        Write-Host "📊 Logs del Frontend..." -ForegroundColor Green
        docker-compose logs -f frontend
    }
    "neo4j" {
        Write-Host "📊 Logs de Neo4j..." -ForegroundColor Green
        docker-compose logs -f neo4j
    }
    default {
        Write-Host "📊 Logs de todos los servicios..." -ForegroundColor Green
        Write-Host "Presiona Ctrl+C para salir" -ForegroundColor Yellow
        Write-Host ""
        docker-compose logs -f
    }
}
