foreach($i in 1..100) {
    Write-Progress -Id 1 -Activity "Outer Search in Progress" -Status "$i% Complete:" -PercentComplete $i;
    foreach($j in 1..10) {
        Write-Progress -ParentId 1 -Activity "Inner Search in Progress" -Status "$j% Complete:" -PercentComplete $j; Start-Sleep -Milliseconds 250
    }
}
