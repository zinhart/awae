We can use: 
```bash
curl  -H 'Authorization: O+JMYwBsU797EKtlRQYu+Q'  http://concord:8001/api/v1/process -F concord.yml=@concord.yml -F org=OffSec -F project=AWAE
```
Really important. In order to use set the **content type** to ***application/octet-stream*** on form uploads use:
```powershell
get-item
``` 
instead of:
```powershell
get-content -raw 
```
Basicallly **application/octet-stream** on **content-type** indicates binary content. If a there is no **System.IO.FileInfo** object (which is return by **get-item**) **invoke-webrequest** assumes the content is **text/plain**.
```powershell
iwr -Uri 'http://concord:8001/api/v1/process' -Method Post -Headers @{ Authorization = "O+JMYwBsU797EKtlRQYu+Q"} -Form @{org = 'OffSec'; project = 'AWAE'; 'concord.yml'= get-item ./concord.yml}
```

To decrypt the value. For this to work however we must enable enable payload archives in the project settings.
The resulting value is apparently in croation. In english it means "I jam all the time, but I don't have any jam"