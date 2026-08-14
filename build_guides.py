from pathlib import Path
from html import escape
from html.parser import HTMLParser
import re

ROOT = Path(__file__).resolve().parent

GUIDES = {
    "神界原罪2-序章梅里威瑟号全任务隐藏内容攻略.md": {
        "out": "神界原罪2-序章梅里威瑟号全任务隐藏内容攻略-增强版.html",
        "eyebrow": "CHAPTER 1 · THE MERRYWEATHER",
        "subtitle": "开场押送船｜谋杀调查、起源角色初见、灾后二次搜刮与离船检查",
        "route": ["💤 醒来", "🕵️ Finn 案", "🗣️ 角色初见", "💥 源力爆发", "🪲 甲板", "🛶 离船"],
        "cards": [("🧭 核心路线", "先搜船舱，再查谋杀；灾后必须二次搜刮。"), ("🎁 隐藏收益", "Finn 尸块可让精灵学习 Adrenaline。"), ("⚠️ 不可返回", "登上救生艇后永久失去梅里威瑟号。"), ("💀 极限玩法", "死亡之雾桶属于高风险破序路线。")],
    },
    "神界原罪2-复仇女神号航船间章全任务隐藏内容攻略.md": {
        "out": "神界原罪2-复仇女神号航船间章全任务隐藏内容攻略-增强版.html",
        "eyebrow": "INTERLUDE · LADY VENGEANCE",
        "subtitle": "跨章活木战船｜永久队伍、Dallis 舱房、Malady 船战与营地服务",
        "route": ["⚓ 登船", "💎 Strange Gem", "🔐 Fortitude", "🎵 唤醒战船", "⚔️ 守护 Malady", "🌀 回音大厅"],
        "cards": [("👥 永久队伍", "第一次启航后四人队锁定，未选起源角色无法再招募。"), ("🔐 舱房密码", "湿透日记给出 Fortitude，Alexander 提供 Strange Gem。"), ("⚔️ 船战目标", "真正胜利条件是守住 Malady，不要求击杀 Dallis。"), ("🪞 船上服务", "魔镜、仓库、雇佣兵与跨章 NPC 都在这里。")],
    },
    "神界原罪2-第二章死神海岸全任务隐藏内容详尽攻略.md": {
        "out": "神界原罪2-第二章死神海岸全任务隐藏内容详尽攻略-增强版.html",
        "eyebrow": "ACT II · REAPER'S COAST",
        "subtitle": "源力觉醒｜漂流之森、破坏者洞穴、黑井、锯木厂与血月岛",
        "route": ["🚢 上岸", "🏘️ 漂流之森", "🕳️ Mordus", "🪦 石园", "🔥 黑井", "🪵 锯木厂", "🌑 血月岛"],
        "cards": [("📌 主线目标", "从七名导师中获得两次扩容，把源力上限提高到 3。"), ("⚠️ 救人优先", "Gwydian、Saheila、Almira、Corbin 等 NPC 很容易意外死亡。"), ("🌹 永久收益", "蜘蛛之吻、Idol of Rebirth、秃鹫套与 Corbin 升级机制。"), ("🧩 长线物品", "Ancient Stone Tablet 同时关联 Ryker、Almira 与 Swornbreaker。")],
    },
    "神界原罪2-第三章无名岛全任务隐藏内容详尽攻略.md": {
        "out": "神界原罪2-第三章无名岛全任务隐藏内容详尽攻略-增强版.html",
        "eyebrow": "ACT III · THE NAMELESS ISLE",
        "subtitle": "升神之争｜七神祭坛、两大阵营、Shadow Prince、学院与永久属性",
        "route": ["🏝️ 登岛", "🛕 七神祭坛", "⚖️ 阵营抉择", "🌳 Mother Tree", "🌙 Lunar Gate", "🏛️ Academy", "🏟️ Arena"],
        "cards": [("☀️🌙 七柱答案", "人、兽人、蜥蜴属太阳；精灵、矮人、小鬼、巫师属月亮。"), ("🗣️ 对话顺序", "Red Prince 必须先谈 Shadow Prince，再让 Sebille 复仇。"), ("📈 永久属性", "学院六名教师提供 +5 / -5 的永久属性交换。"), ("⚠️ 最终节点", "进入 Arena of the One 后无名岛永久关闭。")],
    },
    "神界原罪2-第四章阿克斯全任务隐藏内容详尽攻略.md": {
        "out": "神界原罪2-第四章阿克斯全任务隐藏内容详尽攻略-增强版.html",
        "eyebrow": "ACT IV · ARX",
        "subtitle": "终局之城｜Deathfog、Kemm、Doctor、领事馆、Lucian 墓穴与多结局",
        "route": ["🏚️ 坠毁点", "⚔️ 城门", "⚓ 港口", "🏙️ 城区", "🕳️ 下水道", "🖼️ Kemm Vault", "⛪ Path of Blood"],
        "cards": [("☠️ 最大避坑", "不要误把死亡之雾释放进 Arx，会清空大量 NPC 与任务。"), ("🖼️ 主线枢纽", "Kemm Vault 关联关键画作、Arhu、Kemm 真相和吞噬者头盔。"), ("😈 队友终局", "Lohse / Doctor、Beast / Justinia、Red Prince / Sadha 集中收束。"), ("🐉 四遗物", "污染套与吞噬者套在 Arx 完成最终形态。")],
    },
    "神界原罪2-全章节详尽攻略索引.md": {
        "out": "神界原罪2-全章节详尽攻略索引.html",
        "eyebrow": "DEFINITIVE EDITION · COMPLETE GUIDE",
        "subtitle": "从梅里威瑟号到 Lucian 墓穴｜独立分章、跨章航船与永久节点索引",
        "route": ["🚢 序章", "🏰 欢乐堡", "⛵ 航船间章", "🌊 死神海岸", "🏝️ 无名岛", "🏙️ 阿克斯"],
        "cards": [("📚 六册攻略", "两艘船单列，四幕陆地区域分别整理。"), ("⚠️ 五大节点", "每个不可返回点都有离章检查表。"), ("🧭 双重编号", "同时说明玩家 Act 称呼与游戏日志 Chapter。"), ("🎮 适用版本", "以 Definitive Edition 与四遗物内容为准。")],
    },
}

