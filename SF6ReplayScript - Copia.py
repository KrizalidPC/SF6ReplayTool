import os
import time
import json
import pathlib
import subprocess
import webbrowser
import telebot
import threading
import psutil
from pathlib import Path
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from youtube_uploader import carica_su_youtube

# ==========================================
# CONFIGURAZIONE STRUTTURALE (DA COMPILARE)
# ==========================================

# Configurazione Telegram (Ottenuti da BotFather e UserInfoBot)
API_TOKEN = "TOKENBOTFATHER" 
MIO_ID_TELEGRAM = YourIDHERE 

# Configurazione OBS WebSocket
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "LA_TUA_PASSWORD_WEBSOCKET_OBS"
OBS_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"

# Percorsi di gioco (Modifica in base alla tua installazione)
QUEUE_FILE_PATH = r"D:\SteamLibrary\steamapps\common\Street Fighter 6\reframework\data\replay_queue.json"
BASE_DIR_LUA = pathlib.Path(r"D:\SteamLibrary\steamapps\common\Street Fighter 6\reframework\data")

# Parametri di controllo
SF6_STEAM_URL = "steam://rungameid/1364780"
MAX_SECONDS = 600
HB_TIMEOUT = 8
HB_GRACE = 40  # Tolleranza caricamento iniziale

# File di stato generati dalla mod LUA
TRIG_PATH = BASE_DIR_LUA / "obs_trigger.json"
HB_PATH = BASE_DIR_LUA / "obs_heartbeat.json"
BASE_DIR_VIDEO = pathlib.Path(r"C:\Users\IO\Videos")  # Cartella output OBS

# ==========================================
# VARIABILI DI STATO INTERNE
# ==========================================
bot = telebot.TeleBot(API_TOKEN)
coda_replay = []
in_elaborazione = False
recording = False
video_in_attesa_approvazione = {}

def processo_in_esecuzione(nome_processo):
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() == nome_processo.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def gestisci_coda_lavoro():
    global coda_replay, in_elaborazione, recording
    in_elaborazione = True
    
    while len(coda_replay) > 0:
        prossimo_id = coda_replay.pop(0)
        bot.send_message(MIO_ID_TELEGRAM, f"🔄 Elaborazione coda: inizio registrazione del replay `{prossimo_id}`. Rimanenti in lista: {len(coda_replay)}")
        
        # Pulizia preventiva dei file di stato precedenti
        try:
            if TRIG_PATH.exists(): TRIG_PATH.unlink()
            if HB_PATH.exists(): HB_PATH.unlink()
            print("🧹 File di trigger e heartbeat precedenti ripuliti.")
        except Exception as e:
            print(f"Avviso pulizia file temporanei: {e}")

        dati_coda = {"ids": [prossimo_id], "current_index": 1}
        try:
            os.makedirs(os.path.dirname(QUEUE_FILE_PATH), exist_ok=True)
            with open(QUEUE_FILE_PATH, "w") as f:
                json.dump(dati_coda, f, indent=4)
        except Exception as e:
            bot.send_message(MIO_ID_TELEGRAM, f"❌ Errore scrittura JSON per ID `{prossimo_id}`: {e}")
            continue

        # Avvio condizionale OBS Studio
        if not processo_in_esecuzione("obs64.exe"):
            if os.path.exists(OBS_PATH):
                bot.send_message(MIO_ID_TELEGRAM, "⏳ OBS Studio risulta chiuso. Lo sto avviando automaticamente...")
                subprocess.Popen(OBS_PATH, cwd=os.path.dirname(OBS_PATH))
                time.sleep(5)
            else:
                bot.send_message(MIO_ID_TELEGRAM, f"❌ Impossibile avviare OBS. Percorso non trovato:\n`{OBS_PATH}`")
                in_elaborazione = False
                return

        # Avvio condizionale Street Fighter 6
        if not processo_in_esecuzione("StreetFighter6.exe"):
            webbrowser.open(SF6_STEAM_URL)
            print("⏳ Avvio di Street Fighter 6 in corso... Attendo il caricamento iniziale.")
            time.sleep(60) 
        else:
            time.sleep(6)
        
        # Sincronizzazione avvio replay
        print(f"📡 Attendo che il replay {prossimo_id} inizi la registrazione...")
        timeout_inizio = time.time() + 90  
        while not recording and time.time() < timeout_inizio:
            time.sleep(1)
            
        if not recording:
            print(f"⚠️ Timeout: Il replay {prossimo_id} non è partito.")
            bot.send_message(MIO_ID_TELEGRAM, f"⚠️ Il replay `{prossimo_id}` non è partito (ID errato o timeout caricamento).")
            continue

        print(f"🔴 Replay {prossimo_id} in corso di registrazione. Attendo la fine...")
        while recording:
            time.sleep(1)
                
        # --- CONFIGURAZIONE RICHIESTA DI CONFERMA UPLOAD ---
        # (Qui andrebbe valorizzato l'oggetto con i metadati reali estratti, impostiamo dei fallback per sicurezza)
        nuovo_nome_video = f"Replay_{prossimo_id}.mp4" 
        percorso_video_effettivo = BASE_DIR_VIDEO / nuovo_nome_video
        
        video_in_attesa_approvazione[prossimo_id] = {
            "percorso": percorso_video_effettivo,
            "titolo": f"SF6 Replay | Match ID {prossimo_id}",
            "descrizione": f"Replay ID: {prossimo_id}\n\nRegistrato automaticamente da SF6 Replay Bot.",
            "tag": ["Street Fighter 6", "SF6", "Replay", prossimo_id]
        }
        
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("✅ Sì, Carica", callback_data=f"yt_yes:{prossimo_id}"),
            InlineKeyboardButton("❌ No, Salta", callback_data=f"yt_no:{prossimo_id}")
        )
        
        testo_notifica = f"🏁 Replay `{prossimo_id}` registrato!\nVuoi caricarlo su YouTube come 'Non in elenco'?"
        bot.send_message(MIO_ID_TELEGRAM, testo_notifica, reply_markup=markup, parse_mode="Markdown")
        
        print(f"✅ Replay {prossimo_id} terminato. Richiesta inviata. Attendo pausa...")
        time.sleep(8) 
        
    in_elaborazione = False

