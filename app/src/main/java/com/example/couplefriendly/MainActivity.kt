package com.couplefriendly.app

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.couplefriendly.app.ui.theme.CouplefriendlyTheme

class MainActivity : ComponentActivity() {

    private val isOverlayGranted = mutableStateOf(false)
    // Tracks whether the user has seen and accepted the first-launch consent screen
    private val hasUserConsented = mutableStateOf(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        val sharedPrefs = getSharedPreferences("CoupleFriendlyPrefs", Context.MODE_PRIVATE)
        val savedKey = sharedPrefs.getString("api_key", "") ?: ""
        val savedGeminiKey = sharedPrefs.getString("gemini_api_key", "") ?: ""
        
        AiApiClient.setApiKey(savedKey)
        AiApiClient.setGeminiApiKey(savedGeminiKey)
        AiApiClient.initDataset(this)

        // Read persisted consent flag — true means user already agreed on a previous launch
        hasUserConsented.value = sharedPrefs.getBoolean("user_consented", false)

        setContent {
            CouplefriendlyTheme(dynamicColor = false) {
                Scaffold(
                    modifier = Modifier.fillMaxSize(),
                    containerColor = Color(0xFF0D0614)
                ) { innerPadding ->
                    if (!hasUserConsented.value) {
                        // 🔒 FIRST LAUNCH — Show consent/onboarding screen BEFORE anything else
                        ConsentScreen(
                            modifier = Modifier.padding(innerPadding),
                            onUserConsented = {
                                // Persist consent so we never show this screen again
                                sharedPrefs.edit().putBoolean("user_consented", true).apply()
                                hasUserConsented.value = true
                            }
                        )
                    } else {
                        // ✅ RETURNING USER — Show normal setup screen
                        SetupScreen(
                            modifier = Modifier.padding(innerPadding),
                            isOverlayGranted = isOverlayGranted.value,
                            onOpenOverlaySettings = { openOverlaySettings() },
                            onMinimize = { moveTaskToBack(true) },
                            onClose = { finish() }
                        )
                    }
                }
            }
        }
    }

    override fun onResume() {
        super.onResume()
        checkPermissions()
    }

    private fun checkPermissions() {
        isOverlayGranted.value = Settings.canDrawOverlays(this)
    }

    private fun openOverlaySettings() {
        if (!Settings.canDrawOverlays(this)) {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            )
            startActivity(intent)
        } else {
            Toast.makeText(this, "Overlay permission already granted!", Toast.LENGTH_SHORT).show()
        }
    }
}

