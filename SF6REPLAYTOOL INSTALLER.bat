@echo off
:: Forza la codifica UTF-8 per visualizzare correttamente i caratteri speciali accentati
chcp 65001 >nul
title SF6 Replay Tool - Installer Automatico Dipendenze

:: -------------------------------------------------------------------------
:: CONTROLLO PRIVILEGI DI AMMINISTRATORE
:: -------------------------------------------------------------------------
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [❌ ERRORE] Questo script deve essere eseguito come Amministratore!
    echo.
    echo Per fare click destro sul file e seleziona "Esegui come amministratore".
    echo.
    pause
    exit /b
)

echo =========================================================================
echo       SF6 Replay Tool - INSTALLATORE AUTOMATICO DEI MODULI PYTHON
echo =========================================================================
echo.

:: -------------------------------------------------------------------------
:: VERIFICA SE PYTHON È INSTALLATO
:: -------------------------------------------------------------------------
echo 🔎 Verifica della presenza di Python nel sistema in corso...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [❌ ERRORE] Python non è stato rilevato nel sistema.
    echo Assicurati di scaricare Python dal sito ufficiale o dal Microsoft Store
    echo e di spuntare la casella "Add python.exe to PATH" durante il setup.
    echo.
    pause
    exit /b
)
echo ✅ Python rilevato correttamente.
echo.

:: -------------------------------------------------------------------------
:: AGGIORNAMENTO PIP
:: -------------------------------------------------------------------------
echo 🔄 Aggiornamento di pip (il gestore dei pacchetti di Python) in corso...
python -m pip install --upgrade pip
if %errorLevel% neq 0 (
    echo [⚠️ AVVISO] Impossibile aggiornare pip. Il processo tenterà comunque di proseguire.
)
echo.

:: -------------------------------------------------------------------------
:: INSTALLAZIONE MODULI BASE ED INTERFACCIA OBS
:: -------------------------------------------------------------------------
echo 📦 Installazione dei moduli core, OS e OBS Studio...
for %%i in (pytelegrambotapi psutil obsws-python pygetwindow pywinauto) do (
    echo    - Installazione del modulo: %%i...
    python -m pip install %%i --quiet
    if %errorLevel% neq 0 (
        echo [❌ ERRORE] Fallita l'installazione del modulo %%i. Controlla la rete.
        pause
        exit /b
    )
)
echo ✅ Moduli di sistema e OBS installati con successo!
echo.

:: -------------------------------------------------------------------------
:: INSTALLAZIONE MODULI GOOGLE PER YOUTUBE AUTOMATION
:: -------------------------------------------------------------------------
echo 📺 Installazione dei moduli Google e delle API v3 per l'upload su YouTube...
for %%i in (google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client) do (
    echo    - Installazione del modulo API: %%i...
    python -m pip install %%i --quiet
    if %errorLevel% neq 0 (
        echo [❌ ERRORE] Fallita l'installazione del pacchetto Google %%i.
        pause
        exit /b
    )
)
echo ✅ Moduli di autenticazione e upload YouTube installati con successo!
echo.

:: -------------------------------------------------------------------------
:: FINE PROCESSO ED AVVIO SCRIPT
:: -------------------------------------------------------------------------
echo =========================================================================
echo 🎉 CONFIGURAZIONE COMPLETATA! Tutti i moduli Python sono pronti all'uso.
echo =========================================================================
echo.
set /p scelta="Vuoi avviare subito lo script del Bot Telegram? (S/N): "
if /i "%scelta%"=="S" (
    echo.
    echo 🚀 Avvio di SF6ReplayScript.py in corso...
    if exist "SF6ReplayScript.py" (
        python SF6ReplayScript.py
    ) else (
        echo [❌ ERRORE] File "SF6ReplayScript.py" non trovato nella cartella corrente!
        echo Assicurati che lo script Python si trovi insieme a questo file .bat.
        pause
    )
)

exit /b
