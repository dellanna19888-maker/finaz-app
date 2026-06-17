"""
telegram_bot.py – Creator Growth Bot (DE/EN/IT/ES)
Features: Mehrsprachig, Inline-Buttons, 7-Schritt-Analyse,
          Demo-Modus, Bewertung, Download-Datei, /leads Admin
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
from i18n import t, get_lang, LANG_NAMES, TEXTS

try:
    from crm import save_lead
    HAS_CRM = True
except Exception:
    HAS_CRM = False

BOT_TOKEN = "8977040512:AAHl-2FWFHljEPZ_FCIPB3iueqSNokKmppA"
MODEL = "qwen2.5:3b"

bot = telebot.TeleBot(BOT_TOKEN)

user_state: dict[int, dict] = {}
user_langs: dict[int, str] = {}   # chat_id → "de"/"en"/"it"/"es"

STEPS = ["nische", "tiktok", "instagram", "posting", "problem", "konkurrenz"]
STEP_KEYS = ["q_tiktok", "q_instagram", "q_posting", "q_problem", "q_konkurrenz"]


# ── Hilfsfunktionen ────────────────────────────────────────────

def lang(msg_or_id) -> str:
    if isinstance(msg_or_id, int):
        cid = msg_or_id
        lc = None
    else:
        cid = msg_or_id.chat.id
        lc = getattr(msg_or_id.from_user, "language_code", None)
    return get_lang(cid, lc, user_langs)


def _menu(lg: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎯 Demo"), KeyboardButton("🚀 Analyse starten"))
    kb.add(KeyboardButton("❓ Hilfe"))
    return kb


def _nischen_keyboard(lg: str):
    nischen = TEXTS[lg]["nischen"]
    kb = InlineKeyboardMarkup(row_width=3)
    rows = [nischen[i:i+3] for i in range(0, len(nischen)-1, 3)]
    for row in rows:
        kb.add(*[InlineKeyboardButton(n, callback_data=f"nische:{n}") for n in row])
    kb.add(InlineKeyboardButton(nischen[-1], callback_data="nische:__manuell__"))
    return kb


def _demo_nischen_keyboard(lg: str):
    nischen = TEXTS[lg]["nischen"][:9]  # erste 9
    kb = InlineKeyboardMarkup(row_width=3)
    rows = [nischen[i:i+3] for i in range(0, len(nischen), 3)]
    for row in rows:
        kb.add(*[InlineKeyboardButton(n, callback_data=f"demo:{n}") for n in row])
    kb.add(InlineKeyboardButton(TEXTS[lg]["nischen"][-1], callback_data="demo:__manuell__"))
    return kb


def _vollversion_keyboard(lg: str):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(t("vollversion_btn", lg), callback_data="start_vollversion"))
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


def _sprache_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(*[InlineKeyboardButton(name, callback_data=f"lang:{code}") for code, name in LANG_NAMES.items()])
    return kb


def _send(cid: int, header: str, text: str) -> None:
    bot.send_message(cid, f"*{header}*", parse_mode="Markdown")
    content = text[:3990] + "\n...[gekürzt]" if len(text) > 4000 else text
    bot.send_message(cid, content)


# ── /start ─────────────────────────────────────────────────────

@bot.message_handler(commands=["start"])
def cmd_start(msg):
    user_state.pop(msg.chat.id, None)
    lg = lang(msg)
    bot.send_message(msg.chat.id, t("start", lg), parse_mode="Markdown", reply_markup=_menu(lg))


# ── /sprache ───────────────────────────────────────────────────

@bot.message_handler(commands=["sprache", "language", "lingua", "idioma"])
def cmd_sprache(msg):
    bot.send_message(msg.chat.id, t("sprache_waehlen", lang(msg)), reply_markup=_sprache_keyboard())


@bot.callback_query_handler(func=lambda c: c.data.startswith("lang:"))
def cb_lang(call):
    cid = call.message.chat.id
    code = call.data.split(":")[1]
    user_langs[cid] = code
    bot.answer_callback_query(call.id, t("sprache_gesetzt", code))
    bot.send_message(cid, t("start", code), parse_mode="Markdown", reply_markup=_menu(code))


# ── /demo ──────────────────────────────────────────────────────

@bot.message_handler(commands=["demo"])
@bot.message_handler(func=lambda m: m.text and m.text in ("🎯 Demo", "Demo", "demo"))
def cmd_demo(msg):
    user_state.pop(msg.chat.id, None)
    lg = lang(msg)
    bot.send_message(
        msg.chat.id,
        f"{t('demo_title', lg)}\n\n{t('demo_intro', lg)}",
        parse_mode="Markdown",
        reply_markup=_demo_nischen_keyboard(lg)
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("demo:"))
def cb_demo_nische(call):
    cid = call.message.chat.id
    lg = lang(cid)
    val = call.data.split(":", 1)[1]

    if val == "__manuell__":
        bot.answer_callback_query(call.id)
        bot.send_message(cid, t("enter_nische", lg))
        user_state[cid] = {"demo": True, "warte_nische": True}
        return

    nische = val.split(" ", 1)[-1] if " " in val else val
    bot.answer_callback_query(call.id, f"✅ {nische}")
    bot.send_message(cid, t("demo_running", lg).format(nische), parse_mode="Markdown")
    threading.Thread(target=_run_demo, args=(cid, nische, lg), daemon=True).start()


def _run_demo(cid: int, nische: str, lg: str) -> None:
    ai_lang = TEXTS[lg]["ai_language"]
    results = {}

    def run(key, fn, *args):
        results[key] = fn(*args)

    threads = [
        threading.Thread(target=run, args=("profil", analyse, nische, "0", "0", "3", "mehr Reichweite")),
        threading.Thread(target=run, args=("content", generiere, nische, "")),
        threading.Thread(target=run, args=("hashtags", generiere_hashtags, nische)),
    ]
    for th in threads: th.start()
    for th in threads: th.join()

    try:
        bot.send_message(cid, t("demo_done", lg).format(nische), parse_mode="Markdown")
        _send(cid, "📊 PROFIL", results.get("profil", ""))
        _send(cid, "🎬 CONTENT", results.get("content", ""))
        _send(cid, "#️⃣ HASHTAGS", results.get("hashtags", ""))
        bot.send_message(cid, t("demo_upsell", lg), parse_mode="Markdown",
                         reply_markup=_vollversion_keyboard(lg))
    except Exception as e:
        bot.send_message(cid, f"❌ {e}")


# ── Vollversion starten (nach Demo CTA) ────────────────────────

@bot.callback_query_handler(func=lambda c: c.data == "start_vollversion")
def cb_start_vollversion(call):
    cid = call.message.chat.id
    lg = lang(cid)
    bot.answer_callback_query(call.id)
    user_state[cid] = {"step": 0, "daten": {}}
    bot.send_message(cid, t("analyse_step1", lg), parse_mode="Markdown",
                     reply_markup=_nischen_keyboard(lg))


# ── /analyse ───────────────────────────────────────────────────

@bot.message_handler(commands=["analyse"])
@bot.message_handler(func=lambda m: m.text in ("🚀 Analyse starten", "Analyse starten"))
def cmd_analyse(msg):
    lg = lang(msg)
    user_state[msg.chat.id] = {"step": 0, "daten": {}}
    bot.send_message(msg.chat.id, t("analyse_step1", lg), parse_mode="Markdown",
                     reply_markup=_nischen_keyboard(lg))


@bot.callback_query_handler(func=lambda c: c.data.startswith("nische:"))
def cb_nische(call):
    cid = call.message.chat.id
    lg = lang(cid)
    val = call.data.split(":", 1)[1]

    if val == "__manuell__":
        bot.answer_callback_query(call.id)
        bot.send_message(cid, t("enter_nische", lg))
        user_state[cid] = {"step": 0, "daten": {}, "warte_nische": True}
        return

    nische = val.split(" ", 1)[-1] if " " in val else val
    bot.answer_callback_query(call.id, f"✅ {nische}")
    if cid not in user_state:
        user_state[cid] = {"step": 0, "daten": {}}
    user_state[cid]["daten"]["nische"] = nische
    user_state[cid]["step"] = 1
    bot.send_message(cid, t("q_tiktok", lg))


# ── Rating ─────────────────────────────────────────────────────

@bot.callback_query_handler(func=lambda c: c.data.startswith("rating:"))
def cb_rating(call):
    stars = int(call.data.split(":")[1])
    lg = lang(call.message.chat.id)
    bot.answer_callback_query(call.id, "🙏")
    bot.send_message(call.message.chat.id,
                     f"{'⭐' * stars} {t('rating_thanks', lg)}",
                     reply_markup=_menu(lg))


# ── /hilfe ─────────────────────────────────────────────────────

@bot.message_handler(commands=["hilfe", "help", "aiuto", "ayuda"])
@bot.message_handler(func=lambda m: m.text == "❓ Hilfe")
def cmd_hilfe(msg):
    bot.send_message(msg.chat.id, t("hilfe", lang(msg)), parse_mode="Markdown")


# ── /leads ─────────────────────────────────────────────────────

@bot.message_handler(commands=["leads"])
def cmd_leads(msg):
    if not HAS_CRM:
        bot.send_message(msg.chat.id, "CRM nicht verfügbar.")
        return
    try:
        import sqlite3
        db = Path(__file__).parent / "output" / "crm.db"
        con = sqlite3.connect(db)
        rows = con.execute(
            "SELECT id, name, interesse, status, followup FROM leads ORDER BY id DESC LIMIT 15"
        ).fetchall()
        con.close()
        if not rows:
            bot.send_message(msg.chat.id, "Noch keine Leads.")
            return
        lines = ["*📋 Letzte Leads:*\n"]
        for r in rows:
            lines.append(f"#{r[0]} {r[1]} | {r[2]} | {r[3]} | {r[4]}")
        bot.send_message(msg.chat.id, "\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        bot.send_message(msg.chat.id, f"Fehler: {e}")


# ── Eingabe-Handler ────────────────────────────────────────────

@bot.message_handler(func=lambda m: m.chat.id in user_state)
def handle_input(msg):
    cid = msg.chat.id
    state = user_state[cid]
    lg = lang(cid)

    # Demo: manuelle Nischen-Eingabe
    if state.get("demo") and state.get("warte_nische"):
        nische = msg.text.strip()
        user_state.pop(cid)
        bot.send_message(cid, t("demo_running", lg).format(nische), parse_mode="Markdown")
        threading.Thread(target=_run_demo, args=(cid, nische, lg), daemon=True).start()
        return

    # Vollanalyse: manuelle Nischen-Eingabe
    if state.get("warte_nische"):
        state["daten"]["nische"] = msg.text.strip()
        state["step"] = 1
        state.pop("warte_nische")
        bot.send_message(cid, t("q_tiktok", lg))
        return

    step = state["step"]
    if step == 0:
        state["daten"]["nische"] = msg.text.strip()
        state["step"] = 1
        bot.send_message(cid, t("q_tiktok", lg))
        return

    key = STEPS[step]
    state["daten"][key] = msg.text.strip()
    state["step"] += 1

    if state["step"] < len(STEPS):
        q_key = STEP_KEYS[state["step"] - 1]
        bot.send_message(cid, t(q_key, lg))
    else:
        daten = state["daten"]
        user_state.pop(cid)
        bot.send_message(cid, t("analyse_wait", lg))
        threading.Thread(target=_run_analyse, args=(cid, daten, lg), daemon=True).start()


# ── Vollanalyse ────────────────────────────────────────────────

def _run_analyse(cid: int, d: dict, lg: str) -> None:
    try:
        bot.send_message(cid, t("analyse_running", lg))
        follower = f"TikTok:{d['tiktok']} IG:{d['instagram']}"
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
        for th in threads: th.start()
        for th in threads: th.join()

        _send(cid, "📊 PROFIL-ANALYSE", results.get("profil", ""))
        _send(cid, "📈 GROWTH-STRATEGIE", results.get("growth", ""))
        _send(cid, "💰 MONETISIERUNG", results.get("mono", ""))
        _send(cid, "🎬 CONTENT-IDEEN", results.get("content", ""))
        _send(cid, "✉️ DM-VORLAGEN", results.get("dm", ""))
        _send(cid, "#️⃣ HASHTAGS", results.get("hashtags", ""))
        _send(cid, "🔍 KONKURRENZ-ANALYSE", results.get("konkurrenz", ""))

        if HAS_CRM:
            lid = save_lead(
                name=f"TG-Creator ({d['nische']})",
                interesse=d["nische"], quelle="telegram",
                notizen=f"TikTok:{d['tiktok']} IG:{d['instagram']} Lang:{lg}",
                followup_tage=3,
            )

        ts = datetime.now().strftime("%d.%m.%Y %H:%M")
        report = _erstelle_report(d, results, ts, lg)
        datei = io.BytesIO(report.encode("utf-8"))
        datei.name = f"creator_analyse_{d['nische'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        bot.send_document(cid, datei, caption=t("file_caption", lg).format(ts))

        bot.send_message(cid, t("analyse_done", lg), parse_mode="Markdown",
                         reply_markup=_bewertung_keyboard())

    except Exception as e:
        bot.send_message(cid, f"❌ Fehler: {e}\n/analyse")


def _erstelle_report(d: dict, e: dict, ts: str, lg: str) -> str:
    return (
        f"CREATOR GROWTH ANALYSE\nErstellt: {ts}\n{'='*50}\n\n"
        f"CREATOR-DATEN:\nNische: {d.get('nische','-')}\n"
        f"TikTok: {d.get('tiktok','-')} | Instagram: {d.get('instagram','-')}\n"
        f"Posts/Woche: {d.get('posting','-')} | Sprache: {lg.upper()}\n"
        f"Problem: {d.get('problem','-')}\nKonkurrenz: {d.get('konkurrenz','-')}\n\n"
        + "\n\n".join([
            f"{'='*50}\n{h}\n{'='*50}\n{e.get(k,'')}"
            for h, k in [
                ("📊 PROFIL-ANALYSE","profil"), ("📈 GROWTH-STRATEGIE","growth"),
                ("💰 MONETISIERUNG","mono"), ("🎬 CONTENT-IDEEN","content"),
                ("✉️ DM-VORLAGEN","dm"), ("#️⃣ HASHTAGS","hashtags"),
                ("🔍 KONKURRENZ-ANALYSE","konkurrenz"),
            ]
        ])
        + f"\n\n{'='*50}\nCreator Growth Bot @creatorgrowth_ai_bot\n"
    )


if __name__ == "__main__":
    print("Creator Growth Bot (DE/EN/IT/ES) läuft...")
    bot.infinity_polling()
