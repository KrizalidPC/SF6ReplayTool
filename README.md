# SF6 Automatic Replay Recorder Bot 🤖🎮

Un ecosistema di automazione completo in Python e LUA progettato per la registrazione, l'archiviazione, l'upload e la catalogazione automatica dei replay di **Street Fighter 6** tramite **OBS Studio** e **REFramework**.

Inviando semplicemente uno o più ID dei replay nella chat del tuo Bot Telegram privato, il sistema si occuperà di avviare OBS Studio, lanciare il gioco tramite Steam, navigare i menu di gioco fino alla schermata di ricerca, riprodurre i replay in sequenza, registrare i match e rinominare automaticamente i file video finali con i nomi reali dei giocatori e l'ID del match, offrendoti infine la possibilità di caricarli su YouTube con un semplice click.

---

## ✨ Funzionalità principali

* **Automazione Totale dei Menu**: L'Orchestrator LUA naviga autonomamente da qualsiasi schermata fino alla ricerca per ID, digita il codice e avvia il replay senza alcun input manuale.
* **Gestione Avanzata della Coda**: Supporto per l'invio multiplo di replay nello stesso comando Telegram. Il bot e lo script LUA li elaborano in background in modo sequenziale.
* **Sincronizzazione Frame-Perfect**: 
  * Gestione nativa dell'errore `207 (OBS Not Ready)` con meccanismo di retry progressivo durante l'inizializzazione di OBS Studio.
  * Pulizia preventiva dei file di trigger temporanei ad ogni ciclo per evitare conflitti o falsi avvii.
* **Richiesta di Upload Interattiva**: Al termine di ogni registrazione, il bot invia una notifica su Telegram con pulsanti interattivi (Sì/No) per confermare l'upload su YouTube.
* **Upload Asincrono su YouTube**: I caricamenti avvengono in background tramite thread dedicati in Python, permettendo al bot e al gioco di passare immediatamente al replay successivo senza interruzioni.
* **Privacy e Controllo Qualità**: I video vengono caricati automaticamente in modalità **"Non in elenco" (Unlisted)** per permetterti un controllo qualità prima della pubblicazione.
* **Hook Nativo dei Match**: La registrazione OBS si avvia sul primo frame effettivo del round e si stoppa sull'ultimo frame dell'incontro, catturando solo il gameplay.
* **Prevenzione Conflitti File**: Rilevamento automatico dei file duplicati con l'applicazione di un numbering progressivo (es. `_1`, `_2`) per evitare sovrascritture.
* **Heartbeat di Sicurezza**: Monitoraggio continuo dello stato del gioco. Se il gioco si blocca o si disconnette, OBS interrompe in sicurezza la registrazione per evitare file corrotti o infiniti.
* **Telecomando PC Distante**: Comandi Telegram per controllare lo status dell'hardware, chiudere forzatamente i processi in blocco o spegnere il PC a fine sessione.

---

## 📋 Prerequisiti

Prima di avviare il bot, assicurati di avere installato e configurato i seguenti componenti sul tuo PC Windows:

