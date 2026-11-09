# 好片别错过 - 公众号文章静态站

微信公众号「好片别错过」的文章静态镜像站，托管在 GitHub Pages，用于站外推广引流。

## 线上地址

https://qqbn2027.github.io/haopian2026/

## 如何新增文章

编辑 `articles.txt`，追加一行（一行一篇文章）：

```
https://mp.weixin.qq.com/s/xxxxxxxx | 文章标题(可选)
```

然后 push。GitHub Actions 会自动：抓取文章 → 下载图片到本地 → 重新构建站点 → 发布。

## 会不会重复抓取？

不会。`tools/update.py` 以文章原始链接（`data/*.json` 中的 `source`）判断是否抓过：

- 已抓过的链接直接跳过，重复 push / 重复执行都不会重新下载；
- 同一个链接在 `articles.txt` 里写了两遍，只抓一次（第二次输出 `[dup]`）；
- 在清单中间插入、删除或调整顺序都可以，文章编号和链接不会错位，也不会重复抓取（新文章分配下一个空号）；
- 从清单里删掉某篇，只会提示 `[note]`，不会自动删除已生成的文章页，避免线上链接变 404。

## 列表分页

首页按发布时间倒序（最新在前），每页 10 篇：

- 第 1 页：`index.html`
- 第 N 页：`page/N.html`（页码、上一页/下一页、总篇数自动生成）

每页条数可通过环境变量 `PAGE_SIZE` 调整（默认 10），例如 `PAGE_SIZE=8 python tools/build_site.py`。
文章增减后重新构建会自动重排分页、清理多余的旧分页文件。

本地手动构建（可选）：

```bash
python tools/update.py       # 抓取新文章
python tools/build_site.py   # 生成 site/
```

## 目录结构

```
articles.txt            文章链接清单（每行一条）
data/                   抓取生成的文章 JSON 数据
tools/fetch_article.py  单篇抓取脚本
tools/update.py         按清单批量同步
tools/build_site.py     站点生成（文章页/首页/sitemap）
site/                   构建产物（GitHub Pages 部署目录）
.github/workflows/      GitHub Actions 自动构建发布
```

## 搜索引擎收录

站点接入 IndexNow（Bing、Yandex、Seznam 等支持的即时收录协议，Google 不支持、需单独走 Search Console）：

- `tools/build_site.py` 会在站点根目录生成 IndexNow 验证文件 `{key}.txt`；
- 每次 push 部署完成后，Actions 自动执行 `tools/indexnow.py`，把首页、分页页和全部文章页 URL 一次性推送给 `api.indexnow.org`；
- 手动补推：`SITE_BASE=https://... python tools/indexnow.py`；
- Key 由 `INDEXNOW_KEY` 环境变量或脚本内默认值控制，更换 Key 后需重新构建并部署。

## 首次部署步骤

1. 在 GitHub 创建空仓库 `haopian2026`
2. `git remote add origin git@github.com:<用户名>/haopian2026.git`
3. push 到 main 分支
4. 仓库 Settings → Pages → Source 选择 **GitHub Actions**

## 备注

- 站点仅收录本公众号原创内容，转载文章请确认授权
- 文章图片已本地化，不依赖微信服务器（规避防盗链）
- sitemap 基础地址在构建时由 `SITE_BASE` 环境变量注入
