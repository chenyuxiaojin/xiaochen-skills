# 导航文件格式：Wiki/index.md 与 Wiki/log.md

## Wiki/index.md

按分类组织的内容目录，每次 Ingest 后更新。分类来自 `$VAULT/CLAUDE.md` 中定义的分类体系。

```markdown
---
source: ai-compiled
updated: YYYY-MM-DD
---

# Wiki 索引

## 技术工具
- [[Claude Code]] — AI 编程助手
- [[Obsidian]] — 知识管理工具

## 创作方法
- [[视频制作]] — 短视频内容创作流程

## 合成分析
- [[某某对比分析]] — Query 产出的合成页
```

## Wiki/log.md

操作时间线，仅追加，格式可被 grep 解析。批量 Ingest 的「上次操作时间」和 Lint 的
「概念页过时」判据都读这里的最后一条日期。

```markdown
## [2026-04-05] ingest | 文章标题
摄入来源：收藏夹/article.md
更新页面：[[概念A]]、[[概念B]]
新建页面：[[概念C]]

## [2026-04-05] query | 用户的问题
答案归档：[[合成页标题]]
引用页面：[[概念A]]、[[概念D]]

## [2026-04-05] lint
发现问题：3 个孤岛、1 个断链、2 个过时页
```
