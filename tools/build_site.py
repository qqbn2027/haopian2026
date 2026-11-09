# -*- coding: utf-8 -*-
"""根据 data/*.json 生成静态站点：文章页、首页、sitemap。

用法: python tools/build_site.py
站点基础地址可用环境变量 SITE_BASE 覆盖。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SITE_DIR = os.path.join(ROOT, "site")
SITE_BASE = os.environ.get("SITE_BASE", "https://YOUR_USERNAME.github.io/haopian2026/").rstrip("/")
ACCOUNT = "好片别错过"
ACCOUNT_INTRO = "好片别错过 · 每天一部值得看的好片子"

TPL_ARTICLE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | {account}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="../style.css">
</head>
<body>
<header class="site-header">
  <a class="brand" href="../index.html">{account}</a>
  <span class="brand-sub">{intro}</span>
</header>
<main class="page">
  <article>
    <h1 class="article-title">{title}</h1>
    <div class="article-meta"><span class="account">{account}</span><span>{date}</span></div>
    <div class="article-content">
{content}
    </div>
    <div class="follow-box">
      <img src="../qrcode.jpg" alt="{account} 公众号二维码" class="qr">
      <div class="follow-text">
        <strong>觉得内容不错？</strong>
        <span>微信扫描二维码关注公众号「{account}」，好片别错过。</span>
        <a class="origin-link" href="{source}" target="_blank" rel="noopener">阅读原文 &raquo;</a>
      </div>
    </div>
  </article>
  <nav class="article-nav"><a href="../index.html">&laquo; 返回文章列表</a></nav>
</main>
<footer class="site-footer">
  <p>本站内容同步自微信公众号「{account}」，版权归原作者所有。</p>
</footer>
</body>
</html>
"""

TPL_INDEX = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{account} - {intro}</title>
<meta name="description" content="{account} 公众号文章精选，{intro}">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header home">
  <h1 class="brand-big">{account}</h1>
  <p class="intro">{intro}</p>
</header>
<main class="page">
  <h2 class="list-heading">全部文章</h2>
  <ul class="article-list">
{items}
  </ul>
  <div class="follow-box center">
    <img src="qrcode.jpg" alt="{account} 公众号二维码" class="qr">
    <div class="follow-text">
      <strong>微信扫描二维码</strong>
      <span>关注公众号「{account}」，好片别错过。</span>
    </div>
  </div>
</main>
<footer class="site-footer">
  <p>本站内容同步自微信公众号「{account}」，版权归原作者所有。</p>
</footer>
</body>
</html>
"""

TPL_ITEM = """    <li class="item">
      <a href="articles/{id}.html">
        <h3>{title}</h3>
        <p class="item-desc">{desc}</p>
        <p class="item-meta"><span>{date}</span></p>
      </a>
    </li>"""


def main():
    arts = []
    for fname in sorted(os.listdir(DATA_DIR)):
        if not fname.startswith("article-") or not fname.endswith(".json"):
            continue
        with open(os.path.join(DATA_DIR, fname), encoding="utf-8") as f:
            arts.append(json.load(f))
    arts.sort(key=lambda a: a["id"])

    os.makedirs(os.path.join(SITE_DIR, "articles"), exist_ok=True)

    urls = []
    for a in arts:
        page = TPL_ARTICLE.format(
            title=a["title"], account=a["account"], intro=ACCOUNT_INTRO,
            desc=a["desc"], date=a["date"] or "",
            content=a["content"], source=a["source"],
        )
        path = os.path.join(SITE_DIR, "articles", f"{a['id']}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        urls.append((a["id"], a["title"], a["desc"], a["date"]))
        print(f"生成 articles/{a['id']}.html  {a['title']}")

    items = "\n".join(TPL_ITEM.format(
        id=a["id"], title=a["title"],
        desc=a["desc"] if a["desc"] else "&nbsp;",
        date=a["date"] or "") for a in arts)
    index = TPL_INDEX.format(account=ACCOUNT, intro=ACCOUNT_INTRO, items=items)
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index)
    print("生成 index.html")

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
               f'  <url><loc>{SITE_BASE}/</loc></url>']
    for a in arts:
        sitemap.append(f"  <url><loc>{SITE_BASE}/articles/{a['id']}.html</loc></url>")
    sitemap.append("</urlset>")
    with open(os.path.join(SITE_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap))
    print(f"生成 sitemap.xml  (base: {SITE_BASE})")


if __name__ == "__main__":
    main()
