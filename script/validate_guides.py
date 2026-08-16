"""Validate guide sources and generated HTML without third-party dependencies."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
import re
import sys

from build_guides import GUIDES, HTML_DIR, MD_DIR, PROJECT_ROOT


class PageAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.headings = 0
        self.tables = 0
        self.checkboxes = 0

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if "id" in data:
            self.ids.append(data["id"])
        if tag == "a" and data.get("href"):
            self.hrefs.append(data["href"])
        if tag in {"h1", "h2", "h3", "h4"}:
            self.headings += 1
        if tag == "table":
            self.tables += 1
        if tag == "input" and data.get("type") == "checkbox":
            self.checkboxes += 1


def local_target(base, href):
    href = unquote(href).split("#", 1)[0].strip()
    if not href or href.startswith(("http://", "https://", "mailto:", "javascript:")):
        return None
    return (base / href).resolve()


def markdown_links(path):
    text = path.read_text(encoding="utf-8")
    return re.findall(r"!?(?:\[[^]]*])\(([^)]+)\)", text)


def main():
    errors = []
    source_files = sorted(MD_DIR.glob("*.md"))
    html_files = sorted(HTML_DIR.glob("*.html"))

    expected_sources = {MD_DIR / name for name in GUIDES}
    expected_outputs = {HTML_DIR / cfg["out"] for cfg in GUIDES.values()}
    for path in sorted(expected_sources | expected_outputs):
        if not path.exists():
            errors.append(f"缺少配置文件：{path.relative_to(PROJECT_ROOT)}")

    for path in sorted(set(source_files) - expected_sources):
        errors.append(f"Markdown 未登记到构建配置：{path.relative_to(PROJECT_ROOT)}")
    for path in sorted(set(html_files) - expected_outputs):
        errors.append(f"存在未登记的旧 HTML：{path.relative_to(PROJECT_ROOT)}")

    readme = PROJECT_ROOT / "README.md"
    for path in [readme, *source_files]:
        if not path.exists():
            errors.append(f"缺少 Markdown：{path.relative_to(PROJECT_ROOT)}")
            continue
        for href in markdown_links(path):
            target = local_target(path.parent, href)
            if target and not target.exists():
                errors.append(
                    f"Markdown 失效链接：{path.relative_to(PROJECT_ROOT)} → {href}"
                )

    total_headings = total_tables = total_checkboxes = 0
    for path in html_files:
        audit = PageAudit()
        try:
            audit.feed(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"HTML 无法解析：{path.name}（{exc}）")
            continue

        counts = Counter(audit.ids)
        duplicates = sorted(key for key, count in counts.items() if count > 1)
        if duplicates:
            errors.append(f"重复 ID：{path.name} → {', '.join(duplicates)}")

        ids = set(audit.ids)
        for href in audit.hrefs:
            if href.startswith("#"):
                anchor = unquote(href[1:])
                if anchor and anchor not in ids:
                    errors.append(f"失效锚点：{path.name} → {href}")
                continue
            target = local_target(path.parent, href)
            if target and not target.exists():
                errors.append(f"HTML 失效链接：{path.name} → {href}")

        total_headings += audit.headings
        total_tables += audit.tables
        total_checkboxes += audit.checkboxes

    print(
        "校验统计："
        f"{len(source_files)} 个 Markdown，{len(html_files)} 个 HTML，"
        f"{total_headings} 个标题，{total_tables} 张表格，"
        f"{total_checkboxes} 个 Checklist 项。"
    )
    if errors:
        print("\n发现问题：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("校验通过：配置文件、相对链接、HTML 锚点和 ID 均正常。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
