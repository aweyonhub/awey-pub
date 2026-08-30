# pub-mi 分支：Clash Mi 加密订阅

> 本文档位于 `aweyonhub/awey-pub` 仓库的 `main` 分支（仅文档，不含任何明文配置）。

## 这个分支是干什么的

`pub-mi` 分支用于向 Clash Mi 客户端分发**加密后的配置**：

- 私有仓库（`aweyonhub/awey-mihomo`）打 `v*` tag 后，CI 自动构建完整配置，
  用密码加密成 Clash Mi 兼容密文（AES-128-CBC，密钥 = MD5 密码），推送到本分支。
- 分支上**只有密文文件**：`config.yaml`（GitHub 源版）、`config.jsdelivr.yaml`（jsDelivr 源版）、`VERSION`。
- 任何人都能下载，但只有持密码的人能解密——明文永远不出私有仓库。

## 怎么使用（Clash Mi 客户端）

添加订阅时填写（推荐 **jsDelivr 源版**，规则源走 jsDelivr CDN，GitHub 直连不畅也可用）：

```text
订阅 URL: https://gh.awey.me/ghh/aweyonhub/awey-pub@pub-mi/config.jsdelivr.yaml
解密密码: <发布时使用的密码>
```

如使用 GitHub 源版：

```text
订阅 URL: https://gh.awey.me/ghh/aweyonhub/awey-pub@pub-mi/config.yaml
解密密码: <发布时使用的密码>
```

要点：

- **域名等价**：`gh.awey.me` 与 `gh.872266.xyz` 完全等价，下文 URL 可互相替换。
- `gh.awey.me/ghh/...` 是 VPS Caddy 转发地址，会附加响应头
  `subscription-encryption: true`——**Clash Mi 只认带头响应**，直接使用
  `cdn.jsdelivr.net` 或 raw 直链会报 "Invalid Clash Yaml file"。
- 更新后需要 Clash Mi 重新加载（TUN 关→开 或重启）才生效。

## 非 Clash Mi 客户端 / 手动下载

以下为**不带解密触发头**的原始密文直链，适合命令行、curl、其他脚本或围观：

```text
GitHub 源版:   https://raw.githubusercontent.com/aweyonhub/awey-pub/pub-mi/config.yaml
jsDelivr 源版: https://raw.githubusercontent.com/aweyonhub/awey-pub/pub-mi/config.jsdelivr.yaml
版本标记:      https://raw.githubusercontent.com/aweyonhub/awey-pub/pub-mi/VERSION
```

jsDelivr CDN 镜像（有缓存，更新后需 purge；CI 已内置）：

```text
GitHub 源版:   https://cdn.jsdelivr.net/gh/aweyonhub/awey-pub@pub-mi/config.yaml
jsDelivr 源版: https://cdn.jsdelivr.net/gh/aweyonhub/awey-pub@pub-mi/config.jsdelivr.yaml
```

手动解密：

```bash
curl -sS https://raw.githubusercontent.com/aweyonhub/awey-pub/pub-mi/config.jsdelivr.yaml -o config.enc
python3 tools/crypt-mi.py -d -i config.enc -o config.yaml    # 需持有密码
```

## 维护说明

- **谁写入**：私有仓库 CI 的 `github-actions[bot]`，force-push 覆盖本分支（无历史）。
- **什么时候更新**：私有仓库推送 `v*` tag 时（构建 + 加密 + 自动发布）。
- **密码从哪来**：私有仓库 GitHub Actions Secret `CONFIG_ENCRYPT_PASSWORD`；
  与客户端填的解密密码必须一致。
- **安全须知**：密文公开可离线爆破，密码必须足够长/随机（≥ 20 位）；
  本分支禁止出现任何**明文配置/节点凭证**；发现泄露立即轮换密码并重新发布。

## 相关文档

完整原理与工具用法见私有仓库：
`doc/FEATURE/v0.4-clash-mi-加密订阅.md`
