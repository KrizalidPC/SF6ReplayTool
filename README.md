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

Inviando semplicemente l'ID di un replay in chat, il bot si occupa di avviare OBS Studio, lanciare il gioco tramite Steam, sincronizzarsi con la mod LUA per far partire il match, registrare l'incontro e rinominare automaticamente il file video finale con i nomi dei giocatori e l'ID del replay.

---

## ✨ Funzionalità principali

- **Automazione Totale**: Avvio sequenziale automatico di OBS Studio e Street Fighter 6 se rilevati come chiusi.
- **Gestione della Coda**: Supporto per l'invio multiplo di replay. Il bot li elabora uno alla volta in background senza sovrapposizioni.
- **Sincronizzazione Intelligente (Robust Handshake)**: 
  - Gestione dell'errore `207 (OBS Not Ready)` con tentativi di riconnessione progressivi finché l'interfaccia di OBS non è completamente carica.
  - Pulizia preventiva dei file di trigger temporanei per evitare falsi avvii o conflitti di ID.
- **Prevenzione Falsi Stop (Heartbeat Grace)**: Sistema tollerante ai lunghi caricamenti iniziali delle partite per evitare interruzioni premature del video.
- **Notifiche in Tempo Reale**: Messaggi di stato su Telegram per l'inizio della registrazione, timeout ed elaborazione completata.

---

## 📋 Prerequisiti

Prima di avviare il bot, assicurati di avere installato e configurato i seguenti componenti sul tuo PC Windows:

1. **Python 3.10+** (assicurati di averlo aggiunto al PATH di sistema).
2. **OBS Studio** con il plugin **WebSocket** abilitato (incluso nativamente in OBS 28+).
3. **Street Fighter 6** su Steam.
4. **REFramework** installato nella cartella del gioco con la mod LUA dedicata alla gestione dei replay (che legge/scrive i file `obs_trigger.json` e `obs_heartbeat.json`).

---

## 🚀 Installazione e Configurazione

### 1. Clonare la repository
```bash
git clone https://github.com
cd SF6-Replay-Recorder
```

### 2. Installare le dipendenze Python
Installa i pacchetti richiesti tramite `pip`:
```bash
pip install pyTelegramBotAPI obsws-python
```

### 3. Configurazione del file di script
Apri il file principale Python (`main.py` o il nome che hai assegnato) e compila le variabili di configurazione iniziali con i tuoi dati:

```python
# Configurazione Telegram
TELEGRAM_TOKEN = "IL_TUO_TOKEN_BOT_TELEGRAM"
MIO_ID_TELEGRAM = 123456789  # Il tuo ID utente Telegram

# Configurazione OBS WebSocket
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "LA_TUA_PASSWORD_WEBSOCKET_OBS"
OBS_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"

# Configurazione Gioco e Percorsi Mod LUA
SF6_STEAM_URL = "steam://rungameid/1364780"
QUEUE_FILE_PATH = r"C:\Percorso\Aria\REFramework\data\obs_queue.json"
TRIG_PATH = Path(r"C:\Percorso\Aria\REFramework\data\obs_trigger.json")
HB_PATH = Path(r"C:\Percorso\Aria\REFramework\data\obs_heartbeat.json")
```

---

## 🕹️ Utilizzo

1. Configura OBS impostando la tua scena di cattura gioco preferita e assicurati che il server WebSocket sia attivo sulla porta indicata.
2. Avvia lo script Python:
   ```bash
   python main.py
   ```
3. Apri la chat del tuo Bot su Telegram e usa i seguenti comandi:

| Comando | Descrizione |
| :--- | :--- |
| `/start` | Inizializza il bot e mostra il messaggio di benvenuto. |
| `/registra_replay <ID_REPLAY>` | Aggiunge l'ID (o più ID separati da spazio) alla coda di registrazione e avvia il processo automatico. |

### Esempio di utilizzo in chat:
> **Tu**: `/registra_replay WD544B58N TGKY8EKS3`
> 
> **Bot**: 📝 Aggiunti 2 replay alla lista d'attesa. Totale in coda: 2
> 
> **Bot**: 🔄 Elaborazione coda: inizio registrazione del replay `WD544B58N`. Rimanenti in lista: 1
> 
> **Bot**: 🏁 Replay `WD544B58N` completato con successo.

---

## 🛠️ Risoluzione dei Problemi (Troubleshooting)

- **Il replay salta subito e mostra "heartbeat lost"**: Controlla il valore di `HB_GRACE` nel codice. Se il tuo PC o la tua connessione impiegano molto tempo a caricare il match di SF6, potrebbe essere necessario aumentare questo valore (attualmente ottimizzato a `40` secondi).
- **OBS si apre ma il bot si blocca**: Assicurati che la password in `OBS_PASSWORD` coincida perfettamente con quella impostata in *Strumenti -> Impostazioni server WebSocket* all'interno di OBS Studio.
- **I codici non vengono letti dal gioco**: Verifica che il percorso in `QUEUE_FILE_PATH` punti esattamente alla cartella `data` all'interno della struttura di REFramework di SF6.

---

## 📝 Licenza
Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per ulteriori dettagli.
