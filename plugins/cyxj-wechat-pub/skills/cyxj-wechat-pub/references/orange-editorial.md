# Orange Editorial Theme — 专属规则与组件

> 本文件属于 cyxj-wechat-pub skill。选了 `theme-orange-editorial.css` 时，按这一份走。其他主题忽略本文件。
>
> ⚠️ **orange 主题不要用 `.img-scroll` 组件**（Scroll Gallery）——`theme-orange-editorial.css` 里没有它的样式，
> 排出来会裸奔。多张同类图片直接用多个 `.img-card` 竖排。

## 结构铁律（违反就出白色断层）

公众号编辑器会在所有相邻的 `<section>` 兄弟元素之间强行插入白色间隙，所以这个主题的 HTML 必须长这样：

```html
<section class="article">
  <section class="hero">
    <!-- ticker / corner / title / subtitle / author 全部塞在 hero 内部 -->
    <section class="hero-bleed"></section>
    <section class="hero-bleed-cream"></section>
  </section>
  <section class="body">
    <!-- 所有正文段落 + 章节 + 配图 + 后记 + footer 都在 body 这一个 section 内 -->
    <p>段落...</p>
    <section class="spacer"></section>
    <section class="chapter">...</section>
    <p>段落...</p>
    <!-- ... -->
    <section class="footer-card">...</section>
  </section>
</section>
```

**不要做的事**：
- 不要把 hero 之后的章节 / 后记拆成 `.article` 的多个兄弟 `<section>`
- 不要用 `margin-top` 给章节之间留白——用 `<section class="spacer"></section>` 占位（内部填充米色背景，避免兄弟间隙）
- 不要把 `.body` 嵌套到 `.hero` 里面（嵌套之后 hero 橙色背景会被 WeChat 剥掉）
- 不要用 `position: absolute` / `writing-mode: vertical-rl` / `transform: rotate(180deg)`，公众号统统不支持

## Orange Editorial 专属组件模板

下面列的组件除了基础的 `.quote / .card / .img-card / .callout` 已在通用组件模板
（`${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/references/components.md`）里定义过，
其他都是这个主题专属，仅在 `theme-orange-editorial.css` 里有定义。

### Hero（杂志封面式）

```html
<section class="hero">

  <section class="hero-ticker">WRAPPER · MODEL · PRODUCT · WRAPPER · MODEL · PRODUCT</section>

  <section class="hero-corner">
    <section class="hero-issue">
      <span class="hero-issue-dash"></span>
      ISSUE 03 / 2026.05
    </section>
    <section class="hero-cat">{TAG}</section>
  </section>

  <section class="hero-title">
    <h1>{标题第一行}<br>{标题第二行}<span class="hero-title-arrow">→</span></h1>
  </section>

  <section class="hero-subtitle">
    <section class="hero-eyebrow">STUCK BETWEEN<br>MODEL & WRAPPER</section>
    <section class="hero-deck">{中文副标，1-2 句话讲清楚文章在说什么}</section>
  </section>

  <section class="hero-author">
    <section class="hero-ip"><img src="{头像 CDN}" alt="陈与小金"></section>
    <section class="hero-byline">
      <section class="hero-byline-label">BYLINE / 作者</section>
      <section class="hero-author-name">陈与小金</section>
    </section>
    <section class="hero-author-tags">AI 编程<br>运营干货<br>效率提升</section>
  </section>

  <section class="hero-bleed"></section>
  <section class="hero-bleed-cream"></section>
</section>
```

每篇文章只换 `TAG`、ISSUE 号、ticker 内容、标题、eyebrow（英文小标）、deck（中文副标），其他保持不变。

### Chapter（章节大头）

```html
<section class="chapter">
  <section class="chapter-num">01</section>
  <section class="chapter-right">
    <section class="chapter-tag">CHAPTER ONE</section>
    <section class="chapter-title">{中文小标题}</section>
  </section>
</section>
```

反色变体（用于结论 / 总结章节，黑底橙数字）：

```html
<section class="chapter chapter-dark">...</section>
```

### Spacer（章节之间的米色占位）

```html
<section class="spacer"></section>
```

每个 chapter 之前都加一个 spacer，撑出 36px 米色呼吸区。

### Pull Quote（金句 / 引言）

```html
<section class="quote">
  <section class="quote-mark">"</section>
  <section class="quote-text">{金句正文}</section>
</section>
```

注意这里跟其他主题的 `.quote` 不一样：橙色编辑风用 flex 两列布局，左列大引号，右列引文。

### Stat Callout（双栏数据对比）

