# SmartChimera - Script de Inicio para Windows
# Este script levanta toda la infraestructura con Docker

Write-Host "🚀 SmartChimera - Starting deployment..." -ForegroundColor Cyan
Write-Host ""

# Verificar que Docker está corriendo
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "❌ Docker no está corriendo. Por favor inicia Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker está corriendo" -ForegroundColor Green

# Limpiar contenedores anteriores si existen
Write-Host "🧹 Limpiando contenedores anteriores..." -ForegroundColor Yellow
docker-compose down -v 2>$null

# Construir imágenes
Write-Host ""
Write-Host "🏗️  Construyendo imágenes Docker..." -ForegroundColor Cyan
docker-compose build

# Levantar servicios
Write-Host ""
Write-Host "🚀 Levantando servicios..." -ForegroundColor Cyan
docker-compose up -d

# Esperar a que los servicios estén listos
Write-Host ""
Write-Host "⏳ Esperando a que los servicios inicien..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verificar estado de servicios
Write-Host ""
Write-Host "📊 Estado de servicios:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "✅ SmartChimera está corriendo!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Accesos:" -ForegroundColor Cyan
Write-Host "   • Neo4j Browser:  http://localhost:7474" -ForegroundColor White
Write-Host "     Usuario: neo4j" -ForegroundColor Gray
Write-Host "     Password: (see .env file or NEO4J_PASSWORD env var)" -ForegroundColor Gray
Write-Host ""
Write-Host "   • Backend API:    http://localhost:8000" -ForegroundColor White
Write-Host "   • API Docs:       http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "   • Frontend:       http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Comandos utiles:" -ForegroundColor Cyan
Write-Host "   Ver logs:         docker-compose logs -f" -ForegroundColor Gray
Write-Host "   Ver logs backend: docker-compose logs -f backend" -ForegroundColor Gray
Write-Host "   Detener todo:     docker-compose down" -ForegroundColor Gray
Write-Host "   Reiniciar:        docker-compose restart" -ForegroundColor Gray
Write-Host ""
Write-Host "Presiona Ctrl+C para salir o cierra esta ventana" -ForegroundColor Yellow
Write-Host ""

# Mostrar logs en tiempo real
docker-compose logs -f
