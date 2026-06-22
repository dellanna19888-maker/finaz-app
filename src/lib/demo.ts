// Demo-Modus: realistische KI-Antworten ohne API-Key

export function isDemoMode(): boolean {
  try { return localStorage.getItem('finaz_demo') === '1' } catch { return false }
}

export function setDemoMode(on: boolean): void {
  try {
    if (on) localStorage.setItem('finaz_demo', '1')
    else localStorage.removeItem('finaz_demo')
  } catch { /* ignore */ }
}

const DEMO_RESPONSES: Record<string, string> = {
  default: `## 🧠 Analyse-Ergebnis (Demo)

**Deine 3 größten Wachstums-Hebel:**

1. **Konsistenz** – Poste mind. 3× pro Woche zur gleichen Uhrzeit (18–20 Uhr funktioniert am besten für Creator-Kanäle).
2. **Hook-Optimierung** – Die ersten 3 Sekunden entscheiden. Nutze Zahlen + Neugier: *„3 Fehler, die 90% der Creator machen"*.
3. **Community-Aufbau** – Antworte auf JEDE Kommentar in den ersten 30 Minuten. Der Algorithmus liebt Early Engagement.

**Deine Konkurrenz-Analyse:**
- Kanal A postet täglich, hat aber schwache Hooks → Chance für dich
- Kanal B nutzt Carousels sehr effektiv → Nachahmbar

**Nächster Schritt:** Erstelle diese Woche 1 Video mit diesem Hook-Format und miss die Watch-Time.`,

  hook: `## 🎬 Hook-Ideen für dein nächstes Video

**Hook-Typ A — Zahl + Versprechen:**
> „5 KI-Tools, die mir 3 Stunden pro Tag sparen (davon kennst du 3 nicht)"

**Hook-Typ B — Schock-Fakt:**
> „90% der Creator machen diesen Fehler — und wundern sich warum sie nicht wachsen"

**Hook-Typ C — Story:**
> „Vor 6 Monaten hatte ich 200 Follower. Heute sind es 12.000. Das ist was ich geändert habe."

**Hook-Typ D — Frage:**
> „Warum wächst dein Kanal nicht, obwohl du täglich postest? (Ich hatte exakt das gleiche Problem)"

💡 **Empfehlung:** Nutze Typ A oder B für Shorts/Reels, Typ C für längere Videos.`,

  skript: `## 📝 30-Sekunden Reel-Skript (Demo)

**[0-3s HOOK]**
"Ich zeig dir in 30 Sekunden, warum du kein Geld mit Content verdienst."

**[3-10s PROBLEM]**
"Die meisten Creator erstellen Content für sich selbst – nicht für ihre Zuschauer."

**[10-22s LÖSUNG]**
"Stell dir vor jedem Video diese Frage: Was bekommt mein Zuschauer in den nächsten 60 Sekunden? Nur DANN klicken sie weiter."

**[22-28s BEWEIS]**
"Ich hab meinen Views mit dieser einen Änderung verdoppelt – ohne mehr Content zu erstellen."

**[28-30s CTA]**
"Folg mir für mehr. Link in Bio."

---
📱 **Caption:** Views verdoppelt mit 1 Frage 🎯 #ContentCreator #Wachstum #YouTubeTipps`,

  plan: `## 📅 Content-Plan diese Woche

| Tag | Format | Thema | Plattform |
|-----|--------|-------|-----------|
| Mo | Reel 30s | Hook-Fehler #1 | Instagram/TikTok |
| Di | Post | Karriere-Tipp | LinkedIn |
| Mi | YouTube Short | Tool-Demo | YouTube |
| Do | Story | Behind the Scenes | Instagram |
| Fr | Reel 60s | Wochenzusammenfassung | TikTok |
| Sa | Carousel | 5 Tipps | Instagram |
| So | Pause / Analyse | — | — |

**Zeitaufwand:** ~6h/Woche
**Batch-Strategie:** Dienstags alles aufnehmen, Mittwochs schneiden, Rest planen`,
}

export async function demoChat(
  prompt: string,
  onDelta: (text: string) => void,
): Promise<void> {
  const lower = prompt.toLowerCase()
  let response = DEMO_RESPONSES.default
  if (lower.includes('hook') || lower.includes('idee') || lower.includes('ideen')) response = DEMO_RESPONSES.hook
  else if (lower.includes('skript') || lower.includes('reel') || lower.includes('tiktok')) response = DEMO_RESPONSES.skript
  else if (lower.includes('plan') || lower.includes('woche') || lower.includes('kalender')) response = DEMO_RESPONSES.plan

  // Simulate streaming
  const words = response.split(' ')
  for (const word of words) {
    await delay(15 + Math.random() * 25)
    onDelta(word + ' ')
  }
}

function delay(ms: number) { return new Promise(r => setTimeout(r, ms)) }
