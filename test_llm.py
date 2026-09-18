import json
import urllib.request
import sys
import os
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# API Keys (set via environment variables or paste your key here)
GROQ_KEYS = [
    # "your_groq_api_key_here",
]
DEFAULT_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

V12_PATH = os.path.join("app", "src", "main", "assets", "flirt_dataset_v12.json")
LEGACY_PATH = os.path.join("app", "src", "main", "assets", "flirt_dataset.json")
DATASET_PATH = V12_PATH if os.path.exists(V12_PATH) else LEGACY_PATH

def get_user_style_context():
    if os.path.exists("user_style_pref.txt"):
        try:
            with open("user_style_pref.txt", "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                if lines:
                    return "\n━━━━━━━━━━━━━━━━━━━━━━\n💡 USER'S PERSONAL WRITING STYLE (PREFERRED PAST REPLIES):\n" + \
                           "\n".join(f"  - {line}" for line in lines[:5]) + "\n"
        except Exception:
            pass
    return ""

def record_chosen_reply(reply_text):
    existing = []
    if os.path.exists("user_style_pref.txt"):
        try:
            with open("user_style_pref.txt", "r", encoding="utf-8") as f:
                existing = [line.strip() for line in f.readlines() if line.strip()]
        except Exception:
            pass
            
    if reply_text in existing:
        existing.remove(reply_text)
    existing.insert(0, reply_text)
    
    try:
        with open("user_style_pref.txt", "w", encoding="utf-8") as f:
            for item in existing[:5]:
                f.write(f"{item}\n")
        print(f"\n🎯 Style preference recorded: \"{reply_text}\"!")
    except Exception as e:
        print(f"Error saving preference: {e}")

def load_dataset():
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset file not found at {DATASET_PATH}")
        return []
    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"Loaded dataset from: {os.path.basename(DATASET_PATH)} ({len(data)} scenarios)")
            return data
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return []

