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

dae 按固定顺序查找 geodata（`common/assets/assets.go`），**其中一个位置就是配置文件
所在目录**：

```text
1. $DAE_LOCATION_ASSET
2. <config.dae 所在目录>      ← 把两个 .dat 和 config.dae 放一起即可
3. /usr/local/share/dae
4. /usr/share/dae
```

`dae validate` 与 `dae run` 走的是**同一条**查找路径，所以「校验能找到」等价于
「运行也能找到」。

### 方式一：和 config.dae 放同一目录（推荐）

```bash
cd /etc/dae          # 换成你的 config.dae 所在目录
base=https://raw.githubusercontent.com/aweyonhub/awey-pub/pub-geosite/dist
curl -fsSLO "$base/geosite.dat"
curl -fsSLO "$base/geoip.dat"
```

### 方式二：放到系统目录

```bash
base=https://raw.githubusercontent.com/aweyonhub/awey-pub/pub-geosite/dist
sudo mkdir -p /usr/share/dae
sudo curl -fsSL -o /usr/share/dae/geosite.dat "$base/geosite.dat"
sudo curl -fsSL -o /usr/share/dae/geoip.dat   "$base/geoip.dat"
```

### 校验完整性

```bash
base=https://raw.githubusercontent.com/aweyonhub/awey-pub/pub-geosite/dist
curl -fsSLO "$base/manifest-geodata.json"
python3 - <<'PY'
import hashlib, json, sys
m = json.load(open("manifest-geodata.json"))
bad = 0
for name, meta in sorted(m["files"].items()):
    if "size" not in meta:
        continue                      # 源文件的哈希项，不是产物
    data = open(name, "rb").read()
    ok = hashlib.sha256(data).hexdigest() == meta["sha256"] and len(data) == meta["size"]
    print(("✅" if ok else "❌"), name, len(data), "B")
    bad += 0 if ok else 1
print("generated_at :", m["generated_at"])
print("source_commit:", m["source_commit"])
sys.exit(1 if bad else 0)
PY
```

### 镜像地址

`gh.awey.me` 与 `gh.872266.xyz` 等价，可互换。

```text
GitHub raw:  https://raw.githubusercontent.com/aweyonhub/awey-pub/pub-geosite/dist/geosite.dat
jsDelivr:    https://cdn.jsdelivr.net/gh/aweyonhub/awey-pub@pub-geosite/dist/geosite.dat
加速:        https://gh.awey.me/gh/aweyonhub/awey-pub@pub-geosite/dist/geosite.dat

清单:        https://raw.githubusercontent.com/aweyonhub/awey-pub/pub-geosite/dist/manifest-geodata.json
```

> **jsDelivr 有缓存。** 每次发布后 CI 会主动 purge；若仍拿到旧文件，
> 加 `?t=$(date +%s)` 绕过。

## 数据来源

源全部是**公开规则表**，所以本分支可以公开：

- [MetaCubeX/meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat) `meta` 分支的 `geo/geosite/*.mrs` 与 `geo/geoip/*.mrs`
- [anti-ad.net](https://anti-ad.net/) 的 `mihomo.mrs`

分类清单 —— `geoip` 3 类（`cn` / `private` / `telegram`），
`geosite` 14 类（`anthropic` / `anti-ad` / `category-ai-!cn` / `cn` / `github` /
`google` / `google-ads` / `google-gemini` / `openai` / `private` / `steam` /
`telegram` / `xai` / `youtube`），合计约 **22 万条域名**。

故意不含 v2fly DLC 的完整分类表：私有仓库里每个用到的分类都有 `geo-build` 声明，
那 1500 多个分类一个都用不到。需要完整表时在私有仓库加 `--base`
（产物 4.65 MB → 6.95 MB）。

构建逻辑在 `scripts/build-dat.py`，自带自检：用一个与编码器**独立实现**的解码器
把两个产物解回来，再和本次解析出的源数据逐条比对 —— 复用编码器只能证明内部自洽，
字段号写错时两边会一起错。

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

- 分支自述：`pub-geosite` 分支上的 [README.md](https://github.com/aweyonhub/awey-pub/blob/pub-geosite/README.md)（很短，只讲这是什么、怎么下、去哪看详情）
- dae 后端的设计与约束：私有仓库 `aweyonhub/awey-mihomo` 的 `dae/README.md`（第 11 节就是本文档对应的设计说明）
- 构建脚本：私有仓库 `scripts/build-dat.py`
- workflow 模板：私有仓库 `dae/pub-geosite/geosite.yml`

> **本文档是唯一的详细说明。** 分支上的 README 由 workflow 就地生成，
> 内容刻意保持简短 —— 分支文档按仓库约定集中在 `main` 的 `branch/` 目录下，
> 避免同一份说明在两处维护。
