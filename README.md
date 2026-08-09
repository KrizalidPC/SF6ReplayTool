# SF6ReplayTool
 a system created to automatically record remote replays of the game SF6

 PRE REQUISITI
 -SF6
 -OBS
 -Python

TO DO
Wake On Lan

Posiziona il file installa_sf6_tool.bat sul Desktop (o nella cartella dove tieni il file SF6ReplayScript.py).Fai click destro sul file .bat e seleziona "Esegui come amministratore".Il terminale farà tutto da solo. Se Python è già installato, scaricherà le librerie e farà partire subito la schermata di configurazione dello SF6Replay tool per inserire Token, ID e percorsi.


# SF6 Automatic Replay Recorder Bot 🤖🎮

Un ecosistema di automazione in Python e LUA progettato per la registrazione, l'archiviazione e la catalogazione automatica dei replay di **Street Fighter 6** tramite **OBS Studio** e **REFramework**.

Inviando semplicemente uno o più ID dei replay nella chat del tuo Bot Telegram privato, il sistema si occuperà di avviare OBS Studio, lanciare il gioco tramite Steam, navigare i menu di gioco fino alla schermata di ricerca, riprodurre i replay in sequenza, registrare i match e rinominare i file video finali con i nomi reali dei giocatori e l'ID del match.

---

## ✨ Funzionalità principali

- **Automazione Totale dei Menu**: Grazie all'Orchestrator LUA, il gioco naviga autonomamente da qualsiasi schermata fino alla ricerca per ID, digita il codice e avvia il replay senza alcun input manuale.
- **Gestione Avanzata della Coda**: Supporto per l'invio multiplo di replay nello stesso comando Telegram. Il bot e lo script LUA li elaborano uno alla volta in background in modo sequenziale.
- **Sincronizzazione Frame-Perfect (Robust Handshake)**: 
  - Gestione nativa dell'errore `207 (OBS Not Ready)` con meccanismo di retry progressivo durante l'inizializzazione di OBS Studio.
  - Pulizia preventiva dei file di trigger temporanei ad ogni ciclo per evitare conflitti o falsi avvii.
- **Hook Nativo dei Match**: La registrazione OBS si avvia sul primo frame effettivo del round e si stoppa sull'ultimo frame dell'incontro, catturando solo il gameplay.
- **Prevenzione Conflitti File**: Rilevamento automatico dei file duplicati con l'applicazione di un numbering progressivo (es. `_1`, `_2`) per evitare sovrascritture.
- **Heartbeat di Sicurezza**: Monitoraggio continuo dello stato del gioco. Se il gioco si blocca o si disconnette, OBS interrompe in sicurezza la registrazione per evitare file corrotti o infiniti.
- **Telecomando PC Distante**: Comandi Telegram per controllare lo status dell'hardware, chiudere forzatamente i processi in blocco o spegnere il PC a fine sessione.

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

*   **Ottenere l'`API_TOKEN` (BotFather)**:
    1. Cerca `@BotFather` sulla barra di ricerca di Telegram e avvia la chat.
    2. Invia il comando `/newbot` e segui le istruzioni (scegli un nome visibile e uno username univoco che termini con `_bot`).
    3. Copia l'**HTTP API Token** generato (avrà una struttura simile a: `8847223467:AAHwqf...`).
*   **Ottenere il tuo `MIO_ID_TELEGRAM`**:
    1. Cerca `@userinfobot` su Telegram e avvia la chat.
    2. Invia un qualsiasi messaggio o il comando `/start`.
    3. Il bot ti risponderà mostrando il tuo **ID numerico privato** (es: `124120653`). Copialo.

### 2. Configurazione di OBS Studio
Il bot deve poter comunicare con OBS tramite WebSocket e gestire correttamente i file video generati.

*   **Attivare il WebSocket**:
    1. Apri OBS Studio e vai su **Strumenti** -> **Impostazioni server WebSocket**.
    2. Spunta la voce **Abilita server WebSocket**.
    3. Configura la **Porta del server** (di default è `4455`).
    4. È consigliato lasciare attiva l'autenticazione e generare una password. Se decidi di disattivarla, ricordati di lasciare la variabile `OBS_PASSWORD = ""` all'interno dello script Python.
