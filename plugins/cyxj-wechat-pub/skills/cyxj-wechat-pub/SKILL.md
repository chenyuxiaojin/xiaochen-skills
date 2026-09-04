---
name: cyxj-wechat-pub
description: >
  将 Obsidian Markdown 文章转换为高质量公众号排版，内置 3 套 CSS 主题可选：
  TATALAB 蓝（默认）、炭黑暖金（深度/商务）、暖橙编辑（编辑/海报风）。
  支持内容审查、打磨、IP 配图生成、预览确认，输出可直接粘贴到微信后台。
  触发词：发布到公众号、公众号排版、微信发布、排版文章、XCYJ 排版。
version: 1.2.0
---

# XCYJ WeChat Publisher - 陈与小金公众号排版发布 Skill

## Files

- `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/theme-tatalab.css` - TATALAB 蓝色风格 CSS 主题（默认）
- `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/theme-noir-gold.css` - 炭黑 + 暖金风格 CSS 主题（深度内容/商务调性）
- `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/theme-orange-editorial.css` - 暖橙 × 米黄编辑/海报风 CSS 主题（杂志感长稿）
- `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/preview-template.html` - 预览 HTML 模板
- `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/package.json` - npm 依赖（仅 juice）
- `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/references/components.md` - 通用 HTML 组件模板（Phase 2 落 HTML 时按需读取）
- `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/references/orange-editorial.md` - orange-editorial 主题专属规则与组件（选该主题时必读）
- `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/references/illustration.md` - Phase 3 生图/图床/封面全流程（要配图时读）
- `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/ip-reference/xiaochen-glasses.png` - 现行 IP 参考图（眼镜插画版小陈；`deprecated/` 里是停用的旧图，不要用）

## Theme 选择

排版前先决定用哪个主题（默认 tatalab）：

| 主题文件 | 风格 | 适用题材 |
|---------|------|---------|
| `theme-tatalab.css` | 蓝色商务感（Material Blue 系：#1565C0 / #1976D2 / #BBDEFB） | AI 编程 / 运营干货 / 教程效率类，活泼亲和 |
| `theme-noir-gold.css` | 炭黑 + 暖金沉稳感（#26262A 炭灰 Hero + #8A6D1A 金棕强调 + #FAF6EC 米黄引用块） | AI 行业观察 / 深度分析 / 长稿，沉稳权威 |
| `theme-orange-editorial.css` | 米黄纸面编辑/海报风，橙做点缀（#F2E6CC 米黄底 + #2A1F18 深棕字 + #E8763C 橙只用于色带/大数字/阴影/小块 + #A6461A 深橙强调字 + Bebas Neue + 2px 描边 + 6px 实心阴影 + 网点底纹；橙底上一律深棕字 ≥4.5:1） | AI 行业观察 / 大事件解读 / 海报式长稿，杂志/印刷感强 |

调用 juice 时把 `theme-tatalab.css` 替换成想要的主题文件名即可，其他流程不变。Phase 0 内容审查时顺便判定主题：技术/教程类默认 tatalab；行业观察/深度分析/商业评论类问用户是 noir-gold 还是 orange-editorial（orange-editorial 适合需要强视觉冲击、有数据 + 时间线 + 关键词 + 结论金句的长稿；noir-gold 适合更克制的深度评论）。

**选了 orange-editorial 就必须先读**
`${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/references/orange-editorial.md`
（专属组件 hero-ticker / stat-callout / timeline / keyword-card / layer-list / growth / poster /
prediction / divider-eyebrow、Auto-Recognition 补充表、排版前校验清单都在里面）。

三条结构约束先记住，违反会让公众号出白色断层：
- 整篇文章（含 hero）必须包在**一个** `<section class="article">` 内
- 章节之间用 `<section class="spacer"></section>` 占位，不要用 margin
- 禁止用 `position: absolute`、`writing-mode: vertical-rl`、`transform: rotate(...)`

## Workflow

```
Obsidian .md
  -> Phase 0: 内容审查（判定是否需要扩写/去AI味/结构调整）
  -> Phase 1: 内容打磨（如需要，扩写/改写/Humanize）
  -> Phase 2: 结构分析 + 生成 HTML
  -> Phase 3: IP 配图生成 + 上传公网
  -> Phase 4: CSS 内联 + 预览确认（用户自行复制粘贴到微信后台）
```

### Phase 0: 内容审查（核心步骤）

读取 Obsidian MD 文件后，先做内容质量判定，不急着排版。

**判定维度**：
1. **完整度** — 是大纲/要点还是完整文章？如果只是几个要点，需要扩写
2. **AI 痕迹** — 是否有明显的 AI 生成特征？（夸大修辞、三段式、"值得注意的是"等）
3. **结构** — 章节划分是否合理？是否需要重组？
4. **篇幅** — 公众号文章通常 1500-3000 字，太短或太长都需要调整