OUT_MAP = {name: data["out"] for name, data in GUIDES.items()}
OUT_MAP["神界原罪2-欢乐堡全任务隐藏内容详尽攻略.md"] = "神界原罪2-欢乐堡全任务隐藏内容详尽攻略-增强版.html"


def plain(text):
    text = re.sub(r"\[([^]]+)]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`>#]", "", text)
    return text.strip()


def slugify(text, used):
    slug = plain(text).lower()
    slug = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "-", slug).strip("-") or "section"
    base, n = slug, 2
    while slug in used:
        slug = f"{base}-{n}"
        n += 1
    used.add(slug)
    return slug


def inline(text):
    stash = []

    def link_sub(match):
        label, href = match.group(1), match.group(2)
        href = OUT_MAP.get(href, href)
        token = f"\x00{len(stash)}\x00"
        target = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        stash.append(f'<a href="{escape(href, quote=True)}"{target}>{escape(label)}</a>')
        return token

    text = re.sub(r"\[([^]]+)]\(([^)]+)\)", link_sub, text)
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*", r"<em>\1</em>", text)
    for i, value in enumerate(stash):
        text = text.replace(escape(f"\x00{i}\x00"), value)
    return text


SEMANTIC = [
    (("任务", "索引"), "📜", "quest"), (("路线",), "🧭", "quest"), (("检查",), "✅", "quest"),
    (("误区",), "🚫", "danger"), (("避坑",), "⚠️", "danger"), (("资料来源",), "📚", "source"),
    (("队友",), "👥", "talk"), (("起源角色",), "👥", "talk"), (("永久", "属性"), "📈", "reward"),
    (("复仇女神",), "⛵", "quest"), (("梅里威瑟",), "🚢", "quest"), (("船", "战"), "⚔️", "fight"),
    (("mordus",), "🕳️", "fight"), (("漂流之森",), "🏘️", "quest"), (("石园",), "🪦", "hidden"),
    (("黑井",), "🔥", "fight"), (("锯木厂",), "🪵", "fight"), (("血月岛",), "🌑", "hidden"),
    (("源力导师",), "✨", "quest"), (("仪式",), "🕯️", "quest"), (("动物",), "🐾", "animal"),
    (("academy",), "🏛️", "hidden"), (("学院",), "🏛️", "hidden"), (("祭坛",), "🛕", "hidden"),
    (("lunar gate",), "🌙", "hidden"), (("arena",), "🏟️", "fight"), (("shadow prince",), "🦂", "talk"),
    (("mother tree",), "🌳", "talk"), (("sallow",), "💀", "fight"), (("alexander",), "⚔️", "talk"),
    (("swornbreaker",), "🗡️", "reward"), (("kumm",), "🖼️", "hidden"), (("kemm",), "🖼️", "hidden"),
    (("doctor",), "😈", "fight"), (("deathfog",), "☠️", "danger"), (("死亡之雾",), "☠️", "danger"),
    (("path of blood",), "🩸", "hidden"), (("crypt",), "⚰️", "hidden"), (("lucian",), "☀️", "quest"),
    (("遗物",), "🐉", "reward"), (("吞噬者",), "🐲", "reward"), (("污染套",), "🌿", "reward"),
    (("lohse",), "🎶", "talk"), (("洛思",), "🎶", "talk"), (("red prince",), "🐉", "talk"),
    (("猩红王子",), "🐉", "talk"), (("sebille",), "🗡️", "talk"), (("希贝尔",), "🗡️", "talk"),
    (("fane",), "💀", "talk"), (("费恩",), "💀", "talk"), (("ifan",), "🐺", "talk"),
    (("beast",), "⛵", "talk"), (("比斯特",), "⛵", "talk"), (("谜题",), "🧩", "hidden"),
    (("隐藏",), "🕵️", "hidden"), (("战斗",), "⚔️", "fight"), (("奖励",), "🎁", "reward"),
]