def thread_upload_youtube(chat_id, message_id, replay_id, dati_video):
    """Esegue l'upload in background per evitare il timeout di Telegram"""
    bot.edit_message_text(f"🚀 Upload in corso su YouTube per il replay `{replay_id}`...", chat_id, message_id)
    
    url_youtube = carica_su_youtube(
        percorso_video=dati_video["percorso"],
        titolo=dati_video["titolo"],
        descrizione=dati_video["descrizione"],
        tag=dati_video["tag"],
        privacy="unlisted"
    )
    
    if url_youtube:
        bot.edit_message_text(f"📺 Caricato con successo su YouTube per il replay `{replay_id}`!\n🔗 Link: {url_youtube}", chat_id, message_id)
    else:
        bot.edit_message_text(f"❌ Upload fallito su YouTube per il replay `{replay_id}`. Il file locale è comunque salvo.", chat_id, message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith(('yt_yes:', 'yt_no:')))
def gestisci_conferma_youtube(call):
    if call.from_user.id != MIO_ID_TELEGRAM:
        bot.answer_callback_query(call.id, "⚠️ Non sei autorizzato.", show_alert=True)
        return

    azione, replay_id = call.data.split(":")
    dati_video = video_in_attesa_approvazione.pop(replay_id, None)
    
    if azione == "yt_yes":
        if dati_video and os.path.exists(dati_video["percorso"]):
            bot.answer_callback_query(call.id, "🚀 Avvio dell'upload...")
            t = threading.Thread(target=thread_upload_youtube, args=(call.message.chat.id, call.message.message_id, replay_id, dati_video))
            t.start()
        else:
            bot.answer_callback_query(call.id, "❌ File non trovato.", show_alert=True)
            bot.edit_message_text(f"⚠️ Impossibile caricare il replay `{replay_id}`: file non trovato.", call.message.chat.id, call.message.message_id)
    elif azione == "yt_no":
        bot.answer_callback_query(call.id, "🗑️ Upload annullato.")
        bot.edit_message_text(f"📁 Replay `{replay_id}` salvato esclusivamente in locale.", call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['registra_replay'])
def cmd_registra(message):
    if message.from_user.id != MIO_ID_TELEGRAM: return
    ids = message.text.split()[1:]
    if not ids:
        bot.reply_to(message, "⚠️ Specifica almeno un ID. Es: /registra_replay ID1 ID2")
        return
    
    global coda_replay
    coda_replay.extend(ids)
    bot.reply_to(message, f"📝 Aggiunti `{len(ids)}` replay alla lista d'attesa. Totale in coda: `{len(coda_replay)}`")
    
    if not in_elaborazione:
        t = threading.Thread(target=gestisci_coda_lavoro)
        t.start()

if __name__ == "__main__":
    print("🤖 Bot Telegram in ascolto...")
    bot.infinity_polling()
