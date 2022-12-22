<#
.Description
This is a commandlet used to enumerate microservices via http verb tampering
.PARAMETER ActionList
The string that you want to hash.
.PARAMETER Target
The hashing algorithm.
.PARAMETER Wordlist
.EXAMPLE
PS> Get-HashString.ps1 fIxfs2guY2dnK2nLsnbdk5lbUubWwvnidonkey123 sha1
.EXAMPLE
PS> Get-HashString.ps1 -InputString fIxfs2guY2dnK2nLsnbdk5lbUubWwvnidonkey123 -HashType sha1.
.SYNOPSIS
Providing a more unified experience to computing string hashes when using pwsh on Linux.
#>
function Invoke-RouteBuster() {
  param(
  [Parameter(Mandatory=$true, HelpMessage='Specify string to be hashed. Accepts from pipeline.')]
  [string]$ActionList,
  [Parameter(Mandatory=$true, HelpMessage='')]
  [string]$Target,
  [Parameter(Mandatory=$true, HelpMessage='')]
  [string]$Wordlist
  )
  $actions_list = Get-Content $ActionList
  $word_list = Get-Content $Wordlist
  foreach($word in $word_list) {
    foreach($action in $actions_list) {
      $url = "$target/$word/$action"
      write-output $url
      $res_get = $null
      $res_post = $null
      $res_put = $null
      $res_patch = $null
    }
  }
  
}
