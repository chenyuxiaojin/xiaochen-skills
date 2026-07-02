---
name: cyxj-wechat-pub
description: >
  将 Obsidian Markdown 文章转换为高质量公众号排版，内置 3 套 CSS 主题可选：
  TATALAB 蓝（默认）、炭黑暖金（深度/商务）、暖橙编辑（编辑/海报风）。
  支持内容审查、打磨、IP 配图生成、预览确认，输出可直接粘贴到微信后台。
  触发词：发布到公众号、公众号排版、微信发布、排版文章、XCYJ 排版。
version: 1.0.0
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

## Theme 选择

排版前先决定用哪个主题（默认 tatalab）：

| 主题文件 | 风格 | 适用题材 |
|---------|------|---------|
| `theme-tatalab.css` | 蓝色商务感（Material Blue 系：#1565C0 / #1976D2 / #BBDEFB） | AI 编程 / 运营干货 / 教程效率类，活泼亲和 |
| `theme-noir-gold.css` | 炭黑 + 暖金沉稳感（#26262A 炭灰 Hero + #8A6D1A 金棕强调 + #FAF6EC 米黄引用块） | AI 行业观察 / 深度分析 / 长稿，沉稳权威 |
| `theme-orange-editorial.css` | 暖橙 × 米黄编辑/海报风（#E8763C 橙 + #F2E6CC 米黄 + #2A1F18 深棕 + Bebas Neue + 2px 描边 + 6px 实心阴影 + 网点底纹） | AI 行业观察 / 大事件解读 / 海报式长稿，杂志/印刷感强 |

调用 juice 时把 `theme-tatalab.css` 替换成想要的主题文件名即可，其他流程不变。Phase 0 内容审查时顺便判定主题：技术/教程类默认 tatalab；行业观察/深度分析/商业评论类问用户是 noir-gold 还是 orange-editorial（orange-editorial 适合需要强视觉冲击、有数据 + 时间线 + 关键词 + 结论金句的长稿；noir-gold 适合更克制的深度评论）。

**orange-editorial 主题的强制结构约束**（详见文末「Orange Editorial Theme」节及其 references 文件，必须遵守，否则公众号会出白色断层）：
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

**Important**: You (Claude) are responsible for generating the HTML with correct class names. The converter only handles CSS inlining.

### Phase 3: IP 配图生成 + 上传

#### 3.1 题材识别与视觉方案匹配

先判断文章题材，自动匹配对应的视觉方案。这决定了插图和封面的场景、配色和构图方向：

| 文章题材 | 场景类型 | 配色倾向 | 构图 |
|---------|---------|---------|------|
| AI/科技 | 全息工作站、数据空间、未来城市 | 深蓝+霓虹青+品红边缘光（赛博朋克） | 居中对称，几何光环框架 |
| 读书/生活 | 咖啡馆、书房、窗边、秋日场景 | 暖琥珀金+奶油色+焦橙+深红（文艺暖调） | 三层景深（前景虚化→中景人物→背景环境） |
| 教程/干货 | 黑板、工具台、实验室、工作桌面 | 深色底+亮色重点标注（专业感） | 尺度对比，功能性构图 |
| 感悟/情感 | 自然场景、星空、海边、山顶 | 柔和渐变、淡彩（诗意感） | 负空间留白叙事 |
| 运营/商业 | 会议室、数据仪表盘、增长曲线 | 商务蓝+白+金色点缀（专业信任感） | 居中对称或黄金比例 |

将匹配到的场景、配色、构图描述融入图片生成 prompt，让每篇文章的配图氛围与内容匹配，而不是千篇一律的白底 3D 渲染。

#### 3.2 渲染风格选择

- **默认风格：3D Stylized Toon** — 保持 XCYJ 品牌 IP 一致性，适用于大多数文章
- **备选风格：水彩绘本风** — 适用于读书笔记、生活感悟、情感类文章。将小金 IP 画成柔和水彩/水墨插画风格，保留核心辨识特征（光头、蓝色卫衣、金链耳饰），但呈现为手绘绘本质感

选择哪种风格由文章气质决定：技术/教程/商业类用 3D Toon，文艺/读书/情感类可用水彩风。如果不确定，询问用户。

#### 3.3 图片生成引擎与凭据（GPTIMG2 / gpt-image-2）

所有 IP 配图（插图 + 封面）统一走 **gpt-image-2 @ GPTIMG2 中转站**（OpenAI 兼容协议）。

