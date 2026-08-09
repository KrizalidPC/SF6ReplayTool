import os
import pathlib
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def carica_su_youtube(percorso_video, titolo, descrizione, tag=None, privacy="unlisted"):
    """
    Effettua l'upload di un video su YouTube utilizzando le API v3 ufficiali.
    Privacy options: 'public', 'private', 'unlisted'
    """
    credenziali = None
    if os.path.exists('token.json'):
        credenziali = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    if not credenziali or not credenziali.valid:
        if credenziali and credenziali.expired and credenziali.refresh_token:
            credenziali.refresh(Request())
        else:
            if not os.path.exists('client_secrets.json'):
                print("❌ Errore: File 'client_secrets.json' mancante nella cartella!")
                return None
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            credenziali = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(credenziali.to_json())

    try:
        youtube = build('youtube', 'v3', credentials=credenziali)
        
        body = {
            'snippet': {
                'title': titolo,
                'description': descrizione,
                'tags': tag or ["Street Fighter 6", "SF6", "Replay"],
                'categoryId': '20'  # Gaming
            },
            'status': {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': False
            }
        }

        media = MediaFileUpload(
            str(percorso_video),
            chunksize=-1,
            resumable=True,
            mimetype='video/mp4'
        )

        print(f"🚀 Inizio upload su YouTube del video: {percorso_video}...")
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        risposta = request.execute()
        video_id = risposta.get("id")
        link_video = f"https://youtu.be/{video_id}"
        print(f"✅ Upload completato con successo! ID Video: {video_id}")
        return link_video

    except Exception as e:
        print(f"❌ Errore durante l'upload su YouTube: {e}")
        return None
