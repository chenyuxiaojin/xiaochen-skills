**English** | [中文文档](README.zh-CN.md)

# xiaochen-skills

> xiaochen-skills is a Claude Code plugin marketplace bundling 15 plugins (17 skills) for video production, content publishing, and knowledge management.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-blueviolet)](https://claude.ai/code)

## Why

Claude Code's built-in skills cover general tasks. This collection adds a vertical layer for a specific workflow: **video production → content publishing → personal knowledge management**. Each skill is a self-contained plugin — install one or all.

## Skills

| Skill | What it does | Trigger phrases | Dependencies |
|-------|-------------|-----------------|--------------|
| [cyxj-subfix](./plugins/cyxj-subfix/) | Fix ASR subtitles from DaVinci Resolve: SRT cleanup → Gemini semantic correction → Claude Opus review | `/字幕修正`, `修正字幕`, `字幕错别字`, `SRT 修正` | `GEMINI_API_KEY`; Python: `google-genai`, `pysrt` |
| [cyxj-wechat-pub](./plugins/cyxj-wechat-pub/) | Convert Obsidian Markdown to WeChat Official Account HTML with 3 built-in CSS themes (TATALAB blue / noir-gold / orange editorial) | `发布到公众号`, `公众号排版`, `微信发布`, `排版文章` | npm: `juice`; WeChat backend access |
| [cyxj-obsidian-build](./plugins/cyxj-obsidian-build/) | Compile an Obsidian vault into a 3-tier knowledge architecture (Ingest / Query / Lint) inspired by Karpathy's LLM Wiki methodology | `整理 Obsidian`, `编译知识库`, `摄入笔记`, `查知识库`, `健康度检查` | Obsidian vault path configured; no API key |
| [cyxj-image-studio](./plugins/cyxj-image-studio/) | Image studio (gpt-image-2), one plugin with two skills sharing credential loading: **cyxj-poster** (master-level poster / book cover / album art, 33+ designer + 10 photography styles) and **cyxj-video-cover** (real-person video thumbnails from your photo, 4 aspect ratios; can borrow poster's style library) | `生成海报`, `封面设计`, `/封面`, `生成封面`, `做个视频封面` | `GPTIMG2_BASE_URL`/`GPTIMG2_API_KEY`; poster additionally `GEMINI_API_KEY` + Python `requests`, `google-genai`, `pillow`; video-cover is stdlib-only (Pillow optional) |
| [cyxj-youtube-topics](./plugins/cyxj-youtube-topics/) | Discover YouTube videos published in the last 48 hours on a topic, cluster by theme, score each with verdict (make / wait / follow / skip), write to Obsidian topic library | `选题`, `找选题`, `YouTube 最近有什么`, `有什么新视频` | `YOUTUBE_DATA_API_KEY`; Python: `requests`; Obsidian vault path |
| [cyxj-yt-creator](./plugins/cyxj-yt-creator/) | Research how YouTubers cover a tool/topic via Apify: fetch transcripts, rank by date/views, write differentiation notes to Obsidian draft queue | `查博主怎么用`, `用 Apify 搜 YouTube`, `研究这个工具的 YouTube 视频` | `APIFY_API_TOKEN`; Python: `requests`; Obsidian vault path |
| [cyxj-notebook-research](./plugins/cyxj-notebook-research/) | Submit videos from Obsidian topic library to Google Notebook LM in batch, pull transcripts and research reports back to Obsidian | `帮我研究一下 XXX 话题`, `研究一下这个选题`, `把选题提交给 Notebook LM` | Google account with Notebook LM access; Python: `notebooklm-py`, `python-frontmatter`; `CYXJ_VAULT_BASE` env var |
| [cyxj-geo](./plugins/cyxj-geo/) | Generative Engine Optimization: keyword matrix → article brief → cross-platform publishing list → monitoring SOP so your name/product appears in AI answers | `做 GEO`, `让豆包/DeepSeek/Kimi 提到我`, `AI 时代 SEO`, `个人 IP 出现在 AI 回答里` | No API key required (instruction-only skill) |
| [cyxj-roundtable](./plugins/cyxj-roundtable/) | Convene 6 independent Claude Opus subagents playing adversarial roles (Socrates / harsh peer / biased investor / historian / future-regretful-you / ally) to pressure-test a decision; save to Obsidian | `/圆桌`, `开个圆桌`, `开圆桌`, `/roundtable` | No extra API key (uses Claude Opus via Claude Code); Obsidian vault path |
| [cyxj-ai-weekly-news](./plugins/cyxj-ai-weekly-news/) | End-to-end 9-step SOP for a weekly AI news video: news selection → narration → timecodes → 4K render in DaVinci Resolve; pauses at each human decision point | `/AI每周热点`, `/做下一期`, `/每周AI视频`, `做这周的 AI 视频` | DaVinci Resolve installed locally; Obsidian vault path; **video project path is hardcoded to author's machine — must be updated before use** |
| [cyxj-transcript](./plugins/cyxj-transcript/) | Turn a raw transcript (video voiceover, recording transcription) into a structured article draft: de-spoken, headings added, data tabulated, original preserved at the end — outputs Obsidian Markdown | `转稿`, `逐字稿整理`, `把这个稿子整理成文章`, `口播稿成文` | Obsidian vault path; no API key |
| [cyxj-blog-pub](./plugins/cyxj-blog-pub/) | Publish an article to an Astro blog: validate frontmatter, enforce kebab-case filenames, replace images with CDN URLs, then build and deploy | `发布到博客`, `发博客`, `博客发文`, `上博客`, `Astro 发布` | Astro blog repo configured locally; image CDN configured; **deploy target is author's server — must be updated before use** |
| [cyxj-psjpg](./plugins/cyxj-psjpg/) | Batch-export images to JPG using real local Photoshop (quality configurable, sRGB embedded, Progressive), then strip XMP metadata that reveals PNG/AI-generated origin | `/批量过PS`, `/PS批处理`, `/转jpg`, `png 转 jpg`, `封面转 jpg`, `去掉图片的转换痕迹` | **Adobe Photoshop installed locally (macOS)**; `exiftool` on PATH |
| [cyxj-video-doctor](./plugins/cyxj-video-doctor/) | Knowledge-video clinic (3-min+ aimed at Douyin featured), one plugin with two skills sharing a single track-truth reference: **cyxj-content** (six-dimension content diagnosis) and **cyxj-hook** (opening-hook diagnosis + 4 hook archetypes) | `/内容诊断`, `帮我看看这条稿`, `/cyxj-hook`, `优化我的视频开头`, `开头钩子` | None (instruction-only skills) |
| [cyxj-data-review](./plugins/cyxj-data-review/) | Evidence-driven Douyin analytics review around the KPI chain (saves → followers → featured); every conclusion tagged 【事实】【推断】【未知】 | `复盘我的数据`, `数据复盘`, `看看我最近数据`, `精选诊断` | Douyin analytics export from the user; no API key |

## Install

In Claude Code, run:

```
/plugin marketplace add chenyuxiaojin/xiaochen-skills
```

To install a single plugin only, you can reference it individually once the marketplace supports per-plugin install (check Claude Code docs for current status).

## Usage

After installation, each skill is triggered automatically when you type its trigger phrases in Claude Code. Examples:

```
选题                          → runs cyxj-youtube-topics
/圆桌                         → runs cyxj-roundtable
发布到公众号                    → runs cyxj-wechat-pub
/批量过PS                      → runs cyxj-psjpg
```

No slash command prefix is required for most skills — the trigger phrases listed in the table above are matched by Claude Code automatically.

## Compared to alternatives

| | xiaochen-skills | [anthropic/claude-code-skills](https://github.com/anthropics/claude-code) (official examples) | [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) community list |
|---|---|---|---|
| Focus | Video production + WeChat publishing + Obsidian knowledge management | General-purpose demos and patterns | Curated links to many community skills |
| Skill count | 17 skills / 15 plugins | Varies (reference examples) | Many repos, not a single install |
| Install method | Single `/plugin marketplace add` command | Copy individual files | Each repo installs separately |
| Multi-agent | Yes (roundtable spawns 6 Opus subagents) | Depends on example | Varies |
| Script automation | Yes (Python + Bash, Photoshop, Gemini, Apify) | Minimal | Varies |
| Audience | Video creator / blogger workflow on macOS | Developers learning Claude Code | Developers exploring community work |

## FAQ

**How do I install?**
Run `/plugin marketplace add chenyuxiaojin/xiaochen-skills` inside Claude Code. All 15 plugins (17 skills) are registered.

**Can I install only one skill?**
Yes. Each plugin is self-contained. You can install a single plugin by specifying the plugin name if the marketplace supports it, or copy the individual `plugins/cyxj-{name}/` directory and register it in your own marketplace.

**What does `cyxj-` mean?**
It is the author's personal naming prefix — short for "陈与小金" (Chen Yu Xiaojin), a Chinese content creator. The prefix has no functional meaning; it just namespaces skills to avoid conflicts.

**Which skills work out of the box and which need configuration?**

Skills that work with minimal setup (only Obsidian vault path needed):
- `cyxj-obsidian-build`, `cyxj-geo`, `cyxj-roundtable`, `cyxj-transcript`, `cyxj-video-doctor` (hook + content), `cyxj-data-review`

Skills that require API keys:
- `cyxj-subfix` → `GEMINI_API_KEY`
- `cyxj-image-studio` → `GPTIMG2_BASE_URL`/`GPTIMG2_API_KEY` (both skills); poster additionally `GEMINI_API_KEY` (文字扩写)
- `cyxj-youtube-topics` → `YOUTUBE_DATA_API_KEY`
- `cyxj-yt-creator` → `APIFY_API_TOKEN`
- `cyxj-notebook-research` → Google account with Notebook LM access

Skills with **hardcoded paths or dependencies tied to the author's machine** — you must update paths before use:
- `cyxj-ai-weekly-news` — project path is hardcoded to `~/项目/试験区/ai-weekly-flash-video`
- `cyxj-blog-pub` — deploy target is the author's Astro blog and server
- `cyxj-psjpg` — requires **Adobe Photoshop** installed on macOS and `exiftool` in PATH

**Where are API keys stored?**
The author's setup reads keys from `~/项目/自己的应用/密钥存储/.env`. You can adapt the scripts to read from your own `.env` or environment variables.

## License

[MIT](LICENSE)
