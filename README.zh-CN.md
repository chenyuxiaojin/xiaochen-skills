[**English**](README.md) | 中文

# xiaochen-skills

> 小陈的 Claude Code 插件集：14 个插件（16 个技能），面向视频制作、内容发布和知识管理。

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
| [cyxj-image-studio](./plugins/cyxj-image-studio/) | 生图工坊（gpt-image-2 中转），一个插件两个 skill 共享凭据加载：**cyxj-poster**（33+ 大师风格海报/书封/专辑封面）+ **cyxj-video-cover**（无字底图引擎：真人照重绘保脸，只出 16:9 无文字场景图，供 cyxj-release-kit 封面工作台当底图；带字封面成品一律走 cyxj-release-kit） | `做海报`、`海报设计`、`书籍封面`、`专辑封面` | `GPTIMG2_BASE_URL`/`GPTIMG2_API_KEY`；poster 另需 `GEMINI_API_KEY` + Python `requests`/`google-genai`/`pillow`；video-cover 仅标准库（Pillow 可选） |
| [cyxj-youtube-topics](./plugins/cyxj-youtube-topics/) | 搜索某话题 48 小时内新视频，去重、聚类、打 verdict（值得做/观望/跟风/跳过），写入 Obsidian 选题库 | `YouTube 选题`、`找 YouTube 选题`、`YouTube 最近有什么`、`有什么新视频` | `YOUTUBE_DATA_API_KEY`；`APIFY_API_TOKEN`（字幕）；Python: `requests`；Obsidian 库路径 |
| [cyxj-yt-creator](./plugins/cyxj-yt-creator/) | 用 Apify 研究外部博主怎么讲某工具/话题：抓字幕、按日期整理视频、写差异化切口，存入 Obsidian 待发布稿 | `查博主怎么用`、`用 Apify 搜 YouTube`、`研究这个工具的 YouTube 视频` | `APIFY_API_TOKEN`；Python: `requests`；Obsidian 库路径 |
| [cyxj-roundtable](./plugins/cyxj-roundtable/) | 召集 6 个 Claude Opus subagent 扮演对立角色（苏格拉底 / 严苛同行 / 带偏见投资人 / 历史学家 / 5 年后后悔的你 / 同盟者），多视角压测决策，会议记录自动存入 Obsidian | `/圆桌`、`开个圆桌`、`开圆桌`、`圆桌一下` | 无需额外 API key（通过 Claude Code 调用 Claude Opus）；Obsidian 库路径 |
| [cyxj-transcript](./plugins/cyxj-transcript/) | 把视频/录音逐字稿整理成文章草稿：去口语化、加小标题、数据转表格，原稿保留文末，产出 Obsidian Markdown | `转稿`、`逐字稿整理`、`把这个稿子整理成文章`、`口播稿成文` | Obsidian 库路径；无需 API key |
| [cyxj-blog-pub](./plugins/cyxj-blog-pub/) | 发布文章到 Astro 博客：校验 frontmatter、kebab-case 文件名、正文图片替换为图床 URL，build 后部署 | `发布到博客`、`发博客`、`博客发文`、`上博客`、`Astro 发布` | 本地配置好 Astro 博客仓库和图床；**部署目标是作者自己的服务器，使用前需修改** |
| [cyxj-video-doctor](./plugins/cyxj-video-doctor/) | 知识视频诊所（3 分钟+ 冲抖音精选），一个插件两个 skill 共享赛道真相单源：**cyxj-content**（六维内容诊断）+ **cyxj-hook**（开头/钩子诊断 + 四型方案） | `/内容诊断`、`帮我看看这条稿`、`/cyxj-hook`、`优化我的视频开头`、`开头钩子` | 无（纯指令型技能） |
| [cyxj-data-review](./plugins/cyxj-data-review/) | 抖音数据复盘诊断：围绕 KPI 链（收藏→涨粉→进精选）做证据驱动诊断，每条结论标【事实】【推断】【未知】 | `复盘我的数据`、`数据复盘`、`看看我最近数据`、`精选诊断` | 用户导出的抖音数据；无需 API key |
| [cyxj-jingxuan](./plugins/cyxj-jingxuan/) | 抖音精选申请文案：读成片字幕/逐字稿，按四段式（原创定性→深度证明→受众价值→平台对齐）写 150-250 字申请，每条理由可在视频中核验，数据不编 | `写精选申请`、`精选申请`、`申请精选`、`/cyxj-jingxuan` | 成片字幕/逐字稿；无需 API key |
| [cyxj-release-kit](./plugins/cyxj-release-kit/) | 视频发布物料一条龙：6 平台标题+简介 + HTML 封面工作台三比例出图（无字底图+浏览器排字，零错字零裁切）+ 上传 JPG | `发布物料`、`出发布包`、`六平台标题`、`封面工作台`、`/cyxj-release-kit` | 底图依赖 cyxj-image-studio（`GPTIMG2_*`）；浏览器（封面工作台） |
| [cyxj-audio-check](./plugins/cyxj-audio-check/) | 成片音频体检 + 修法:ffmpeg 量响度(LUFS)/真峰值/左右声道/BGM 比例/静音/码率,出放行表(可发/不可发);不可发给达芬奇菜单级修法(F1-F6),可 ffmpeg 应急修音轨或人声+BGM 自动闪避重混,修完自动复测 | `音频体检`、`查一下音频`、`这版能发吗`、`人声太小`、`BGM 太大`、`/cyxj-audio-check` | ffmpeg / ffprobe;Python `numpy` 可选(母带对齐) |

