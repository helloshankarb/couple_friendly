package com.couplefriendly.app.ml

import android.content.Context
import org.json.JSONObject
import java.io.InputStream
import kotlin.math.exp
import kotlin.math.ln
import kotlin.math.sqrt

/**
 * High-performance on-device Linear N-gram Classifier (Word 1-2 + Char 3-5).
 * Executes feature extraction, sublinear TF-IDF, sparse dot-product, and calibrated Softmax in < 1ms.
 */
internal class LinearNgramClassifier(val modelName: String) {

    private var classes: List<String> = emptyList()
    private var intercepts: FloatArray = FloatArray(0)
    private var numWordFeatures: Int = 0
    private var numCharFeatures: Int = 0

    private var wordVocab: Map<String, Int> = emptyMap()
    private var wordIdf: FloatArray = FloatArray(0)

    private var charVocab: Map<String, Int> = emptyMap()
    private var charIdf: FloatArray = FloatArray(0)

    // Coefficients stored as Array<FloatArray>: [classIndex][featureIndex]
    private var coefficients: Array<FloatArray> = emptyArray()
    var isLoaded: Boolean = false
        private set

    fun loadFromAsset(context: Context, assetPath: String) {
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
        val root = JSONObject(jsonStr)

        val classesArray = root.getJSONArray("classes")
        val classesList = mutableListOf<String>()
        for (i in 0 until classesArray.length()) {
            classesList.add(classesArray.getString(i))
        }
        this.classes = classesList

        val interArray = root.getJSONArray("intercepts")
        val interFloats = FloatArray(interArray.length())
        for (i in 0 until interArray.length()) {
            interFloats[i] = interArray.getDouble(i).toFloat()
        }
        this.intercepts = interFloats

        this.numWordFeatures = root.getInt("num_word_features")
        this.numCharFeatures = root.getInt("num_char_features")

        val wVocabObj = root.getJSONObject("word_vocab")
        val wVocabMap = HashMap<String, Int>(wVocabObj.length())
        val wKeys = wVocabObj.keys()
        while (wKeys.hasNext()) {
            val k = wKeys.next()
            wVocabMap[k] = wVocabObj.getInt(k)
        }
        this.wordVocab = wVocabMap

        val wIdfArray = root.getJSONArray("word_idf")
        val wIdfFloats = FloatArray(wIdfArray.length())
        for (i in 0 until wIdfArray.length()) {
            wIdfFloats[i] = wIdfArray.getDouble(i).toFloat()
        }
        this.wordIdf = wIdfFloats

        val cVocabObj = root.getJSONObject("char_vocab")
        val cVocabMap = HashMap<String, Int>(cVocabObj.length())
        val cKeys = cVocabObj.keys()
        while (cKeys.hasNext()) {
            val k = cKeys.next()
            cVocabMap[k] = cVocabObj.getInt(k)
        }
        this.charVocab = cVocabMap

        val cIdfArray = root.getJSONArray("char_idf")
        val cIdfFloats = FloatArray(cIdfArray.length())
        for (i in 0 until cIdfArray.length()) {
            cIdfFloats[i] = cIdfArray.getDouble(i).toFloat()
        }
        this.charIdf = cIdfFloats

        val coefArray = root.getJSONArray("coefficients")
        val numClasses = coefArray.length()
        val coefMatrix = Array(numClasses) { FloatArray(numWordFeatures + numCharFeatures) }

        for (c in 0 until numClasses) {
            val classRow = coefArray.getJSONArray(c)
            val rowLen = classRow.length()
            val targetRow = coefMatrix[c]
            for (f in 0 until rowLen) {
                targetRow[f] = classRow.getDouble(f).toFloat()
            }
        }
        this.coefficients = coefMatrix
        this.isLoaded = true
    }

