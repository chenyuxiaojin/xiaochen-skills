---
name: cyxj-obsidian-build
description: >
  基于 Karpathy LLM Wiki 方法论，将 Obsidian 库编译成三层知识架构。
  支持 Ingest（摄入）、Query（查询）、Lint（检查）三大操作。
  触发词：整理 Obsidian、编译知识库、摄入笔记、查知识库、健康度检查。
  当用户提到 Obsidian 整理、笔记关联、知识管理、Wiki 维护时，使用此 skill。
version: 2.0.0
---

<!-- 给人看的建议：此 skill 涉及大量语义关联，主流程建议 Opus，子代理扫描可用 Sonnet -->

# Obsidian 知识库编译器

> 灵感来源：Andrej Karpathy 的 [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 方法论
> 核心理念：LLM 增量构建并维护一个持久的 Wiki — 一个结构化、互相链接的 Markdown 文件集合。知识编译一次，持续维护，而不是每次查询时重新推导。

---

## 定位库（任何操作之前先做）

全文的 `$VAULT` 指 **Obsidian 库的根目录**。确认方式：

1. 当前工作目录（或用户明确给出的路径）下存在 `.obsidian/` 目录 → 该目录即 `$VAULT`
2. cwd 不是库（没有 `.obsidian/`）→ 停下来问用户库路径，不要猜
3. 用户给的路径不存在或仍无 `.obsidian/` → **终止并报告**，不要在错误的目录里建任何东西

「首次运行」的建目录、写 CLAUDE.md 等动作，**必须在确认 `$VAULT` 之后**才能执行。

---

## 三层架构

```
Layer 1: Raw Sources（原始资料）— 用户写的，LLM 只读不写
       ↓ LLM 编译
Layer 2: Wiki（知识层）— LLM 全权维护，用户只读
       ↑ 规则来自
Layer 3: Schema（配置层）— SKILL.md + $VAULT/CLAUDE.md
```

### Layer 1: Raw Sources（原始资料）

用户的原始笔记。**完全不可变** — LLM 读取但绝不修改这些文件。库根 CLAUDE.md 除外（仅首次运行或用户要求时可写，见「权限边界」）。

包括：日记、灵感、收藏的文章、资源笔记等。具体目录结构由 `$VAULT/CLAUDE.md` 定义。

### Layer 2: Wiki（知识层）

LLM 维护的知识产物，存放在 `$VAULT/资源库/Wiki/`（默认，可在 CLAUDE.md 中自定义）。

Wiki 层包含：
- **概念页** — 工具、人物、方法论的结构化页面
- **合成页** — Query 操作产生的对比分析、总结
- **index.md** — 按分类组织的内容目录
- **log.md** — 操作时间线日志

所有跨笔记的链接关系都在 Wiki 页面里维护。原始笔记不需要写任何链接 — Obsidian 的反向链接面板会自动显示哪些 Wiki 页面引用了它。

### Layer 3: Schema（配置层）

分两部分：
- **本 SKILL.md** — 操作流程、页面模板、权限边界（通用逻辑）
- **`$VAULT/CLAUDE.md`** — 库专属配置（目录结构、分类体系）

用户在 Obsidian 库目录启动 Claude Code 时，CLAUDE.md 被自动读取。

---

## 首次运行

前提：已按「定位库」确认 `$VAULT`。如果 `$VAULT/CLAUDE.md` 不存在，先生成它再开始工作：

1. 扫描库的顶层目录结构
2. 读 `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-obsidian-build/templates/vault-claude-md.md`，按实际目录调整后生成 CLAUDE.md
3. 让用户确认或修改后再继续

同时创建 `Wiki/index.md` 和 `Wiki/log.md`（格式见
`${CLAUDE_PLUGIN_ROOT}/skills/cyxj-obsidian-build/templates/index-and-log.md`）。

---

## 操作一：Ingest（摄入）

将原始资料编译进 Wiki。一篇资料可能触及 10-15 个 Wiki 页面。

### 单条摄入

用户指定一篇笔记（或刚添加的新笔记）：

1. **读取配置**：从 `$VAULT/CLAUDE.md` 获取目录结构和分类体系
2. **读取资料**：用 `obsidian-cli read` 读取指定笔记
3. **讨论要点**：和用户简要讨论这篇笔记的核心内容和值得提取的概念
4. **识别概念**：提取笔记中的概念、工具名、人名、方法论
5. **匹配 Wiki**：对每个概念，用 `obsidian-cli search` 检查是否已有 Wiki 页面
   - 已有 → 用 `obsidian-cli read` 读取，用 `obsidian-cli append` 追加新信息
   - 没有 → 用 `obsidian-cli create` 创建新概念页，模板与规则见
     `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-obsidian-build/templates/concept-page.md`
6. **更新索引**：更新 `Wiki/index.md`，添加新页面条目
7. **记录日志**：追加到 `Wiki/log.md`
8. **汇报结果**：告诉用户创建/更新了哪些页面

### 批量摄入

用户要求全量整理或扫描某个目录：

1. **读取配置**：同上
2. **扫描变化**：读取 `Wiki/log.md` 获取上次操作时间，以 log.md 最后一条的日期为界，用 `find $VAULT -name "*.md" -newermt "该日期"`（或按文件 mtime）过滤出未处理的笔记
3. **概念发现**：扫描所有未处理笔记，找出在 3 个以上不同文件中出现的概念
4. **用户确认**：列出发现的概念清单（待创建 / 待更新 / 跳过），等用户确认
5. **批量执行**：对确认的概念逐个执行创建/更新
6. **更新索引和日志**

**概念筛选标准：**
- 具体的、可链接的概念（如"Claude Code"、"视频制作"），不要过于笼统的词
- 优先选择能串联多个领域笔记的"桥梁概念"

### 日记提炼（Ingest 的子流程）

摄入日记时，额外提取有认知价值的洞察：

**提炼：** 原创观点、方法论总结、项目决策和复盘、有启发的失败
**忽略：** 生活流水账、纯情绪宣泄、已在其他笔记中记录的内容

提炼的洞察写入对应概念页的"日记洞察"区块，附带日期和关键原文。

---

## 操作二：Query（查询）

对知识库提问，好的答案存回 Wiki。

1. **理解问题**：解析用户的提问
2. **搜索 Wiki**：用 `obsidian-cli search` 在 Wiki 中查找相关页面
3. **深入阅读**：用 `obsidian-cli read` 读取相关的 Wiki 页面和原始资料
4. **合成答案**：综合多个来源，给出带引用的回答
5. **提议归档**：问用户"这次分析要存回 Wiki 吗？"
   - 是 → 按 `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-obsidian-build/templates/synthesis-page.md`
     创建合成页，更新 index.md，追加 log.md
   - 否 → 仅追加 log.md 记录查询

这样你的提问和思考也会沉淀到知识库里，而不是消失在聊天记录中。

---

## 操作三：Lint（检查）

健康度检查，发现问题但不自动修复。

1. **读取配置**：从 CLAUDE.md 获取目录结构
2. **执行检查项**：

| 检查项 | 方法 | 说明 |
|--------|------|------|
| 孤岛 Wiki 页 | `obsidian-cli backlinks` | 没有被任何笔记引用的 Wiki 页面 |
| 断裂链接 | `obsidian-cli search` + 验证 | `[[链接]]` 指向不存在的文件 |
| 概念页过时 | 以 log.md 最后一条日期为判据 | 该日期之后的新资料提到某概念但页面未更新 |
| 缺失概念 | 分析原始资料 | 高频出现但没有 Wiki 页面的概念 |
| 矛盾内容 | 读取相关页面对比（仅抽查本次操作涉及的概念页，不做全库比对） | 同一概念在不同页面有矛盾描述 |
| 空文件 | 扫描 Wiki/ | 文件存在但内容为空或只有标题 |
| 数据缺口 | 分析概念页 | 概念页内容单薄，建议补充的方向 |

3. **生成报告**：按严重程度排序，建议用户如何处理
4. **追加 log.md**：记录本次检查结果

---

## 模板文件（用到时再读）

所有页面模板都在 `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-obsidian-build/templates/` 下，写文件前读对应的那份：

| 文件 | 什么时候读 |
|---|---|
| `vault-claude-md.md` | 首次运行，生成库根 CLAUDE.md |
| `concept-page.md` | Ingest 创建/更新概念页（含 aliases、链接、只追加不删的规则） |
| `synthesis-page.md` | Query 的答案要存回 Wiki |
| `index-and-log.md` | 更新 Wiki/index.md 或 Wiki/log.md |

---

## 工具使用

开始前先探测 obsidian-cli 是否可用（如跑一次 `obsidian-cli tags`，或检查命令是否存在）；不可用则全程走下表的兜底列，不要反复尝试失败的命令。

优先使用 Obsidian CLI（通过 `obsidian:obsidian-cli` skill），文件系统工具作为兜底：

| 操作 | Obsidian CLI 命令 | 兜底方案 |
|------|-------------------|----------|
| 读取笔记 | `read file="笔记名"` | Read 工具 |
| 搜索内容 | `search query="关键词" limit=20` | Grep 工具 |
| 创建页面 | `create name="页面名" content="..." silent` | Write 工具 |
| 追加内容 | `append file="页面名" content="..."` | Edit 工具 |
| 设置属性 | `property:set file="页面名" name="key" value="val"` | Edit 工具 |
| 查反向链接 | `backlinks file="笔记名"` | Grep `\[\[笔记名\]\]` |
| 查标签 | `tags` | Grep `#tag` |

---

## 权限边界

### 可以做
- 在 Wiki 目录下创建和更新文件（概念页、合成页、index.md、log.md）
- 读取库中所有 `.md` 文件用于分析
- 在库根目录创建/更新 CLAUDE.md（仅首次运行或用户要求时）
- 使用 Obsidian CLI 的搜索、读取、反向链接功能

### 绝不可以做
- 修改 Wiki 目录以外的任何文件（原始资料完全不可变）
- 删除任何文件或文件夹
- 修改 `.obsidian/` 目录下的配置
- 创建指向不存在文件的 `[[wikilink]]`

---

## 执行策略

| 场景 | 流程 |
|------|------|
| **首次运行** | 生成 CLAUDE.md → 用户确认 → 批量 Ingest → 创建 index.md + log.md |
| **日常使用** | 用户添加新笔记后单条 Ingest；随时 Query；定期 Lint |
| **全量刷新** | 用户明确要求时，基于 log.md 增量处理 |

**用户确认点：**
- 首次运行的 CLAUDE.md 内容
- 批量 Ingest 的概念列表（确认后再创建页面）
- Query 的答案是否存回 Wiki
- Lint 的修复建议（报告不自动修复）