```html
<section class="stat-callout">
  <section class="stat-row">
    <section class="stat-cell">
      <section class="stat-label">ANTHROPIC</section>
      <section class="stat-value">34.44%</section>
    </section>
    <section class="stat-cell">
      <section class="stat-label">OPENAI</section>
      <section class="stat-value">32.30%</section>
    </section>
  </section>
  <section class="stat-footnote">{数据来源 / 时间 / 样本说明}</section>
</section>
```

### List Card（票据风 dashed 分隔的编号列表）

```html
<section class="list-card">
  <p class="list-item"><span class="list-num">01</span>OpenAI 创始成员</p>
  <p class="list-item"><span class="list-num">02</span>特斯拉前 AI 总监</p>
  <p class="list-item"><span class="list-num">03</span>斯坦福读博时的导师是李飞飞</p>
</section>
```

### Timeline（时间线表格，最新行高亮）

```html
<section class="timeline">
  <section class="timeline-head">
    <section class="timeline-head-year">YEAR</section>
    <section class="timeline-head-event">EVENT / 事件</section>
  </section>
  <section class="timeline-row">
    <section class="timeline-year">2015</section>
    <section class="timeline-event">OpenAI 成立，他是联合创始人之一</section>
  </section>
  <section class="timeline-row">
    <section class="timeline-year">2017.06</section>
    <section class="timeline-event">被挖到特斯拉，直接向马斯克汇报</section>
  </section>
  <section class="timeline-row timeline-row-current">
    <section class="timeline-year">2026.05.19</section>
    <section class="timeline-event">加入 Anthropic 预训练团队 →</section>
  </section>
</section>
```

最新 / 当前事件加 `.timeline-row-current`，会变橙底反白。

### Keyword Card（黑底橙阴影的概念锚点）

```html
<section class="keyword-card">
  <section class="keyword-label">KEYWORD 01 →</section>
  <section class="keyword-text">VIBE CODING</section>
</section>
```

如果要带中英对照（如 LLM WIKI / 大模型 WIKI）：

```html
<section class="keyword-card">
  <section class="keyword-label">KEYWORD 02 →</section>
  <section class="keyword-text">LLM WIKI<br><span class="keyword-sub">大模型 WIKI</span></section>
</section>
```

### Layer List（洋葱式 L1-L4 分层）

```html
<section class="layer-list">
  <section class="layer">
    <section class="layer-num">L1</section>
    <section class="layer-body">
      <section class="layer-eyebrow">FIRST LAYER</section>
      <section class="layer-title">命令行工具，比如 Claude Code</section>
    </section>
  </section>
  <section class="layer">
    <section class="layer-num">L2</section>
    <section class="layer-body">
      <section class="layer-eyebrow">SECOND LAYER</section>
      <section class="layer-title">Skills、子智能体、Agent Teams</section>
    </section>
  </section>
  <section class="layer layer-outer">
    <section class="layer-num">L4</section>
    <section class="layer-body">
      <section class="layer-eyebrow">OUTER LAYER →</section>
      <section class="layer-title">记忆 + CLAUDE.md 文件——给模型的上下文</section>
    </section>
  </section>
</section>
```

最外层加 `.layer-outer` 变成橙底反白，强调"最重要的一层"。

### Growth（增长可视化，简易横条形）

```html
<section class="growth">
  <section class="growth-head">
    <section class="growth-head-date">DATE</section>
    <section class="growth-head-share">ANTHROPIC SHARE / 采纳率</section>
  </section>
  <section class="growth-row">
    <section class="growth-date">2023.06</section>
    <section class="growth-bar-cell">
      <section class="growth-bar" style="width:2px;"></section>
      <section class="growth-value">0.003%</section>
    </section>
  </section>
  <section class="growth-row">
    <section class="growth-date">2025.04</section>
    <section class="growth-bar-cell">
      <section class="growth-bar" style="width:46px;"></section>
      <section class="growth-value">7.94%</section>
    </section>
  </section>
  <section class="growth-row growth-row-current">
    <section class="growth-date">2026.04</section>
    <section class="growth-bar-cell">
      <section class="growth-bar" style="width:200px;max-width:60%;"></section>
      <section class="growth-value">34.44%</section>
    </section>
  </section>
</section>
```

横条宽度按数据比例手工算（行内 style 写 width），最新一行加 `.growth-row-current`。

### Poster（海报式中央大字块）

```html
<section class="poster">
  <section class="poster-eyebrow">→ THE NAME IS</section>
  <section class="poster-text">WRAPPER</section>
  <section class="poster-cn">套　壳</section>
</section>
```

结论 / verdict 强力变体（中文大字，英文做补充）：

```html
<section class="poster poster-verdict">
  <section class="poster-eyebrow">→ THE VERDICT</section>
  <section class="poster-text">套壳<br>才是产品</section>
  <section class="poster-cn">WRAPPER IS THE PRODUCT</section>
</section>
```

