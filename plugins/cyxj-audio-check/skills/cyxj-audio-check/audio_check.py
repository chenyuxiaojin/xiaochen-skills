#!/usr/bin/env python3
"""cyxj-audio-check · 成片音频体检(只读,不改任何文件)

用法:
  python3 audio_check.py <成片.mp4> [--master 母带.mov] [--target -14] [--tp -1] [--json]

依赖:ffmpeg / ffprobe 在 PATH。numpy 可选(只有 --master 对齐检查用到,没有就跳过)。
输出:一张放行表 + 结论(可发 / 不可发 + 病因 + 修法编号,修法见 references/davinci-playbook.md)。
"""
import argparse, json, math, re, shutil, subprocess, sys
from array import array

OK, WARN, FAIL = "✅", "⚠️", "❌"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def need_tools():
    for t in ("ffmpeg", "ffprobe"):
        if not shutil.which(t):
            sys.exit(f"找不到 {t},先 brew install ffmpeg")


# ---------- 容器 / 码率 ----------
def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration,bit_rate,size",
             "-show_streams", "-of", "json", path])
    if r.returncode:
        sys.exit(f"ffprobe 失败:{r.stderr.strip()}")
    d = json.loads(r.stdout)
    v = next((s for s in d["streams"] if s.get("codec_type") == "video"), None)
    a = next((s for s in d["streams"] if s.get("codec_type") == "audio"), None)
    fps = 0.0
    if v and v.get("r_frame_rate"):
        n, _, m = v["r_frame_rate"].partition("/")
        fps = float(n) / float(m) if m and float(m) else float(n)
    return {
        "duration": float(d["format"].get("duration", 0) or 0),
        "size_mb": float(d["format"].get("size", 0) or 0) / 1e6,
        "video": v and {"codec": v.get("codec_name"), "w": int(v.get("width", 0)), "h": int(v.get("height", 0)),
                        "fps": fps, "kbps": int(v.get("bit_rate") or 0) / 1000, "frames": v.get("nb_frames"),
                        "pix_fmt": v.get("pix_fmt")},
        "audio": a and {"codec": a.get("codec_name"), "sr": int(a.get("sample_rate") or 0),
                        "ch": int(a.get("channels") or 0), "kbps": int(a.get("bit_rate") or 0) / 1000},
    }


def video_floor_mbps(w, h, fps):
    """YouTube 推荐上传码率(SDR)的下限。"""
    px, hi = w * h, fps > 40
    if px >= 3840 * 2160 * 0.9: return 53 if hi else 35
    if px >= 2560 * 1440 * 0.9: return 24 if hi else 16
    if px >= 1920 * 1080 * 0.9: return 12 if hi else 8
    if px >= 1280 * 720 * 0.9: return 7.5 if hi else 5
    return 2.5


# ---------- 响度 / 峰值 ----------
def loudness(path):
    r = run(["ffmpeg", "-v", "info", "-nostats", "-i", path, "-map", "0:a:0",
             "-af", "ebur128=peak=true", "-f", "null", "-"])
    out = r.stderr

    def grab(key):
        m = re.search(rf"^\s+{key}:\s+(-?[\d.]+|-inf)", out, re.M)
        return None if not m or m.group(1) == "-inf" else float(m.group(1))
    return {"I": grab("I"), "LRA": grab("LRA"), "TP": grab("Peak")}


def stats(path):
    r = run(["ffmpeg", "-v", "info", "-nostats", "-i", path, "-map", "0:a:0", "-af",
             "astats=measure_perchannel=RMS_level+Peak_level:measure_overall=Peak_level+Flat_factor+Peak_count",
             "-f", "null", "-"])
    section, per, overall = None, {}, {}
    for line in r.stderr.splitlines():
        line = re.sub(r"^\[.*?\]\s*", "", line)
        m = re.match(r"Channel:\s*(\d+)", line)
        if m:
            section = int(m.group(1)); per[section] = {}; continue
        if line.startswith("Overall"):
            section = "overall"; continue
        m = re.match(r"(RMS level dB|Peak level dB|Flat factor|Peak count):\s*(-?[\d.]+|-inf|nan)", line)
        if m and section is not None:
            val = m.group(2)
            val = None if val in ("-inf", "nan") else float(val)
            (overall if section == "overall" else per[section])[m.group(1)] = val
    return per, overall


