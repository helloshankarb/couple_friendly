"""
improve_dataset_gemini.py — Regenerate flirt_dataset.json replies using Gemini 2.5-flash
Gets all 4 tones in ONE call per entry to minimise API usage.
Rate-limited to 12 calls/min (safely under free-tier 15 RPM).

Usage:
    python tools/improve_dataset_gemini.py           # full run (220 entries ~18 min)
    python tools/improve_dataset_gemini.py --test    # first 5 entries only
    GEMINI_API_KEY=... python tools/improve_dataset_gemini.py

Progress is saved after every entry — safe to interrupt and resume.
"""
import json, sys, os, time, urllib.request, urllib.error, getpass, shutil, re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATASET_PATH  = "app/src/main/assets/flirt_dataset.json"
PROGRESS_PATH = "tools/improve_progress.json"
GEMINI_MODEL  = "gemini-2.5-flash"
CALLS_PER_MIN = 12   # 15 RPM limit, stay safe
SLEEP_BETWEEN = 60 / CALLS_PER_MIN   # ~5 seconds per call


PROMPT_TEMPLATE = """You are a native Telugu speaker writing WhatsApp flirt replies in TANGLISH (Telugu in English alphabet / Roman script only, never Telugu script).

Generate exactly 5 replies for EACH of the 4 tones for this incoming message.

INCOMING MESSAGE: "{incoming}"

HARD RULES:
- Roman script only — Telugu in English letters. NEVER use Telugu script (అ బ గ etc).
- Short & punchy — 1-2 lines, 6-15 words. WhatsApp speed.
- Sound like a REAL Telugu person texting, NOT a translation app.
- Use naturally: ra, da, le, di, ga, kada, ani, enti, ayyo, naa, nee, ikkade, cheppu, bujji, bangaram, baby.
- Max 1 emoji per reply at the very end only.
- Vary structure across 5 replies — don't repeat patterns.
- NEVER translate English phrases word-for-word.

BAD (translated-sounding): "Nuvvu chala beautiful ga unnavu", "Nenu nee kosam wait chestunna"
GOOD (native): "Ayyo, ila cheppakunda poyav enti", "Nuvvu ledante boring le bujji 😒"

TONE DEFINITIONS:
- romantic: warm, heartfelt, close boyfriend — poetic Tanglish
- sweet: caring, cozy, soft teasing — friendly warmth
- funny: desi Gen-Z wit — sarcasm, playful roast, light poke
- bold: confident, slightly daring — 😏 never explicit

OUTPUT — JSON only, no explanation, exactly this structure:
{{
  "romantic": ["reply1", "reply2", "reply3", "reply4", "reply5"],
  "sweet":    ["reply1", "reply2", "reply3", "reply4", "reply5"],
  "funny":    ["reply1", "reply2", "reply3", "reply4", "reply5"],
  "bold":     ["reply1", "reply2", "reply3", "reply4", "reply5"]
}}"""


def call_gemini(api_key, incoming):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={api_key}"
    auth_headers = {}
    prompt = PROMPT_TEMPLATE.format(incoming=incoming.replace('"', '\\"'))
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 1024,
            "temperature": 0.85,
            "responseMimeType": "application/json"
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **auth_headers},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read())
        raw = body["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw)


def validate_tones(result):
    """Returns True if result has all 4 tones with 5 replies each."""
    for tone in ("romantic", "sweet", "funny", "bold"):
        if tone not in result:
            return False, f"Missing tone: {tone}"
        if not isinstance(result[tone], list) or len(result[tone]) < 4:
            return False, f"Tone '{tone}' has {len(result.get(tone,[]))} replies (need ≥4)"
        for r in result[tone]:
            if not isinstance(r, str) or len(r.strip()) < 5:
                return False, f"Tone '{tone}' has an empty/too-short reply"
    return True, "ok"


def load_progress():
    if os.path.exists(PROGRESS_PATH):
        with open(PROGRESS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_progress(progress):
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def main():
    test_mode = "--test" in sys.argv
    print("=" * 60)
    print("  Gemini Dataset Improver — Couple Friendly App")
    print("  Model:", GEMINI_MODEL)
    if test_mode:
        print("  MODE: TEST (first 5 entries only)")
    print("=" * 60)

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("\nEnter your Gemini API key (input hidden):")
        api_key = getpass.getpass("  Key: ").strip()
    if not api_key:
        print("No API key provided. Exiting.")
        sys.exit(1)

    with open(DATASET_PATH, encoding="utf-8") as f:
        dataset = json.load(f)

    if test_mode:
        dataset = dataset[:5]

    # Backup original (only once)
    backup_path = DATASET_PATH + ".bak"
    if not os.path.exists(backup_path):
        shutil.copy2(DATASET_PATH, backup_path)
        print(f"\nBackup saved: {backup_path}")

    progress = load_progress()
    total = len(dataset)
    improved = 0
    skipped = 0
    failed = 0

    print(f"\nProcessing {total} entries at ~{CALLS_PER_MIN} calls/min...\n")

    for idx, entry in enumerate(dataset):
        incoming = entry["incoming"]
        key = f"{idx}:{incoming}"

        if key in progress:
            dataset[idx].update(progress[key])
            skipped += 1
            print(f"  [{idx+1}/{total}] SKIP (cached): {incoming[:40]}")
            continue

        print(f"  [{idx+1}/{total}] Processing: {incoming[:40]} ...", end=" ", flush=True)
        t0 = time.time()

        retries = 2
        result = None
        last_err = ""
        for attempt in range(retries + 1):
            try:
                result = call_gemini(api_key, incoming)
                ok, reason = validate_tones(result)
                if ok:
                    break
                else:
                    last_err = f"Validation failed: {reason}"
                    result = None
                    if attempt < retries:
                        time.sleep(3)
            except urllib.error.HTTPError as e:
                try:
                    err_json = json.loads(e.read())
                    last_err = err_json.get("error", {}).get("message", str(e))[:120]
                except Exception:
                    last_err = str(e)
                if e.code == 429:
                    wait = 30 if attempt == 0 else 60
                    print(f"\n    429 rate limit — waiting {wait}s...", end=" ", flush=True)
                    time.sleep(wait)
                elif attempt < retries:
                    time.sleep(5)
            except Exception as e:
                last_err = str(e)[:120]
                if attempt < retries:
                    time.sleep(5)

        elapsed = time.time() - t0

        if result:
            # Keep only 5 replies per tone
            for tone in ("romantic", "sweet", "funny", "bold"):
                dataset[idx][tone] = result[tone][:5]
            progress[key] = {t: result[t][:5] for t in ("romantic", "sweet", "funny", "bold")}
            save_progress(progress)
            improved += 1
            print(f"OK ({elapsed:.1f}s)")
        else:
            failed += 1
            print(f"FAILED — {last_err}")

        # Rate limiting
        if idx < total - 1:
            time.sleep(max(0, SLEEP_BETWEEN - elapsed))

    # Save improved dataset
    if not test_mode:
        with open(DATASET_PATH, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        print(f"\nDataset saved: {DATASET_PATH}")
    else:
        out_path = DATASET_PATH.replace(".json", "_test_improved.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        print(f"\nTest output saved: {out_path}")

    print(f"\nDone! improved={improved}  skipped={skipped}  failed={failed}")
    if failed > 0:
        print("Re-run the script to retry failed entries (progress is saved).")


if __name__ == "__main__":
    main()
