# awey-pub

awey 公开仓库，用于杂项需求或者私有仓库的公开加密分发。

| 分支 | 用途 | 说明 |
|---|---|---|
| [main](https://github.com/aweyonhub/awey-pub/tree/main) | 文档说明 | 本 README + `branch/` 目录下的分支说明 |
| [pub-mi](https://github.com/aweyonhub/awey-pub/tree/pub-mi) | Clash Mi 加密订阅 | CI 自动推送密文；使用说明见 [branch/pub-mi.md](branch/pub-mi.md) |
| [pub-geosite](https://github.com/aweyonhub/awey-pub/tree/pub-geosite) | dae 规则数据 | CI 每日推送；使用说明见 [branch/pub-geosite.md](branch/pub-geosite.md) |
| [sin](https://github.com/aweyonhub/awey-pub/tree/sin) | 神界：原罪 2 个人攻略整理 | 个人游戏攻略存档 |
| [dev_wsl1-pm2-bridge](https://github.com/aweyonhub/awey-pub/tree/dev_wsl1-pm2-bridge) | WSL1 + PM2 管理 Windows 进程 | 原生 C++ Job Object 桥接器、VBS 回退方案及可迁移 Skill；独立 orphan 分支 |

## 杂项项目分支

`dev_wsl1-pm2-bridge` 是一个独立的 orphan 分支，不包含 `main` 的目录内容，专门存放 WSL1 中使用 PM2 管理 Windows 命令和可执行文件的桥接器项目。默认方案是原生 C++ 桥接器，也提供 VBS 回退方式。

详细背景、构建和使用说明见该分支的 [README](https://github.com/aweyonhub/awey-pub/tree/dev_wsl1-pm2-bridge)。
