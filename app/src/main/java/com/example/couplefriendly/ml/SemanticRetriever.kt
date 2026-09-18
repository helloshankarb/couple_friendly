package com.couplefriendly.app.ml

import android.content.Context
import org.json.JSONArray
import java.io.InputStream
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sqrt

/**
 * On-device Semantic Retriever and Re-Ranker.
 * Executes sparse vector cosine similarity, intent prior conditioning,
 * and linear re-ranking with 7 weighted features and contextual modifiers.
 */
internal class SemanticRetriever(
    private val intentClassifier: IntentClassifier
) {

    private val scenarios = mutableListOf<ScenarioVector>()
    var isLoaded: Boolean = false
        private set

    fun loadFromAsset(context: Context, assetPath: String = "ml/scenarios_index.json") {
        try {
            context.assets.open(assetPath).use { stream ->
                loadFromStream(stream)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun loadFromStream(stream: InputStream) {
        val jsonStr = stream.bufferedReader(Charsets.UTF_8).use { it.readText() }
        val array = JSONArray(jsonStr)

        scenarios.clear()
        for (i in 0 until array.length()) {
            val obj = array.getJSONObject(i)
            val id = obj.getInt("id")
            val incoming = obj.getString("incoming")
            val category = obj.optString("category", "casual_chat")
            val domain = obj.optString("domain", "GENERAL")
            val intent = obj.optString("intent", "GENERAL_CHAT")
            val emotion = obj.optString("emotion", "NEUTRAL")

            val idxArr = obj.getJSONArray("sparse_indices")
            val indices = IntArray(idxArr.length())
            for (j in 0 until idxArr.length()) {
                indices[j] = idxArr.getInt(j)
            }

            val valArr = obj.getJSONArray("sparse_values")
            val values = FloatArray(valArr.length())
            for (j in 0 until valArr.length()) {
                values[j] = valArr.getDouble(j).toFloat()
            }

            val respObj = obj.getJSONObject("responses")
            val respMap = mutableMapOf<String, List<String>>()
            val keys = respObj.keys()
            while (keys.hasNext()) {
                val tone = keys.next()
                val listArr = respObj.getJSONArray(tone)
                val list = mutableListOf<String>()
                for (k in 0 until listArr.length()) {
                    list.add(listArr.getString(k))
                }
                respMap[tone] = list
            }

            scenarios.add(
                ScenarioVector(
                    id = id,
                    incoming = incoming,
                    category = category,
                    domain = domain,
                    intent = intent,
                    emotion = emotion,
                    sparseIndices = indices,
                    sparseValues = values,
                    responses = respMap
                )
            )
        }
        this.isLoaded = true
    }

    private fun computeSubIntentAlignment(query: String, scenario: String): Float {
        val qWords = query.lowercase().split("\\s+".toRegex()).toSet()
        val sWords = scenario.lowercase().split("\\s+".toRegex()).toSet()
        val overlap = qWords.intersect(sWords).size
        val denom = max(1, min(qWords.size, sWords.size))
        return min(1.0f, overlap.toFloat() / denom)
    }

    /**
     * Retrieves top-K scenarios matching the normalized query using the linear re-ranker.
     */
    fun retrieve(
        query: String,
        predictedIntent: String,
        predictedEmotion: String,
        topK: Int = 5
    ): List<ScoredScenario> {
        if (!isLoaded || scenarios.isEmpty()) return emptyList()

        val qSparse = intentClassifier.extractSparseFeatures(query)
        var qNormSq = 0.0f
        for ((_, v) in qSparse) {
            qNormSq += v * v
        }
        val qNorm = sqrt(qNormSq)

        val qPronouns = TanglishNormalizer.getPronouns(query)
        val qIsQuestion = TanglishNormalizer.isQuestionFormat(query)

        // Stage 1: Candidate Pool Retrieval (Cosine Similarity + Prior Bonus)
        val stage1Pool = mutableListOf<Pair<Float, ScenarioVector>>()

        for (sc in scenarios) {
            // Fast domain filtering
            if (predictedIntent in listOf("EMOTIONAL_HURT", "CONFLICT_FRUSTRATION", "ANGER_ARGUMENT", "BREAKUP_THREATS") &&
                sc.domain == "PLAYFUL_HUMOR"
            ) {
                continue
            }
            if (predictedIntent in listOf("TEASING", "PLAYFUL_BANTER") && sc.domain == "CONFLICT") {
                continue
            }

            // Sparse cosine dot product
            var dot = 0.0f
            if (qNorm > 0.0f) {
                for (j in sc.sparseIndices.indices) {
                    val scIdx = sc.sparseIndices[j]
                    val qVal = qSparse[scIdx] ?: continue
                    dot += qVal * sc.sparseValues[j]
                }
            }
            val rawSim = if (qNorm > 0.0f) max(0.0f, min(1.0f, dot / qNorm)) else 0.0f

            var prior = 0.0f
            if (sc.intent == predictedIntent) {
                prior += 0.35f
            } else if (sc.domain == sc.domain) {
                prior += 0.15f
            }

            stage1Pool.add(Pair(rawSim + prior, sc))
        }

        stage1Pool.sortByDescending { it.first }
        val topCandidates = stage1Pool.take(12)

        // Stage 2: Linear Weighted Re-Ranker
        val reranked = mutableListOf<ScoredScenario>()

        for ((_, sc) in topCandidates) {
            var dot = 0.0f
            if (qNorm > 0.0f) {
                for (j in sc.sparseIndices.indices) {
                    val scIdx = sc.sparseIndices[j]
                    val qVal = qSparse[scIdx] ?: continue
                    dot += qVal * sc.sparseValues[j]
                }
            }
            val semanticSim = if (qNorm > 0.0f) max(0.0f, min(1.0f, dot / qNorm)) else 0.0f

            val intentMatch = if (sc.intent == predictedIntent) 1.0f else 0.0f
            val subIntentMatch = computeSubIntentAlignment(query, sc.incoming)
            val emotionMatch = if (sc.emotion == predictedEmotion) 1.0f else 0.0f

            val sPronouns = TanglishNormalizer.getPronouns(sc.incoming)
            val pronounAlignment = when {
                qPronouns.isEmpty() && sPronouns.isEmpty() -> 0.8f
                qPronouns.intersect(sPronouns).isNotEmpty() -> 1.0f
                else -> 0.3f
            }

            val sIsQuestion = TanglishNormalizer.isQuestionFormat(sc.incoming)
            val questionMatch = if (qIsQuestion == sIsQuestion) 1.0f else 0.3f
            val lexSim = TanglishNormalizer.computeCharDice(query, sc.incoming)

            // Length-ratio penalty to prevent 1-word scenarios from dominating long queries
            val qWords = query.lowercase().split("\\s+".toRegex()).filter { it.isNotBlank() }
            val sWords = sc.incoming.lowercase().split("\\s+".toRegex()).filter { it.isNotBlank() }
            var lengthPenalty = 0.0f
            if (sWords.size == 1 && qWords.size >= 4) {
                lengthPenalty = 0.20f
            }

            // Polarity modifier (conciliatory markers favor reconciliation)
            val qLower = query.lowercase()
            var polarityModifier = 0.0f
            val isConciliatory = TanglishNormalizer.conciliatoryTokens.any { qLower.contains(it) }
            if (isConciliatory) {
                if (sc.intent in listOf("RECONCILIATION", "APOLOGY_SEEKING")) {
                    polarityModifier += 0.15f
                } else if (sc.intent in listOf("ANGER_ARGUMENT", "CONFLICT_FRUSTRATION")) {
                    polarityModifier -= 0.15f
                }
            }

            // Distress vs Flirt filter (waiting/hurt distress does not match playful questions)
            var distressModifier = 0.0f
            if (predictedEmotion in listOf("HURT", "SAD", "ANXIOUS")) {
                if (sc.emotion in listOf("PLAYFUL", "FLIRTY") || (sc.intent == "MISSING" && sc.incoming.contains("?"))) {
                    distressModifier -= 0.20f
                } else if (sc.emotion in listOf("HURT", "SAD", "ANXIOUS") || sc.intent in listOf("NO_REPLY", "IGNORING", "EMOTIONAL_HURT")) {
                    distressModifier += 0.10f
                }
            }

            val finalScore = (
                0.45f * semanticSim +
                0.20f * intentMatch +
                0.15f * subIntentMatch +
                0.08f * emotionMatch +
                0.05f * pronounAlignment +
                0.04f * questionMatch +
                0.03f * lexSim -
                lengthPenalty +
                polarityModifier +
                distressModifier
            )

            reranked.add(
                ScoredScenario(
                    scenario = sc,
                    score = finalScore * 100.0f,
                    rawSimilarity = semanticSim
                )
            )
        }

        reranked.sortByDescending { it.score }
        return reranked.take(topK)
    }
}
