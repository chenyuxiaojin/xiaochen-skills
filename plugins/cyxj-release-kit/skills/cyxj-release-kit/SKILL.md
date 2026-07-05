---
name: cyxj-release-kit
description: |
  陈与小金的视频发布物料一条龙：成片定稿后，一次产出 6 平台「标题+简介」（YouTube/B站/抖音 主平台,
  视频号/TikTok/小红书 分发平台）+ 三比例封面（16:9 / 4:3 / 3:4,HTML 封面工作台出图,文字零错字零裁切）
  + 上传用 JPG。封面走「无字底图 + HTML 排字」路线,不再用生图赌中文渲染。
  触发方式:/cyxj-release-kit、发布物料、出发布包、取标题、六平台标题、写标题和简介、
  做封面(HTML/工作台)、封面工作台、视频要发布了。
  凡是"视频做完了准备发"的场景都应该用本 skill——哪怕用户只提了其中一样(只要标题/只要封面),
  也按本 skill 对应模块走,保证口径一致。
---

# cyxj-release-kit:视频发布物料一条龙

成片定稿 → 标题(6 平台)→ 简介(6 平台)→ 封面(3 比例)→ 上传 JPG。
本 skill 把 2026-07-05 loop 视频那次全流程实战固化下来,核心教训只有一条:
**中文文字永远不要交给生图模型渲染**——模型不认精确比例、脚本会中心裁切,文字进画面必掉字;
文字由浏览器渲染,底图才交给生图/实拍。

## 前置

1. 读 `内容创作/log/index.md` HEAD,拿到:成片位置、**最终导出字幕**(SRT)位置、视频主题。
2. 确认**视频标题已定稿**。没定稿就先出候选(规则见下),用户拍板后再走后面模块。
3. 所有事实(数字、时间戳、功能点)只从最终字幕/成片里来,**数据不编**(同 cyxj-jingxuan 的红线)。

## 模块一:标题(6 平台)

先读 `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-release-kit/references/platform-specs.md` 的标题部分。

铁律(来自用户反馈,违者返工):
- **体裁匹配**:标题承诺的体裁必须=内容真实体裁(教程/评测/观点/复盘)。教程别错卖成评测;
  片中无数据支撑的主观体感、副线彩蛋,不上标题(放简介或不放)。
- **三平台卖同一件货**:各平台只调钩子位置和关键词密度,不换体裁不换卖点。
- 不抖机灵、不用「不是…而是…」句式、给精确数字(跑了 3 个月、每天 9:07)。

## 模块二:简介(6 平台)

规格逐平台见 platform-specs.md。要点:
- YouTube 简介带章节时间戳,第一条必须 `00:00`,**每个时间戳都要回字幕核对**,禁止估。
- 标题+简介成对交付,一次给全 6 个平台,别挤牙膏。

## 模块三:封面(HTML 封面工作台)

### 3.1 底图(一期一张,无字)

底图 = 16:9 无文字场景图,来源二选一:
- **生图**:调 cyxj-image-studio 的 generate.py(gpt-image-2-vip),场景提示词里必须写明
  「画面中完全不出现任何文字、字母、数字、标志、水印」+「右侧大面积空墙留给排版」,
  人脸参考用 `~/Pictures/封面形象/` 里用户指定的原图(**每次都喂原图,严禁拿生成图回喂**,会越来越不像)。
- **实拍/抽帧**:用户给照片,或从成片开头口播段 ffmpeg 抽帧(注意挑眼睛睁开的帧,先抽 5-6 帧给用户选)。

底图只出 16:9 一个比例——其余比例由工作台的 blur-fill 自己适配,不要分比例生图。

### 3.2 工作台

1. 把 `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-release-kit/templates/cover-studio.html` 复制到本期
   物料目录(`~/Pictures/封面出图/<日期>-<项目>-最终/源文件/`),底图重命名为 `plate_16x9.png` 放同目录。
