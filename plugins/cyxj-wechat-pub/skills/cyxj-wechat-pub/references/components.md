# 通用 HTML 组件模板（HTML Component Templates）

> 本文件属于 cyxj-wechat-pub skill。Phase 2 排版落 HTML 时，按 SKILL.md 的
> Auto-Recognition Rules 匹配到组件后，来这里取对应的 HTML 模板。
> 这些是三套主题通用的组件；orange-editorial 主题的专属组件在
> `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-wechat-pub/references/orange-editorial.md`。
> ⚠️ Scroll Gallery（`.img-scroll`）只有 tatalab / noir-gold 两套主题有样式，orange-editorial 不能用。

## Hero Banner
```html
<section class="hero">
  <section class="hero-top">
    <section class="hero-tag">{TAG}</section>
    <h1>{title}</h1>
    <section class="hero-line"></section>
    <p class="hero-subtitle">{subtitle}</p>
    <section class="hero-author">
      <section class="hero-ip"><img src="https://img.xiaochens.com/i/2026/03/21/69be46623a45d.png" alt="陈与小金"></section>
      <section>
        <section class="hero-author-name">陈与小金</section>
        <section class="hero-author-tags">
          <section class="hero-author-tag">AI 编程</section>
          <section class="hero-author-tag">运营干货</section>
          <section class="hero-author-tag">效率提升</section>
        </section>
      </section>
    </section>
  </section>
</section>
```

**Hero 作者区是固定 IP 标志**，每篇文章不变。只替换 `{TAG}`、`{title}`、`{subtitle}`。

## Chapter Section
```html
<section class="chapter">
  <section class="chapter-num">01</section>
  <section class="chapter-tag">CHAPTER ONE</section>
  <section class="chapter-title">{title}</section>
</section>
```

Chapter tag English mapping (use these or similar):
- 01: CHAPTER ONE
- 02: CHAPTER TWO
- 03: CHAPTER THREE
- 04: CHAPTER FOUR
- 05: CHAPTER FIVE
- 06+: CHAPTER {N}

## Sub-heading with Pill
```html
<h3><span class="pill">{title}</span></h3>
```

## Quote (Golden Sentence)
```html
<section class="quote">
  <p>{content}</p>
</section>
```

## Knowledge Card
```html
<section class="card">
  <section class="card-title">{optional title}</section>
  <section class="card-item"><strong>{key}</strong>: {description}</section>
  <section class="card-item"><strong>{key}</strong>: {description}</section>
</section>
```

## List Card
```html
<section class="list-card">
  <p class="list-item"><strong>{title}</strong>: {description}</p>
  <p class="list-item"><strong>{title}</strong>: {description}</p>
</section>
```

## Image Card
```html
<section class="img-card">
  <img src="{url}" alt="{alt}">
  <section class="img-caption">{alt text as caption}</section>
</section>
```

## Scroll Gallery (横向滑动图片组)
```html
<section class="img-scroll">
  <section class="img-scroll-track">
    <section class="img-scroll-item">
      <img src="{url1}" alt="{alt1}">
      <section class="img-caption">{caption1}</section>
    </section>
    <section class="img-scroll-item">
      <img src="{url2}" alt="{alt2}">
      <section class="img-caption">{caption2}</section>
    </section>
    <section class="img-scroll-item">
      <img src="{url3}" alt="{alt3}">
      <section class="img-caption">{caption3}</section>
    </section>
  </section>
  <p class="img-scroll-hint">← 左右滑动查看 →</p>
</section>
```

适用场景：多张同类截图（如 Notion 截图、对比图等），避免竖排堆叠占据过多篇幅。
**仅限 tatalab / noir-gold 主题**——orange-editorial 的 CSS 没有 `.img-scroll` 样式，该主题下改用多个 `.img-card`。

