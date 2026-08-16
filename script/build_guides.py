from pathlib import Path
from html import escape
from html.parser import HTMLParser
import re

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
MD_DIR = PROJECT_ROOT / "md"
HTML_DIR = PROJECT_ROOT / "html"

GUIDES = {
    "神界原罪2-序章梅里威瑟号全任务隐藏内容攻略.md": {
        "out": "神界原罪2-序章梅里威瑟号全任务隐藏内容攻略-增强版.html",
        "eyebrow": "CHAPTER 1 · THE MERRYWEATHER",
        "subtitle": "4 区完整序章｜教学舱、谋杀调查、六起源初见、灾后二次搜刮与返舱救援",
        "route": ["📦 01 教学舱", "🛏️ 02 Finn 案", "💥 03 受损船舱", "🪲 04 甲板返救"],
        "cards": [
            ("📜 2+1 条日志线", "Troubled Waters、The Collar，另完整收录 Death Belowdecks。"),
            ("🎁 免费技能", "精灵吃 Finn 的 Chunk of Flesh 可永久学会 Adrenaline。"),
            ("👥 六名起源初见", "爆发前逐一交谈，灾后返舱还会出现第二轮救援对白。"),
            ("⚠️ 不可返回", "登上救生艇或完成最后救援后，梅里威瑟号永久关闭。"),
            ("🛏️ 三张床卷", "序章就应至少带走一张并放入快捷栏。"),
            ("💀 特殊玩法", "死亡之雾桶依赖抢时间或负重规划，不属于默认路线。"),
        ],
    },
    "神界原罪2-复仇女神号航船间章全任务隐藏内容攻略.md": {
        "out": "神界原罪2-复仇女神号航船间章全任务隐藏内容攻略-增强版.html",
        "eyebrow": "INTERLUDE · LADY VENGEANCE",
        "subtitle": "9 阶段跨章营地｜夺船、永久队伍、Dallis 舱房、船战与阿克斯灵体船",
        "cards": [
            ("📜 2 条航船主线", "Lady o' War 与 To the Hall of Echoes；后续继续承接多章长线。"),
            ("👥 永久队伍", "第一次回音大厅结束后四人队锁定，未选起源角色永久不可招募。"),
            ("📚 限时技能商人", "Simone、Exter、Samadel 等会在船战后消失，启航前必须采购。"),
            ("⚔️ 船战目标", "真正胜利条件是守住 Malady 五回合；逼退 Dallis 另有条件独占奖励。"),
            ("🔺 两枚金字塔", "红色在 Dallis 舱房，蓝色在秘密底舱，都是跨章核心工具。"),
            ("🪞 跨章服务", "魔镜、仓库、雇佣兵、Corbin 与 Arx 回音大厅均在本篇统一说明。"),
        ],
        "route_title": "复仇女神号跨章路线图",
        "route_hint": "按首次夺船、回音大厅与后续回船时点推进",
        "route_groups": [
            ("首次夺船 · Lv8–9", ["⚓ 01 主甲板", "🪞 02 重组", "🔐 03 舱房", "🎵 04 唤醒", "⚔️ 05 船战"]),
            ("回音大厅 · Lv9", ["🌀 06 Bless 神祇"]),
            ("跨章营地 · Lv9–18", ["🌊 07 死神海岸", "🏝️ 08 无名岛", "🛠️ 09 Arena 前", "🌙 10 Arena 后夜谈"]),
            ("终章营地 · Lv18+", ["🏙️ 11 Arx 灵体船"]),
        ],
        "legend": ["📌 必做", "⚠️ 不可逆", "🐾 Pet Pal", "👥 起源专属", "📚 技能书", "🎁 唯一装备", "🌟 永久奖励", "📦 跨章物品"],
    },
    "神界原罪2-欢乐堡全任务隐藏内容详尽攻略.md": {
        "out": "神界原罪2-欢乐堡全任务隐藏内容详尽攻略-增强版.html",
        "eyebrow": "ACT I · FORT JOY",
        "subtitle": "16 区逃岛路线｜27 条任务基线、十系商人、六起源顺序、四遗物与离岛扫尾",
        "cards": [
            ("📜 27 条正式任务", "另收录 The Collar、Nothing But Child's Play、六起源日志与跨章长线。"),
            ("🗺️ 16 个自然区域", "从 Lv1 登陆海滩到 Lv8 亚历山大决战，按堡内、沼泽与终战分段。"),
            ("📚 十系技能商人", "欢乐堡与阿玛迪亚圣所均有采购节点，并标明逃堡或推进后的商人变化。"),
            ("👥 共享对话顺序", "Red Prince、Sebille、Stingtail 与 Griff 必须按顺序处理，避免永久丢失角色内容。"),
            ("🐉 四遗物开端", "Captain、Devourer、Contamination 与 Vulture 线索均纳入本章检查。"),
            ("⚠️ 离岛硬锁", "接受 Malady 送往复仇女神号后，欢乐堡岛永久关闭。"),
        ],
        "route_title": "欢乐堡区域路线图",
        "route_hint": "按推荐等级从堡内推进至空洞沼泽与码头终战",
        "route_groups": [
            ("堡内 · Lv1–4", ["🏖️ 01 海滩", "🏘️ 02 广场", "🍲 03 南区", "🕳️ 04 精灵洞", "🐊 05 鳄鱼", "🏟️ 06 竞技场"]),
            ("逃堡 · Lv4–5", ["🔒 07 拘留区", "🏰 08 城堡 / 码头"]),
            ("沼泽 · Lv5–7", ["⛺ 09 圣所", "🌫️ 10 北岸", "🗝️ 11 宝库", "🔥 12 军械库", "🐉 13 Slane"]),
            ("离岛 · Lv6–8", ["🧩 14 迷宫 / 塔", "⛺ 15 废弃营地", "⚔️ 16 Alexander"]),
        ],
        "legend": ["📌 必做", "⚠️ 不可逆", "👻 Spirit Vision", "🐾 Pet Pal", "🧝 Elf", "👥 起源专属", "📚 技能书", "🎁 唯一装备", "🌟 永久奖励", "📦 跨章物品"],
    },
    "神界原罪2-第二章死神海岸全任务隐藏内容详尽攻略.md": {
        "out": "神界原罪2-第二章死神海岸全任务隐藏内容详尽攻略-增强版.html",
        "eyebrow": "ACT II · REAPER'S COAST",
        "subtitle": "17 区自然探索路线｜推荐等级、实走顺序、任务锁点、唯一装备与全内容检查",
        "cards": [
            ("🗺️ 17 个区域", "从 Lv9 登陆到 Lv16–17 离岛，按自然等级曲线拆分。"),
            ("📚 10 系技能书", "Ovis、Bree、Haran、Papa Thrash 覆盖全部基础学派。"),
            ("⚠️ 三个硬锁", "Peeper Egg、Ninyan 唯一斧、Malady 启航都不可逆。"),
            ("👻 灵视回查", "首次仪式后回查车队五魂、鲨鱼、鸡舍与锡瓦学徒。"),
            ("🎁 本区唯一装备", "Hanal Lechet、Ninyan's Axe 与 Fingal Lv11 唯一弓。"),
            ("🧬 内容优先级", "剧情完整度 > 后续内容 > 唯一奖励 > 正常经验 > 金币。"),
        ],
        "route_title": "死神海岸区域路线图",
        "route_hint": "按推荐等级由南向北推进",
        "route_groups": [
            ("序段 · Lv9–10", ["🚢 00 船上", "🏖️ 01 登陆", "🏘️ 02 镇内", "🍺 03 酒馆", "🌉 04 东桥"]),
            ("西南 · Lv10–12", ["🌊 05 西郊", "🕳️ 06 Mordus", "🪦 07 石园", "🐄 08 农田"]),
            ("东南 · Lv12–14", ["🌲 09 回廊", "🛡️ 10 桥头", "🏚️ 11 黑井村", "⛏️ 12 矿洞", "☠️ 13 天堂丘"]),
            ("北部 · Lv14–17", ["🪵 14 锯木厂", "🔥 15 Boss", "🌑 16 血月岛", "⛵ 17 扫尾"]),
        ],
        "legend": ["📌 必做", "⚠️ 不可逆", "👻 Spirit Vision", "🐾 Pet Pal", "🧝 Elf", "👥 起源专属", "📚 技能书", "🎁 唯一装备", "🌟 永久奖励", "📦 跨章物品"],
    },
    "神界原罪2-第三章无名岛全任务隐藏内容详尽攻略.md": {
        "out": "神界原罪2-第三章无名岛全任务隐藏内容详尽攻略-增强版.html",
        "eyebrow": "ACT III · THE NAMELESS ISLE",
        "subtitle": "10 区升神路线｜17 条任务、七神祭坛、双阵营、学院与永久属性",
        "cards": [
            ("📜 17 条正式任务", "另纳入六名起源角色、Swornbreaker、两封阿克斯信与四遗物长线。"),
            ("☀️🌙 七神祭坛", "先亲自祈祷七座祭坛，再从阵营首领取整套答案，避免成就被提前关闭。"),
            ("🗣️ 双起源顺序", "Red Prince 必须先谈 Shadow Prince，再让 Sebille 完成复仇。"),
            ("📈 六项永久课程", "学院教师提供 +5 / -5 属性交换；每种课程全队只能领取一次。"),
            ("📚 十系技能商人", "黑环南营与精灵神殿合计覆盖全部常规战斗学派。"),
            ("⚠️ 最终节点", "向 Eternal Arbiter 确认准备完成后，无名岛与正常船上采购永久关闭。"),
        ],
        "route_title": "无名岛区域路线图",
        "route_hint": "先完成七神祭坛与阵营内容，再进入学院",
        "route_groups": [
            ("南部 · Lv16", ["🚢 00 船上", "☁️ 01 Amadia", "🐉 02 蜥蜴神殿"]),
            ("中西部 · Lv16–17", ["🪨 03 Duna / Rhalic", "🌊 04 Vrogir", "⏱️ 05 Xantezza"]),
            ("北部 · Lv17–18", ["🌳 06 精灵神殿", "🕳️ 07 苍白人 / 月之门"]),
            ("学院 · Lv17–18", ["🏛️ 08 Academy", "🔥 09 Arena of the One"]),
        ],
        "legend": ["📌 必做", "⚠️ 不可逆", "👻 Spirit Vision", "🐾 Pet Pal", "🧝 Elf", "👥 起源专属", "📚 技能书", "🎁 唯一装备", "🌟 永久奖励", "📦 跨章物品"],
    },
    "神界原罪2-第四章阿克斯全任务隐藏内容详尽攻略.md": {
        "out": "神界原罪2-第四章阿克斯全任务隐藏内容详尽攻略-增强版.html",
        "eyebrow": "ACT IV · ARX",
        "subtitle": "14 区终局路线｜Deathfog、Kemm、Doctor、领事馆、Lucian 墓穴与多结局",
        "cards": [
            ("📜 20+1 条正式任务", "Chapter 6 共 20 条；进入墓穴后由 End Times 收束 Chapter 7。"),
            ("☠️ 最大避坑", "Deathfog 必须排入海中；排进 Arx 会清空大量 NPC、商店与任务。"),
            ("🖼️ 主线枢纽", "Kemm Vault 关联两幅机关画、Arhu、Swornbreaker、Kemm 真相与吞噬者头盔。"),
            ("👥 三条大型队友线", "Lohse / Doctor、Beast / Justinia、Red Prince / Sadha 都在进墓穴前结算。"),
            ("📚 十系技能补给", "City Square 与教堂东南商人覆盖全部常规战斗学派。"),
            ("🐉 四遗物终章", "污染套与吞噬者套在 Arx 完成最终形态和独立终战。"),
        ],
        "route_title": "阿克斯区域路线图",
        "route_hint": "先清外围与城区，再收束四条终局任务线",
        "route_groups": [
            ("外围 · Lv18–19", ["🏚️ 00 坠毁", "🏕️ 01 朝圣营", "⚓ 02 港口", "⚔️ 03 城门"]),
            ("城区 · Lv19", ["🏰 04 兵营", "🏫 05 学校教堂", "💍 06 西城区", "🕳️ 07 北下水道"]),
            ("主线收束 · Lv19–21", ["☠️ 08 Isbeil", "🖼️ 09 Kemm Vault", "🐉 10 领事馆", "😈 11 Doctor"]),
            ("终局 · Lv20–21", ["🧾 12 全城扫尾", "⛪ 13 Lucian 墓穴"]),
        ],
        "legend": ["📌 必做", "⚠️ 不可逆", "👻 Spirit Vision", "🐾 Pet Pal", "🧝 Elf", "👥 起源专属", "📚 技能书", "🎁 唯一装备", "🌟 永久奖励", "📦 跨章物品"],
    },
    "神界原罪2-全章节详尽攻略索引.md": {
        "out": "神界原罪2-全章节详尽攻略索引.html",
        "eyebrow": "DEFINITIVE EDITION · COMPLETE GUIDE",
        "subtitle": "从梅里威瑟号到 Lucian 墓穴｜独立分章、跨章航船与永久节点索引",
        "route": ["🚢 序章", "🏰 欢乐堡", "⛵ 航船间章", "🌊 死神海岸", "🏝️ 无名岛", "🏙️ 阿克斯"],
        "cards": [("📚 六册攻略", "两艘船单列，四幕陆地区域分别整理。"), ("⚠️ 五大节点", "每个不可返回点都有离章检查表。"), ("🧭 双重编号", "同时说明玩家 Act 称呼与游戏日志 Chapter。"), ("🎮 适用版本", "以 Definitive Edition 与四遗物内容为准。")],
        "route_title": "全章节推荐路线",
        "route_hint": "按剧情顺序进入各册；航船篇同时承担跨章营地索引",
        "route_groups": [
            ("完整旅程 · Lv1–21", ["🚢 序章", "🏰 欢乐堡", "⛵ 航船间章", "🌊 死神海岸", "🏝️ 无名岛", "🏙️ 阿克斯"]),
        ],
        "legend": ["🗺️ 区域路线", "📜 正式任务", "⚠️ 不可逆", "👥 起源专属", "🐾 Pet Pal", "👻 Spirit Vision", "🎁 唯一装备", "🌟 永久奖励", "📦 跨章物品"],
    },
}

