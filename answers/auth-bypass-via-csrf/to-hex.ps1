$working_dir = (Get-Location).path;
$bytes = [System.IO.File]::ReadAllBytes("$working_dir/pg_exec.so");
$test = [System.BitConverter]::toString($bytes).replace('-','');
$test;
<#  Not really sure wtf this was
$text = [System.Text.Encoding]::UTF8.GetString($bytes);
$text_array=$text.ToCharArray();
$text_array[1].getType()
$hex_string = '';
Foreach ($char in $text_array) {

$hex_string = $hex_string + [System.String]::Format("{0:X2}");#, [System.Convert]::ToUInt32($char));
}
$hex_string.toLower();
#>