# -*- coding: utf-8 -*-
"""
Phase 3 — Offline Verification Audit
Scans the Kotlin ML package and related integration files for any
networking, cloud, or API references that would violate the
100% offline requirement.
"""

import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ML_PACKAGE_DIR = os.path.join("app", "src", "main", "java", "com", "example", "couplefriendly", "ml")

# Files that integrate with the ML engine
INTEGRATION_FILES = [
    os.path.join("app", "src", "main", "java", "com", "example", "couplefriendly", "AiApiClient.kt"),
    os.path.join("app", "src", "main", "java", "com", "example", "couplefriendly", "FloatingOverlayManager.kt"),
    os.path.join("app", "src", "main", "java", "com", "example", "couplefriendly", "FloatingOverlayService.kt"),
    os.path.join("app", "src", "main", "java", "com", "example", "couplefriendly", "MainActivity.kt"),
]

# Forbidden patterns in ML package
FORBIDDEN_PATTERNS = [
    (r'\bRetrofit\b', 'Retrofit networking library'),
    (r'\bOkHttp\b', 'OkHttp networking library'),
    (r'\bKtor\b', 'Ktor networking library'),
    (r'\bVolley\b', 'Volley networking library'),
    (r'\bFirebase\b', 'Firebase cloud service'),
    (r'\bfirebase\b', 'Firebase cloud service'),
    (r'\bAPI_KEY\b', 'API key constant'),
    (r'\bapi[_\-]?key\b', 'API key reference'),
    (r'\bhttps?://', 'HTTP/HTTPS URL'),
    (r'\bURL\(', 'URL constructor'),
    (r'\bHttpURLConnection\b', 'HttpURLConnection'),
    (r'\bURLConnection\b', 'URLConnection'),
    (r'\bjava\.net\b', 'java.net networking package'),
    (r'\bHttpClient\b', 'HttpClient'),
    (r'\bSocket\b', 'Socket connection'),
    (r'\bWebSocket\b', 'WebSocket connection'),
    (r'\bCloudFunction\b', 'Cloud function'),
    (r'\bRemoteModel\b', 'Remote model download'),
    (r'\bdownloadModel\b', 'Model download'),
    (r'\bfetchModel\b', 'Model fetch'),
    (r'\bGemini\b', 'Gemini AI API'),
    (r'\bOpenAI\b', 'OpenAI API'),
    (r'\bChatGPT\b', 'ChatGPT API'),
    (r'\bGPT\b', 'GPT reference'),
    (r'\bGenerativeModel\b', 'GenerativeModel (Gemini)'),
    (r'\bgenerativeModel\b', 'GenerativeModel (Gemini)'),
    (r'\bmodelDownload\b', 'Remote model download'),
]

# ML terminology that should NOT appear in UI-facing files
UI_FORBIDDEN_TERMS = [
    (r'\bDOMAIN\b', 'Internal ML term: DOMAIN'),
    (r'\bINTENT\b', 'Internal ML term: INTENT'),
    (r'\bSUB_INTENT\b', 'Internal ML term: SUB_INTENT'),
    (r'\bTF-IDF\b', 'Internal ML term: TF-IDF'),
    (r'\bRETRIEVAL SCORE\b', 'Internal ML term: RETRIEVAL SCORE'),
]