## Chat Bubbles (Table-based for WeChat compatibility)
```html
<table class="chat-table" cellpadding="0" cellspacing="0">
  <tr>
    <td class="avatar-cell">
      <section class="avatar">{first letter}</section>
    </td>
    <td>
      <section class="chat-name">{name}</section>
      <section class="chat-bubble">{content}</section>
    </td>
  </tr>
  <tr>
    <td class="avatar-cell">
      <section class="avatar">{first letter}</section>
    </td>
    <td>
      <section class="chat-name">{name}</section>
      <section class="chat-bubble">{content}</section>
    </td>
  </tr>
</table>
```

## Center Quote (Ending)
```html
<section class="center-quote">{content}</section>
```

## Footer Card (固定 IP 标志)
```html
<section class="footer-card">
  <section class="footer-author">我是<strong>陈与小金</strong></section>
  <section class="footer-desc">祝你身体健康，永远平安。<br>祝你 Token 无限，永远自由。</section>
  <section class="footer-sign">— {日期} —</section>
  <section class="footer-thanks">THANKS FOR READING</section>
</section>
```

**Footer 是固定 IP 标志**，祝福语不变，只替换 `{日期}`（格式：`2026.03.21`）。

## Callout (Functional Tip / Warning)
```html
<section class="callout callout-warn">
  <section class="callout-title">⚠️ 危险陷阱：均值回归</section>
  <p>内容文字...</p>
</section>
```

Variants:
- Default (`.callout`): 蓝色左边框 + 浅蓝底，一般提示
- Warning (`.callout-warn`): 琥珀色左边框 + 浅黄底，陷阱/危险
- Tip (`.callout-tip`): 绿色左边框 + 浅绿底，最佳实践

与 `.quote` 的区别：quote 是金句/引用（偏文学感），callout 是功能性提示（偏信息感），callout 带标题行。

## Dark Card (Terminal / Core Rules)
```html
<section class="card-dark">
  <section class="card-dark-title">Skills 避坑与高阶法则</section>
  <p class="card-dark-item">➜ 不要安装太多。选项越多越难触发。</p>
  <p class="card-dark-item">➜ 用斜杠手动触发最可靠。</p>
</section>
```

## Steps List (Numbered Steps)
```html
<table class="steps" cellpadding="0" cellspacing="0">
  <tr>
    <td class="step-num-cell"><section class="step-num">1</section></td>
    <td><p class="step-text"><strong>学会写清晰具体的提示词。</strong> 围绕目标去写具体功能。</p></td>
  </tr>
  <tr>
    <td class="step-num-cell"><section class="step-num">2</section></td>
    <td><p class="step-text"><strong>学会评估输出。</strong> 你得知道好的长什么样。</p></td>
  </tr>
</table>
```

## Grid Cards (Parallel Concepts)
```html
<table class="grid-cards" cellpadding="0" cellspacing="0">
  <tr>
    <td class="grid-card">
      <section class="grid-card-tag">01</section>
      <section class="grid-card-title">多终端同项目</section>
      <p class="grid-card-desc">开两到十个终端同时干活。</p>
    </td>
    <td class="grid-card">
      <section class="grid-card-tag">02</section>
      <section class="grid-card-title">Worktree</section>
      <p class="grid-card-desc">不同分支各自干活再合并。</p>
    </td>
  </tr>
  <tr>
    <td class="grid-card">
      <section class="grid-card-tag">03</section>
      <section class="grid-card-title">Agent + Worktree</section>
      <p class="grid-card-desc">主窗口生成 sub-agent。</p>
    </td>
    <td class="grid-card">
      <section class="grid-card-tag">04</section>
      <section class="grid-card-title">Agent Team</section>
      <p class="grid-card-desc">终极形态，自动协调。</p>
    </td>
  </tr>
</table>
```

奇数项处理：如果只有 3 个卡片，最后一行只放 1 个 `<td class="grid-card">`，另一个 `<td>` 留空。

## Divider
```html
<hr>
```
