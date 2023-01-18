# Blackbox
- Prototype pollution is usually possible through serialization of a JSON payload, because it is not possible to directly pass javascript object within HTTP requests otherwise.
- It's important to keep in mind that blackbox techniques are abrasive and might lead to denial of service of the target application. Unlike reflected XSS, prototype pollution will continue affecting the target application until it is restarted.
- Not all prototype pollution vulnerabilities come from the ability to inject "__proto__" into a JSON object. Some may split a string with a period character ("file.name"), loop over the properties, and set the value to the contents. In these situations, other payloads like "constructor.prototype" would work instead of "__proto__". These types of vulnerabilities are more difficult to discover using blackbox techniques.  
Overwritting the **toString** function is one of the more reliable tests
# Whitebox
- Apparently using square brackets to access an array protects computed properties from prototype pollution, need to understand why.
- According to offsec prototype pollution is more likely to be found within a library the application uses rather than its source code.
  - of course this does not exclude an application's source code from code review but it is important to keep in mind in terms of low hanging fruit.
## searching for prototype pollution within an applications libraries
We would want to list an applications packages with:
```bash
npm list -prod -depth 1
```
Note that we limit the depth here to first order packages in the dependency tree since the further we get into the dependency tree the less likely it is for us to be able to reach that code from the application, e.g. low hanging fruit.

```bash
npm list -prod -depth 1 | grep "merge\|extend"
```
```powershell
npm list -prod -depth 1 | sls -Pattern "merge|extend"
```

Another and perhaps better way of searching for ***known*** vulnerabilities in an applications packages is by using npm audit.
```bash
npm audit
```
## extramiles
### 1
We can use the **hasOwnProperty** method to trigger another prototype pollution error.  
```json
"__proto__" : {
  "hasOwnProperty":"applesauce"
}
The most important thing I learned hhere was how to generate a list of suitable targets.  
In a browsers developer tools we can:
1. create a new **default** object
```javascript
let s = new Object
```
2. list out all of this objects properties
```
s.getownproperties()
```
3. the properties are
```
constructor
hasOwnProperty
isPrototypeOf
propertyIsEnumerable
toLocaleString
toString   
valueOf
```
### 2
The directory traversal is on the /files route.  
The intended behavior is to only allow downloading of files places within the **shared** directory.  
There is a trivial protection of filtering out **../** sequences to prevent file traversal which we can bypass with **....//**.  
Effectively the inner **../** gets stripped out.  
A request to download a file then looks like:  
```powershell
iwr -Uri http://chips/files/....//app.js -SkipHttpErrorCheck
```
pulling the encryption key:
```powershell
iwr -Uri http://chips/files/....//settings/clientOptions.json -SkipHttpErrorCheck
```
# Prototype Pollution Exploitation
- A useful prototype pollution exploit, ***in terms of RCE***, is application- and library-dependent. Ideally we want to find a point in the application where undefined variables are appended to a child_process.exec, eval, vm.runInNewContext function, or something like a templating engine.
- A useful prototype pollution exploit, ***in terms of the RBAC within WebAPP***, would allow us to overwrite a property such as **isAdmin** and thus grant ourselves admin privileges within the application itself.
# ejs
first this we must do is set ejs to be the template engine e.g.  
```
TEMPLATING_ENGINE=ejs docker-compose up
```
A better way with posh:  
```powershell
Import-Module Posh-SSH;
[string]$userName = 'student'
[string]$userPassword = 'studentlab'
[string]$machine = 'chips'
[securestring]$secStringPassword = ConvertTo-SecureString $userPassword -AsPlainText -Force
[pscredential]$credObject = New-Object System.Management.Automation.PSCredential ($userName, $secStringPassword)

$worker = New-SSHSession -ComputerName $machine -Credential $credObject
$worker
$result = Invoke-SSHCommand -Command 'docker-compose -f /home/student/chips/docker-compose.yml down && export TEMPLATING_ENGINE=ejs && docker-compose -f /home/student/chips/docker-compose.yml up -d' -SSHSession $worker
$result
iwr -Uri http://chips | sls -Pattern '<!-- Using EJS as Templating Engine -->' | % -process {$_.Matches.Value}
```
The main idea here is to dig into the source code of the template engine library and find the logic where the template is rendered. That is the ideal location to find a variable to pollute.

We can use get-ejs-esc-token.ps1 to get an rdp token that will trigger the esc error.  
The application internally uses a guaclite websocket tunnel to reach the **/guaclite** endpoint and it pulls the token from **window.location.search** so in order to reach it with standard http we would have use a headless browser in order to populate **window.location.search** by visiting **http://chips/rdp?token=blah&width=num&height=num** triggering the **rdp()** function in **/frontend/index.js**.  
Otherwise standard powershell requests to the guac endpoint are parsed by the files enpdpoint thus return 404.  
So instead we get an rdp token to trigger the **esc** error and paste that into burp where we have the **/guaclite** request.  
```
. ./get=ejs-esc-token.ps1
```

## ejs rce & extramile
### Exercises

Follow along with this section but connect to the remote debugger and observe the prototype pollution exploit.  
Obtain a shell.

### Extra Mile

Earlier, we used the escape variable to detect if the target is running EJS. We can also use this variable to obtain RCE with some additional payload modifications. Find how to obtain RCE by polluting the escape variable.