## 安装

在 Claude Code 中运行：

```
/plugin marketplace add chenyuxiaojin/xiaochen-skills
```

一条命令安装全部 14 个插件（16 个技能）。

## 使用方法

安装后，在 Claude Code 中输入触发词，对应技能会自动启动。例如：

```
YouTube 选题            → 启动 cyxj-youtube-topics
/圆桌                  → 启动 cyxj-roundtable
发布到公众号             → 启动 cyxj-wechat-pub
发布物料                → 启动 cyxj-release-kit
```

大多数技能无需加 `/` 前缀——输入触发词即可，Claude Code 会自动匹配。

## 对比同类

| | xiaochen-skills | [Anthropic 官方示例 Skills](https://github.com/anthropics/claude-code) | [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) 社区列表 |
|---|---|---|---|
| 定位 | 视频制作 + 公众号发布 + Obsidian 知识管理 | 通用示例和模式参考 | 社区技能链接汇总，非单一安装 |
| 技能数量 | 16 个技能 / 14 个插件 | 随示例变化 | 多仓库分散 |
| 安装方式 | 一条命令全量安装 | 手动复制文件 | 各仓库分别安装 |
| 多智能体 | 有（圆桌召集 6 个 Opus subagent） | 取决于示例 | 各异 |
| 脚本自动化 | 有（Python + Bash + Gemini + Apify） | 较少 | 各异 |
| 目标用户 | macOS 上的视频创作者 / 博主工作流 | 学习 Claude Code 的开发者 | 探索社区工作的开发者 |

## 常见问题

**怎么安装？**
在 Claude Code 里运行 `/plugin marketplace add chenyuxiaojin/xiaochen-skills`，14 个插件（16 个技能）全部注册。

**能只安装一个技能吗？**
可以。每个插件互相独立。如果 marketplace 支持单插件安装，可以按名称指定；也可以手动复制 `plugins/cyxj-{name}/` 目录并在自己的 marketplace.json 里注册。

**`cyxj-` 前缀是什么意思？**
这是作者的个人命名前缀，取自"陈与小金"的拼音首字母缩写，用于命名空间隔离，避免与其他插件冲突。前缀本身没有功能含义。

**哪些技能开箱即用？哪些需要配置？**

开箱即用（只需配置 Obsidian 库路径）：
- `cyxj-obsidian-build`、`cyxj-roundtable`、`cyxj-transcript`、`cyxj-video-doctor`（hook + content）、`cyxj-data-review`、`cyxj-jingxuan`

需要 API key 的技能：
- `cyxj-subfix` → `GEMINI_API_KEY`
- `cyxj-image-studio` → `GPTIMG2_BASE_URL`/`GPTIMG2_API_KEY`（两个 skill 共用）；poster 另需 `GEMINI_API_KEY`（文字扩写）
- `cyxj-youtube-topics` → `YOUTUBE_DATA_API_KEY` + `APIFY_API_TOKEN`（字幕）
- `cyxj-yt-creator` → `APIFY_API_TOKEN`
- `cyxj-release-kit` → 封面底图依赖 `cyxj-image-studio`（`GPTIMG2_*`）

**强绑作者本人环境、使用前必须改配置的技能**：
- `cyxj-blog-pub` — 部署目标是作者自己的 Astro 博客和服务器

**API key 存在哪里？**
作者的环境从 `~/项目/自己的应用/密钥存储/.env` 读取。你可以修改脚本，改成从自己的 `.env` 或环境变量读取。

## License

[MIT](LICENSE)
