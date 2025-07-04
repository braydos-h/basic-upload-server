
@echo off
rem create_uploader_scaffold.bat
rem Builds the uploader/ directory tree on Windows

setlocal EnableDelayedExpansion

rem ---- Config ----
set "ROOT=uploader"

rem ---- Make folders (ignore errors if they already exist) ----
mkdir "%ROOT%\static" 2>nul
mkdir "%ROOT%\uploads" 2>nul

rem ---- Touch files ----
> "%ROOT%\app.py" type nul
> "%ROOT%\cleanup.py" type nul
> "%ROOT%\static\index.html" type nul

rem ---- Drop a one-liner into index.html so you know it worked ----
(
    echo ^<!DOCTYPE html^>
    echo ^<html^>^<head^>^<title^>fuckass uploader^</title^>^</head^>
    echo ^<body^>^<h1^>It works &#x1F389;^</h1^>^</body^>
    echo ^</html^>
) > "%ROOT%\static\index.html"

rem ---- Add uploader/uploads/ to .gitignore (create it if needed) ----
if exist ".gitignore" (
    findstr /x /c:"uploader/uploads/" ".gitignore" >nul ^
        || echo uploader/uploads/>>".gitignore"
) else (
    echo uploader/uploads/>".gitignore"
)

echo 📂  All done. Tree created under "%ROOT%".
endlocal
