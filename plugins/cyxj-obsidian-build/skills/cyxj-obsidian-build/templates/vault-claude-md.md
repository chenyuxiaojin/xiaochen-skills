# 库根 CLAUDE.md 默认模板

首次运行时生成 `$VAULT/CLAUDE.md` 用。先扫库的顶层目录结构，按实际目录调整下面的内容，
再让用户确认或修改。同时创建 `Wiki/index.md` 和 `Wiki/log.md`（如果不存在）。

---

```markdown
# Obsidian 知识库配置

## 原始资料目录（LLM 只读不写）
- 日记/
- 灵感库/
- 收藏夹/
- 资源库/（Wiki/ 子目录除外）

## Wiki 目录（LLM 维护）
- 资源库/Wiki/

## 分类体系
Wiki 概念页按以下分类组织（可随时扩展）：
- 技术工具
- 创作方法
- 人物
- 商业认知
- 自我认知

## 约定
- Wiki 概念页 frontmatter 包含 `source: ai-compiled`
- 合成页 frontmatter 包含 `source: ai-synthesized`
- 所有 [[wikilink]] 必须指向真实存在的文件
```
