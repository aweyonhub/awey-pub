# pub-geosite 分支：dae 规则数据

> 本文档位于 `aweyonhub/awey-pub` 仓库的 `main` 分支（仅文档，不含产物本身）。
> 产物在 [pub-geosite](https://github.com/aweyonhub/awey-pub/tree/pub-geosite) 分支。

## 这个分支是干什么的

向 [dae](https://github.com/daeuniverse/dae)（eBPF 透明代理）分发规则数据。
私有仓库 `aweyonhub/awey-mihomo` 每天构建一次，CI 自动推送到本分支。

分支上**只有数据和一份自述文档**，没有明文配置、节点信息或凭证：

```text
.github/workflows/geosite.yml   生成这个分支的 workflow 自身
.gitattributes                  产物是二进制 protobuf，禁止换行转换
.gitignore
README.md                       分支自述
dist/
  geosite.dat                   域名分类（约 22 万条），v2ray GeoSiteList 格式
  geoip.dat                     IP 分类，v2ray GeoIPList 格式
  manifest-geodata.json         size + sha256 + 生成时间 + 源提交
```

**分支上永远只有 1 个 commit（orphan，无父提交）。** 每次发布都是从空仓库重建再
force-push，不累积历史 —— 只被机器拉取，历史没有价值，单提交让 `git clone` 永远是 O(1)。

## 怎么使用

dae 按固定顺序查找 geodata，**其中一个位置就是配置文件所在目录**，所以最简单的用法是
把两个 `.dat` 下载到和 `config.dae` 同一目录：

```bash
cd /etc/dae          # 换成你的 config.dae 所在目录
base=https://raw.githubusercontent.com/aweyonhub/awey-pub/pub-geosite/dist
curl -fsSLO "$base/geosite.dat"
curl -fsSLO "$base/geoip.dat"
```

`dae validate` 与 `dae run` 走同一条查找路径，校验通过即代表运行也能找到。

完整的下载地址、系统目录用法、完整性校验脚本、镜像地址见分支上的
[README](https://github.com/aweyonhub/awey-pub/blob/pub-geosite/README.md)。

## 数据来源

源全部是**公开规则表**，所以本分支可以公开：

- [MetaCubeX/meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat) `meta` 分支的 `geo/geosite/*.mrs` 与 `geo/geoip/*.mrs`
- [anti-ad.net](https://anti-ad.net/) 的 `mihomo.mrs`

分类清单 —— `geoip` 3 类（`cn` / `private` / `telegram`），
`geosite` 14 类（`anthropic` / `anti-ad` / `category-ai-!cn` / `cn` / `github` /
`google` / `google-ads` / `google-gemini` / `openai` / `private` / `steam` /
`telegram` / `xai` / `youtube`）。

故意不含 v2fly DLC 的完整分类表：私有仓库里每个用到的分类都有 `geo-build` 声明，
那 1500 多个分类一个都用不到。

## 维护说明

- **谁写入**：`aweyonhub/awey-pub` 自己的 GitHub Actions（`.github/workflows/geosite.yml`），
  用仓库内置 `GITHUB_TOKEN` force-push。**不需要** `PUBLIC_REPO_TOKEN` 那类跨仓库写权限。
- **什么时候更新**：每天 **18:23 UTC（次日 02:23 CST）**。上游内容没变时**不产生提交**。
  分钟刻意不取 0 —— GitHub 文档说整点是负载高峰，`schedule` 可能被延迟甚至丢弃。
- **为什么定时任务放在公开仓库**：GitHub 的 `schedule` 触发器在私有仓库上不可靠
  （免费账号下可能根本不触发）。本仓库公开，且每天都有 push，
  「60 天无活动自动禁用」也碰不到。私有仓库 `aweyonhub/awey-mihomo` 保留了
  `.github/workflows/geodata.yml` 作为**手动备份出口**。
- **需要什么 secret**：本仓库的 `SOURCE_REPO_TOKEN` —— 对私有仓库
  `aweyonhub/awey-mihomo` 有**只读**权限的 token（CI 要 clone 它来跑构建脚本）。
- **workflow 必须以 `main` 上的文件为准**：GitHub 只在**默认分支**上发现 workflow，
  再让你选 ref 运行。放在 `pub-geosite` 上既不会触发 `schedule`，
  `workflow_dispatch` 也会返回 `404: workflow ... not found on the default branch`。

## 与 pub-mi 的区别

| | [pub-mi](https://github.com/aweyonhub/awey-pub/tree/pub-mi) | pub-geosite |
|---|---|---|
| 内容 | 加密后的 mihomo 配置 | dae 的规则数据（明文，本身就是公开数据） |
| 触发 | 私有仓库打 `v*` tag | 每天定时 |
| 谁推送 | 私有仓库 CI（PAT force-push） | 本仓库自己的 CI（内置 token） |
| 消费者 | Clash Mi 客户端 | dae / daed |

## 相关文档

- 分支自述（下载地址、校验脚本、镜像）：[pub-geosite/README.md](https://github.com/aweyonhub/awey-pub/blob/pub-geosite/README.md)
- dae 后端的设计与约束：私有仓库 `aweyonhub/awey-mihomo` 的 `dae/README.md`
- 构建脚本：私有仓库 `scripts/build-dat.py`
