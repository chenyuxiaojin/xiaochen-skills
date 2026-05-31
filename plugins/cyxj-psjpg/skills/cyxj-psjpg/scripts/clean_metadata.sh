#!/bin/bash
# clean_metadata.sh
# 把真 PS 导出的 JPG 的 XMP History 改写成干净的 created -> saved 两步，
# 删除 PS Save As 时留下的 "from image/png to image/jpeg" 转换痕迹（含 converted 动作），
# 让产物看起来像 PS 里原生做好直接导出，不暴露 png 来源。
# 保留每张图自身真实的 CreateDate / ModifyDate / instanceID，时间线自洽。
# softwareAgent 从图片自身的 IFD0:Software 动态读取（即真实 PS 版本），避免写死版本号。
#
# 用法:
#   clean_metadata.sh <目录>              # 清理目录下所有 .jpg
#   clean_metadata.sh a.jpg b.jpg ...     # 清理指定文件
#
# 依赖: exiftool（brew install exiftool）
# 兼容 macOS 自带 bash 3.2

set -euo pipefail

# 读不到真实版本时的兜底
SA_FALLBACK="Adobe Photoshop (Macintosh)"

if ! command -v exiftool >/dev/null 2>&1; then
  echo "错误：未找到 exiftool（brew install exiftool）" >&2
  exit 1
fi

lc() { tr 'A-Z' 'a-z'; }

clean_one() {
  local f="$1"
  local CD MD IID2 ODID IID1 SA

  CD=$(exiftool -s3 -XMP-xmp:CreateDate "$f" 2>/dev/null || true)
  MD=$(exiftool -s3 -XMP-xmp:ModifyDate "$f" 2>/dev/null || true)
  IID2=$(exiftool -s3 -XMP-xmpMM:InstanceID "$f" 2>/dev/null || true)
  ODID=$(exiftool -s3 -XMP-xmpMM:OriginalDocumentID "$f" 2>/dev/null || true)
  # 真实 PS 版本（如 "Adobe Photoshop 27.7 (Macintosh)"），动态读取避免写死
  SA=$(exiftool -s3 -IFD0:Software "$f" 2>/dev/null || true)
  [ -z "$SA" ] && SA="$SA_FALLBACK"

  # 兜底：字段缺失时生成/回退，保证写入合法
  [ -z "$CD" ] && CD="$MD"
  [ -z "$MD" ] && MD="$CD"
  [ -z "$IID2" ] && IID2="xmp.iid:$(uuidgen | lc)"
  if [ -n "$ODID" ]; then
    IID1="xmp.iid:${ODID#xmp.did:}"
  else
    IID1="xmp.iid:$(uuidgen | lc)"
  fi

  # 第一步：彻底删除整个 History（清空必须单独成一条命令，否则会被追加）
  exiftool -overwrite_original "-XMP-xmpMM:History=" "$f" >/dev/null
  # 第二步：写入干净的 created -> saved
  exiftool -overwrite_original \
    "-XMP-xmpMM:History+={action=created, when=$CD, softwareAgent=$SA, instanceID=$IID1}" \
    "-XMP-xmpMM:History+={action=saved, when=$MD, softwareAgent=$SA, instanceID=$IID2, changed=/}" \
    "$f" >/dev/null

  echo "已清理: $f"
}

if [ "$#" -eq 0 ]; then
  echo "用法: $0 <目录 | a.jpg b.jpg ...>" >&2
  exit 1
fi

count=0
for arg in "$@"; do
  if [ -d "$arg" ]; then
    while IFS= read -r -d '' j; do
      clean_one "$j"; count=$((count+1))
    done < <(find "$arg" -maxdepth 1 -type f -iname '*.jpg' -print0)
  elif [ -f "$arg" ]; then
    clean_one "$arg"; count=$((count+1))
  else
    echo "跳过（不存在）: $arg" >&2
  fi
done
echo "完成，共清理 $count 张。"
