---
name: wsl1-pm2-windows
description: Manage Windows executables, CMD/BAT files, and PowerShell commands with PM2 running inside WSL1, preferring a native Job Object bridge with explicit VBS fallback modes. Use when direct launches fail with EISDIR, EBADF, uv_pipe_open, restart loops, inherited stdio problems, or incomplete Windows child cleanup.
---

# WSL1 PM2 Windows

Keep PM2 as the process supervisor in WSL1 while inserting a Windows-side bridge between PM2 and the Windows command.

## Principle

Directly starting a Windows Node.js or console process from Linux PM2 can pass WSL pipe/IPC-backed standard handles that the Windows runtime cannot use. Typical symptoms are `EISDIR`, `EBADF`, `uv_pipe_open`, or a process that briefly reports `online` and then enters a restart loop.

## Backend selection

Use the native bridge by default. Select VBS only when the native executable is unavailable, incompatible, or explicitly requested. Never silently downgrade because stop semantics differ.

### Native bridge (default)

Use this chain:

```text
WSL1 PM2 -> wsl1-pm2-bridge.exe -> Windows Job Object -> Windows child tree
```

The native bridge:

- creates Windows anonymous pipes for the child and forwards stdout/stderr to PM2;
- waits for the root child and propagates its exit code so PM2 `autorestart` works;
- places the child tree in a Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`;
- lets `pm2 stop`, `pm2 delete`, bridge crashes, and forced termination clean the Windows child tree without polling.

The packaged default executable is [bin/wsl1-pm2-bridge.exe](bin/wsl1-pm2-bridge.exe). The generator resolves it relative to its own Skill directory, so moving or installing the Skill on another drive does not change the command. Packaged version `0.1.0` targets x86_64 Windows, uses only Windows system DLLs, and has SHA-256 `B407C97CB6AB7460D5762BC46F8E0C6CE0CC91A90DEE976E8E0B4CEB1C6B6A46`; MinGW-w64 is not required at runtime.

From WSL, its resolved path has this shape:

```text
<skill-root>/bin/wsl1-pm2-bridge.exe
```

Override the packaged executable with `--native-exe <WSL-path>` only when testing or deploying another build.

### VBS fallback

Use this chain only as an explicit fallback:

```text
WSL1 PM2 -> cscript.exe -> generated VBS -> cmd.exe -> Windows command
```

The VBS bridge:

- creates the Windows child through `WScript.Shell.Exec`, so the child receives Windows-side pipes rather than WSL1 PM2 handles;
- forwards the child's stdout/stderr to `WScript.StdOut`/`WScript.StdErr`, allowing PM2 to write its normal `/home/<user>/.pm2/logs/` files;
- runs without a visible console window;
- waits synchronously for the Windows command;
- returns its exit code so PM2 `autorestart` works;
- removes a stale matching Windows command before restart.

Without a watchdog, `pm2 stop/delete` stops only `cscript.exe`; the Windows `cmd/node` tree may remain running and must be closed manually. `pm2 restart` remains usable because the next bridge removes the stale app-specific `cmd` tree before launching a replacement.

Add `--watchdog` only with `--backend vbs` when automatic stop-tree cleanup is required but the native bridge cannot be used. This third script polls bridge liveness and performs `taskkill /T`; it is less atomic than the native Job Object design.

`.vbe` is only an encoded VBS file and provides no process-management advantage. Generate `.vbs` files even though the directory is named `win-vbe`.

## Generate or select a bridge

Use [scripts/generate_bridge.py](scripts/generate_bridge.py) from inside the target WSL distribution. It prints the exact `pm2 start` command for the selected backend.

Required inputs:

- a short PM2-safe name;
- the exact Windows command that already works under `cmd.exe /d /s /c`.

Native default; this creates no fallback scripts:

```bash
python3 /path/to/scripts/generate_bridge.py \
  --name web1 \
  --command 'dsh --profile web1' \
  --cwd /mnt/d/Users/example/.dsh
```

Explicit VBS fallback:

```bash
python3 /path/to/scripts/generate_bridge.py \
  --backend vbs \
  --name web1 \
  --command 'dsh --profile web1' \
  --cwd /mnt/d/Users/example/.dsh
```

Explicit VBS fallback with watchdog:

```bash
python3 /path/to/scripts/generate_bridge.py \
  --backend vbs --watchdog \
  --name web1 \
  --command 'dsh --profile web1' \
  --cwd /mnt/d/Users/example/.dsh
```

VBS modes create `<name>.cmd` and `<name>.vbs` under `~/.pm2/win-vbe/`; watchdog mode additionally creates `<name>-watchdog.vbs`. Keep that directory script-only. PM2 logs remain under `~/.pm2/logs/`.

The generator prints the exact `pm2 start` command. Run it only when the user asked to register or start the process; script generation alone does not imply permission to change the active PM2 process list.

For VBS modes, preserve existing destination files unless replacement was explicitly requested. Use `--force` only with that authorization. `--watchdog` and `--force` are invalid for the native backend.

## Register and verify

Use `--interpreter none` and put bridge arguments after `--`. Pass a stable, Windows-backed WSL `--cwd` when the command has a natural working directory; do not persist a temporary Codex workspace as `pm_cwd`. The generator defaults to a 3000 ms restart delay to prevent tight failure loops.

After registration:

1. Check `pm2 describe <name>` and confirm `status: online` and `autorestart: true`.
2. Verify the actual service outcome, such as its listening port or expected output file.
3. Read runtime output with `pm2 logs <name>`. The `~/.pm2/win-vbe/` directory contains bridge scripts, not the authoritative runtime logs.
4. Exercise `pm2 restart <name>` and ensure the new process remains stable.
5. For native mode, exercise `pm2 stop <name>` and verify the Windows child tree and listening port disappear, then start it again if the service should remain running.
6. For VBS without watchdog, warn that `pm2 stop/delete` requires manually closing the remaining Windows process tree. For VBS with watchdog, exercise stop and verify cleanup.
7. Run `pm2 save` only when persistence was requested or is already part of the user's workflow.

Use a small `restart_delay` when repeated failures would otherwise produce a tight restart loop.

## Operational boundaries

- `pm2 save` stores the process list but does not itself start WSL after Windows reboot. For reboot persistence, use one Windows Task Scheduler entry at user logon with a 5-second trigger delay, then run `wsl.exe -d <distro> -u <pm2-user> -- bash -lc "pm2 resurrect"`; PM2 remains the app-level manager. The short delay lets Windows sign-in and WSL interoperability initialization settle; preserve another delay when the user explicitly requests one. `<pm2-user>` must be the Linux user that owns `~/.pm2/dump.pm2` and normally runs the PM2 daemon. Do not rely on WSL's default user or use root unless it is genuinely that same PM2 user; the Windows task principal and the WSL Linux user are separate identities.
- WSL1 PM2 cannot reliably tree-kill Windows descendants itself. Native mode supplies atomic OS-enforced cleanup through a Windows Job Object. VBS mode leaves cleanup manual unless its optional polling watchdog is enabled.
- Avoid inline `bash -> cmd -> PowerShell` quoting when the command is non-trivial. Put the Windows command in the generated `.cmd` file.
- Do not overwrite unrelated PM2 applications or kill processes using a broad executable-name match.
- These bridges supervise process exit, not responsiveness. Do not claim PM2 detects a process that remains alive but is hung unless a separate health check was explicitly added.
