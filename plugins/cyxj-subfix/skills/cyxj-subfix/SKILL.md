---
name: cyxj-subfix
description: >
  达芬奇字幕修正工具：SRT 清理、Gemini 语义初修、Opus 审查把关。
  触发词：/字幕修正、修正字幕、字幕错别字、SRT 修正、达芬奇字幕。
  当用户提供 SRT 文件路径需要修正时使用此 skill。
version: 4.1.1
---

# 达芬奇字幕修正 Skill v4

## 路径约定

脚本一律用 `${CLAUDE_PLUGIN_ROOT}`（Claude Code 加载插件时自动注入）定位：
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/cyxj-subfix/srt_cleaner.py" ...
```

## 架构原则

**三层分离**：Python 做结构处理，Gemini 做语义初修，Opus 审查把关。

- Python（srt_cleaner.py）：HTML 清理、去重、标点替换、合并、拆分、编号、导出逐字稿 Markdown — 所有时间码操作
- Gemini（srt_corrector.py）：同音字修正 + 去口吃 + 去填充词 — API 自动处理，几乎免费
- Opus（对话内）：审查 Gemini 的修改清单，纠正错误修正，发现遗漏 — 只看 diff，token 极少

**词典定位**：词典是"已知陷阱"参考，不是主力。同一个词的错误变体太多，词典永远无法穷举。真正的修正靠 Gemini 的语义理解 + 视频主题上下文。Opus 审查后发现的遗漏会反馈到词典，让系统越来越准。

## 使用方法

```
/字幕修正 ~/Desktop/Timeline1.srt                          # 完整流程
/字幕修正 ~/Desktop/Timeline1.srt --topic "Claude Code教程" # 指定主题提高修正准确度
/字幕修正 ~/Desktop/Timeline1.srt --no-regroup             # 跳过合并拆分
/字幕修正 ~/Desktop/Timeline1.srt --premium                # Phase 2a 用高端 Gemini 模型
/字幕修正 添加词条 错误词→正确词                             # 添加词典条目（见下方"词典管理"）
```

## 显示规则

- 场景：横屏 16:9
- 软上限：18 字符（正常通过）
- 警告区：18-25 字符（输出时标注提醒）
- 硬上限：25 字符（Python 强制拆分，标记需人工校验）
- 字符计算：中文/中文标点=1, ASCII=0.5, 向上取整
- 标点规则：字幕中不用逗号句号（替换为空格），保留？！

## 执行步骤

<steps>

### Phase 1: Python 结构处理

1. **备份**：创建 `.bak` 备份文件（保住原始 SRT——后续各 Phase 会在同目录产出多个文件，防误覆盖，也便于最后回滚比对）
2. **运行 srt_cleaner.py**：
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/cyxj-subfix/srt_cleaner.py" "<input.srt>" --stats
   ```
   如果用户指定 `--no-regroup`，追加该参数跳过合并拆分。
3. **报告结果**：向用户汇报去重、合并、拆分、超限条目数量

### Phase 2a: Gemini 自动初修

1. **确认主题**：如果用户提供了 `--topic`，以此为语境参考；否则从字幕内容推断主题，向用户确认
2. **运行 srt_corrector.py**：
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/cyxj-subfix/srt_corrector.py" "<_cleaned.srt>" --topic "主题"
   ```
   如果用户指定 `--premium`，追加该参数使用高端模型。
3. **输出**：
   - `_gemini_fixed.srt`：Gemini 修正后的完整 SRT
   - `_changes.json`：修改清单（原文→修正，带原因）

### Phase 2b: Opus 审查（在对话中）

1. **读取 `_changes.json`**（只看修改清单，不读全文 SRT）
2. **审查 Gemini 的修正**：
   - 检查每项修正是否合理
   - 标记错误的修正（Gemini 改错了的）
   - 发现遗漏的错误（浏览 _gemini_fixed.srt 中 Gemini 未修改的部分，抽查是否有遗漏）
3. **应用最终修正**：
   - 撤销错误的修正
   - 补充遗漏的修正
   - 保存为 `_fixed.srt`
4. **反馈到词典**：
   - 把 Gemini 漏掉的重要错误写入 `dictionary.json` 的 `feedback.gemini_missed` 字段
   - 如果遗漏的错误有通用性（不是偶发的），同时添加到 `corrections` 中

### Phase 2c: 音频交叉验证（有成片音频时强烈推荐）

SRT 是 ASR 已经听错一遍的产物，拿 SRT 改 SRT 只能靠主题和上下文猜。**若用户能提供成片音频**，用 lark-minutes 妙记转写作为第二个独立信源做交叉验证（运行时证据 > 单一 ASR）：

> 依赖声明：本 Phase 依赖本机已配置好的 `lark-minutes` CLI（飞书妙记）。该 CLI 不可用时直接跳过本 Phase。

1. `drive +upload <音频>` → `minutes +upload --file-token <token>` → `minutes +detail --minute-tokens <token> --transcript` 拿妙记逐字稿
2. 逐条核对 Phase 2b 的存疑/猜测条目：**两源一致 → 钉死；两源冲突 → 并列存疑，请用户听音核对**
3. 妙记中文口语质量通常更高，能纠正大量同音字与语义误判（实测可纠正二三十处）

没有音频时跳过本 Phase，存疑条目在汇总里显式标注「请对音频核对」，不要把推断当事实。

### Phase 3: 写回 Obsidian 逐字稿（不再默认产 .txt）

Phase 2b/2c 完成后，从 `_fixed.srt` 生成分段逐字稿 Markdown：
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/cyxj-subfix/srt_cleaner.py" "<_fixed.srt>" --export-md --title "<视频标题>"
```
生成 `_transcript.md`（按自然停顿 + 每段约 200 字分段，文字一字不改）。然后写回 Obsidian：

