#!/usr/bin/env python3
"""
generate_narration.py — Tự động viết 26 file narration cho video review Amazon
dựa trên thông tin sản phẩm thật (scrape từ trang Amazon).

Hỗ trợ 3 API (chọn qua biến môi trường AI_PROVIDER):
  claude    → Anthropic Claude  (mặc định, đặt ANTHROPIC_API_KEY)
  openai    → OpenAI ChatGPT    (đặt OPENAI_API_KEY)
  deepseek  → DeepSeek          (đặt DEEPSEEK_API_KEY, rẻ nhất ~$0.0001/video)

Cách dùng:
  python3 scripts/generate_narration.py "https://www.amazon.com/dp/B0F7FBZNMZ"

  Hoặc đặt URL làm biến môi trường:
  AMAZON_URL="https://..." python3 scripts/generate_narration.py
"""

import json
import os
import re
import sys
import urllib.request
import urllib.parse

# ─── Cấu hình ───────────────────────────────────────────────────────────────

PROVIDER    = os.environ.get("AI_PROVIDER", "claude").lower()
MAX_WORDS   = 22          # giới hạn mỗi chunk để Kokoro TTS không bị cắt
OUTPUT_DIR  = "assets"    # thư mục lưu narration-01.txt .. narration-26.txt

API_CONFIG = {
    "claude": {
        "url":     "https://api.anthropic.com/v1/messages",
        "key_env": "ANTHROPIC_API_KEY",
        "model":   "claude-haiku-4-5",
    },
    "openai": {
        "url":     "https://api.openai.com/v1/chat/completions",
        "key_env": "OPENAI_API_KEY",
        "model":   "gpt-4o-mini",
    },
    "deepseek": {
        "url":     "https://api.deepseek.com/v1/chat/completions",
        "key_env": "DEEPSEEK_API_KEY",
        "model":   "deepseek-chat",
    },
}

# ─── Lấy thông tin sản phẩm từ trang Amazon ──────────────────────────────────

def scrape_amazon(url: str) -> dict:
    """Trả về dict: title, asin, description (tất cả đều có thể rỗng nếu bị chặn)."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[scrape] Warning: {e} — dùng URL làm nguồn thông tin dự phòng.")
        html = ""

    def find(pattern):
        m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else ""

    asin = re.search(r'(?:/dp/|/product/|/gp/product/)([A-Z0-9]{10})', url)
    title = find(r'<span id="productTitle"[^>]*>(.*?)</span>')
    title = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', title))

    # Mô tả ngắn từ bullet points
    bullets = re.findall(r'<span class="a-list-item"[^>]*>(.*?)</span>', html)
    bullets_clean = [re.sub(r'<[^>]+>', '', b).strip() for b in bullets[:5]]
    description = " | ".join(b for b in bullets_clean if len(b) > 10)

    return {
        "asin":        asin.group(1) if asin else "",
        "title":       title or "this product",
        "description": description or "",
        "url":         url,
    }

# ─── Gọi AI API ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You write YouTube voiceover narration for "Path of the Heart" — a faith-based
Christian product review channel for parents, homeschool families, and Sunday school teachers.

TONE: Warm, honest, conversational. Like a trusted friend sharing a find over coffee.
Never salesy. Never preachy. Sounds like a real person, not a promotional script.

VOICE RULES (non-negotiable):
- Use contractions: it's, you'll, I'd, that's, won't, isn't
- Short sentences mixed with slightly longer ones
- Natural spoken rhythm — write to be heard, not read
- No bullet-list energy in the voice

BANNED PHRASES (never use these):
- "In today's video we're going to talk about"
- "Without further ado" / "Let's dive in"
- "Make sure to like, comment, and subscribe" as an opener
- "Comprehensive" / "game-changer" / "transformative" / "innovative"
- "I hope you found this helpful"
- Any sentence starting with "This product is designed to..."
- "Amazing" / "incredible" / "absolutely"

BANNED STRUCTURES:
- Opening with the product name before the hook
- Listing features without saying why each one matters to the viewer
- Generic CTA that sounds copy-pasted
- Every section the same length and energy"""

