"""
telegram_bot.py – Creator Growth Bot per Telegram.
Features: Inline-Buttons, 7-Schritt-Analyse, Hashtags, Konkurrenz,
          Bewertung, Zusammenfassung als Datei, Admin /leads
"""
import sys
import io
import time
import threading
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

import telebot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from creator.profil_agent import analyse
from creator.growth_agent import erstelle_plan as growth_plan
from creator.monetize_agent import erstelle_plan as mono_plan
from creator.content_agent import generiere
from creator.pitch_agent import erstelle_dm
from creator.hashtag_agent import generiere_hashtags
from creator.konkurrenz_agent import analysiere_konkurrenz

try:
    from crm import save_lead, list_leads
    HAS_CRM = True
except Exception:
    HAS_CRM = False

BOT_TOKEN = "8977040512:AAHl-2FWFHljEPZ_FCIPB3iueqSNokKmppA"
MODEL = "qwen2.5:3b"
ADMIN_IDS: set[int] = set()  # wird beim ersten /leads automatisch gefüllt

bot = telebot.TeleBot(BOT_TOKEN)

user_state: dict[int, dict] = {}

NISCHEN_BUTTONS = [
    ["🏋️ Fitness", "💰 Finanzen", "💄 Beauty"],
    ["🎮 Gaming", "🍳 Kochen", "✈️ Reisen"],
    ["📸 Fotografie", "🎵 Musik", "💻 Tech"],
    ["✍️ Andere Nische eingeben"],
]

STEPS = ["nische", "tiktok", "instagram", "posting", "problem", "konkurrenz"]
QUESTIONS = {
    "tiktok":    "📱 Wie viele TikTok-Follower hast du? (z.B. 1200, oder 0)",
    "instagram": "📸 Wie viele Instagram-Follower hast du? (z.B. 800, oder 0)",
    "posting":   "📅 Wie oft postest du pro Woche? (z.B. 3)",
    "problem":   "❓ Was ist dein größtes Problem als Creator?",
    "konkurrenz": "🔍 Wer ist dein größter Konkurrent? (z.B. @fitness_max oder 'kein')",
}


def _menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🚀 Analyse starten"))
    kb.add(KeyboardButton("❓ Hilfe"))
    return kb


def _nischen_keyboard():
    kb = InlineKeyboardMarkup()
    for row in NISCHEN_BUTTONS:
        kb.add(*[InlineKeyboardButton(n, callback_data=f"nische:{n}") for n in row])
    return kb


def _bewertung_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("⭐", callback_data="rating:1"),
        InlineKeyboardButton("⭐⭐", callback_data="rating:2"),
        InlineKeyboardButton("⭐⭐⭐", callback_data="rating:3"),
        InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rating:4"),
        InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rating:5"),
    )
    return kb


@bot.message_handler(commands=["start"])
def cmd_start(msg):
    user_state.pop(msg.chat.id, None)
    ADMIN_IDS.add(msg.chat.id)
    bot.send_message(
        msg.chat.id,
        "🚀 Willkommen beim *Creator Growth System*!\n\n"
        "Ich analysiere dein Creator-Profil und erstelle:\n"
        "📊 Profil-Analyse\n"
        "📈 30-Tage-Wachstumsplan\n"
        "💰 Monetisierungs-Strategie\n"
        "🎬 Content-Ideen\n"
        "✉️ DM-Vorlagen\n"
        "#️⃣ Hashtag-Strategie\n"
        "🔍 Konkurrenz-Analyse\n\n"
        "Tippe *🚀 Analyse starten* oder /analyse",
        parse_mode="Markdown",
        reply_markup=_menu()
    )


@bot.message_handler(commands=["analyse"])
@bot.message_handler(func=lambda m: m.text in ("🚀 Analyse starten", "Analyse starten"))
def cmd_analyse(msg):
    user_state[msg.chat.id] = {"step": 0, "daten": {}}
    bot.send_message(
        msg.chat.id,
        "🎯 *Schritt 1/6 – Deine Nische*\n\nWähle eine Nische oder tippe deine eigene:",
        parse_mode="Markdown",
        reply_markup=_nischen_keyboard()
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("nische:"))
def cb_nische(call):
    cid = call.message.chat.id
    nische_raw = call.data.split(":", 1)[1]
    # Emoji entfernen für die Analyse
    nische = nische_raw.split(" ", 1)[-1] if " " in nische_raw else nische_raw

    if nische == "Andere Nische eingeben":
        bot.answer_callback_query(call.id)
        bot.send_message(cid, "✏️ Gib deine Nische ein:")
        user_state[cid] = {"step": 0, "daten": {}, "warte_nische": True}
        return

    bot.answer_callback_query(call.id, f"Nische: {nische} ✅")
    if cid not in user_state:
        user_state[cid] = {"step": 0, "daten": {}}
    user_state[cid]["daten"]["nische"] = nische
    user_state[cid]["step"] = 1
    bot.send_message(cid, QUESTIONS["tiktok"])


