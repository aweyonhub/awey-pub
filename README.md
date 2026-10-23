# dae 规则数据

本分支是**独立 orphan 分支**，只放数据，**永远只有 1 个 commit**
（每次发布都 force-push 覆盖，不累积历史）。

```text
dist/geosite.dat             域名分类（约 22 万条），v2ray GeoSiteList 格式
dist/geoip.dat               IP 分类，v2ray GeoIPList 格式
dist/manifest-geodata.json   size + sha256 + 生成时间 + 源提交
```

由私有仓库 [`aweyonhub/awey-mihomo`](https://github.com/aweyonhub/awey-mihomo)
每周构建，源全部是公开规则表，所以本分支**不含任何个人配置或凭证**。

## 用法

dae 会在 `config.dae` 所在目录查找 geodata，所以放到一起即可：

```bash
cd /etc/dae          # 换成你的 config.dae 所在目录
base=https://raw.githubusercontent.com/aweyonhub/awey-pub/pub-geosite/dist
curl -fsSLO "$base/geosite.dat"
curl -fsSLO "$base/geoip.dat"
```

## 详情

完整说明见 [`branch/pub-geosite.md`](https://github.com/aweyonhub/awey-pub/blob/main/branch/pub-geosite.md)：
分类清单、系统目录用法、完整性校验脚本、jsDelivr 镜像、维护说明。
