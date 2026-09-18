package com.couplefriendly.app.ml

import android.content.Context
import org.json.JSONObject

/**
 * 100% Offline Tanglish Text Normalizer & Preprocessor
 * Implements identical phonetic typo standardization, elongation compression,
 * and conversational token classification as the Python pipeline.
 */
object TanglishNormalizer {

    private val defaultTypoMap = mapOf(
        "ekad" to "ekkada",
        "ekada" to "ekkada",
        "unav" to "unnav",
        "nanu" to "nannu",
        "ninu" to "ninnu",
        "naku" to "naaku",
        "istam" to "ishtam",
        "istammm" to "ishtam",
        "avthuna" to "avuthunna",
        "avthunaa" to "avuthunna",
        "avthunnav" to "avuthunnav",
        "avuthunav" to "avuthunnav",
        "matladatle" to "matladatledu",
        "matladotle" to "matladatledu",
        "cehpthe" to "chepthe",
        "ceyyaku" to "cheyyaku",
        "cheyaku" to "cheyyaku",
        "seyyaku" to "cheyyaku",
        "edipisthunaav" to "edipisthunnav",
        "edipisthunav" to "edipisthunnav",
        "chestunav" to "chesthunnav",
        "chesthunaav" to "chesthunnav",
        "chestunaav" to "chesthunnav",
        "chudatam" to "chudadam",
        "vintha" to "vinta",
        "plz" to "please",
        "tq" to "thank you",
        "gm" to "good morning",
        "gn" to "good night",
        "wt" to "enti",
        "y" to "enduku"
    )

    private var typoMap: MutableMap<String, String> = defaultTypoMap.toMutableMap()
    val pronouns = setOf("nannu", "nenu", "nuvvu", "neeku", "naaku", "naatho", "natho", "neetho")
    val questionTokens = setOf("enduku", "enti", "eppudu", "ekkada", "evaru", "ela", "avuna", "nijama", "kada", "kaada")
    val conciliatoryTokens = listOf("please", "vadiley", "sorry", "forgive", "peace")
    val cryingTokens = listOf("edip", "edav", "yedus", "edupu", "crying")
    val feelingsTokens = listOf("feelings", "care cheyyatledu", "pattinchukovatledu")

    fun init(context: Context) {
        try {
            val jsonStr = context.assets.open("ml/normalizer_rules.json").bufferedReader().use { it.readText() }
            val obj = JSONObject(jsonStr)
            if (obj.has("phonetic_typo_map")) {
                val mapObj = obj.getJSONObject("phonetic_typo_map")
                val keys = mapObj.keys()
                while (keys.hasNext()) {
                    val k = keys.next()
                    typoMap[k] = mapObj.getString(k)
                }
            }
        } catch (_: Exception) {
            // Use built-in defaults safely
        }
    }

    /**
     * Compresses elongated characters:
     * e.g. "chestunavvv" -> "chestunav", "hiiii" -> "hi", "kopamaaaa" -> "kopama"
     */
    fun compressElongation(text: String): String {
        return text.replace("([a-zA-Z])\\1{2,}".toRegex(), "$1")
    }

    /**
     * Complete 3-stage normalization pipeline.
     */
    fun normalize(text: String): String {
        if (text.isBlank()) return ""

        var clean = text.lowercase().trim()
        clean = clean.replace("([!?.,])\\1+".toRegex(), "$1")
        clean = compressElongation(clean)

        val words = clean.split("\\s+".toRegex())
        val normalizedWords = words.map { word ->
            val coreWord = word.replace("[^\\w]".toRegex(), "")
            val punct = if (word.length > coreWord.length) word.substring(coreWord.length) else ""
            val replacement = typoMap[coreWord] ?: coreWord
            replacement + punct
        }

        return normalizedWords.joinToString(" ")
    }

    fun isQuestionFormat(text: String): Boolean {
        val t = text.lowercase().trim()
        if (t.contains("?")) return true
        val words = t.split("\\s+".toRegex()).toSet()
        return words.any { it in questionTokens } || t.endsWith("aa") || t.endsWith("na")
    }

    fun getPronouns(text: String): Set<String> {
        val words = text.lowercase().split("\\s+".toRegex()).map { it.replace("[^a-zA-Z]".toRegex(), "") }.toSet()
        return words.intersect(pronouns)
    }

    fun computeCharDice(s1: String, s2: String): Float {
        val a = s1.lowercase().trim()
        val b = s2.lowercase().trim()
        if (a == b) return 1.0f
        if (a.length < 2 || b.length < 2) return 0.0f

        val b1 = mutableSetOf<String>()
        for (i in 0 until a.length - 1) b1.add(a.substring(i, i + 2))

        val b2 = mutableSetOf<String>()
        for (i in 0 until b.length - 1) b2.add(b.substring(i, i + 2))

        val intersection = b1.intersect(b2).size
        val total = b1.size + b2.size
        return if (total > 0) (2.0f * intersection) / total else 0.0f
    }
}
