#!/usr/bin/env python3
"""cyxj-image-studio 插件级共享模块：GPTIMG2 中转站凭据加载 + base URL 规整。

被 skills/cyxj-poster 和 skills/cyxj-video-cover 的脚本共用。只用标准库——
video-cover 的「零第三方依赖」属性依赖这一点，不要在这里引入 requests 等包。

约定：
- GPTIMG2_BASE_URL 官方形态是 https://api.chatgpt-code.com（末尾没有 /v1），
  但用户误填带 /v1 的也要接受。
- load_gptimg2() 返回的 base 统一为「无末尾斜杠、无 /v1」；
  需要拼端点时用 api_base(base) 得到以 /v1 结尾的形态。
"""

import os
import sys

DEFAULT_ENV_FILE = "~/项目/自己的应用/密钥存储/.env"


def api_base(base: str) -> str:
    """规整成以 /v1 结尾（不含末尾斜杠），可直接拼 /images/edits 等端点。"""
    base = base.rstrip("/")
    if not base.endswith("/v1"):
        base = base + "/v1"
    return base


def load_gptimg2() -> tuple[str, str]:
    """读 GPTIMG2_BASE_URL / GPTIMG2_API_KEY：环境变量优先，否则解析密钥存储 .env。

    .env 路径可用 GPTIMG2_ENV_FILE 覆盖（默认 ~/项目/自己的应用/密钥存储/.env）。
    解析容忍引号、空格和注释行。

    Returns:
        (base, key)。base 无末尾斜杠、无 /v1（要带 /v1 的形态用 api_base()）。
        找不到凭据时打印指引并 sys.exit(1)。
    """
    base = os.environ.get("GPTIMG2_BASE_URL")
    key = os.environ.get("GPTIMG2_API_KEY")

    env_path = os.path.expanduser(os.environ.get("GPTIMG2_ENV_FILE") or DEFAULT_ENV_FILE)
    if not base or not key:
        try:
            with open(env_path, encoding="utf-8") as f:
                for ln in f:
                    ln = ln.strip()
                    if ln.startswith("#") or "=" not in ln:
                        continue
                    k, _, v = ln.partition("=")
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k == "GPTIMG2_BASE_URL" and not base:
                        base = v
                    elif k == "GPTIMG2_API_KEY" and not key:
                        key = v
        except FileNotFoundError:
            pass

    if not base or not key:
        print(
            "❌ 找不到中转站配置。需要 GPTIMG2_BASE_URL 和 GPTIMG2_API_KEY。\n"
            f"   已查找：环境变量 + {env_path}\n"
            "   请在密钥存储 .env 里确认这两行存在，或先 export；\n"
            "   .env 路径可用 GPTIMG2_ENV_FILE 环境变量指定。",
            file=sys.stderr,
        )
        sys.exit(1)

    base = base.rstrip("/")
    if base.endswith("/v1"):
        base = base[: -len("/v1")]
    return base, key
