import time
import os
import subprocess
import telebot
from telebot import types
import psutil
import webbrowser
import json  
import pathlib
import re
import threading
import obsws_python as obs

# ==========================================
# CONFIGURAZIONE DATI PERSONALI E PERCORSI
# ==========================================
API_TOKEN = "InsertBOTFatherTokenHERE" 
MIO_ID_TELEGRAM = YourIDHere 

SF6_STEAM_URL = "steam://rungameid/1364780"
OBS_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"

# PERCORSI SUL TUO SECONDO HARD DISK (D:)
QUEUE_FILE_PATH = r"D:\SteamLibrary\steamapps\common\Street Fighter 6\reframework\data\replay_queue.json"
BASE_DIR_LUA = pathlib.Path(r"D:\SteamLibrary\steamapps\common\Street Fighter 6\reframework\data")
TRIG_PATH = BASE_DIR_LUA / "obs_trigger.json"
HB_PATH = BASE_DIR_LUA / "obs_heartbeat.json"

# Configurazione OBS WebSocket
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "" # Lascia vuoto se hai disattivato l'autenticazione nelle impostazioni di OBS

# Limiti di sicurezza e heartbeat presi dal codice originale di GitHub
MAX_SECONDS = 600
HB_TIMEOUT = 8
HB_GRACE = 15
# ==========================================

bot = telebot.TeleBot(API_TOKEN)
cl = None 

last, pending, recording, rec_started = -1, {}, False, 0.0
coda_replay = []
in_elaborazione = False

def clean(s):
    s = (s or "").strip()
    return re.sub(r'[\\/:*?"<>|]', "_", s) or "unknown"

def hb_age():
    try:
        return time.time() - json.loads(HB_PATH.read_text(encoding="utf-8")).get("t", 0)
    except Exception:
        return 9999

def do_stop(reason):
    global recording, cl
    if not recording or not cl:
        return
    try:
        resp = cl.stop_record()
        src = pathlib.Path(resp.output_path)
        p1, p2 = clean(pending.get("p1")), clean(pending.get("p2"))
        rid = (pending.get("id") or "").strip()
        
        # Nome base generato per il replay
        base_name = f"{p1} vs {p2} {clean(rid) if rid else int(time.time())}"
        suffix = src.suffix
        
        rinominato = False
        for tentativo in range(5):
            print(f"Attendo che OBS rilasci il file... Tentativo {tentativo + 1}/5")
            time.sleep(2.0)
            try:
                # --- GESTIONE DEI FILE DUPLICATI (Risolve WinError 183) ---
                dst = src.with_name(f"{base_name}{suffix}")
                
                # Se il file esiste già, aggiungiamo un contatore progressivo (es: _1, _2)
                contatore = 1
                while dst.exists():
                    dst = src.with_name(f"{base_name}_{contatore}{suffix}")
                    contatore += 1
                # ----------------------------------------------------------

                src.rename(dst)
                msg_salvato = f"Video salvato e rinominato ({reason}): {dst.name}"
                print(msg_salvato)
                bot.send_message(MIO_ID_TELEGRAM, f"📁 {msg_salvato}")
                rinominato = True
                break
            except PermissionError:
                # OBS potrebbe avere ancora il file bloccato in scrittura, riprova al prossimo ciclo
                continue
            except Exception as e:
                print(f"Errore generico durante la ridenominazione: {e}")
                break
                
        if not rinominato:
            bot.send_message(MIO_ID_TELEGRAM, f"⚠️ OBS ha impiegato troppo tempo a chiudere il video. Lo trovi come: `{src.name}`")

    except Exception as e:
        print("Richiesta di stop a OBS fallita o ignorata:", e)
    finally:
        recording = False

