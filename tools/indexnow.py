# -*- coding: utf-8 -*-
"""把站点全部页面 URL 推送给 IndexNow（Bing/Yandex 等搜索引擎的即时收录协议）。

用法: python tools/indexnow.py
站点基础地址可用环境变量 SITE_BASE 覆盖；Key 可用 INDEXNOW_KEY 覆盖。
前置条件: build_site.py 已生成站点根目录下的 {key}.txt 验证文件并已部署上线。
"""
import json
import os
import sys
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SITE_BASE = os.environ.get("SITE_BASE", "https://qqbn2027.github.io/haopian2026/").rstrip("/")
INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "5bf2867207184b91b5ae94f7d942baad")
ENDPOINT = "https://api.indexnow.org/IndexNow"


def collect_urls():
    urls = [f"{SITE_BASE}/"]
    # 分页页（page/N.html 存在的话）
    p = 2
    while os.path.exists(os.path.join(ROOT, "site", "page", f"{p}.html")):
        urls.append(f"{SITE_BASE}/page/{p}.html")
        p += 1
    # 文章页
    ids = []
    for fname in os.listdir(DATA_DIR):
        if fname.startswith("article-") and fname.endswith(".json"):
            with open(os.path.join(DATA_DIR, fname), encoding="utf-8") as f:
                art = json.load(f)
            if art.get("date"):
                ids.append((art["date"], art["id"]))
    ids.sort(reverse=True)
    urls += [f"{SITE_BASE}/articles/{i}.html" for _, i in ids]
    return urls


def main():
    urls = collect_urls()
    payload = {
        "host": SITE_BASE.split("//", 1)[1].split("/", 1)[0],
        "key": INDEXNOW_KEY,
        "keyLocation": f"{SITE_BASE}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"})
    print(f"推送 {len(urls)} 条 URL 给 IndexNow (host: {payload['host']})")
    for u in urls:
        print(f"  {u}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code, text = r.status, r.read().decode("utf-8", errors="ignore").strip()
    except urllib.error.HTTPError as e:
        code, text = e.code, e.read().decode("utf-8", errors="ignore").strip()
        hints = {400: "请求格式错误", 403: "Key 验证失败（检查 {key}.txt 是否已上线）",
                 422: "URL 不属于提交的 host", 429: "请求过于频繁"}
        print(f"推送失败: HTTP {code} {hints.get(code, '')} {text}")
        sys.exit(1)
    # 200: 接受；202: 接受，验证稍后进行
    print(f"推送成功: HTTP {code} {text or '(empty)'}")
    if code == 202:
        print("Key 验证会在搜索引擎侧异步完成，收录通常几小时内生效。")


if __name__ == "__main__":
    main()