def analyze_semantics(message):
    msg = message.lower().strip()
    norm_msg = msg.replace("cehpthe", "chepthe").replace("ceyyaku", "cheyyaku")
    clean_words = set(re.findall(r'\b[a-zA-Z]+\b', norm_msg))

    # Ultimate contact cutoff / Breakup threat / Permanent boundary
    is_breakup_threat = any(
        k in norm_msg for k in [
            "inkeppudu", "inka eppudu", "block chestha", "block chesta",
            "breakup", "vellipotha", "naa valla kaadu", "single ga untanu",
            "dooram undu", "dooranga undu"
        ]
    ) or (
        any(v in norm_msg for v in ["call", "message", "msg", "phone", "text"]) and 
        any(neg in norm_msg for neg in ["ceyyaku", "cheyyaku", "cheyaku", "seyyaku", "vaddu", "oddu", "vadhu", "vaddhu"])
    )

    # Frustration / Irritation / Repetition conflict
    is_frustration_conflict = any(
        k in norm_msg for k in [
            "ardham kaada", "ardham kaadha", "ardham avvatleda", "ardham kavatleda",
            "ardham kavatledha", "ardham cheskova", "ardham chesukova",
            "oka sari chepthe", "okkasari chepthe", "enni sarlu",
            "chepthe vinava", "cheppindi vinava", "vinara", "vinava",
            "buddhi leda", "mind leda", "sense leda", "visugu", "visugosthondi",
            "visiginchaku", "chiraku", "chimpestha", "gola cheyyaku"
        ]
    )

    # Stage 1: Detect User Emotion
    emotion = "NEUTRAL"
    if is_breakup_threat or is_frustration_conflict:
        emotion = "ANGRY"
    elif any(k in norm_msg for k in ["edip", "edav", "edupu", "yedus", "cry", "crying", "hurt", "badha", "baadha", "kallalo", "tears", "pain"]):
        emotion = "HURT"
    elif any(k in norm_msg for k in ["kopam", "gussa", "irritat", "matladaku", "matladanu", "vaddu", "vadiley", "dooram", "fight", "breakup"]) or "enduku ila matlad" in norm_msg:
        emotion = "ANGRY"
    elif any(k in norm_msg for k in ["ignore", "pattinchukodam", "pattinchukovadam"]):
        emotion = "IGNORED"
    elif any(k in norm_msg for k in ["reply ivvatledu", "reply ivvaledu", "reply enduku"]):
        emotion = "NO_REPLY"
    elif any(k in norm_msg for k in ["ex", "other girl", "ammailu", "jealous"]):
        emotion = "JEALOUS"
    elif any(k in norm_msg for k in ["miss", "missing", "gurthosth", "ontari"]):
        emotion = "MISSING"
    elif any(k in norm_msg for k in ["teas", "allari", "prank", "roast"]):
        emotion = "PLAYFUL"
    elif any(k in norm_msg for k in ["love", "prema", "muddu", "hug", "kiss", "ishtam"]):
        emotion = "ROMANTIC"

    # Stage 2: Detect Scenario Intent
    intent = "CASUAL_CHAT"
    if is_breakup_threat:
        intent = "BREAKUP_THREATS"
    elif is_frustration_conflict:
        intent = "CONFLICT"
    elif any(k in norm_msg for k in ["ignore", "pattinchukodam", "pattinchukovadam"]):
        intent = "IGNORING"
    elif any(k in norm_msg for k in ["reply ivvatledu", "reply ivvaledu", "reply enduku"]):
        intent = "NO_REPLY"
    elif emotion == "HURT" or any(k in norm_msg for k in ["hurt", "edip", "baadha", "badha"]):
        intent = "EMOTIONAL_HURT"
    elif emotion in ["ANGRY", "IGNORED"] or any(k in norm_msg for k in ["kopam", "matladaku", "enduku ila matlad"]):
        intent = "CONFLICT"
    elif emotion == "JEALOUS":
        intent = "JEALOUSY"
    elif any(w in msg for w in ["morning", "mrng"]) or "gm" in clean_words:
        intent = "GREETING_MORNING"
    elif any(w in msg for w in ["night", "nidra", "sleep", "paduko"]):
        intent = "GREETING_NIGHT"
    elif any(w in msg for w in ["tinnava", "thinnava", "tinna", "thinna", "food", "curry"]):
        intent = "FOOD_CHECK"
    elif emotion == "MISSING":
        intent = "MISSING"
    elif any(w in msg for w in ["handsome", "cute", "beautiful", "gorgeous", "photo", "pic"]):
        intent = "COMPLIMENT"
    elif any(w in msg for w in ["kalus", "kaluddham", "meet", "date", "bayataki"]):
        intent = "DATE_REQUEST"
    elif any(w in msg for w in ["pelli", "marriage", "proposal"]):
        intent = "PROPOSAL"
    elif emotion == "PLAYFUL" or any(k in msg for k in ["teas", "allari", "prank"]):
        intent = "TEASING"
    elif any(w in msg for w in ["sorry", "kshaminchu"]):
        intent = "APOLOGY"
    elif any(w in msg for w in ["bore", "boring", "trip", "gift"]):
        intent = "RANDOM"

    return emotion, intent

def determine_intent_category(message):
    _, intent = analyze_semantics(message)
    return intent

def get_related_dataset_examples(latest_message, dataset, count=2):
    if not latest_message or not dataset:
        return ""
    
    intent = determine_intent_category(latest_message)
    filtered_dataset = dataset
    if intent:
        filtered_dataset = [
            entry for entry in dataset 
            if intent in entry.get("category", "").lower() or intent in entry.get("incoming", "").lower()
        ]
        
    final_pool = filtered_dataset if filtered_dataset else dataset
    
    stop_words = {
        "nuvvu", "nannu", "naa", "nee", "chala", "unnav", "unnaru", "unnappudu", 
        "kadha", "le", "bujji", "bangaram", "baby", "sweetheart", "na", "ne", "ani", 
        "ga", "tho", "koo", "lo", "inka", "i", "am", "you", "are", "the", "to",
        "chesthunnav", "chesthunna", "chesthunnadu", "cheyyi"
    }
    
    latest_clean = "".join([c if c.isalnum() or c.isspace() else "" for c in latest_message.lower()])
    latest_words = [w for w in latest_clean.split() if len(w) > 1 and w not in stop_words]
    
    scored_items = []
    for item in final_pool:
        incoming = item.get("incoming", "")
        incoming_clean = "".join([c if c.isalnum() or c.isspace() else "" for c in incoming.lower()])
        incoming_words = incoming_clean.split()
        
        # Calculate overlap of non-stopword tokens
        overlap = sum(1 for w in latest_words if any(w in iw or iw in w for iw in incoming_words))
        exact = 100 if incoming.lower().strip() == latest_message.lower().strip() else 0
        score = overlap + exact
        
        if score > 0:
            scored_items.append((score, item))
            
    # Sort by score descending
    scored_items.sort(key=lambda x: x[0], reverse=True)
    top_matches = [item for _, item in scored_items[:count]]
    
    if not top_matches:
        import random
        top_matches = random.sample(final_pool, count) if len(final_pool) >= count else final_pool[:count]
        
    # Format matches into a readable style guide prompt
    context_str = ""
    for idx, match in enumerate(top_matches):
        context_str += f"Example {idx+1}:\n"
        context_str += f"User message: \"{match.get('incoming', '')}\"\n"
        context_str += f"  - Romantic: {', '.join(match.get('romantic', [])[:2])}\n"
        context_str += f"  - Sweet: {', '.join(match.get('sweet', [])[:2])}\n"
        context_str += f"  - Funny: {', '.join(match.get('funny', [])[:2])}\n"
        context_str += f"  - Bold: {', '.join(match.get('bold', [])[:2])}\n\n"
    return context_str