# ---------- 静音段 ----------
def silences(path, duration, noise="-45dB", min_len=1.5):
    r = run(["ffmpeg", "-v", "info", "-nostats", "-i", path, "-map", "0:a:0",
             "-af", f"silencedetect=n={noise}:d={min_len}", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*(-?[\d.]+)", r.stderr)]
    while len(ends) < len(starts):
        ends.append(duration)
    return [(s, e) for s, e in zip(starts, ends)]


# ---------- BGM / 人声比例(估算) ----------
def decode_mono(path, sr=8000):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-ac", "1", "-ar", str(sr),
                        "-f", "s16le", "-"], capture_output=True)
    a = array("h"); a.frombytes(r.stdout)
    return a


def block_db(samples, sr=8000, step=0.1):
    n = int(sr * step)
    try:
        import numpy as np
        x = np.frombuffer(samples.tobytes(), dtype=np.int16).astype(np.float64) / 32768
        k = len(x) // n
        rms = np.sqrt((x[:k * n].reshape(k, n) ** 2).mean(axis=1))
        return (20 * np.log10(rms + 1e-9)).tolist()
    except ImportError:
        out = []
        for i in range(0, len(samples) - n + 1, n):
            s = 0
            for v in samples[i:i + n]:
                s += v * v
            out.append(20 * math.log10(math.sqrt(s / n) / 32768 + 1e-9))
        return out


def pct(vals, p):
    if not vals: return None
    s = sorted(vals); i = max(0, min(len(s) - 1, int(round((len(s) - 1) * p))))
    return s[i]


def bgm_ratio(mix_blocks, master_blocks=None):
    """返回 (人声段 dBFS, BGM 段 dBFS, 差值 dB, 方法)。
    有母带(纯人声)时用母带找停顿位置,准;没有就用成片自身分布估算。"""
    if master_blocks:
        n = min(len(mix_blocks), len(master_blocks))
        pause = [mix_blocks[i] for i in range(n) if -99 < master_blocks[i] < -60]
        speech = [mix_blocks[i] for i in range(n) if master_blocks[i] > -40]
        if len(pause) >= 10 and speech:
            v, b = pct(speech, 0.5), pct(pause, 0.5)
            return v, b, v - b, "母带定位停顿"
    live = [x for x in mix_blocks if x > -70]
    if len(live) < 50:
        return None, None, None, "样本不足"
    v, b = pct(live, 0.5), pct(live, 0.03)  # 2026-09-04 用两条实片对母带法校准,误差 <0.5 dB
    return v, b, v - b, "成片自身估算,给母带更准"


def aligned_master_blocks(master_blocks, n_mix, offsets, step=0.1):
    """把母带块按检测到的分段位移对到成片时间轴上;对不上的位置填 -100 哨兵。母带时间 = 成片时间 + off。"""
    ts = [t for t, _, _ in offsets] if offsets else []
    out = []
    for i in range(n_mix):
        ti = i * step
        off = offsets[min(range(len(ts)), key=lambda j: abs(ts[j] - ti))][1] if ts else 0.0
        j = int(round((ti + off) / step))
        out.append(master_blocks[j] if 0 <= j < len(master_blocks) else -100.0)
    return out


# ---------- 与母带对齐 ----------
def align(mix_path, master_path, duration):
    try:
        import numpy as np
    except ImportError:
        return None
    sr = 8000
    a = np.frombuffer(decode_mono(mix_path, sr).tobytes(), dtype=np.int16).astype(float)
    b = np.frombuffer(decode_mono(master_path, sr).tobytes(), dtype=np.int16).astype(float)
    res, win, search = [], 8, 2.5
    t = 10
    while t + win + search < min(len(a), len(b)) / sr:
        ea = a[int(t * sr):int((t + win) * sr)]
        mb = b[int((t - search) * sr):int((t + win + search) * sr)]
        ea = ea - ea.mean(); mb = mb - mb.mean(); n = len(ea) + len(mb)
        c = np.fft.irfft(np.fft.rfft(ea, n) * np.conj(np.fft.rfft(mb, n)), n)
        k = int(np.argmax(c)); k = k - n if k > n // 2 else k
        corr = float(c.max() / (np.sqrt((ea ** 2).sum() * (mb ** 2).sum()) + 1e-9))
        res.append((t, -(search + k / sr), corr))  # 母带时间 = 成片时间 - off  → off<0 表示成片这里比母带早
        t += 20
    return res


