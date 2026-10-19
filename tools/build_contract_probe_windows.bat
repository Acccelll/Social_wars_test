@echo off
setlocal
set "ROOT=%~dp0.."
if defined FLEX_HOME (
  set "MXMLC=%FLEX_HOME%\bin\mxmlc.bat"
) else (
  set "MXMLC=mxmlc"
)
if not exist "%ROOT%\dist" mkdir "%ROOT%\dist"
call "%MXMLC%" -target-player=32.0 -debug=true -omit-trace-statements=false -source-path+="%ROOT%\as3\contract_harness\src" -source-path+="%ROOT%\as3\src" -output="%ROOT%\dist\ContractProbe.swf" "%ROOT%\as3\contract_harness\src\ContractProbe.as"
if errorlevel 1 exit /b 1
if not exist "%ROOT%\dist\ContractProbe.swf" exit /b 1
echo CONTRACT_COMPILATION_SUCCESS
