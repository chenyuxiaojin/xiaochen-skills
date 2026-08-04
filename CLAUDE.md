# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

这是一个 Claude Code 插件市场仓库（Plugin Marketplace），里面是一组 `cyxj-*` skill，通过
`/plugin marketplace add chenyuxiaojin/xiaochen-skills` 安装到 Claude Code。

**真相源 = `.claude-plugin/marketplace.json`**。判断"有几个/哪些插件、各自路径"时一律以它为准，
不要相信任何文档里写死的数字（它们会漂移）。`plugins/` 下的目录数 ≥ marketplace 注册数：
没注册进 marketplace 的插件，用户**装不到**（这通常是遗漏，不是设计）。

## 架构

```
.claude-plugin/marketplace.json   ← 插件市场注册表（所有插件的入口，新插件必须在此注册）
plugins/
  cyxj-{name}/
    skills/
      cyxj-{name}/               ← 技能文件夹名 = 插件名 = SKILL.md 的 name，三者必须一致
        SKILL.md                 ← Skill 核心：frontmatter(name/description) + 指令，运行时被读取
        *.py / scripts/*         ← 辅助脚本（直接放 SKILL.md 同级，或放 scripts/ 子目录，仓库里两种都有）
        *.css / *.html           ← 静态资源（如 wechat-pub 的排版模板）
        references/ templates/   ← 参考素材 / 模板（部分 skill 有）
```

**两类 skill**：
- **纯指令型**（obsidian-build、roundtable、ai-weekly-news、jingxuan 等）—— 没有脚本，全靠 SKILL.md 的
  frontmatter + 正文指令（部分配 references/ 模板）驱动；roundtable 还会现场拉起多个 Opus subagent 扮演不同角色
- **脚本型**—— SKILL.md 调用同目录的 Python/Bash 脚本，脚本里用 `${CLAUDE_PLUGIN_ROOT}`（或 `$SKILL_DIR`）
  拼本地路径定位资源。新写脚本引用本地文件时**必须**走这个变量，不能写死绝对路径

`description` frontmatter 不只是说明文字——它定义了 skill 的**触发条件**（含触发词），写得准不准直接决定
Claude Code 会不会在对应场景自动唤起这个 skill。

## 命名规则（三处必须完全一致）

插件目录名、技能文件夹名、SKILL.md 的 `name` 字段，三处全等，格式 `cyxj-{短名}`：

```
plugins/cyxj-foo/skills/cyxj-foo/SKILL.md   ← name: cyxj-foo
.claude-plugin/marketplace.json             ← "name": "cyxj-foo", "source": "./plugins/cyxj-foo"
```

**例外：多 skill 插件**（目前有 `cyxj-video-doctor`（cyxj-content + cyxj-hook）和
`cyxj-image-studio`（cyxj-poster + cyxj-video-cover）两个）。
此时插件名不等于技能名，但**每个技能文件夹名仍必须 = 其 SKILL.md 的 `name`**；插件级共享资源放
`plugins/{插件}/references/`（文档）或 `plugins/{插件}/lib/`（Python 模块，脚本里按
`Path(__file__).resolve().parents[3] / "lib"` 定位），skill 里用 `${CLAUDE_PLUGIN_ROOT}/...` 引用。
只有需要共享文件的强关联 skill 才合并进同一插件，不要为省注册条目乱合。

## 改 Skill 后的同步检查清单

文档与注册表极易漂移（本仓库历史上多次出现）。任何对 skill 的改动（增 / 删 / 改名 / 改内容）做完都要逐项核对：

1. **SKILL.md frontmatter** — `name` 与文件夹名一致
2. **`.claude-plugin/marketplace.json`** — `name` 和 `source` 已同步；新插件**已注册**（漏注册 = 用户装不到）；
   插件**改名/合并/删除**时必须在顶层 `renames` 字段加映射（改名 → 新名，删除 → null），已装用户才能自动迁移。
   `renames` 是 append-only 历史，旧条目**永不删除**（Claude Code 会沿改名链跟踪）
3. **README.md** — Skills 表格同步（名称 + 链接路径），且不留指向已删除目录的幽灵条目
4. **CLAUDE.md** — 只在「架构 / 命名规则 / 流程」这些**不会随插件增减而变**的规则受影响时才动它；
   不要在这里维护逐插件清单（会漂），要看有哪些插件读 `marketplace.json`
5. **AGENTS.md** — 已改为指向本文件的重定向（2026-06-13 起单源维护，不再镜像同步），正常情况不需要动它
6. **push 到 GitHub** — 本地改动不会自动同步给已安装用户，**必须 push 后才对用户生效**

## 新增 Skill 的流程

1. 建 `plugins/cyxj-{name}/skills/cyxj-{name}/SKILL.md`（frontmatter 的 `name` 与文件夹名一致）
2. 辅助脚本 / 资源放同级目录或 `scripts/`
3. 在 `.claude-plugin/marketplace.json` 的 `plugins` 数组注册
4. 更新 README.md 的 Skills 表格
5. push 到 GitHub 后生效（AGENTS.md 是重定向，无需同步；CLAUDE.md 不维护逐插件清单，通常不用动）

## 常用命令

```bash
# 验证 marketplace.json 格式
python3 -m json.tool .claude-plugin/marketplace.json

# 漂移自检：找出"有目录但没注册进 marketplace"的插件（理想为空；非空 = 有插件漏注册）
python3 -c "import json,os; reg={p['name'] for p in json.load(open('.claude-plugin/marketplace.json'))['plugins']}; print(sorted({d for d in os.listdir('plugins') if os.path.isdir('plugins/'+d)}-reg))"
```
