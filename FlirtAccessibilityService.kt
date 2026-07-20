package com.example.maata

import android.accessibilityservice.AccessibilityService
import android.graphics.PixelFormat
import android.os.Bundle
import android.util.Log
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.Button
import android.widget.Toast

class FlirtAccessibilityService : AccessibilityService() {

    private lateinit var windowManager: WindowManager
    private lateinit var floatingView: View

    override fun onServiceConnected() {
        super.onServiceConnected()
        Log.d("CoupleFriendly", "Accessibility Service Connected")
        setupFloatingOverlay()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // This is called constantly when the screen changes in WhatsApp/Instagram
        // We don't process everything here to save battery.
        // We only parse the screen when the user clicks the floating "Magic Wand" button.
    }

    override fun onInterrupt() {
        Log.d("CoupleFriendly", "Accessibility Service Interrupted")
    }

    override fun onDestroy() {
        super.onDestroy()
        if (::floatingView.isInitialized) {
            windowManager.removeView(floatingView)
        }
    }

    private fun setupFloatingOverlay() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        
        // This requires SYSTEM_ALERT_WINDOW permission
        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )

        params.gravity = Gravity.CENTER_VERTICAL or Gravity.END
        params.x = 0
        params.y = 100

        // For this demo, we create a simple button dynamically.
        // In the real app, this will inflate a Jetpack Compose View or XML layout.
        val button = Button(this).apply {
            text = "✨"
            textSize = 24f
            setOnClickListener {
                Log.d("CoupleFriendly", "Magic Wand Tapped! Reading screen...")
                val chatHistory = readChatBubbles()
                
                // Example: Hardcoded suggestion (In reality, this comes from Groq/Gemini)
                val aiSuggestion = "Sare, phone pettesay, nenu vachi nidrapuchutha. 😉"
                
                // Auto-paste into WhatsApp input field
                pasteTextIntoChat(aiSuggestion)
            }
        }

        floatingView = button
        windowManager.addView(floatingView, params)
    }

    private fun readChatBubbles(): List<String> {
        val rootNode = rootInActiveWindow ?: return emptyList()
        val messages = mutableListOf<String>()

        // Recursively traverse the screen nodes to find text
        fun traverseNodes(node: AccessibilityNodeInfo) {
            if (node.text != null && node.text.isNotEmpty()) {
                val text = node.text.toString()
                // Simple filter to avoid reading buttons like "Type a message"
                if (text != "Type a message" && text != "Message") {
                    messages.add(text)
                }
            }
            for (i in 0 until node.childCount) {
                node.getChild(i)?.let { traverseNodes(it) }
            }
        }

        traverseNodes(rootNode)
        
        Log.d("CoupleFriendly", "Extracted Chat History:")
        messages.forEach { Log.d("CoupleFriendly", "-> $it") }
        
        return messages
    }

    private fun pasteTextIntoChat(replyText: String) {
        val rootNode = rootInActiveWindow ?: return
        
        // WhatsApp input field has the contentDescription "Type a message" or hint "Message"
        val inputNodes = rootNode.findAccessibilityNodeInfosByText("Message")
        
        if (inputNodes.isNotEmpty()) {
            val inputField = inputNodes[0]
            val arguments = Bundle().apply {
                putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, replyText)
            }
            // Execute the paste!
            inputField.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
            Toast.makeText(this, "Reply injected!", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(this, "Could not find chat input field.", Toast.LENGTH_SHORT).show()
        }
    }
}
