@echo off
setlocal

set "ROOT=%~dp0"
set "CXX=D:\dev\MinGW\bin\g++.exe"
set "OUTPUT=%ROOT%build\wsl1-pm2-bridge.exe"

if not exist "%CXX%" (
  echo Compiler not found: %CXX% 1>&2
  exit /b 2
)

if not exist "%ROOT%build" mkdir "%ROOT%build"

"%CXX%" ^
  -std=c++17 ^
  -O2 ^
  -Wall -Wextra -Wpedantic ^
  -D_WIN32_WINNT=0x0A00 ^
  -municode ^
  -static -static-libgcc -static-libstdc++ ^
  -Wl,--gc-sections -Wl,--strip-all ^
  "%ROOT%src\main.cpp" ^
  -o "%OUTPUT%"

if errorlevel 1 exit /b %errorlevel%

echo Built: %OUTPUT%
