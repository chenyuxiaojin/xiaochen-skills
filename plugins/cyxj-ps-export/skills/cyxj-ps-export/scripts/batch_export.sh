#!/bin/bash
# batch_export.sh - 批量把指定目录的图片用 Photoshop 重新过一遍，输出 JPG
# 用法: batch_export.sh <源目录> [输出目录] [质量 1-12]
# 默认: 输出目录 = <源目录>_ps；质量 = 12（PS 最高档）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SRC="${1:-}"
if [ -z "$SRC" ]; then
    echo "用法: batch_export.sh <源目录> [输出目录] [质量 1-12]"
    echo ""
    echo "示例:"
    echo "  batch_export.sh /Users/chenhuajin/Pictures/AI生成"
    echo "  batch_export.sh ~/Pictures/foo ~/Desktop/foo_ps 11"
    exit 1
fi

# 展开 ~ 和相对路径
SRC=$(cd "$SRC" 2>/dev/null && pwd) || { echo "源目录不存在: $1"; exit 1; }

OUT="${2:-${SRC}_ps}"
QUALITY="${3:-12}"

# 校验质量范围
if ! [[ "$QUALITY" =~ ^([1-9]|1[0-2])$ ]]; then
    echo "质量必须是 1-12，当前: $QUALITY"
    exit 1
fi

mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)

# 找 PS 应用名（兼容多版本）
PS_APP=$(ls /Applications/ 2>/dev/null | grep -i "^Adobe Photoshop" | head -1)
if [ -z "$PS_APP" ]; then
    echo "未找到 Adobe Photoshop。请确认已安装在 /Applications/。"
    exit 1
fi

# 统计源文件数
TOTAL=$(find "$SRC" -maxdepth 1 -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" \) | wc -l | xargs)

echo "===== PS 批量过图 ====="
echo "PS 版本: $PS_APP"
echo "源目录:  $SRC"
echo "输出:    $OUT"
echo "质量:    $QUALITY (PS Save As, Progressive 3 Scans)"
echo "待处理:  $TOTAL 张"
echo ""

if [ "$TOTAL" -eq 0 ]; then
    echo "源目录里没有图片（png/jpg/jpeg），跳过。"
    exit 0
fi

# 生成临时 jsx（注入参数）
TMP_JSX=$(mktemp -t cyxj_ps_XXXXXX).jsx
trap "rm -f $TMP_JSX" EXIT

# 转义 JS 字符串里的特殊字符
JS_SRC=$(printf '%s' "$SRC" | sed 's/\\/\\\\/g; s/"/\\"/g')
JS_OUT=$(printf '%s' "$OUT" | sed 's/\\/\\\\/g; s/"/\\"/g')

cat > "$TMP_JSX" <<EOF
#target photoshop

var srcDir = "$JS_SRC";
var outDir = "$JS_OUT";
var QUALITY = $QUALITY;

var outFolder = new Folder(outDir);
if (!outFolder.exists) outFolder.create();

var logFile = new File(outDir + "/batch_export.log");
function log(msg) {
    logFile.open("a");
    logFile.writeln(msg);
    logFile.close();
}
logFile.open("w");
logFile.writeln("Start: " + (new Date()).toString());
logFile.writeln("Quality: " + QUALITY + " (PS Save As, Progressive 3 Scans)");
logFile.close();

var srcFolder = new Folder(srcDir);
var files = srcFolder.getFiles(function(f) {
    return (f instanceof File) && /\\.(png|jpe?g)\$/i.test(f.name);
});

log("Found: " + files.length + " files");

var saveOpts = new JPEGSaveOptions();
saveOpts.quality = QUALITY;
saveOpts.embedColorProfile = true;
saveOpts.formatOptions = FormatOptions.PROGRESSIVE;
saveOpts.scans = 3;
saveOpts.matte = MatteType.NONE;

var success = 0;
var failed = 0;

for (var i = 0; i < files.length; i++) {
    var srcFile = files[i];
    var baseName = srcFile.name.replace(/\\.[^.]+\$/, "");
    var outFile = new File(outDir + "/" + baseName + ".jpg");

    try {
        var doc = app.open(srcFile);
        doc.saveAs(outFile, saveOpts, true, Extension.LOWERCASE);
        doc.close(SaveOptions.DONOTSAVECHANGES);
        success++;
        log("[OK " + (i + 1) + "/" + files.length + "] " + srcFile.name);
    } catch (e) {
        failed++;
        log("[FAIL " + (i + 1) + "/" + files.length + "] " + srcFile.name + " - " + e.toString());
        try { if (app.documents.length > 0) app.activeDocument.close(SaveOptions.DONOTSAVECHANGES); } catch (e2) {}
    }
}

log("Done. Success: " + success + ", Failed: " + failed);
log("End: " + (new Date()).toString());
EOF

echo "PS 启动中..."
START=$(date +%s)

osascript -e "tell application \"$PS_APP\" to do javascript file \"$TMP_JSX\"" >/dev/null

exiftool -overwrite_original -UserComment= -SourceFile= "$OUT"/*.jpg 2>/dev/null || true

END=$(date +%s)
ELAPSED=$((END - START))

echo ""
echo "===== 完成（耗时 ${ELAPSED} 秒）====="

LOG="$OUT/batch_export.log"
if [ -f "$LOG" ]; then
    SUCCESS=$(grep -c "^\[OK" "$LOG" 2>/dev/null; true)
    FAIL=$(grep -c "^\[FAIL" "$LOG" 2>/dev/null; true)
    SUCCESS=${SUCCESS:-0}
    FAIL=${FAIL:-0}
    OUT_COUNT=$(ls "$OUT"/*.jpg 2>/dev/null | wc -l | xargs)
    SIZE=$(du -sh "$OUT" 2>/dev/null | awk '{print $1}')
    echo "处理:    成功 $SUCCESS · 失败 $FAIL"
    echo "实际输出: $OUT_COUNT 张 JPG · 总大小 $SIZE"
    echo "输出位置: $OUT"
    if [ "$FAIL" -gt 0 ]; then
        echo ""
        echo "===== 失败清单 ====="
        grep "^\[FAIL" "$LOG"
    fi
    if [ "$OUT_COUNT" -lt "$SUCCESS" ]; then
        DIFF=$((SUCCESS - OUT_COUNT))
        echo ""
        echo "提示: 处理了 $SUCCESS 张但实际只有 $OUT_COUNT 张输出文件——"
        echo "      可能源目录里有同名 PNG 和 JPEG 对（如 foo.png + foo.jpeg），输出会互相覆盖。"
        echo "      差 $DIFF 张。如需保留所有版本，请改用不同的源目录结构。"
    fi
fi
