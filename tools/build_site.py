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
ACCOUNT_INTRO = "好戏即将登场，所有影视新消息，在这里抢先看。"
PAGE_SIZE = int(os.environ.get("PAGE_SIZE", "10"))  # 首页每页文章数
# IndexNow 验证 Key（明文存放，IndexNow Key 本身就是公开的验证凭证）
INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "5bf2867207184b91b5ae94f7d942baad")
# 百度统计站点 ID（tongji.baidu.com）
HMT_ID = os.environ.get("HMT_ID", "c9930abe29fd95e3b273fad3e4060a64")
TPL_HMT = """<script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?%s";
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(hm, s);
})();
</script>""" % HMT_ID

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
{hmt}</body>
</html>
"""

TPL_INDEX = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{account} - {intro}</title>
<meta name="description" content="{account} 公众号文章精选，{intro}">
<link rel="stylesheet" href="{base}style.css">
{head_extra}</head>
<body>
<header class="site-header home">
  <h1 class="brand-big">{account}</h1>
  <p class="intro">{intro}</p>
</header>
<main class="page">
  <h2 class="list-heading">{heading}</h2>
  <ul class="article-list">
{items}
  </ul>
{pager}
  <div class="follow-box center">
    <img src="{base}qrcode.jpg" alt="{account} 公众号二维码" class="qr">
    <div class="follow-text">
      <strong>微信扫描二维码</strong>
      <span>关注公众号「{account}」，好片别错过。</span>
    </div>
  </div>
</main>
<footer class="site-footer">
  <p>本站内容同步自微信公众号「{account}」，版权归原作者所有。</p>
</footer>
{hmt}</body>
</html>
"""

TPL_ITEM = """    <li class="item">
      <a href="{base}articles/{id}.html">
        <h3>{title}</h3>
        <p class="item-desc">{desc}</p>
        <p class="item-meta"><span>{date}</span></p>
      </a>
    </li>"""

TPL_PAGER = """  <nav class="pager" aria-label="分页导航">
{prev}
    <span class="pager-pages">{pages}</span>
{next}
  </nav>
  <p class="pager-info">第 {cur} / {total} 页 · 共 {count} 篇</p>"""



def page_href(page, base):
    """第 1 页固定是根目录的 index.html，其余放在 page/ 下。"""
    return f"{base}index.html" if page == 1 else f"{base}page/{page}.html"


def build_list_pages(arts):
    """按发布时间倒序分页生成首页，第 1 页为 index.html，其余为 page/N.html。"""
    ordered = sorted(arts, key=lambda a: (a.get("date") or "", a["id"]), reverse=True)
    total_pages = max(1, (len(ordered) + PAGE_SIZE - 1) // PAGE_SIZE)
    page_dir = os.path.join(SITE_DIR, "page")
    os.makedirs(page_dir, exist_ok=True)
    # 文章变少时清掉多余的分页文件，避免旧页残留
    for fname in os.listdir(page_dir):
        if fname.endswith(".html"):
            os.remove(os.path.join(page_dir, fname))

    for p in range(1, total_pages + 1):
        base = "" if p == 1 else "../"
        chunk = ordered[(p - 1) * PAGE_SIZE:p * PAGE_SIZE]
        items = "\n".join(TPL_ITEM.format(
            base=base, id=a["id"], title=a["title"],
            desc=a["desc"] if a["desc"] else "&nbsp;",
            date=a["date"] or "") for a in chunk)

        if p > 1:
            prev = (f'    <a class="pager-btn" href="{page_href(p - 1, base)}"'
                    f' rel="prev">&laquo; 上一页</a>')
        else:
            prev = '    <span class="pager-btn disabled">&laquo; 上一页</span>'
        if p < total_pages:
            nxt = (f'    <a class="pager-btn" href="{page_href(p + 1, base)}"'
                   f' rel="next">下一页 &raquo;</a>')
        else:
            nxt = '    <span class="pager-btn disabled">下一页 &raquo;</span>'

        nums = []
        for i in range(1, total_pages + 1):
            if i == p:
                nums.append(f'<span class="pager-num current">{i}</span>')
            else:
                nums.append(f'<a class="pager-num" href="{page_href(i, base)}">{i}</a>')
        pager = TPL_PAGER.format(
            prev=prev, next=nxt, pages=" ".join(nums),
            cur=p, total=total_pages, count=len(ordered))

        # 分页页面的 SEO 提示：canonical + 上一页/下一页
        head_extra = ""
        if total_pages > 1:
            canonical = "index.html" if p == 1 else f"page/{p}.html"
            head_extra += (f'<link rel="canonical" href="{SITE_BASE}/{canonical}">\n')
            if p > 1:
                head_extra += (f'<link rel="prev" href="{SITE_BASE}/'
                               f'{"index.html" if p == 2 else f"page/{p - 1}.html"}">\n')
            if p < total_pages:
                head_extra += f'<link rel="next" href="{SITE_BASE}/page/{p + 1}.html">\n'

        heading = "全部文章" if p == 1 else f"全部文章 · 第 {p} 页"
        html = TPL_INDEX.format(
            account=ACCOUNT, intro=ACCOUNT_INTRO, base=base,
            head_extra=head_extra, heading=heading, items=items, pager=pager,
            hmt=TPL_HMT)

        if p == 1:
            path = os.path.join(SITE_DIR, "index.html")
            print(f"生成 index.html  (第 1/{total_pages} 页, {len(chunk)} 篇)")
        else:
            path = os.path.join(page_dir, f"{p}.html")
            print(f"生成 page/{p}.html  (第 {p}/{total_pages} 页, {len(chunk)} 篇)")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    return ordered, total_pages


def main():
    arts = []
    for fname in sorted(os.listdir(DATA_DIR)):
        if not fname.startswith("article-") or not fname.endswith(".json"):
            continue
        with open(os.path.join(DATA_DIR, fname), encoding="utf-8") as f:
            arts.append(json.load(f))
    arts.sort(key=lambda a: a["id"])

    os.makedirs(os.path.join(SITE_DIR, "articles"), exist_ok=True)

    for a in arts:
        page = TPL_ARTICLE.format(
            title=a["title"], account=a["account"], intro=ACCOUNT_INTRO,
            desc=a["desc"], date=a["date"] or "",
            content=a["content"], source=a["source"], hmt=TPL_HMT,
        )
        path = os.path.join(SITE_DIR, "articles", f"{a['id']}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"生成 articles/{a['id']}.html  {a['title']}")

    ordered, total_pages = build_list_pages(arts)

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
               f'  <url><loc>{SITE_BASE}/</loc></url>']
    for p in range(2, total_pages + 1):
        sitemap.append(f"  <url><loc>{SITE_BASE}/page/{p}.html</loc></url>")
    for a in ordered:
        sitemap.append(f"  <url><loc>{SITE_BASE}/articles/{a['id']}.html</loc></url>")
    sitemap.append("</urlset>")
    with open(os.path.join(SITE_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap))
    print(f"生成 sitemap.xml  (base: {SITE_BASE})")

    # IndexNow 验证文件：https://SITE_BASE/{key}.txt，内容就是 key
    key_path = os.path.join(SITE_DIR, f"{INDEXNOW_KEY}.txt")
    with open(key_path, "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY)
    print(f"生成 {INDEXNOW_KEY}.txt  (IndexNow 验证文件)")


if __name__ == "__main__":
    main()
