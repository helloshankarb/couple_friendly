# Product Requirements Document (PRD) — Telugu AI Flirting Assistant

## 1. Product Overview
**Name:** (To be decided - e.g., "Maata", "FlirtAI Telugu")
**Platform:** Native Android (Kotlin)
**Core Concept:** A floating Android overlay assistant that reads WhatsApp/Instagram chats via Accessibility Services and suggests contextual, natural-sounding Telugu flirting replies using LLMs.
**Key Differentiator:** No copy-pasting, no screenshots. 100% automated floating UI. Culturally rich Telugu dataset ('nuvvu' informal tone).

## 2. Technical Stack (The Recommended Choice)
*   **App Framework:** Native Android (Kotlin / Java) 🏆
    *   *Why not React Native/Expo?* React Native struggles with the "firehose" of accessibility events and background floating UI (`SYSTEM_ALERT_WINDOW`), leading to extreme battery drain, UI freezes, and crashes. Native Kotlin provides a lag-free, battery-efficient system integration.
*   **UI Toolkit:** Jetpack Compose (for the floating UI and settings screens).
*   **AI Engine:** Groq API (Llama 3.3) for primary ultra-fast inference / Google Gemini Flash for fallback.
*   **Data Storage:** Android Room / SharedPreferences (for API keys, preferences, local prompts).

## 3. Core Mechanisms

### 3.1 Screen Reading (AccessibilityService)
*   The app requests the `BIND_ACCESSIBILITY_SERVICE` permission.
*   When active, it scans `AccessibilityNodeInfo` to extract text from chat bubbles.
*   It distinguishes between "User" (outgoing) and "Her" (incoming) messages based on node hierarchy, alignment, or sender names.

### 3.2 Floating Overlay (System Alert Window)
*   The app uses `SYSTEM_ALERT_WINDOW` to draw a floating "Magic Wand" icon over messaging apps.
*   When tapped, the wand expands into a minimal bottom sheet or chat bubble showing 3 generated reply options.
*   Clicking an option triggers `ACTION_SET_TEXT` to automatically paste the text into the WhatsApp/Instagram input field.

## 4. Prompt Engineering Architecture

To ensure the AI doesn't get confused and replies ONLY to the most recent message while retaining full context, the prompt is structured into distinct blocks before being sent to the LLM.

### 4.1 The Prompt Template

```text
[SYSTEM INSTRUCTION]
You are a witty and romantic Telugu flirting assistant. 
Below is a chat conversation between a boy (User) and his girlfriend (Her). 
Use the "CHAT HISTORY" only to understand the mood, context, and what they are talking about. 
Your task is to generate 3 short, natural Telugu replies ONLY to the "LATEST MESSAGE". 
Do not reply to the older messages. Keep the tone casual (use 'nuvvu').

[CHAT HISTORY]
{DYNAMIC_HISTORY_EXTRACTED_BY_ACCESSIBILITY}
(e.g., User: Emaindi, silent ga unnav? -> Her: Emi ledu, just tired. -> User: Work ekuva aindha eroju?)

[LATEST MESSAGE]
{DYNAMIC_LATEST_MESSAGE_EXTRACTED_BY_ACCESSIBILITY}
(e.g., Her: Avunu, full stress. Nidrostundi.)

[YOUR TASK]
Generate 3 reply options for the User to respond to the LATEST MESSAGE.
```

### 4.2 Why this structure?
1. **Context Awareness:** The AI reads the history to understand she is stressed from work.
2. **Target Isolation:** The AI knows its only job is to reply to the final *"Avunu, full stress..."* message.
3. **Flirty Output:** The AI generates relevant responses (e.g., *"Sare, phone pettesay, nenu vachi nidrapuchutha. 😉"*).

## 5. Development Setup & Architecture

### 5.1 Project Initialization
1.  Open Android Studio.
2.  Create New Project -> "Empty Compose Activity" (Kotlin).
3.  Minimum SDK: API 26 (Android 8.0) - recommended for modern overlay support.

### 5.2 Core Components Needed
1.  **`FlirtAccessibilityService.kt`**: Extends `AccessibilityService`. 
    *   Listens for `TYPE_WINDOW_CONTENT_CHANGED`.
    *   Parses the View hierarchy to extract chat text.
    *   Injects text back using `AccessibilityNodeInfo.ACTION_SET_TEXT`.
2.  **`FloatingOverlayManager.kt`**: 
    *   Manages the `WindowManager.LayoutParams` (TYPE_APPLICATION_OVERLAY).
    *   Renders the Jetpack Compose view for the magic wand and suggestion list.
3.  **`AiApiClient.kt`**: 
    *   Uses Retrofit or OkHttp to send the structured prompt to Groq/Gemini API.