def obs_watcher_loop():
    global last, pending, recording, rec_started, cl
    print("🤖 Thread di monitoraggio OBS avviato. In ascolto per l'apertura del programma...")
    
    # --- NUOVA LOGICA DI ATTESA SILENZIOSA ---
    mostrato_avviso_attesa = False
    
    while cl is None:
        # Controlliamo prima se l'eseguibile di OBS è aperto in Windows
        if not processo_in_esecuzione("obs64.exe"):
            if not mostrato_avviso_attesa:
                print("⏳ OBS Studio è chiuso. Il bot rimarrà in attesa silenziosa finché non lo avvii...")
                mostrato_avviso_attesa = True
            time.sleep(5)  # Aspetta 5 secondi prima di ricontrollare se hai aperto OBS
            continue
        
        # Se siamo qui, il processo obs64.exe è stato rilevato! Proviamo a connetterci
        try:
            print("🚀 OBS Studio rilevato in esecuzione! Tento la sincronizzazione WebSocket...")
            # Tentativo mirato senza inondare la console di errori traceback
            cl = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD, timeout=3)
            versione = cl.get_version()
            print(f"✅ Sincronizzazione WebSocket con OBS Studio riuscita! (Versione OBS: {versione.obs_version})")
            bot.send_message(MIO_ID_TELEGRAM, f"✅ Sincronizzazione stabilita con OBS Studio (Porta: {OBS_PORT})")
        except Exception:
            print("⏳ OBS si sta ancora caricando o il server WebSocket non è pronto. Riprovo tra 4 secondi...")
            mostrato_avviso_attesa = False  # Resetta lo stato se OBS dovesse essere chiuso improvvisamente
            time.sleep(4)

    # --- FINE LOGICA DI ATTESA (Il resto rimane invariato) ---
    try:
        if TRIG_PATH.exists():
            last = json.loads(TRIG_PATH.read_text(encoding="utf-8")).get("seq", -1)
    except Exception:
        pass

    while True:
        try:
            if recording:
                age = time.time() - rec_started
                if age > MAX_SECONDS:
                    do_stop("absolute timeout")
                elif age > HB_GRACE and hb_age() > HB_TIMEOUT:
                    do_stop("heartbeat lost")

            if TRIG_PATH.exists():
                d = json.loads(TRIG_PATH.read_text(encoding="utf-8"))
                if d.get("seq", -1) != last:
                    last = d["seq"]
                    cmd = d.get("cmd")
                    
                    if cmd == "start":
                        pending = d
                        try:
                            cl.start_record()
                            recording = True
                            rec_started = time.time()
                            msg_start = f"🔴 REC Partito: {d.get('p1')} vs {d.get('p2')} (ID: {d.get('id')})"
                            print(msg_start)
                            bot.send_message(MIO_ID_TELEGRAM, msg_start)
                        except Exception as e:
                            print("Impossibile avviare la registrazione su OBS:", e)
                            
                    elif cmd == "stop":
                        if recording:
                            do_stop("replay end")
                            bot.send_message(MIO_ID_TELEGRAM, "Replay registrato correttamente")
                        else:
                            print("Comando stop ricevuto ma OBS non stava registrando.")
        except Exception:
            pass
        time.sleep(0.4)

def gestisci_coda_lavoro():
    global coda_replay, in_elaborazione, recording
    in_elaborazione = True
    
    while len(coda_replay) > 0:
        prossimo_id = coda_replay.pop(0)
        bot.send_message(MIO_ID_TELEGRAM, f"🔄 Elaborazione coda: inizio registrazione del replay `{prossimo_id}`. Rimanenti in lista: {len(coda_replay)}")
        
        dati_coda = {
            "ids": [prossimo_id],
            "current_index": 1
        }
        try:
            os.makedirs(os.path.dirname(QUEUE_FILE_PATH), exist_ok=True)
            with open(QUEUE_FILE_PATH, "w") as f:
                json.dump(dati_coda, f, indent=4)
        except Exception as e:
            bot.send_message(MIO_ID_TELEGRAM, f"❌ Errore scrittura JSON per ID `{prossimo_id}`: {e}")
            continue

        # Se il gioco è chiuso, lo avviamo
        if not processo_in_esecuzione("StreetFighter6.exe"):
            webbrowser.open(SF6_STEAM_URL)
            print("⏳ Avvio di Street Fighter 6 in corso... Attendo 45 secondi per il caricamento iniziale.")
            time.sleep(45)
        else:
            # Se il gioco è già aperto, diamo 5 secondi alla mod LUA per leggere il nuovo JSON
            time.sleep(5)
        
        # --- NUOVA LOGICA DI SINCRO REPLAY ---
        print(f"📡 Attendo che il replay {prossimo_id} inizi la registrazione...")
        # 1. Aspetta che OBS avvi la registrazione tramite l'hook nativo (max 60 secondi)
        timeout_inizio = time.time() + 60
        while not recording and time.time() < timeout_inizio:
            time.sleep(1)
            
        if not recording:
            print(f"⚠️ Timeout: Il replay {prossimo_id} non è partito o l'ID è invalido. Salto al prossimo.")
            bot.send_message(MIO_ID_TELEGRAM, f"⚠️ Il replay `{prossimo_id}` non è partito (ID errato o timeout caricamento).")
            continue

        print(f"🔴 Replay {prossimo_id} in corso di registrazione. Attendo la fine...")
        # 2. Rimani in questo punto finché OBS sta registrando il match
        while recording:
            time.sleep(1)
                
        bot.send_message(MIO_ID_TELEGRAM, f"🏁 Replay `{prossimo_id}` completato con successo.")
        print(f"✅ Replay {prossimo_id} terminato. Attendo 5 secondi di pausa prima del prossimo ID.")
        time.sleep(5) 
        
    bot.send_message(MIO_ID_TELEGRAM, "✅ Lista d'attesa svuotata! Tutti i replay sono stati registrati.")
    in_elaborazione = False