*   **Impostazioni di Output (Video)**:
    1. Vai in **Impostazioni** -> **Uscita** -> scheda **Registrazione**.
    2. Imposta il **Formato di registrazione** su `MP4` o `MKV`.
    3. Prendi nota del **Percorso di registrazione** (la cartella in cui OBS salva i video), poiché è lì che lo script Python cercherà i file per rinominarli con i dati reali del match.

---

## 🎮 Struttura e Configurazione lato Gioco (REFramework & LUA)

L'automazione all'interno del motore grafico del gioco è gestita da due script LUA che comunicano costantemente con la controparte in Python attraverso file JSON di stato memorizzati nella cartella `reframework/data/`.

### I file LUA inclusi
All'interno della repository trovi due file LUA che devono essere inseriti nella cartella `<Cartella Gioco>\reframework\autorun\`:

1.  **`orchestrator.lua`**: Implementa una macchina a stati complessa che analizza i flussi dell'interfaccia utente di gioco (`app.UIFlowManager`). Inietta input di tastiera virtuali a basso livello per navigare i menu, stabilizzare le transizioni della UI, inserire l'ID nella casella di testo corretta e avviare il replay. Integra un pannello ImGui interno al gioco per monitorare lo stato della coda in tempo reale.
2.  **`recon.lua`**: Si aggancia (`hook`) ai metodi di riproduzione nativi del gioco (`BattleReplayController` e `BattleReplayDataManager`). Estrae in tempo reale i metadati dell'incontro (ID, Nickname reali dei giocatori, ID dei personaggi scelti) e scrive i trigger di avvio/arresto (`start` / `stop`) captati all'esatto primo e ultimo frame del match, sincronizzando OBS al millisecondo. Genera inoltre il ciclo di *heartbeat* a 60 FPS.

### Flusso di Comunicazione dei File di Stato
Il coordinamento tra Python e il gioco avviene tramite tre file nella cartella `reframework/data/`:
-   `replay_queue.json`: Scritto da Python, contiene la lista degli ID in attesa che l'Orchestrator LUA deve processare.
-   `obs_trigger.json`: Scritto da `recon.lua`, notifica a Python l'esatto momento in cui avviare o stoppare la registrazione OBS, allegando i metadati estratti dal gioco.
-   `obs_heartbeat.json`: Scritto da `recon.lua` ogni 60 frame durante il match per certificare che il gioco sia reattivo.

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
L'installer si occuperà in automatico di verificare Python, aggiornare `pip`, installare i pacchetti necessari (`pytelegrambotapi`, `psutil`, `obsws-python`, `pygetwindow`, `pywinauto`) e avviare l'istanza del bot.

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
> **Tu**: `/registra_replay WD544B58N`
> 
> **Bot**: 📝 Aggiunti `1` replay alla lista d'attesa. Totale in coda: `1`
> 
> **Bot**: 🔄 Elaborazione coda: inizio registrazione del replay `WD544B58N`. Rimanenti in lista: 0
> 
> **Bot**: 🔴 REC Partito: ChangeTime vs rappz (ID: WD544B58N)
> 
> **Bot**: 📁 Video salvato e rinominato (replay end): ChangeTime vs rappz WD544B58N.mp4
> 
> **Bot**: 🏁 Replay `WD544B58N` completato con successo.

---

## 🛠️ Risoluzione dei Problemi (Troubleshooting)

- **Il replay salta subito e mostra un errore di heartbeat**: Controlla il valore di `HB_GRACE` nel codice Python. Se il tuo PC o la tua connessione impiegano molto tempo a caricare i menu o i caricamenti interni di SF6, aumenta questo valore (attualmente impostato a `40` secondi) per dare più tolleranza alla mod LUA prima che generi il primo file di battito cardiaco.
- **OBS si apre ma il bot continua a mostrare errori di connessione**: Verifica che la password WebSocket inserita in `OBS_PASSWORD` sia identica a quella impostata nei menu di OBS Studio.
- **L'Orchestrator LUA si blocca nei menu**: I nomi dei flussi interni della UI di Capcom (es. `app.menu.UIFlowTitle.Param`) possono subire variazioni a seguito di aggiornamenti o patch importanti di *Street Fighter 6*. In caso di blocchi post-aggiornamento, procedi in questo modo:
  1. Apri il menu in-game di **REFramework** (tasto `Insert` di default).
  2. Usa lo strumento **Object Explorer** per identificare i flussi della UI attivi in quel momento.
  3. Verifica e correggi le costanti `F_*` posizionate all'inizio del file `orchestrator.lua` inserendo i nuovi nomi dei flussi.