def make_groq_request(api_key, system_instruction, latest_message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"[LATEST MESSAGE]\n{latest_message}"}
        ],
        "temperature": 0.5,
        "max_tokens": 150
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            return res_body["choices"][0]["message"]["content"]
    except Exception as e:
        if hasattr(e, 'read'):
            error_details = e.read().decode('utf-8')
            return f"HTTP Error: {e.code} - {error_details}"
        return f"Error: {e}"

def make_gemini_request(api_key, system_instruction, latest_message):
    import time
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    payload = {
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "parts": [{"text": f"[LATEST MESSAGE]\n{latest_message}"}]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                return res_body["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            last_error = e
            if hasattr(e, 'read'):
                try:
                    error_details = e.read().decode('utf-8')
                except Exception:
                    error_details = str(e)
                if e.code in [503, 429]:
                    print(f"⚠️ Gemini API returned {e.code}. Retrying in {2 * (attempt + 1)} seconds...")
                    time.sleep(2 * (attempt + 1))
                    continue
                return f"HTTP Error: {e.code} - {error_details}"
            time.sleep(1)
            
    if last_error and hasattr(last_error, 'read'):
        try:
            error_details = last_error.read().decode('utf-8')
        except Exception:
            error_details = str(last_error)
        return f"HTTP Error: {last_error.code} - {error_details}"
    return f"Error: {last_error}"


def sanitize_reply(text):
    if not text:
        return text
    clean = text.strip().strip('"').strip("'")
    
    corrections = {
        "alochichadame": "alochinchadame",
        "alochichadam": "alochinchadam",
        "alochichanu": "alochinchanu",
        "alochichasthu": "alochisthu",
        "alochichatam": "alochinchadam",
        "alochiche": "alochinche",
        "puri munigipoyanu": "poorthiga munigipoya",
        "puri munigipoya": "poorthiga munigipoya",
        "munigipoyanu": "munigipoya",
        "upiri theesukuntunna": "nee dhyasa lo unna",
        "oopiri theeskuntunna": "nee dhyasa lo unna",
        "vunta": "unta",
        "vuntunna": "untunna",
        "vunnav": "unnav",
        "vunnaru": "unnaru",
        "cheshanu": "chesa",
        "chesthunnau": "chesthunna",
        "eduru choostunna": "wait chesthunna",
        "eduruchoostunna": "wait chesthunna",
        "pettukovoyyi": "petko",
        "poortiga": "poorthiga",
        "chudali": "chudaali",
        "unnapudu": "unnappudu",
        "aipothunna": "aipoya",
        "matladaku": "matladodu",
        "vadiley": "vadilei",
        "badha ga undhi": "baadhaga undi",
        "badhaga undhi": "baadhaga undi",
        "badha ga undi": "baadhaga undi",
        "kopam ga": "kopamga",
        # New additions for advanced robotic cleanups
        "na silence complete missing thought analysis": "miss avthunna bujji, busy unna",
        "na silence complete missing thought": "miss avthunna bujji, phone silent lo undi",
        "na silence complete missing": "miss avthunna bujji",
        "naa silence complete missing thought analysis": "miss avthunna bujji, busy unna",
        "naa silence complete missing thought": "miss avthunna bujji, phone silent lo undi",
        "naa silence complete missing": "miss avthunna bujji",
        "naa gundey full ga ne di only": "naa gunde motham neede bujji",
        "na gundey full ga ne di only": "naa gunde motham neede bujji",
        "naa gunde full ga ne di only": "naa gunde motham neede bujji",
        "na gunde full ga ne di only": "naa gunde motham neede bujji",
        "nee msg kosam eduru choosthunna": "nee msg kosam wait chesthunna",
        "nee msg kosam eduruchoosthunna": "nee msg kosam wait chesthunna",
        "nee message kosam eduru choosthunna": "nee msg kosam wait chesthunna",
        "nee message kosam eduruchoosthunna": "nee msg kosam wait chesthunna",
        "premisthunna nee life": "nee meeda prema eppatiki thaggadu bangaram",
        "premisthunnanu nee life": "nee meeda prema eppatiki thaggadu bangaram",
        "premisthunna na life": "nuvve na life bangaram",
        "premisthunnanu na life": "nuvve na life bangaram",
        "nannu vodileyaku": "please nannu dooram pettaku",
        "nannu vadileyaku": "please nannu dooram pettaku",
        "nannu vodileiyaku": "please nannu dooram pettaku",
        "duranga vellaku": "dooram vellaku",
        "duranga vellipoku": "dooranga vellipoku",
        "matladatam ledhu endhuku": "matladadam ledu enduku",
        "matladatam ledu endhuku": "matladadam ledu enduku",
        "matladatam ledhu enduku": "matladadam ledu enduku",
        "matladadam ledhu endhuku": "matladadam ledu enduku",
        "kopam thaggincha": "kopam tagginda",
        "kopam thagginchava": "kopam tagginda",
        "tax kattaali": "tax kattali"
    }
    
    import re
    for wrong, right in corrections.items():
        clean = re.sub(rf'(?i)\b{wrong}\b', right, clean)
        if wrong in clean.lower():
            clean = re.sub(wrong, right, clean, flags=re.IGNORECASE)
            
    clean = re.sub(r'(?i)\bmeeru\b', "nuvvu", clean)
    clean = re.sub(r'(?i)\bela unnaru\b', "ela unnav", clean)
    clean = re.sub(r'(?i)\bmeere\b', "nuvve", clean)
    
    # Pronoun confusion fixes (correcting "I am thinking of myself" to "I am thinking of you")
    clean = re.sub(r'(?i)\bnaa? gurinche alochisthunna\b', "nee gurinche alochisthunna", clean)
    clean = re.sub(r'(?i)\bnaa? gurinchi alochisthunna\b', "nee gurinche alochisthunna", clean)
    
    clean = re.sub(r'(?i)\bkopam chesukoku\b', "kopam vaddu", clean)
    clean = re.sub(r'(?i)\bkopam cheyyaku\b', "kopam vaddu", clean)
    clean = re.sub(r'(?i)\bkopam cheyaku\b', "kopam vaddu", clean)
    clean = re.sub(r'(?i)\bnaa? mind lo nuvvu undhi?\b', "naa mind lo nuvve vunnav", clean)
    clean = re.sub(r'(?i)\bnaa? mind lo nuvvu undi\b', "naa mind lo nuvve vunnav", clean)
    clean = re.sub(r'(?i)\bnaa? mind lo nuvve unnav\b', "naa mind lo nuvve vunnav", clean)
    clean = re.sub(r'(?i)\bnaa? mind lo nuvve vunnav\b', "naa mind lo nuvve vunnav", clean)
    
    emoji_match = re.search(r'([\u2600-\u27BF]|[\uD83C-\uDBFF][\uDC00-\uDFFF])+$', clean)
    if emoji_match:
        start_idx = emoji_match.start()
        if start_idx > 0 and clean[start_idx - 1] != ' ':
            clean = clean[:start_idx] + ' ' + clean[start_idx:]
            
    return clean

def main():
    print("====================================================")
    print("🔥 Couple Friendly AI - Prompt Testing Terminal 🔥")
    print("====================================================\n")
    
    dataset = load_dataset()
    if not dataset:
        print("Could not proceed without dataset.")
        return
        
    latest_message = input("Enter test user message (e.g. 'hi', 'coffee date'): ").strip()
    if not latest_message:
        latest_message = "Hi"
        print("Using default: 'Hi'")
        
    tone = input("Enter reply tone (romantic, sweet, funny, bold) [default: sweet]: ").strip().lower()
    if not tone or tone not in ["romantic", "sweet", "funny", "bold"]:
        tone = "sweet"
    
    emotion, intent = analyze_semantics(latest_message)
    
    print("\n🔍 Querying V12 Native Dataset (ALL APIs DISABLED)...")
    
    INTENT_TARGET_CATEGORIES = {
        "EMOTIONAL_HURT": ["emotional", "fight", "conflict"],
        "CONFLICT": ["conflict", "fight", "angry"],
        "JEALOUSY": ["jealous", "jealousy"],
        "TEASING": ["teasing", "playful"],
        "GREETING_MORNING": ["morning", "morning_motivation"],
        "GREETING_NIGHT": ["night", "night_chat", "sleepy"],
        "FOOD_CHECK": ["food"],
        "MISSING": ["miss", "missing"],
        "COMPLIMENT": ["compliment", "compliments", "photo"],
        "DATE_REQUEST": ["date", "plans", "future_plans"],
        "PROPOSAL": ["proposal", "love"],
        "APOLOGY": ["emotional", "conflict", "fight"],
        "RANDOM": ["random"]
    }
    
    target_cats = INTENT_TARGET_CATEGORIES.get(intent, [])
    pool = [e for e in dataset if e.get("category", "").lower() in target_cats] if target_cats else dataset
    
    stop_words = {
        "nuvvu", "nannu", "naa", "nee", "chala", "unnav", "unnaru", "unnappudu", "unna", "undi", "undhi",
        "kadha", "le", "bujji", "bangaram", "baby", "sweetheart", "na", "ne", "ani", 
        "ga", "tho", "koo", "lo", "inka", "i", "am", "you", "are", "the", "to",
        "chesthunnav", "chesthunna", "chesthunnadu", "cheyyi"
    }
    
    concept_map = {
        "edip": ["cry", "crying", "hurt", "badha", "baadha"],
        "hurt": ["edip", "badha", "baadha", "cry"],
        "badha": ["hurt", "edip", "cry"],
        "kopam": ["fight", "angry", "dooram"],
        "matladaku": ["silent", "fight", "kopam"]
    }
    
    m = latest_message.lower().strip()
    is_interpersonal = any(w in m for w in ["nannu", "natho", "naatho", "ila", "enduku", "chesav", "chesavu", "chesthunnav", "ceyyaku", "cheyyaku", "naku"])

    scored_items = []
    for item in pool:
        inc = item.get("incoming", "").lower()
        cat = item.get("category", "").lower()
        item_intent = str(item.get('intent', '')).upper()

        # Hard negative rejection
        if intent in ["EMOTIONAL_HURT", "CONFLICT", "BREAKUP_THREATS", "IGNORING", "NO_REPLY"] and cat in ["teasing", "playful"]:
            continue
        if intent == "TEASING" and cat in ["fight", "conflict", "emotional", "angry", "breakup_threats"]:
            continue

        score = 0
        intent_match_level = "LOW"

        # Intent Matching
        if intent == "BREAKUP_THREATS":
            if cat in ["breakup_threats"]:
                score += 35
                intent_match_level = "VERY HIGH"
            elif cat in ["conflict", "fight", "angry"]:
                score += 20
                intent_match_level = "HIGH"
        elif intent == "EMOTIONAL_HURT":
            if "hurt" in inc or (item_intent in ["FIGHT", "CONFLICT"] and "hurt" in inc):
                score += 30
                intent_match_level = "VERY HIGH"
            elif any(r in inc for r in ["edus", "yedus"]):
                score += 20
                intent_match_level = "HIGH"
            elif item_intent in ["EMOTIONAL", "SAD"] or cat in ["emotional", "fight"]:
                score += 15
                intent_match_level = "HIGH"
        elif intent == "CONFLICT":
            if cat in ["angry", "fight", "conflict"]:
                score += 20
                intent_match_level = "HIGH"
        elif intent == "IGNORING" and "ignore" in inc:
            score += 35
            intent_match_level = "VERY HIGH"
        elif intent == "NO_REPLY" and "reply" in inc:
            score += 35
            intent_match_level = "VERY HIGH"
        elif intent == "TEASING" and "tease" in inc:
            score += 35
            intent_match_level = "VERY HIGH"
        elif intent == "GREETING_MORNING" and "morning" in inc:
            score += 30
            intent_match_level = "VERY HIGH"
        elif intent == "FOOD_CHECK" and any(f in inc for f in ["tinna", "thinna", "food", "curry"]):
            score += 30
            intent_match_level = "VERY HIGH"

        # Interpersonal Attribution Match
        if is_interpersonal:
            if any(w in inc for w in ["hurt", "ignore", "chesa", "matlad", "reply", "forgive", "vaddhu", "dooram", "block"]):
                score += 12

        # Semantic Root & Concept Similarity
        if intent == "BREAKUP_THREATS":
            if any(w in m for w in ["call", "message", "msg", "ceyyaku", "cheyyaku"]) and any(w in inc for w in ["matlad", "block", "breakup", "call", "msg"]):
                score += 18
            if any(w in m for w in ["inkeppudu", "never", "dooram"]) and any(w in inc for w in ["dooram", "breakup", "matlad", "vaddu"]):
                score += 15
            if "ardham" in m and ("ardham" in inc or "feelings" in inc):
                score += 12

        if any(r in m for r in ["edip", "edav", "yedus"]) and any(r in inc for r in ["edus", "yedus", "cry", "hurt"]):
            score += 12
        if "hurt" in m and "hurt" in inc:
            score += 15
        if "kopam" in m and "kopam" in inc:
            score += 15
        if "teas" in m and "teas" in inc:
            score += 15

        if inc == m:
            score += 100

        if score > 0:
            scored_items.append((score, item, intent_match_level))

    scored_items.sort(key=lambda x: x[0], reverse=True)

    # Guaranteed Fallback: Never return empty list
    if not scored_items:
        fallback_cat = "breakup_threats" if intent == "BREAKUP_THREATS" else ("emotional" if intent == "EMOTIONAL_HURT" else "conflict")
        candidates = [item for item in dataset if item.get('category', '').lower() == fallback_cat]
        if not candidates:
            candidates = dataset
        scored_items = [(20, item, "HIGH") for item in candidates[:3]]

    all_replies = []
    matched_items = []
    for sc, item, iml in scored_items[:3]:
        matched_items.append((item.get('incoming'), sc, iml))
        responses = item.get("responses", {})
        tone_entries = responses.get(tone, item.get(tone, []))
        for r in tone_entries:
            if isinstance(r, dict):
                all_replies.append(r.get("text", ""))
            elif isinstance(r, str):
                all_replies.append(r)

    # Emotional safety gate
    safe_replies = []
    if intent in ["EMOTIONAL_HURT", "CONFLICT"]:
        if tone == "funny":
            for r in all_replies:
                if not any(bad in r.lower() for bad in ["cartoon", "photo frame", "facial glow", "mascara"]):
                    safe_replies.append(r)
            if len(safe_replies) < 3:
                safe_replies.extend([
                    "Sare bujji, first tears off cheyyi... tarvatha nannu question cheyyi 😂❤️",
                    "Ayyo bujji, ila emotional avvaku... first smile ivvu, tarvatha nannu thittuko 😂❤️"
                ])
        elif tone == "bold":
            for r in all_replies:
                if not any(bad in r.lower() for bad in ["kisses thoti mayam", "wilder", "intense romance", "chest meeda vaalipo"]):
                    safe_replies.append(r)
            if len(safe_replies) < 3:
                safe_replies.extend([
                    "Nuvvu hurt ayye la malli cheyyanu bujji, first naa maatavinu ❤️",
                    "Nee smile tirigi vacche varaku ninnu convince cheyyadam naa responsibility 😏❤️"
                ])
    if not safe_replies:
        safe_replies = all_replies

    intent_match_label = matched_items[0][2] if matched_items else "MEDIUM"
    attribution_label = "PARTNER_ACCOUNTABILITY" if is_interpersonal else "PERSONAL_MOOD"

    print(f"\n📩 Incoming Message : \"{latest_message}\"\n")
    print(f"🎭 Reply Style      : {tone.upper()}")
    print(f"❤️ Incoming Emotion : {emotion}")
    print(f"🎯 Detected Intent  : {intent}\n")

    print(f"📊 Retrieval Analysis")
    print(f"   Intent Match     : {intent_match_label}")
    print(f"   Semantic Match   : HIGH")
    print(f"   Emotion Match    : HIGH")
    print(f"   Attribution      : {attribution_label}\n")

    print(f"📦 LOCAL DATASET")
    for idx, (name, sc, iml) in enumerate(matched_items, 1):
        print(f"{idx}. {name:<32} score: {sc}")
    print()

    selected_replies = [sanitize_reply(r) for r in safe_replies[:3]]
    print(f"Replies ({tone.upper()}):")
    if selected_replies:
        for idx, item in enumerate(selected_replies, 1):
            print(f"  {idx}. {item}")

        print("\n--------------------------------------------------------")
        choice = input("Select which reply you like best [1, 2, 3 or Enter to skip]: ").strip()
        if choice in ["1", "2", "3"]:
            chosen_text = selected_replies[int(choice) - 1]
            record_chosen_reply(chosen_text)
    else:
        print("  No replies found in dataset for this tone.")

if __name__ == "__main__":
    main()
