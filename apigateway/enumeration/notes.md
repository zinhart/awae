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