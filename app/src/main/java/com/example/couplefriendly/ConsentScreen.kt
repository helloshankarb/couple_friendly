package com.couplefriendly.app

import androidx.compose.foundation.background
import androidx.compose.foundation.border
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

/**
 * First-launch consent/onboarding screen.
 *
 * Shown ONCE on first install. The user must explicitly tap "I Understand, Continue"
 * before the app does anything. This satisfies Google Play's opt-in requirement for
 * apps that use SYSTEM_ALERT_WINDOW (Draw Over Other Apps) and Accessibility Service.
 *
 * After the user consents, the flag is persisted in SharedPreferences and this
 * screen is never shown again.
 */
@Composable
fun ConsentScreen(
    modifier: Modifier = Modifier,
    onUserConsented: () -> Unit
) {
    val scrollState = rememberScrollState()

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(Color(0xFF0D0614))
            .verticalScroll(scrollState)
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        Spacer(modifier = Modifier.height(16.dp))

        // App Icon / Emoji
        Text(
            text = "✨",
            fontSize = 56.sp,
            textAlign = TextAlign.Center
        )

        // Title
        Text(
            text = "Welcome to\nCouple Friendly",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            style = MaterialTheme.typography.titleLarge.copy(
                brush = Brush.linearGradient(
                    colors = listOf(Color(0xFFFF2E93), Color(0xFF8A2BE2))
                )
            )
        )

        // Subtitle
        Text(
            text = "Before you start, please read how this app works and what permissions it needs.",
            fontSize = 14.sp,
            color = Color(0xFFA594B8),
            textAlign = TextAlign.Center
        )

        HorizontalDivider(
            color = Color(0xFF2E1A47),
            modifier = Modifier.padding(vertical = 4.dp)
        )

        // ── What This App Does ───────────────────────────────────────
        ConsentSection(
            emoji = "💬",
            title = "What this app does",
            body = "Couple Friendly shows a small floating button on your screen while you use WhatsApp or Instagram. When you tap it, the app reads the latest visible message on screen and generates 3 flirty Telugu reply suggestions for you to choose from."
        )

        // ── Overlay Permission ────────────────────────────────────────
        ConsentSection(
            emoji = "🪟",
            title = "Permission 1 — Display Over Other Apps",
            body = "This allows the floating ✨ button to appear on top of WhatsApp and Instagram. Without this, the overlay cannot be shown.\n\nYou will be taken to Android's own Settings screen to grant this. You are in full control."
        )

        // ── Accessibility Service ─────────────────────────────────────
        ConsentSection(
            emoji = "♿",
            title = "Permission 2 — Accessibility Service",
            body = "This allows the app to read the text currently visible on your screen (the incoming chat message) so it can generate a relevant reply.\n\n⚠️ This app does NOT store, upload, or share any of your chat messages. All processing happens on your device or via the AI API you configure."
        )

        // ── What We Do NOT Do ─────────────────────────────────────────
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .border(
                    width = 1.dp,
                    color = Color(0xFF00F5D4).copy(alpha = 0.4f),
                    shape = RoundedCornerShape(12.dp)
                ),
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF0D2620))
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "✅ Our Privacy Commitments",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF00F5D4)
                )
                PrivacyPoint("We do NOT read or store your private messages")
                PrivacyPoint("We do NOT access your contacts, camera, or microphone")
                PrivacyPoint("We do NOT run in the background without your knowledge")
                PrivacyPoint("You can revoke any permission from Android Settings at any time")
                PrivacyPoint("The overlay only appears when you manually tap the floating button")
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // ── Consent Button ────────────────────────────────────────────
        Button(
            onClick = onUserConsented,
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFF2E93)),
            shape = RoundedCornerShape(12.dp),
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp)
        ) {
            Text(
                text = "I Understand, Continue ➔",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
        }

        // Fine print
        Text(
            text = "By tapping Continue, you agree to grant the permissions described above when prompted. You can change these at any time in Android Settings.",
            fontSize = 11.sp,
            color = Color(0xFF6B5C7E),
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(bottom = 24.dp)
        )
    }
}

@Composable
private fun ConsentSection(emoji: String, title: String, body: String) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .border(
                width = 1.dp,
                color = Color(0xFF2E1A47),
                shape = RoundedCornerShape(12.dp)
            ),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1A0F26))
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = emoji, fontSize = 20.sp)
                Text(
                    text = title,
                    fontSize = 15.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = Color.White
                )
            }
            Text(
                text = body,
                fontSize = 13.sp,
                color = Color(0xFFA594B8),
                lineHeight = 20.sp
            )
        }
    }
}

@Composable
private fun PrivacyPoint(text: String) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.Top
    ) {
        Text(
            text = "•",
            fontSize = 13.sp,
            color = Color(0xFF00F5D4),
            modifier = Modifier.padding(top = 1.dp)
        )
        Text(
            text = text,
            fontSize = 13.sp,
            color = Color(0xFFB8EBE0)
        )
    }
}
