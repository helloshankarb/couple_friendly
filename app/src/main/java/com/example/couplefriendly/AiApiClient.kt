package com.couplefriendly.app

import android.content.Context
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

object AiApiClient {
    
    private var appContext: Context? = null

    // =========================================================================
    // 🌐 VERCEL PROXY — API keys live on the server, never in the APK
    // Set VERCEL_URL to your deployed endpoint, e.g.:
    //   https://your-app-name.vercel.app/api/suggest
    // =========================================================================
    private const val VERCEL_URL = "https://couple-friendly-vercel.vercel.app/api/suggest"

    // Optional shared secret — set the same value as APP_SECRET in Vercel env vars
    // This is a low-sensitivity value (rate-limit protection only, not a user credential)
    private const val APP_SECRET = "change-me-to-random-string"

    fun setApiKey(key: String) { /* kept for UI compatibility — keys now live on server */ }
    fun setGeminiApiKey(key: String) { /* kept for UI compatibility — keys now live on server */ }

    // =========================================================================
    // 🌐 VERCEL PROXY CALL — single endpoint, keys stored server-side
    // =========================================================================
    suspend fun fetchSuggestions(
        history: List<String>,
        latestMessage: String,
        tone: String
    ): List<String> = withContext(Dispatchers.IO) {

        val intent = determineIntentCategory(latestMessage)
        val finalTone = if (intent == "fight" || intent == "care") "Comforting/Apologetic" else tone

        // 1. Try Vercel proxy (handles Gemini + Groq rotation server-side)
        val vercelResult = fetchFromVercel(history, latestMessage, finalTone)
        if (vercelResult != null && vercelResult.isNotEmpty()) {
            return@withContext vercelResult.map { sanitizeReply(it) }
        }
        Log.w("CoupleFriendly", "Vercel unreachable. Falling back to local dataset.")

        // 3. Local dataset fallback (offline)
        Log.d("CoupleFriendly", "All AI engines exhausted. Using local dataset.")
        return@withContext getLocalFallbackSuggestions(latestMessage, finalTone)
    }


    // =========================================================================
    // 🌐 VERCEL FETCH — sends request to your deployed proxy
    // =========================================================================
    private suspend fun fetchFromVercel(
        history: List<String>,
        latestMessage: String,
        tone: String
    ): List<String>? = withContext(Dispatchers.IO) {
        try {
            val historyJson = history.takeLast(6).joinToString(",") { "\"${it.replace("\"", "\\\"")}\"" }
            val escapedMsg = latestMessage.replace("\"", "\\\"")
            val escapedTone = tone.replace("\"", "\\\"")
            val jsonBody = "{\"incoming\":\"$escapedMsg\",\"tone\":\"$escapedTone\",\"history\":[$historyJson]}"

            val url = URL(VERCEL_URL)
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json")
            conn.setRequestProperty("X-App-Secret", APP_SECRET)
            conn.connectTimeout = 15000
            conn.readTimeout = 15000
            conn.doOutput = true

            OutputStreamWriter(conn.outputStream, "UTF-8").use { it.write(jsonBody); it.flush() }

