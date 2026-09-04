#!/usr/bin/env python3
"""cyxj-audio-check · ffmpeg 音频修复 / 混音(画面原样拷贝,不重编码视频;永远输出新文件,不碰原文件)

两种模式:
  remaster  已混好的成片只修音轨:声道修正 + 两遍 loudnorm 到目标响度
      python3 audio_fix.py remaster <成片.mp4> [--mono-from right|left|mix] [--target -14] [--tp -1] [-o 输出]

  mix       人声 + BGM 重新混:声道修正 → BGM 压到人声下 N dB → 人声一出音乐自动闪避(侧链) → 两遍 loudnorm
      python3 audio_fix.py mix --voice <人声.wav|带人声的视频> --bgm <音乐.mp3> [--video <画面视频>]
             [--voice-channel right|left|mix] [--bgm-under 14] [--duck 4] [--target -14] [--tp -1] [-o 输出]

跑完自动调用 audio_check.py 复测输出文件。
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audio_check  # noqa: E402


def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit("ffmpeg 出错:\n" + r.stderr[-2000:])
    return r


def pan_expr(sel):
    return {"right": "pan=mono|c0=c1", "left": "pan=mono|c0=c0", "mix": "pan=mono|c0=0.5*c0+0.5*c1"}[sel]


def measure_loudnorm(src_args, filt, target, tp):
    """第一遍:测量。src_args 是 ffmpeg 输入参数列表,filt 是测量前要套的滤镜(可空)。"""
    chain = (filt + "," if filt else "") + f"loudnorm=I={target}:TP={tp - 1.0}:LRA=7:print_format=json"
    r = run(["ffmpeg", "-v", "info", "-nostats", *src_args, "-af", chain, "-f", "null", "-"], check=False)
    found = re.findall(r"\{[^{}]*\}", r.stderr, re.S)
    if not found:
        sys.exit("loudnorm 测量失败:\n" + r.stderr[-1500:])
    return json.loads(found[-1])


def loudnorm_pass2(meas, target, tp):
    tp = tp - 1.0  # AAC 编码会让真峰值回弹 0.2-0.4 dB,先多留 1 dB 余量,成品才能稳在上限以下
    return (f"loudnorm=I={target}:TP={tp}:LRA=7:measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:"
            f"measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}:offset={meas['target_offset']}:"
            f"linear=true,aformat=sample_rates=48000")


def voice_loudness(path, filt):
    r = run(["ffmpeg", "-v", "info", "-nostats", "-i", path, "-map", "0:a:0", "-af",
             (filt + "," if filt else "") + "ebur128", "-f", "null", "-"], check=False)
    m = re.search(r"^\s+I:\s+(-?[\d.]+)", r.stderr, re.M)
    return float(m.group(1)) if m else None


def out_path(given, src, suffix):
    if given: return given
    base, ext = os.path.splitext(src)
    return f"{base}-{suffix}{ext if ext.lower() in ('.mp4', '.mov', '.mkv', '.m4a', '.wav') else '.mp4'}"


def is_video(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_type", "-of", "csv=p=0", path], check=False)
    return "video" in r.stdout


def remaster(a):
    src = a.file
    out = out_path(a.output, src, "audiofix")
    if os.path.abspath(out) == os.path.abspath(src):
        sys.exit("输出不能覆盖原文件")
    pre = ""
    if a.mono_from:
        pre = pan_expr(a.mono_from) + ",pan=stereo|c0=c0|c1=c0"
    meas = measure_loudnorm(["-i", src, "-map", "0:a:0"], pre, a.target, a.tp)
    chain = (pre + "," if pre else "") + loudnorm_pass2(meas, a.target, a.tp)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-map", "0:v:0?", "-map", "0:a:0",
           "-c:v", "copy", "-af", chain, "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", out]
    if not is_video(src):
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-map", "0:a:0", "-af", chain, "-c:a", "aac", "-b:a", "320k", out]
    run(cmd)
    print(f"已输出:{out}\n测量:原片 {meas['input_i']} LUFS / {meas['input_tp']} dBTP → 目标 {a.target} / {a.tp}\n")
    return out


def mix(a):
    voice, bgm = a.voice, a.bgm
    video = a.video or (voice if is_video(voice) else None)
    out = out_path(a.output, video or voice, "mix")
    if not video:
        out = os.path.splitext(out)[0] + ".m4a"
    vpan = pan_expr(a.voice_channel)
    vi = voice_loudness(voice, vpan)
    bi = voice_loudness(bgm, "aformat=channel_layouts=mono")
    if vi is None or bi is None:
        sys.exit("测不到人声或 BGM 的响度")
    bgm_gain = (vi - a.bgm_under) - bi                 # 先把 BGM 放到人声下 N dB
    thr = 10 ** ((vi - 10) / 20)                       # 侧链门槛:人声响度往下 10 dB
    graph = (f"[0:a]{vpan},asplit=2[v][sc];"
             f"[1:a]aformat=channel_layouts=mono,volume={bgm_gain:.2f}dB[m];"
             f"[m][sc]sidechaincompress=threshold={thr:.5f}:ratio={a.duck}:attack=40:release=600[d];"
             f"[v][d]amix=inputs=2:duration=first:normalize=0,pan=stereo|c0=c0|c1=c0[mix]")
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    run(["ffmpeg", "-v", "error", "-y", "-i", voice, "-stream_loop", "-1", "-i", bgm,
         "-filter_complex", graph, "-map", "[mix]", "-ar", "48000", tmp])
    meas = measure_loudnorm(["-i", tmp], "", a.target, a.tp)
    chain = loudnorm_pass2(meas, a.target, a.tp)
    if video:
        run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", tmp, "-map", "0:v:0", "-map", "1:a:0",
             "-c:v", "copy", "-af", chain, "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart", out])
    else:
        run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", chain, "-c:a", "aac", "-b:a", "320k", out])
    os.unlink(tmp)
    print(f"已输出:{out}\n人声 {vi:.1f} LUFS,BGM 原始 {bi:.1f} LUFS → BGM 增益 {bgm_gain:+.1f} dB(停顿处低于人声 {a.bgm_under} dB),"
          f"说话时再闪避约 {10 * (1 - 1 / a.duck):.0f} dB;混音 {meas['input_i']} LUFS → 目标 {a.target}\n")
    return out


def main():
    ap = argparse.ArgumentParser(description="ffmpeg 音频修复 / 混音")
    sub = ap.add_subparsers(dest="mode", required=True)
    r = sub.add_parser("remaster"); r.add_argument("file")
    r.add_argument("--mono-from", choices=["right", "left", "mix"], help="人声只在一边时,取哪一边做单声道")
    m = sub.add_parser("mix")
    m.add_argument("--voice", required=True); m.add_argument("--bgm", required=True); m.add_argument("--video")
    m.add_argument("--voice-channel", choices=["right", "left", "mix"], default="mix")
    m.add_argument("--bgm-under", type=float, default=14, help="停顿处 BGM 低于人声多少 dB,默认 14")
    m.add_argument("--duck", type=float, default=4, help="闪避压缩比,默认 4(说话时再压约 7 dB)")
    for p in (r, m):
        p.add_argument("--target", type=float, default=-14.0); p.add_argument("--tp", type=float, default=-1.0)
        p.add_argument("-o", "--output")
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("找不到 ffmpeg,先 brew install ffmpeg")
    out = remaster(a) if a.mode == "remaster" else mix(a)
    print("—— 复测 ——")
    res = audio_check.check(out, None, a.target, a.tp)
    audio_check.render(res)


if __name__ == "__main__":
    main()
