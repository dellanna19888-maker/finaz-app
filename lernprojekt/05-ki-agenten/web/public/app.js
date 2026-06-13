// ============================================================
//  Frontend-Logik der Webseite
// ============================================================
// Diese Datei laeuft im BROWSER. Sie schickt Nische + Plattform an den
// Server und zeigt die Ergebnisse der vier Agenten LIVE an, sobald sie
// eintreffen (ueber "Server-Sent Events" / EventSource).

const formular = document.getElementById("formular");
const startKnopf = document.getElementById("startKnopf");
const statusBox = document.getElementById("status");
const statusText = document.getElementById("statusText");

// Ordnet jeden "Schritt" vom Server der passenden Karte zu.
const karten = {
  recherche: { karte: "karte-recherche", text: "text-recherche" },
  ideen: { karte: "karte-ideen", text: "text-ideen" },
  post: { karte: "karte-post", text: "text-post" },
  fertig: { karte: "karte-fertig", text: "text-fertig" },
};

let quelle = null; // die aktive EventSource-Verbindung

formular.addEventListener("submit", (ereignis) => {
  ereignis.preventDefault();

  const nische = document.getElementById("nische").value.trim();
  const plattform = document.getElementById("plattform").value;
  if (!nische) return;

  starteGenerierung(nische, plattform);
});

function starteGenerierung(nische, plattform) {
  // Alte Ergebnisse ausblenden und Oberflaeche zuruecksetzen.
  for (const { karte, text } of Object.values(karten)) {
    document.getElementById(karte).classList.add("versteckt");
    document.getElementById(text).textContent = "";
  }
  statusBox.classList.remove("versteckt", "fehler");
  statusText.textContent = "Verbindung wird aufgebaut ...";
  startKnopf.disabled = true;
  startKnopf.textContent = "⏳ Agenten arbeiten ...";

  // Eine offene Verbindung zum Server aufbauen. Der Server schickt darueber
  // nach und nach die Ergebnisse jedes Agenten.
  const url =
    "/api/generate?nische=" +
    encodeURIComponent(nische) +
    "&plattform=" +
    encodeURIComponent(plattform);
  quelle = new EventSource(url);

  quelle.onmessage = (ereignis) => {
    const { schritt, text } = JSON.parse(ereignis.data);

    if (schritt === "status") {
      statusText.textContent = text;
    } else if (schritt === "ende") {
      beendeGenerierung("✅ Fertig!");
    } else if (schritt === "fehler") {
      zeigeFehler(text);
    } else if (karten[schritt]) {
      // Ergebnis-Karte fuellen und einblenden.
      document.getElementById(karten[schritt].text).textContent = text;
      document.getElementById(karten[schritt].karte).classList.remove("versteckt");
    }
  };

  // Wird ausgeloest, wenn die Verbindung unerwartet abbricht.
  quelle.onerror = () => {
    if (quelle) zeigeFehler("Verbindung zum Server unterbrochen.");
  };
}

function beendeGenerierung(meldung) {
  if (quelle) {
    quelle.close(); // wichtig: sonst verbindet sich der Browser neu!
    quelle = null;
  }
  statusBox.classList.add("versteckt");
  startKnopf.disabled = false;
  startKnopf.textContent = "✨ Content erstellen";
  if (meldung) console.log(meldung);
}

function zeigeFehler(text) {
  beendeGenerierung();
  statusBox.classList.remove("versteckt");
  statusBox.classList.add("fehler");
  statusText.textContent = "⚠️ " + text;
}
