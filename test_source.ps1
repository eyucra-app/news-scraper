# Test script para crear y probar fuente de Correo del Sur

Write-Host "=== Creando fuente... ===" -ForegroundColor Yellow

$body = @{
    name = "Correo del Sur - Local"
    url = "https://correodelsur.com/local"
    container = ".uk-container"
    holder = 'a[href*="/local/202"]'
    category = "local"
    is_active = $true
} | ConvertTo-Json

try {
    $createResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/sources/" -Method POST -Body $body -ContentType "application/json"
    
    Write-Host "`n=== Fuente creada exitosamente! ===" -ForegroundColor Green
    Write-Host "ID: $($createResponse.id)"
    Write-Host "Nombre: $($createResponse.name)"
    
    $sourceId = $createResponse.id
    
    Write-Host "`n=== Probando extracción de titulares... ===" -ForegroundColor Yellow
    
    $testResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/sources/$sourceId/test" -Method POST
    
    Write-Host "`n=== Resultados del Test ===" -ForegroundColor Cyan
    Write-Host "Status: $($testResponse.status)"
    Write-Host "Titulares encontrados: $($testResponse.stats.headlines_found)"
    Write-Host "Titulares nuevos: $($testResponse.stats.headlines_new)"
    
    if ($testResponse.error_message) {
        Write-Host "`nError: $($testResponse.error_message)" -ForegroundColor Red
    }
    
    if ($testResponse.sample_headlines -and $testResponse.sample_headlines.Count -gt 0) {
        Write-Host "`n=== Titulares de ejemplo ===" -ForegroundColor Green
        $testResponse.sample_headlines | ForEach-Object { Write-Host "  - $_" }
    }
    
} catch {
    Write-Host "`nError: $_" -ForegroundColor Red
    Write-Host "StatusCode: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
}
