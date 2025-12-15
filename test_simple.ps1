# Test con selector simple

Write-Host "=== Probando con selector SIMPLE (h2) ===" -ForegroundColor Yellow

$simpleBody = @{
    name = "Test Simple H2"
    url = "https://correodelsur.com/local"
    container = "uk-container"
    holder = "h2"
    category = "local"
    is_active = $true
} | ConvertTo-Json

try {
    $createResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/sources/" -Method POST -Body $simpleBody -ContentType "application/json"
    
    Write-Host "`nFuente creada - ID: $($createResponse.id)" -ForegroundColor Green
    
    $testResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/sources/$($createResponse.id)/test" -Method POST
    
    Write-Host "`n=== Resultados ===" -ForegroundColor Cyan
    Write-Host "Titulares encontrados: $($testResponse.stats.headlines_found)"
    
    if ($testResponse.sample_headlines -and $testResponse.sample_headlines.Count -gt 0) {
        Write-Host "`nPrimeros 3 titulares:" -ForegroundColor Green
        $testResponse.sample_headlines[0..2] | ForEach-Object { Write-Host "  - $_" }
    } else {
        Write-Host "`nNo se encontraron titulares!" -ForegroundColor Red
    }
    
} catch {
    Write-Host "`nError: $_" -ForegroundColor Red
}