4.  **`MainActivity.kt`**: 
    *   The settings screen.
    *   Handles permission requests (Accessibility + Overlay).
    *   Allows the user to paste their API key or select flirting tone (Funny, Sweet, Naughty).

## 5. 🎨 Premium UI/UX Design System

To ensure a premium, modern, and youthful look, the app must avoid generic Android UI components. It should feel like a premium utility app with rich micro-animations, smooth transitions, and distinct styling.

### 5.1 Color Palette & Theme (Cyber-Romance Vibe)
The app uses a dark-mode-first aesthetic with romantic, neon-tinged color accents.

| Token | Hex Value | Role |
| :--- | :--- | :--- |
| **Primary Midnight** | `#0D0614` | Main application background (Very deep dark plum) |
| **Surface Dark** | `#1A0F26` | Card and sheet backgrounds |
| **Accent Rose** | `#FF2E93` | Call-to-actions, romantic states, glowing borders |
| **Accent Violet** | `#8A2BE2` | AI features, active selections, wizard progress |
| **Success Emerald** | `#00F5D4` | Permission granted states, success indicators |
| **Text Primary** | `#FFFFFF` | Core reading text |
| **Text Secondary** | `#A594B8` | Subtitles and hints |

### 5.2 The Floating Overlay UI/UX (The Magic Wand)
The overlay is the primary point of user interaction. It must be unobtrusive, beautiful, and highly responsive.

```
[Normal Idle State]          [Expanded Suggestion State]
   ┌──────┐                   ┌────────────────────────────────────────┐
   │  ✨  │◄─ Drag/Tap        │  ✨ Maata AI                           │
   └──────┘                   ├────────────────────────────────────────┤
 (Glow pulse)                 │  Select a reply to paste:              │
                              │ ┌────────────────────────────────────┐ │
                              │ │ 1. Sare, nenu vachi nidrapuchutha. │ │
                              │ └────────────────────────────────────┘ │
                              │ ┌────────────────────────────────────┐ │
                              │ │ 2. Dreams lo nene vastha ready ga..│ │
                              │ └────────────────────────────────────┘ │
                              │  [ Tone: Romantic 💘 ] [ Refresh 🔄 ]  │
                              └────────────────────────────────────────┘
```

*   **Idle Overlay Badge:** A tiny floating pill with a circular background gradient (Rose-to-Violet) and a pulsing neon "✨" glow animation. If idle for 5 seconds, its opacity drops to `40%` and it snaps semi-transparently to the nearest screen edge.
*   **Expansion Physics:** Tapping the idle badge triggers a bouncy spring animation (using Jetpack Compose standard physics) expanding it into a sleek, glassmorphic card containing 3 generated replies.
*   **Selection State:** Tapping a reply option shows a ripple wave effect across the card, followed by a checkmark scale animation, after which the card auto-collapses.

### 5.3 Settings & Setup Screen UI
The main configuration screen uses large, high-fidelity interactive elements for permission management.

*   **Permission Cards:** 
    *   Instead of standard checkboxes, permissions are managed via custom, high-contrast toggle cards.
    *   *State "Off":* Card is greyed out, border is dotted.
    *   *State "On":* Card lights up, border glows with `Success Emerald` (`#00F5D4`), and a checked shield icon bounces into view.
*   **Tone Selector Dial:** 
    *   An interactive, horizontal scroll wheel for choosing the flirtation tone:
        *   **Funny 🤭** (Yellow theme)
        *   **Sweet 🥰** (Soft Pink theme)
        *   **Romantic 💘** (Neon Rose theme)
        *   **Bold/Naughty 🔥** (Crimson Red theme)
    *   Changing the tone dynamically shifts the accent background glow of the main UI, giving a highly interactive and sensory response.

---

## 6. Permissions Required
*   `android.permission.INTERNET` (For API calls)
*   `android.permission.SYSTEM_ALERT_WINDOW` (For floating UI)
*   `android.permission.BIND_ACCESSIBILITY_SERVICE` (For reading/writing text)

## 7. Next Steps for Implementation
1.  **Phase 1: Foundation.** Initialize Android Studio project and create the basic Floating View (`SYSTEM_ALERT_WINDOW`).
2.  **Phase 2: Screen Reader.** Implement `FlirtAccessibilityService.kt` to successfully extract the last 5 messages from WhatsApp and print them to the Android Logcat.
3.  **Phase 3: Prompt Injection.** Format the extracted messages into the Prompt Template and send them to the Groq/Gemini API.
4.  **Phase 4: Auto-Paste.** Display the API response in the floating view. When tapped, use the Accessibility Service to paste it into the chat input field.
5.  **Phase 5: Polish.** Add animations, tone selection, and error handling.
