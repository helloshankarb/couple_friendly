"""
test_gemini.py  — Direct Gemini API tester (bypasses Vercel)
Tests all 3 models with the exact same prompt used by suggest.js
Usage: python tools/test_gemini.py
       GEMINI_API_KEY=AIza... python tools/test_gemini.py
"""
import json, urllib.request, urllib.error, os, sys, getpass, time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
]

def build_prompt(tone, incoming):
    return f"""You are a native Telugu speaker writing WhatsApp flirt replies in TANGLISH (Telugu spoken in English alphabet). You grew up speaking Telugu, not translating it.

TONE: {tone}

HARD RULES:
1. ROMAN SCRIPT ONLY — Telugu in English letters. Never Telugu script.
2. Sound like a real Telugu person texting — NOT like a translation app.
3. 1-2 lines max. 6-12 words. Punchy, casual, WhatsApp speed.
4. Use these NATURALLY: ra, da, le, di, ga, kada, ani, enti, ayyo, naa, nee, ikkade, cheppu, chuddu, em, ela, nuvvu, nenu.
5. Max 1 emoji per reply, at the very end only.
6. Vary each reply — different structure, different slang.
7. NEVER say "I am AI". NEVER use English phrases like "my heart", "I feel", "you are".

BAD (avoid — sounds translated):
❌ "Nee maatani ardham ayyindi bujji"
❌ "Nee gunde naku telusu"

GOOD (sounds real):
✅ "Enti ra, ila cheppakunda velipoyav?"
✅ "Nuvvu ledante boring ga undi le bujji 😒"
✅ "Cheppu da, ikkade unna — miss avutunna"

OUTPUT FORMAT — exactly this, nothing else:
1. [reply]
2. [reply]
3. [reply]

Reply to: \"{incoming}\""""


def call_gemini(api_key, model, incoming, tone="romantic"):
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": build_prompt(tone, incoming)}]}],
        "generationConfig": {"maxOutputTokens": 256, "temperature": 0.85}
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        return body["candidates"][0]["content"]["parts"][0]["text"]


def parse_replies(text):
    import re
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    replies = []
    for line in lines:
        m = re.match(r'^(?:[1-3][.)]\s*|[-•]\s*)(.+)$', line)
        if m:
            replies.append(m.group(1).strip())
        if len(replies) == 3:
            break
    if len(replies) < 2:
        replies = [l for l in lines if len(l) > 5][:3]
    return replies


def main():
    print("=" * 58)
    print("   Gemini Direct API Test — Couple Friendly App")
    print("=" * 58)

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("\nEnter your Gemini API key (input hidden):")
        api_key = getpass.getpass("  Key: ").strip()
    if not api_key:
        print("No API key provided. Exiting.")
        sys.exit(1)

    incoming = input("\nTest message [default: Hi bujji]: ").strip() or "Hi bujji"
    tone = input("Tone [romantic/sweet/funny/bold, default: romantic]: ").strip() or "romantic"
    print()

    any_success = False
    for model in GEMINI_MODELS:
        print(f"  Model : {model}", flush=True)
        t0 = time.time()
        try:
            raw = call_gemini(api_key, model, incoming, tone)
            elapsed = time.time() - t0
            replies = parse_replies(raw)
            if replies:
                print(f"  Status: OK ({elapsed:.1f}s)")
                print(f"  Replies for \"{incoming}\" [{tone}]:")
                for i, r in enumerate(replies, 1):
                    print(f"    {i}. {r}")
                any_success = True
                break
            else:
                print(f"  Status: Parse failed. Raw output:")
                print(f"    {raw[:200]}")
        except urllib.error.HTTPError as e:
            elapsed = time.time() - t0
            try:
                err_json = json.loads(e.read())
                err_msg = err_json.get("error", {}).get("message", str(e))
            except Exception:
                err_msg = str(e)
            print(f"  Status: HTTP {e.code} ({elapsed:.1f}s)")
            print(f"  Error : {err_msg[:200]}")
        except Exception as e:
            print(f"  Status: Exception — {e}")
        print()

    if not any_success:
        print("\nAll models failed. Check quota at: https://ai.dev/rate-limit")
    else:
        print("\nGemini API is working correctly.")


if __name__ == "__main__":
    main()