OUT_MAP = {name: data["out"] for name, data in GUIDES.items()}


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


def inline(text, enhanced=False):
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

    def tag_sub(match):
        label = match.group(1)
        low = label.lower()
        if any(k in low for k in ("不可逆", "会锁", "暂时不要", "先存档", "等级较高", "不要卖")):
            kind = "danger"
        elif any(k in low for k in ("唯一装备", "永久奖励", "永久能力", "relics")):
            kind = "reward"
        elif any(k in low for k in ("spirit vision", "灵视")):
            kind = "ghost"
        elif any(k in low for k in ("pet pal", "动物")):
            kind = "animal"
        elif any(k in low for k in ("专属", "ifan", "beast", "lohse", "fane", "sebille")):
            kind = "origin"
        elif any(k in low for k in ("跨章", "elf", "corpse eater")):
            kind = "cross"
        elif any(k in low for k in ("必做", "容易漏")):
            kind = "must"
        else:
            kind = "info"
        return f'<span class="tag tag-{kind}">【{label}】</span>'

    if enhanced:
        text = re.sub(r"【([^】]+)】", tag_sub, text)
    for i, value in enumerate(stash):
        text = text.replace(escape(f"\x00{i}\x00"), value)
    return text


SEMANTIC_V2 = [
    (("攻略使用说明",), "📖", "source"), (("区域划分",), "🗺️", "quest"), (("区域总表",), "🗺️", "quest"),
    (("开局能力",), "🧰", "reward"), (("第 01 区",), "🏖️", "quest"), (("区域卡",), "🎛️", "source"),
    (("传送点",), "🗿", "quest"), (("鲨鱼",), "🦈", "animal"), (("虚空虫",), "🪲", "fight"),
    (("失事车队",), "🛞", "hidden"), (("鸡舍",), "🐔", "animal"), (("吊刑架",), "🪓", "fight"),
    (("fingal boyd",), "🏹", "reward"), (("锡瓦家",), "🕯️", "quest"), (("灵视",), "👻", "hidden"),
    (("结算状态",), "📋", "source"), (("分支",), "⚖️", "talk"), (("checklist",), "✅", "quest"),
    (("漂流之森至离岛",), "🧭", "quest"),
    (("技能书购买点",), "📚", "reward"), (("条件商人",), "🧙", "reward"),
    (("技能书刷新",), "🔄", "reward"), (("重要 npc",), "👥", "talk"), (("购物路线",), "🛒", "reward"),
]

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


