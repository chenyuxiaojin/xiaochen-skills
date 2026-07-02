# 引擎实测对照（Step 0 附录）

> 从 SKILL.md Step 0 拆出的引擎实测资料。选引擎前读这里，禁止凭记忆。

**引擎对照（全部 2026-06-26 实测，按需选，禁止凭记忆）：**

| 引擎 / 模型 | key | 比例 | 质量 | 中文标题 | 喂脸 |
|---|---|---|---|---|---|
| **`gemini-3-pro-image-preview`** | `GEMINI_API_KEY`（一手） | ✅认(16:9→1.79) | 高 | ✅基本准 | ✅ inline_data |
| `gpt-image-2-vip` | `GPTIMG2_API_KEY` | ⚠️只16:9稳 | medium | ✅准 | ✅ edits |
| `gpt-image-2`（默认档） | `GPTIMG2_API_KEY` | ❌强制1254² | ❌low | ✅准 | ✅ |
| `gemini-2.5-flash-image` | `GEMINI_API_KEY` | ✅ | 高 | ❌乱码 | ✅ |
| `imagen-4.0-*` | `GEMINI_API_KEY` | ✅原生档 | 高 | ⚠️CJK未测 | ❌ |

- **脚本主路径 = `gpt-image-2-vip`**（`generate.py` 走 GPTIMG2）；多比例(16:9+4:3+3:4)想更稳可走 `gemini-3-pro-image-preview`——它是**实验性手动路径（无脚本支撑，按下方速记现场调用）**，三比例构图都干净、脸还原好。
- **只要 16:9、想要粗描边正宗涂鸦质感**：`gpt-image-2-vip` 也行；但它 **4:3/3:4 会把标题裁切**，别用它出非 16:9。
- ❌ 避开：`gpt-image-2` 默认档（无视 size/quality 缩水）、`gemini-2.5-flash-image`（中文乱码）。
- **两个引擎中文都不是 100%**（gemini 偶把「五个」出成「三个」）：每张多出 2–3 版挑文字对的，或文字单独叠层。

**Gemini 调用速记**（探测用，实验性手动路径）：
`POST .../v1beta/models/gemini-3-pro-image-preview:generateContent?key=$GEMINI_API_KEY`，body =
`{"contents":[{"parts":[{"text":"<prompt>"},{"inline_data":{"mime_type":"image/png","data":"<脸b64>"}}]}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"16:9"}}}`；
出图在 `candidates[0].content.parts[].inlineData.data`(b64)；不喂脸就去掉 inline_data 那个 part；出图后用 Pillow 中心裁到精确比例。
