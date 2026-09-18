package com.couplefriendly.app

import android.content.Context
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader

data class DatasetScenario(
    val incoming: String,
    val category: String,
    val intent: String,
    val subIntent: String,
    val responses: Map<String, List<String>>
)

data class MessageGroupBundle(
    val incomingMessage: String,
    val detectedEmotion: String,
    val detectedIntent: String,
    val topScenario: String,
    val romantic: List<String>,
    val sweet: List<String>,
    val funny: List<String>,
    val bold: List<String>
)

object AiApiClient {

    private var appContext: Context? = null
    private var datasetCache: List<DatasetScenario>? = null

    fun setApiKey(key: String) { /* API keys disabled for 100% offline local dataset */ }
    fun setGeminiApiKey(key: String) { /* API keys disabled for 100% offline local dataset */ }

    // =========================================================================
    // 📦 DATASET INITIALIZATION
    // Loads flirt_dataset.json (or flirt_dataset_v12.json) from assets
    // =========================================================================
    fun initDataset(context: Context) {
        appContext = context.applicationContext
        com.couplefriendly.app.ml.ReplyEngine.init(context)
        if (datasetCache != null) return

        try {
            val assetManager = context.assets
            val filename = try {
                assetManager.open("flirt_dataset.json").close()
                "flirt_dataset.json"
            } catch (e: Exception) {
                "flirt_dataset_v12.json"
            }

            val jsonString = assetManager.open(filename).bufferedReader(Charsets.UTF_8).use { it.readText() }
            val parsed = parseDataset(jsonString)
            datasetCache = parsed
            Log.d("CoupleFriendly", "Loaded $filename with ${parsed.size} native scenarios.")
        } catch (e: Exception) {
            Log.e("CoupleFriendly", "Failed to load flirt dataset", e)
        }
    }

    private fun parseDataset(jsonString: String): List<DatasetScenario> {
        val list = mutableListOf<DatasetScenario>()
        try {
            val jsonArray = JSONArray(jsonString)
            for (i in 0 until jsonArray.length()) {
                val obj = jsonArray.getJSONObject(i)
                val incoming = obj.optString("incoming", "")
                val category = obj.optString("category", "casual_chat")
                val intent = obj.optString("intent", "CASUAL_CHAT")
                val subIntent = obj.optString("sub_intent", "")

                val responseMap = mutableMapOf<String, List<String>>()
                val responsesObj = obj.optJSONObject("responses")

                for (tone in listOf("romantic", "sweet", "funny", "bold")) {
                    val toneList = mutableListOf<String>()
                    if (responsesObj != null && responsesObj.has(tone)) {
                        val arr = responsesObj.optJSONArray(tone)
                        if (arr != null) {
                            for (j in 0 until arr.length()) {
                                val item = arr.get(j)
                                if (item is JSONObject) {
                                    val text = item.optString("text", "")
                                    if (text.isNotBlank()) toneList.add(text)
                                } else if (item is String && item.isNotBlank()) {
                                    toneList.add(item)
                                }
                            }
                        }
                    } else if (obj.has(tone)) {
                        val arr = obj.optJSONArray(tone)
                        if (arr != null) {
                            for (j in 0 until arr.length()) {
                                val item = arr.optString(j, "")
                                if (item.isNotBlank()) toneList.add(item)
                            }
                        }
                    }
                    responseMap[tone] = toneList
                }

                if (incoming.isNotBlank()) {
                    list.add(DatasetScenario(incoming, category, intent, subIntent, responseMap))
                }
            }
        } catch (e: Exception) {
            Log.e("CoupleFriendly", "Error parsing dataset JSON", e)
        }
        return list
    }

