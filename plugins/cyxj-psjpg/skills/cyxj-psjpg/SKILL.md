---
name: cyxj-psjpg
description: |
  用本机真 Photoshop 把一个目录里的图片批量导出成统一规格的 JPG（质量可配 / Progressive /
  嵌 sRGB），并清理 XMP 元数据里的 PNG→JPG 转换痕迹，让产物看起来像 PS 里原生做好直接导出的图，
  不暴露 png 截图 / AI 生成 / 下载素材的来源。
  小陈做公众号封面、小红书封面、视频缩略图、AI 生成图上传各平台前的统一处理常用。
  触发方式：/批量过PS、/PS批处理、/转jpg、「把这些图过 PS 统一一下」「png 转 jpg」「封面转 jpg」
  「用 ps 导出 jpg」「准备一批封面图」「批量处理这个文件夹的图片」「去掉图片的转换痕迹 / 来源痕迹元数据」。
  默认输出 Progressive JPG 质量 12（PS 最高档）到单独目录，原图保留不动，可自定义输出目录和质量。
---

# cyxj-psjpg：真 PS 批量导出 JPG + 清理转换痕迹

把目标目录里所有 `png/jpg/jpeg` 用**本机真 Photoshop** 导出为统一规格的 JPG，再清理元数据中暴露 PNG 来源的痕迹。一条命令跑完两步，原文件保留不动。

## 为什么是真 PS 而不是 sips/ffmpeg

目标是让封面带上**真实可信的 Photoshop 元数据**（Software=Adobe Photoshop、sRGB ICC、质量 12 Progressive、内嵌缩略图等），脚本伪造的元数据经不起深度核对。所以必须走真 Photoshop 的 `Save As` 路径，元数据由 PS 自己写。导出后再把 XMP History 里的 `created → converted → saved`（含 `from image/png to image/jpeg`）改写成干净的 `created → saved`，保留各自真实时间戳与 instanceID，时间线自洽。

## 用法

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/psjpg.sh <源目录> [输出目录] [质量 1-12]
```

| 参数 | 默认 |
|------|------|
| 源目录 | 必填 |
| 输出目录 | `<源目录>_psjpg`（单独目录，原图不动）|
| 质量 | `12`（PS 最高档）|

## 工作流

1. **拿到源目录**。用户给了明确路径直接用；模糊指代去对话上下文里找；只给了单个文件就取其所在目录；找不到就问。
2. **确认 PNG 透明背景风险**。JPEG 不支持透明通道——若目录里有透明背景 PNG，PS 会把透明区填成白底。封面一般满版无透明，正常；不确定就提醒用户一句。
3. **跑脚本**（导出 + 清理一条龙）。
4. **转述结果**：成功/失败张数、输出位置、总大小；有失败就列清单。

## 只做其中一步

```bash
# 只清理元数据痕迹（不重新导出），可对目录或指定文件
${CLAUDE_PLUGIN_ROOT}/scripts/clean_metadata.sh <目录>
${CLAUDE_PLUGIN_ROOT}/scripts/clean_metadata.sh a.jpg b.jpg
```

## 验证（需要核对痕迹是否清干净时）

```bash
exiftool -s -XMP-xmpMM:HistoryAction -XMP-xmpMM:HistoryParameters -IFD0:Software <输出目录>/*.jpg
```

期望：`HistoryAction = created, saved`；`HistoryParameters` 不再出现 `from image/png to image/jpeg`；`Software = Adobe Photoshop <版本> (Macintosh)`。

## 依赖与注意

- **仅 macOS**（用 osascript 驱动 PS）。
- **本机已装 Adobe Photoshop**（脚本自动探测 `/Applications/` 下的 `Adobe Photoshop*`，兼容 2026/2025/CC 多版本，不写死版本）。
- **exiftool**（`brew install exiftool`），清理痕迹用；缺失时脚本会提前报错。
- 去痕迹的 `softwareAgent` 从导出 JPG 的 `IFD0:Software` **动态读取真实版本**，不写死版本号。
- 跑的过程中 PS 被占用，不能同时手动用 PS；每张约 2-4 秒。
- 输出到单独目录，源目录里若有同名 `foo.png` 和 `foo.jpeg`，导出的 `foo.jpg` 会互相覆盖（脚本会提示差额）。
- `OriginalDocumentID`、`SlicesGroupName` 是真实 PS 文件本就有的字段，不暴露 PNG 来源，保留更自然，脚本不动它们。

## scripts/ 文件说明

| 文件 | 作用 |
|------|------|
| `psjpg.sh` | 入口：导出 + 清理一条龙 |
| `ps_export.jsx` | Photoshop ExtendScript，真 PS 导出 JPG；参数从 `/tmp/cyxj_psjpg_cfg.txt` 读 |
| `clean_metadata.sh` | exiftool 清理 XMP History，可独立调用 |
