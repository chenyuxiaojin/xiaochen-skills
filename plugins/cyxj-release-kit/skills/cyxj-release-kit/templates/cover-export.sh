#!/bin/zsh
# 封面编辑器 → 三比例成品。用法:
#   ./导出.sh                 用 ~/Downloads 里最新的「封面布局-*.json」
#   ./导出.sh 某个布局.json    指定布局文件
#   ./导出.sh --factory       不用布局文件,按编辑器里的出厂位置
set -e
H="$(cd "$(dirname "$0")" && pwd)"; O="$(dirname "$H")"
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [[ "$1" == "--factory" ]]; then J=""; elif [[ -n "$1" ]]; then J="$1"; else J=$(ls -t ~/Downloads/封面布局-*.json 2>/dev/null | head -1); fi
if [[ -n "$J" ]]; then
  [[ -f "$J" ]] || { echo "找不到布局文件:$J"; exit 1; }
  [[ "$J" -ef "$H/布局.json" ]] || cp "$J" "$H/布局.json"; echo "用布局:$J(已复制到 源文件/布局.json)"
  S="&s=$(python3 -c 'import sys,base64,urllib.parse;print(urllib.parse.quote(base64.b64encode(open(sys.argv[1],"rb").read()).decode()))' "$J")"
else S=""; echo "用出厂布局"; fi
typeset -A SZ; SZ=(16x9 "2560,1440" 4x3 "2048,1536" 3x4 "1536,2048")
for r in 4x3 16x9 3x4; do
  "$C" --headless --disable-gpu --hide-scrollbars --window-size=${SZ[$r]} --virtual-time-budget=4000 \
       --screenshot="$O/封面_$r.png" "file://$H/cover-editor.html?export=1&r=$r$S" >/dev/null 2>&1
  sips -s format jpeg -s formatOptions 95 "$O/封面_$r.png" --out "$O/封面_$r.jpg" >/dev/null
  echo "✅ 封面_$r.png / .jpg  $(sips -g pixelWidth -g pixelHeight "$O/封面_$r.png" | awk '/pixel/{printf "%s ", $2}')"
done
ffmpeg -v error -y -i "$O/封面_4x3.png" -i "$O/封面_16x9.png" -i "$O/封面_3x4.png" -filter_complex "[0]scale=-1:900[a];[1]scale=-1:900[b];[2]scale=-1:900[c];[a][b][c]hstack=3" "$O/核对-A1三比例.jpg"
open "$O/核对-A1三比例.jpg"
