#!/usr/bin/env python3
"""共享路径与密钥配置 — 全部从环境变量读取，缺失时给出清晰引导。"""

import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent

# 匹配 YOUTUBE_API_KEY / YOUTUBE_API_KEY_2 / YOUTUBE_API_KEY_3 ... 同时容忍
# 用户在 .env 里用 YouTube_API_key2 这种大小写混杂、漏下划线的写法。
_YOUTUBE_KEY_PATTERN = re.compile(r"^YOUTUBE_?API_?KEY(?:_?(\d+))?$", re.IGNORECASE)


def _collect_youtube_keys_from_env(env_dict: dict[str, str]) -> list[tuple[int, str]]:
    """从 dict（os.environ 或 .env 解析结果）筛 YouTube key，返回 [(序号, key值)]。
    主 key（YOUTUBE_API_KEY）序号为 0；带后缀的按数字序号排。"""
    out = []
    for name, val in env_dict.items():
        m = _YOUTUBE_KEY_PATTERN.match(name)
        if not m or not val.strip():
            continue
        idx = int(m.group(1)) if m.group(1) else 0
        out.append((idx, val.strip(' "\'\n\r')))
    return out


def _parse_env_file(path: Path) -> dict[str, str]:
    """简易 .env 解析：KEY=VAL，忽略注释 / 空行。"""
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        out[key.strip()] = val.strip()
    return out


def load_youtube_api_keys() -> list[str]:
    """返回所有可用的 YouTube API key，按序号排列（主 key 在前，备用 key 按 _N 序号排）。

    查找位置（按优先级）：环境变量 → ${SKILL_DIR}/.env → ~/.config/cyxj/.env。
    同一序号若在多处出现，优先级高的覆盖低的。空列表会触发退出。
    """
    by_idx: dict[int, str] = {}

    # 低优先级先填，高优先级覆盖
    for env_path in (Path.home() / ".config" / "cyxj" / ".env", SKILL_DIR / ".env"):
        for idx, val in _collect_youtube_keys_from_env(_parse_env_file(env_path)):
            by_idx[idx] = val
    for idx, val in _collect_youtube_keys_from_env(dict(os.environ)):
        by_idx[idx] = val

    if not by_idx:
        print(
            "错误：未找到任何 YOUTUBE_API_KEY。请按以下任一方式配置：\n"
            "  1. 环境变量：export YOUTUBE_API_KEY=你的key\n"
            f"  2. 在 {SKILL_DIR}/.env 写入：YOUTUBE_API_KEY=你的key\n"
            "  3. 在 ~/.config/cyxj/.env 写入：YOUTUBE_API_KEY=你的key\n"
            "如有多个 key 想轮询，按 YOUTUBE_API_KEY_2 / YOUTUBE_API_KEY_3 命名。\n"
            "获取 API key：https://console.cloud.google.com/apis/credentials",
            file=sys.stderr,
        )
        sys.exit(1)

    return [val for _, val in sorted(by_idx.items())]


def load_youtube_api_key() -> str:
    """向后兼容：返回首选 key（主 key 或最小序号的备用 key）。"""
    return load_youtube_api_keys()[0]


def load_apify_token() -> str:
    """按优先级查找 APIFY_API_TOKEN。必需配置，找不到报错退出。

    1. 环境变量 APIFY_API_TOKEN
    2. ${SKILL_DIR}/.env
    3. ~/.config/cyxj/.env
    """
    token = os.environ.get("APIFY_API_TOKEN")
    if token:
        return token.strip()

    for env_path in (SKILL_DIR / ".env", Path.home() / ".config" / "cyxj" / ".env"):
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("APIFY_API_TOKEN="):
                    return line.split("=", 1)[1].strip(' "\'\n\r')

    print(
        "错误：未找到 APIFY_API_TOKEN。请按以下任一方式配置：\n"
        "  1. 环境变量：export APIFY_API_TOKEN=你的token\n"
        f"  2. 在 {SKILL_DIR}/.env 写入：APIFY_API_TOKEN=你的token\n"
        "  3. 在 ~/.config/cyxj/.env 写入：APIFY_API_TOKEN=你的token\n"
        "获取方式：apify.com 注册 → Settings → API & Integrations → Personal API Token\n"
        "另外需要在 Apify Store 搜索并 bookmark Actor：karamelo/youtube-transcripts",
        file=sys.stderr,
    )
    sys.exit(1)


def load_supadata_key() -> str:
    """按优先级查找 SUPADATA_API_KEY。可选配置，找不到返回空字符串。

    1. 环境变量 SUPADATA_API_KEY
    2. ${SKILL_DIR}/.env
    3. ~/.config/cyxj/.env
    """
    key = os.environ.get("SUPADATA_API_KEY")
    if key:
        return key.strip()

    for env_path in (SKILL_DIR / ".env", Path.home() / ".config" / "cyxj" / ".env"):
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("SUPADATA_API_KEY="):
                    return line.split("=", 1)[1].strip(' "\'\n\r')

    return ""


def get_topic_dir() -> Path:
    """返回 Obsidian 选题库目录路径。从环境变量 CYXJ_TOPIC_DIR 读取。"""
    env_path = os.environ.get("CYXJ_TOPIC_DIR")
    if not env_path:
        print(
            "错误：未设置 CYXJ_TOPIC_DIR 环境变量。\n"
            "请指向你 Obsidian 库中存放 YouTube 选题的目录，例如：\n"
            "  export CYXJ_TOPIC_DIR=\"$HOME/obsidian/灵感库/选题库\"\n"
            "建议把这一行加到 ~/.zshrc 或 ~/.bashrc。",
            file=sys.stderr,
        )
        sys.exit(1)
    return Path(env_path).expanduser()


def get_state_dir() -> Path:
    """返回流水线状态文件的存放目录（话题索引 / 创作者索引 / 判断日志 / .seen_video_ids）。

    关键：这些是机器内部状态，**不放进 iCloud / Obsidian 同步目录**。iCloud 同步守护进程
    （bird/fileproviderd）会对同步目录加 advisory lock，写盘时连写多文件会撞
    `OSError: [Errno 11] Resource deadlock avoided`。把状态文件放本地非同步目录可从根上避开。
    （供人阅读的 .md 总览仍留在 CYXJ_TOPIC_DIR / iCloud。）

    默认：~/Library/Application Support/cyxj-youtube-topics/state
    可用环境变量 CYXJ_STATE_DIR 覆盖。目录不存在则自动创建。
    """
    env_path = os.environ.get("CYXJ_STATE_DIR")
    if env_path:
        state_dir = Path(env_path).expanduser()
    else:
        state_dir = (
            Path.home() / "Library" / "Application Support"
            / "cyxj-youtube-topics" / "state"
        )
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


def load_user_profile() -> str:
    """返回用户个人档案的纯文本内容。可用于判断层做差异化建议。

    优先读 CYXJ_USER_PROFILE 环境变量指向的文件。找不到返回空字符串（判断层会降级）。
    """
    env_path = os.environ.get("CYXJ_USER_PROFILE")
    if env_path:
        p = Path(env_path).expanduser()
        if p.exists():
            try:
                return p.read_text(encoding="utf-8")
            except Exception:
                pass
    return ""
