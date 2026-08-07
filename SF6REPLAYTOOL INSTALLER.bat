@echo off
:: Controlla i privilegi di amministratore
title SF6Replay Tool - Installer Automatico
clc
echo ============================================================
echo   INSTALLATORE AUTOMATICO PER SF6REPLAY TOOL
echo ============================================================
echo.

:: Verifica se i privilegi sono di amministratore
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Privilegi di amministratore rilevati.
) else (
    echo [ERRORE] Fai click destro su questo file e seleziona "Esegui come amministratore".
    echo.
    pause
    exit /b
)

echo.
echo ------------------------------------------------------------
echo 1. VERIFICA DI PYTHON NEL SISTEMA
echo ------------------------------------------------------------
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Python e' gia' installato nel sistema.
) else (
    echo [ATTENZIONE] Python non e' stato trovato nel PATH o non e' installato.
    echo Sto aprendo il sito ufficiale. Scarica l'installer di Windows ed esegui.
    echo IMPORTANTE: Spunta la casella "Add python.exe to PATH" durante l'installazione!
    echo.
    timeout /t 5
    start https://python.org
    echo Premi un tasto dopo aver completato l'installazione di Python per continuare...
    pause >nul
)

echo.
echo ------------------------------------------------------------
echo 2. AGGIORNAMENTO DI PIP E INSTALLAZIONE LIBRERIE PYTHON
echo ------------------------------------------------------------
echo Sto aggiornando il gestore pacchetti (pip)...
python -m pip install --upgrade pip

echo.
echo Sto installando le librerie richieste (pyTelegramBotAPI, psutil, obsws-python, pygetwindow, pywinauto)...
:: Installa i pacchetti esatti per far girare lo script senza conflitti
pip install pytelegrambotapi psutil obsws-python pygetwindow pywinauto

if %errorLevel% == 0 (
    echo.
    echo [OK] Tutte le librerie Python sono state installate con successo!
) else (
    echo.
    echo [ERRORE] Si e' verificato un problema durante l'installazione delle librerie.
    pause
    exit /b
)

echo.
echo ------------------------------------------------------------
echo 3. AVVIO DELLA CONFIGURAZIONE DELLO SCRIPT
echo ------------------------------------------------------------
echo Assicurati che il file dello script Python (SF6ReplayScript.py) sia nella stessa cartella.
if exist "SF6ReplayScript.py" (
    echo [OK] File TEST.py trovato. Avvio la configurazione iniziale...
    echo.
    timeout /t 3
    python SF6ReplayScript.py
) else (
    echo [ATTENZIONE] Il file 'SF6ReplayScript.py' non e' stato trovato in questa cartella.
    echo Posiziona questo file .bat di fianco a TEST.py e rilancialo per completare la prima configurazione.
    echo.
)

pause
