---
name: cyxj-video-cover
description: |
  无字底图生成引擎(gpt-image-2-vip,真人照片重绘保脸)。只出不带任何文字的场景图,
  供 cyxj-release-kit 的 HTML 封面工作台当底图,或手动要一张无字人物场景图时用。
  ⚠️ 封面成品、视频发布物料(标题/简介/封面)一律走 cyxj-release-kit——
  本 skill 不再直接产出带字封面,不要用它响应「做封面/生成封面」类请求。
---

# cyxj-video-cover:无字底图生成引擎(已降级)

**2026-07-26 降级定稿**(裁决记录见 内容创作/log):旧「生图直接渲染中文标题」工作流作废——
中文文字永远不要交给生图模型渲染,文字由浏览器渲染(cyxj-release-kit 的 cover-studio.html),
底图才交给生图。本 skill 只剩一件事:**出无字底图**。

## 唯一入口:generate.py

```bash
python3 <本目录>/scripts/generate.py \
  --title "占位" \                  # 仍需传参但别指望它排字;场景里必须禁字(见下)
  --label "<项目名>-底图" \
  --ratios "16:9" \
  --face ~/Pictures/封面形象/<用户指定的原图> \
  --scene "<场景描述>。画面中完全不出现任何文字、字母、数字、标志、水印;右侧大面积留白给排版"
```

硬规矩:
1. **人脸参考必须由用户指定原图**(`--face` 显式传),严禁默认取目录第一张、严禁拿生成图回喂(会越来越不像)。
2. **场景提示词必须带禁字条款**(上面那句),出图后人工检查画面无任何文字残留。
3. 底图只出 16:9 一张;分比例适配、标题渲染、JPG 转换全部在 cyxj-release-kit 里做。
4. 输出仍落 `~/Pictures/封面出图/<日期>-<label>/`。

## 技术事实(engine 层,维护时看)

- 引擎:`gpt-image-2-vip` @ GPTIMG2 中转 `api.chatgpt-code.com`(OpenAI 兼容,`{base}/v1/images/edits`,
  真人照片做参考图重绘保脸;`response_format=url`,脚本下载落地 PNG)
- 密钥:`密钥存储/.env` 的 `GPTIMG2_BASE_URL`(末尾无 `/v1`)+ `GPTIMG2_API_KEY`,脚本自动读
- 引擎实测对照与 Gemini 实验路径:`references/engines.md`
- 依赖:Python 3.11+ 标准库;可选 Pillow(自动中心裁切)

## 历史

旧版完整工作流(整图带字、4 比例×2、风格预设、psjpg 交付)已删,如需考古看本仓 git 历史
(2026-07-26 之前的版本);网页生成模板 web-prompts.md 同日删除。
