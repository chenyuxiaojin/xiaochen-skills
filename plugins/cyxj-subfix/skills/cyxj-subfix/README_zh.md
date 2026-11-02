# 达芬奇字幕修正工具

[English](README.md)

一个 Claude Code Skill，用于修正达芬奇 DaVinci Resolve 导出 SRT 字幕中的语音识别（ASR）错误。采用 **Sonnet + Opus 混合架构**：Sonnet 负责初修，Opus 审查修改。

## 解决什么问题

达芬奇的中文语音转文字准确度有限，导出的字幕经常出现：
- **同音字替换**：专业术语被识别成同音常见词（如 "Claude Code" → "Color Code"，"上下文" → "善夏文"）
- **口吃重复**："我说的我说的我说的" 应该是 "我说的"
- **填充词**："嗯""啊""那个""就是说" 等口头禅
- **重复条目**：达芬奇有时会生成时间重叠的字幕片段

## 架构

```
Phase 1: Python 结构处理 (srt_cleaner.py)
  HTML 清理 → 去重 → 标点替换 → 合并短条目 → 拆分长条目 → 重新编号

Phase 2a: Sonnet 自动初修，通过 `claude -p` 调用 (srt_corrector.py)
  分批调用（词典 + 主题上下文）→ _sonnet_fixed.srt + _changes.json

Phase 2b: Opus 审查（在 Claude Code 对话中）
  审查 Sonnet 的修改清单 → 纠正错误 → 补充遗漏 → 保存 _fixed.srt

Phase 2c: 音频交叉验证（有成片音频时，用 lark-minutes 妙记逐字稿做第二信源）

Phase 3: 写回 Obsidian 逐字稿

Phase 4: 收尾清理（只保留母片原文件 + _fixed.srt，含 .bak 在内的中间产物自动清理）
```

流程结束后，本地目录只留两个文件：用户给的原始 SRT（母片，全程未改动）和最终修正后的 `_fixed.srt`；`.bak`、`_cleaned.srt`、`_sonnet_fixed.srt`、`_changes.json` 等中间产物会被自动清理（删 `.bak` 前先 `cmp` 校验母片完好）。

### 为什么用混合架构？

Sonnet 走 Claude Code 额度完成初修，不需要额外的 API key；Opus 只审查修改清单（diff），不处理全文。

## 环境要求

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3.10+

```bash
pip install pysrt jieba
```

## 安装

### 作为 Claude Code Skill 安装（推荐）

```bash
/plugin marketplace add chenyuxiaojin/xiaochen-skills
```

在 Claude Code 中使用：
```
/字幕修正 ~/Desktop/Timeline1.srt --topic "视频主题"
```

### 独立使用

```bash
# Phase 1: 结构清理
python3 srt_cleaner.py "input.srt" --stats

# Phase 2a: Sonnet 自动修正
python3 srt_corrector.py "input_cleaned.srt" --topic "视频主题"
```

## 文件说明

| 文件 | 用途 |
|------|------|
| `srt_cleaner.py` | Phase 1：结构处理（HTML 清理、去重、合并/拆分、编号） |
| `srt_corrector.py` | Phase 2a：通过 `claude -p` 用 Sonnet 分批修正，支持词典 |
| `dictionary.json` | 已知 ASR 错误映射（正确词 → 错误变体列表） |
| `SKILL.md` | Claude Code Skill 定义和工作流程 |

## 词典

词典将正确术语映射到已知的 ASR 错误变体：

```json
{
  "corrections": {
    "Claude Code": ["Color Code", "Closet Code", "Colortico", "clotco"],
    "上下文": ["善夏文", "善效文"],
    "worktree": ["工作数", "工夫"]
  }
}
```

通过 Claude Code 添加新条目：
```
/字幕修正 --add "错误词" "正确词"
```

`feedback.first_pass_missed` 字段记录初修漏掉但 Opus 发现的错误，实现持续改进。

## 模型

初修用 `sonnet`，这是 Claude Code 的模型别名，指向当前的 Sonnet。要换模型就传 `--model`。

## 显示规则

针对 16:9 横屏视频字幕优化：
- 每条上限：16 显示字符（中文=1，ASCII=0.5；Netflix 简体中文每行 16 字），超过就按词边界拆开并标记需人工校验
- 标点：逗号句号 → 空格，保留？！

## 许可证

MIT
