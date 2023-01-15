# Blackbox
- Prototype pollution is usually possible through serialization of a JSON payload, because it is not possible to directly pass javascript object within HTTP requests otherwise.
- It's important to keep in mind that blackbox techniques are abrasive and might lead to denial of service of the target application. Unlike reflected XSS, prototype pollution will continue affecting the target application until it is restarted.
- Not all prototype pollution vulnerabilities come from the ability to inject "__proto__" into a JSON object. Some may split a string with a period character ("file.name"), loop over the properties, and set the value to the contents. In these situations, other payloads like "constructor.prototype" would work instead of "__proto__". These types of vulnerabilities are more difficult to discover using blackbox techniques.
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
### 2
The directory traversal is on the /files route.  
The intended behavior is to only allow downloading of files places within the **shared** directory.  
There is a trivial protection of filtering out **../** sequences to prevent file traversal which we can bypass with **....//**.  
Effectively the inner **../** gets stripped out.  
A request to download a file then looks like:  
```powershell
iwr -Uri http://chips/files/....//app.js -SkipHttpErrorCheck
```