**判定结果（向用户报告）**：
- **A. 内容就绪** -> 直接进入 Phase 2 排版
- **B. 需要扩写** -> 进入 Phase 1，Claude 基于要点扩写
- **C. 需要去 AI 味** -> 进入 Phase 1，调用 Humanizer-zh skill 处理（未安装 Humanizer-zh 则由 Claude 手动去 AI 味）
- **D. 需要扩写 + 去 AI 味** -> Phase 1 先扩写再 Humanize
- **E. 需要结构调整** -> 向用户建议章节重组方案，确认后进入 Phase 1

**关键**：判定结果必须告知用户，由用户决定是否处理，不自动执行。

### Phase 1: 内容打磨（按需执行）

根据 Phase 0 的判定结果：
- **扩写**：基于用户的要点/大纲，扩展为完整段落。保留用户原始表达，补充论据和过渡
- **去 AI 味**：调用 Humanizer-zh skill 处理，或手动调整措辞
- **结构调整**：按用户确认的方案重组

打磨完成后，输出完整 Markdown 文本给用户确认，确认后再进入排版。

### Phase 2: 结构分析 + 生成 HTML

1. 分析内容结构，按 **Auto-Recognition Rules** 匹配组件
2. 生成带 class 的 HTML（使用 `<section>` 标签，非 `<div>`）
3. 列表使用 `<p class="list-item">` 而非 `<ul><li>`（微信兼容）
4. 整体包裹在 `<section class="article">...</section>` 中
5. 排版落 HTML 时，按需读取 `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/references/components.md` 获取各组件的 HTML 模板；选 orange-editorial 主题时，还必须先读 `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/references/orange-editorial.md`
6. **正文不放文章大标题**：hero 里不出 `<h1>`，标题只在微信后台标题栏填。标题 / 摘要 / 封面在 Phase 4 预览页底部的「发布信息区」单独列出，不进复制区

**Important**: You (Claude) are responsible for generating the HTML with correct class names. The converter only handles CSS inlining.

### Phase 3: IP 配图生成 + 上传

需要 IP 配图 / 封面时，读
`${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/references/illustration.md`——
里面是题材↔视觉方案匹配表、渲染风格选择、GPTIMG2 引擎与凭据、两个端点的 curl 示例、
分辨率档位、图床上传流程、封面 21:9 规格。**不要凭印象拼 API 参数，以该文件为准。**

先问用户需要几张 IP 配图（短文章已有截图时只补无图章节），再动手。纯文字排版不配图时跳过本 Phase。

### Phase 4: CSS 内联 + 预览确认

1. Run juice to inline all CSS styles:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub && { [ -d node_modules ] || npm install; }
```

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub && node -e "
const juice = require('juice');
const fs = require('fs');
// 改这一行切换主题：theme-tatalab.css / theme-noir-gold.css / theme-orange-editorial.css
const css = fs.readFileSync('theme-tatalab.css', 'utf8');
const html = fs.readFileSync('/tmp/wechat-input.html', 'utf8');
fs.writeFileSync('/tmp/wechat-output.html', juice.inlineContent(html, css));
"
```

2. Read `preview-template.html`
3. Replace `{{CONTENT}}` with the juice-inlined HTML
4. 填底部「发布信息区」四个占位符（只在预览页显示，在 `#output` 之外，复制按钮抓不到）：
   - `{{TITLE}}`：文章标题（frontmatter `title`）
   - `{{DIGEST}}`：摘要，≤120 字（微信上限）。frontmatter 有 `digest` / `summary` 就用，没有则 Claude 起一段给用户确认
   - `{{COVER_21x9}}` / `{{COVER_16x9}}`：封面图**绝对路径**（预览放 /tmp 也能显示）；没做封面填「未生成」，图片加载失败会自动隐藏
5. Write to `/tmp/wechat-preview.html`
6. **打开预览给用户看**：`open /tmp/wechat-preview.html`（系统浏览器，用户可在底部点「复制到剪贴板」；标题 / 摘要 / 封面照发布信息区手动填到后台）
7. **可选：Claude 自验证排版**——Playwright MCP 不支持 file:// 协议，必须先起本地 http server：
   ```bash
   cd /tmp && python3 -m http.server 8765 &
   ```
   然后让 Playwright `navigate` 到 `http://localhost:8765/wechat-preview.html`，`browser_take_screenshot` 后用 `pkill -f "http.server 8765"` 关闭 server。
   - **截图 filename 必须用相对路径**，比如 `.playwright-mcp/skill-test.png` 或工作目录下的 `xxx.png`；写 `/tmp/xxx.png` 等绝对路径会被 MCP 以 `outside allowed roots` 拒绝。
   - 截图看完后 `rm -rf .playwright-mcp` 清理，避免污染工作区。