def semantic(text, level=2, enhanced=False):
    t = plain(text).lower()
    for keys, icon, kind in (SEMANTIC_V2 + SEMANTIC if enhanced else SEMANTIC):
        if all(k in t for k in keys):
            return icon, kind
    fallbacks = {2: ("📖", "quest"), 3: ("🔹", "quest"), 4: ("▫️", "quest")}
    return fallbacks.get(level, ("📌", "quest"))


def split_heading_icon(text):
    """Keep Markdown-authored emoji while avoiding a duplicate icon in HTML."""
    match = re.match(
        r"^([\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF](?:\uFE0F|\u200D[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]\uFE0F?)*)\s+(.+)$",
        text,
    )
    return (match.group(1), match.group(2)) if match else (None, text)


def parse_markdown(md, enhanced=False):
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
            explicit_icon, display_raw = split_heading_icon(raw) if enhanced else (None, raw)
            sid = slugify(display_raw, used)
            icon, kind = semantic(display_raw, level, enhanced)
            icon = explicit_icon or icon
            headings.append((level, sid, plain(display_raw), icon))
            out.append(f'<h{level} id="{sid}" data-kind="{kind}"><span class="h-icon" aria-hidden="true">{icon}</span>{inline(display_raw, enhanced)}</h{level}>')
            i += 1; continue
        if line.startswith(">"):
            close_list()
            parts = []
            while i < len(lines) and lines[i].startswith(">"):
                content = lines[i][1:].lstrip()
                if content:
                    parts.append(inline(content, enhanced))
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
            th = "".join(f"<th>{inline(c, enhanced)}</th>" for c in headers)
            trs = []
            for row in rows:
                row += [""] * (len(headers) - len(row))
                trs.append("<tr>" + "".join(f"<td>{inline(c, enhanced)}</td>" for c in row[:len(headers)]) + "</tr>")
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
                icon, _ = semantic(cb.group(2), 3, enhanced)
                out.append(f'<li><label><input type="checkbox"{checked}><span class="check-icon">{icon}</span><span>{inline(cb.group(2), enhanced)}</span></label></li>')
            else:
                out.append(f"<li>{inline(body, enhanced)}</li>")
            i += 1; continue
        close_list()
        paras = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].rstrip()
            if not nxt or nxt.startswith(("#", ">", "|", "---")) or re.match(r"^\s*(-|\d+\.)\s+", nxt):
                break
            paras.append(nxt); i += 1
        out.append("<p>" + inline(" ".join(paras), enhanced) + "</p>")
    close_list()
    return "\n".join(out), headings


