#!/usr/bin/env python3
"""
Đo độ dài thật của 26 file audio ngắn (đã sinh bằng `hyperframes tts`,
mỗi file là 1 câu/cụm ngắn để né giới hạn cắt-cụt-văn-bản-dài của Kokoro),
gộp lại theo 5 nhóm tương ứng 5 cảnh, rồi thay placeholder __D1__..__D5__
và __TOTAL__ trong index.html bằng số thật.
Chạy SAU bước TTS, TRƯỚC bước lint/render trong workflow.
"""
import json
import subprocess
import sys

# Số file audio thuộc mỗi cảnh, theo đúng thứ tự narration-01..26.
# Scene 1 (hook+intro+FTC) = 7, Scene 2 (gallery "A Peek Inside") = 2,
# Scene 3 (what we liked) = 8, Scene 4 (caveat) = 5, Scene 5 (CTA) = 4.
# Tổng = 26.
SCENE_CHUNK_COUNTS = [7, 2, 8, 5, 4]

TOTAL_CHUNKS = sum(SCENE_CHUNK_COUNTS)
AUDIO_FILES = [f"voice-{i:02d}.wav" for i in range(1, TOTAL_CHUNKS + 1)]
AUDIO_FILES_TXT = [f"assets/narration-{i:02d}.txt" for i in range(1, TOTAL_CHUNKS + 1)]


def ffprobe_duration(path: str) -> float:
    out = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "json",
            path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(out.stdout)
    return float(data["format"]["duration"])


def main() -> None:
    chunk_durations = [ffprobe_duration(p) for p in AUDIO_FILES]

    print("Measured chunk durations (seconds):")
    for i, d in enumerate(chunk_durations, start=1):
        words = len(open(AUDIO_FILES_TXT[i - 1], encoding="utf-8").read().split())
        sec_per_word = d / words if words else 0
        flag = "  <-- looks too short for word count" if sec_per_word < 0.15 else ""
        print(f"  voice-{i:02d}.wav -> {d:.2f}s ({words} words){flag}")

    # Gộp theo nhóm cảnh
    scene_durations = []
    idx = 0
    for count in SCENE_CHUNK_COUNTS:
        group = chunk_durations[idx: idx + count]
        scene_durations.append(sum(group))
        idx += count

    total = sum(scene_durations)

    print("\nScene durations (seconds):")
    for i, d in enumerate(scene_durations, start=1):
        print(f"  Scene {i} -> {d:.2f}s")
    print(f"  TOTAL -> {total:.2f}s")

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    for i, d in enumerate(scene_durations, start=1):
        token = f"__D{i}__"
        if token not in html:
            print(f"ERROR: token {token} not found in index.html", file=sys.stderr)
            sys.exit(1)
        html = html.replace(token, f"{d:.3f}")

    if "__TOTAL__" not in html:
        print("ERROR: token __TOTAL__ not found in index.html", file=sys.stderr)
        sys.exit(1)
    html = html.replace("__TOTAL__", f"{total:.3f}")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("\nindex.html updated with real durations.")


if __name__ == "__main__":
    main()