**生图凭据（两级查找，凭据说明只写在本节，其他小节一律引用这里）**：
1. **环境变量优先**：`GPTIMG2_BASE_URL`（= `https://api.chatgpt-code.com`，**末尾没有 `/v1`**）和 `GPTIMG2_API_KEY`
2. 环境变量未设置时，先 `set -a; source ~/项目/自己的应用/密钥存储/.env; set +a` 加载再继续（作者机器的约定路径；这个 .env 同时存放图床凭证 `LSKY_EMAIL` / `LSKY_PASSWORD`）。文件里没对应的 key，提示用户加。

**模型**：`gpt-image-2`（中文标题渲染准确率高，适合封面直接出字）。

**两个端点（按是否带 IP 参考图选）**：
- **带 IP 参考图（保小金形象一致）→ `{base}/v1/images/edits`**（multipart 表单，`image` 字段传 `ip-reference/xiaojin-spec-sheet.png`）。IP 配图默认走这个端点。
- **纯文生图（不需要小金形象，如纯场景图）→ `{base}/v1/images/generations`**（JSON body）。

**出图方式**：请求带 `response_format=url`，拿到返回 JSON 里的图片 url 后**先 `curl` 下载落地到本地临时文件**，再走下方「图床上传流程」上传公网。不要直接把中转站 url 写进 HTML（可能过期）。

**分辨率：默认 2K 出图**（公众号配图清晰度需要）。按构图比例选 `size`：
| 比例 | 用途 | `size` |
|------|------|--------|
| 16:9 | 横图配图（默认） | `2560x1440` |
| 4:3 | 横图配图（偏方） | `2048x1536` |
| 9:16 | 竖图配图 | `1440x2560` |

封面是 21:9 特殊规格，见 3.4。

**curl 示例 A — 带 IP 参考图（`/v1/images/edits`，IP 配图走这个）**：

```bash
# 凭据加载见上方「生图凭据」两级查找
SKILL_DIR="${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub"

curl -s -X POST "${GPTIMG2_BASE_URL}/v1/images/edits" \
  -H "Authorization: Bearer ${GPTIMG2_API_KEY}" \
  -F "model=gpt-image-2" \
  -F "image=@${SKILL_DIR}/ip-reference/xiaojin-spec-sheet.png" \
  -F "prompt=小金（光头、蓝色卫衣写着\"陈与小金\"、金链耳饰、蓝眼睛）站在全息工作站前，深蓝+霓虹青赛博朋克配色，居中对称构图，3D Stylized Toon 风格" \
  -F "size=2560x1440" \
  -F "n=1" \
  -F "response_format=url"
# 返回: {"data":[{"url":"https://.../xxxx.png"}]}
```

**curl 示例 B — 纯文生图（`/v1/images/generations`，无需小金形象时）**：

```bash
# 凭据加载见上方「生图凭据」两级查找
curl -s -X POST "${GPTIMG2_BASE_URL}/v1/images/generations" \
  -H "Authorization: Bearer ${GPTIMG2_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "暖琥珀金+奶油色的文艺暖调咖啡馆窗边场景，三层景深，柔和光线，水彩绘本风",
    "size": "2560x1440",
    "n": 1,
    "response_format": "url"
  }'
# 返回: {"data":[{"url":"https://.../xxxx.png"}]}
```

**拿到 url 后下载落地**：

```bash
IMG_URL=$(curl -s ... | python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['url'])")
curl -s -o /tmp/wechat-illust-1.png "$IMG_URL"
# 然后把 /tmp/wechat-illust-1.png 走下方图床上传流程
```

**插图生成步骤**：

1. 根据每个章节主题 + 上面匹配到的视觉方案，撰写 gpt-image-2 图片生成 prompt
2. 调用 `{base}/v1/images/edits` 端点，传入 IP 参考图（`ip-reference/xiaojin-spec-sheet.png`），用上面的 curl 示例 A；prompt 中包含题材对应的场景、配色、构图描述
3. 从返回 JSON 取 `data[0].url`，`curl` 下载到本地临时文件
4. 上传到 Lsky Pro 图床（见下方上传流程）
5. 在 HTML 中插入 `.img-card` 组件，使用图床返回的公网 URL

**IP 配图数量策略**：
- 短文章（<1500 字）且已有截图配图时，IP 配图只补无图章节，不要每章都插
- 先询问用户需要几张 IP 配图，不要自作主张

**IP 形象核心特征（每次生成必须强调）**：光头、蓝色卫衣写着"陈与小金"、金链耳饰、蓝眼睛。

**图床上传流程**（Lsky Pro - img.xiaochens.com）：

> 图床凭证 `LSKY_EMAIL` / `LSKY_PASSWORD` 按 3.3「生图凭据」的两级查找方式加载（同一个 .env 文件）。没有这两个 key 就提示用户加。