    // =========================================================================
    // 🎯 TWO-STAGE SEMANTIC CLASSIFIER (Emotion vs Intent)
    // =========================================================================
    fun analyzeSemantics(message: String): Pair<String, String> {
        val m = message.lowercase().trim()
        val norm = m.replace("cehpthe", "chepthe")
            .replace("ceyyaku", "cheyyaku")
            .replace("cheyaku", "cheyyaku")
            .replace("seyyaku", "cheyyaku")

        val cleanWords = norm.split("\\s+".toRegex())
            .map { it.replace("[^a-zA-Z]".toRegex(), "") }
            .filter { it.isNotEmpty() }
            .toSet()

        // 1. Contact cutoff / Breakup threats
        val isBreakupThreat = listOf(
            "inkeppudu", "inka eppudu", "block chestha", "block chesta",
            "breakup", "vellipotha", "naa valla kaadu", "single ga untanu",
            "dooram undu", "dooranga undu"
        ).any { norm.contains(it) } || (
            listOf("call", "message", "msg", "phone", "text").any { norm.contains(it) } &&
            listOf("cheyyaku", "vaddu", "oddu", "vadhu", "vaddhu").any { norm.contains(it) }
        )

        // 2. Frustration / Repetition conflict
        val isFrustrationConflict = listOf(
            "ardham kaada", "ardham kaadha", "ardham avvatleda", "ardham kavatleda",
            "ardham kavatledha", "ardham cheskova", "ardham chesukova",
            "oka sari chepthe", "okkasari chepthe", "enni sarlu",
            "chepthe vinava", "cheppindi vinava", "vinara", "vinava",
            "buddhi leda", "mind leda", "sense leda", "visugu", "visugosthondi",
            "visiginchaku", "chiraku", "chimpestha", "gola cheyyaku"
        ).any { norm.contains(it) }

        // Stage 1: Detect Emotion
        var emotion = "NEUTRAL"
        if (isBreakupThreat || isFrustrationConflict) {
            emotion = "ANGRY"
        } else if (listOf("edip", "edav", "edupu", "yedus", "cry", "crying", "hurt", "badha", "baadha", "kallalo", "tears", "pain").any { norm.contains(it) }) {
            emotion = "HURT"
        } else if (listOf("kopam", "gussa", "irritat", "matladaku", "matladanu", "vaddu", "vadiley", "dooram", "fight", "breakup").any { norm.contains(it) } || norm.contains("enduku ila matlad")) {
            emotion = "ANGRY"
        } else if (listOf("ignore", "pattinchukodam", "pattinchukovadam").any { norm.contains(it) }) {
            emotion = "IGNORED"
        } else if (listOf("reply ivvatledu", "reply ivvaledu", "reply enduku").any { norm.contains(it) }) {
            emotion = "NO_REPLY"
        } else if (listOf("ex", "other girl", "ammailu", "jealous").any { norm.contains(it) }) {
            emotion = "JEALOUS"
        } else if (listOf("miss", "missing", "gurthosth", "ontari").any { norm.contains(it) }) {
            emotion = "MISSING"
        } else if (listOf("teas", "allari", "prank", "roast").any { norm.contains(it) }) {
            emotion = "PLAYFUL"
        } else if (listOf("love", "prema", "muddu", "hug", "kiss", "ishtam").any { norm.contains(it) }) {
            emotion = "ROMANTIC"
        }

        // Stage 2: Detect Intent
        var intent = "CASUAL_CHAT"
        if (isBreakupThreat) {
            intent = "BREAKUP_THREATS"
        } else if (isFrustrationConflict) {
            intent = "CONFLICT"
        } else if (listOf("ignore", "pattinchukodam", "pattinchukovadam").any { norm.contains(it) }) {
            intent = "IGNORING"
        } else if (listOf("reply ivvatledu", "reply ivvaledu", "reply enduku").any { norm.contains(it) }) {
            intent = "NO_REPLY"
        } else if (emotion == "HURT" || listOf("hurt", "edip", "baadha", "badha").any { norm.contains(it) }) {
            intent = "EMOTIONAL_HURT"
        } else if (emotion in listOf("ANGRY", "IGNORED") || listOf("kopam", "matladaku", "enduku ila matlad").any { norm.contains(it) }) {
            intent = "CONFLICT"
        } else if (emotion == "JEALOUS") {
            intent = "JEALOUSY"
        } else if (listOf("morning", "mrng").any { norm.contains(it) } || cleanWords.contains("gm")) {
            intent = "GREETING_MORNING"
        } else if (listOf("night", "nidra", "sleep", "paduko").any { norm.contains(it) }) {
            intent = "GREETING_NIGHT"
        } else if (listOf("tinnava", "thinnava", "tinna", "thinna", "food", "curry").any { norm.contains(it) }) {
            intent = "FOOD_CHECK"
        } else if (emotion == "MISSING") {
            intent = "MISSING"
        } else if (listOf("handsome", "cute", "beautiful", "gorgeous", "photo", "pic").any { norm.contains(it) }) {
            intent = "COMPLIMENT"
        } else if (listOf("kalus", "kaluddham", "meet", "date", "bayataki").any { norm.contains(it) }) {
            intent = "DATE_REQUEST"
        } else if (listOf("pelli", "marriage", "proposal").any { norm.contains(it) }) {
            intent = "PROPOSAL"
        } else if (emotion == "PLAYFUL" || listOf("teas", "allari", "prank").any { norm.contains(it) }) {
            intent = "TEASING"
        } else if (listOf("sorry", "kshaminchu").any { norm.contains(it) }) {
            intent = "APOLOGY"
        } else if (listOf("bore", "boring", "trip", "gift").any { norm.contains(it) }) {
            intent = "RANDOM"
        }

        return Pair(emotion, intent)
    }

