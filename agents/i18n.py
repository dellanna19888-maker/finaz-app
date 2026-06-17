"""
Mehrsprachigkeit: DE, EN, IT, ES
Der Bot erkennt die Sprache automatisch per Telegram-Einstellung.
"""

TEXTS = {
    "de": {
        "start": (
            "🚀 Willkommen beim *Creator Growth System*!\n\n"
            "👉 Kostenlose Demo: /demo\n"
            "👉 Vollständige Analyse: /analyse\n\n"
            "Die vollständige Analyse liefert:\n"
            "📊 Profil-Analyse\n📈 30-Tage-Wachstumsplan\n💰 Monetisierungs-Strategie\n"
            "🎬 Content-Ideen\n✉️ DM-Vorlagen\n#️⃣ Hashtag-Strategie\n🔍 Konkurrenz-Analyse\n📄 Download-Datei"
        ),
        "demo_title": "🎯 *GRATIS DEMO – Creator Analyse*",
        "demo_intro": (
            "In 10 Sekunden bekommst du:\n"
            "📊 Deine Profil-Analyse\n🎬 3 virale Content-Ideen\n#️⃣ 15 Hashtags\n\nWähle deine Nische:"
        ),
        "demo_running": "⚡ Starte Demo-Analyse für *{}*...",
        "demo_done": "✅ *Demo-Analyse für {}*",
        "demo_upsell": (
            "━━━━━━━━━━━━━━━━━━\n"
            "🔒 *Das war die GRATIS Demo!*\n\n"
            "Die vollständige Analyse enthält zusätzlich:\n"
            "📈 30-Tage-Wachstumsplan\n💰 Monetisierungs-Strategie\n"
            "✉️ DM-Vorlagen\n🔍 Konkurrenz-Analyse\n📄 Download-Datei\n\n"
            "👇 Starte jetzt die vollständige Analyse:"
        ),
        "vollversion_btn": "🚀 Vollständige Analyse starten",
        "analyse_step1": "🎯 *Schritt 1/6 – Deine Nische*\n\nWähle eine Nische oder tippe deine eigene:",
        "analyse_running": "⚡ Alle 7 Analysen starten gleichzeitig...",
        "analyse_done": "✅ *Analyse abgeschlossen!*\n\nWie hilfreich war die Analyse?",
        "analyse_wait": "⏳ Analyse läuft... Das dauert ca. 20 Sekunden.",
        "rating_thanks": "Danke! Neue Analyse? Tippe /analyse",
        "q_tiktok": "📱 Wie viele TikTok-Follower hast du? (z.B. 1200, oder 0)",
        "q_instagram": "📸 Wie viele Instagram-Follower hast du? (z.B. 800, oder 0)",
        "q_posting": "📅 Wie oft postest du pro Woche? (z.B. 3)",
        "q_problem": "❓ Was ist dein größtes Problem als Creator?",
        "q_konkurrenz": "🔍 Wer ist dein größter Konkurrent? (z.B. @fitness_max oder 'kein')",
        "enter_nische": "✏️ Gib deine Nische ein:",
        "hilfe": (
            "*Creator Growth Bot – Hilfe*\n\n"
            "/demo – Kostenlose Demo (10 Sekunden)\n"
            "/analyse – Vollständige 7-Schritt-Analyse\n"
            "/sprache – Sprache ändern\n"
            "/start – Startmenü\n\n"
            "💡 *Tipp:* Starte mit /demo!"
        ),
        "sprache_waehlen": "🌍 Wähle deine Sprache / Choose your language:",
        "sprache_gesetzt": "✅ Sprache: Deutsch",
        "file_caption": "📄 Deine vollständige Analyse vom {}",
        "nischen": ["🏋️ Fitness", "💰 Finanzen", "💄 Beauty", "🎮 Gaming", "🍳 Kochen", "✈️ Reisen", "📸 Fotografie", "🎵 Musik", "💻 Tech", "✍️ Andere eingeben"],
        "ai_language": "Deutsch",
    },
    "en": {
        "start": (
            "🚀 Welcome to *Creator Growth System*!\n\n"
            "👉 Free Demo: /demo\n"
            "👉 Full Analysis: /analyse\n\n"
            "Full analysis includes:\n"
            "📊 Profile Analysis\n📈 30-Day Growth Plan\n💰 Monetization Strategy\n"
            "🎬 Content Ideas\n✉️ DM Templates\n#️⃣ Hashtag Strategy\n🔍 Competitor Analysis\n📄 Download File"
        ),
        "demo_title": "🎯 *FREE DEMO – Creator Analysis*",
        "demo_intro": (
            "In 10 seconds you get:\n"
            "📊 Your Profile Analysis\n🎬 3 viral Content Ideas\n#️⃣ 15 Hashtags\n\nChoose your niche:"
        ),
        "demo_running": "⚡ Starting demo analysis for *{}*...",
        "demo_done": "✅ *Demo Analysis for {}*",
        "demo_upsell": (
            "━━━━━━━━━━━━━━━━━━\n"
            "🔒 *That was the FREE Demo!*\n\n"
            "The full analysis also includes:\n"
            "📈 30-Day Growth Plan\n💰 Monetization Strategy\n"
            "✉️ DM Templates\n🔍 Competitor Analysis\n📄 Download File\n\n"
            "👇 Start your full analysis now:"
        ),
        "vollversion_btn": "🚀 Start Full Analysis",
        "analyse_step1": "🎯 *Step 1/6 – Your Niche*\n\nChoose a niche or type your own:",
        "analyse_running": "⚡ Starting all 7 analyses simultaneously...",
        "analyse_done": "✅ *Analysis complete!*\n\nHow helpful was the analysis?",
        "analyse_wait": "⏳ Analysis running... takes about 20 seconds.",
        "rating_thanks": "Thanks! New analysis? Type /analyse",
        "q_tiktok": "📱 How many TikTok followers do you have? (e.g. 1200, or 0)",
        "q_instagram": "📸 How many Instagram followers do you have? (e.g. 800, or 0)",
        "q_posting": "📅 How often do you post per week? (e.g. 3)",
        "q_problem": "❓ What is your biggest challenge as a creator?",
        "q_konkurrenz": "🔍 Who is your biggest competitor? (e.g. @fitness_max or 'none')",
        "enter_nische": "✏️ Enter your niche:",
        "hilfe": (
            "*Creator Growth Bot – Help*\n\n"
            "/demo – Free Demo (10 seconds)\n"
            "/analyse – Full 7-step analysis\n"
            "/sprache – Change language\n"
            "/start – Main menu\n\n"
            "💡 *Tip:* Start with /demo!"
        ),
        "sprache_waehlen": "🌍 Wähle deine Sprache / Choose your language:",
        "sprache_gesetzt": "✅ Language: English",
        "file_caption": "📄 Your complete analysis from {}",
        "nischen": ["🏋️ Fitness", "💰 Finance", "💄 Beauty", "🎮 Gaming", "🍳 Cooking", "✈️ Travel", "📸 Photography", "🎵 Music", "💻 Tech", "✍️ Enter custom"],
        "ai_language": "English",
    },
    "it": {
        "start": (
            "🚀 Benvenuto nel *Creator Growth System*!\n\n"
            "👉 Demo gratuita: /demo\n"
            "👉 Analisi completa: /analyse\n\n"
            "L'analisi completa include:\n"
            "📊 Analisi Profilo\n📈 Piano Crescita 30 giorni\n💰 Strategia Monetizzazione\n"
            "🎬 Idee Contenuti\n✉️ Modelli DM\n#️⃣ Strategia Hashtag\n🔍 Analisi Concorrenza\n📄 File Download"
        ),
        "demo_title": "🎯 *DEMO GRATUITA – Analisi Creator*",
        "demo_intro": (
            "In 10 secondi ricevi:\n"
            "📊 Analisi del tuo profilo\n🎬 3 idee di contenuto virali\n#️⃣ 15 Hashtag\n\nScegli la tua nicchia:"
        ),
        "demo_running": "⚡ Avvio analisi demo per *{}*...",
        "demo_done": "✅ *Analisi Demo per {}*",
        "demo_upsell": (
            "━━━━━━━━━━━━━━━━━━\n"
            "🔒 *Questa era la Demo GRATUITA!*\n\n"
            "L'analisi completa include anche:\n"
            "📈 Piano Crescita 30 giorni\n💰 Strategia Monetizzazione\n"
            "✉️ Modelli DM\n🔍 Analisi Concorrenza\n📄 File Download\n\n"
            "👇 Inizia ora l'analisi completa:"
        ),
        "vollversion_btn": "🚀 Inizia Analisi Completa",
        "analyse_step1": "🎯 *Passo 1/6 – La tua nicchia*\n\nScegli una nicchia o digita la tua:",
        "analyse_running": "⚡ Avvio di tutte e 7 le analisi contemporaneamente...",
        "analyse_done": "✅ *Analisi completata!*\n\nQuanto è stata utile l'analisi?",
        "analyse_wait": "⏳ Analisi in corso... circa 20 secondi.",
        "rating_thanks": "Grazie! Nuova analisi? Scrivi /analyse",
        "q_tiktok": "📱 Quanti follower hai su TikTok? (es. 1200, o 0)",
        "q_instagram": "📸 Quanti follower hai su Instagram? (es. 800, o 0)",
        "q_posting": "📅 Quante volte pubblichi a settimana? (es. 3)",
        "q_problem": "❓ Qual è il tuo problema principale come creator?",
        "q_konkurrenz": "🔍 Chi è il tuo principale concorrente? (es. @fitness_max o 'nessuno')",
        "enter_nische": "✏️ Inserisci la tua nicchia:",
        "hilfe": (
            "*Creator Growth Bot – Aiuto*\n\n"
            "/demo – Demo gratuita (10 secondi)\n"
            "/analyse – Analisi completa in 7 passi\n"
            "/sprache – Cambia lingua\n"
            "/start – Menu principale\n\n"
            "💡 *Consiglio:* Inizia con /demo!"
        ),
        "sprache_waehlen": "🌍 Wähle deine Sprache / Choose your language:",
        "sprache_gesetzt": "✅ Lingua: Italiano",
        "file_caption": "📄 La tua analisi completa del {}",
        "nischen": ["🏋️ Fitness", "💰 Finanza", "💄 Beauty", "🎮 Gaming", "🍳 Cucina", "✈️ Viaggi", "📸 Fotografia", "🎵 Musica", "💻 Tech", "✍️ Inserisci personalizzata"],
        "ai_language": "Italian",
    },
    "es": {
        "start": (
            "🚀 ¡Bienvenido al *Creator Growth System*!\n\n"
            "👉 Demo gratuito: /demo\n"
            "👉 Análisis completo: /analyse\n\n"
            "El análisis completo incluye:\n"
            "📊 Análisis de Perfil\n📈 Plan de Crecimiento 30 días\n💰 Estrategia de Monetización\n"
            "🎬 Ideas de Contenido\n✉️ Plantillas DM\n#️⃣ Estrategia Hashtag\n🔍 Análisis Competencia\n📄 Archivo Descarga"
        ),
        "demo_title": "🎯 *DEMO GRATIS – Análisis Creator*",
        "demo_intro": (
            "En 10 segundos recibes:\n"
            "📊 Tu Análisis de Perfil\n🎬 3 ideas de contenido virales\n#️⃣ 15 Hashtags\n\nElige tu nicho:"
        ),
        "demo_running": "⚡ Iniciando análisis demo para *{}*...",
        "demo_done": "✅ *Análisis Demo para {}*",
        "demo_upsell": (
            "━━━━━━━━━━━━━━━━━━\n"
            "🔒 *¡Eso fue el Demo GRATIS!*\n\n"
            "El análisis completo también incluye:\n"
            "📈 Plan de Crecimiento 30 días\n💰 Estrategia de Monetización\n"
            "✉️ Plantillas DM\n🔍 Análisis Competencia\n📄 Archivo Descarga\n\n"
            "👇 Inicia tu análisis completo ahora:"
        ),
        "vollversion_btn": "🚀 Iniciar Análisis Completo",
        "analyse_step1": "🎯 *Paso 1/6 – Tu nicho*\n\nElige un nicho o escribe el tuyo:",
        "analyse_running": "⚡ Iniciando los 7 análisis simultáneamente...",
        "analyse_done": "✅ *¡Análisis completado!*\n\n¿Qué tan útil fue el análisis?",
        "analyse_wait": "⏳ Análisis en curso... unos 20 segundos.",
        "rating_thanks": "¡Gracias! ¿Nuevo análisis? Escribe /analyse",
        "q_tiktok": "📱 ¿Cuántos seguidores tienes en TikTok? (ej. 1200, o 0)",
        "q_instagram": "📸 ¿Cuántos seguidores tienes en Instagram? (ej. 800, o 0)",
        "q_posting": "📅 ¿Cuántas veces publicas por semana? (ej. 3)",
        "q_problem": "❓ ¿Cuál es tu mayor problema como creator?",
        "q_konkurrenz": "🔍 ¿Quién es tu mayor competidor? (ej. @fitness_max o 'ninguno')",
        "enter_nische": "✏️ Escribe tu nicho:",
        "hilfe": (
            "*Creator Growth Bot – Ayuda*\n\n"
            "/demo – Demo gratuito (10 segundos)\n"
            "/analyse – Análisis completo en 7 pasos\n"
            "/sprache – Cambiar idioma\n"
            "/start – Menú principal\n\n"
            "💡 *Consejo:* ¡Empieza con /demo!"
        ),
        "sprache_waehlen": "🌍 Wähle deine Sprache / Choose your language:",
        "sprache_gesetzt": "✅ Idioma: Español",
        "file_caption": "📄 Tu análisis completo del {}",
        "nischen": ["🏋️ Fitness", "💰 Finanzas", "💄 Beauty", "🎮 Gaming", "🍳 Cocina", "✈️ Viajes", "📸 Fotografía", "🎵 Música", "💻 Tech", "✍️ Introducir personalizado"],
        "ai_language": "Spanish",
    },
}

LANG_NAMES = {"de": "🇩🇪 Deutsch", "en": "🇬🇧 English", "it": "🇮🇹 Italiano", "es": "🇪🇸 Español"}

# Standard-Sprache pro Telegram-Sprachcode
LANG_MAP = {
    "de": "de", "en": "en", "it": "it", "es": "es",
    "de-DE": "de", "en-US": "en", "en-GB": "en",
    "it-IT": "it", "es-ES": "es", "es-419": "es",
}


def get_lang(chat_id: int, user_lang_code: str | None, user_langs: dict) -> str:
    """Gibt die Sprache für diesen User zurück."""
    if chat_id in user_langs:
        return user_langs[chat_id]
    code = (user_lang_code or "de").split("-")[0].lower()
    return LANG_MAP.get(code, "de")


def t(key: str, lang: str) -> str:
    """Übersetzung holen."""
    return TEXTS.get(lang, TEXTS["de"]).get(key, TEXTS["de"].get(key, key))
