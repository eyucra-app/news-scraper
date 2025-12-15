# Test Playwright with Correo del Sur

Write-Host "=== Testing Playwright Implementation ===" -ForegroundColor Cyan

$body = @{
    name        = "Correo del Sur - Local (Playwright)"
    url         = "https://correodelsur.com/local"
    container   = ".uk-container"
    holder      = 'a[href*="/local/202"] h2, a[href*="/local/202"] h5'
    requires_js = $true
    category    = "local"
    is_active   = $true
} | ConvertTo-Json

try {
    Write-Host "`nCreating source with Playwright enabled..." -ForegroundColor Yellow
    $createResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/sources/" -Method POST -Body $body -ContentType "application/json"
    
    Write-Host "Source created! ID: $($createResponse.id)" -ForegroundColor Green
    Write-Host "requires_js: $($createResponse.requires_js)" -ForegroundColor Cyan
    
    $sourceId = $createResponse.id
    
    Write-Host "`nTesting scrape with Playwright..." -ForegroundColor Yellow
    Write-Host "(This may take 3-5 seconds due to browser startup)" -ForegroundColor Gray
    
    $testResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/sources/$sourceId/test" -Method POST
    
    Write-Host "`n=== RESULTS ===" -ForegroundColor Green
    Write-Host "Status: $($testResponse.status)"
    Write-Host "Headlines found: $($testResponse.stats.headlines_found)" -ForegroundColor $(if ($testResponse.stats.headlines_found -gt 0) { 'Green' }else { 'Red' })
    Write-Host "New headlines: $($testResponse.stats.headlines_new)"
    
    if ($testResponse.error_message) {
        Write-Host "`nError: $($testResponse.error_message)" -ForegroundColor Red
    }
    
    if ($testResponse.sample_headlines -and $testResponse.sample_headlines.Count -gt 0) {
        Write-Host "`n=== Sample Headlines (First 5) ===" -ForegroundColor Cyan
        $count = [Math]::Min(4, $testResponse.sample_headlines.Count - 1)
        for ($i = 0; $i -le $count; $i++) {
            Write-Host "  ✓ $($testResponse.sample_headlines[$i])" -ForegroundColor White
        }
        Write-Host "`n✅ SUCCESS! Playwright is working!" -ForegroundColor Green
    }
    else {
        Write-Host "`n❌ No headlines found - check logs" -ForegroundColor Red
    }
    
}
catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Yellow
    }
}