```bash
# 1. 获取 token
curl -s -X POST "https://img.xiaochens.com/api/v1/tokens" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$LSKY_EMAIL\",\"password\":\"$LSKY_PASSWORD\"}"
# 返回: {"data":{"token":"1|xxxxx"}}

# 2. 上传图片
curl -s -X POST "https://img.xiaochens.com/api/v1/upload" \
  -H "Authorization: Bearer {token}" \
  -F "file=@image.png"
# 返回: {"data":{"links":{"url":"https://img.xiaochens.com/i/2026/04/02/xxxxx.png"}}}
```

#### 3.4 封面生成

封面是文章的门面，必须同时包含 **IP 形象 + 文章标题文字**。

封面同样走 3.3 的 GPTIMG2 引擎、凭据和出图方式（`response_format=url` → 下载落地 → 图床上传）。因为封面必须含小金形象，**用 `{base}/v1/images/edits` 端点**（带 IP 参考图，curl 示例 A），在 prompt 中明确要求：
- IP 形象（小金）处于画面中，场景和配色按题材视觉方案
- **文章标题文字直接渲染在封面图上**，作为设计的一部分（不是后期叠加）。gpt-image-2 中文渲染准确率高，适合直接出标题字
- 标题文字要清晰可读，字体风格与画面氛围匹配
- 封面是 21:9 微信公众号规格，目标 1800x766。但 GPTIMG2 的 `size` 取离散档位，21:9 没有原生档——请求时用最接近的 16:9 `2560x1440`（2K，比例略宽），拿到图后再裁成 1800x766；或直接在 prompt 里要求 21:9 超宽构图。**不要回退到低分辨率出图**

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
4. Write to `/tmp/wechat-preview.html`
5. **打开预览给用户看**：`open /tmp/wechat-preview.html`（系统浏览器，用户可在底部点「复制到剪贴板」）
6. **可选：Claude 自验证排版**——Playwright MCP 不支持 file:// 协议，必须先起本地 http server：
   ```bash
   cd /tmp && python3 -m http.server 8765 &
   ```
   然后让 Playwright `navigate` 到 `http://localhost:8765/wechat-preview.html`，`browser_take_screenshot` 后用 `pkill -f "http.server 8765"` 关闭 server。
   - **截图 filename 必须用相对路径**，比如 `.playwright-mcp/skill-test.png` 或工作目录下的 `xxx.png`；写 `/tmp/xxx.png` 等绝对路径会被 MCP 以 `outside allowed roots` 拒绝。
   - 截图看完后 `rm -rf .playwright-mcp` 清理，避免污染工作区。
7. Ask: "排版满意吗？需要调整什么？"
8. If user wants changes, go back to Phase 2
9. 交接：文章发布后，若这篇想被 AI 搜索（豆包/DeepSeek/Kimi）引用，提示可用 `cyxj-geo` 出投放与监控方案


## Auto-Recognition Rules

When reading the Markdown, apply these rules to determine component mapping:

| Content Pattern | Component | Class |
|----------------|-----------|-------|
| Frontmatter has `title` and optional `subtitle` | Hero Banner | `.hero` |
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
- Use `<section>` instead of `<div>` - better semantic structure
- Use `<p class="list-item">` instead of `<ul><li>` for lists - more reliable rendering in WeChat
- Do NOT use `<thead>`, `<tbody>`, `<caption>` in tables - WeChat renders each as a separate empty table. Only use `<table><tr><th/td>` three-level structure
- 上传图片到 Lsky Pro 图床 `img.xiaochens.com`，通过 API 获取公网 URL
- 预览 HTML 用 `open` 命令打开系统浏览器，Playwright MCP 不支持 `file://` 协议
- 封面分辨率已更新为 1800x766（规格详见 3.4 节），不要改回低分辨率
- 最终产出是预览 HTML + 复制按钮，用户自行复制粘贴到微信后台发布

## Orange Editorial Theme — 专属规则（按需读取）

暖橙 × 米黄编辑/海报风，Bebas Neue + 2px 描边 + 6px 实心阴影，适合海报式长稿 / 大事件解读，杂志/印刷感强。

选 orange-editorial 主题时，**排版前必须先读**
`${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/references/orange-editorial.md`，
里面有：结构铁律（单根 `.article` + `.spacer` 占位，违反会出白色断层）、全部专属组件模板（hero-ticker / stat-callout / timeline / keyword-card / layer-list / growth / poster / prediction / divider-eyebrow 等）、专属 Auto-Recognition 补充表、排版前校验清单。

注意：orange 主题的 CSS 没有 `.img-scroll` 样式，**不要用 Scroll Gallery 组件**，多张同类图片改用多个 `.img-card`。其他主题忽略本节。