1. **Python 3.10+** (ricordati di spuntare la casella *"Add python.exe to PATH"* durante l'installazione).
2. **OBS Studio** con il plugin **WebSocket** abilitato (incluso nativamente in OBS 28+).
3. **Street Fighter 6** su Steam.
4. **REFramework** inserito nella cartella principale di Street Fighter 6.

---

## ⚙️ Guida alle Configurazioni Preliminari

### 1. Come ottenere il Token e l'ID Telegram
Per far funzionare lo script, devi creare un bot e ricavare il tuo ID utente per fare in modo che solo tu possa impartire comandi.

* **Ottenere l'`API_TOKEN` (BotFather)**:
  1. Cerca `@BotFather` sulla barra di ricerca di Telegram e avvia la chat.
  2. Invia il comando `/newbot` e segui le istruzioni (scegli un nome visibile e uno username univoco che termini con `_bot`).
  3. Copia l'**HTTP API Token** generato (avrà una struttura simile a: `8847223467:AAHwqf...`).
* **Ottenere il tuo `MIO_ID_TELEGRAM`**:
  1. Cerca `@userinfobot` su Telegram e avvia la chat.
  2. Invia un qualsiasi messaggio o il comando `/start`.
  3. Il bot ti risponderà mostrando il tuo **ID numerico privato** (es: `124120653`). Copialo.

### 2. Configurazione di OBS Studio
Il bot deve poter comunicare con OBS tramite WebSocket e gestire correttamente i file video generati.

* **Attivare il WebSocket**:
  1. Apri OBS Studio e vai su **Strumenti** -> **Impostazioni server WebSocket**.
  2. Spunta la voce **Abilita server WebSocket**.
  3. Configura la **Porta del server** (di default è `4455`).
  4. È consigliato lasciare attiva l'autenticazione e generare una password. Se decidi di disattivarla, ricordati di lasciare la variabile `OBS_PASSWORD = ""` all'interno dello script Python.
* **Impostazioni di Output (Video)**:
  1. Vai in **Impostazioni** -> **Uscita** -> scheda **Registrazione**.
  2. Imposta il **Formato di registrazione** su `MP4` o `MKV`.
  3. Prendi nota del **Percorso di registrazione** (la cartella in cui OBS salva i video), poiché è lì che lo script Python cercherà i file per rinominarli con i dati reali del match.

### 3. Integrazione ed Upload su YouTube 📺
Il bot include un modulo per caricare le registrazioni direttamente sul tuo canale YouTube.

* **Configurazione delle Credenziali**:
  1. Accedi a [Google Cloud Console](https://cloud.google.com/) e crea un progetto.
  2. Abilita le **YouTube Data API v3** e crea una schermata di consenso OAuth inserendo la tua email tra gli *utenti di test*.
  3. Genera un **ID Client OAuth** impostando il tipo di applicazione su *Applicazione Desktop*.
  4. Scarica il file JSON delle credenziali, rinominalo in **`client_secrets.json`** e posizionalo nella cartella principale del bot.
* **Primo Avvio (Autenticazione Handshake)**:
  1. Alla prima registrazione confermata, lo script Python aprirà una pagina nel tuo browser web richiedendo l'accesso al tuo account Google.
  2. Consenti i permessi di upload. Il bot genererà in automatico un file locale **`token.json`**, garantendo l'autenticazione automatica silenziosa per tutti i caricamenti futuri.

---

## 🎮 Struttura e Configurazione lato Gioco (REFramework & LUA)

L'automazione all'interno del motore grafico del gioco è gestita da due script LUA che comunicano costantemente con la controparte in Python attraverso file JSON di stato memorizzati nella cartella `reframework/data/`.

### I file LUA inclusi
All'interno della repository trovi due file LUA che devono essere inseriti nella cartella `<Cartella Gioco>\reframework\autorun\`:

1. **`orchestrator.lua`**: Implementa una macchina a stati complessa che analizza i flussi dell'interfaccia utente di gioco (`app.UIFlowManager`). Inietta input di tastiera virtuali a basso livello per navigare i menu, stabilizzare le transizioni della UI, inserire l'ID nella casella di testo corretta e avviare il replay. Integra un pannello ImGui interno al gioco per monitorare lo stato della coda in tempo reale.
2. **`recon.lua`**: Si aggancia (`hook`) ai metodi di riproduzione nativi del gioco (`BattleReplayController` e `BattleReplayDataManager`). Estrae in tempo reale i metadati dell'incontro (ID, Nickname reali dei giocatori, ID dei personagens scelti) e scrive i trigger di avvio/arresto (`start` / `stop`) captati all'esatto primo e ultimo frame del match, sincronizzando OBS al millisecondo. Genera inoltre il ciclo di *heartbeat* a 60 FPS.

---

## 🚀 Installazione e Configurazione dello Script

### 1. Posizionamento dei file
Scarica o clona questa repository sul tuo PC, assicurandoti che il file di installazione `.bat` e lo script `.py` si trovino nella stessa cartella:
```bash
git clone https://github.com
cd SF6-Replay-Recorder
```
*Ricordati di copiare i file `.lua` nella cartella `reframework/autorun/` del gioco.*

### 2. Modifica delle variabili Python
Apri il file `SF6ReplayScript.py` con un editor di testo e compila le variabili iniziali inserendo i dati raccolti:

```python
# Configurazione Telegram
API_TOKEN = "IL_TUO_TOKEN_BOT_TELEGRAM" 
MIO_ID_TELEGRAM = IL_TUO_ID_TELEGRAM 

# Configurazione OBS WebSocket
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "LA_TUA_PASSWORD_WEBSOCKET_OBS"
OBS_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"

# Percorsi di gioco (Modifica la lettera del disco in base alla tua installazione)
QUEUE_FILE_PATH = r"D:\SteamLibrary\steamapps\common\Street Fighter 6\reframework\data\replay_queue.json"
BASE_DIR_LUA = pathlib.Path(r"D:\SteamLibrary\steamapps\common\Street Fighter 6\reframework\data")
```

### 3. Installazione automatica delle dipendenze
Fai click destro sul file `SF6Replay Tool - Installer Automatico.bat` e seleziona **"Esegui come amministratore"**. 
L'installer si occuperà in automatico di verificare Python, aggiornare `pip`, installare i pacchetti necessari (compresi i moduli Google per le API di YouTube) e avviare l'istanza del bot.

---

## 🕹️ Comandi del Bot Telegram

Il bot imposterà automaticamente il menu dei comandi rapidi alla prima esecuzione. Puoi interagire con lui usando i seguenti input:

| Comando | Descrizione |
| :--- | :--- |
| `/status` | Mostra se SF6 e OBS sono aperti, lo stato della connessione WebSocket e il numero di replay rimasti in coda. |
| `/avvia_gioco` | Forza l'apertura manuale di OBS Studio e di Street Fighter 6 tramite Steam. |
| `/registra_replay <ID_1> <ID_2>` | Accoda uno o più ID (separati da uno spazio) per avviare la sequenza di registrazione automatica. |
| `/stop` | Forza la chiusura immediata di SF6 e OBS, interrompe la registrazione e svuota la coda d'attesa. |
| `/spegni` | Avvia un timer di 10 secondi e spegne completamente il PC. |

### Esempio di scenario in chat:
> **Tu**: `/registra_replay xxxxxxxxx`
> 
> **Bot**: 📝 Aggiunto `1` replay alla lista d'attesa.
> 
> **Bot**: 🔄 Elaborazione coda: inizio registrazione del replay `xxxxxxxxx`...
> 
> **Bot**: 🔴 REC Partito: P1 vs P2 (ID: WD544B58N)
> 
> **Bot**: 🏁 Replay `xxxxxxxxx` registrato!
>        📁 File: `P1 vs P2 xxxxxxxxx.mp4`
>        *Vuoi caricarlo su YouTube?*
>        `[ ✅ Sì, Carica ]`  `[ ❌ No, Salta ]`
> > *(Se l'utente clicca su Sì)*
> 
> **Bot**: 🚀 Upload in corso su YouTube per il replay `xxxxxxxxx`...
> 
> **Bot**: 📺 Caricato con successo su YouTube per il replay `xxxxxxxxx`!
>        🔗 Link: `https://youtu.be`

---

## 🛠️ Risoluzione dei Problemi (Troubleshooting)

* **L'Orchestrator LUA si blocca nei menu**: I nomi dei flussi interni della UI di Capcom (es. `app.menu.UIFlowTitle.Param`) possono subire variazioni a seguito di aggiornamenti o patch importanti di *Street Fighter 6*. In caso di **blocchi post-aggiornamento**, procedi in questo modo:
  1. Apri il menu in-game di **REFramework** (tasto `Insert` di default).
  2. Usa lo strumento **Object Explorer** per identificare i flussi della UI attivi in quel momento.
  3. Verifica e correggi le costanti **`F_*`** posizionate all'inizio del file `orchestrator.lua` inserendo i nuovi nomi dei flussi.

* **Il replay salta subito e mostra un errore di heartbeat locale**: Controlla il valore di **`HB_GRACE`** nel codice Python. Se il tuo PC o la tua connessione impiegano molto tempo a caricare i menu o i caricamenti interni di SF6, **aumenta questo valore** (attualmente impostato a `40` secondi) per dare più tolleranza alla mod LUA prima che generi il primo file di battito cardiaco.

* **OBS si apre ma il bot continua a mostrare errori di connessione**: Verifica che la password WebSocket inserita nella variabile **`OBS_PASSWORD`** sia identica a quella impostata manualmente all'interno dei menu di *OBS Studio*.

---

## 📝 Licenza

Questo progetto è rilasciato sotto licenza **MIT**.

-----------------------------------------------------
# SF6 Replay Bot 🎮🤖

Bot Telegram che automatizza la ricerca, registrazione e pubblicazione dei replay di **Street Fighter 6**: basta mandare al bot uno o più ID di replay, e lui fa navigare il gioco fino al replay richiesto, avvia la registrazione con OBS Studio, rinomina il video con i nomi dei due giocatori e ti chiede — con un pulsante su Telegram — se vuoi caricarlo su YouTube (come video "Non in elenco").

## ✨ Funzionalità

- **Telecomando via Telegram**: avvia SF6 e OBS, controlla lo stato del PC, spegni il PC da remoto.
- **Coda replay**: invia più ID in un colpo solo (`/registra_replay ID1 ID2 ID3`), il bot li registra uno dopo l'altro.
- **Navigazione automatica in-game**: uno script Lua (via [REFramework](https://github.com/praydog/REFramework)) porta da solo il gioco dal menu principale fino al replay richiesto.
- **Registrazione automatica con OBS**: avvio/stop dell'OBS WebSocket sincronizzato con l'inizio e la fine del match, con un sistema di heartbeat che evita registrazioni "orfane" se qualcosa va storto in game.
- **Rinomina automatica dei file**: `Giocatore1 vs Giocatore2 <ID replay>.mp4`, con gestione dei duplicati.
- **Upload YouTube opzionale**: dopo ogni registrazione, il bot chiede conferma via pulsante prima di caricare il video (privacy "Non in elenco" di default).
- **Auto-recovery di rete**: se la connessione a Telegram cade, il bot si riavvia da solo invece di chiudersi.

## 🏗️ Architettura

```
┌─────────────────┐      JSON (coda replay)      ┌──────────────────────┐
│  SF6ReplayScript │ ───────────────────────────▶ │  orchestrator.lua    │
│  (bot Telegram)  │                               │  (dentro SF6, via    │
│                  │ ◀─────────────────────────── │  REFramework)        │
└────────┬─────────┘   JSON (trigger/heartbeat)    └──────────┬───────────┘
         │                                                     │
         │ OBS WebSocket                                       │ hook sui replay
         ▼                                                     ▼
┌──────────────────┐                                ┌──────────────────────┐
│   OBS Studio      │                                │   recon.lua           │
│  (registrazione)  │                                │  (metadata giocatori, │
└────────┬───────────┘                                │   start/stop rec)     │
         │                                            └──────────────────────┘
         ▼
┌──────────────────┐
│ youtube_uploader  │
│  (upload YouTube  │
│   opzionale)      │
└───────────────────┘
```

Il bot Python e gli script Lua comunicano **solo tramite file JSON** scambiati nella cartella `reframework/data` del gioco — nessuna connessione diretta tra i due mondi.

## 📁 Struttura del progetto

| File | Dove va installato | Cosa fa |
|---|---|---|
| `SF6ReplayScript.py` | PC, cartella a piacere | Bot Telegram principale, orchestratore generale |
| `youtube_uploader.py` | Stessa cartella di `SF6ReplayScript.py` | Modulo per l'upload su YouTube via API v3 |
| `orchestrator.lua` | `<cartella SF6>\reframework\autorun\` | Naviga automaticamente i menu del gioco fino al replay richiesto |
| `recon.lua` | `<cartella SF6>\reframework\autorun\` | Rileva inizio/fine replay ed estrae i nomi dei giocatori |
| `dinput8.dll` | Cartella principale del gioco (root, accanto all'eseguibile) | Loader di [REFramework](https://github.com/praydog/REFramework), necessario per eseguire gli script `.lua` |
| `SF6REPLAYTOOL_INSTALLER.bat` | Stessa cartella di `SF6ReplayScript.py` | Installa automaticamente tutte le dipendenze Python |

## ✅ Requisiti

- Windows 10/11
- [Python 3.10+](https://www.python.org/) (durante l'installazione, spunta "Add python.exe to PATH")
- [OBS Studio](https://obsproject.com/) con il plugin **obs-websocket** abilitato (integrato di default dalla v28 in poi)
- Street Fighter 6 su Steam
- Un progetto su [Google Cloud Console](https://console.cloud.google.com/) con l'API "YouTube Data API v3" abilitata, se vuoi usare l'upload automatico
- Un bot Telegram creato tramite [@BotFather](https://t.me/BotFather)

## 🚀 Installazione

1. **Installa REFramework nel gioco**
   Copia `dinput8.dll` nella cartella principale di Street Fighter 6 (dove si trova l'eseguibile del gioco). Al primo avvio del gioco, REFramework creerà da solo la cartella `reframework/`.

2. **Installa gli script Lua**
   Copia `orchestrator.lua` e `recon.lua` dentro `<cartella SF6>\reframework\autorun\`.

3. **Configura OBS**
   In OBS Studio vai su `Strumenti → Impostazioni WebSocket-obs` e assicurati che il server sia attivo sulla porta `4455` (o aggiorna `OBS_PORT` nello script se ne usi una diversa).

4. **Installa le dipendenze Python**
   Metti `SF6ReplayScript.py`, `youtube_uploader.py` e `SF6REPLAYTOOL_INSTALLER.bat` nella stessa cartella, poi fai click destro su `SF6REPLAYTOOL_INSTALLER.bat` → **Esegui come amministratore**.

5. **Configura le credenziali** (vedi sezione sotto)

6. **Avvia il bot**
   ```
   python SF6ReplayScript.py
   ```

## ⚙️ Configurazione

Apri `SF6ReplayScript.py` e imposta le variabili in cima al file:

```python
API_TOKEN = "IL_TUO_TOKEN_BOT_TELEGRAM"
MIO_ID_TELEGRAM = 123456789   # il tuo ID numerico Telegram (es. da @userinfobot)

OBS_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
QUEUE_FILE_PATH = r"D:\...\Street Fighter 6\reframework\data\replay_queue.json"
BASE_DIR_LUA = pathlib.Path(r"D:\...\Street Fighter 6\reframework\data")
```

Per l'upload su YouTube, scarica da Google Cloud Console il file delle credenziali OAuth e rinominalo `client_secrets.json`, mettendolo nella stessa cartella di `youtube_uploader.py`. Al primo upload il bot aprirà il browser per farti autorizzare l'app; da lì in poi userà il `token.json` generato automaticamente.

> ⚠️ **Attenzione, sicurezza**: `API_TOKEN`, `client_secrets.json` e `token.json` sono credenziali personali. **Non committarle mai su GitHub.** Se il repository è pubblico, aggiungi un file `.gitignore` con almeno:
> ```
> client_secrets.json
> token.json
> ```
> e sposta `API_TOKEN` in una variabile d'ambiente invece di lasciarlo scritto nel codice, ad esempio:
> ```python
> API_TOKEN = os.environ["SF6BOT_TELEGRAM_TOKEN"]
> ```

## 🕹️ Comandi Telegram

| Comando | Descrizione |
|---|---|
| `/status` | Mostra lo stato di SF6, OBS e la coda replay |
| `/avvia_gioco` | Apre OBS Studio e Street Fighter 6 |
| `/registra_replay ID1 ID2 ...` | Aggiunge uno o più replay alla coda di registrazione |
| `/stop` | Interrompe tutto e svuota la coda |
| `/spegni` | Spegne il PC da remoto (con 10 secondi di preavviso) |

## 🔧 Troubleshooting

- **Il bot non risponde ai comandi**: controlla che `MIO_ID_TELEGRAM` corrisponda al tuo vero ID Telegram.
- **Lo script si chiude subito dopo l'avvio**: lancialo da terminale (`python SF6ReplayScript.py`), non con doppio click, per vedere il messaggio di errore reale invece che una finestra che sparisce.
- **`ModuleNotFoundError: No module named 'youtube_uploader'`**: `youtube_uploader.py` deve stare nella stessa cartella di `SF6ReplayScript.py`.
- **Errore `invalid_scope` durante il login Google**: cancella `token.json` e rifai il login: potrebbe essere rimasto un token generato con un permesso OAuth diverso da quello attuale.
- **L'orchestratore in-game si blocca dopo un aggiornamento di SF6**: le patch di Capcom possono rinominare le schermate interne del gioco. Controlla le costanti `F_*` in cima a `orchestrator.lua`.

## 📄 Licenza
Questo progetto è rilasciato sotto licenza **MIT**.