- **若本次对话已能定位对应的待发布笔记**（同一视频的逐字稿草稿，通常在 `~/obsidian/灵感库/待发布/`）：把该笔记正文替换为逐字稿；同一视频的多份草稿合拢成一篇，多余的删除（vault 是 git 仓库，可回滚）。
- **否则**：写到 `~/obsidian/灵感库/待发布/<视频标题>（成片逐字稿）.md`，留待用户归位。

> `.txt`（`--export-txt` → `_script.txt`）已不是默认产物——它过去仅用于把逐字稿转回 Obsidian，现在直接写回。只有用户明确要把逐字稿导回 DaVinci IntelliScript 时才用 `--export-txt`。

**交接**：逐字稿写回后，若用户想把这期视频再做成图文，提示可用 `cyxj-transcript`（转稿）把逐字稿整理成文章草稿。

### Phase 4: 收尾清理（强制，不许跳过）

Phase 3 完成、逐字稿已写回 Obsidian 后，**必须**清理全部中间产物。同目录最终只留两份文件：

- `<原文件名>.srt` — 母片（用户给的原始文件，全程未改动）
- `<原文件名>_fixed.srt` — 最终修正后的字幕

清理步骤：

1. 先把 `_cleaned_stats.json` 里的 `splits_needing_review` 和 `over_soft_limit` 条目提醒给用户（这是唯一需要在删除前读取的信息）
2. 用 `cmp` 确认母片与 `.bak` 逐字节一致（母片没被误改）。一致 → 连 `.bak` 一起删；不一致 → 先用 `.bak` 还原母片，再删 `.bak`
3. 执行清理：

```bash
cmp -s "<原文件>.srt" "<原文件>.srt.bak" && rm -f "<原文件>.srt.bak" "<stem>_cleaned.srt" "<stem>_cleaned_stats.json" "<stem>_gemini_fixed.srt" "<stem>_changes.json" "<stem>_transcript.md"
```

`_transcript.md` 已在 Phase 3 写回 Obsidian，本地副本一并删除。删除后向用户报一句"以下中间产物已清理"+文件列表（不用事先逐个确认）。

向用户说明最终输出：
- `<原文件名>.srt` — 母片（未动）
- `<stem>_fixed.srt` — 最终修正后的字幕
- Obsidian 待发布笔记 — 已写回成片逐字稿（Phase 3）

</steps>

## Opus 审查时的权限边界

**可以做：**
- 审查并修正 Gemini 的错误修改
- 补充 Gemini 遗漏的同音字、口吃、填充词修正
- 将遗漏反馈到词典
- 审查合并结果，标记语义问题
- 建议用户添加新词典条目

**绝不可以做：**
- 修改任何时间码
- 合并或拆分条目
- 调整条目顺序
- 删除整条字幕（即使是填充词，也只清空文字保留时间码结构）
- 书面化改写口语表达

## 模型选择

| 用途 | 模型 ID | 价格（输入/输出 per M token） | 说明 |
|------|---------|------|------|
| 日常初修 | `gemini-3.1-flash-lite` | $0.25 / $1.50 | 默认，官方定位"高频/批量数据处理"，价格约为 3.5-flash 的 1/6 |
| 高端初修 | `gemini-3.5-flash` | $1.50 / $9.00 | `--premium` 时启用，语义理解更强，用于疑难字幕 |
| 审查 | Opus（对话内） | 按对话计费 | 只审查 diff |

价格核实于 2026-07-09（ai.google.dev/gemini-api/docs/pricing 原文，Standard 档）。

**注意**：`gemini-3.1-flash-image`（Nano Banana 2）、`gemini-3-pro-image`（Nano Banana Pro）是图片生成专用模型，不用于文本修正。

## 词典管理

添加词条 = 由 Claude 直接编辑 `dictionary.json` 的 `user_additions` 字段（格式：正确词 → 错误变体数组），编辑完成后向用户复述已添加的映射。脚本没有 `--add` 参数。

词典结构为"正确词 → 已知错误变体列表"，添加时归类到对应的正确词下：
```json
"user_additions": {"正确词": ["错误变体1", "错误变体2"]}
```

词典路径：`${CLAUDE_PLUGIN_ROOT}/skills/cyxj-subfix/dictionary.json`

### 反馈机制

`dictionary.json` 的 `feedback.gemini_missed` 字段记录 Gemini 漏掉但 Opus 审查时发现的错误：
```json
{"original": "错误文字", "correct": "正确文字", "context": "错误类型描述", "date": "2026-03-21"}
```

这些记录用于：
1. 优化 Gemini 的 prompt（如果某类错误反复出现）
2. 扩充 corrections 词典（如果错误有通用性）
