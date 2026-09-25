[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$AudioPath,

    # Cle API OpenAI. Par defaut, lit $env:OPENAI_API_KEY
    [string]$ApiKey = $env:OPENAI_API_KEY,

    [string]$OutFile
)

$ErrorActionPreference = "Stop"

if (-not $ApiKey) {
    Write-Error "Aucune cle API. Passe -ApiKey <ta_cle> ou definis `$env:OPENAI_API_KEY avant d'appeler ce script."
    exit 1
}
if (-not (Test-Path $AudioPath)) {
    Write-Error "Fichier audio introuvable : $AudioPath"
    exit 1
}
$AudioPath = (Resolve-Path $AudioPath).Path

if (-not $OutFile) {
    $OutFile = Join-Path (Split-Path $AudioPath -Parent) "transcript.txt"
}

Write-Host "Transcription en cours via l'API OpenAI Whisper..."

$result = & curl.exe -s "https://api.openai.com/v1/audio/transcriptions" `
    -H "Authorization: Bearer $ApiKey" `
    -F "file=@$AudioPath" `
    -F "model=whisper-1"

try {
    $obj = $result | ConvertFrom-Json
} catch {
    Write-Error "Reponse inattendue de l'API : $result"
    exit 1
}

if ($obj.error) {
    Write-Error "Erreur API : $($obj.error.message)"
    exit 1
}

$obj.text | Out-File -FilePath $OutFile -Encoding utf8
Write-Host "Transcription enregistree -> $OutFile"
