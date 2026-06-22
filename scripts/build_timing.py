#!/usr/bin/env python3
"""
Đo thời lượng 26 chunks, gộp theo 5 cảnh, rồi inject cả timing lẫn
product metadata (từ narrations/<PRODUCT_NAME>/meta.json) vào index.html.
"""
import json, os, subprocess, sys

SCENE_CHUNK_COUNTS = [7, 2, 8, 5, 4]  # tổng = 26
TOTAL_CHUNKS = sum(SCENE_CHUNK_COUNTS)

# ── Đọc metadata sản phẩm ────────────────────────────────────────────────────
PRODUCT_NAME = os.environ.get("PRODUCT_NAME", "")
meta_path = f"narrations/{PRODUCT_NAME}/meta.json" if PRODUCT_NAME else ""

DEFAULT_META = {
    "product_name": "Product Review",
    "product_sub":  "Path of the Heart",
    "chips":        ["See Description", "Amazon Pick", "Faith-Based"],
    "liked": [
        {"title": "Feature 1", "sub": "Why it matters"},
        {"title": "Feature 2", "sub": "Why it matters"},
        {"title": "Feature 3", "sub": "Why it matters"},
    ],
    "caveat_body": "Check the listing for full details before purchasing.",
    "caveat_sub":  "Link in description below",
}

if meta_path and os.path.exists(meta_path):
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    print(f"Loaded meta: {meta_path}")
else:
    meta = DEFAULT_META
    print(f"No meta.json found for '{PRODUCT_NAME}' — using defaults.")

# ── Đo thời lượng audio ──────────────────────────────────────────────────────
def ffprobe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "json", path],
        capture_output=True, text=True, check=True)
    return float(json.loads(out.stdout)["format"]["duration"])

audio_files = [f"voice-{i:02d}.wav" for i in range(1, TOTAL_CHUNKS + 1)]
chunk_durations = [ffprobe_duration(p) for p in audio_files]

print(f"\nChunk durations:")
for i, d in enumerate(chunk_durations, 1):
    print(f"  voice-{i:02d}.wav → {d:.2f}s")

scene_durations = []
idx = 0
for count in SCENE_CHUNK_COUNTS:
    scene_durations.append(sum(chunk_durations[idx:idx+count]))
    idx += count

total = sum(scene_durations)
print(f"\nScene durations: {[f'{d:.2f}s' for d in scene_durations]}")
print(f"TOTAL: {total:.2f}s")

# ── Đọc, inject, ghi index.html ──────────────────────────────────────────────
with open("index.html", encoding="utf-8") as f:
    html = f.read()

# Inject timing
for i, d in enumerate(scene_durations, 1):
    html = html.replace(f"__D{i}__", f"{d:.3f}")
html = html.replace("__TOTAL__", f"{total:.3f}")

# Inject product metadata
chips = meta.get("chips", DEFAULT_META["chips"])
liked = meta.get("liked", DEFAULT_META["liked"])

replacements = {
    "__PNAME__":       meta.get("product_name", DEFAULT_META["product_name"]),
    "__PSUB__":        meta.get("product_sub",  DEFAULT_META["product_sub"]),
    "__CHIP1__":       chips[0] if len(chips) > 0 else "",
    "__CHIP2__":       chips[1] if len(chips) > 1 else "",
    "__CHIP3__":       chips[2] if len(chips) > 2 else "",
    "__LIKED1_TITLE__": liked[0]["title"] if len(liked) > 0 else "",
    "__LIKED1_SUB__":   liked[0]["sub"]   if len(liked) > 0 else "",
    "__LIKED2_TITLE__": liked[1]["title"] if len(liked) > 1 else "",
    "__LIKED2_SUB__":   liked[1]["sub"]   if len(liked) > 1 else "",
    "__LIKED3_TITLE__": liked[2]["title"] if len(liked) > 2 else "",
    "__LIKED3_SUB__":   liked[2]["sub"]   if len(liked) > 2 else "",
    "__CAVEAT_BODY__":  meta.get("caveat_body", DEFAULT_META["caveat_body"]),
    "__CAVEAT_SUB__":   meta.get("caveat_sub",  DEFAULT_META["caveat_sub"]),
}

for token, value in replacements.items():
    if token not in html:
        print(f"WARNING: token {token} not found in index.html", file=sys.stderr)
    html = html.replace(token, value)

# Kiểm tra không còn placeholder nào sót
remaining = [t for t in list(replacements.keys()) + [f"__D{i}__" for i in range(1,6)] + ["__TOTAL__"]
             if t in html]
if remaining:
    print(f"ERROR: Unresolved placeholders: {remaining}", file=sys.stderr)
    sys.exit(1)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"\nindex.html updated — product: {meta.get('product_name')}")