@bot.callback_query_handler(func=lambda c: c.data.startswith("rating:"))
def cb_rating(call):
    stars = int(call.data.split(":")[1])
    bot.answer_callback_query(call.id, "Danke für deine Bewertung! 🙏")
    bot.send_message(
        call.message.chat.id,
        f"{'⭐' * stars} Danke! Deine Bewertung hilft uns, besser zu werden.\n"
        f"Neue Analyse? Tippe /analyse",
        reply_markup=_menu()
    )


@bot.message_handler(commands=["hilfe"])
@bot.message_handler(func=lambda m: m.text == "❓ Hilfe")
def cmd_hilfe(msg):
    bot.send_message(
        msg.chat.id,
        "*Creator Growth Bot – Hilfe*\n\n"
        "/analyse – Neue Analyse starten\n"
        "/leads – Alle Leads anzeigen (Admin)\n"
        "/start – Startmenü\n\n"
        "💡 *Tipp:* Je konkreter deine Nische, desto besser die Analyse.\n"
        "Beispiele: 'Fitness für Frauen', 'Krypto für Anfänger', 'Vegan Kochen'",
        parse_mode="Markdown"
    )


@bot.message_handler(commands=["leads"])
def cmd_leads(msg):
    if not HAS_CRM:
        bot.send_message(msg.chat.id, "CRM nicht verfügbar.")
        return
    try:
        import sqlite3
        from pathlib import Path as P
        db = P(__file__).parent / "output" / "crm.db"
        con = sqlite3.connect(db)
        rows = con.execute(
            "SELECT id, name, interesse, status, followup FROM leads ORDER BY id DESC LIMIT 15"
        ).fetchall()
        con.close()
        if not rows:
            bot.send_message(msg.chat.id, "Noch keine Leads im CRM.")
            return
        lines = ["*📋 Letzte Leads:*\n"]
        for r in rows:
            lines.append(f"#{r[0]} {r[1]} | {r[2]} | {r[3]} | {r[4]}")
        bot.send_message(msg.chat.id, "\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        bot.send_message(msg.chat.id, f"Fehler: {e}")


@bot.message_handler(func=lambda m: m.chat.id in user_state)
def handle_input(msg):
    cid = msg.chat.id
    state = user_state[cid]

    # Warte auf manuelle Nischen-Eingabe
    if state.get("warte_nische"):
        state["daten"]["nische"] = msg.text.strip()
        state["step"] = 1
        state.pop("warte_nische")
        bot.send_message(cid, QUESTIONS["tiktok"])
        return

    step = state["step"]
    if step == 0:
        # Nische noch nicht gesetzt (Fallback)
        state["daten"]["nische"] = msg.text.strip()
        state["step"] = 1
        bot.send_message(cid, QUESTIONS["tiktok"])
        return

    key = STEPS[step]
    state["daten"][key] = msg.text.strip()
    state["step"] += 1

    if state["step"] < len(STEPS):
        next_key = STEPS[state["step"]]
        bot.send_message(cid, QUESTIONS[next_key])
    else:
        daten = state["daten"]
        user_state.pop(cid)
        bot.send_message(
            cid,
            "⏳ Analyse läuft... Das dauert 3–5 Minuten.\nDu bekommst alle Ergebnisse gleich hier."
        )
        threading.Thread(target=_run_analyse, args=(cid, daten), daemon=True).start()


def _send(cid: int, header: str, text: str) -> None:
    bot.send_message(cid, f"*{header}*", parse_mode="Markdown")
    content = text[:3990] + "\n...[gekürzt]" if len(text) > 4000 else text
    bot.send_message(cid, content)


def _run_analyse(cid: int, d: dict) -> None:
    ergebnisse = {}
    try:
        bot.send_message(cid, "⚡ Alle 7 Analysen starten gleichzeitig...")
        follower = f"TikTok:{d['tiktok']} IG:{d['instagram']}"

        # Alle 7 Agents PARALLEL starten
        results = {}

        def run(key, fn, *args):
            results[key] = fn(*args)

        threads = [
            threading.Thread(target=run, args=("profil", analyse, d["nische"], d["tiktok"], d["instagram"], d["posting"], d["problem"])),
            threading.Thread(target=run, args=("growth", growth_plan, d["nische"], "")),
            threading.Thread(target=run, args=("mono", mono_plan, d["nische"], follower, "")),
            threading.Thread(target=run, args=("content", generiere, d["nische"], "")),
            threading.Thread(target=run, args=("dm", erstelle_dm, d["nische"], "Creator Coaching", "auf Anfrage")),
            threading.Thread(target=run, args=("hashtags", generiere_hashtags, d["nische"])),
            threading.Thread(target=run, args=("konkurrenz", analysiere_konkurrenz, d["nische"], d.get("konkurrenz", "kein"))),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Ergebnisse in Reihenfolge senden
        profil = results.get("profil", "")
        growth = results.get("growth", "")
        ergebnisse = results

        _send(cid, "📊 PROFIL-ANALYSE", profil)
        _send(cid, "📈 GROWTH-STRATEGIE", growth)
        _send(cid, "💰 MONETISIERUNG", results.get("mono", ""))
        _send(cid, "🎬 CONTENT-IDEEN", results.get("content", ""))
        _send(cid, "✉️ DM-VORLAGEN", results.get("dm", ""))
        _send(cid, "#️⃣ HASHTAGS", results.get("hashtags", ""))
        _send(cid, "🔍 KONKURRENZ-ANALYSE", results.get("konkurrenz", ""))

        # CRM speichern
        lead_id = None
        if HAS_CRM:
            lead_id = save_lead(
                name=f"TG-Creator ({d['nische']})",
                interesse=d["nische"],
                quelle="telegram",
                notizen=f"TikTok:{d['tiktok']} IG:{d['instagram']} Problem:{d['problem']} Konkurrenz:{d.get('konkurrenz','-')}",
                followup_tage=3,
            )
            bot.send_message(cid, f"✅ Im CRM gespeichert als Lead #{lead_id}.")

        # Zusammenfassung als .txt Datei
        ts = datetime.now().strftime("%d.%m.%Y %H:%M")
        report = _erstelle_report(d, ergebnisse, ts)
        datei = io.BytesIO(report.encode("utf-8"))
        datei.name = f"creator_analyse_{d['nische'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        bot.send_document(cid, datei, caption=f"📄 Deine vollständige Analyse vom {ts}")

        # Bewertung
        bot.send_message(
            cid,
            "✅ *Analyse abgeschlossen!*\n\nWie hilfreich war die Analyse?",
            parse_mode="Markdown",
            reply_markup=_bewertung_keyboard()
        )

    except Exception as e:
        bot.send_message(cid, f"❌ Fehler bei der Analyse: {e}\nBitte versuche es erneut mit /analyse")


def _erstelle_report(d: dict, e: dict, ts: str) -> str:
    return f"""CREATOR GROWTH ANALYSE
Erstellt: {ts}
{'='*50}

CREATOR-DATEN:
Nische: {d.get('nische','-')}
TikTok: {d.get('tiktok','-')} Follower
Instagram: {d.get('instagram','-')} Follower
Posts/Woche: {d.get('posting','-')}
Problem: {d.get('problem','-')}
Konkurrenz: {d.get('konkurrenz','-')}

{'='*50}
📊 PROFIL-ANALYSE
{'='*50}
{e.get('profil','')}

{'='*50}
📈 GROWTH-STRATEGIE
{'='*50}
{e.get('growth','')}

{'='*50}
💰 MONETISIERUNG
{'='*50}
{e.get('mono','')}

{'='*50}
🎬 CONTENT-IDEEN
{'='*50}
{e.get('content','')}

{'='*50}
✉️ DM-VORLAGEN
{'='*50}
{e.get('dm','')}

{'='*50}
#️⃣ HASHTAGS
{'='*50}
{e.get('hashtags','')}

{'='*50}
🔍 KONKURRENZ-ANALYSE
{'='*50}
{e.get('konkurrenz','')}

{'='*50}
Erstellt mit Creator Growth Bot @creatorgrowth_ai_bot
"""


if __name__ == "__main__":
    print("Creator Growth Bot läuft...")
    print("Bot: @creatorgrowth_ai_bot")
    print("Stoppen mit Ctrl+C")
    bot.infinity_polling()
