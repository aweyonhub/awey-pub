#!/usr/bin/env python3
"""Print or generate a Windows bridge command for WSL1-hosted PM2."""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
from pathlib import Path


NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,62}$")
SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_NATIVE_EXE = SKILL_ROOT / "bin" / "wsl1-pm2-bridge.exe"


def vbs_string(value: str) -> str:
    return value.replace('"', '""')


def windows_path(path: Path) -> str:
    try:
        result = subprocess.run(
            ["wslpath", "-w", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise SystemExit("Run this generator inside the target WSL distribution.") from exc
    return result.stdout.strip()


def build_cmd(name: str, command: str) -> str:
    return (
        "@echo off\r\n"
        "setlocal\r\n"
        f'set "PM2_WIN_BRIDGE_NAME={name}"\r\n'
        f"{command}\r\n"
        "exit /b %errorlevel%\r\n"
    )


def build_vbs(name: str, watchdog: bool = False) -> str:
    safe_name = vbs_string(name)
    watchdog_declarations = ""
    watchdog_path_assignment = ""
    watchdog_start = ""

    if watchdog:
        watchdog_declarations = '''Dim bridgeProcesses, bridgeProcess
Dim watchdogPath, watchdogCommand, bridgePid, newestCreation
'''
        watchdog_path_assignment = (
            f'watchdogPath = fso.BuildPath(scriptDir, "{safe_name}-watchdog.vbs")\n'
        )
        watchdog_start = '''
' Find the newest cscript process running this exact bridge script. Only a
' still-running child needs a watchdog; short-lived commands can exit directly.
If child.Status = 0 Then
  bridgePid = 0
  newestCreation = ""
  Set bridgeProcesses = wmi.ExecQuery( _
    "SELECT ProcessId, CreationDate, CommandLine FROM Win32_Process " & _
    "WHERE Name = 'cscript.exe'")

  For Each bridgeProcess In bridgeProcesses
    If Not IsNull(bridgeProcess.CommandLine) Then
      If InStr(1, bridgeProcess.CommandLine, WScript.ScriptFullName, vbTextCompare) > 0 Then
        If bridgeProcess.CreationDate > newestCreation Then
          newestCreation = bridgeProcess.CreationDate
          bridgePid = bridgeProcess.ProcessId
        End If
      End If
    End If
  Next

  If bridgePid = 0 Then
    shell.Run "taskkill.exe /PID " & child.ProcessID & " /T /F", 0, True
    WScript.Quit 3
  End If

  watchdogCommand = "wscript.exe //nologo " & _
    quote & watchdogPath & quote & " " & _
    bridgePid & " " & child.ProcessID & " " & _
    quote & WScript.ScriptFullName & quote & " " & _
    quote & batchPath & quote
  shell.Run watchdogCommand, 0, False
End If
'''

    return f'''Option Explicit

Dim shell, wmi, fso, processes, process, child
Dim scriptDir, batchPath
Dim quote, command, exitCode
{watchdog_declarations}
Set shell = CreateObject("WScript.Shell")
Set wmi = GetObject("winmgmts:\\\\.\\root\\cimv2")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
batchPath = fso.BuildPath(scriptDir, "{safe_name}.cmd")
{watchdog_path_assignment}
' Remove only a stale cmd process launched from this app-specific batch file.
Set processes = wmi.ExecQuery( _
  "SELECT ProcessId, Name, CommandLine FROM Win32_Process WHERE Name = 'cmd.exe'")

For Each process In processes
  If Not IsNull(process.CommandLine) Then
    If InStr(1, process.CommandLine, batchPath, vbTextCompare) > 0 Then
      shell.Run "taskkill.exe /PID " & process.ProcessId & " /T /F", 0, True
    End If
  End If
Next

quote = Chr(34)
command = "cmd.exe /d /s /c " & quote & _
  "call " & quote & batchPath & quote & quote

' Exec creates Windows-side pipes for the child. Forward them through cscript
' so PM2 receives the output on its normal stdout/stderr log paths.
Set child = shell.Exec(command)
child.StdIn.Close
{watchdog_start}
Do While child.Status = 0
  If Not child.StdOut.AtEndOfStream Then
    WScript.StdOut.WriteLine child.StdOut.ReadLine
  End If
  If Not child.StdErr.AtEndOfStream Then
    WScript.StdErr.WriteLine child.StdErr.ReadLine
  End If
  WScript.Sleep 100
Loop

Do While Not child.StdOut.AtEndOfStream
  WScript.StdOut.WriteLine child.StdOut.ReadLine
Loop
Do While Not child.StdErr.AtEndOfStream
  WScript.StdErr.WriteLine child.StdErr.ReadLine
Loop

exitCode = child.ExitCode
WScript.Quit exitCode
'''


def build_watchdog() -> str:
    return '''Option Explicit

Dim shell, wmi, bridgePid, childPid, bridgeMarker, childMarker

If WScript.Arguments.Count <> 4 Then
  WScript.Quit 2
End If

Set shell = CreateObject("WScript.Shell")
Set wmi = GetObject("winmgmts:\\\\.\\root\\cimv2")

bridgePid = CLng(WScript.Arguments(0))
childPid = CLng(WScript.Arguments(1))
bridgeMarker = WScript.Arguments(2)
childMarker = WScript.Arguments(3)

Do
  If Not ProcessMatches(childPid, childMarker) Then
    WScript.Quit 0
  End If

  If Not ProcessMatches(bridgePid, bridgeMarker) Then
    shell.Run "taskkill.exe /PID " & childPid & " /T /F", 0, True
    WScript.Quit 0
  End If

  WScript.Sleep 250
Loop

Function ProcessMatches(processId, marker)
  Dim matches, item
  ProcessMatches = False
  Set matches = wmi.ExecQuery( _
    "SELECT CommandLine FROM Win32_Process WHERE ProcessId = " & CLng(processId))

  For Each item In matches
    If Not IsNull(item.CommandLine) Then
      If InStr(1, item.CommandLine, marker, vbTextCompare) > 0 Then
        ProcessMatches = True
      End If
    End If
  Next
End Function
'''


def write_new(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"Refusing to overwrite existing file: {path}")
    path.write_text(content, encoding="utf-8", newline="")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="PM2 application name")
    parser.add_argument("--command", required=True, help="Windows cmd.exe command line")
    parser.add_argument(
        "--backend",
        choices=("native", "vbs"),
        default="native",
        help="bridge backend (default: native)",
    )
    parser.add_argument(
        "--native-exe",
        default=str(DEFAULT_NATIVE_EXE),
        help=f"WSL path to native bridge (default: {DEFAULT_NATIVE_EXE})",
    )
    parser.add_argument(
        "--output-dir",
        default="~/.pm2/win-vbe",
        help="WSL output directory (default: ~/.pm2/win-vbe)",
    )
    parser.add_argument("--cwd", help="stable WSL working directory for the PM2 app")
    parser.add_argument(
        "--restart-delay",
        type=int,
        default=3000,
        help="PM2 restart delay in milliseconds (default: 3000)",
    )
    parser.add_argument(
        "--watchdog",
        action="store_true",
        help="enable polling cleanup so PM2 stop/delete also terminates the Windows child tree",
    )
    parser.add_argument("--force", action="store_true", help="replace existing bridge files")
    args = parser.parse_args()

    if not NAME_RE.fullmatch(args.name):
        raise SystemExit("--name must contain only letters, digits, dot, underscore, or hyphen")
    if "\n" in args.command or "\r" in args.command:
        raise SystemExit("--command must be a single command line")
    if args.restart_delay < 0:
        raise SystemExit("--restart-delay cannot be negative")
    if not os.environ.get("WSL_DISTRO_NAME"):
        raise SystemExit("Run this generator inside the target WSL distribution.")
    if args.backend != "vbs" and args.watchdog:
        raise SystemExit("--watchdog requires --backend vbs")
    if args.backend != "vbs" and args.force:
        raise SystemExit("--force applies only to --backend vbs")

    if args.backend == "native":
        native_exe = Path(args.native_exe).expanduser().resolve()
        if not native_exe.is_file():
            raise SystemExit(
                f"Native bridge not found: {native_exe}\n"
                "Build/install it, pass --native-exe, or explicitly fall back "
                "with --backend vbs."
            )

        command_parts = [
            "pm2",
            "start",
            str(native_exe),
            "--name",
            args.name,
            "--restart-delay",
            str(args.restart_delay),
        ]
        if args.cwd:
            command_parts.extend(
                ["--cwd", str(Path(args.cwd).expanduser().resolve())]
            )
        command_parts.extend(
            ["--interpreter", "none", "--", "--cmd", args.command]
        )

        print(f"Backend: native ({native_exe})")
        print(
            "Stop semantics: Windows Job Object terminates the child process tree "
            "when PM2 stops/deletes the bridge."
        )
        print("PM2 command:")
        print(" ".join(shlex.quote(part) for part in command_parts))
        return

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd_path = output_dir / f"{args.name}.cmd"
    vbs_path = output_dir / f"{args.name}.vbs"
    watchdog_path = output_dir / f"{args.name}-watchdog.vbs"

    write_new(cmd_path, build_cmd(args.name, args.command), args.force)
    write_new(vbs_path, build_vbs(args.name, watchdog=args.watchdog), args.force)
    if args.watchdog:
        write_new(watchdog_path, build_watchdog(), args.force)

    win_vbs = windows_path(vbs_path)
    cscript = subprocess.run(
        ["bash", "-lc", "command -v cscript.exe"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    print("Backend: vbs" + (" + watchdog" if args.watchdog else ""))
    print(f"Created: {cmd_path}")
    print(f"Created: {vbs_path}")
    if args.watchdog:
        print(f"Created: {watchdog_path}")
        print("Watchdog enabled: PM2 stop/delete will terminate the Windows child tree.")
    else:
        print(
            "WARNING: watchdog is disabled by default. PM2 stop/delete only stops "
            "the bridge; close the remaining Windows cmd/node process tree manually."
        )
        if watchdog_path.exists():
            print(f"Unused old watchdog file remains: {watchdog_path}")
    print("PM2 command:")
    command_parts = [
        "pm2",
        "start",
        cscript,
        "--name",
        args.name,
        "--restart-delay",
        str(args.restart_delay),
    ]
    if args.cwd:
        command_parts.extend(["--cwd", str(Path(args.cwd).expanduser().resolve())])
    command_parts.extend(["--interpreter", "none", "--", "//nologo", win_vbs])
    print(" ".join(shlex.quote(part) for part in command_parts))


if __name__ == "__main__":
    main()