@Composable
fun SetupScreen(
    modifier: Modifier = Modifier,
    isOverlayGranted: Boolean,
    onOpenOverlaySettings: () -> Unit,
    onMinimize: () -> Unit,
    onClose: () -> Unit
) {
    val scrollState = rememberScrollState()
    val context = androidx.compose.ui.platform.LocalContext.current

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFF0D0614)) // Cyber-Romance Midnight background
            .verticalScroll(scrollState)
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Spacer(modifier = Modifier.height(16.dp))

        // Header (Clean and standard for home screen settings)
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            contentAlignment = Alignment.Center
        ) {
            // App Title
            Text(
                text = "✨ Couple Friendly ✨",
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold,
                style = MaterialTheme.typography.titleLarge.copy(
                    brush = Brush.linearGradient(
                        colors = listOf(Color(0xFFFF2E93), Color(0xFF8A2BE2)) // Neon Rose to Accent Violet
                    )
                )
            )
        }
        
        Spacer(modifier = Modifier.height(4.dp))
        
        // Subtitle (Single, centered, elegant)
        Text(
            text = "Telugu AI Flirting Assistant",
            fontSize = 16.sp,
            fontWeight = FontWeight.Medium,
            color = Color(0xFFA594B8), // Text Secondary
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(bottom = 8.dp)
        )

        // 🚀 LAUNCH / STOP FLOATING OVERLAY BUTTON
        val context = androidx.compose.ui.platform.LocalContext.current
        val isSystemReady = isOverlayGranted

        Button(
            onClick = {
                if (isSystemReady) {
                    FloatingOverlayService.start(context)
                }
            },
            enabled = isSystemReady,
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFFFF2E93),
                disabledContainerColor = Color(0xFF2E1A47)
            ),
            shape = RoundedCornerShape(12.dp),
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp)
                .border(
                    width = 1.dp,
                    brush = Brush.linearGradient(
                        colors = if (isSystemReady) {
                            listOf(Color(0xFFFF2E93), Color(0xFF8A2BE2))
                        } else {
                            listOf(Color(0xFF2E1A47), Color(0xFF2E1A47))
                        }
                    ),
                    shape = RoundedCornerShape(12.dp)
                )
        ) {
            Text(
                text = if (!isSystemReady) "🔒 Grant Overlay Permission First" else "✨ Show Floating Assistant ✨",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = if (isSystemReady) Color.White else Color(0xFFA594B8)
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Overlay Permission Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(
                    width = 1.dp,
                    color = if (isOverlayGranted) Color(0xFF00F5D4) else Color(0xFFFF2E93),
                    shape = RoundedCornerShape(16.dp)
                )
                .clickable { onOpenOverlaySettings() },
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = if (isOverlayGranted) Color(0xFF102620) else Color(0xFF1A0F26)
            )
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "1. Grant Overlay Permission",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color.White
                    )
                    Text(
                        text = "Allows drawing the interactive magic wand overlay button over other apps.",
                        fontSize = 12.sp,
                        color = if (isOverlayGranted) Color(0xFFB8EBE0) else Color(0xFFA594B8),
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }
                
                // Status Pill
                Box(
                    modifier = Modifier
                        .background(
                            color = if (isOverlayGranted) Color(0xFF00F5D4).copy(alpha = 0.2f) else Color(0xFFFF2E93).copy(alpha = 0.2f),
                            shape = RoundedCornerShape(8.dp)
                        )
                        .padding(horizontal = 10.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = if (isOverlayGranted) "Active ✓" else "Setup ➔",
                        color = if (isOverlayGranted) Color(0xFF00F5D4) else Color(0xFFFF2E93),
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Dynamic System Status & Usage Guide Banner
        if (isSystemReady) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .border(
                        width = 2.dp,
                        brush = Brush.linearGradient(colors = listOf(Color(0xFF00F5D4), Color(0xFF8A2BE2))),
                        shape = RoundedCornerShape(16.dp)
                    ),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF102620))
            ) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Text(
                        text = "🎉 System Fully Active! 🚀",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF00F5D4)
                    )
                    
                    Text(
                        text = "Couple Friendly is active and listening for WhatsApp and Instagram chats.",
                        fontSize = 13.sp,
                        color = Color.White,
                        textAlign = TextAlign.Center
                    )

                    HorizontalDivider(color = Color(0xFF00F5D4).copy(alpha = 0.3f), modifier = Modifier.padding(vertical = 4.dp))

                    Text(
                        text = "System Status Check:",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF00F5D4),
                        modifier = Modifier.align(Alignment.Start)
                    )

                    Column(
                        verticalArrangement = Arrangement.spacedBy(6.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("✓", color = Color(0xFF00F5D4), fontWeight = FontWeight.Bold, modifier = Modifier.width(20.dp))
                            Text("Screen Overlay Permission active", color = Color.White, fontSize = 12.sp)
                        }
                    }

                    HorizontalDivider(color = Color(0xFF00F5D4).copy(alpha = 0.3f), modifier = Modifier.padding(vertical = 4.dp))

                    Text(
                        text = "How to use:",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF00F5D4),
                        modifier = Modifier.align(Alignment.Start)
                    )

                    Column(
                        verticalArrangement = Arrangement.spacedBy(6.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("1. Tap ✨ Show Floating Assistant to launch the overlay.", fontSize = 12.sp, color = Color.White)
                        Text("2. A floating ✨ bubble will appear on screen.", fontSize = 12.sp, color = Color.White)
                        Text("3. Open WhatsApp or Instagram — tap the bubble when you get a message.", fontSize = 12.sp, color = Color.White)
                        Text("4. Type what they said, pick a tone, tap a reply to copy it.", fontSize = 12.sp, color = Color.White)
                        Text("5. Paste it in your chat and send! 😍", fontSize = 12.sp, color = Color.White)
                    }
                }
            }


        } else {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF26101F))
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "⏳ Setup Incomplete",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFFFF2E93)
                    )
                    
                    Text(
                        text = "Please complete the setup step highlighted in red above to activate the floating assistant overlay.",
                        fontSize = 12.sp,
                        color = Color(0xFFA594B8)
                    )

                    Spacer(modifier = Modifier.height(4.dp))

                    // Checklist
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = if (isOverlayGranted) "✓" else "✗",
                            color = if (isOverlayGranted) Color(0xFF00F5D4) else Color(0xFFFF2E93),
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.width(20.dp)
                        )
                        Text(
                            text = "Overlay Permission granted",
                            color = if (isOverlayGranted) Color.White else Color(0xFFA594B8),
                            fontSize = 12.sp
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // 🛠️ DEVELOPER SETTINGS CARD
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(
                    width = 1.dp,
                    color = Color(0xFF8A2BE2).copy(alpha = 0.5f),
                    shape = RoundedCornerShape(16.dp)
                ),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E142B))
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "ℹ️ How it works",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF00F5D4)
                )
                Text(
                    text = "AI replies are generated via a secure cloud server. No API keys needed on your device.",
                    fontSize = 12.sp,
                    color = Color(0xFFA594B8)
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
    }
}

@Preview(showBackground = true, backgroundColor = 0xFF0D0614)
@Composable
fun SetupScreenPendingPreview() {
    CouplefriendlyTheme(dynamicColor = false) {
        SetupScreen(
            isOverlayGranted = false,
            onOpenOverlaySettings = {},
            onMinimize = {},
            onClose = {}
        )
    }
}

@Preview(showBackground = true, backgroundColor = 0xFF0D0614)
@Composable
fun SetupScreenActivePreview() {
    CouplefriendlyTheme(dynamicColor = false) {
        SetupScreen(
            isOverlayGranted = true,
            onOpenOverlaySettings = {},
            onMinimize = {},
            onClose = {}
        )
    }
}