### Callout（黑底 takeaway）

```html
<section class="callout callout-dark">
  <section class="callout-title">→ TAKEAWAY</section>
  <p>{重要结论 / 一句话总结}</p>
</section>
```

普通米色 callout 用 `<section class="callout">...</section>`；橙色编辑风默认就有 6px 实心阴影。

### Prediction（橙表头预测卡）

```html
<section class="prediction">
  <section class="prediction-head">
    <section class="prediction-label">PREDICTION 01</section>
    <section class="prediction-title">{预测主题}</section>
  </section>
  <section class="prediction-body">
    <p>{核心论点}</p>
    <p class="prediction-note">{补充说明，灰色小字}</p>
  </section>
</section>
```

### Divider Eyebrow（横线 + 小标 + 横线，用于段落分隔）

```html
<section class="divider-eyebrow">
  <section class="divider-eyebrow-line"></section>
  <section class="divider-eyebrow-label">P.S. / 后记</section>
  <section class="divider-eyebrow-line"></section>
</section>
```

### Center Quote（结尾感言 + 箭头）

```html
<section class="center-quote">
  <section class="center-quote-arrows">→ → →</section>
  <section class="center-quote-text">本期就到这里。<br>如果对你有帮助，欢迎评论转发。</section>
</section>
```

### Footer Card（黑底 sign-off）

```html
<section class="footer-card">
  <section class="footer-head">— SIGN OFF —</section>
  <section class="footer-body">
    <section class="footer-label">SIGNED</section>
    <section class="footer-author">陈与小金</section>
    <section class="footer-desc">祝你身体健康，永远平安。<br>祝你 Token 无限，永远自由。</section>
    <section class="footer-sign-row">
      <section class="footer-sign-line"></section>
      <section class="footer-sign">{2026 · 05 · 23}</section>
      <section class="footer-sign-line"></section>
    </section>
    <section class="footer-thanks">THANKS FOR READING →</section>
  </section>
</section>
```

### End Ticker（最后一条跑马灯字条）

```html
<section class="ticker-end">
  WRAPPER · MODEL · PRODUCT · WRAPPER · MODEL · PRODUCT · END
</section>
```

放在 footer-card 之后，作为整篇文章的视觉收束。

## Orange Editorial 专属 Auto-Recognition（补充）

在通用 Auto-Recognition Rules 基础上，遇到下列模式优先选橙色编辑风专属组件：

| 内容模式 | 选哪个组件 |
|---------|----------|
| 两个对比数字（如 X% vs Y%）| `.stat-callout` |
| 一个"概念单词 + 中文释义"作为本章关键词 | `.keyword-card` |
| 多个时间点 + 事件描述（含最新事件）| `.timeline` + 最新行加 `.timeline-row-current` |
| 同一指标在多个时间点的数值变化 | `.growth` |
| 分层 / 嵌套结构（L1/L2/L3 等）| `.layer-list` |
| 三条左右的预测 / 推断 | `.prediction` 每条一卡 |
| 单独成段、需要"大字"视觉冲击的概念词或结论 | `.poster`（中段）/ `.poster poster-verdict`（结论） |
| 一段"重点结论 / 一句话总结" | `.callout callout-dark` 加 `→ TAKEAWAY` 标签 |
| 后记 / P.S. 分隔 | `.divider-eyebrow` |
| 文章首尾的"杂志感"字条 | `.hero-ticker`（首）+ `.ticker-end`（尾） |
| 多张同类图片 | ❌ 不要用 `.img-scroll`（本主题 CSS 无此样式），改用多个 `.img-card` |

## Orange Editorial 校验清单

排完版准备调 juice 之前，对照下面这张清单检查一遍：

- [ ] 整篇 HTML 是 `<section class="article">` 一个根节点，hero 和 body 都在它内部
- [ ] body 内所有章节都是同一个 `<section class="body">` 的子元素，没有把章节拆成 `.article` 的兄弟
- [ ] 章节之间是 `<section class="spacer"></section>`，不是 margin
- [ ] grep 一遍 HTML，确认没有 `position: absolute`、`writing-mode`、`transform: rotate`
- [ ] hero 末尾有 `.hero-bleed` + `.hero-bleed-cream` 两块米色压底（缓冲 WeChat 间隙）
- [ ] body 开头有 `border-top: 30px solid #F2E6CC`（CSS 里已写好，HTML 别覆盖）
- [ ] 文章开头确认有橙底网点的 hero，结尾确认有 footer-card + ticker-end
- [ ] 全文没有出现 `.img-scroll` / `.img-scroll-track` / `.img-scroll-item`
