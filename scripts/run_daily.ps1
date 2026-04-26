# run_daily.ps1
# デイリーリサーチフローをSTEPごとに分割実行するオーケストレーター
# 使い方:
#   .\scripts\run_daily.ps1                    # 本日日付で実行
#   .\scripts\run_daily.ps1 -Date 2026-04-24   # 日付指定
#   .\scripts\run_daily.ps1 -Step 3            # 指定STEPから再開

param(
    [string]$Date = (Get-Date -Format "yyyy-MM-dd"),
    [int]$Step = 0  # 0 = 自動検出（未完了の最初のSTEPから開始）
)

$MaxRetry = 3

# -------------------------------------------------------
# ユーティリティ
# -------------------------------------------------------

function Write-Step {
    param($msg)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " $msg" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Skip    { param($msg) Write-Host "[スキップ] $msg" -ForegroundColor Yellow }
function Write-Fail    { param($msg) Write-Host "[失敗] $msg" -ForegroundColor Red }

function Test-StepDone {
    param([int]$s)
    switch ($s) {
        1 { return Test-Path "reports/${Date}_macro.md" }
        2 { return Test-Path "reports/${Date}_screening.md" }
        3 { return Test-Path "reports/${Date}_evaluation.md" }
        4 { return ($null -ne (Get-ChildItem "reports/${Date}_deepdive_*.md" -ErrorAction SilentlyContinue)) }
        5 { return (Test-Path "reports/${Date}_article_macro.md") -and (Test-Path "reports/${Date}_article_screening.md") }
        default { return $false }
    }
}

function Invoke-ClaudeStep {
    param([int]$s, [string]$prompt)

    for ($i = 1; $i -le $MaxRetry; $i++) {
        Write-Host "  実行中 (試行 $i/$MaxRetry)..." -ForegroundColor DarkGray
        claude -p $prompt
        if (Test-StepDone $s) {
            return $true
        }
        Write-Host "  出力ファイルが見つかりません。リトライします..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    }
    return $false
}

function Invoke-GitPush {
    param([int]$s)
    Write-Host "  git push 実行中 (STEP ${s})..." -ForegroundColor DarkGray
    git add reports/ targets/
    $status = git status --porcelain
    if (-not $status) {
        Write-Host "  コミット対象なし。スキップ。" -ForegroundColor DarkGray
        return
    }
    git commit -m "Add daily research STEP${s}: ${Date}"
    git push origin main
    if ($?) { Write-Success "git push 完了 (STEP ${s})" } else { Write-Fail "git push 失敗 (STEP ${s})" }
}

# -------------------------------------------------------
# STEP 0：前提チェック
# -------------------------------------------------------

Write-Step "デイリーリサーチ開始：$Date"

$watchlist = "targets/${Date}_watchlist.csv"
if (-not (Test-Path $watchlist)) {
    Write-Fail "$watchlist が見つかりません。watchlistを作成してから再実行してください。"
    exit 1
}
Write-Success "watchlist確認: $watchlist"

# 開始STEPの自動検出
if ($Step -eq 0) {
    $Step = 1
    for ($s = 1; $s -le 5; $s++) {
        if (Test-StepDone $s) { $Step = $s + 1 }
        else { break }
    }
    if ($Step -gt 5) {
        Write-Skip "全STEPが完了済みです。"
        exit 0
    }
    Write-Host "開始STEP: $Step（未完了の最初のSTEPを自動検出）" -ForegroundColor DarkGray
}

# -------------------------------------------------------
# STEP 1：マクロ分析
# -------------------------------------------------------

if ($Step -le 1) {
    Write-Step "STEP 1：マクロ分析"

    if (Test-StepDone 1) {
        Write-Skip "reports/${Date}_macro.md は作成済み"
    } else {
        $prompt = @"
実行日: $Date
STEP 1（マクロ分析）のみ実行してください。

.claude/skills/macro.md のスキル手順に従い、${Date} のマクロ分析を実施してください。
結果を reports/${Date}_macro.md に保存して終了してください。
他のSTEPは実行しないでください。
"@
        $ok = Invoke-ClaudeStep 1 $prompt
        if (-not $ok) { Write-Fail "STEP 1 失敗。処理を中断します。"; exit 1 }
        Write-Success "STEP 1 完了"
        Invoke-GitPush 1
    }
}

# -------------------------------------------------------
# STEP 2：スクリーニング
# -------------------------------------------------------

if ($Step -le 2) {
    Write-Step "STEP 2：スクリーニング"

    if (Test-StepDone 2) {
        Write-Skip "reports/${Date}_screening.md は作成済み"
    } elseif (-not (Test-StepDone 1)) {
        Write-Fail "reports/${Date}_macro.md が存在しません。STEP 1から再実行してください。"
        exit 1
    } else {
        $prompt = @"
実行日: $Date
STEP 2（スクリーニング）のみ実行してください。

前提ファイル: reports/${Date}_macro.md（作成済み）
対象watchlist: targets/${Date}_watchlist.csv

.claude/skills/screening.md のスキル手順に従い、スクリーニングを実施してください。
結果を reports/${Date}_screening.md に保存して終了してください。
他のSTEPは実行しないでください。
"@
        $ok = Invoke-ClaudeStep 2 $prompt
        if (-not $ok) { Write-Fail "STEP 2 失敗。処理を中断します。"; exit 1 }
        Write-Success "STEP 2 完了"
        Invoke-GitPush 2
    }
}

# -------------------------------------------------------
# STEP 3：銘柄評価
# -------------------------------------------------------

if ($Step -le 3) {
    Write-Step "STEP 3：銘柄評価"

    if (Test-StepDone 3) {
        Write-Skip "reports/${Date}_evaluation.md は作成済み"
    } elseif (-not (Test-StepDone 2)) {
        Write-Fail "reports/${Date}_screening.md が存在しません。STEP 2から再実行してください。"
        exit 1
    } else {
        $prompt = @"
実行日: $Date
STEP 3（銘柄評価）のみ実行してください。

前提ファイル:
- reports/${Date}_macro.md（作成済み）
- reports/${Date}_screening.md（作成済み）

.claude/skills/evaluation.md のスキル手順に従い、スクリーニング選出銘柄を評価してください。
結果を reports/${Date}_evaluation.md に保存して終了してください。
他のSTEPは実行しないでください。
"@
        $ok = Invoke-ClaudeStep 3 $prompt
        if (-not $ok) { Write-Fail "STEP 3 失敗。処理を中断します。"; exit 1 }
        Write-Success "STEP 3 完了"
        Invoke-GitPush 3
    }
}

# -------------------------------------------------------
# STEP 4：詳細調査
# -------------------------------------------------------

if ($Step -le 4) {
    Write-Step "STEP 4：詳細調査（上位2銘柄）"

    if (Test-StepDone 4) {
        Write-Skip "deepdiveファイルは作成済み"
    } elseif (-not (Test-StepDone 3)) {
        Write-Fail "reports/${Date}_evaluation.md が存在しません。STEP 3から再実行してください。"
        exit 1
    } else {
        $prompt = @"
実行日: $Date
STEP 4（詳細調査）のみ実行してください。

前提ファイル:
- reports/${Date}_macro.md（作成済み）
- reports/${Date}_screening.md（作成済み）
- reports/${Date}_evaluation.md（作成済み）

.claude/skills/deep-dive.md のスキル手順に従い、evaluation.md の総合スコア上位2銘柄を詳細調査してください。
各銘柄の結果を reports/${Date}_deepdive_XXXX.md（XXXXは銘柄コード）に保存して終了してください。
他のSTEPは実行しないでください。
"@
        $ok = Invoke-ClaudeStep 4 $prompt
        if (-not $ok) { Write-Fail "STEP 4 失敗。処理を中断します。"; exit 1 }
        Write-Success "STEP 4 完了"
        Invoke-GitPush 4
    }
}

# -------------------------------------------------------
# STEP 5：記事作成 & note投稿
# -------------------------------------------------------

if ($Step -le 5) {
    Write-Step "STEP 5：記事作成 & note下書き投稿"

    if (Test-StepDone 5) {
        Write-Skip "記事ファイルは作成済み"
    } elseif (-not (Test-StepDone 4)) {
        Write-Fail "deepdiveファイルが存在しません。STEP 4から再実行してください。"
        exit 1
    } else {
        $prompt = @"
実行日: $Date
STEP 5（記事作成・note投稿）のみ実行してください。

前提ファイル（すべて作成済み）:
- reports/${Date}_macro.md
- reports/${Date}_screening.md
- reports/${Date}_evaluation.md
- reports/${Date}_deepdive_*.md

.claude/skills/article.md のスキル手順に従い、2種類の記事を作成・保存してnoteに下書き投稿してください。
- reports/${Date}_article_macro.md を作成 → note投稿
- reports/${Date}_article_screening.md を作成 → note投稿
完了後に終了してください。他のSTEPは実行しないでください。
"@
        $ok = Invoke-ClaudeStep 5 $prompt
        if (-not $ok) { Write-Fail "STEP 5 失敗。記事ファイルの保存状況を確認してください。"; exit 1 }
        Write-Success "STEP 5 完了"
        Invoke-GitPush 5
    }
}

# -------------------------------------------------------
# 完了サマリー
# -------------------------------------------------------

Write-Step "デイリーリサーチ完了：$Date"

$files = Get-ChildItem "reports/${Date}_*.md" -ErrorAction SilentlyContinue
Write-Host "生成ファイル一覧:"
$files | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Green }
