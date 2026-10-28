# 即墨区利晨针织厂官网 — 本地预览 / local preview
# 用法 / usage:  右键“使用 PowerShell 运行”，或在终端执行:
#                powershell -ExecutionPolicy Bypass -File .\preview-local.ps1
param(
    [int]$Port = 8000,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

function Find-Python {
    foreach ($candidate in @("py", "python", "python3")) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    return $null
}

$python = Find-Python
if (-not $python) {
    Write-Host ""
    Write-Host "[!] 未找到 Python。可以直接双击 index.html 预览，" -ForegroundColor Yellow
    Write-Host "    但部分浏览器在 file:// 下会限制语言切换。安装 Python 后可自动启动本地服务器:" -ForegroundColor Yellow
    Write-Host "    https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

$url = "http://127.0.0.1:$Port/index.html"
Write-Host ""
Write-Host "  即墨区利晨针织厂官网 本地预览" -ForegroundColor Cyan
Write-Host "  ----------------------------"
Write-Host "  中文: $url"
Write-Host "  英文: $url`?lang=en"
Write-Host ""
Write-Host "  按 Ctrl+C 停止服务器。"
Write-Host ""

if (-not $NoBrowser) { Start-Process $url }

try {
    & $python -m http.server $Port --bind 127.0.0.1
} finally {
    Write-Host "服务器已停止。" -ForegroundColor DarkGray
}