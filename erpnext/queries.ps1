Import-Module Posh-SSH;
[string]$userName = 'frappe'
[string]$userPassword = 'frappe'
[securestring]$secStringPassword = ConvertTo-SecureString $userPassword -AsPlainText -Force
[pscredential]$credObject = New-Object System.Management.Automation.PSCredential ($userName, $secStringPassword)
$worker = New-SSHSession -ComputerName erpnext -Credential $credObject

$result = Invoke-SSHCommand -Command "grep -rwn '@frappe.whitelist(allow_guest=True)' /home/frappe/frappe-bench/apps/frappe/frappe  --color" -SSHSession $worker
Remove-Item -Path './frappe-public-endpoints.txt' -ErrorAction SilentlyContinue
Remove-Item -Path './frappe-public-endpoints-with-sql-statements.txt' -ErrorAction SilentlyContinue
foreach($i in $result.Output ) {
  $file_path = $i.split(":")[0]
  $line_number = $i.split(":")[1]
  #echo "$file_path | $line_number "
  echo "Filepath: $file_path, $line_number" >> frappe-public-endpoints.txt 
  $sql_statements_results = Invoke-SSHCommand -Command "grep -rwn 'sql\|select.*\|query' $file_path" $worker
  <#
  if(!([string]::IsNullOrEmpty($sql_statements_results.Output))) {
    echo "File: $file_path" >> 'frappe-public-endpoints-with-sql-statements.txt'
    echo "Line number: $($sql_statements_results.Output.split(":")[0])" >> 'frappe-public-endpoints-with-sql-statements.txt'
    echo "Code Block: $($sql_statements_results.Output.split(":")[1])" >> 'frappe-public-endpoints-with-sql-statements.txt'
  }
  #>
}
