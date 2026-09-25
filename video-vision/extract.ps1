[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$Video,

    # Nombre de frames reparties uniformement sur toute la duree (defaut: 24)
    [int]$Frames = 24,

    # Mode dense : ignore -Frames et extrait 1 image par seconde
    [switch]$Dense,

    # Ne pas extraire l'audio
    [switch]$NoAudio
)

$ErrorActionPreference = "Stop"

# Resoudre le chemin : chemin direct, ou nom de fichier dans .\input\
$videoPath = $Video
if (-not (Test-Path $videoPath)) {
    $candidate = Join-Path $PSScriptRoot "input\$Video"
    if (Test-Path $candidate) { $videoPath = $candidate }
}
if (-not (Test-Path $videoPath)) {
    Write-Error "Video introuvable : $Video (cherche aussi dans .\input\)"
    exit 1
}
$videoPath = (Resolve-Path $videoPath).Path

$baseName = [System.IO.Path]::GetFileNameWithoutExtension($videoPath)
$outDir = Join-Path $PSScriptRoot "output\$baseName"
$framesDir = Join-Path $outDir "frames"
New-Item -ItemType Directory -Force -Path $framesDir | Out-Null

# Nettoyer d'anciennes frames si on relance sur la meme video
Get-ChildItem $framesDir -Filter "frame_*.jpg" -ErrorAction SilentlyContinue | Remove-Item -Force

if ($Dense) {
    Write-Host "Mode dense : 1 frame par seconde"
    $fps = 1
} else {
    $durationRaw = & ffprobe -v error -show_entries format=duration -of csv=p=0 "$videoPath"
    $duration = [double]$durationRaw
    if ($duration -le 0) {
        Write-Error "Impossible de lire la duree de la video."
        exit 1
    }
    $fps = $Frames / $duration
    Write-Host ("Duree: {0:N1}s -> extraction de ~{1} frames (fps={2:N4})" -f $duration, $Frames, $fps)
}

& ffmpeg -y -v error -i "$videoPath" -vf "fps=$fps" -q:v 2 (Join-Path $framesDir "frame_%03d.jpg")

$frameCount = (Get-ChildItem $framesDir -Filter "frame_*.jpg").Count
Write-Host "$frameCount frames extraites -> $framesDir"

if (-not $NoAudio) {
    $audioPath = Join-Path $outDir "audio.mp3"
    & ffmpeg -y -v error -i "$videoPath" -vn -acodec libmp3lame -q:a 2 "$audioPath" 2>$null
    if (Test-Path $audioPath) {
        Write-Host "Audio extrait -> $audioPath"
    } else {
        Write-Host "Pas de piste audio detectee (ou extraction echouee)."
    }
}

Write-Host ""
Write-Host "Termine. Dossier : $outDir"