def semantic(text, level=2):
    t = plain(text).lower()
    for keys, icon, kind in SEMANTIC:
        if all(k in t for k in keys):
            return icon, kind
    fallbacks = {2: ("📖", "quest"), 3: ("🔹", "quest"), 4: ("▫️", "quest")}
    return fallbacks.get(level, ("📌", "quest"))


def parse_markdown(md):
    lines = md.splitlines()
    used = set()
    headings = []
    out = []
    i = 0
    list_type = None

    def close_list():
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            close_list()
            i += 1
            continue
        if line.startswith("---") and set(line) <= {"-", " "}:
            close_list(); out.append("<hr>"); i += 1; continue
        hm = re.match(r"^(#{1,4})\s+(.+)$", line)
        if hm:
            close_list()
            level = len(hm.group(1)); raw = hm.group(2)
            sid = slugify(raw, used)
            icon, kind = semantic(raw, level)
            headings.append((level, sid, plain(raw), icon))
            out.append(f'<h{level} id="{sid}" data-kind="{kind}"><span class="h-icon" aria-hidden="true">{icon}</span>{inline(raw)}</h{level}>')
            i += 1; continue
        if line.startswith(">"):
            close_list()
            parts = []
            while i < len(lines) and lines[i].startswith(">"):
                content = lines[i][1:].lstrip()
                if content:
                    parts.append(inline(content))
                i += 1
            out.append("<blockquote>" + "<br>".join(parts) + "</blockquote>")
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-+", lines[i + 1]):
            close_list()
            headers = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in headers)
            trs = []
            for row in rows:
                row += [""] * (len(headers) - len(row))
                trs.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row[:len(headers)]) + "</tr>")
            out.append('<div class="table-wrap"><table><thead><tr>' + th + "</tr></thead><tbody>" + "".join(trs) + "</tbody></table></div>")
            continue
        lm = re.match(r"^\s*(-|\d+\.)\s+(.+)$", line)
        if lm:
            marker, body = lm.group(1), lm.group(2)
            wanted = "ol" if marker[0].isdigit() else "ul"
            if list_type != wanted:
                close_list(); out.append(f'<{wanted} class="task-list">'); list_type = wanted
            cb = re.match(r"^\[([ xX])]\s*(.*)$", body)
            if cb:
                checked = " checked" if cb.group(1).lower() == "x" else ""
                icon, _ = semantic(cb.group(2), 3)
                out.append(f'<li><label><input type="checkbox"{checked}><span class="check-icon">{icon}</span><span>{inline(cb.group(2))}</span></label></li>')
            else:
                out.append(f"<li>{inline(body)}</li>")
            i += 1; continue
        close_list()
        paras = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].rstrip()
            if not nxt or nxt.startswith(("#", ">", "|", "---")) or re.match(r"^\s*(-|\d+\.)\s+", nxt):
                break
            paras.append(nxt); i += 1
        out.append("<p>" + inline(" ".join(paras)) + "</p>")
    close_list()
    return "\n".join(out), headings