8. Ask: "排版满意吗？需要调整什么？"
9. If user wants changes, go back to Phase 2


## Auto-Recognition Rules

When reading the Markdown, apply these rules to determine component mapping:

| Content Pattern | Component | Class |
|----------------|-----------|-------|
| Frontmatter has `subtitle`（`title` 不进正文，只进预览页发布信息区） | Hero Banner（无 `<h1>`） | `.hero` |
| `## N. Title` or sequential `## Title` headings | Chapter Section | `.chapter` + `.chapter-num` + `.chapter-title` |
| `### Title` | Sub-heading with pill style | `h3` + `.pill` |
| Single short bold/italic sentence (<50 chars) standing alone | Quote | `.quote` |
| Multiple `**Keyword**: description` items in sequence | Knowledge Card | `.card` + `.card-item` |
| Bullet list where each item has `**Title**: description` | List Card | `.list-card` |
| Sequential `Name: "dialogue content"` patterns | Chat Bubbles | `.chat` + `.chat-item` |
| Final short emotional/inspirational sentence | Center Quote | `.center-quote` |
| `![alt](url)` image | Image Card | `.img-card` |
| Multiple consecutive images of the same category (2-4 images) | Scroll Gallery | `.img-scroll`（仅 tatalab / noir-gold；orange-editorial 禁用） |
| `---` horizontal rule | Divider | `hr` |
| Regular paragraph text | Body text | `p` |
| Paragraph with warning/danger/trap context, or preceded by ⚠️/💡 emoji | Callout | `.callout` + variant |
| Multiple sequential key points about rules/laws/tips in code/terminal context | Dark Card | `.card-dark` |
| Ordered steps where each has **bold title**: description | Steps List | `.steps` |
| 3-4 parallel short concepts/subcategories needing side-by-side display | Grid Cards | `.grid-cards` |
| Ordered/unordered lists (without special formatting) | List items | `p.list-item` |
| Code blocks | Code block | `pre` > `code` |
| Tables | Styled table | `table` |

## HTML 组件模板（按需读取）

上表匹配到组件后，排版落 HTML 时读取通用组件模板文件：
`${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/references/components.md`
——里面是 Hero / Chapter / Quote / Card / Chat Bubbles / Callout / Dark Card / Steps / Grid Cards 等全部通用组件的 HTML 结构（含固定 IP 标志的 Hero 作者区和 Footer 祝福语）。不要凭印象手写组件结构，以模板文件为准。

## Editorial Mindset

你是杂志排版编辑，不是 Markdown 转 HTML 的翻译器。每篇文章结构不同，组件选择靠编辑判断，不靠固定规则。

**核心思考流程（逐章扫一遍）**：
1. **读者此刻的情绪是什么？** 刚读完三段密集论述？需要视觉喘息点
2. **这段内容的最佳呈现形式是什么？** 同样是三个要点，知识卡片（`.card`）强调学习感，列表卡片（`.list-card`）强调并列感——选哪个取决于上下文语气
3. **这句话值不值得单独拎出来？** 引用卡片（`.quote`）要挑有画面感、有冲击力的金句，不要挑总结性的废话。读者扫到引用卡片时会停下来——你要对得起这个停顿
4. **长章节是否需要内部分隔？** 超过 4 段的章节考虑用药丸标签（`.pill`）切分子主题，打破视觉单调
5. **加粗用在哪？** 只点关键词（2-4 个字），不要加粗整句话。加粗是手指点一下的力度，不是一拳打过去

**节奏公式**：密集文字（2-3 段）→ 视觉组件喘气 → 密集文字 → 视觉组件 → ...
- 避免连续 4+ 段纯文字
- 避免连续 2 个视觉组件紧挨（会显得碎）

**铁律**：
- 文字一字不动——只改 HTML 标签结构，原文整段搬运，不能缩写、改词、调顺序
- 排版是为内容服务的，不是为了好看而好看

## WeChat Compatibility Notes

- All styles MUST be inlined via juice (WeChat strips `<style>` tags)
- Use `<table>` for chat bubbles instead of flex layout
- Avoid CSS pseudo-elements (::before, ::after) - use real HTML elements
- `box-shadow` and `border-radius` work in modern WeChat
- External images in `<img src>` will be auto-fetched by WeChat CDN when pasted
- `linear-gradient` works in WeChat for backgrounds
- Do NOT use `position: absolute/fixed` - WeChat may strip these
- Keep all widths relative (%, auto) - avoid fixed px widths except for small elements
- Do NOT use `<thead>`, `<tbody>`, `<caption>` in tables - WeChat renders each as a separate empty table. Only use `<table><tr><th/td>` three-level structure

