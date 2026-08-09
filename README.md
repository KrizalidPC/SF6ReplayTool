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

Un bot Python per Telegram progettato per automatizzare la registrazione dei replay di **Street Fighter 6** tramite **OBS Studio** e la mod **REFramework (LUA)**. 

Inviando semplicemente uno o più ID dei replay in chat, il bot si occupa di avviare OBS Studio, lanciare il gioco tramite Steam, sincronizzarsi con la mod LUA per far partire il match, registrare l'incontro e rinominare automaticamente il file video finale con i nomi dei giocatori e l'ID del match.

---

## ✨ Funzionalità principali

- **Automazione Totale**: Avvio sequenziale automatico di OBS Studio e Street Fighter 6 se rilevati come chiusi nel sistema.
- **Gestione della Coda**: Supporto per l'invio multiplo di replay nello stesso comando. Il bot li elabora uno alla volta in background senza sovrapposizioni.
- **Sincronizzazione Intelligente (Robust Handshake)**: 
  - Gestione dell'errore `207 (OBS Not Ready)` con tentativi di riconnessione progressivi finché l'interfaccia di OBS non è completamente carica.
  - Pulizia preventiva dei file di trigger temporanei ad ogni ciclo per evitare falsi avvii o conflitti di ID.
- **Prevenzione Conflitti File**: Sistema automatico di numbering progressivo (es. `_1`, `_2`) se esiste già un file video registrato con lo stesso nome.
- **Telecomando PC Integrato**: Comandi per controllare lo status dei programmi, chiudere forzatamente i processi in blocco o spegnere il PC a distanza.

---

## 📋 Prerequisiti

Prima di avviare il bot, assicurati di avere installato e configurato i seguenti componenti sul tuo PC Windows:

1. **Python 3.10+** (ricordati di spuntare la casella *"Add python.exe to PATH"* durante l'installazione).
2. **OBS Studio** con il plugin **WebSocket** abilitato (incluso nativamente in OBS 28+).
3. **Street Fighter 6** su Steam.
4. **REFramework** installato nella cartella del gioco con la mod LUA dedicata alla gestione dei replay (che legge/scrive i file `obs_trigger.json` e `obs_heartbeat.json`).

---

## ⚙️ Guida alle Configurazioni Preliminari

### 1. Come ottenere il Token e l'ID Telegram
Per far funzionare lo script, devi creare un bot e ricavare il tuo ID utente per fare in modo che solo tu possa controllarlo.

*   **Ottenere l'`API_TOKEN` (BotFather)**:
    1. Cerca `@BotFather` su Telegram e avvia la chat.
    2. Invia il comando `/newbot` e segui le istruzioni (scegli un nome e uno username per il tuo bot).
    3. Copia l'**HTTP API Token** generato (es: `8847223467:AAHwqf...`).
*   **Ottenere il tuo `MIO_ID_TELEGRAM`**:
    1. Cerca `@userinfobot` (o `@MissRose_bot`) su Telegram e avvia la chat.
    2. Invia un qualsiasi messaggio o il comando `/start`.
    3. Il bot ti risponderà mostrando il tuo **ID numerico** (es: `124120653`). Copialo.

### 2. Configurazione di OBS Studio
Il bot deve poter comunicare con OBS e gestire correttamente i file video generati.

*   **Attivare il WebSocket**:
    1. Apri OBS Studio e vai su **Strumenti** -> **Impostazioni server WebSocket**.
    2. Spunta la voce **Abilita server WebSocket**.
    3. Segna il numero della **Porta del server** (di default è `4455`).
    4. Se desideri una maggiore sicurezza, lascia attiva l'autenticazione e genera una password, altrimenti rimuovi la spunta da *Abilita autenticazione* (se la disattivi, lascia `OBS_PASSWORD = ""` nello script).
*   **Impostazioni di Output (Video)**:
    1. Vai in **Impostazioni** -> **Uscita** -> scheda **Registrazione**.
    2. Imposta il **Formato di registrazione** su `MP4` o `MKV` (lo script supporta nativamente l'estensione rilevata).
    3. Prendi nota del **Percorso di registrazione** (la cartella in cui OBS salva i video), poiché è lì che lo script cercherà i file per rinominarli.

---

## 🚀 Installazione e Configurazione dello Script

### 1. Clonare la repository e posizionare i file
Scarica o clona questa repository sul tuo PC, assicurandoti che il file di installazione `.bat` e lo script `.py` si trovino nella stessa cartella:
```bash
git clone https://github.com
cd SF6-Replay-Recorder
```

### 2. Modifica del file Python
Apri il file `SF6ReplayScript.py` con un editor di testo e compila le variabili iniziali inserendo i dati raccolti nei passaggi precedenti:

```python
# Configurazione Telegram
API_TOKEN = "IL_TUO_TOKEN_BOT_TELEGRAM" 
MIO_ID_TELEGRAM = IL_TUO_ID_TELEGRAM 

# Configurazione OBS WebSocket
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "LA_TUA_PASSWORD_WEBSOCKET_OBS" # Lascia vuoto "" se disattivata in OBS
OBS_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"

# Percorsi di gioco (Modifica la lettera del disco se necessario, es: C: o D:)
QUEUE_FILE_PATH = r"D:\SteamLibrary\steamapps\common\Street Fighter 6\reframework\data\replay_queue.json"
BASE_DIR_LUA = pathlib.Path(r"D:\SteamLibrary\steamapps\common\Street Fighter 6\reframework\data")
```

### 3. Installazione automatica delle dipendenze
Fai click destro sul file `SF6Replay Tool - Installer Automatico.bat` e seleziona **"Esegui come amministratore"**. 
L'installer si occuperà in automatico di:
- Verificare la presenza di Python nel sistema.
- Aggiornare `pip`.
- Installare tutti i pacchetti necessari (`pytelegrambotapi`, `psutil`, `obsws-python`, `pygetwindow`, `pywinauto`).
- Avviare la prima esecuzione dello script.

---

## 🕹️ Comandi del Bot Telegram

Il bot imposterà automaticamente il menu dei comandi rapidi alla prima esecuzione. Puoi interagire con lui usando i seguenti input:

| Comando | Descrizione |
| :--- | :--- |
| `/status` | Mostra se SF6 e OBS sono aperti, lo stato della connessione WebSocket e il numero di replay in coda. |
| `/avvia_gioco` | Forza l'apertura manuale di OBS Studio e di Street Fighter 6 tramite Steam. |
| `/registra_replay <ID_1> <ID_2>` | Accoda uno o più ID (separati da uno spazio) per avviare la sequenza di registrazione automatica. |
| `/stop` | Forza la chiusura immediata di SF6 e OBS, interrompe la registrazione e svuota la coda d'attesa. |
| `/spegni` | Avvia un timer di 10 secondi e spegne completamente il PC di casa. |

### Esempio di scenario in chat:
> **Tu**: `/registra_replay WD544B58N TGKY8EKS3`
> 
> **Bot**: 📝 Aggiunti `2` replay alla lista d'attesa. Totale in coda: `2`
> 
> **Bot**: 🔄 Elaborazione coda: inizio registrazione del replay `WD544B58N`. Rimanenti in lista: 1
> 
> **Bot**: 🔴 REC Partito: Player1 vs Player2 (ID: WD544B58N)
> 
> **Bot**: 📁 Video salvato e rinominato (replay end): Player1 vs Player2 WD544B58N.mp4
> 
> **Bot**: 🏁 Replay `WD544B58N` completato con successo.

---

## 📝 Licenza
Questo progetto è rilasciato sotto licenza MIT.
