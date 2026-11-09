# -*- coding: utf-8 -*-
"""抓取单篇微信文章：下载正文图片、生成 JSON 数据。

用法: python tools/fetch_article.py <序号> <URL> <可选标题>
"""
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "site", "img")
DATA_DIR = os.path.join(ROOT, "data")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="ignore")


def get_title(raw):
    m = re.search(r'<h1[^>]*id="activity-name"[^>]*>(.*?)</h1>', raw, re.S)
    if not m:
        m = re.search(r"<title>\s*(.*?)\s*</title>", raw, re.S)
    if not m:
        return "未命名文章"
    t = re.sub(r"<[^>]+>", "", m.group(1))  # 清理内部标签
    t = re.sub(r"\s+", " ", t)
    return t.replace("_腾讯新闻", "").strip() or "未命名文章"


def get_meta(raw):
    account = ""
    m = re.search(r'<a[^>]*id="js_name"[^>]*>\s*(.*?)\s*</a>', raw, re.S)
    if m:
        account = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    author = ""
    m = re.search(r'<meta name="author"[^>]*content="([^"]*)"', raw)
    if m:
        author = m.group(1).strip()
    pub = ""
    m = re.search(r'<em[^>]*id="publish_time"[^>]*>\s*(.*?)\s*</em>', raw, re.S)
    if m:
        pub = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    if not pub:
        m = re.search(r'var ct = "(\d+)"', raw)
        if m:
            import datetime
            pub = datetime.datetime.fromtimestamp(int(m.group(1))).strftime("%Y-%m-%d")
    m = re.search(r'<meta property="og:description"[^>]*content="([^"]*)"', raw)
    desc = m.group(1).strip() if m else ""
    return account, author, pub, desc


def extract_content(raw):
    m = re.search(r'<div[^>]*id="js_content"[^>]*>', raw)
    if not m:
        return ""
    start = m.end()
    depth = 1
    pos = start
    for tm in re.finditer(r"<(/?)div[^>]*>", raw[start:], re.I):
        if tm.group(1):
            depth -= 1
            if depth == 0:
                pos = start + tm.start()
                break
        else:
            depth += 1
    return raw[start:pos]


def clean_content(html):
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.S | re.I)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.S | re.I)
    html = re.sub(r"<svg[^>]*>.*?</svg>", "", html, flags=re.S | re.I)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    html = re.sub(r'<p[^>]*style="display:\s*none[^"]*"[^>]*>.*?</p>', "", html, flags=re.S)
    html = re.sub(r'src="data:image[^"]*"', "", html)
    html = html.replace("data-src=", "src=")
    html = html.replace("\u200b", "").replace("\ufeff", "")
    return html.strip()


def download_image(url, dest):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Referer": "https://mp.weixin.qq.com/",
    })
    with urllib.request.urlopen(req, timeout=30) as r, open(dest, "wb") as f:
        f.write(r.read())


def main():
    idx = sys.argv[1]
    url = sys.argv[2]
    title_override = sys.argv[3] if len(sys.argv) > 3 else ""

    raw = fetch(url)
    title = title_override or get_title(raw)
    account, author, pub, desc = get_meta(raw)
    content = clean_content(extract_content(raw))

    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    mapping = {}
    for i, u in enumerate(re.findall(r'src="(https?://mmbiz\.qpic\.cn/[^"]+)"', content), 1):
        u = u.replace("&amp;", "&")
        if u in mapping:
            continue
        m = re.search(r"wx_fmt=([a-zA-Z]+)", u)
        ext = (m.group(1) if m else "jpg").lower()
        if ext == "jpeg":
            ext = "jpg"
        fname = f"a{idx}-{i}.{ext}"
        try:
            download_image(u, os.path.join(IMG_DIR, fname))
            mapping[u] = f"../img/{fname}"
            print(f"OK  {fname}")
        except Exception as e:
            print(f"FAIL {fname}: {e}", file=sys.stderr)

    for u, local in mapping.items():
        content = content.replace(u, local)
        content = content.replace(u.replace("&", "&amp;"), local)

    # 相对路径转义（文章页位于 site/articles/ 下）
    data = {
        "id": int(idx),
        "title": title,
        "account": account or "好片别错过",
        "author": author,
        "date": pub,
        "desc": (desc or title)[:80],
        "source": url,
        "content": content,
    }
    out = os.path.join(DATA_DIR, f"article-{idx}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"标题: {title}")
    print(f"账号: {data['account']}  日期: {pub}")
    print(f"图片: {len(mapping)} 张  ->  {out}")


if __name__ == "__main__":
    main()