def imposta_menu_comandi():
    comandi = [
        types.BotCommand("status", "📊 Controlla lo stato del PC"),
        types.BotCommand("avvia_gioco", "🚀 Apri SF6 + OBS Studio"),
        types.BotCommand("registra_replay", "🎮 Registra Replay (Invia uno o più ID separati da spazio)"),
        types.BotCommand("stop", "🛑 Chiudi forzatamente e svuota coda"),
        types.BotCommand("spegni", "🔌 Spegni il PC di casa")
    ]
    bot.set_my_commands(comandi)

def utente_autorizzato(message):
    return message.from_user.id == MIO_ID_TELEGRAM

def processo_in_esecuzione(nome_processo):
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == nome_processo.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

@bot.message_handler(commands=['start', 'aiuto', 'status'])
def send_status(message):
    if not utente_autorizzato(message): return
    sf6_attivo = processo_in_esecuzione("StreetFighter6.exe")
    obs_attivo = processo_in_esecuzione("obs64.exe")
    stato_sf6 = "🟢 In esecuzione" if sf6_attivo else "🔴 Chiuso"
    stato_obs = "🟢 In esecuzione" if obs_attivo else "🔴 Chiuso"
    
    riepilogo = (
        "🖥️ *Riepilogo Status PC*\n\n"
        f"• *Street Fighter 6:* {stato_sf6}\n"
        f"• *OBS Studio:* {stato_obs}\n"
        f"• *Connessione WebSocket:* {'🟢 Sincronizzato' if cl else '🔴 Disconnesso'}\n"
        f"• *Replay in coda d'attesa:* `{len(coda_replay)}`\n\n"
        "Invia `/registra_replay ID1 ID2` per accodare più match."
    )
    bot.reply_to(message, riepilogo, parse_mode='Markdown')

@bot.message_handler(commands=['avvia_gioco'])
def avvia_gioco_e_obs(message):
    if not utente_autorizzato(message): return
    bot.reply_to(message, "⏳ Apertura di OBS Studio e Street Fighter 6...")
    
    if not processo_in_esecuzione("obs64.exe"):
        if os.path.exists(OBS_PATH):
            obs_dir = os.path.dirname(OBS_PATH)
            subprocess.Popen(OBS_PATH, cwd=obs_dir)
            # Abbiamo rimosso la connessione istantanea qui, se ne occuperà in automatico l'obs_watcher_loop in background
            time.sleep(3)
        else:
            bot.reply_to(message, f"❌ Errore: OBS non trovato su:\n`{OBS_PATH}`", parse_mode='Markdown')
            return
        
    if not processo_in_esecuzione("StreetFighter6.exe"):
        webbrowser.open(SF6_STEAM_URL)
        
@bot.message_handler(commands=['registra_replay'])
def registra_replay_id(message):
    if not utente_autorizzato(message): 
        return
    
    input_testo = message.text.split()
    if len(input_testo) < 2:
        bot.reply_to(message, "❌ Specifica almeno un ID! Es: `/registra_replay ABCD1234 EFGH5678`")
        return
        
    nuovi_id = [str(x).strip().upper() for x in input_testo[1:]]
    
    global coda_replay, in_elaborazione
    coda_replay.extend(nuovi_id)
    
    bot.reply_to(message, f"📝 Aggiunti `{len(nuovi_id)}` replay alla lista d'attesa. Totale in coda: `{len(coda_replay)}`", parse_mode='Markdown')

    if not in_elaborazione:
        thread_coda = threading.Thread(target=gestisci_coda_lavoro, daemon=True)
        thread_coda.start()

@bot.message_handler(commands=['stop'])
def stop_everything(message):
    if not utente_autorizzato(message): 
        return
    global coda_replay, cl
    coda_replay = []
    bot.reply_to(message, "⚠️ Chiusura forzata in corso e lista d'attesa SVUOTATA...")
    
    if recording:
        do_stop("forced stop")
        
    os.system("taskkill /f /im StreetFighter6.exe")
    os.system("taskkill /f /im obs64.exe")
    cl = None  # Resettiamo la connessione OBS per il loop di ripristino
    bot.reply_to(message, "🛑 Tutti i processi interrotti e coda azzerata.")

@bot.message_handler(commands=['spegni'])
def shutdown_pc(message):
    if not utente_autorizzato(message): 
        return
    bot.reply_to(message, "🔌 Il PC di casa si spegnerà tra 10 secondi.")
    time.sleep(10)
    os.system("shutdown /s /t 1")

# ==========================================
# BLOCCO DI AVVIO PRINCIPALE CON INDENTAZIONE CORRETTA
# ==========================================
if __name__ == "__main__":
    imposta_menu_comandi()
    
    watcher_thread = threading.Thread(target=obs_watcher_loop, daemon=True)
    watcher_thread.start()
    
    try:
        bot.send_message(MIO_ID_TELEGRAM, "🚀 Il PC di casa è acceso! Il telecomando unificato con OBS WebSocket è attivo.")
    except Exception as e:
        print(f"Impossibile inviare la notifica di avvio: {e}")
        
    bot.infinity_polling()
