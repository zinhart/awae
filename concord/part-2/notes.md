We can use: 
```bash
curl  -H 'Authorization: O+JMYwBsU797EKtlRQYu+Q'  http://concord:8001/api/v1/process -F concord.yml=@concord.yml -F org=OffSec -F project=AWAE
```
This is a work in progress. For some reason get-content is mangling concord.yml
```powershell
iwr -Uri 'http://concord:8001/api/v1/process' -Method Post -Headers @{ Authorization = "O+JMYwBsU797EKtlRQYu+Q"} -Form @{org = 'OffSec'; project = 'AWAE'; 'concord.yml'= get-content ./concord.yml}
```

To decrypt the value. For this to work however we must enable enable payload archives in the project settings.
The resulting value is apparently in croation. In english it means "I jam all the time, but I don't have any jam"