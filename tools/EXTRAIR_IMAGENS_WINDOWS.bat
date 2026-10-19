@echo off
setlocal EnableExtensions
rem Social Wars 0.02a - exportacao VISUAL em lotes para Windows.
rem Este utilitario NAO modifica sua instalacao nem seus saves.
set "ROOT=%~dp0.."
cd /d "%ROOT%"
set "INPUT_ZIP=%SW_ZIP%"
if not defined INPUT_ZIP set "INPUT_ZIP=%ROOT%\social-warriors_0.02a.zip"
set "FFDEC=%FFDEC_JAR%"
if not defined FFDEC set "FFDEC=%ROOT%\tools\ffdec.jar"
if not exist "%INPUT_ZIP%" (
  echo ERRO: Nao encontrei social-warriors_0.02a.zip.
  echo Coloque o ZIP original na raiz do repositorio ou defina SW_ZIP.
  exit /b 2
)
if not exist "%FFDEC%" (
  echo ERRO: Nao encontrei ffdec.jar em "%FFDEC%".
  echo Baixe JPEXS FFDec e copie ffdec.jar para tools ou defina FFDEC_JAR.
  exit /b 2
)
where java >nul 2>&1
if errorlevel 1 (
  echo ERRO: Java nao encontrado. Instale Java 17 ou superior.
  exit /b 2
)
where py >nul 2>&1
if errorlevel 1 (
  echo ERRO: Python Launcher nao encontrado. Instale Python 3.
  exit /b 2
)
set "START=%SW_START%"
if not defined START set "START=0"
set "LIMIT=%SW_LIMIT%"
if not defined LIMIT set "LIMIT=30"
set "TYPE=%SW_TYPES%"
if not defined TYPE set "TYPE=visual"
set "EXTERNAL="
if "%START%"=="0" set "EXTERNAL=--external"
echo Extraindo lote START=%START% LIMIT=%LIMIT% TYPE=%TYPE%
echo Os arquivos serao salvos em dist\visual-export sem alterar o jogo.
py -3 tools\visual_extract.py --archive "%INPUT_ZIP%" --ffdec "%FFDEC%" --out "%ROOT%\dist\visual-export" --start %START% --limit %LIMIT% --types %TYPE% %EXTERNAL%
if errorlevel 1 (
  echo Falha. Consulte dist\visual-export\export_summary.json
  exit /b 1
)
echo Lote finalizado. Para prosseguir, aumente SW_START em %LIMIT%.
exit /b 0
