"""
telegram_bot.py – Creator Growth Bot per Telegram.

Il creator scrive al bot, inserisce i dati e riceve l'analisi completa.
Il lead viene salvato automaticamente nel CRM.

Avvio:
  pip install pyTelegramBotAPI
  python3 telegram_bot.py
"""
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from creator.profil_agent import analyse
from creator.growth_agent import erstelle_plan as growth_plan
from creator.monetize_agent import erstelle_plan as mono_plan
from creator.content_agent import generiere
from creator.pitch_agent import erstelle_dm

try:
    from crm import save_lead
    HAS_CRM = True
except Exception:
    HAS_CRM = False

BOT_TOKEN = "8977040512:AAHl-2FWFHljEPZ_FCIPB3iueqSNokKmppA"
MODEL = "tinyllama"

bot = telebot.TeleBot(BOT_TOKEN)

# Stato per ogni utente: {chat_id: {step, dati}}
user_state: dict[int, dict] = {}

STEPS = ["nische", "tiktok", "instagram", "posting", "problem"]
QUESTIONS = {
    "nische":    "Deine Nische / Thema (z.B. Fitness, Finance, Beauty):",
    "tiktok":    "Wie viele TikTok-Follower hast du? (z.B. 1200)",
    "instagram": "Wie viele Instagram-Follower hast du? (z.B. 800)",
    "posting":   "Wie oft postest du pro Woche? (z.B. 3)",
    "problem":   "Was ist dein groesstes Problem als Creator?",
}


def _menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Analyse starten"))
    kb.add(KeyboardButton("Hilfe"))
    return kb


@bot.message_handler(commands=["start"])
def cmd_start(msg):
    user_state.pop(msg.chat.id, None)
    bot.send_message(
        msg.chat.id,
        "Willkommen beim *Creator Growth System*!\n\n"
        "Ich analysiere dein Creator-Profil und erstelle:\n"
        "• Profil-Analyse\n"
        "• 30-Tage-Wachstumsplan\n"
        "• Monetisierungs-Strategie\n"
        "• Content-Ideen\n"
        "• DM-Vorlagen\n\n"
        "Tippe *Analyse starten* oder /analyse",
        parse_mode="Markdown",
        reply_markup=_menu()
    )


@bot.message_handler(commands=["analyse"])
@bot.message_handler(func=lambda m: m.text == "Analyse starten")
def cmd_analyse(msg):
    user_state[msg.chat.id] = {"step": 0, "daten": {}}
    bot.send_message(msg.chat.id, QUESTIONS["nische"])


@bot.message_handler(commands=["hilfe"])
@bot.message_handler(func=lambda m: m.text == "Hilfe")
def cmd_hilfe(msg):
    bot.send_message(
        msg.chat.id,
        "*Befehle:*\n"
        "/start – Startmenue\n"
        "/analyse – Neue Analyse starten\n"
        "/hilfe – Diese Hilfe\n\n"
        "Bei Problemen: schreib einfach was du brauchst.",
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda m: m.chat.id in user_state)
def handle_input(msg):
    cid = msg.chat.id
    state = user_state[cid]
    step = state["step"]
    key = STEPS[step]
    state["daten"][key] = msg.text.strip()
    state["step"] += 1

    if state["step"] < len(STEPS):
        next_key = STEPS[state["step"]]
        bot.send_message(cid, QUESTIONS[next_key])
    else:
        # Alle Daten da – starte Analyse in Thread
        daten = state["daten"]
        user_state.pop(cid)
        bot.send_message(cid, "Analyse laeuft... Das dauert 2-4 Minuten. Bitte warten.")
        threading.Thread(target=_run_analyse, args=(cid, daten), daemon=True).start()


def _run_analyse(cid: int, d: dict) -> None:
    try:
        bot.send_message(cid, "1/5 – Profil-Analyse...")
        profil = analyse(d["nische"], d["tiktok"], d["instagram"], d["posting"], d["problem"], MODEL)
        bot.send_message(cid, f"*PROFIL-ANALYSE*\n\n{profil}", parse_mode="Markdown")

        bot.send_message(cid, "2/5 – Growth-Strategie...")
        growth = growth_plan(d["nische"], profil, MODEL)
        bot.send_message(cid, f"*GROWTH-STRATEGIE*\n\n{growth}", parse_mode="Markdown")

        bot.send_message(cid, "3/5 – Monetisierungs-Plan...")
        follower = f"TikTok:{d['tiktok']} IG:{d['instagram']}"
        mono = mono_plan(d["nische"], follower, profil, MODEL)
        bot.send_message(cid, f"*MONETISIERUNG*\n\n{mono}", parse_mode="Markdown")

        bot.send_message(cid, "4/5 – Content-Ideen...")
        content = generiere(d["nische"], growth, MODEL)
        bot.send_message(cid, f"*CONTENT-IDEEN*\n\n{content}", parse_mode="Markdown")

        bot.send_message(cid, "5/5 – DM-Vorlagen...")
        dm = erstelle_dm(d["nische"], "Creator Coaching", "auf Anfrage", MODEL)
        bot.send_message(cid, f"*DM-VORLAGEN*\n\n{dm}", parse_mode="Markdown")

        # CRM speichern
        if HAS_CRM:
            lid = save_lead(
                name=f"TG-Creator ({d['nische']})",
                interesse=d["nische"],
                quelle="telegram",
                notizen=f"TikTok:{d['tiktok']} IG:{d['instagram']} Problem:{d['problem']}",
                followup_tage=3,
            )
            bot.send_message(cid, f"Im CRM gespeichert als Lead #{lid}.")

        bot.send_message(
            cid,
            "Analyse abgeschlossen! Schreibe /analyse fuer eine neue Analyse.",
            reply_markup=_menu()
        )

    except Exception as e:
        bot.send_message(cid, f"Fehler bei der Analyse: {e}\nBitte versuche es erneut mit /analyse")


if __name__ == "__main__":
    print("Creator Growth Bot laeuft...")
    print("Bot: @creatorgrowth_ai_bot")
    print("Stoppen mit Ctrl+C")
    bot.infinity_polling()
