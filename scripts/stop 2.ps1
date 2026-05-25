$listener = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($null -ne $listener) {
    $pid = $listener.OwningProcess
    Stop-Process -Id $pid -Force
    Write-Host "Stopped process $pid listening on port 8000."
} else {
    Write-Host "No process listening on port 8000."
}
