# -*- coding: utf-8 -*-
"""
CoupleFriendly - Tanglish Text Normalizer & Preprocessor
Performs repetition compression, phonetic typo standardization, and token cleanup.
"""

import re

PHONETIC_TYPO_MAP = {
    "ekad": "ekkada",
    "ekada": "ekkada",
    "unav": "unnav",
    "nanu": "nannu",
    "ninu": "ninnu",
    "naku": "naaku",
    "istam": "ishtam",
    "istammm": "ishtam",
    "avthuna": "avuthunna",
    "avthunaa": "avuthunna",
    "avthunnav": "avuthunnav",
    "avuthunav": "avuthunnav",
    "matladatle": "matladatledu",
    "matladotle": "matladatledu",
    "cehpthe": "chepthe",
    "ceyyaku": "cheyyaku",
    "edipisthunaav": "edipisthunnav",
    "edipisthunav": "edipisthunnav",
    "chestunav": "chesthunnav",
    "chesthunaav": "chesthunnav",
    "chestunaav": "chesthunnav",
    "chudatam": "chudadam",
    "vintha": "vinta",
    "plz": "please",
    "tq": "thank you",
    "gm": "good morning",
    "gn": "good night",
    "wt": "enti",
    "y": "enduku"
}

def compress_elongation(text: str) -> str:
    """
    Compresses expressive elongated character repetitions:
    e.g. 'chestunavvv' -> 'chestunav'
         'istammm'     -> 'istam'
         'kopamaaaa'   -> 'kopama'
         'hiiii'       -> 'hi'
    Preserves valid double consonants (e.g. 'nannu', 'bujji', 'unnav').
    """
    # First compress 3+ repeats down to 1
    # Special case: for 'a' or vowels, compress 3+ to 1
    def repl(match):
        char = match.group(1)
        # In Telugu Latin script, double consonants like kk, tt, nn, dd, ll, mm, jj can be valid
        # But when user writes 3+ (e.g., vvv, aaaa, mmm), reduce to standard 1
        return char

    compressed = re.sub(r'([a-zA-Z])\1{2,}', r'\1', text)
    return compressed

def normalize_tanglish(text: str) -> str:
    """
    Full text normalization pipeline:
    1. Lowercase & strip excess whitespace
    2. Compress elongated characters
    3. Standardize phonetic typos and dialect chat slang
    """
    if not text:
        return ""

    # Lowercase & basic punctuation cleanup
    clean = text.lower().strip()
    # Remove excessive repeated punctuation (e.g. '???', '!!!')
    clean = re.sub(r'([!?.,])\1+', r'\1', clean)

    # Elongation compression
    clean = compress_elongation(clean)

    # Word-by-word typo mapping
    words = clean.split()
    normalized_words = []
    for w in words:
        # Strip trailing punctuation for dictionary lookup
        core_word = re.sub(r'[^\w\s]', '', w)
        punct = w[len(core_word):] if len(w) > len(core_word) else ""
        if core_word in PHONETIC_TYPO_MAP:
            normalized_words.append(PHONETIC_TYPO_MAP[core_word] + punct)
        else:
            normalized_words.append(w)

    result = " ".join(normalized_words)
    return result

if __name__ == "__main__":
    test_inputs = [
        "em chestunavvv",
        "em chesthunaav",
        "ninnu miss avthunaa",
        "ninu enduku ignore chesthunav",
        "nuvvu ekad unav",
        "naatho enduku matladatle",
        "naku chala istammm",
        "kopamaaaa",
        "edipisthunaavvv",
        "nuvvu nanu hurt chesav"
    ]
    print("Normalizer Verification:")
    for inp in test_inputs:
        print(f"  {inp:30} -> {normalize_tanglish(inp)}")
