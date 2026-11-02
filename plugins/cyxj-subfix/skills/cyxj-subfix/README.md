# DaVinci Subtitle Fixer

[中文版](README_zh.md)

A Claude Code skill for correcting ASR (Automatic Speech Recognition) errors in SRT subtitle files exported from DaVinci Resolve. Uses a **Sonnet + Opus hybrid architecture**: Sonnet makes the first pass, and Opus reviews the changes.

## The Problem

When you export subtitles from DaVinci Resolve's built-in speech-to-text, Chinese transcription is riddled with errors:
- **Homophone substitutions**: Technical terms get replaced by common words with similar pronunciation (e.g., "Claude Code" → "Color Code", "上下文" → "善夏文")
- **Stutter/repetition**: "我说的我说的我说的" should be "我说的"
- **Filler words**: "嗯", "啊", "那个", "就是说" cluttering the text
- **Duplicate entries**: DaVinci sometimes generates overlapping subtitle segments

## Architecture

```
Phase 1: Python structural processing (srt_cleaner.py)
  HTML cleanup → dedup → punctuation → merge short → split long → renumber

Phase 2a: Sonnet auto-correction via `claude -p` (srt_corrector.py)
  Batched calls with dictionary + topic context → _sonnet_fixed.srt + _changes.json

Phase 2b: Opus review (in Claude Code conversation)
  Review Sonnet's change list → fix errors → catch misses → save _fixed.srt

Phase 2c: Audio cross-check (when the finished audio is available, via lark-minutes as a second source)

Phase 3: Write transcript back to Obsidian

Phase 4: Cleanup (keep only the original SRT + _fixed.srt; intermediates incl. .bak auto-deleted)
```

After the run, only two files remain locally: the original SRT the user provided (untouched master) and the final `_fixed.srt`; intermediates like `.bak`, `_cleaned.srt`, `_sonnet_fixed.srt`, and `_changes.json` are cleaned up automatically (the `.bak` is removed only after a `cmp` check confirms the master is intact).

### Why Hybrid?

Sonnet handles the first pass through your Claude Code plan, with no extra API key. Opus only reviews the diff, not the full text.

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- Python 3.10+

```bash
pip install pysrt jieba
```

## Installation

### As a Claude Code Skill (Recommended)

```bash
/plugin marketplace add chenyuxiaojin/xiaochen-skills
```

Then use it in Claude Code:
```
/字幕修正 ~/Desktop/Timeline1.srt --topic "Your video topic"
```

### Standalone Usage

```bash
# Phase 1: Structural cleanup
python3 srt_cleaner.py "input.srt" --stats

# Phase 2a: Sonnet auto-correction
python3 srt_corrector.py "input_cleaned.srt" --topic "Video topic"
```

## Files

| File | Purpose |
|------|---------|
| `srt_cleaner.py` | Phase 1: Structural processing (HTML strip, dedup, merge/split, renumber) |
| `srt_corrector.py` | Phase 2a: Batched Sonnet correction via `claude -p`, with dictionary support |
| `dictionary.json` | Known ASR error mappings (correct term → error variants) |
| `SKILL.md` | Claude Code skill definition and workflow |

## Dictionary

The dictionary maps correct terms to known ASR error variants:

```json
{
  "corrections": {
    "Claude Code": ["Color Code", "Closet Code", "Colortico", "clotco"],
    "上下文": ["善夏文", "善效文"],
    "worktree": ["工作数", "工夫"]
  }
}
```

Add new entries via Claude Code:
```
/字幕修正 --add "error_word" "correct_word"
```

The `feedback.first_pass_missed` field tracks errors the first pass missed but Opus caught, enabling continuous improvement.

## Model

The first pass uses `sonnet`, Claude Code's alias for the current Sonnet model. Pass `--model` to use another one.

## Display Rules

Optimized for 16:9 landscape video subtitles:
- Line limit: 16 display characters (Chinese = 1, ASCII = 0.5; Netflix Simplified Chinese allows 16 per line). Longer cues are split at word boundaries and flagged for review
- Punctuation: commas/periods → spaces, keep ？！

## License

MIT