CSS = r'''
*{box-sizing:border-box}html{scroll-behavior:smooth}body{--ink:#eaf1f5;--muted:#aebdca;--green:#7ee0ad;--blue:#88caff;--gold:#f2c767;--violet:#c59cff;--danger:#f08178;margin:0;color:var(--ink);font:16px/1.75 system-ui,-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:radial-gradient(circle at 15% 0,#193943 0,transparent 26rem),radial-gradient(circle at 95% 20%,#34224b 0,transparent 28rem),#0c1218;background-attachment:fixed}body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.22;background-image:linear-gradient(#ffffff05 1px,transparent 1px),linear-gradient(90deg,#ffffff05 1px,transparent 1px);background-size:32px 32px}main{position:relative;max-width:1220px;margin:auto;padding:30px 28px 70px}.hero{position:relative;overflow:hidden;padding:34px 38px;margin-bottom:18px;border:1px solid #5a777c;border-radius:22px;background:linear-gradient(135deg,#1d4744ee,#1d3045ee 58%,#34264bee);box-shadow:0 20px 50px #0007}.hero>*{position:relative;z-index:2}.eyebrow{font-size:.78rem;letter-spacing:.18em;color:#a9f2ca;font-weight:800}.hero h1{max-width:930px;margin:.25rem 0 .5rem;font-size:clamp(2rem,4.2vw,3.25rem);line-height:1.16}.hero p{max-width:860px;margin:.4rem 0;color:#cbd9e2}.hero-orbit{position:absolute;inset:0;z-index:1!important;opacity:.28;pointer-events:none}.hero-orbit span{position:absolute;font-size:clamp(1.3rem,3vw,2.5rem);filter:drop-shadow(0 5px 8px #0008);animation:drift 5s ease-in-out infinite}.hero-orbit span:nth-child(1){right:4%;top:12%}.hero-orbit span:nth-child(2){right:16%;bottom:12%;animation-delay:-1s}.hero-orbit span:nth-child(3){right:29%;top:15%;animation-delay:-2s}.hero-orbit span:nth-child(4){right:40%;bottom:8%;animation-delay:-3s}@keyframes drift{50%{transform:translateY(-9px) rotate(6deg)}}.quick-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0}.quick-card{padding:15px;border:1px solid #496677;border-radius:14px;background:linear-gradient(145deg,#203746dd,#15212bdd);box-shadow:0 10px 24px #0004;transition:.18s}.quick-card:hover{transform:translateY(-3px);border-color:#8ac7ff}.quick-card b{display:block;margin-bottom:3px;color:#fff}.quick-card span{display:block;color:#b9c8d2;font-size:.9rem;line-height:1.5}.legend{display:flex;flex-wrap:wrap;gap:7px;margin:15px 0}.chip{padding:4px 9px;border:1px solid #4b6271;border-radius:999px;background:#17242d;color:#c6d4dc;font-size:.84rem}.route{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:7px;margin:16px 0 24px;padding:11px;border:1px dashed #526d7a;border-radius:13px;background:#101b22}.stop{padding:4px 8px;border-radius:8px;background:#1a2b35;color:#d6e2e7}.arrow{color:var(--green);font-weight:900}.layout{display:grid;grid-template-columns:285px minmax(0,1fr);gap:24px}.toc{position:sticky;top:18px;align-self:start;max-height:calc(100vh - 36px);overflow:auto;padding:18px 16px;border:1px solid #344653;border-radius:16px;background:#111b24e8;box-shadow:0 16px 42px #0005}.toc h2{margin:0 0 10px;border:0;padding:0;color:var(--green);font-size:1rem}.toc ul{list-style:none;margin:0;padding:0}.toc li{margin:2px 0}.toc .l3{padding-left:14px;font-size:.9rem}.toc a{display:block;padding:2px 5px;border-radius:6px;color:#aebdca;text-decoration:none}.toc a:hover{color:#fff;background:#20313d}.toc-emoji{display:inline-block;width:1.55em;text-align:center}article{min-width:0;padding:30px 35px;border:1px solid #2b3b47;border-radius:18px;background:#101820eb;box-shadow:0 20px 50px #0004}article>h1{display:none}h2,h3,h4{scroll-margin-top:24px;line-height:1.35}.h-icon{display:inline-block;min-width:1.55em;text-align:center;margin-right:.2em;filter:drop-shadow(0 3px 4px #0007)}h2{margin:2.1em 0 .8em;padding:0 0 8px;border-bottom:1px solid #344955;color:var(--green)}h3{margin:1.6em 0 .7em;padding:8px 11px;border-left:3px solid #527589;border-radius:7px;color:var(--blue);background:linear-gradient(90deg,#1a2b38aa,transparent 78%)}h3[data-kind="fight"]{border-color:var(--danger)}h3[data-kind="reward"]{border-color:var(--violet)}h3[data-kind="talk"]{border-color:var(--blue)}h3[data-kind="hidden"]{border-color:#c59cff}h3[data-kind="danger"]{border-color:var(--danger)}p{margin:0 0 1em}a{color:#8bd0ff}strong{color:#fff}code{padding:.1em .35em;border:1px solid #40505d;border-radius:5px;background:#091016;color:#f2d78d}blockquote{position:relative;margin:1.15em 0;padding:12px 17px 12px 48px;border-left:5px solid var(--gold);border-radius:8px;background:linear-gradient(90deg,#4a3b205c,#17242d);color:#d4dedf}blockquote:before{content:"📌";position:absolute;left:14px;top:11px;font-size:1.25rem}ul,ol{margin:0 0 1em;padding-left:1.5em}li{margin:.24em 0}li label{display:flex;align-items:flex-start;gap:.45em;padding:4px 6px;border-radius:7px}li label:hover{background:#1b2b36}input{margin-top:.46em;accent-color:var(--green)}.check-icon{min-width:1.45em;text-align:center}.table-wrap{overflow:auto;margin:1.1em 0 1.55em;border-radius:11px;box-shadow:0 8px 25px #0004}table{width:100%;min-width:610px;border-collapse:collapse;background:#131e27}th,td{padding:9px 11px;border:1px solid #344653;text-align:left;vertical-align:top}th{position:sticky;top:0;background:#263b49;color:#fff}tr:nth-child(even) td{background:#182630}hr{border:0;border-top:1px solid #344653;margin:2em 0}.progress{position:fixed;z-index:30;left:0;top:0;height:4px;width:0;background:linear-gradient(90deg,var(--green),var(--blue),var(--violet));box-shadow:0 0 13px var(--blue)}.backtop{position:fixed;z-index:30;right:22px;bottom:22px;padding:10px 13px;border:1px solid #5e7c8b;border-radius:999px;background:#182832e8;color:#fff;text-decoration:none;box-shadow:0 8px 24px #0007;opacity:0;pointer-events:none;transition:.2s}.backtop.show{opacity:1;pointer-events:auto}.footer{max-width:1220px;margin:0 auto 24px;padding:0 28px;color:#94a5b1;font-size:.88rem}@media(max-width:900px){main{padding:16px 12px 60px}.hero{padding:28px 22px}.quick-grid{grid-template-columns:repeat(2,1fr)}.layout{display:block}.toc{position:static;max-height:420px;margin-bottom:16px}article{padding:22px 18px}}@media(max-width:540px){.quick-grid{grid-template-columns:1fr}.route{justify-content:flex-start}.arrow{transform:rotate(90deg)}.hero-orbit span:nth-child(n+3){display:none}}@media print{body{background:#fff;color:#111}body:before,.progress,.backtop,.quick-grid,.legend,.route,.hero-orbit{display:none}.hero,article{background:#fff;border:0;box-shadow:none}.toc{display:none}.layout{display:block}h2,h3{color:#111}a{color:#111;text-decoration:underline}}
'''