def build_user_prompt(product: dict) -> str:
    return f"""Write voiceover narration for a short Amazon product review video (under 3 min).
Split into EXACTLY 26 spoken chunks following the structure below.

PRODUCT INFO:
- Title: {product['title']}
- ASIN: {product['asin']}
- URL: {product['url']}
- Details: {product['description'] or '(scrape failed — infer from title only, do not invent specs)'}

5-SCENE STRUCTURE — follow this exactly:

SCENE 1 — Chunks 01–07: HOOK + WHAT IT IS + FTC DISCLOSURE
  - Chunk 01: Open on the VIEWER'S SITUATION or problem — NOT the product name.
    Example style: "If quiet time with your kids usually turns into chaos after five minutes, this one's worth a look."
  - Chunks 02–04: Introduce product naturally (name, what it is, page count or key spec, where to get it)
  - Chunks 05–07: FTC disclosure — spoken naturally within 30 seconds, not like a legal disclaimer.
    Must include: affiliate link mention, small commission, no extra cost to viewer, only share what you'd recommend.
    Split across 2–3 short chunks so it doesn't feel rushed.

SCENE 2 — Chunks 08–09: A PEEK INSIDE
  - 2 short sentences about what the interior pages look like.
  - Do NOT repeat what was already said. Focus on the visual experience of the pages.

SCENE 3 — Chunks 10–17: WHAT WE LIKED (3 points)
  - 3 specific things worth praising. For EACH point:
    → Name the feature (1 chunk)
    → Explain WHY IT MATTERS to this viewer — not just what it is (1–2 chunks)
  - Example of WRONG: "The pages are single-sided."
  - Example of RIGHT: "Every page is single-sided — so if your kid is using markers, nothing bleeds through onto the next picture."

SCENE 4 — Chunks 18–22: HONEST CAVEAT
  - One real limitation or who this is NOT for. Never skip this — it's what makes the review trustworthy.
  - Be specific. Not "it might not be for everyone" — say exactly who it won't suit and why.

SCENE 5 — Chunks 23–26: CTA
  - Where to get it (link in description)
  - Subscribe ask — one natural line, not a demand
  - Closing line specific to THIS product, not a generic sign-off

HARD RULES:
1. EXACTLY 26 chunks total. No more, no less.
2. Each chunk ≤ {MAX_WORDS} words. Split longer thoughts across 2 chunks.
3. No em-dashes (—). Use commas or split into new chunk instead.
4. No exclamation marks.
5. Mention the real product title at least once, naturally — not robotically repeated.

Output format — JSON only, no markdown fences, no explanation before or after:
{{"chunks": ["chunk 1 text", "chunk 2 text", ..., "chunk 26 text"]}}"""


def call_api(prompt: str, product: dict) -> list[str]:
    cfg = API_CONFIG.get(PROVIDER)
    if not cfg:
        sys.exit(f"[error] Provider '{PROVIDER}' không hợp lệ. Chọn: claude, openai, deepseek")

    api_key = os.environ.get(cfg["key_env"])
    if not api_key:
        sys.exit(f"[error] Chưa đặt biến môi trường {cfg['key_env']}")

    # Build request body theo từng provider
    if PROVIDER == "claude":
        body = {
            "model": cfg["model"],
            "max_tokens": 1500,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "Content-Type":      "application/json",
            "x-api-key":         api_key,
            "anthropic-version": "2023-06-01",
        }
    else:  # openai / deepseek — cùng format OpenAI
        body = {
            "model": cfg["model"],
            "max_tokens": 1500,
            "messages": [
                {"role": "system",  "content": SYSTEM_PROMPT},
                {"role": "user",    "content": prompt},
            ],
        }
        headers = {
            "Content-Type":  "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    data = json.dumps(body).encode()
    req  = urllib.request.Request(cfg["url"], data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.load(resp)
    except urllib.error.HTTPError as e:
        body_err = e.read().decode()
        sys.exit(f"[error] API trả về {e.code}: {body_err}")

    # Trích text từ response
    if PROVIDER == "claude":
        raw = result["content"][0]["text"]
    else:
        raw = result["choices"][0]["message"]["content"]

    # Parse JSON (bỏ markdown fence nếu model thêm vào)
    raw = re.sub(r"```(?:json)?|```", "", raw).strip()
    try:
        parsed = json.loads(raw)
        chunks = parsed["chunks"]
    except Exception:
        sys.exit(f"[error] Không parse được JSON từ API:\n{raw}")

    if len(chunks) != 26:
        sys.exit(f"[error] API trả về {len(chunks)} chunks, cần đúng 26.")

    return chunks

# ─── Kiểm tra word count + cảnh báo ─────────────────────────────────────────

def validate(chunks: list[str]) -> None:
    ok = True
    for i, chunk in enumerate(chunks, start=1):
        words = len(chunk.split())
        if words > MAX_WORDS:
            print(f"  [warn] Chunk {i:02d}: {words} từ (vượt {MAX_WORDS}) — '{chunk[:60]}...'")
            ok = False
    if ok:
        print(f"  Tất cả 26 chunks đều ≤ {MAX_WORDS} từ.")

# ─── Ghi file ────────────────────────────────────────────────────────────────

def write_files(chunks: list[str]) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for i, text in enumerate(chunks, start=1):
        path = os.path.join(OUTPUT_DIR, f"narration-{i:02d}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.strip())
    print(f"  Đã ghi {len(chunks)} file vào {OUTPUT_DIR}/")

# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("AMAZON_URL", "")
    if not url:
        sys.exit("Cách dùng: python3 scripts/generate_narration.py <amazon_url>")

    print(f"[1/4] Provider: {PROVIDER.upper()}")
    print(f"[2/4] Scraping: {url}")
    product = scrape_amazon(url)
    print(f"      Title: {product['title']}")
    print(f"      ASIN:  {product['asin'] or '(không tìm được)'}")

    print(f"[3/4] Gọi {PROVIDER.upper()} API để viết 26 chunks...")
    prompt = build_user_prompt(product)
    chunks = call_api(prompt, product)

    print("[4/4] Kiểm tra + ghi file:")
    validate(chunks)
    write_files(chunks)

    print("\nXong! Chạy workflow GitHub Actions ngay bây giờ.")

if __name__ == "__main__":
    main()
