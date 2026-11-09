# -*- coding: utf-8 -*-
"""读取 articles.txt，抓取尚未入库的文章。

清单格式（每行）: URL | 标题(可选)

去重规则：以文章原始链接（data/*.json 里的 source）为准，
已经抓过的链接一律跳过，因此：
- 同一个链接在清单里出现多次，只会抓一次；
- 在清单中间插入/删除/调整顺序，不会导致文章重复抓取或错位覆盖；
- 新文章分配一个未被占用的序号，已有文章的编号与链接永久不变。
"""
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST = os.path.join(ROOT, "articles.txt")
DATA_DIR = os.path.join(ROOT, "data")

URL_RE = re.compile(r"^https?://(mp\.weixin\.qq\.com|tungsten\.qq\.com)/")

with open(LIST, encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

os.makedirs(DATA_DIR, exist_ok=True)

# 扫描已有数据，建立 链接 -> 序号 索引
by_url = {}
used_ids = set()
for path in glob.glob(os.path.join(DATA_DIR, "article-*.json")):
    try:
        with open(path, encoding="utf-8") as f:
            art = json.load(f)
        art_id = int(art["id"])
    except (ValueError, KeyError, json.JSONDecodeError):
        print(f"[warn] 跳过损坏的数据文件: {os.path.basename(path)}")
        continue
    used_ids.add(art_id)
    src = (art.get("source") or "").strip()
    if src:
        by_url[src] = art_id

next_id = max(used_ids) + 1 if used_ids else 1
listed = set()
fetched = 0

for line in lines:
    parts = line.split("|")
    url = parts[0].strip()
    title = parts[1].strip() if len(parts) > 1 else ""
    if not URL_RE.match(url):
        print(f"[warn] 不是微信文章链接，已忽略: {line}")
        continue
    if url in listed:
        print(f"[dup]  清单内重复链接，已忽略: {url}")
        continue
    listed.add(url)
    if url in by_url:
        print(f"[skip] 已抓取过 -> articles/{by_url[url]}.html")
        continue

    while next_id in used_ids:
        next_id += 1
    print(f"[fetch] article-{next_id}: {url}")
    cmd = [sys.executable, os.path.join(ROOT, "tools", "fetch_article.py"),
           str(next_id), url]
    if title:
        cmd.append(title)
    subprocess.run(cmd, check=True)
    used_ids.add(next_id)
    by_url[url] = next_id
    next_id += 1
    fetched += 1

# 数据里存在但清单里已删除的文章，只提示不自动删（避免线上链接失效）
for url, art_id in by_url.items():
    if url not in listed:
        print(f"[note] articles/{art_id}.html 不在 articles.txt 中（如需下线请手动删除 data/article-{art_id}.json）")

print(f"完成：新增抓取 {fetched} 篇，清单共 {len(listed)} 条，库内共 {len(by_url)} 篇")
