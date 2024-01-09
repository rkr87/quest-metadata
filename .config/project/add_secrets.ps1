# call this script from venv/scripts/activate.ps1 to load all secrets as env variables
# Invoke-Expression "& $VenvDir\..\.config\project\add_secrets.ps1"

## .secrets
# GOOGLE_PROJECT_ID=""
# GOOGLE_PRIVATE_KEY_ID=""
# GOOGLE_PRIVATE_KEY=""
# GOOGLE_CLIENT_EMAIL=""
# GOOGLE_CLIENT_ID=""
# GOOGLE_CERT_URL=""

Set-Variable EnvFileRelLoc -Option Constant -Value ".config\project\.secrets";

Get-Content $EnvFileRelLoc | foreach {
    $name, $value = [regex]::split($_, '(?<=[A-Z_]+)=(?= |\W+)') ;
    if (
        ![string]::IsNullOrWhiteSpace($name) -AND 
        !$name.Contains('#') -AND 
        !$name.Contains('=')
    ) 
    {
        $value = $value.Replace("\n","`r`n").Replace("`"","")
        Set-Content env:$name $value
    }
}