CSS = r'''
*{box-sizing:border-box}html{scroll-behavior:smooth}body{--ink:#eaf1f5;--muted:#aebdca;--green:#7ee0ad;--blue:#88caff;--gold:#f2c767;--violet:#c59cff;--danger:#f08178;margin:0;color:var(--ink);font:16px/1.75 system-ui,-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:radial-gradient(circle at 15% 0,#193943 0,transparent 26rem),radial-gradient(circle at 95% 20%,#34224b 0,transparent 28rem),#0c1218;background-attachment:fixed}body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.22;background-image:linear-gradient(#ffffff05 1px,transparent 1px),linear-gradient(90deg,#ffffff05 1px,transparent 1px);background-size:32px 32px}main{position:relative;max-width:1220px;margin:auto;padding:30px 28px 70px}.hero{position:relative;overflow:hidden;padding:34px 38px;margin-bottom:18px;border:1px solid #5a777c;border-radius:22px;background:linear-gradient(135deg,#1d4744ee,#1d3045ee 58%,#34264bee);box-shadow:0 20px 50px #0007}.hero>*{position:relative;z-index:2}.eyebrow{font-size:.78rem;letter-spacing:.18em;color:#a9f2ca;font-weight:800}.hero h1{max-width:930px;margin:.25rem 0 .5rem;font-size:clamp(2rem,4.2vw,3.25rem);line-height:1.16}.hero p{max-width:860px;margin:.4rem 0;color:#cbd9e2}.hero-orbit{position:absolute;inset:0;z-index:1!important;opacity:.28;pointer-events:none}.hero-orbit span{position:absolute;font-size:clamp(1.3rem,3vw,2.5rem);filter:drop-shadow(0 5px 8px #0008);animation:drift 5s ease-in-out infinite}.hero-orbit span:nth-child(1){right:4%;top:12%}.hero-orbit span:nth-child(2){right:16%;bottom:12%;animation-delay:-1s}.hero-orbit span:nth-child(3){right:29%;top:15%;animation-delay:-2s}.hero-orbit span:nth-child(4){right:40%;bottom:8%;animation-delay:-3s}@keyframes drift{50%{transform:translateY(-9px) rotate(6deg)}}.quick-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0}.quick-card{padding:15px;border:1px solid #496677;border-radius:14px;background:linear-gradient(145deg,#203746dd,#15212bdd);box-shadow:0 10px 24px #0004;transition:.18s}.quick-card:hover{transform:translateY(-3px);border-color:#8ac7ff}.quick-card b{display:block;margin-bottom:3px;color:#fff}.quick-card span{display:block;color:#b9c8d2;font-size:.9rem;line-height:1.5}.legend{display:flex;flex-wrap:wrap;gap:7px;margin:15px 0}.chip{padding:4px 9px;border:1px solid #4b6271;border-radius:999px;background:#17242d;color:#c6d4dc;font-size:.84rem}.route{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:7px;margin:16px 0 24px;padding:11px;border:1px dashed #526d7a;border-radius:13px;background:#101b22}.stop{padding:4px 8px;border-radius:8px;background:#1a2b35;color:#d6e2e7}.arrow{color:var(--green);font-weight:900}.layout{display:grid;grid-template-columns:285px minmax(0,1fr);gap:24px}.toc{position:sticky;top:18px;align-self:start;max-height:calc(100vh - 36px);overflow:auto;padding:18px 16px;border:1px solid #344653;border-radius:16px;background:#111b24e8;box-shadow:0 16px 42px #0005}.toc h2{margin:0 0 10px;border:0;padding:0;color:var(--green);font-size:1rem}.toc ul{list-style:none;margin:0;padding:0}.toc li{margin:2px 0}.toc .l3{padding-left:14px;font-size:.9rem}.toc a{display:block;padding:2px 5px;border-radius:6px;color:#aebdca;text-decoration:none}.toc a:hover{color:#fff;background:#20313d}.toc-emoji{display:inline-block;width:1.55em;text-align:center}article{min-width:0;padding:30px 35px;border:1px solid #2b3b47;border-radius:18px;background:#101820eb;box-shadow:0 20px 50px #0004}article>h1{display:none}h2,h3,h4{scroll-margin-top:24px;line-height:1.35}.h-icon{display:inline-block;min-width:1.55em;text-align:center;margin-right:.2em;filter:drop-shadow(0 3px 4px #0007)}h2{margin:2.1em 0 .8em;padding:0 0 8px;border-bottom:1px solid #344955;color:var(--green)}h3{margin:1.6em 0 .7em;padding:8px 11px;border-left:3px solid #527589;border-radius:7px;color:var(--blue);background:linear-gradient(90deg,#1a2b38aa,transparent 78%)}h3[data-kind="fight"]{border-color:var(--danger)}h3[data-kind="reward"]{border-color:var(--violet)}h3[data-kind="talk"]{border-color:var(--blue)}h3[data-kind="hidden"]{border-color:#c59cff}h3[data-kind="danger"]{border-color:var(--danger)}p{margin:0 0 1em}a{color:#8bd0ff}strong{color:#fff}code{padding:.1em .35em;border:1px solid #40505d;border-radius:5px;background:#091016;color:#f2d78d}blockquote{position:relative;margin:1.15em 0;padding:12px 17px 12px 48px;border-left:5px solid var(--gold);border-radius:8px;background:linear-gradient(90deg,#4a3b205c,#17242d);color:#d4dedf}blockquote:before{content:"📌";position:absolute;left:14px;top:11px;font-size:1.25rem}ul,ol{margin:0 0 1em;padding-left:1.5em}li{margin:.24em 0}li label{display:flex;align-items:flex-start;gap:.45em;padding:4px 6px;border-radius:7px}li label:hover{background:#1b2b36}input{margin-top:.46em;accent-color:var(--green)}.check-icon{min-width:1.45em;text-align:center}.table-wrap{overflow:auto;margin:1.1em 0 1.55em;border-radius:11px;box-shadow:0 8px 25px #0004}table{width:100%;min-width:610px;border-collapse:collapse;background:#131e27}th,td{padding:9px 11px;border:1px solid #344653;text-align:left;vertical-align:top}th{position:sticky;top:0;background:#263b49;color:#fff}tr:nth-child(even) td{background:#182630}hr{border:0;border-top:1px solid #344653;margin:2em 0}.progress{position:fixed;z-index:30;left:0;top:0;height:4px;width:0;background:linear-gradient(90deg,var(--green),var(--blue),var(--violet));box-shadow:0 0 13px var(--blue)}.backtop{position:fixed;z-index:30;right:22px;bottom:22px;padding:10px 13px;border:1px solid #5e7c8b;border-radius:999px;background:#182832e8;color:#fff;text-decoration:none;box-shadow:0 8px 24px #0007;opacity:0;pointer-events:none;transition:.2s}.backtop.show{opacity:1;pointer-events:auto}.footer{max-width:1220px;margin:0 auto 24px;padding:0 28px;color:#94a5b1;font-size:.88rem}@media(max-width:900px){main{padding:16px 12px 60px}.hero{padding:28px 22px}.quick-grid{grid-template-columns:repeat(2,1fr)}.layout{display:block}.toc{position:static;max-height:420px;margin-bottom:16px}article{padding:22px 18px}}@media(max-width:540px){.quick-grid{grid-template-columns:1fr}.route{justify-content:flex-start}.arrow{transform:rotate(90deg)}.hero-orbit span:nth-child(n+3){display:none}}@media print{body{background:#fff;color:#111}body:before,.progress,.backtop,.quick-grid,.legend,.route,.hero-orbit{display:none}.hero,article{background:#fff;border:0;box-shadow:none}.toc{display:none}.layout{display:block}h2,h3{color:#111}a{color:#111;text-decoration:underline}}
'''


