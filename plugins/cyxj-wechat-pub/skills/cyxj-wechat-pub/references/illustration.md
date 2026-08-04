# Phase 3：IP 配图生成 + 上传（按需读取）

排版流程走到 Phase 3、且用户确认要 IP 配图/封面时才读本文件。
只做纯文字排版（不配图）时不需要读。

---


## 3.1 题材识别与视觉方案匹配

先判断文章题材，自动匹配对应的视觉方案。这决定了插图和封面的场景、配色和构图方向：

| 文章题材 | 场景类型 | 配色倾向 | 构图 |
|---------|---------|---------|------|
| AI/科技 | 全息工作站、数据空间、未来城市 | 深蓝+霓虹青+品红边缘光（赛博朋克） | 居中对称，几何光环框架 |
| 读书/生活 | 咖啡馆、书房、窗边、秋日场景 | 暖琥珀金+奶油色+焦橙+深红（文艺暖调） | 三层景深（前景虚化→中景人物→背景环境） |
| 教程/干货 | 黑板、工具台、实验室、工作桌面 | 深色底+亮色重点标注（专业感） | 尺度对比，功能性构图 |
| 感悟/情感 | 自然场景、星空、海边、山顶 | 柔和渐变、淡彩（诗意感） | 负空间留白叙事 |
| 运营/商业 | 会议室、数据仪表盘、增长曲线 | 商务蓝+白+金色点缀（专业信任感） | 居中对称或黄金比例 |

将匹配到的场景、配色、构图描述融入图片生成 prompt，让每篇文章的配图氛围与内容匹配，而不是千篇一律的白底 3D 渲染。

## 3.2 渲染风格选择

- **默认风格：3D Stylized Toon** — 保持 XCYJ 品牌 IP 一致性，适用于大多数文章
- **备选风格：水彩绘本风** — 适用于读书笔记、生活感悟、情感类文章。将小金 IP 画成柔和水彩/水墨插画风格，保留核心辨识特征（光头、蓝色卫衣、金链耳饰），但呈现为手绘绘本质感

选择哪种风格由文章气质决定：技术/教程/商业类用 3D Toon，文艺/读书/情感类可用水彩风。如果不确定，询问用户。

## 3.3 图片生成引擎与凭据（GPTIMG2 / gpt-image-2）

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

## 3.4 封面生成

封面是文章的门面，必须同时包含 **IP 形象 + 文章标题文字**。

封面同样走 3.3 的 GPTIMG2 引擎、凭据和出图方式（`response_format=url` → 下载落地 → 图床上传）。因为封面必须含小金形象，**用 `{base}/v1/images/edits` 端点**（带 IP 参考图，curl 示例 A），在 prompt 中明确要求：
- IP 形象（小金）处于画面中，场景和配色按题材视觉方案
- **文章标题文字直接渲染在封面图上**，作为设计的一部分（不是后期叠加）。gpt-image-2 中文渲染准确率高，适合直接出标题字
- 标题文字要清晰可读，字体风格与画面氛围匹配
- 封面是 21:9 微信公众号规格，目标 1800x766。但 GPTIMG2 的 `size` 取离散档位，21:9 没有原生档——请求时用最接近的 16:9 `2560x1440`（2K，比例略宽），拿到图后再裁成 1800x766；或直接在 prompt 里要求 21:9 超宽构图。**不要回退到低分辨率出图**
