---
name: cyxj-blog-pub
description: >
  把文章发布到 Astro 博客。生成符合规范的 post（frontmatter 必填项校验、
  kebab-case 文件名、正文图片全部换成图床公网 URL），放进
  src/content/posts/，再 build 并部署。产出物在博客仓库，不在内容创作工作区。
  触发词：发布到博客、发博客、博客发文、上博客、Astro 发布、blog 发布。
version: 1.0.0
---

# cyxj-blog-pub — Astro 博客发布

把一篇成稿文章发到博客站点。**只做博客这一个平台**，不要顺手发别处。

## 前置检查

- 博客仓库路径读环境变量 `CYXJ_BLOG_REPO`；未设置则回退 `~/项目/服务器/server-config/blog/`，并向用户确认。
- 后文所有 `$CYXJ_BLOG_REPO` 都指这个路径。

## 何时用

- 用户说「发到博客」「发个博客」并指明（或已存在）一篇文章
- 文章源通常是 Obsidian `$CYXJ_VAULT_BASE/待发布/` 的成稿（未设置 `CYXJ_VAULT_BASE` 时按 `~/obsidian/灵感库` 兜底，并向用户确认），或刚由 `cyxj-transcript` 产出的草稿

**前置**：文章已成文。还是逐字稿先走 `/cyxj-transcript`。

## 项目坐标（来自内容创作 CLAUDE.md）

| 项 | 值 |
|----|----|
| 博客项目 | `$CYXJ_BLOG_REPO`（见「前置检查」） |
| 文章目录 | `src/content/posts/`（文件名 **kebab-case**） |
| 图片 | **全部用图床公网 URL**，禁止本地路径进正文 |
| 部署 | 进入 `$CYXJ_BLOG_REPO` 后先定位 `package.json` 所在目录再跑 `pnpm build`；build 后确认 `dist/` 实际位置再拷贝 → `bash deploy.sh blog` |

## frontmatter 规范

```yaml
---
title: <文章标题>          # 必填
description: <一句话摘要>   # 必填
pubDate: <YYYY-MM-DD>      # 必填
tags: [<可选>]            # 可选
image: <封面图床 URL>      # 可选
draft: false              # 可选；true 则不发布
---
```

发布前**校验三个必填项齐全**：title/pubDate 可据稿推断后向用户确认；description 缺失必须问用户。

## 工作流

1. **取稿**：Read 文章源（路径不明就在 `$CYXJ_VAULT_BASE/待发布/` 搜或问用户）。
2. **定文件名**：英文 kebab-case，如 `claude-code-for-non-coders.md`。
3. **处理图片（关键红线）**：正文里所有图片必须是图床 URL。
   - 本地图 → 先传图床（`img.xiaochens.com`，Lsky Pro，见内容创作 CLAUDE.md「图床操作参考」），拿到公网 URL 再写进正文。
   - 若读不到图床操作参考或缺少凭据，**必须停下向用户要上传方式**；绝不允许跳过图床直接用本地路径发布。
   - **绝不把本地图片路径写进博客正文。**
4. **写 post**：先检查目标 `$CYXJ_BLOG_REPO/src/content/posts/<kebab>.md` 是否已存在，存在则停下确认是否覆盖；再组装 frontmatter + 正文写入。
5. **构建 + 部署**（动手前向用户确认要不要立即上线）：
   - 进入 `$CYXJ_BLOG_REPO` 后先定位 `package.json` 所在目录，在那里跑 `pnpm build`。
   - build 完成后用 `ls` 确认 `dist/` 的实际位置，再执行拷贝（如 `cp -r dist/* landing/`）；拷贝目标不确定时停下问用户。
   - 最后 `bash deploy.sh blog`。
6. **报告**：给出文章路径 + 部署结果；失败就贴报错原文，别说「成功了」。
7. **交接**：文章上线后，若这篇想被 AI 搜索（豆包/DeepSeek/Kimi）引用，提示可用 `cyxj-geo` 出投放与监控方案。

## 红线

- 只发博客这一个平台，不默认走多平台。
- 正文图片只用图床 URL。
- 不臆造 frontmatter：title/pubDate 可据稿推断后向用户确认；description 缺失必须问用户。
- 部署是对外动作——`pnpm build` 之后、推上线之前，先跟用户确认一次。
