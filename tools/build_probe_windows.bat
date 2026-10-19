@echo off
setlocal
set "ROOT=%~dp0.."
if defined FLEX_HOME (
  set "MXMLC=%FLEX_HOME%\bin\mxmlc.bat"
) else (
  set "MXMLC=mxmlc"
)
if not exist "%ROOT%\dist" mkdir "%ROOT%\dist"
call "%MXMLC%" -source-path+="%ROOT%\as3\src" -output="%ROOT%\dist\AS3Probe.swf" "%ROOT%\as3\src\AS3Probe.as"
if errorlevel 1 (
  echo COMPILATION_FAILED_OR_COMPILER_UNAVAILABLE
  exit /b 1
)
if not exist "%ROOT%\dist\AS3Probe.swf" (
  echo COMPILATION_FAILED
  exit /b 1
)
echo COMPILATION_SUCCESS: %ROOT%\dist\AS3Probe.swf