            if (conn.responseCode == HttpURLConnection.HTTP_OK) {
                val response = BufferedReader(InputStreamReader(conn.inputStream)).readText()
                Log.d("CoupleFriendly", "Vercel response: $response")
                // Parse {"suggestions":["reply1","reply2","reply3"]}
                val regex = "\"([^\"]+)\"".toRegex()
                val suggestionsKey = "\"suggestions\":"
                val startIdx = response.indexOf(suggestionsKey)
                if (startIdx != -1) {
                    val arrayStart = response.indexOf("[", startIdx)
                    val arrayEnd = response.indexOf("]", arrayStart)
                    if (arrayStart != -1 && arrayEnd != -1) {
                        val arrayContent = response.substring(arrayStart + 1, arrayEnd)
                        val replies = regex.findAll(arrayContent).map { it.groupValues[1] }.toList()
                        if (replies.size >= 2) return@withContext replies.take(3)
                    }
                }
            } else {
                Log.e("CoupleFriendly", "Vercel error: ${conn.responseCode}")
            }
        } catch (e: Exception) {
            Log.e("CoupleFriendly", "Vercel request failed", e)
        }
        return@withContext null
    }

    // =========================================================================
    // 📦 JSON DATASET-POWERED FALLBACK ENGINE
    // Loads flirt_dataset.json from assets, keyword-matches the incoming message,
    // and returns highly relevant, shuffled Telugu flirting replies!
    // =========================================================================
    
    private var datasetCache: List<Map<String, Any>>? = null

    fun initDataset(context: Context) {
        appContext = context.applicationContext
        if (datasetCache != null) return
        try {
            val jsonString = context.assets.open("flirt_dataset.json").bufferedReader().use { it.readText() }
            datasetCache = parseDatasetJson(jsonString)
            Log.d("CoupleFriendly", "Dataset loaded: ${datasetCache?.size ?: 0} patterns")
        } catch (e: Exception) {
            Log.e("CoupleFriendly", "Failed to load flirt dataset", e)
        }
    }

    @Suppress("UNCHECKED_CAST")
    private fun parseDatasetJson(json: String): List<Map<String, Any>> {
        val results = mutableListOf<Map<String, Any>>()
        // Simple manual JSON array-of-objects parser
        val trimmed = json.trim()
        if (!trimmed.startsWith("[")) return results
        
        var i = 1 // skip opening [
        while (i < trimmed.length) {
            // Find next object
            val objStart = trimmed.indexOf('{', i)
            if (objStart == -1) break
            
            // Find matching closing brace (handle nested arrays)
            var braceCount = 0
            var objEnd = objStart
            for (j in objStart until trimmed.length) {
                when (trimmed[j]) {
                    '{' -> braceCount++
                    '}' -> {
                        braceCount--
                        if (braceCount == 0) { objEnd = j; break }
                    }
                }
            }
            
            val objStr = trimmed.substring(objStart, objEnd + 1)
            val entry = mutableMapOf<String, Any>()
            
            // Extract "incoming" field
            val incomingMatch = "\"incoming\"\\s*:\\s*\"([^\"]+)\"".toRegex().find(objStr)
            if (incomingMatch != null) {
                entry["incoming"] = incomingMatch.groupValues[1]
            }
            
            // Extract arrays for each tone
            for (tone in listOf("romantic", "sweet", "funny", "bold")) {
                val tonePattern = "\"$tone\"\\s*:\\s*\\[([^\\]]+)\\]".toRegex()
                val toneMatch = tonePattern.find(objStr)
                if (toneMatch != null) {
                    val arrayContent = toneMatch.groupValues[1]
                    val items = "\"([^\"]+)\"".toRegex().findAll(arrayContent).map { it.groupValues[1] }.toList()
                    entry[tone] = items
                }
            }
            
            if (entry.containsKey("incoming")) {
                results.add(entry)
            }
            
            i = objEnd + 1
        }
        return results
    }

    fun sanitizeReply(text: String): String {
        var clean = text.trim()
        
        // Remove surrounding quotes or bracket artifacts
        clean = clean.removeSurrounding("\"").removeSurrounding("'")
        
        // List of common JSON spelling corrections and robotic translations
        val corrections = mapOf(
            "alochichadame" to "alochinchadame",
            "alochichadam" to "alochinchadam",
            "alochichanu" to "alochinchanu",
            "alochichasthu" to "alochisthu",
            "alochichatam" to "alochinchadam",
            "alochiche" to "alochinche",
            "puri munigipoyanu" to "poorthiga munigipoya",
            "puri munigipoya" to "poorthiga munigipoya",
            "munigipoyanu" to "munigipoya",
            "upiri theesukuntunna" to "nee dhyasa lo unna",
            "oopiri theeskuntunna" to "nee dhyasa lo unna",
            "vunta" to "unta",
            "vuntunna" to "untunna",
            "vunnav" to "unnav",
            "vunnaru" to "unnaru",
            "cheshanu" to "chesa",
            "chesthunnau" to "chesthunna",
            "eduru choostunna" to "wait chesthunna",
            "eduruchoostunna" to "wait chesthunna",
            "pettukovoyyi" to "petko",
            "poortiga" to "poorthiga",
            "chudali" to "chudaali",
            "unnapudu" to "unnappudu",
            "avuthundi" to "avuthundi",
            "aipothunna" to "aipoya",
            "matladaku" to "matladodu",
            "vadiley" to "vadilei",
            "badha ga undhi" to "baadhaga undi",
            "badhaga undhi" to "baadhaga undi",
            "badha ga undi" to "baadhaga undi",
            "kopam ga" to "kopamga",
            "na silence complete missing thought analysis" to "miss avthunna bujji, busy unna",
            "na silence complete missing thought" to "miss avthunna bujji, phone silent lo undi",
            "na silence complete missing" to "miss avthunna bujji",
            "naa silence complete missing thought analysis" to "miss avthunna bujji, busy unna",
            "naa silence complete missing thought" to "miss avthunna bujji, phone silent lo undi",
            "naa silence complete missing" to "miss avthunna bujji",
            "naa gundey full ga ne di only" to "naa gunde motham neede bujji",
            "na gundey full ga ne di only" to "naa gunde motham neede bujji",
            "naa gunde full ga ne di only" to "naa gunde motham neede bujji",
            "na gunde full ga ne di only" to "naa gunde motham neede bujji",
            "nee msg kosam eduru choosthunna" to "nee msg kosam wait chesthunna",
            "nee msg kosam eduruchoosthunna" to "nee msg kosam wait chesthunna",
            "nee message kosam eduru choosthunna" to "nee msg kosam wait chesthunna",
            "nee message kosam eduruchoosthunna" to "nee msg kosam wait chesthunna",
            "premisthunna nee life" to "nee meeda prema eppatiki thaggadu bangaram",
            "premisthunnanu nee life" to "nee meeda prema eppatiki thaggadu bangaram",
            "premisthunna na life" to "nuvve na life bangaram",
            "premisthunnanu na life" to "nuvve na life bangaram",
            "nannu vodileyaku" to "please nannu dooram pettaku",
            "nannu vadileyaku" to "please nannu dooram pettaku",
            "nannu vodileiyaku" to "please nannu dooram pettaku",
            "duranga vellaku" to "dooram vellaku",
            "duranga vellipoku" to "dooranga vellipoku",
            "matladatam ledhu endhuku" to "matladadam ledu enduku",
            "matladatam ledu endhuku" to "matladadam ledu enduku",
            "matladatam ledhu enduku" to "matladadam ledu enduku",
            "matladadam ledhu endhuku" to "matladadam ledu enduku",
            "kopam thaggincha" to "kopam tagginda",
            "kopam thagginchava" to "kopam tagginda",
            "tax kattaali" to "tax kattali"
        )
        
        // Case-insensitive replacement
        for ((wrong, right) in corrections) {
            val pattern = "(?i)\\b$wrong\\b".toRegex()
            clean = clean.replace(pattern, right)
            
            // Also replace substring matches if they are compound words
            if (clean.lowercase().contains(wrong)) {
                clean = clean.replace(wrong, right, ignoreCase = true)
            }
        }
        
        // Force informal friendly/romantic address (avoid robotic 'meeru' or formal 'ela unnaru')
        clean = clean.replace("(?i)\\bmeeru\\b".toRegex(), "nuvvu")
        clean = clean.replace("(?i)\\bela unnaru\\b".toRegex(), "ela unnav")
        clean = clean.replace("(?i)\\bmeere\\b".toRegex(), "nuvve")
        
        // Pronoun confusion fixes (correcting "I am thinking of myself" to "I am thinking of you")
        clean = clean.replace("(?i)\\bnaa? gurinche alochisthunna\\b".toRegex(), "nee gurinche alochisthunna")
        clean = clean.replace("(?i)\\bnaa? gurinchi alochisthunna\\b".toRegex(), "nee gurinche alochisthunna")
        
        clean = clean.replace("(?i)\\bkopam chesukoku\\b".toRegex(), "kopam vaddu")
        clean = clean.replace("(?i)\\bkopam cheyyaku\\b".toRegex(), "kopam vaddu")
        clean = clean.replace("(?i)\\bkopam cheyaku\\b".toRegex(), "kopam vaddu")
        clean = clean.replace("(?i)\\bnaa? mind lo nuvvu undhi?\\b".toRegex(), "naa mind lo nuvve vunnav")
        clean = clean.replace("(?i)\\bnaa? mind lo nuvvu undi\\b".toRegex(), "naa mind lo nuvve vunnav")
        clean = clean.replace("(?i)\\bnaa? mind lo nuvve unnav\\b".toRegex(), "naa mind lo nuvve vunnav")
        clean = clean.replace("(?i)\\bnaa? mind lo nuvve vunnav\\b".toRegex(), "naa mind lo nuvve vunnav")
        
        // Ensure emoji spacing
        val emojiRegex = "[\\uD83C-\\uDBFF\\uDC00-\\uDFFF]+$".toRegex()
        val match = emojiRegex.find(clean)
        if (match != null) {
            val emojiStart = match.range.first
            if (emojiStart > 0 && clean[emojiStart - 1] != ' ') {
                clean = clean.substring(0, emojiStart) + " " + clean.substring(emojiStart)
            }
        }

        return clean
    }

    private fun determineIntentCategory(message: String): String {
        val msg = message.lowercase().trim()
        val cleanWords = msg.split("\\s+".toRegex())
            .map { it.replace("[^a-zA-Z]".toRegex(), "") }
            .filter { it.isNotEmpty() }
            .toSet()

        return when {
            msg.contains("morning") || msg.contains("mrng") || cleanWords.contains("gm") -> "morning"
            msg.contains("night") || msg.contains("nidra") || msg.contains("sleep") || msg.contains("paduko") || msg.contains("online") -> "night"
            msg.contains("tinnava") || msg.contains("thinnava") || msg.contains("tinna") || msg.contains("thinna") || msg.contains("food") -> "tinnava"
            msg.contains("miss") || msg.contains("missing") -> "missing"
            msg.contains("exgurinchi") || msg.contains("past") || msg.contains("jealous") || cleanWords.contains("ex") || cleanWords.contains("ex-") -> "jealousy"
            msg.contains("handsome") || msg.contains("cute") || msg.contains("beautiful") || msg.contains("gorgeous") || msg.contains("stunning") || msg.contains("photo") || cleanWords.contains("pic") || cleanWords.contains("pics") -> "compliment"
            msg.contains("love") || msg.contains("prema") || msg.contains("premisth") -> "flirt"
            msg.contains("torture") || msg.contains("torcher") || msg.contains("fight") || msg.contains("kopam") || msg.contains("badha") || msg.contains("baadha") || msg.contains("hurt") || msg.contains("silent") || msg.contains("silence") || msg.contains("matladatam ledhu") || msg.contains("matladadam ledhu") || msg.contains("picha") || msg.contains("pichi") || msg.contains("venta") || msg.contains("padoddu") || msg.contains("padaku") || msg.contains("vaddu") || msg.contains("vadiley") || msg.contains("matladaku") || msg.contains("irritate") || msg.contains("irritat") || msg.contains("nachaledu") || msg.contains("nachavu") || msg.contains("nachedu") || msg.contains("nachala") || cleanWords.contains("sad") -> "fight"
            msg.contains("care") || msg.contains("important") || msg.contains("tired") || msg.contains("rest") -> "care"
            msg.contains("pelli") || msg.contains("marriage") || msg.contains("proposal") -> "proposal"
            msg.contains("bore") || msg.contains("boring") || msg.contains("trip") || msg.contains("gift") || msg.contains("ekkadiki") -> "random"
            else -> ""
        }
    }

    @Suppress("UNCHECKED_CAST")
    fun getLocalFallbackSuggestions(latestMessage: String, tone: String): List<String> {
        val cleanTone = tone.lowercase()
        val toneKey = when {
            cleanTone.contains("romantic") -> "romantic"
            cleanTone.contains("sweet") -> "sweet"
            cleanTone.contains("funny") -> "funny"
            cleanTone.contains("bold") -> "bold"
            else -> "romantic"
        }

        val dataset = datasetCache
        if (dataset == null || dataset.isEmpty()) {
            return listOf(
                "Cheppu bangaram, vintunna! ❤️",
                "Haha nice, inka cheppu! 😊",
                "Aww so sweet! 🥰"
            )
        }

        val intent = determineIntentCategory(latestMessage)
        val filteredDataset = if (intent.isNotEmpty()) {
            dataset.filter { entry ->
                val category = (entry["category"] as? String ?: "").lowercase()
                val incoming = (entry["incoming"] as? String ?: "").lowercase()
                category.contains(intent) || incoming.contains(intent)
            }
        } else {
            dataset
        }

        val finalPool = if (filteredDataset.isNotEmpty()) filteredDataset else dataset

        val stopWords = setOf(
            "nuvvu", "nannu", "naa", "nee", "chala", "unnav", "unnaru", "unnappudu", 
            "kadha", "le", "bujji", "bangaram", "baby", "sweetheart", "na", "ne", "ani", 
            "ga", "tho", "koo", "lo", "inka", "i", "am", "you", "are", "the", "to",
            "chesthunnav", "chesthunna", "chesthunnadu", "cheyyi"
        )

        val msgWords = latestMessage.lowercase()
            .split("\\s+".toRegex())
            .map { it.replace("[^a-zA-Z]".toRegex(), "") }
            .filter { it.length > 1 && !stopWords.contains(it) }

        val scored = finalPool.map { entry ->
            val incoming = (entry["incoming"] as? String ?: "").lowercase()
            val incomingWords = incoming.split("\\s+".toRegex()).map { it.replace("[^a-zA-Z]".toRegex(), "") }
            
            val overlap = msgWords.count { word -> 
                incomingWords.any { it.contains(word) || word.contains(it) } 
            }
            val exactMatch = if (incoming == latestMessage.lowercase().trim()) 100 else 0
            entry to (overlap + exactMatch)
        }.sortedByDescending { it.second }

        val allReplies = mutableListOf<String>()
        for ((entry, score) in scored) {
            val replies = entry[toneKey] as? List<String> ?: continue
            allReplies.addAll(replies)
            if (allReplies.size >= 15) break
        }

        if (allReplies.isNotEmpty()) {
            return allReplies.shuffled().take(3).map { sanitizeReply(it) }
        }

        return listOf(
            "Cheppu bangaram, vintunna! ❤️",
            "Haha nice, inka cheppu! 😊",
            "Aww so sweet! 🥰"
        )
    }

    @Suppress("UNCHECKED_CAST")
    private fun getRelatedDatasetExamples(latestMessage: String): String {
        val dataset = datasetCache
        if (dataset == null || dataset.isEmpty()) return ""

        val intent = determineIntentCategory(latestMessage)
        val filteredDataset = if (intent.isNotEmpty()) {
            dataset.filter { entry ->
                val category = (entry["category"] as? String ?: "").lowercase()
                val incoming = (entry["incoming"] as? String ?: "").lowercase()
                category.contains(intent) || incoming.contains(intent)
            }
        } else {
            dataset
        }

        val finalPool = if (filteredDataset.isNotEmpty()) filteredDataset else dataset

        val stopWords = setOf(
            "nuvvu", "nannu", "naa", "nee", "chala", "unnav", "unnaru", "unnappudu", 
            "kadha", "le", "bujji", "bangaram", "baby", "sweetheart", "na", "ne", "ani", 
            "ga", "tho", "koo", "lo", "inka", "i", "am", "you", "are", "the", "to",
            "chesthunnav", "chesthunna", "chesthunnadu", "cheyyi"
        )

        val msgWords = latestMessage.lowercase()
            .split("\\s+".toRegex())
            .map { it.replace("[^a-zA-Z]".toRegex(), "") }
            .filter { it.length > 1 && !stopWords.contains(it) }

        val scored = finalPool.map { entry ->
            val incoming = (entry["incoming"] as? String ?: "").lowercase()
            val incomingWords = incoming.split("\\s+".toRegex()).map { it.replace("[^a-zA-Z]".toRegex(), "") }
            
            val overlap = msgWords.count { word -> 
                incomingWords.any { it.contains(word) || word.contains(it) } 
            }
            val exactMatch = if (incoming == latestMessage.lowercase().trim()) 100 else 0
            entry to (overlap + exactMatch)
        }.filter { it.second > 0 }.sortedByDescending { it.second }

        if (scored.isEmpty()) {
            val defaults = finalPool.shuffled().take(2)
            return formatEntriesForPrompt(defaults)
        }

        return formatEntriesForPrompt(scored.take(2).map { it.first })
    }

    @Suppress("UNCHECKED_CAST")
    private fun formatEntriesForPrompt(entries: List<Map<String, Any>>): String {
        val sb = StringBuilder()
        for (entry in entries) {
            val incoming = entry["incoming"] as? String ?: continue
            sb.append("- When she says: \"$incoming\"\n")
            for (tone in listOf("romantic", "sweet", "funny", "bold")) {
                val replies = entry[tone] as? List<String> ?: continue
                val sanitizedReplies = replies.map { sanitizeReply(it) }
                sb.append("  * ${tone.replaceFirstChar { it.uppercase() }}: ${sanitizedReplies.joinToString(" OR ")}\n")
            }
            sb.append("\n")
        }
        return sb.toString()
    }

    /**
     * Saves a successfully chosen reply to learn user's preferred style.
     */
    fun recordChosenReply(replyText: String) {
        val context = appContext ?: return
        try {
            val prefs = context.getSharedPreferences("user_style_pref", Context.MODE_PRIVATE)
            val savedSet = prefs.getStringSet("replies", emptySet()) ?: emptySet()
            
            val updatedList = savedSet.toMutableList()
            if (updatedList.contains(replyText)) {
                updatedList.remove(replyText)
            }
            updatedList.add(0, replyText) // Put the latest chosen reply at the top
            
            // Keep only the top 5 most recent preferred replies
            val trimmedList = updatedList.take(5)
            
            prefs.edit().putStringSet("replies", trimmedList.toSet()).apply()
            Log.d("CoupleFriendly", "Saved user style preference: $replyText")
        } catch (e: java.lang.Exception) {
            Log.e("CoupleFriendly", "Failed to save chosen reply style", e)
        }
    }

    /**
     * Retrieves the formatted personal writing style from SharedPreferences.
     */
    private fun getUserStyleContext(): String {
        val context = appContext ?: return ""
        try {
            val prefs = context.getSharedPreferences("user_style_pref", Context.MODE_PRIVATE)
            val savedSet = prefs.getStringSet("replies", emptySet()) ?: emptySet()
            if (savedSet.isEmpty()) return ""
            
            return "\n━━━━━━━━━━━━━━━━━━━━━━\n💡 USER'S PERSONAL WRITING STYLE (PREFERRED PAST REPLIES):\n" +
                    savedSet.joinToString("\n") { "  - $it" } + "\n"
        } catch (e: java.lang.Exception) {
            Log.e("CoupleFriendly", "Failed to read user style preference", e)
        }
        return ""
    }


}
