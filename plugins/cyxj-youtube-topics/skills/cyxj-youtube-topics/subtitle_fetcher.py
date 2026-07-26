#!/usr/bin/env python3
"""拉 YouTube 视频字幕前 N 秒的纯文本。

主路径：Apify Actor `scrape-creators/best-youtube-transcripts-scraper`。
Fallback：Supadata（独立服务商，独立 IP 池）。
karamelo 与新主路径同属 Apify、共用同一额度，保留它做兜底没有意义，因此删除。

设计约束：
- 入口签名 fetch_subtitle(video_url_or_id, max_seconds=180) 不变
- max_seconds=None 时返回全文
- 失败返回 None 不抛异常
- 返回约前 max_seconds*60 字符的纯文本（粗估，无时间戳按字符数截断；足够判断角度）
- stderr 打印耗时和失败原因
"""

import html
import json
import re
import sys
import time
import urllib.request

from paths import load_apify_token, load_supadata_key

DEFAULT_MAX_SECONDS = 180

VIDEO_ID_PATTERN = re.compile(r"([0-9A-Za-z_-]{11})")


def _normalize(video_url_or_id: str):
    """归一化为 (video_id, url)。无法解析返回 (None, None)。"""
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", video_url_or_id):
        return video_url_or_id, f"https://www.youtube.com/watch?v={video_url_or_id}"
    m = VIDEO_ID_PATTERN.search(video_url_or_id)
    if not m:
        return None, None
    return m.group(1), video_url_or_id


def _truncate(text: str, max_seconds: int | None) -> str:
    if max_seconds is None:
        return text
    return text[: max_seconds * 60]


def _fetch_via_scrape_creators(vid: str, max_seconds: int | None):
    """主路径：Apify scrape-creators Actor。失败返回 None。"""
    try:
        token = load_apify_token()
        api_url = (
            "https://api.apify.com/v2/acts/"
            "scrape-creators~best-youtube-transcripts-scraper"
            "/run-sync-get-dataset-items"
        )
        body = json.dumps(
            {"videoUrls": [f"https://www.youtube.com/watch?v={vid}"]}
        ).encode("utf-8")
        req = urllib.request.Request(
            api_url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "curl/8.4.0",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            if not (200 <= r.status < 300):
                print(
                    f"warn scrape-creators {vid}: HTTP {r.status}",
                    file=sys.stderr,
                )
                return None
            items = json.loads(r.read())
    except Exception as e:
        print(
            f"warn scrape-creators {vid}: {type(e).__name__} {str(e)[:120]}",
            file=sys.stderr,
        )
        return None

    if not items:
        return None
    item = items[0] or {}

    text = item.get("transcript_only_text")
    if not text:
        transcript = item.get("transcript") or []
        text = " ".join(
            str(part.get("text") or "")
            for part in transcript
            if isinstance(part, dict)
        )
    if isinstance(text, str):
        text = re.sub(r"\s+", " ", html.unescape(text)).strip()
        if text:
            return _truncate(text, max_seconds)
    return None


def _fetch_via_supadata(vid: str, max_seconds: int | None):
    """Fallback：Supadata。文本模式无时间戳，按字符数粗估截断。失败返回 None。"""
    try:
        key = load_supadata_key()
    except Exception as e:
        print(
            f"warn supadata {vid}: {type(e).__name__} {str(e)[:120]}",
            file=sys.stderr,
        )
        return None
    if not key:
        return None
    api_url = (
        f"https://api.supadata.ai/v1/youtube/transcript?videoId={vid}&text=true"
    )
    req = urllib.request.Request(
        api_url,
        headers={
            "x-api-key": key,
            "User-Agent": "curl/8.4.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            if r.status != 200:
                print(f"warn supadata {vid}: HTTP {r.status}", file=sys.stderr)
                return None
            d = json.loads(r.read())
    except Exception as e:
        print(
            f"warn supadata {vid}: {type(e).__name__} {str(e)[:120]}",
            file=sys.stderr,
        )
        return None

    text = d.get("content", "")
    if not text:
        return None
    return _truncate(text, max_seconds)


def fetch_subtitle(
    video_url_or_id: str, max_seconds: int | None = DEFAULT_MAX_SECONDS
):
    """拉字幕纯文本；max_seconds=None 返回全文。失败返回 None。
    主路径 Apify scrape-creators，失败 fallback 到 Supadata。"""
    vid, _ = _normalize(video_url_or_id)
    if not vid:
        return None

    t0 = time.monotonic()
    text = _fetch_via_scrape_creators(vid, max_seconds)
    dt = (time.monotonic() - t0) * 1000
    if text:
        print(
            f"info subtitle {vid}: scrape-creators 成功（{dt:.0f}ms）",
            file=sys.stderr,
        )
        return text

    print(
        f"info subtitle {vid}: scrape-creators 未取到（{dt:.0f}ms），"
        "fallback supadata",
        file=sys.stderr,
    )
    t1 = time.monotonic()
    text = _fetch_via_supadata(vid, max_seconds)
    dt2 = (time.monotonic() - t1) * 1000
    if text:
        print(f"info subtitle {vid}: supadata 成功（{dt2:.0f}ms）", file=sys.stderr)
    else:
        print(f"info subtitle {vid}: supadata 也失败（{dt2:.0f}ms）", file=sys.stderr)
    return text


def main():
    if len(sys.argv) < 2:
        print(
            "用法: python3 subtitle_fetcher.py <video_url_or_id> [max_seconds]",
            file=sys.stderr,
        )
        sys.exit(1)
    max_s = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MAX_SECONDS
    text = fetch_subtitle(sys.argv[1], max_s)
    if text is None:
        sys.exit(2)
    print(text)


if __name__ == "__main__":
    main()
