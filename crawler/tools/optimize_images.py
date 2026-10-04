# -*- coding: utf-8 -*-
"""
媒体图片优化脚本：MD5 去重 + Pillow 压缩

- 去重：内容完全相同的图片只保留一份，数据库 image_url 同步改指保留文件
- 压缩：等比缩放至最长边 1200px，JPEG quality=80 渐进式保存；
        无透明通道的 PNG 转为 JPG（同步更新数据库引用与文件名）
- 全程报告写入 .workbuddy/image_optimize_report.json（UTF-8）

用法（项目根目录）：
    venv/Scripts/python.exe crawler/tools/optimize_images.py
"""
import os
import sys
import io
import json
import hashlib
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
MEDIA = BASE / "travel_web" / "media" / "attractions"
REPORT = BASE / ".workbuddy" / "image_optimize_report.json"

MAX_SIDE = 1200
JPEG_QUALITY = 80
IMG_EXTS = {".jpg", ".jpeg", ".png"}

sys.path.insert(0, str(BASE / "travel_web"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travel_web.settings")

import django  # noqa: E402

django.setup()

from attractions.models import Attraction  # noqa: E402
from PIL import Image  # noqa: E402

Image.MAX_IMAGE_PIXELS = None  # 携程原图较大，关闭告警上限


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def media_url(filename: str) -> str:
    return "/media/attractions/" + filename


def update_db_refs(rename_map: dict) -> int:
    """rename_map: 旧文件名 -> 新文件名，批量更新数据库 image_url"""
    if not rename_map:
        return 0
    url_map = {media_url(k): media_url(v) for k, v in rename_map.items()}
    updated = 0
    for att in Attraction.objects.filter(image_url__in=list(url_map.keys())):
        att.image_url = url_map[att.image_url]
        att.save(update_fields=["image_url"])
        updated += 1
    return updated


def main() -> None:
    files = sorted(p for p in MEDIA.iterdir() if p.suffix.lower() in IMG_EXTS)
    size_before = sum(p.stat().st_size for p in files)
    report = {
        "files_before": len(files),
        "size_before_mb": round(size_before / 1024 / 1024, 2),
        "duplicates_removed": 0,
        "db_refs_dedup": 0,
        "png_to_jpg": 0,
        "db_refs_convert": 0,
        "compressed": 0,
        "errors": [],
    }

    # ---------- 1. MD5 去重（先改数据库引用，再删文件） ----------
    by_hash = {}
    for p in files:
        by_hash.setdefault(md5_of(p), []).append(p)

    dedup_map = {}
    for group in by_hash.values():
        if len(group) < 2:
            continue
        keep = group[0]
        for p in group[1:]:
            dedup_map[p.name] = keep.name
    report["db_refs_dedup"] = update_db_refs(dedup_map)
    for old_name in dedup_map:
        target = MEDIA / old_name
        if target.exists():
            target.unlink()
            report["duplicates_removed"] += 1

    # ---------- 2. 修复悬空引用（本地文件缺失的记录从 CSV 原始 URL 重新下载） ----------
    import pandas as pd
    import requests

    csv_path = BASE / "crawler" / "data" / "attractions_cleaned.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        origin_url = {
            (str(r["name"]).strip(), str(r["city"]).strip()): str(r["image_url"])
            for _, r in df.iterrows()
        }
    else:
        origin_url = {}

    repaired = 0
    missing = []
    for att in Attraction.objects.exclude(image_url=""):
        url = att.image_url
        if not url.startswith("/media/attractions/"):
            continue
        local = MEDIA / url.rsplit("/", 1)[-1]
        if local.exists():
            continue
        src = origin_url.get((att.name.strip(), att.city.name.strip()), "")
        if not src.startswith("http"):
            missing.append(att.name)
            continue
        try:
            resp = requests.get(src, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            if len(resp.content) < 1000:
                missing.append(att.name)
                continue
            fname = f"{att.id}_{hashlib.md5(src.encode()).hexdigest()[:8]}.jpg"
            img = Image.open(io.BytesIO(resp.content))
            img.load()
            img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
            img.convert("RGB").save(
                MEDIA / fname, "JPEG", quality=JPEG_QUALITY, optimize=True,
                progressive=True,
            )
            att.image_url = media_url(fname)
            att.save(update_fields=["image_url"])
            repaired += 1
        except Exception:
            missing.append(att.name)
    report["repaired_missing"] = repaired
    report["still_missing"] = missing

    # ---------- 3. 压缩 ----------
    convert_map = {}
    for p in sorted(MEDIA.iterdir()):
        if p.suffix.lower() not in IMG_EXTS:
            continue
        try:
            img = Image.open(p)
            img.load()
        except Exception as exc:  # 损坏图片跳过
            report["errors"].append({"file": p.name, "error": str(exc)})
            continue

        img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        has_alpha = img.mode in ("RGBA", "LA") or (
            img.mode == "P" and "transparency" in img.info
        )

        if p.suffix.lower() == ".png" and not has_alpha:
            newp = p.with_suffix(".jpg")
            img.convert("RGB").save(
                newp, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True
            )
            p.unlink()
            convert_map[p.name] = newp.name
            report["png_to_jpg"] += 1
        elif p.suffix.lower() == ".png":
            img.save(p, "PNG", optimize=True)
        else:
            img.convert("RGB").save(
                p, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True
            )
        report["compressed"] += 1

    report["db_refs_convert"] = update_db_refs(convert_map)

    remaining = [p for p in MEDIA.iterdir() if p.suffix.lower() in IMG_EXTS]
    size_after = sum(p.stat().st_size for p in remaining)
    report["files_after"] = len(remaining)
    report["size_after_mb"] = round(size_after / 1024 / 1024, 2)
    report["saved_mb"] = round((size_before - size_after) / 1024 / 1024, 2)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with io.open(REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