2. 改模板顶部三个常量 `L1/L2/L3`(标题三段)。字数和默认(5/4/4 字)差很多时,按
   「字数 × 字号 ≈ 可用宽度」调 `RATIOS` 里各比例的 `s1/s3`,渲一次画廊自检确认没有换行/贴边。
3. `open -a "Google Chrome" 工作台.html` 给用户挑。画廊 = 3 比例 × 3 样式(A 右栏三行+星芒箭头 /
   B 通栏大字 / C 微倾斜+橙底线),点选存 localStorage,可多选。
4. 读用户选择:**扩展碰不了 file:// 页面**,从磁盘读:
   ```bash
   cd ~/Library/Application\ Support/Google/Chrome/Default/Local\ Storage/leveldb
   strings -a $(ls -t *.log | head -1) | grep -a 'coverPicks\|16x9-\|4x3-\|3x4-' | tail -3
   ```
   取**最后一条** JSON 数组为准。读不到就直接问用户选了哪几个编号。
5. 按选中变体逐张导出(无头 Chrome,像素级精确):
   ```bash
   C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
   "$C" --headless --disable-gpu --hide-scrollbars \
        --window-size=<W>,<H> --virtual-time-budget=4000 \
        --screenshot=<输出>.png "file://<工作台绝对路径>?v=<变体ID>"
   ```
   尺寸:16x9=2560,1440;4x3=2048,1536;3x4=1536,2048。导出后 `sips -g pixelWidth -g pixelHeight` 验尺寸。

### 3.3 工作台原理(改样式/排错时读)

- **blur-fill 模糊延展**:清晰底图按宽度贴底,画布上方缺口用同图 `blur(60px)` 放大版补,
  清晰层顶部加 `mask-image: linear-gradient` 渐隐,接缝不可见。模糊层 `background-position`
  取景**纯墙区**(right center),否则人物鬼影会浮在模糊区。
- 人物大小由清晰层 `plateW` 控制(小 ≈ 画布宽的 70-75%),文字大小在 `RATIOS` 每比例配置里。
- 字体 = 得意黑 Smiley Sans,已装 `~/Library/Fonts/SmileySans-Oblique.ttf`;模板 @font-face 走
  `local()` + 同目录 ttf 兜底。新机器没装:GitHub `atelier-anchor/smiley-sans` releases 下载
  (v2.0.1 实测可用),cp 进 `~/Library/Fonts/`。

## 模块四:上传 JPG

- **默认轻量转换**(HTML 截图无任何来源痕迹,无需去痕):
  `sips -s format jpeg -s formatOptions 95 <png> --out <jpg>`
- 用户要「PS 出品」元数据外观时才调 **cyxj-psjpg** skill(真 Photoshop 导出,约 2-4 秒/张)。

## 产物归集与收尾

```
~/Pictures/封面出图/<日期>-<项目>-最终/
  封面_16x9.png / 封面_4x3.png / 封面_3x4.png     ← 定稿 PNG
  源文件/ 封面工作台.html + plate_16x9.png + 字体   ← 可复用,下期只改 L1/L2/L3
~/Pictures/封面出图/<日期>-<项目>-最终_psjpg/       ← 走 psjpg 时的 JPG
```
- 过程稿文件夹在用户确认定稿后**问一声再删**(先例:用户会要求清掉)。
- 标题+简介直接在对话交付;按内容创作仓库规矩更新 log HEAD + 历史流水。

## 与相邻 skill 的分工

| skill | 管什么 | 本 skill 关系 |
|---|---|---|
| cyxj-video-cover | 生图封面(整图带字) | 降级为**底图生成器**,文字不再交给它 |
| cyxj-psjpg | 真 PS 转 JPG + 去痕 | 可选后处理,默认不用 |
| cyxj-jingxuan | 抖音精选申请文案 | 发布后的下一步,不在本 skill 内 |
| cyxj-hook / cyxj-content | 视频开头/内容诊断 | 管片子本身,不管发布物料 |