    // =========================================================================
    // 🛡️ EMOTIONAL SAFETY GATE
    // Protects sensitive intents from insensitive mockery or sexualization
    // =========================================================================
    private fun applySafetyGate(replies: List<String>, intent: String, tone: String): List<String> {
        if (intent !in listOf("EMOTIONAL_HURT", "CONFLICT", "BREAKUP_THREATS")) {
            return replies
        }

        val filtered = mutableListOf<String>()
        if (tone == "funny") {
            val forbidden = listOf("cartoon", "photo frame", "facial glow", "mascara")
            for (r in replies) {
                if (forbidden.none { r.lowercase().contains(it) }) {
                    filtered.add(r)
                }
            }
            if (filtered.isEmpty()) {
                filtered.add("Sare bujji, first tears off cheyyi... tarvatha nannu question cheyyi 😂❤️")
                filtered.add("Ayyo bujji, ila emotional avvaku... first smile ivvu, tarvatha nannu thittuko 😂❤️")
                filtered.add("Mana fight ki referee avasaram ledu, direct ga ice cream tho settle cheddam 😂❤️")
            }
            return filtered
        } else if (tone == "bold") {
            val forbidden = listOf("kisses thoti mayam", "wilder", "intense romance", "chest meeda vaalipo")
            for (r in replies) {
                if (forbidden.none { r.lowercase().contains(it) }) {
                    filtered.add(r)
                }
            }
            if (filtered.isEmpty()) {
                filtered.add("Nuvvu hurt ayye la malli cheyyanu bujji, first naa maatavinu ❤️")
                filtered.add("Nee smile tirigi vacche varaku ninnu convince cheyyadam naa responsibility 😏❤️")
                filtered.add("First step evaru vesina okay… manam matladukundam, dooram undaku 😉❤️")
            }
            return filtered
        }
        return replies
    }

    // =========================================================================
    // ✨ MESSAGE GROUP GENERATOR (Core Production Engine)
    // Generates a multi-style group: Romantic, Sweet, Funny, Bold
    // =========================================================================
    fun generateMessageGroup(message: String): MessageGroupBundle {
        val romantic = com.couplefriendly.app.ml.ReplyEngine.generateRepliesSync(message, com.couplefriendly.app.ml.ReplyTone.ROMANTIC)
        val sweet = com.couplefriendly.app.ml.ReplyEngine.generateRepliesSync(message, com.couplefriendly.app.ml.ReplyTone.SWEET)
        val funny = com.couplefriendly.app.ml.ReplyEngine.generateRepliesSync(message, com.couplefriendly.app.ml.ReplyTone.FUNNY)
        val bold = com.couplefriendly.app.ml.ReplyEngine.generateRepliesSync(message, com.couplefriendly.app.ml.ReplyTone.BOLD)

        return MessageGroupBundle(
            incomingMessage = message,
            detectedEmotion = "",
            detectedIntent = "",
            topScenario = "CoupleFriendly",
            romantic = romantic,
            sweet = sweet,
            funny = funny,
            bold = bold
        )
    }

