# -*- coding: utf-8 -*-
"""读取 articles.txt，抓取尚未入库的文章。

清单格式（每行）: URL | 标题(可选)
已入库的文章（按行号即序号）自动跳过。
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST = os.path.join(ROOT, "articles.txt")
DATA_DIR = os.path.join(ROOT, "data")

URL_RE = r"^https?://(mp\.weixin\.qq\.com|tungsten\.qq\.com)"

with open(LIST, encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

os.makedirs(DATA_DIR, exist_ok=True)
for i, line in enumerate(lines, 1):
    parts = line.split("|")
    url = parts[0].strip()
    title = parts[1].strip() if len(parts) > 1 else ""
    out = os.path.join(DATA_DIR, f"article-{i}.json")
    if os.path.exists(out):
        print(f"[skip] article-{i} 已存在")
        continue
    print(f"[fetch] article-{i}: {url}")
    cmd = [sys.executable, os.path.join(ROOT, "tools", "fetch_article.py"), str(i), url]
    if title:
        cmd.append(title)
    subprocess.run(cmd, check=True)
