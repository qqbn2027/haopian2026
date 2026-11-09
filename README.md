# 好片别错过 - 公众号文章静态站

微信公众号「好片别错过」的文章静态镜像站，托管在 GitHub Pages，用于站外推广引流。

## 线上地址

`https://<你的GitHub用户名>.github.io/haopian2026/`

## 如何新增文章

编辑 `articles.txt`，追加一行（一行一篇文章）：

```
https://mp.weixin.qq.com/s/xxxxxxxx | 文章标题(可选)
```

然后 push。GitHub Actions 会自动：抓取文章 → 下载图片到本地 → 重新构建站点 → 发布。

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

## 首次部署步骤

1. 在 GitHub 创建空仓库 `haopian2026`
2. `git remote add origin git@github.com:<用户名>/haopian2026.git`
3. push 到 main 分支
4. 仓库 Settings → Pages → Source 选择 **GitHub Actions**

## 备注

- 站点仅收录本公众号原创内容，转载文章请确认授权
- 文章图片已本地化，不依赖微信服务器（规避防盗链）
- sitemap 基础地址在构建时由 `SITE_BASE` 环境变量注入