    // =========================================================================
    // 🌐 APP INTERFACE (Single Tone Extraction)
    // =========================================================================
    suspend fun fetchSuggestions(
        history: List<String>,
        latestMessage: String,
        tone: String
    ): List<String> = withContext(Dispatchers.IO) {
        val group = generateMessageGroup(latestMessage)
        val cleanTone = tone.lowercase()
        val result = when {
            cleanTone.contains("romantic") -> group.romantic
            cleanTone.contains("sweet") -> group.sweet
            cleanTone.contains("funny") -> group.funny
            cleanTone.contains("bold") -> group.bold
            else -> group.sweet
        }
        return@withContext if (result.isNotEmpty()) result else listOf(
            "Cheppu bangaram, vintunna! ❤️",
            "Haha nice, inka cheppu! 😊",
            "Aww so sweet! 🥰"
        )
    }

    fun getLocalFallbackSuggestions(latestMessage: String, tone: String): List<String> {
        val group = generateMessageGroup(latestMessage)
        val cleanTone = tone.lowercase()
        return when {
            cleanTone.contains("romantic") -> group.romantic
            cleanTone.contains("sweet") -> group.sweet
            cleanTone.contains("funny") -> group.funny
            cleanTone.contains("bold") -> group.bold
            else -> group.sweet
        }
    }

    // =========================================================================
    // 🧹 ANTI-ROBOTIC TANGLISH POLISHER
    // =========================================================================
    fun sanitizeReply(text: String): String {
        var clean = text.trim().removeSurrounding("\"").removeSurrounding("'")

        val corrections = mapOf(
            "alochichadame" to "alochinchadame",
            "alochichadam" to "alochinchadam",
            "alochichanu" to "alochinchanu",
            "puri munigipoyanu" to "poorthiga munigipoya",
            "puri munigipoya" to "poorthiga munigipoya",
            "munigipoyanu" to "munigipoya",
            "upiri theesukuntunna" to "nee dhyasa lo unna",
            "oopiri theeskuntunna" to "nee dhyasa lo unna",
            "vunta" to "unta",
            "vuntunna" to "untunna",
            "vunnav" to "unnav",
            "cheshanu" to "chesa",
            "chesthunnau" to "chesthunna",
            "eduru choostunna" to "wait chesthunna",
            "eduruchoostunna" to "wait chesthunna",
            "badha ga undhi" to "baadhaga undi",
            "badhaga undhi" to "baadhaga undi",
            "badha ga undi" to "baadhaga undi",
            "kopam ga" to "kopamga",
            "matladaku" to "matladodu",
            "vadiley" to "vadilei",
            "matladatam ledhu endhuku" to "matladadam ledu enduku"
        )

        for ((wrong, right) in corrections) {
            val pattern = "(?i)\\b$wrong\\b".toRegex()
            clean = clean.replace(pattern, right)
        }

        // Force informal native couple pronouns
        clean = clean.replace("(?i)\\bmeeru\\b".toRegex(), "nuvvu")
        clean = clean.replace("(?i)\\bela unnaru\\b".toRegex(), "ela unnav")
        clean = clean.replace("(?i)\\bmeere\\b".toRegex(), "nuvve")

        // Pronoun direction fixes
        clean = clean.replace("(?i)\\bnaa? gurinche alochisthunna\\b".toRegex(), "nee gurinche alochisthunna")
        clean = clean.replace("(?i)\\bnaa? gurinchi alochisthunna\\b".toRegex(), "nee gurinche alochisthunna")

        return clean
    }
}