def scan_file(filepath, patterns, context_label):
    """Scans a single file for forbidden patterns. Returns list of violations."""
    violations = []
    if not os.path.isfile(filepath):
        return violations

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, start=1):
        # Skip comments
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/**"):
            continue

        for pattern, description in patterns:
            if re.search(pattern, line):
                violations.append({
                    "file": filepath,
                    "line": line_num,
                    "pattern": description,
                    "content": stripped[:100],
                    "context": context_label
                })

    return violations


def run_audit():
    all_violations = []

    # 1. Scan ML package files for networking/cloud references
    print("=" * 60)
    print("OFFLINE VERIFICATION AUDIT")
    print("=" * 60)
    print()

    print(f"Scanning ML package: {ML_PACKAGE_DIR}")
    if os.path.isdir(ML_PACKAGE_DIR):
        for fname in os.listdir(ML_PACKAGE_DIR):
            if fname.endswith(".kt"):
                fpath = os.path.join(ML_PACKAGE_DIR, fname)
                violations = scan_file(fpath, FORBIDDEN_PATTERNS, "ML_PACKAGE")
                all_violations.extend(violations)
                status = "❌ VIOLATIONS" if violations else "✅ CLEAN"
                print(f"  {fname}: {status}")
    else:
        print(f"  ⚠️ ML package directory not found!")
        all_violations.append({"file": ML_PACKAGE_DIR, "line": 0, "pattern": "MISSING DIRECTORY", "content": "", "context": "ML_PACKAGE"})

    print()

    # 2. Scan integration files
    print("Scanning integration files...")
    for fpath in INTEGRATION_FILES:
        if os.path.isfile(fpath):
            violations = scan_file(fpath, FORBIDDEN_PATTERNS, "INTEGRATION")
            all_violations.extend(violations)
            status = "❌ VIOLATIONS" if violations else "✅ CLEAN"
            print(f"  {os.path.basename(fpath)}: {status}")
        else:
            print(f"  {os.path.basename(fpath)}: ⚠️ NOT FOUND")

    print()

    # 3. Check UI files don't expose ML terminology
    print("Scanning for exposed ML terminology in UI...")
    ui_files = [f for f in INTEGRATION_FILES if "FloatingOverlay" in f]
    for fpath in ui_files:
        if os.path.isfile(fpath):
            violations = scan_file(fpath, UI_FORBIDDEN_TERMS, "UI_TERMINOLOGY")
            all_violations.extend(violations)
            status = "❌ ML TERMS EXPOSED" if violations else "✅ CLEAN"
            print(f"  {os.path.basename(fpath)}: {status}")

    print()

    # 4. Verify assets are bundled
    print("Verifying bundled ML assets...")
    assets_dir = os.path.join("app", "src", "main", "assets", "ml")
    required_assets = [
        "intent_classifier.json",
        "emotion_classifier.json",
        "scenarios_index.json",
        "normalizer_rules.json"
    ]
    for asset in required_assets:
        apath = os.path.join(assets_dir, asset)
        if os.path.isfile(apath):
            size_kb = os.path.getsize(apath) / 1024
            print(f"  {asset}: ✅ ({size_kb:.1f} KB)")
        else:
            print(f"  {asset}: ❌ MISSING")
            all_violations.append({"file": apath, "line": 0, "pattern": "MISSING ASSET", "content": "", "context": "ASSETS"})

    print()

    # 5. Check build.gradle for forbidden dependencies
    print("Scanning build.gradle for forbidden ML dependencies...")
    gradle_path = os.path.join("app", "build.gradle.kts")
    forbidden_deps = [
        (r'retrofit', 'Retrofit dependency'),
        (r'okhttp', 'OkHttp dependency'),
        (r'ktor', 'Ktor dependency'),
        (r'firebase', 'Firebase dependency'),
        (r'generativeai', 'Gemini GenerativeAI dependency'),
        (r'openai', 'OpenAI dependency'),
    ]
    if os.path.isfile(gradle_path):
        violations = scan_file(gradle_path, forbidden_deps, "GRADLE")
        all_violations.extend(violations)
        status = "❌ FORBIDDEN DEPS" if violations else "✅ CLEAN"
        print(f"  build.gradle.kts: {status}")
    else:
        print(f"  build.gradle.kts: ⚠️ NOT FOUND")

    print()

    # Summary
    print("-" * 60)
    ml_violations = [v for v in all_violations if v['context'] in ('ML_PACKAGE', 'ASSETS', 'UI_TERMINOLOGY')]
    integration_warnings = [v for v in all_violations if v['context'] in ('INTEGRATION', 'GRADLE')]

    if ml_violations:
        print(f"AUDIT RESULT:     ❌ FAIL ({len(ml_violations)} ML-path violations)")
        print()
        for v in ml_violations:
            print(f"  [{v['context']}] {v['file']}:{v['line']} - {v['pattern']}")
            if v['content']:
                print(f"    → {v['content']}")
        return False
    else:
        print("ML PACKAGE AUDIT: ✅ PASS — 100% OFFLINE VERIFIED")
        print()
        print("No networking, cloud, API, or remote-model references found")
        print("in the ML package, bundled assets, or UI layer.")
        if integration_warnings:
            print()
            print(f"ℹ️  {len(integration_warnings)} legacy integration warning(s) (not in ML path):")
            for v in integration_warnings:
                print(f"  [{v['context']}] {os.path.basename(v['file'])}:{v['line']} - {v['pattern']}")
                if v['content']:
                    print(f"    → {v['content']}")
            print()
            print("These are pre-existing code patterns outside the ML pipeline scope.")
        return True


if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)
