# wsl1-pm2-bridge

一个用于 WSL1 + PM2 管理 Windows 命令和 Windows 可执行文件的轻量原生桥接器。

本分支是 `awey-pub` 中的独立杂项项目分支，采用 orphan branch，不包含 `main` 分支的目录和说明内容。

## 背景

直接从 WSL1 的 PM2 启动 Windows Node.js 或控制台程序时，WSL 的标准输入输出句柄可能被 Windows 运行时误识别，常见结果包括：

- `EISDIR`
- `EBADF`
- `uv_pipe_open`
- 进程短暂显示 `online` 后不断重启
- PM2 停止后 Windows 子进程仍然残留

## 原理

默认使用原生 C++ 桥接器：

```text
WSL1 PM2 -> wsl1-pm2-bridge.exe -> Windows Job Object -> Windows child tree
```

桥接器为子进程创建 Windows 匿名管道，把 stdout/stderr 转发给 PM2，并将子进程放入启用 `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` 的 Job Object。

因此：

- 子进程异常退出时，退出码传回 PM2，PM2 可以自动重启；
- `pm2 stop/delete` 终止桥接器时，Windows 内核自动清理整个子进程树；
- 不需要 watchdog 轮询；
- PM2 日志仍位于 `~/.pm2/logs/`。

## 构建

开发机使用 MinGW-w64，默认路径：

```text
D:\dev\MinGW
```

执行：

```bat
build.cmd
```

输出：

```text
build\wsl1-pm2-bridge.exe
```

运行目标机器只需要 Windows，不需要安装 MinGW-w64。

## 使用

直接运行 CMD/BAT 命令：

```powershell
wsl1-pm2-bridge.exe --cmd "dsh --profile web1"
```

直接运行 Windows EXE：

```powershell
wsl1-pm2-bridge.exe --exe ping.exe -t 127.0.0.1
```

指定 Windows 工作目录：

```powershell
wsl1-pm2-bridge.exe --cwd D:\work --cmd "tool.cmd --serve"
```

在 WSL1 中由 PM2 管理：

```bash
pm2 start /mnt/d/path/to/wsl1-pm2-bridge.exe \
  --name web1 \
  --restart-delay 3000 \
  --cwd /mnt/d/Users/example/.dsh \
  --interpreter none -- \
  --cmd "dsh --profile web1"
```

常用命令：

```bash
pm2 restart web1
pm2 logs web1
pm2 stop web1
pm2 delete web1
pm2 save
```

## Skill

项目内的 [skill/wsl1-pm2-bridge](skill/wsl1-pm2-bridge) 是可迁移的 Skill 副本，包含：

- `SKILL.md`：决策和操作说明；
- `scripts/generate_bridge.py`：生成 PM2 命令或 VBS 回退脚本；
- `bin/wsl1-pm2-bridge.exe`：默认原生桥接器；
- `agents/openai.yaml`：Skill UI 元数据。

从 Skill 目录中的生成器运行时，默认使用其自身 `bin/` 下的 EXE，不依赖固定盘符：

```bash
python3 skill/wsl1-pm2-bridge/scripts/generate_bridge.py \
  --name web1 \
  --command 'dsh --profile web1' \
  --cwd /mnt/d/Users/example/.dsh
```

## VBS 回退

原生 EXE 不可用时，可显式选择 VBS：

```bash
python3 skill/wsl1-pm2-bridge/scripts/generate_bridge.py \
  --backend vbs \
  --name web1 \
  --command 'dsh --profile web1'
```

VBS + watchdog：

```bash
python3 skill/wsl1-pm2-bridge/scripts/generate_bridge.py \
  --backend vbs --watchdog \
  --name web1 \
  --command 'dsh --profile web1'
```

VBS 脚本放在 `~/.pm2/win-vbe/`，日志仍由 PM2 写入 `~/.pm2/logs/`。VBS 无 watchdog 时，`pm2 stop/delete` 只能停止 `cscript.exe`，残留的 Windows 子进程需要手动关闭；watchdog 使用轮询，优先级低于原生 Job Object 方案。

## 限制

- 当前内置 EXE 面向 x86_64 Windows；
- 只监督进程退出，不检测进程假死或业务健康状态；
- Windows 传统 OEM/GBK 命令输出可能在 UTF-8 日志终端中显示乱码；
- `--cmd` 用于 CMD/BAT 或 Windows 命令行，简单 EXE 优先使用 `--exe`。