CSS_V2 = r'''
/* v2 reading interface */
.quick-grid{grid-template-columns:repeat(3,minmax(0,1fr))}.quick-card{position:relative;overflow:hidden;min-height:104px}.quick-card:after{content:"";position:absolute;inset:auto -28px -38px auto;width:92px;height:92px;border-radius:50%;background:#ffffff08}.quick-card b{font-size:1rem}.quick-card:hover{box-shadow:0 14px 30px #0006}.legend{padding:10px 12px;border:1px solid #304754;border-radius:13px;background:#101a21}.chip{transition:.18s}.chip:hover{color:#fff;border-color:#7897a8;background:#20323d}.route-map{margin:16px 0 24px;padding:15px;border:1px solid #3d5967;border-radius:16px;background:linear-gradient(145deg,#10202a,#101820);box-shadow:0 12px 30px #0004}.route-title{display:flex;align-items:center;justify-content:space-between;margin:0 0 11px;color:#eaf7f0;font-weight:800}.route-title small{color:#8197a5;font-weight:500}.route-phases{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.route-phase{padding:10px;border:1px solid #314854;border-radius:12px;background:#15232d}.phase-name{display:block;margin-bottom:7px;color:var(--gold);font-size:.78rem;font-weight:800;letter-spacing:.04em}.phase-stops{display:flex;flex-wrap:wrap;gap:5px}.phase-stop{padding:4px 7px;border:1px solid #36515f;border-radius:7px;background:#1b2e39;color:#d5e4e9;font-size:.82rem}.phase-stop.is-current{border-color:#77dca7;background:#183b33;color:#dffff0;box-shadow:0 0 0 1px #65d69a33 inset}.toc{padding-top:14px;scrollbar-width:thin;scrollbar-color:#4d7180 #111b24}.toc::-webkit-scrollbar,.table-wrap::-webkit-scrollbar{width:9px;height:9px}.toc::-webkit-scrollbar-track,.table-wrap::-webkit-scrollbar-track{background:#111b24}.toc::-webkit-scrollbar-thumb,.table-wrap::-webkit-scrollbar-thumb{border:2px solid #111b24;border-radius:999px;background:#4d7180}.toc::-webkit-scrollbar-thumb:hover,.table-wrap::-webkit-scrollbar-thumb:hover{background:#6b94a5}.toc-header{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:9px}.toc-header h2{margin:0}.toc-count{padding:2px 7px;border:1px solid #385361;border-radius:999px;color:#9fc8d7;font-size:.72rem;white-space:nowrap}.toc-tools{display:grid;grid-template-columns:1fr auto;gap:6px;margin-bottom:10px}.toc-search{min-width:0;width:100%;padding:7px 9px;border:1px solid #354b58;border-radius:8px;outline:none;background:#0c151c;color:#eaf1f5;font:inherit;font-size:.82rem}.toc-search:focus{border-color:#72c69a;box-shadow:0 0 0 2px #72c69a22}.toc-reset{padding:6px 8px;border:1px solid #4c5e68;border-radius:8px;background:#192832;color:#bacbd3;cursor:pointer}.toc-reset:hover{border-color:#d9877f;color:#fff}.toc a{border-left:2px solid transparent;transition:.15s}.toc a.active{border-left-color:var(--green);background:#1e3440;color:#fff}.toc li.filtered{display:none}.tag{display:inline-block;margin:.08em .12em .08em 0;padding:.03em .5em;border:1px solid;border-radius:999px;font-size:.78em;font-weight:800;line-height:1.7;vertical-align:.05em;white-space:nowrap}.tag-danger{color:#ffc0ba;border-color:#864a48;background:#4b2427}.tag-reward{color:#e7d1ff;border-color:#73569a;background:#37254f}.tag-ghost{color:#cfc7ff;border-color:#665f9c;background:#2d2b54}.tag-animal{color:#c7f3c5;border-color:#4e8050;background:#203f29}.tag-origin{color:#bde4ff;border-color:#47759a;background:#1e3850}.tag-cross{color:#ffe0a6;border-color:#8b6d37;background:#47371f}.tag-must{color:#fff3ae;border-color:#92803d;background:#4a4120}.tag-info{color:#c7dae3;border-color:#506976;background:#233640}h2[data-kind="danger"],h3[data-kind="danger"]{color:#ffaaa2}h2[data-kind="reward"],h3[data-kind="reward"]{color:#dbc2ff}h2[data-kind="hidden"],h3[data-kind="hidden"]{color:#d8c7ff}h2[data-kind="animal"],h3[data-kind="animal"]{color:#b7ebb6}ol.task-list{counter-reset:route-step;list-style:none;padding:0}ol.task-list>li{position:relative;margin:.55em 0;padding:10px 13px 10px 48px;border:1px solid #2d424e;border-radius:10px;background:linear-gradient(90deg,#172630,#111b23)}ol.task-list>li:before{counter-increment:route-step;content:counter(route-step);position:absolute;left:12px;top:10px;display:grid;place-items:center;width:25px;height:25px;border:1px solid #568171;border-radius:50%;background:#1a3932;color:#bff4d5;font-size:.78rem;font-weight:900}ul.task-list>li{padding-left:.15em}.table-wrap{position:relative;border:1px solid #304551;scrollbar-width:thin;scrollbar-color:#4d7180 #111b24}.table-wrap table tbody td:first-child{min-width:96px;color:#e7f4f7;font-weight:700}.table-wrap table tbody tr:hover td{background:#20313b}.reading-status{display:flex;align-items:center;gap:8px;margin:0 0 14px;padding:8px 10px;border:1px solid #304754;border-radius:10px;background:#101a21;color:#aebfca;font-size:.82rem}.reading-status strong{color:#a9f2ca}.draft-note{margin:12px 0 18px;padding:12px 15px;border:1px solid #775d35;border-radius:11px;background:linear-gradient(90deg,#4a361f99,#17242d);color:#ecd6a4}.footer{display:flex;justify-content:space-between;gap:14px}.footer .build-note{color:#6f8490}
@media(max-width:1050px){.route-phases{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:900px){.quick-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.toc-tools{position:sticky;top:0;z-index:3;padding:5px 0;background:#111b24}.toc a{padding:5px 6px}.route-phases{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:540px){.quick-grid{grid-template-columns:1fr}.route-phases{grid-template-columns:1fr}.route-title{align-items:flex-start;flex-direction:column}.quick-card{min-height:auto}.tag{white-space:normal}.footer{display:block}.table-wrap:before{content:"↔ 可横向滑动";display:block;padding:5px 8px;color:#8fa4af;font-size:.72rem;background:#101a21}}
@media print{.toc-tools,.reading-status{display:none}.tag{border-color:#777;color:#111;background:#fff}.route-map{display:none}ol.task-list>li{break-inside:avoid;background:#fff}}
'''