def build_page(src_name, cfg):
    md_path = ROOT / src_name
    md = md_path.read_text(encoding="utf-8")
    article, headings = parse_markdown(md)
    title = plain(re.search(r"^#\s+(.+)$", md, re.M).group(1))
    toc_items = []
    for level, sid, label, icon in headings:
        if level not in (2, 3):
            continue
        cls = "l3" if level == 3 else "l2"
        toc_items.append(f'<li class="{cls}"><a href="#{sid}"><span class="toc-emoji">{icon}</span>{escape(label)}</a></li>')
    cards = "".join(f'<div class="quick-card"><b>{escape(head)}</b><span>{escape(desc)}</span></div>' for head, desc in cfg["cards"])
    route = "".join(("" if i == 0 else '<span class="arrow">➜</span>') + f'<span class="stop">{escape(stop)}</span>' for i, stop in enumerate(cfg["route"]))
    html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{escape(cfg['subtitle'], quote=True)}"><title>{escape(title)}</title><style>{CSS}</style></head>
<body id="top"><div class="progress"></div><main>
<section class="hero"><div class="eyebrow">{escape(cfg['eyebrow'])}</div><h1>{escape(title)}</h1><p>{escape(cfg['subtitle'])}</p><p>终极版 / Definitive Edition｜任务分支、隐藏内容、永久收益、跨章影响与离章检查表。</p><div class="hero-orbit" aria-hidden="true"><span>🗺️</span><span>⚔️</span><span>✨</span><span>🎒</span></div></section>
<div class="quick-grid">{cards}</div>
<div class="legend"><span class="chip">📌 主线</span><span class="chip">🗣️ 对话</span><span class="chip">⚔️ 战斗</span><span class="chip">🕵️ 隐藏</span><span class="chip">🎁 奖励</span><span class="chip">⚠️ 易错过</span><span class="chip">🧩 解谜</span><span class="chip">🐾 动物</span></div>
<div class="route">{route}</div>
<div class="layout"><nav class="toc"><h2>🧭 本章目录</h2><ul>{''.join(toc_items)}</ul></nav><article>{article}</article></div>
</main><div class="footer">由同目录 Markdown 生成；网页完全离线可用。章节内外链已自动对应到 HTML 版本。</div>
<a class="backtop" href="#top" aria-label="返回顶部">⬆️</a>
<script>const bar=document.querySelector('.progress'),topBtn=document.querySelector('.backtop');function ui(){{const d=document.documentElement,p=d.scrollTop/Math.max(1,d.scrollHeight-d.clientHeight)*100;bar.style.width=Math.max(0,Math.min(100,p))+'%';topBtn.classList.toggle('show',d.scrollTop>500)}}addEventListener('scroll',ui,{{passive:true}});ui();</script>
</body></html>'''
    HTMLParser().feed(html)
    out_path = ROOT / cfg["out"]
    out_path.write_text(html, encoding="utf-8")
    return out_path, len(headings), html.count("<table")


if __name__ == "__main__":
    for source, config in GUIDES.items():
        path, headings, tables = build_page(source, config)
        print(f"{path.name}: {path.stat().st_size} bytes, {headings} headings, {tables} tables")
