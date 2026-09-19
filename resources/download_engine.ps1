[string]$base_url = $args[0]
[string]$engine_zip = $args[1]
[string]$engine_dir = $args[2]
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri "$base_url/$engine_zip" -OutFile "$Env:TMP\$engine_zip"
Expand-Archive -Path "$Env:TMP\$engine_zip" -DestinationPath $engine_dir
Remove-Item "$Env:TMP\$engine_zip"