def build_page(src_name, cfg):
    md_path = MD_DIR / src_name
    md = md_path.read_text(encoding="utf-8")
    article, headings = parse_markdown(md, bool(cfg.get("route_groups")))
    title = plain(re.search(r"^#\s+(.+)$", md, re.M).group(1))
    toc_items = []
    for level, sid, label, icon in headings:
        if level not in (2, 3):
            continue
        cls = "l3" if level == 3 else "l2"
        toc_items.append(f'<li class="{cls}"><a href="#{sid}"><span class="toc-emoji">{icon}</span>{escape(label)}</a></li>')
    cards = "".join(f'<div class="quick-card"><b>{escape(head)}</b><span>{escape(desc)}</span></div>' for head, desc in cfg["cards"])
    if cfg.get("route_groups"):
        phases = []
        for phase_name, stops in cfg["route_groups"]:
            phase_stops = "".join(f'<span class="phase-stop">{escape(stop)}</span>' for stop in stops)
            phases.append(f'<div class="route-phase"><span class="phase-name">{escape(phase_name)}</span><div class="phase-stops">{phase_stops}</div></div>')
        route_title = cfg.get("route_title", "章节区域路线图")
        route_hint = cfg.get("route_hint", "按推荐等级与任务依赖顺序推进")
        route_block = f'<div class="route-map"><div class="route-title"><span>🧭 {escape(route_title)}</span><small>{escape(route_hint)}</small></div><div class="route-phases">' + "".join(phases) + '</div></div>'
    else:
        route = "".join(("" if i == 0 else '<span class="arrow">➜</span>') + f'<span class="stop">{escape(stop)}</span>' for i, stop in enumerate(cfg["route"]))
        route_block = f'<div class="route">{route}</div>'
    legend_items = cfg.get("legend", ["📌 主线", "🗣️ 对话", "⚔️ 战斗", "🕵️ 隐藏", "🎁 奖励", "⚠️ 易错过", "🧩 解谜", "🐾 动物"])
    legend = "".join(f'<span class="chip">{escape(item)}</span>' for item in legend_items)
    enhanced_ui = bool(cfg.get("route_groups"))
    if enhanced_ui:
        toc_block = f'<nav class="toc"><div class="toc-header"><h2>🧭 本章目录</h2><span class="toc-count" id="checkStats">0 / 0</span></div><div class="toc-tools"><input class="toc-search" id="tocSearch" type="search" placeholder="筛选区域 / NPC / 任务…" aria-label="筛选本章目录"><button class="toc-reset" id="resetChecks" type="button" title="重置本页检查项">↺</button></div><ul>{"".join(toc_items)}</ul></nav>'
        article_open = '<article><div class="reading-status"><span>📍</span><span>当前阅读：<strong id="currentSection">章节概览</strong></span></div>'
        footer = '<div class="footer"><span>《神界：原罪 2》Definitive Edition 全内容路线攻略。</span><span class="build-note">Checklist 勾选进度仅保存在本机浏览器。</span></div>'
        script = r'''<script>
const bar=document.querySelector('.progress'),topBtn=document.querySelector('.backtop'),search=document.querySelector('#tocSearch'),reset=document.querySelector('#resetChecks'),stats=document.querySelector('#checkStats'),current=document.querySelector('#currentSection');
function ui(){const d=document.documentElement,p=d.scrollTop/Math.max(1,d.scrollHeight-d.clientHeight)*100;bar.style.width=Math.max(0,Math.min(100,p))+'%';topBtn.classList.toggle('show',d.scrollTop>500)}addEventListener('scroll',ui,{passive:true});ui();
if(search)search.addEventListener('input',()=>{const q=search.value.trim().toLowerCase();document.querySelectorAll('.toc li').forEach(li=>li.classList.toggle('filtered',q&&!li.textContent.toLowerCase().includes(q)))});
const tocLinks=[...document.querySelectorAll('.toc a')],headingMap=new Map(tocLinks.map(a=>[decodeURIComponent(a.hash.slice(1)),a]));
if('IntersectionObserver'in window){const io=new IntersectionObserver(entries=>{const hit=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top)[0];if(!hit)return;tocLinks.forEach(a=>a.classList.remove('active'));const a=headingMap.get(hit.target.id);if(a){a.classList.add('active');current.textContent=a.textContent.trim()}},{rootMargin:'-10% 0px -78% 0px',threshold:[0,1]});document.querySelectorAll('article h2,article h3').forEach(h=>io.observe(h))}
const boxes=[...document.querySelectorAll('input[type=checkbox]')],storageKey='dos2-guide-checks:'+location.pathname;
function updateStats(){const done=boxes.filter(b=>b.checked).length;if(stats)stats.textContent=done+' / '+boxes.length}
try{const saved=JSON.parse(localStorage.getItem(storageKey)||'[]');boxes.forEach((b,i)=>b.checked=!!saved[i])}catch(e){}
boxes.forEach((b,i)=>b.addEventListener('change',()=>{try{localStorage.setItem(storageKey,JSON.stringify(boxes.map(x=>x.checked)))}catch(e){}updateStats()}));
if(reset)reset.addEventListener('click',()=>{if(!boxes.length||!confirm('重置本页所有 Checklist 勾选状态？'))return;boxes.forEach(b=>b.checked=false);try{localStorage.removeItem(storageKey)}catch(e){}updateStats()});updateStats();
</script>'''
    else:
        toc_block = f'<nav class="toc"><h2>🧭 本章目录</h2><ul>{"".join(toc_items)}</ul></nav>'
        article_open = '<article>'
        footer = '<div class="footer">《神界：原罪 2》Definitive Edition 全内容路线攻略。</div>'
        script = "<script>const bar=document.querySelector('.progress'),topBtn=document.querySelector('.backtop');function ui(){const d=document.documentElement,p=d.scrollTop/Math.max(1,d.scrollHeight-d.clientHeight)*100;bar.style.width=Math.max(0,Math.min(100,p))+'%';topBtn.classList.toggle('show',d.scrollTop>500)}addEventListener('scroll',ui,{passive:true});ui();</script>"
    html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{escape(cfg['subtitle'], quote=True)}"><title>{escape(title)}</title><style>{CSS + (CSS_V2 if enhanced_ui else '')}</style></head>
<body id="top"><div class="progress"></div><main>
<section class="hero"><div class="eyebrow">{escape(cfg['eyebrow'])}</div><h1>{escape(title)}</h1><p>{escape(cfg['subtitle'])}</p><p>终极版 / Definitive Edition｜任务分支、隐藏内容、永久收益、跨章影响与离章检查表。</p><div class="hero-orbit" aria-hidden="true"><span>🗺️</span><span>⚔️</span><span>✨</span><span>🎒</span></div></section>
<div class="quick-grid">{cards}</div>
<div class="legend">{legend}</div>
{route_block}
<div class="layout">{toc_block}{article_open}{article}</article></div>
</main>{footer}
<a class="backtop" href="#top" aria-label="返回顶部">⬆️</a>
{script}
</body></html>'''
    HTMLParser().feed(html)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    out_path = HTML_DIR / cfg["out"]
    out_path.write_text(html, encoding="utf-8")
    return out_path, len(headings), html.count("<table")


if __name__ == "__main__":
    for source, config in GUIDES.items():
        path, headings, tables = build_page(source, config)
        print(f"{path.name}: {path.stat().st_size} bytes, {headings} headings, {tables} tables")
