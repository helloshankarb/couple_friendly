import json
import urllib.request
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# API Keys (set via environment variables or paste your key here)
GROQ_KEYS = [
    # "your_groq_api_key_here",
]
DEFAULT_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")

DATASET_PATH = os.path.join("app", "src", "main", "assets", "flirt_dataset.json")

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
        print(f"\n🎯 Model trained with your preferred style: \"{reply_text}\"!")
    except Exception as e:
        print(f"Error saving preference: {e}")

def load_dataset():
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset file not found at {DATASET_PATH}")
        return []
    try:
        with open(DATASET_PATH, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return []

def determine_intent_category(message):
    import re
    msg = message.lower().strip()
    clean_words = set(re.findall(r'\b\w+\b', msg))
    
    if any(w in msg for w in ["morning", "mrng"]) or "gm" in clean_words:
        return "morning"
    if any(w in msg for w in ["night", "nidra", "sleep", "paduko", "online"]):
        return "night"
    if any(w in msg for w in ["tinnava", "thinnava", "tinna", "thinna", "food"]):
        return "tinnava"
    if any(w in msg for w in ["miss", "missing"]):
        return "missing"
    if any(w in msg for w in ["exgurinchi", "past", "jealous"]) or any(w in clean_words for w in ["ex", "ex-"]):
        return "jealousy"
    if any(w in msg for w in ["handsome", "cute", "beautiful", "gorgeous", "stunning", "photo"]) or "pic" in clean_words or "pics" in clean_words:
        return "compliment"
    if any(w in msg for w in ["love", "prema", "premisth"]):
        return "flirt"
    if any(w in msg for w in ["torture", "torcher", "fight", "kopam", "badha", "baadha", "hurt", "silent", "silence", "matladatam ledhu", "matladadam ledhu", "picha", "pichi", "venta", "padoddu", "padaku", "vaddu", "vadiley", "matladaku", "irritate", "irritat", "nachaledu", "nachavu", "nachedu", "nachala"]) or "sad" in clean_words:
        return "fight"
    if any(w in msg for w in ["care", "important", "tired", "rest"]):
        return "care"
    if any(w in msg for w in ["pelli", "marriage", "proposal"]):
        return "proposal"
    if any(w in msg for w in ["bore", "boring", "trip", "gift", "ekkadiki"]):
        return "random"
    return ""

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
        
    tone = input("Enter tone (Romantic, Sweet, Funny, Bold) [default: Romantic]: ").strip()
    if not tone:
        tone = "Romantic"
    tone = tone.capitalize()
    
    intent = determine_intent_category(latest_message)
    if intent in ["fight", "care"]:
        tone = "Comforting/Apologetic"
        print(f"\n⚠️ Sensitive message detected! Tone auto-overridden to: {tone}")
    
    print("\n[1] Groq API (Llama-3.3-70b)")
    print("[2] Gemini API (Gemini-1.5-Flash)")
    engine_choice = input("Select Engine [1 or 2]: ").strip()
    
    dataset_context = get_related_dataset_examples(latest_message, dataset)
    
    style_context = get_user_style_context()
    
    system_instruction = f"""You are an elite Telugu flirting reply generator built for WhatsApp & Instagram. You write ONLY in ROMAN SCRIPT TANGLISH — Telugu words spelled in English alphabet. NEVER use Telugu script (తెలుగు).

{style_context}

━━━━━━━━━━━━━━━━━━━━━━
💬 ROLEPLAY CONTEXT (CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━
The [LATEST MESSAGE] is sent by your girlfriend/crush to you. 
You are the boyfriend/guy replying directly to her. 
Write the reply from your perspective (the boyfriend) to her. Do not write from the perspective of a third person or friend.

━━━━━━━━━━━━━━━━━━━━━━
🎯 YOUR IDENTITY & NATIVITY MANDATE
━━━━━━━━━━━━━━━━━━━━━━
You are a charming, witty, and smooth modern Telugu guy replying to your girlfriend/crush. Every reply must be what you (the guy) would say back to her. You write like a real modern Telugu youth from Hyderabad/Vijayawada — NOT like a translation tool. 

⚠️ CRITICAL WARNING: Every single one of the 3 generated replies must be highly realistic, independent, and native modern Telugu. You are strictly forbidden from translating English words/phrases literally. Do not generate literal English-to-Telugu translations for reply 2 and reply 3. All three options must feel like they were typed by the boyfriend, not generated by an AI translation tool.

━━━━━━━━━━━━━━━━━━━━━━
📱 CORE RULES (NEVER BREAK THESE)
━━━━━━━━━━━━━━━━━━━━━━
1. ROMAN SCRIPT ONLY — Telugu words in English alphabet always.
2. SHORT & PUNCHY — Each reply is 1-2 lines max, 5-10 words. WhatsApp-style.
3. NATIVE VOCABULARY — Use these naturally:
   Terms of endearment: bangaram, bujji, sweetheart, baby, nee life, chinnadam
   Casual fillers: kadaa, avunaa, le, rey, chaaluu, enti, ayyo, appudu, alaage
   Emotion words: miss aipothunna, nee gurinchi, naa mind lo, feel avutunna
4. AVOID ROBOTIC PHRASES like:
   ❌ "nuvvu entha beautiful ga unnav"
   ❌ "nee smile na face ki vachindi"
   ❌ "meeru ela unnaru" (too formal)
   ❌ direct English-to-Telugu word-by-word translation
5. EACH OF THE 3 REPLIES MUST BE ENTIRELY DIFFERENT — vary the opening words, structure, slang, and emojis across all 3 options. Do not repeat the same words or patterns.
6. MAX 1 EMOJI per reply, placed at the end. No emoji spam.
7. NEVER reveal you are an AI or assistant.
8. ACT AS A RESPONDENT: Do not repeat or echo the girl's complaints/words back to her. Reassure her, tease her, or reply to her statement from your perspective as the boyfriend. If she says "you stopped caring", reply by telling her she's always on your mind, not by mirroring her words.
9. NATIVE WORD ORDER & GRAMMAR: Never translate English literally. For example, instead of grammatically broken/robotic phrases like "Nannu premisthunna nee life", write authentic, fluid colloquial sentences like "Nee meeda prema eppatiki thaggadu bangaram! ❤️" or "Nuvve naa prapancham baby! 🥰" or "Prati second nee gurinche naa alochana bujji! 😘". Keep it extremely natural.
10. SENSITIVE / EMOTIONAL MESSAGES: If the girl's message expresses sadness, anger, hurt, or a desire to be left alone/ignored (e.g., "naku vaddu", "please vadiley", "badha ga undhi", "kopam", "natho matladaku"):
    - NEVER generate playful, funny, bold, or flirty teasing replies.
    - Instead, automatically switch to a deeply comforting, maturely reassuring, sincere, and gentle tone.
    - Examples: "Ala anaku bangaram, nuvvu lekunda nenu undalenu. Pls matladu. ❤️" or "Kopam unna parvaledu, kani nannu duranga pettaku bujji. Pls. 😭" or "Sorry bangaram, ninnu badha pettalani ledu. Pls coordinate cheyyi. 🥰"
11. DO NOT COPY INSTRUCTIONS OR EXAMPLES: The style inspiration examples are only for grammar/tone. You are strictly prohibited from copying any example reply word-for-word. You must always create your own unique, freshly worded variations with perfect modern Telugu Tanglish spelling and premium grammar.

━━━━━━━━━━━━━━━━━━━━━━
⛔ COLLOQUIAL TANGLISH STANDARDS & BANNED TRANSLATIONS (CRITICAL)
━━━━━━━━━━━━━━━━━━━━━━
You are strictly forbidden from inventing literal word-by-word translations. Always map your intent to how real young Telugu couples talk casually on WhatsApp/Instagram:
❌ BANNED DRAMATIC/BOOKISH/ROBOTIC WORDS (NEVER USE THESE):
- Never use "jeevan saarthakam" (dramatic, bookish). Instead use: "naa life set aipothundi" or "chala happy ga undhi".
- Never use "prati palu" or "prathi paalu" (broken translation of moment). Instead use: "prathi kshanam" or "roju motham".
- Never use literal English translations like "nuvvu chala precious ga unnav" or "badha peduthunnav". Instead use: "nuvvu naku chala pranam bujji" or "ninnu badha pettalani ledu bangaram".
- Never use broken words like "pettaanivela" or "alochichadame". Always use correct orthography: "alochinchadame", "chesa", "matladukundham".
- Never use literal translations for family references like "pakkane amma and akka unnaru kani". Instead say: "Amma, akka unte parvaledu le bujji, tharvatha free unnapudu call chei. 😉" or "Pakkana evarunna parvaledu le, tharvatha matladukundham. ❤️"
- Never say creepy flirty things when the partner is angry or complaining. If she says "you are torturing/tormenting me", say: "Ninnu torture cheddhamani kaadu le bangaram. Teasing chesthunna le bujji, serious ga theesukoku! ❤️"

👉 PERFECT COLLOQUIAL FORMULA FOR CRITICAL PHRASES:
- "I'm thinking about you" -> "Nee dhyasa lone unna bangaram ❤️" or "Nee gurinche alochisthu unna bujji 😘"
- "I'm waiting for your message" -> "Nee msg kosam eduru choosthunna bangaram! 🥰"
- "Tell me your pain/let's talk" -> "Badha padaku bangaram, nenu unna kadaa. Free unnapudu call chei matladukundham! ❤️"
- "Don't be angry/sad" -> "Kopam tagginda bangaram? Pls smile okasari! 🥰"

━━━━━━━━━━━━━━━━━━━━━━
🎭 TONE DEFINITIONS
━━━━━━━━━━━━━━━━━━━━━━
ROMANTIC: Deep, heartfelt, makes her feel she's his whole world.
  → Use: ne gurinchi alochisthunna, miss aipothunna, nee tho unnapudu
  → Energy: soft, sincere, boyfriend material

SWEET: Cute, warm, cozy banter. The kind that makes her go "aww".
  → Use: bujji, scroll chesthunna, boring without you
  → Energy: lighthearted, wholesome, puppy love

FUNNY: Witty, self-aware humor that makes her laugh.
  → Use: insomnia sponsor kavali, phone brighter than future, dramatic-but-charming
  → Energy: playful teasing, zero cringe, Gen-Z desi humor

BOLD: Confident, flirty, slightly daring without being disrespectful.
  → Use: midnight plans, bold compliments, 😏 energy
  → Energy: cool guy who knows what he wants

COMFORTING/APOLOGETIC: Soft, reassuring, gentle, sincere apology to de-escalate fights or sadness.
  → Use: badha padaku bangaram, sorry bujji, nenu unna kadaa, pls smile okasari
  → Energy: loving protector, mature boyfriend, extremely comforting

CURRENT SELECTED TONE: {tone}

━━━━━━━━━━━━━━━━━━━━━━
💡 STYLE INSPIRATION (Native Dataset)
━━━━━━━━━━━━━━━━━━━━━━
{dataset_context}

━━━━━━━━━━━━━━━━━━━━━━
📤 OUTPUT FORMAT — STRICTLY FOLLOW
━━━━━━━━━━━━━━━━━━━━━━
Respond ONLY as a valid JSON array of exactly 3 strings.
No markdown. No explanation. No preamble. No code fences.
["reply 1", "reply 2", "reply 3"]"""

    print("\n----------------- RETRIEVED DATASET CONTEXT -----------------")
    print(dataset_context)
    print("-------------------------------------------------------------")
    print("\nSending API Request...")
    
    if engine_choice == "2":
        print(f"Using Google Gemini API...")
        response = make_gemini_request(DEFAULT_GEMINI_KEY, system_instruction, latest_message)
    else:
        success = False
        response = ""
        for idx, groq_key in enumerate(GROQ_KEYS):
            print(f"Trying Groq Llama API (Key {idx+1}: {groq_key[:10]}...)...")
            res = make_groq_request(groq_key, system_instruction, latest_message)
            if "HTTP Error" not in res and "Error:" not in res:
                response = res
                success = True
                print(f"✅ Key {idx+1} succeeded!")
                break
            else:
                print(f"❌ Key {idx+1} failed: {res.strip()}")
        
        if not success:
            response = "All Groq keys failed. Please check your keys or network."
        
    print("\n================== RAW RESPONSE FROM LLM ==================")
    print(response)
    print("===========================================================")
    
    # Try parsing to make sure it's valid JSON
    try:
        parsed = json.loads(response.strip())
        parsed = [sanitize_reply(item) for item in parsed]
        print("\n✅ SUCCESS: Valid JSON Array of 3 items generated!")
        for idx, item in enumerate(parsed):
            print(f"  Option {idx+1}: {item}")
            
        print("\n-------------------------------------------------------------")
        choice = input("Select which reply you like best to train the model [1, 2, 3 or Enter to skip]: ").strip()
        if choice in ["1", "2", "3"]:
            chosen_text = parsed[int(choice) - 1]
            record_chosen_reply(chosen_text)
    except Exception as e:
        import re
        # Extract all quoted strings
        matches = re.findall(r'"([^"]+)"', response)
        parsed = [sanitize_reply(m) for m in matches if m.strip()]
        if len(parsed) >= 3:
            parsed = parsed[:3]
            print("\n✅ SUCCESS: Extracted 3 options using regex fallback parser!")
            for idx, item in enumerate(parsed):
                print(f"  Option {idx+1}: {item}")
                
            print("\n-------------------------------------------------------------")
            choice = input("Select which reply you like best to train the model [1, 2, 3 or Enter to skip]: ").strip()
            if choice in ["1", "2", "3"]:
                chosen_text = parsed[int(choice) - 1]
                record_chosen_reply(chosen_text)
        else:
            print("\n❌ WARNING: Output is NOT a valid JSON array!")

if __name__ == "__main__":
    main()