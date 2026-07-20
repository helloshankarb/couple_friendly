"""
test_vercel.py  — Test the deployed Vercel API endpoint
Usage: python tools/test_vercel.py

Tests https://couple-friendly-vercel.vercel.app/api/suggest
with the same request format that AiApiClient.kt sends.
"""
import json, urllib.request, urllib.error, sys, time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

VERCEL_URL = "https://couple-friendly-vercel.vercel.app/api/suggest"
APP_SECRET  = "change-me-to-random-string"   # must match Vercel APP_SECRET env var

TEST_CASES = [
    {"msg": "Hi bujji",              "tone": "sweet"},
    {"msg": "Good morning bangaram", "tone": "romantic"},
    {"msg": "Ninnu miss avthunna",   "tone": "romantic"},
    {"msg": "Nuvvu chala cute unnav","tone": "funny"},
    {"msg": "Naku bore ga undhi",    "tone": "bold"},
]

def call_vercel(message: str, tone: str) -> dict:
    payload = json.dumps({"incoming": message, "tone": tone}).encode("utf-8")
    req = urllib.request.Request(
        VERCEL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-App-Secret": APP_SECRET,
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    print("=" * 60)
    print("  Vercel API Test — Couple Friendly")
    print(f"  URL: {VERCEL_URL}")
    print("=" * 60)

    custom = input("\nEnter a custom message to test (or press Enter to run all presets): ").strip()
    custom_tone = ""
    if custom:
        custom_tone = input("Tone [romantic/sweet/funny/bold, default: sweet]: ").strip() or "sweet"
        cases = [{"msg": custom, "tone": custom_tone}]
    else:
        cases = TEST_CASES

    print()
    passed = 0
    for case in cases:
        msg, tone = case["msg"], case["tone"]
        print(f"▶ Message : \"{msg}\"")
        print(f"  Tone    : {tone}")
        t0 = time.time()
        try:
            result = call_vercel(msg, tone)
            elapsed = time.time() - t0

            # The API returns {replies: [...], engine: "...", model: "..."}
            replies  = result.get("replies", result.get("suggestions", []))
            engine   = result.get("engine", "?")
            model    = result.get("model", "?")

            print(f"  Engine  : {engine}  ({model})")
            print(f"  Time    : {elapsed:.1f}s")
            if replies:
                print("  Replies :")
                for i, r in enumerate(replies, 1):
                    print(f"    {i}. {r}")
                passed += 1
            else:
                print(f"  ⚠ No replies in response: {result}")
        except urllib.error.HTTPError as e:
            elapsed = time.time() - t0
            try:
                body = json.loads(e.read().decode("utf-8"))
                err       = body.get("error", body)
                last_err  = body.get("lastError", "")
            except Exception:
                err, last_err = str(e), ""
            print(f"  ✗ HTTP {e.code} ({elapsed:.1f}s): {err}")
            if last_err:
                print(f"  ↳ Root cause: {last_err}")
        except Exception as e:
            elapsed = time.time() - t0
            print(f"  ✗ Error ({elapsed:.1f}s): {e}")
        print()

    if len(cases) > 1:
        print(f"Results: {passed}/{len(cases)} passed")


if __name__ == "__main__":
    main()