# ---------- 主流程 ----------
def check(path, master=None, target=-14.0, tp_limit=-1.0):
    need_tools()
    p = probe(path)
    if not p["audio"]:
        sys.exit("这个文件没有音轨。")
    dur = p["duration"]
    loud = loudness(path)
    per, overall = stats(path)
    sil = [(s, e) for s, e in silences(path, dur) if s > 1.0 and e < dur - 3.0]
    mix_blocks = block_db(decode_mono(path))
    master_blocks = block_db(decode_mono(master)) if master else None
    offsets = align(path, master, dur) if master else None
    if master_blocks:
        master_blocks = aligned_master_blocks(master_blocks, len(mix_blocks), offsets)
    v_db, b_db, ratio, method = bgm_ratio(mix_blocks, master_blocks)

    rows, fixes = [], []

    def row(status, item, value, note=""):
        rows.append((status, item, value, note))

    # 码率
    if p["video"]:
        v = p["video"]; floor = video_floor_mbps(v["w"], v["h"], v["fps"]); mbps = v["kbps"] / 1000
        st = OK if mbps >= floor else (WARN if mbps >= floor * 0.85 else FAIL)
        row(st, "视频码率", f"{mbps:.1f} Mbps({v['w']}×{v['h']} {v['fps']:.0f}fps {v['codec']})",
            f"推荐 ≥ {floor} Mbps" + {OK: "", WARN: ",略低:画面简单时编码器自然用得少,可发", FAIL: ",明显偏低,重导时把码率调高"}[st])
        if st == FAIL: fixes.append("F6")
    a = p["audio"]
    st = OK if a["kbps"] >= 192 else (WARN if a["kbps"] >= 128 else FAIL)
    row(st, "音频编码", f"{a['codec']} {a['kbps']:.0f} kbps {a['sr']} Hz {a['ch']}ch",
        "" if a["sr"] == 48000 else "采样率不是 48k,平台会重采样")
    if st == FAIL: fixes.append("F6")

    # 响度
    I = loud["I"]
    if I is None:
        row(FAIL, "整片响度", "测不到", "音轨可能是静音"); fixes.append("F2")
    elif I < target - 2:
        row(FAIL, "整片响度", f"{I:.1f} LUFS", f"目标 {target:.0f},低了 {target - I:.1f} dB,平台不会帮你抬"); fixes.append("F2")
    elif I > target + 2:
        row(WARN, "整片响度", f"{I:.1f} LUFS", f"目标 {target:.0f},偏响,平台会压下来,可发")
    else:
        row(OK, "整片响度", f"{I:.1f} LUFS", f"目标 {target:.0f}")

    LRA = loud["LRA"]
    if LRA is not None and LRA > 12:
        row(WARN, "响度范围", f"{LRA:.1f} LU", "忽大忽小;口播一般 < 8 LU"); fixes.append("F5")

    TP = loud["TP"]
    flat = overall.get("Flat factor") or 0.0
    if TP is None:
        row(WARN, "真峰值", "测不到", "")
    elif TP > tp_limit + 0.05 or flat > 0.5:
        row(FAIL, "真峰值 / 削波", f"{TP:.1f} dBTP,削波系数 {flat:.1f}", f"上限 {tp_limit:.0f} dBTP;超了会破音"); fixes.append("F3")
    else:
        row(OK, "真峰值 / 削波", f"{TP:.1f} dBTP,无削波", f"上限 {tp_limit:.0f} dBTP")

    # 左右声道
    if a["ch"] >= 2 and 1 in per and 2 in per and per[1].get("RMS level dB") is not None and per[2].get("RMS level dB") is not None:
        l, r = per[1]["RMS level dB"], per[2]["RMS level dB"]
        diff = abs(l - r)
        if diff > 1.5:
            side = "右" if r > l else "左"
            row(FAIL, "左右声道", f"L {l:.1f} / R {r:.1f} dB", f"{side}声道响 {diff:.1f} dB,耳机听人声偏{side}"); fixes.append("F1")
        else:
            row(OK, "左右声道", f"L {l:.1f} / R {r:.1f} dB", "平衡")
    else:
        row(OK, "左右声道", f"{a['ch']} 声道", "单声道无此问题" if a["ch"] == 1 else "")

    # BGM 比例
    if ratio is None:
        row(WARN, "BGM / 人声", "估不出", method)
    elif b_db is not None and b_db < -65:
        row(OK, "BGM / 人声", f"人声 {v_db:.1f} dBFS,停顿处 {b_db:.1f} dBFS", f"基本没有 BGM({method})")
    elif ratio < 10:
        row(FAIL, "BGM / 人声", f"BGM 只比人声低 {ratio:.0f} dB", f"要 15-20 dB;BGM 太大({method})"); fixes.append("F4")
    elif ratio < 15:
        row(WARN, "BGM / 人声", f"BGM 比人声低 {ratio:.0f} dB", f"要 15-20 dB,偏大一点({method})")
    elif ratio > 26:
        row(WARN, "BGM / 人声", f"BGM 比人声低 {ratio:.0f} dB", f"几乎听不见,想要有就抬一点({method})")
    else:
        row(OK, "BGM / 人声", f"BGM 比人声低 {ratio:.0f} dB", f"要 15-20 dB({method})")

    # 静音段
    if sil:
        desc = ",".join(f"{s:.1f}-{e:.1f}s" for s, e in sil[:5]) + ("…" if len(sil) > 5 else "")
        row(WARN, "片中静音", f"{len(sil)} 段 >1.5s", desc + ";确认不是漏音")
    else:
        row(OK, "片中静音", "无 >1.5s 空白", "")

    # 对齐
    if master:
        if offsets is None:
            row(WARN, "与母带对齐", "跳过", "缺 numpy(pip install numpy)")
        else:
            shifted = [(t, o) for t, o, c in offsets if abs(o) > 0.02]
            if not shifted:
                row(OK, "与母带对齐", "全程 0 位移", f"抽查 {len(offsets)} 处")
            else:
                t0, o0 = shifted[0]
                row(WARN, "与母带对齐", f"约 {t0}s 起偏移 {o0:+.2f}s", "达芬奇里有剪切;确认画面和字幕跟着一起移了")

    verdict_fail = [r for r in rows if r[0] == FAIL]
    verdict = "不可发" if verdict_fail else "可发"
    return {"file": path, "duration": dur, "probe": p, "loudness": loud, "rows": rows,
            "verdict": verdict, "fixes": sorted(set(fixes)), "offsets": offsets}