    /**
     * Extracts active word (1-2) and character (3-5) n-grams and computes L2-normalized TF-IDF sparse features.
     * Returns: Map of globalFeatureIndex -> normalizedTfIdfValue
     */
    fun extractSparseFeatures(text: String): Map<Int, Float> {
        val sparse = mutableMapOf<Int, Float>()
        if (text.isBlank()) return sparse

        val clean = text.lowercase().trim()

        // 1. Word (1-2) n-grams
        val tokens = clean.split("\\s+".toRegex()).filter { it.isNotBlank() }
        val wordCounts = mutableMapOf<String, Int>()
        for (i in tokens.indices) {
            val unigram = tokens[i]
            wordCounts[unigram] = (wordCounts[unigram] ?: 0) + 1
            if (i + 1 < tokens.size) {
                val bigram = "$unigram ${tokens[i + 1]}"
                wordCounts[bigram] = (wordCounts[bigram] ?: 0) + 1
            }
        }

        val activeWordFeats = mutableMapOf<Int, Float>()
        var wordSumSq = 0.0f
        for ((ngram, count) in wordCounts) {
            val featIdx = wordVocab[ngram] ?: continue
            val idf = if (featIdx < wordIdf.size) wordIdf[featIdx] else 1.0f
            val tf = 1.0f + ln(count.toDouble()).toFloat()
            val rawVal = tf * idf
            activeWordFeats[featIdx] = rawVal
            wordSumSq += rawVal * rawVal
        }

        val wordL2 = sqrt(wordSumSq)
        if (wordL2 > 0.0f) {
            for ((featIdx, rawVal) in activeWordFeats) {
                sparse[featIdx] = rawVal / wordL2
            }
        }

        // 2. Character (3-5) n-grams
        val charCounts = mutableMapOf<String, Int>()
        for (n in 3..5) {
            if (clean.length >= n) {
                for (i in 0..(clean.length - n)) {
                    val charNgram = clean.substring(i, i + n)
                    charCounts[charNgram] = (charCounts[charNgram] ?: 0) + 1
                }
            }
        }

        val activeCharFeats = mutableMapOf<Int, Float>()
        var charSumSq = 0.0f
        for ((ngram, count) in charCounts) {
            val featIdx = charVocab[ngram] ?: continue
            val idf = if (featIdx < charIdf.size) charIdf[featIdx] else 1.0f
            val tf = 1.0f + ln(count.toDouble()).toFloat()
            val rawVal = tf * idf
            activeCharFeats[featIdx] = rawVal
            charSumSq += rawVal * rawVal
        }

        val charL2 = sqrt(charSumSq)
        if (charL2 > 0.0f) {
            for ((featIdx, rawVal) in activeCharFeats) {
                val globalIdx = numWordFeatures + featIdx
                sparse[globalIdx] = rawVal / charL2
            }
        }

        return sparse
    }

    /**
     * Performs forward inference: computes logits = intercepts + dot(weights, sparseX),
     * applies Softmax, and returns the top label with confidence.
     */
    fun predict(text: String): ClassifierOutput {
        if (!isLoaded || classes.isEmpty()) {
            return ClassifierOutput("GENERAL", 0.5f, emptyMap())
        }

        val sparse = extractSparseFeatures(text)
        val numClasses = classes.size
        val logits = FloatArray(numClasses)

        for (c in 0 until numClasses) {
            var logit = if (c < intercepts.size) intercepts[c] else 0.0f
            val weights = coefficients[c]
            for ((featIdx, featVal) in sparse) {
                if (featIdx < weights.size) {
                    logit += featVal * weights[featIdx]
                }
            }
            logits[c] = logit
        }

        // Softmax with numerical stability (subtract max)
        var maxLogit = Float.NEGATIVE_INFINITY
        for (logit in logits) {
            if (logit > maxLogit) maxLogit = logit
        }

        val expValues = FloatArray(numClasses)
        var sumExp = 0.0f
        for (i in 0 until numClasses) {
            val v = exp(logits[i] - maxLogit)
            expValues[i] = v
            sumExp += v
        }

        var topClassIdx = 0
        var topProb = 0.0f
        val probMap = mutableMapOf<String, Float>()

        for (i in 0 until numClasses) {
            val prob = if (sumExp > 0.0f) expValues[i] / sumExp else 0.0f
            val cls = classes[i]
            probMap[cls] = prob
            if (prob > topProb) {
                topProb = prob
                topClassIdx = i
            }
        }

        return ClassifierOutput(
            label = classes[topClassIdx],
            confidence = topProb,
            probabilities = probMap
        )
    }
}
