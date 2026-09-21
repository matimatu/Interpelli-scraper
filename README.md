# Interpelli-scraper
un progetto pensato per aiutare i poveri docenti della Liguria non ancora di ruolo, in attesa che esca un interpello di loro interesse.
## Setup
ATTENZIONE: per adesso il progetto è pensato per funzionare in OS Windows
- Scaricare il progetto in .zip
- Estrarre il file compresso in una cartella a piacere
- da cmd eseguire il file `scripts\setup.ps1` con questo comando:
    ```powershell
    powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
    ```
- Creare il bot su Telegram (BotFather)
    - Apri Telegram e cerca @BotFather (ha la spunta blu).
    - Avvia la chat e manda il comando:
    `/newbot`
    - BotFather ti chiederà un nome del bot e uno username che deve finire con "bot"
    - Se tutto va bene, BotFather ti risponde con un link al tuo bot
    e un __token__ tipo: `123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`
    - Salva quel token nel file BOT.properties (_guarda come inserirlo tramite il file BOT.properties.example_)
    - Recupera il tuo `chat_id` personale interrogando _@RawDataBot_ o _@userinfobot_ e salvalo sempre nello stesso file
- Crea e configura il file `config.json` mettendo le preferenze di classi di concorso e su che province cercare. Segui la struttura di `config.json.example`
- Fai partire il programma con questo comando da cmd:
    ```powershell
    powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1
    ```
    - Se funziona e trova nuovi interpelli ti arriverà un messaggio dal tuo bot, altrimenti non manderà alcun messaggio
- Per automatizzare l'esecuzione utilizza il programma `Pianificazione attività` di Windows
    - Crea attività
    - Imposta uno o più trigger giornalieri
    - Come programma inserisci _powershell.exe_
    - Come argomenti inserisci:
    ```powershell
    -NoProfile -ExecutionPolicy Bypass -File "C:\percorso\interpelli-scraper\scripts\run.ps1"
    ```



