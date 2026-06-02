[**English**](README.md) | 中文

# xiaochen-skills

> 小陈的 Claude Code 插件集：14 个面向视频制作、内容发布和知识管理的个人自动化技能。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-blueviolet)](https://claude.ai/code)

## 为什么做这个

Claude Code 内置技能覆盖通用任务。这个集合在上面加了一层垂直工作流：**视频制作 → 内容发布 → 个人知识管理**。每个技能是独立插件，可以单独安装，也可以全量装。

## 技能列表

| 技能 | 功能 | 触发词 | 前置依赖 |
|------|------|--------|---------|
| [cyxj-subfix](./plugins/cyxj-subfix/) | 达芬奇字幕修正：SRT 清理 → Gemini 语义初修 → Claude Opus 审查把关 | `/字幕修正`、`修正字幕`、`字幕错别字`、`SRT 修正` | `GEMINI_API_KEY`；Python: `google-genai`、`pysrt` |
| [cyxj-wechat-pub](./plugins/cyxj-wechat-pub/) | Obsidian Markdown → 微信公众号 HTML，内置 3 套主题（TATALAB 蓝 / 炭黑暖金 / 暖橙编辑），可直接粘贴到微信后台 | `发布到公众号`、`公众号排版`、`微信发布`、`排版文章` | npm: `juice`；微信公众号后台权限 |
| [cyxj-obsidian-build](./plugins/cyxj-obsidian-build/) | 将 Obsidian 库编译为三层知识架构（摄入/查询/检查），灵感来自 Karpathy 的 LLM Wiki 方法论 | `整理 Obsidian`、`编译知识库`、`摄入笔记`、`查知识库`、`健康度检查` | 配置 Obsidian 库路径；无需 API key |
| [cyxj-poster](./plugins/cyxj-poster/) | 一句话生成海报 / 书籍封面 / 专辑封面，33+ 传奇设计师风格 + 10 种摄影风格 | `生成海报`、`封面设计`、`做个封面` | `GEMINI_API_KEY`；Python: `google-genai`、`pillow` |
| [cyxj-youtube-topics](./plugins/cyxj-youtube-topics/) | 搜索某话题 48 小时内新视频，去重、聚类、打 verdict（值得做/观望/跟风/跳过），写入 Obsidian 选题库 | `选题`、`找选题`、`YouTube 最近有什么`、`有什么新视频` | `YOUTUBE_DATA_API_KEY`；Python: `requests`；Obsidian 库路径 |
| [cyxj-yt-creator](./plugins/cyxj-yt-creator/) | 用 Apify 研究外部博主怎么讲某工具/话题：抓字幕、按日期整理视频、写差异化切口，存入 Obsidian 待发布稿 | `查博主怎么用`、`用 Apify 搜 YouTube`、`研究这个工具的 YouTube 视频` | `APIFY_API_TOKEN`；Python: `requests`；Obsidian 库路径 |
| [cyxj-notebook-research](./plugins/cyxj-notebook-research/) | 将 Obsidian 选题库里的视频批量提交给 Google Notebook LM，拉取转录稿和研究报告写回 Obsidian | `帮我研究一下 XXX 话题`、`研究一下这个选题`、`把选题提交给 Notebook LM` | Google 账号（有 Notebook LM 权限）；Python: `notebooklm-py`、`python-frontmatter`；环境变量 `CYXJ_VAULT_BASE` |
| [cyxj-video-cover](./plugins/cyxj-video-cover/) | 真人视频封面生成：上传自己的照片，gpt-image-2 把你重绘进封面场景，默认输出 4 个比例各 2 张 | `/封面`、`/video-cover`、`生成封面`、`做个视频封面`、`做个 YouTube 封面` | OpenAI 兼容 API key（密钥存储中配置的中转站）；仅用 Python 标准库 |
| [cyxj-geo](./plugins/cyxj-geo/) | 生成式搜索引擎优化（GEO）：关键词矩阵 → 文章 brief → 跨平台投放清单 → 监控 SOP，让你/你的产品出现在 AI 回答里 | `做 GEO`、`让豆包/DeepSeek/Kimi 提到我`、`AI 时代 SEO`、`个人 IP 出现在 AI 回答里` | 无需 API key（纯指令型技能） |
| [cyxj-roundtable](./plugins/cyxj-roundtable/) | 召集 6 个 Claude Opus subagent 扮演对立角色（苏格拉底 / 严苛同行 / 带偏见投资人 / 历史学家 / 5 年后后悔的你 / 同盟者），多视角压测决策，会议记录自动存入 Obsidian | `/圆桌`、`开个圆桌`、`开圆桌`、`圆桌一下` | 无需额外 API key（通过 Claude Code 调用 Claude Opus）；Obsidian 库路径 |
| [cyxj-ai-weekly-news](./plugins/cyxj-ai-weekly-news/) | 每周 AI 热点视频端到端 9 步 SOP：选题 → 旁白稿 → 时间码 → 达芬奇 4K 渲染，每个决策点停下等用户确认 | `/AI每周热点`、`/做下一期`、`/每周AI视频`、`做这周的 AI 视频` | 本机安装达芬奇（DaVinci Resolve）；Obsidian 库路径；**项目路径硬编码到作者机器，使用前需修改** |
| [cyxj-transcript](./plugins/cyxj-transcript/) | 把视频/录音逐字稿整理成文章草稿：去口语化、加小标题、数据转表格，原稿保留文末，产出 Obsidian Markdown | `转稿`、`逐字稿整理`、`把这个稿子整理成文章`、`口播稿成文` | Obsidian 库路径；无需 API key |
| [cyxj-blog-pub](./plugins/cyxj-blog-pub/) | 发布文章到 Astro 博客：校验 frontmatter、kebab-case 文件名、正文图片替换为图床 URL，build 后部署 | `发布到博客`、`发博客`、`博客发文`、`上博客`、`Astro 发布` | 本地配置好 Astro 博客仓库和图床；**部署目标是作者自己的服务器，使用前需修改** |
| [cyxj-psjpg](./plugins/cyxj-psjpg/) | 用本机真实 Photoshop 批量导出 JPG（质量可配 / Progressive / 嵌 sRGB），并清理 XMP 元数据中的 PNG/AI 生成来源痕迹 | `/批量过PS`、`/PS批处理`、`/转jpg`、`png 转 jpg`、`封面转 jpg`、`去掉图片的转换痕迹` | **本机安装 Adobe Photoshop（macOS）**；PATH 中有 `exiftool` |

## 安装

在 Claude Code 中运行：

```
/plugin marketplace add chenyuxiaojin/xiaochen-skills
```

一条命令安装全部 14 个插件。

## 使用方法

安装后，在 Claude Code 中输入触发词，对应技能会自动启动。例如：

```
选题                   → 启动 cyxj-youtube-topics
/圆桌                  → 启动 cyxj-roundtable
发布到公众号             → 启动 cyxj-wechat-pub
/批量过PS              → 启动 cyxj-psjpg
```

大多数技能无需加 `/` 前缀——输入触发词即可，Claude Code 会自动匹配。

## 对比同类

| | xiaochen-skills | [Anthropic 官方示例 Skills](https://github.com/anthropics/claude-code) | [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) 社区列表 |
|---|---|---|---|
| 定位 | 视频制作 + 公众号发布 + Obsidian 知识管理 | 通用示例和模式参考 | 社区技能链接汇总，非单一安装 |
| 技能数量 | 14 个 | 随示例变化 | 多仓库分散 |
| 安装方式 | 一条命令全量安装 | 手动复制文件 | 各仓库分别安装 |
| 多智能体 | 有（圆桌召集 6 个 Opus subagent） | 取决于示例 | 各异 |
| 脚本自动化 | 有（Python + Bash + Photoshop + Gemini + Apify） | 较少 | 各异 |
| 目标用户 | macOS 上的视频创作者 / 博主工作流 | 学习 Claude Code 的开发者 | 探索社区工作的开发者 |

## 常见问题

**怎么安装？**
在 Claude Code 里运行 `/plugin marketplace add chenyuxiaojin/xiaochen-skills`，14 个插件全部注册。

**能只安装一个技能吗？**
可以。每个插件互相独立。如果 marketplace 支持单插件安装，可以按名称指定；也可以手动复制 `plugins/cyxj-{name}/` 目录并在自己的 marketplace.json 里注册。

**`cyxj-` 前缀是什么意思？**
这是作者的个人命名前缀，取自"陈与小金"的拼音首字母缩写，用于命名空间隔离，避免与其他插件冲突。前缀本身没有功能含义。

**哪些技能开箱即用？哪些需要配置？**

开箱即用（只需配置 Obsidian 库路径）：
- `cyxj-obsidian-build`、`cyxj-geo`、`cyxj-roundtable`、`cyxj-transcript`

需要 API key 的技能：
- `cyxj-subfix` → `GEMINI_API_KEY`
- `cyxj-poster` → `GEMINI_API_KEY`
- `cyxj-youtube-topics` → `YOUTUBE_DATA_API_KEY`
- `cyxj-yt-creator` → `APIFY_API_TOKEN`
- `cyxj-video-cover` → OpenAI 兼容 API key（中转站）
- `cyxj-notebook-research` → Google 账号（有 Notebook LM 访问权限）

**强绑作者本人环境、使用前必须改配置的技能**：
- `cyxj-ai-weekly-news` — 项目路径硬编码为 `~/项目/试験区/ai-weekly-flash-video`
- `cyxj-blog-pub` — 部署目标是作者自己的 Astro 博客和服务器
- `cyxj-psjpg` — 需要本机安装 Adobe Photoshop（macOS）和 `exiftool`

**API key 存在哪里？**
作者的环境从 `~/项目/自己的应用/密钥存储/.env` 读取。你可以修改脚本，改成从自己的 `.env` 或环境变量读取。

## License

[MIT](LICENSE)
