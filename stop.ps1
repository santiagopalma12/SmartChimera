# Script para detener SmartChimera

Write-Host "🛑 Deteniendo SmartChimera..." -ForegroundColor Yellow

docker-compose down

Write-Host ""
Write-Host "✅ Todos los servicios han sido detenidos" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Para borrar también los datos:" -ForegroundColor Cyan
Write-Host "   docker-compose down -v" -ForegroundColor Gray