FIX_TEXT = {
    "F1": "F1 声道:达芬奇选中人声片段 → 右键「片段属性」→ 音频 → 格式 Mono、源声道选实际有声的那个(内嵌通道 1=左 / 2=右)。应急:audio_fix.py remaster --mono-from right",
    "F2": "F2 响度:交付页 → 音频归一化 → 勾「归一化音频」→「优化至标准」→ 标准选 YouTube(-14 LKFS / -1 dBTP)。应急:audio_fix.py remaster",
    "F3": "F3 峰值/削波:先把总线或人声推子降 3 dB,再用交付页「优化至标准」。应急:audio_fix.py remaster",
    "F4": "F4 BGM 太大:音乐轨推子拉到人声下 18 dB 左右;或音频助手重跑(素材全放好后最后一步跑)。应急:audio_fix.py mix --voice 人声 --bgm 音乐",
    "F5": "F5 忽大忽小:人声片段先「归一化音频电平」(BS.1770-4,-16)拉平,再跑音频助手做对白拉平,最后交付页「优化至标准」",
    "F6": "F6 码率:交付页把视频码率调到下限以上(4K30 ≥ 35 Mbps,1080p ≥ 8 Mbps),音频 AAC 320 kbps 48 kHz",
}


def render(res):
    p = res["probe"]; dur = res["duration"]
    print(f"文件:{res['file']}")
    print(f"时长:{int(dur // 60)}:{dur % 60:04.1f}  大小:{p['size_mb']:.0f} MB")
    print()
    for st, item, value, note in res["rows"]:
        print(f"{st} {item}:{value}" + (f"  ← {note}" if note else ""))
    print()
    print(f"结论:{'✅' if res['verdict'] == '可发' else '❌'} {res['verdict']}")
    if res["fixes"]:
        print("修法(细节见 references/davinci-playbook.md):")
        for f in res["fixes"]:
            print("  " + FIX_TEXT[f])


def main():
    ap = argparse.ArgumentParser(description="成片音频体检")
    ap.add_argument("file")
    ap.add_argument("--master", help="无 BGM 的母带/纯人声文件,用于停顿定位和对齐检查")
    ap.add_argument("--target", type=float, default=-14.0, help="目标响度 LUFS,默认 -14")
    ap.add_argument("--tp", type=float, default=-1.0, help="真峰值上限 dBTP,默认 -1")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = check(a.file, a.master, a.target, a.tp)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    else:
        render(res)
    sys.exit(0 if res["verdict"] == "可发" else 1)


if __name__ == "__main__":
    main()
