import tkinter as tk
import psutil
import ctypes
import sys
import os
import winreg
import json
import subprocess
import threading
import time
import webbrowser
import urllib.request
import urllib.parse
import traceback
import faulthandler

APP_NAME = 'PulseBar'
VERSION  = '2.5'

# ── Crash logging (enabled when NETCPURAM_DEBUG=1) ─────────────────────
def _debug_log_path():
    base = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    return os.path.join(base, 'widget_debug.log')

if os.environ.get('NETCPURAM_DEBUG') == '1':
    try:
        _logf = open(_debug_log_path(), 'a', buffering=1, encoding='utf-8')
        faulthandler.enable(_logf)
        def _log(msg):
            _logf.write(msg + '\n'); _logf.flush()
        def _excepthook(exc, val, tb):
            _logf.write('UNCAUGHT:\n'); traceback.print_exception(exc, val, tb, file=_logf); _logf.flush()
        sys.excepthook = _excepthook
        try:
            threading.excepthook = lambda a: (_logf.write('THREAD EXC:\n'),
                                              traceback.print_exception(a.exc_type, a.exc_value, a.exc_traceback, file=_logf),
                                              _logf.flush())
        except Exception:
            pass
        _log('=== widget started ===')
    except Exception:
        def _log(msg): pass
else:
    def _log(msg): pass

# ── Translations ───────────────────────────────────────────────────────
LANGS = ['en', 'el', 'es', 'de', 'fr', 'it', 'pt', 'ru']   # order shown in menu
LANG_NAMES = {'en': 'English', 'el': 'Ελληνικά', 'es': 'Español',
              'de': 'Deutsch', 'fr': 'Français', 'it': 'Italiano',
              'pt': 'Português', 'ru': 'Русский'}

T = {
 'en': {'metrics':'Metrics','position':'Position','size':'Size','opacity':'Opacity',
        'refresh':'Refresh rate','netunit':'Network unit','reposition':'Reset position',
        'fullscreen':'Hide in fullscreen','startup':'Start with Windows','language':'Language',
        'close':'Close','left':'Left','center':'Center','right':'Right',
        'small':'Small','normal':'Normal','large':'Large',
        'net_bytes':'MB/s (bytes)','net_bits':'Mbps (bits)',
        'cpu':'CPU','ram':'RAM','net':'Network',
        'toast_on':'Will start with Windows ✓','toast_off':'Removed from startup.'},
 'el': {'metrics':'Ενδείξεις','position':'Θέση','size':'Μέγεθος','opacity':'Διαφάνεια',
        'refresh':'Ανανέωση','netunit':'Μονάδα δικτύου','reposition':'Επανατοποθέτηση',
        'fullscreen':'Κρύψιμο σε fullscreen','startup':'Εκκίνηση με Windows','language':'Γλώσσα',
        'close':'Κλείσιμο','left':'Αριστερά','center':'Κέντρο','right':'Δεξιά',
        'small':'Μικρό','normal':'Κανονικό','large':'Μεγάλο',
        'net_bytes':'MB/s (bytes)','net_bits':'Mbps (bits)',
        'cpu':'CPU','ram':'RAM','net':'Δίκτυο',
        'toast_on':'Θα ξεκινάει με τα Windows ✓','toast_off':'Αφαιρέθηκε από την εκκίνηση.'},
 'es': {'metrics':'Indicadores','position':'Posición','size':'Tamaño','opacity':'Opacidad',
        'refresh':'Frecuencia','netunit':'Unidad de red','reposition':'Restablecer posición',
        'fullscreen':'Ocultar en pantalla completa','startup':'Iniciar con Windows','language':'Idioma',
        'close':'Cerrar','left':'Izquierda','center':'Centro','right':'Derecha',
        'small':'Pequeño','normal':'Normal','large':'Grande',
        'net_bytes':'MB/s (bytes)','net_bits':'Mbps (bits)',
        'cpu':'CPU','ram':'RAM','net':'Red',
        'toast_on':'Se iniciará con Windows ✓','toast_off':'Eliminado del inicio.'},
 'de': {'metrics':'Anzeigen','position':'Position','size':'Größe','opacity':'Transparenz',
        'refresh':'Aktualisierung','netunit':'Netzwerkeinheit','reposition':'Position zurücksetzen',
        'fullscreen':'Im Vollbild ausblenden','startup':'Mit Windows starten','language':'Sprache',
        'close':'Schließen','left':'Links','center':'Mitte','right':'Rechts',
        'small':'Klein','normal':'Normal','large':'Groß',
        'net_bytes':'MB/s (bytes)','net_bits':'Mbps (bits)',
        'cpu':'CPU','ram':'RAM','net':'Netzwerk',
        'toast_on':'Startet mit Windows ✓','toast_off':'Aus dem Autostart entfernt.'},
 'fr': {'metrics':'Indicateurs','position':'Position','size':'Taille','opacity':'Opacité',
        'refresh':'Rafraîchissement','netunit':'Unité réseau','reposition':'Réinitialiser la position',
        'fullscreen':'Masquer en plein écran','startup':'Démarrer avec Windows','language':'Langue',
        'close':'Fermer','left':'Gauche','center':'Centre','right':'Droite',
        'small':'Petit','normal':'Normal','large':'Grand',
        'net_bytes':'MB/s (bytes)','net_bits':'Mbps (bits)',
        'cpu':'CPU','ram':'RAM','net':'Réseau',
        'toast_on':'Démarre avec Windows ✓','toast_off':'Retiré du démarrage.'},
 'it': {'metrics':'Indicatori','position':'Posizione','size':'Dimensione','opacity':'Opacità',
        'refresh':'Aggiornamento','netunit':'Unità di rete','reposition':'Reimposta posizione',
        'fullscreen':'Nascondi a schermo intero','startup':'Avvia con Windows','language':'Lingua',
        'close':'Chiudi','left':'Sinistra','center':'Centro','right':'Destra',
        'small':'Piccolo','normal':'Normale','large':'Grande',
        'net_bytes':'MB/s (bytes)','net_bits':'Mbps (bits)',
        'cpu':'CPU','ram':'RAM','net':'Rete',
        'toast_on':'Si avvierà con Windows ✓','toast_off':'Rimosso dall\'avvio.'},
 'pt': {'metrics':'Indicadores','position':'Posição','size':'Tamanho','opacity':'Opacidade',
        'refresh':'Atualização','netunit':'Unidade de rede','reposition':'Repor posição',
        'fullscreen':'Ocultar em tela cheia','startup':'Iniciar com o Windows','language':'Idioma',
        'close':'Fechar','left':'Esquerda','center':'Centro','right':'Direita',
        'small':'Pequeno','normal':'Normal','large':'Grande',
        'net_bytes':'MB/s (bytes)','net_bits':'Mbps (bits)',
        'cpu':'CPU','ram':'RAM','net':'Rede',
        'toast_on':'Inicia com o Windows ✓','toast_off':'Removido da inicialização.'},
 'ru': {'metrics':'Показатели','position':'Позиция','size':'Размер','opacity':'Прозрачность',
        'refresh':'Обновление','netunit':'Единица сети','reposition':'Сбросить позицию',
        'fullscreen':'Скрывать в полноэкранном','startup':'Запуск с Windows','language':'Язык',
        'close':'Закрыть','left':'Слева','center':'По центру','right':'Справа',
        'small':'Маленький','normal':'Обычный','large':'Большой',
        'net_bytes':'МБ/с (байты)','net_bits':'Мбит/с (биты)',
        'cpu':'ЦП','ram':'ОЗУ','net':'Сеть',
        'toast_on':'Будет запускаться с Windows ✓','toast_off':'Удалено из автозапуска.'},
}

# Extra strings added later (disk/battery/theme/sparklines) merged into T below
EXTRA = {
 'en': {'disk':'Disk','batt':'Battery','theme':'Theme','sparklines':'Mini graphs','details':'Details','cpu_freq':'CPU speed (GHz)','ram_gb':'RAM in GB','gpu':'GPU','cpu_name':'CPU name','layout':'Layout','horizontal':'Horizontal','vertical':'Vertical','stacked':'Two rows (stacked)','weather':'Weather','setcity':'Set city…'},
 'el': {'disk':'Δίσκος','batt':'Μπαταρία','theme':'Θέμα','sparklines':'Mini γραφήματα','details':'Λεπτομέρειες','cpu_freq':'Ταχύτητα CPU (GHz)','ram_gb':'RAM σε GB','gpu':'GPU','cpu_name':'Όνομα CPU','layout':'Διάταξη','horizontal':'Οριζόντια','vertical':'Κάθετη','stacked':'Δύο σειρές','weather':'Καιρός','setcity':'Ορισμός πόλης…'},
 'es': {'disk':'Disco','batt':'Batería','theme':'Tema','sparklines':'Mini gráficos','details':'Detalles','cpu_freq':'Velocidad CPU (GHz)','ram_gb':'RAM en GB','gpu':'GPU','cpu_name':'Nombre CPU','layout':'Disposición','horizontal':'Horizontal','vertical':'Vertical','stacked':'Two rows (stacked)','weather':'Tiempo','setcity':'Ciudad…'},
 'de': {'disk':'Festplatte','batt':'Akku','theme':'Design','sparklines':'Mini-Diagramme','details':'Details','cpu_freq':'CPU-Takt (GHz)','ram_gb':'RAM in GB','gpu':'GPU','cpu_name':'CPU-Name','layout':'Layout','horizontal':'Horizontal','vertical':'Vertikal','stacked':'Zwei Zeilen','weather':'Wetter','setcity':'Stadt…'},
 'fr': {'disk':'Disque','batt':'Batterie','theme':'Thème','sparklines':'Mini-graphiques','details':'Détails','cpu_freq':'Vitesse CPU (GHz)','ram_gb':'RAM en Go','gpu':'GPU','cpu_name':'Nom du CPU','layout':'Disposition','horizontal':'Horizontale','vertical':'Verticale','stacked':'Deux lignes','weather':'Météo','setcity':'Ville…'},
 'it': {'disk':'Disco','batt':'Batteria','theme':'Tema','sparklines':'Mini grafici','details':'Dettagli','cpu_freq':'Velocità CPU (GHz)','ram_gb':'RAM in GB','gpu':'GPU','cpu_name':'Nome CPU','layout':'Disposizione','horizontal':'Orizzontale','vertical':'Verticale','stacked':'Due righe','weather':'Meteo','setcity':'Città…'},
 'pt': {'disk':'Disco','batt':'Bateria','theme':'Tema','sparklines':'Mini gráficos','details':'Detalhes','cpu_freq':'Velocidade CPU (GHz)','ram_gb':'RAM em GB','gpu':'GPU','cpu_name':'Nome CPU','layout':'Disposição','horizontal':'Horizontal','vertical':'Vertical','stacked':'Two rows (stacked)','weather':'Tempo','setcity':'Cidade…'},
 'ru': {'disk':'Диск','batt':'Батарея','theme':'Тема','sparklines':'Мини-графики','details':'Детали','cpu_freq':'Частота ЦП (ГГц)','ram_gb':'ОЗУ в ГБ','gpu':'GPU','cpu_name':'Имя ЦП','layout':'Раскладка','horizontal':'Горизонтально','vertical':'Вертикально','stacked':'Две строки','weather':'Погода','setcity':'Город…'},
}
for _lng, _d in EXTRA.items():
    T.setdefault(_lng, {}).update(_d)

# ── Donations (set these to your own links) ────────────────────────────
DONATE_PAYPAL  = 'https://www.paypal.com/donate/?hosted_button_id=PHZG592VLQAFA'
DONATE_REVOLUT = 'https://revolut.me/fokionpap'

DONATE_LABEL = {
 'en':'Donate','el':'Δωρεά','es':'Donar','de':'Spenden',
 'fr':'Faire un don','it':'Dona','pt':'Doar','ru':'Поддержать',
}
DONATE_MSG = {
 'en':'This widget is free.\nIf you enjoy it, consider a small donation 💜',
 'el':'Αυτό το widget είναι δωρεάν.\nΑν σου αρέσει, σκέψου μια μικρή δωρεά 💜',
 'es':'Este widget es gratis.\nSi te gusta, considera una pequeña donación 💜',
 'de':'Dieses Widget ist kostenlos.\nWenn es dir gefällt, freue ich mich über eine Spende 💜',
 'fr':'Ce widget est gratuit.\nSi vous l’aimez, pensez à un petit don 💜',
 'it':'Questo widget è gratuito.\nSe ti piace, considera una piccola donazione 💜',
 'pt':'Este widget é gratuito.\nSe gostares, considera uma pequena doação 💜',
 'ru':'Этот виджет бесплатный.\nЕсли он вам нравится, поддержите автора 💜',
}
TRANSP_LABEL = {
 'en':'Transparent background','el':'Διάφανο φόντο','es':'Fondo transparente',
 'de':'Transparenter Hintergrund','fr':'Fond transparent','it':'Sfondo trasparente',
 'pt':'Fundo transparente','ru':'Прозрачный фон',
}
BG_LABEL = {
 'en':'Background','el':'Φόντο','es':'Fondo','de':'Hintergrund',
 'fr':'Arrière-plan','it':'Sfondo','pt':'Fundo','ru':'Фон',
}
LOCK_LABEL = {
 'en':'Lock position','el':'Κλείδωμα θέσης','es':'Bloquear posición',
 'de':'Position sperren','fr':'Verrouiller la position','it':'Blocca posizione',
 'pt':'Bloquear posição','ru':'Заблокировать позицию',
}
ONTASKBAR_LABEL = {
 'en':'On the taskbar','el':'Πάνω στη μπάρα','es':'En la barra de tareas',
 'de':'Auf der Taskleiste','fr':'Sur la barre des tâches','it':'Sulla barra',
 'pt':'Na barra de tarefas','ru':'На панели задач',
}
DISKS_LABEL = {
 'en':'Disks (space)','el':'Δίσκοι (χώρος)','es':'Discos (espacio)',
 'de':'Laufwerke (Platz)','fr':'Disques (espace)','it':'Dischi (spazio)',
 'pt':'Discos (espaço)','ru':'Диски (место)',
}
TOOLTIPS_LABEL = {
 'en':'Hover details','el':'Λεπτομέρειες (hover)','es':'Detalles al pasar',
 'de':'Hover-Details','fr':'Détails au survol','it':'Dettagli al passaggio',
 'pt':'Detalhes ao passar','ru':'Подсказки при наведении',
}
# tooltip body strings, per language
TIP = {
 'en':{'top':'Top processes','used':'Used','free':'Free','total':'Total','session':'Session',
       'cores':'Cores','source':'Windows counters','charging':'Charging','onbatt':'On battery',
       'timeleft':'Time left','now':'Now','perdisk':'Per-disk · read / write','status':'Status',
       'sampling':'sampling…','loading':'loading…','vramused':'VRAM used',
       'feels':'Feels like','humidity':'Humidity','wind':'Wind','forecast':'Forecast'},
 'el':{'top':'Κορυφαίες διεργασίες','used':'Σε χρήση','free':'Ελεύθερα','total':'Σύνολο','session':'Συνεδρία',
       'cores':'Πυρήνες','source':'Μετρητές Windows','charging':'Φόρτιση','onbatt':'Στη μπαταρία',
       'timeleft':'Απομένει','now':'Τώρα','perdisk':'Ανά δίσκο · ανάγν./εγγρ.','status':'Κατάσταση',
       'sampling':'δειγματοληψία…','loading':'φόρτωση…','vramused':'VRAM σε χρήση',
       'feels':'Αίσθηση','humidity':'Υγρασία','wind':'Άνεμος','forecast':'Πρόγνωση'},
 'es':{'top':'Procesos principales','used':'Usado','free':'Libre','total':'Total','session':'Sesión',
       'cores':'Núcleos','source':'Contadores de Windows','charging':'Cargando','onbatt':'Con batería',
       'timeleft':'Restante','now':'Ahora','perdisk':'Por disco · lect./escr.','status':'Estado',
       'sampling':'muestreando…','loading':'cargando…','vramused':'VRAM usada',
       'feels':'Sensación','humidity':'Humedad','wind':'Viento','forecast':'Pronóstico'},
 'de':{'top':'Top-Prozesse','used':'Belegt','free':'Frei','total':'Gesamt','session':'Sitzung',
       'cores':'Kerne','source':'Windows-Zähler','charging':'Lädt','onbatt':'Akkubetrieb',
       'timeleft':'Restzeit','now':'Jetzt','perdisk':'Pro Datenträger · L/S','status':'Status',
       'sampling':'Abtastung…','loading':'lädt…','vramused':'VRAM belegt',
       'feels':'Gefühlt','humidity':'Luftfeuchte','wind':'Wind','forecast':'Vorhersage'},
 'fr':{'top':'Processus principaux','used':'Utilisé','free':'Libre','total':'Total','session':'Session',
       'cores':'Cœurs','source':'Compteurs Windows','charging':'En charge','onbatt':'Sur batterie',
       'timeleft':'Restant','now':'Maintenant','perdisk':'Par disque · lect./écr.','status':'État',
       'sampling':'échantillonnage…','loading':'chargement…','vramused':'VRAM utilisée',
       'feels':'Ressenti','humidity':'Humidité','wind':'Vent','forecast':'Prévisions'},
 'it':{'top':'Processi principali','used':'Usato','free':'Libero','total':'Totale','session':'Sessione',
       'cores':'Core','source':'Contatori Windows','charging':'In carica','onbatt':'A batteria',
       'timeleft':'Rimanente','now':'Ora','perdisk':'Per disco · lett./scritt.','status':'Stato',
       'sampling':'campionamento…','loading':'caricamento…','vramused':'VRAM usata',
       'feels':'Percepita','humidity':'Umidità','wind':'Vento','forecast':'Previsioni'},
 'pt':{'top':'Processos principais','used':'Usado','free':'Livre','total':'Total','session':'Sessão',
       'cores':'Núcleos','source':'Contadores do Windows','charging':'Carregando','onbatt':'Na bateria',
       'timeleft':'Restante','now':'Agora','perdisk':'Por disco · leit./escr.','status':'Estado',
       'sampling':'amostragem…','loading':'carregando…','vramused':'VRAM usada',
       'feels':'Sensação','humidity':'Humidade','wind':'Vento','forecast':'Previsão'},
 'ru':{'top':'Топ процессы','used':'Занято','free':'Свободно','total':'Всего','session':'Сессия',
       'cores':'Ядра','source':'Счётчики Windows','charging':'Зарядка','onbatt':'От батареи',
       'timeleft':'Осталось','now':'Сейчас','perdisk':'По дискам · чт./зап.','status':'Состояние',
       'sampling':'выборка…','loading':'загрузка…','vramused':'VRAM занято',
       'feels':'Ощущается','humidity':'Влажность','wind':'Ветер','forecast':'Прогноз'},
}
# localized short weekday names (Mon=0 … Sun=6)
WDAYS = {
 'en':['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
 'el':['Δευ','Τρι','Τετ','Πεμ','Παρ','Σαβ','Κυρ'],
 'es':['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'],
 'de':['Mo','Di','Mi','Do','Fr','Sa','So'],
 'fr':['Lun','Mar','Mer','Jeu','Ven','Sam','Dim'],
 'it':['Lun','Mar','Mer','Gio','Ven','Sab','Dom'],
 'pt':['Seg','Ter','Qua','Qui','Sex','Sáb','Dom'],
 'ru':['Пн','Вт','Ср','Чт','Пт','Сб','Вс'],
}
UPDATE_LABEL = {
 'en':'Update available','el':'Διαθέσιμη ενημέρωση','es':'Actualización disponible',
 'de':'Update verfügbar','fr':'Mise à jour disponible','it':'Aggiornamento disponibile',
 'pt':'Atualização disponível','ru':'Доступно обновление',
}
CHECKUPD_LABEL = {
 'en':'Check for updates','el':'Έλεγχος ενημερώσεων','es':'Buscar actualizaciones',
 'de':'Nach Updates suchen','fr':'Rechercher des mises à jour','it':'Cerca aggiornamenti',
 'pt':'Procurar atualizações','ru':'Проверять обновления',
}
RELEASES_URL = 'https://github.com/FokionPapanikolaou/PulseBar/releases/latest'
RELEASES_API = 'https://api.github.com/repos/FokionPapanikolaou/PulseBar/releases/latest'

def _ver_tuple(s):
    out = []
    for p in str(s).replace('-', '.').split('.'):
        n = ''.join(ch for ch in p if ch.isdigit())
        out.append(int(n) if n else 0)
    return tuple(out)
BG_TRANSP = {
 'en':'Transparent','el':'Διάφανο','es':'Transparente','de':'Transparent',
 'fr':'Transparent','it':'Trasparente','pt':'Transparente','ru':'Прозрачный',
}

DONATE_THANKS = {
 'en':'Thank you for your support! 🙏','el':'Ευχαριστώ για τη στήριξη! 🙏',
 'es':'¡Gracias por tu apoyo! 🙏','de':'Danke für deine Unterstützung! 🙏',
 'fr':'Merci de votre soutien ! 🙏','it':'Grazie per il supporto! 🙏',
 'pt':'Obrigado pelo apoio! 🙏','ru':'Спасибо за поддержку! 🙏',
}

HINTS = {
 'en':'Settings are in the tray icon (bottom-right). Right-click it.',
 'el':'Οι ρυθμίσεις είναι στο εικονίδιο της μπάρας (κάτω δεξιά). Κάνε δεξί κλικ.',
 'es':'Los ajustes están en el icono de la bandeja (abajo dcha.). Clic derecho.',
 'de':'Einstellungen im Tray-Symbol (unten rechts). Rechtsklick darauf.',
 'fr':'Les réglages sont dans l’icône de la barre (en bas à droite). Clic droit.',
 'it':'Le impostazioni sono nell’icona del tray (in basso a destra). Clic destro.',
 'pt':'As definições estão no ícone da bandeja (canto inf. dir.). Clique direito.',
 'ru':'Настройки — в значке в трее (внизу справа). Нажмите правой кнопкой.',
}

def detect_language():
    """Map the Windows UI language to one we support; fall back to English."""
    try:
        lid = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3ff
        return {0x09:'en', 0x08:'el', 0x0a:'es', 0x07:'de', 0x0c:'fr',
                0x10:'it', 0x16:'pt', 0x19:'ru'}.get(lid, 'en')
    except Exception:
        return 'en'

# ── Single-instance guard ──────────────────────────────────────────────
def already_running():
    """Create a named mutex; if it already exists, another copy is running."""
    ERROR_ALREADY_EXISTS = 183
    kernel32 = ctypes.windll.kernel32
    # Global\ prefix so it's unique across the whole session
    kernel32.CreateMutexW(None, False, 'Global\\PulseBar_SingleInstance')
    return kernel32.GetLastError() == ERROR_ALREADY_EXISTS

# ── Windows work area ──────────────────────────────────────────────────
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

def get_taskbar_info():
    rect = RECT()
    ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0)
    screen_h = ctypes.windll.user32.GetSystemMetrics(1)
    screen_w = ctypes.windll.user32.GetSystemMetrics(0)
    taskbar_h = screen_h - rect.bottom
    return rect.bottom, max(taskbar_h, 40), screen_w

def list_drives():
    """Fixed drive letters with a filesystem, e.g. ['C:', 'D:']."""
    out = []
    try:
        for p in psutil.disk_partitions(all=False):
            dev = (p.device or '').rstrip('\\')
            if dev and p.fstype and 'cdrom' not in (p.opts or ''):
                out.append(dev)
    except Exception:
        pass
    return out

def get_total_vram_gb():
    """Total dedicated VRAM of the discrete GPU (GB), read from the display
    adapter registry keys. Returns the largest adapter's memory. None if absent."""
    base = r'SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}'
    best = 0
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base)
        i = 0
        while True:
            try:
                sub = winreg.EnumKey(k, i); i += 1
            except OSError:
                break
            if not sub.isdigit():
                continue
            try:
                sk = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base + '\\' + sub)
                for name in ('HardwareInformation.qwMemorySize',
                             'HardwareInformation.MemorySize'):
                    try:
                        val, _ = winreg.QueryValueEx(sk, name)
                        if isinstance(val, bytes):
                            val = int.from_bytes(val, 'little')
                        best = max(best, int(val))
                        break
                    except (FileNotFoundError, OSError, ValueError):
                        continue
                winreg.CloseKey(sk)
            except OSError:
                pass
        winreg.CloseKey(k)
    except OSError:
        pass
    return (best / 1073741824) if best else None

# ── paths ──────────────────────────────────────────────────────────────
TRANSPARENT = '#010101'
BG = '#0d1117'   # dark widget background (blends with the taskbar)

def _base_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

ICON_DIR = os.path.join(_base_dir(), 'icons')

def _exe_dir():
    """Folder where the .exe (or .py) actually lives — NOT the temp _MEIPASS."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def _resolve_config_dir():
    """Portable-first config location.

    Prefer a 'config.json' next to the executable so settings travel with the
    app (USB stick / portable folder). If that folder isn't writable (e.g. the
    app was installed under Program Files), fall back to %APPDATA%.
    """
    portable = _exe_dir()
    try:
        testfile = os.path.join(portable, '.write_test')
        with open(testfile, 'w') as f:
            f.write('')
        os.remove(testfile)
        # If a portable config already exists, or the folder is writable & not
        # a protected install dir, use it.
        program_files = (os.environ.get('ProgramFiles', ''), os.environ.get('ProgramFiles(x86)', ''))
        if not any(p and portable.lower().startswith(p.lower()) for p in program_files):
            return portable
    except OSError:
        pass
    return os.path.join(os.environ.get('APPDATA', portable), APP_NAME)

CONFIG_DIR  = _resolve_config_dir()
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

DEFAULTS = {
    'opacity':   0.6,     # 0.4 – 1.0  (lower = more see-through)
    'align':     'left',  # left | center | right
    'free_pos':  False,   # True after dragging — remembers a custom position
    'pos_x':     0,
    'pos_y':     0,
    'locked':    False,   # lock position (ignore drags) to avoid accidents
    'font_scale':'normal',# small | normal | large
    'interval':  1000,    # ms
    'show_cpu':  True,
    'show_ram':  True,
    'show_net':  True,
    'show_gpu':  True,    # GPU utilization %
    'show_weather': True, # weather (Open-Meteo)
    'show_disk': False,   # disk read/write speed
    'show_batt': False,   # battery % (laptops)
    'cpu_freq':  False,   # (inline mode only) CPU clock speed next to CPU %
    'ram_gb':    False,   # (inline mode only) RAM used in GB next to RAM %
    'weather_unit': 'C',  # C | F
    'weather_city': '',   # '' = auto-locate via IP
    'orientation': 'horizontal',  # horizontal | vertical
    'stacked':   True,    # label on top, value below (like the net rows)
    'transparent_bg': True,   # fully transparent background (chroma-key) + click-through
    'follow_taskbar': True,  # always hide when taskbar hides (fullscreen apps)
    'on_taskbar': True,      # sit ON the taskbar band (vs floating just above it)
    'net_unit':  'bits',     # bits (Mbps) | bytes (MB/s)
    'language':  None,       # None = auto-detect from Windows
    'theme':     'default',  # see THEMES
    'sparklines':False,      # mini history graphs
    'disks':     [],         # drive letters to show space % for, e.g. ['C:']
    'tooltips':  True,       # hover a metric -> details popup
    'check_updates': True,   # check GitHub for a newer release on launch
    'last_update_check': 0,  # epoch seconds of the last check (throttle)
}

# Color themes — 'accent' tints icons-divider, 'val' is the calm value color
THEMES = {
    'default': {'val':'#ffffff', 'accent':'#2d333b', 'spark':'#3fb950'},
    'ocean':   {'val':'#cde9ff', 'accent':'#1f6feb', 'spark':'#58a6ff'},
    'matrix':  {'val':'#b9ffb9', 'accent':'#1a4d1a', 'spark':'#3fb950'},
    'amber':   {'val':'#ffe6b3', 'accent':'#5a3d00', 'spark':'#ffa657'},
    'mono':    {'val':'#e6e6e6', 'accent':'#444444', 'spark':'#aaaaaa'},
    # ── gaming ──
    'neon':    {'val':'#39ff14', 'accent':'#0f5c0a', 'spark':'#39ff14'},   # neon green
    'cyber':   {'val':'#00fff7', 'accent':'#ff007c', 'spark':'#ff007c'},   # cyberpunk cyan/magenta
    'inferno': {'val':'#ff6a00', 'accent':'#7a1500', 'spark':'#ff2d00'},   # fire
    'plasma':  {'val':'#c46bff', 'accent':'#5b1a8a', 'spark':'#e000ff'},   # purple plasma
    'rgb':     {'val':'#ff0000', 'accent':'#ff0000', 'spark':'#ff0000'},   # animated (handled live)
}
GAMING_THEMES = ('neon', 'cyber', 'inferno', 'plasma', 'rgb')

def hsv_to_hex(h, s=1.0, v=1.0):
    """h in [0,1) -> #rrggbb"""
    i = int(h * 6) % 6
    f = h * 6 - int(h * 6)
    p = v * (1 - s); q = v * (1 - f * s); t = v * (1 - (1 - f) * s)
    r, g, b = [(v, t, p), (q, v, p), (p, v, t),
               (p, q, v), (t, p, v), (v, p, q)][i]
    return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

def load_config():
    cfg = dict(DEFAULTS)
    try:
        # utf-8-sig tolerates a BOM if the file was saved with one
        with open(CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            cfg.update(json.load(f))
    except (FileNotFoundError, ValueError):
        pass
    return cfg

def save_config(cfg):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
    except OSError:
        pass

# ── Startup (registry Run key) ─────────────────────────────────────────
REG_KEY  = r'Software\Microsoft\Windows\CurrentVersion\Run'
REG_NAME = 'PulseBar'

def _startup_cmd():
    """The Run-key command that should launch THIS exe/script from its current
    location. Recomputed every launch so a moved portable .exe stays correct."""
    if getattr(sys, 'frozen', False):
        return f'"{sys.executable}"'
    script = os.path.abspath(__file__)
    pythonw = sys.executable.replace('python.exe', 'pythonw.exe')
    return f'"{pythonw}" "{script}"'

def is_startup_enabled():
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_READ)
        winreg.QueryValueEx(k, REG_NAME)
        winreg.CloseKey(k)
        return True
    except FileNotFoundError:
        return False

def set_startup(enable: bool):
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE)
    if enable:
        winreg.SetValueEx(k, REG_NAME, 0, winreg.REG_SZ, _startup_cmd())
    else:
        try:
            winreg.DeleteValue(k, REG_NAME)
        except FileNotFoundError:
            pass
    winreg.CloseKey(k)

def sync_startup():
    """Self-heal the auto-start entry: if it is enabled but points to an old
    path (e.g. the portable .exe was moved or renamed), rewrite it to the
    current location. Idempotent — a no-op when nothing changed or disabled."""
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_READ)
        try:
            current, _ = winreg.QueryValueEx(k, REG_NAME)
        finally:
            winreg.CloseKey(k)
    except FileNotFoundError:
        return   # auto-start is off — nothing to heal
    if current != _startup_cmd():
        try:
            set_startup(True)
        except Exception:
            pass

# ── Weather (Open-Meteo, free, no API key) ─────────────────────────────
def _http_json(url, timeout=6):
    req = urllib.request.Request(url, headers={'User-Agent': 'PulseBar'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8', 'ignore'))

def weather_icon_name(code):
    if code == 0: return 'wx_clear'
    if code in (1, 2): return 'wx_partly'
    if code == 3: return 'wx_cloudy'
    if code in (45, 48): return 'wx_fog'
    if 51 <= code <= 67: return 'wx_rain'
    if 71 <= code <= 77: return 'wx_snow'
    if 80 <= code <= 82: return 'wx_rain'
    if 85 <= code <= 86: return 'wx_snow'
    if code >= 95: return 'wx_storm'
    return 'wx_cloudy'

def fetch_weather(unit='C', city=''):
    """Return a rich weather dict or None. Best-effort.
    Keys: temp, code, city, feels, humidity, wind, wind_unit,
          daily=[{code,tmax,tmin,wd}] (next 3 days)."""
    try:
        if city:
            q = urllib.parse.quote(city)
            g = _http_json(f'https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1')
            res = (g or {}).get('results')
            if not res:
                return None
            lat, lon, name = res[0]['latitude'], res[0]['longitude'], res[0].get('name', city)
        else:
            g = _http_json('https://ipapi.co/json/')
            lat, lon = g['latitude'], g['longitude']
            name = g.get('city', '')
        tu = 'fahrenheit' if unit == 'F' else 'celsius'
        wu = 'mph' if unit == 'F' else 'kmh'
        w = _http_json(
            f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
            f'&current=temperature_2m,apparent_temperature,relative_humidity_2m,'
            f'wind_speed_10m,weather_code'
            f'&daily=weather_code,temperature_2m_max,temperature_2m_min'
            f'&forecast_days=4&timezone=auto&temperature_unit={tu}&wind_speed_unit={wu}')
        cur = w['current']
        out = {'temp': round(cur['temperature_2m']), 'code': int(cur['weather_code']),
               'city': name,
               'feels': round(cur.get('apparent_temperature', cur['temperature_2m'])),
               'humidity': int(cur.get('relative_humidity_2m', 0)),
               'wind': round(cur.get('wind_speed_10m', 0)),
               'wind_unit': ('mph' if unit == 'F' else 'km/h')}
        import datetime
        d = w.get('daily') or {}
        codes = d.get('weather_code') or []
        tmax = d.get('temperature_2m_max') or []
        tmin = d.get('temperature_2m_min') or []
        times = d.get('time') or []
        daily = []
        for i in range(1, min(4, len(codes))):
            try: wd = datetime.date.fromisoformat(times[i]).weekday()
            except Exception: wd = 0
            daily.append({'code': int(codes[i]), 'tmax': round(tmax[i]),
                          'tmin': round(tmin[i]), 'wd': wd})
        out['daily'] = daily
        return out
    except Exception:
        return None

# ── CPU name ───────────────────────────────────────────────────────────
def get_cpu_name():
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r'HARDWARE\DESCRIPTION\System\CentralProcessor\0')
        val, _ = winreg.QueryValueEx(k, 'ProcessorNameString')
        winreg.CloseKey(k)
        # tidy: drop "(R)", "(TM)", "CPU", and the trailing "@ x.xGHz"
        name = val.strip()
        for junk in ('(R)', '(TM)', '(r)', '(tm)'):
            name = name.replace(junk, '')
        name = name.split('@')[0].replace('CPU', '').strip()
        return ' '.join(name.split())
    except Exception:
        return 'CPU'

# ── GPU utilization via PDH (locale-independent, no external tools) ────
import ctypes.wintypes as _wt

class _PDH_FMT_COUNTERVALUE(ctypes.Structure):
    _fields_ = [("CStatus", _wt.DWORD), ("doubleValue", ctypes.c_double)]

class _PDH_FMT_COUNTERVALUE_ITEM_W(ctypes.Structure):
    _fields_ = [("szName", _wt.LPWSTR), ("FmtValue", _PDH_FMT_COUNTERVALUE)]

_PDH_FMT_DOUBLE = 0x00000200
_PDH_MORE_DATA  = 0x800007D2

class GpuCounter:
    """Reads GPU 3D-engine utilization % and dedicated VRAM usage via PDH."""
    PATH_UTIL = r'\GPU Engine(*engtype_3D)\Utilization Percentage'
    PATH_MEM  = r'\GPU Process Memory(*)\Dedicated Usage'

    def __init__(self):
        self.ok = False
        self._cm = None
        try:
            self._pdh = ctypes.windll.pdh
            self._q = _wt.HANDLE()
            if self._pdh.PdhOpenQueryW(None, 0, ctypes.byref(self._q)) != 0:
                return
            self._c = _wt.HANDLE()
            if self._pdh.PdhAddEnglishCounterW(self._q, self.PATH_UTIL, 0, ctypes.byref(self._c)) != 0:
                return
            cm = _wt.HANDLE()   # VRAM counter is optional
            if self._pdh.PdhAddEnglishCounterW(self._q, self.PATH_MEM, 0, ctypes.byref(cm)) == 0:
                self._cm = cm
            self._pdh.PdhCollectQueryData(self._q)   # prime
            self.ok = True
        except Exception:
            self.ok = False

    def _sum(self, counter):
        if not counter:
            return None
        size = _wt.DWORD(0); count = _wt.DWORD(0)
        st = self._pdh.PdhGetFormattedCounterArrayW(
            counter, _PDH_FMT_DOUBLE, ctypes.byref(size), ctypes.byref(count), None) & 0xFFFFFFFF
        if st != _PDH_MORE_DATA or size.value == 0:
            return None
        buf = (ctypes.c_byte * size.value)()
        st = self._pdh.PdhGetFormattedCounterArrayW(
            counter, _PDH_FMT_DOUBLE, ctypes.byref(size), ctypes.byref(count), buf) & 0xFFFFFFFF
        if st != 0:
            return None
        items = ctypes.cast(buf, ctypes.POINTER(_PDH_FMT_COUNTERVALUE_ITEM_W))
        total = 0.0
        for i in range(count.value):
            total += max(0.0, items[i].FmtValue.doubleValue)
        return total

    def read(self):
        """Returns (utilization_percent | None, vram_gb | None)."""
        if not self.ok:
            return (None, None)
        try:
            if (self._pdh.PdhCollectQueryData(self._q) & 0xFFFFFFFF) != 0:
                return (None, None)
            util = self._sum(self._c)
            mem = self._sum(self._cm)
            upct = int(min(100, round(util))) if util is not None else None
            mgb = (mem / 1073741824) if mem else None
            return (upct, mgb)
        except Exception:
            return (None, None)

# ── Live CPU frequency via PDH (psutil reports only the static base clock) ──
class CpuFreq:
    PATH = r'\Processor Information(_Total)\% Processor Performance'

    def __init__(self):
        self.ok = False
        self.base_mhz = self._nominal()
        try:
            self._pdh = ctypes.windll.pdh
            self._q = _wt.HANDLE()
            if self._pdh.PdhOpenQueryW(None, 0, ctypes.byref(self._q)) != 0:
                return
            self._c = _wt.HANDLE()
            if self._pdh.PdhAddEnglishCounterW(self._q, self.PATH, 0, ctypes.byref(self._c)) != 0:
                return
            self._pdh.PdhCollectQueryData(self._q)   # prime
            self.ok = True
        except Exception:
            self.ok = False

    def _nominal(self):
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r'HARDWARE\DESCRIPTION\System\CentralProcessor\0')
            v, _ = winreg.QueryValueEx(k, '~MHz')
            winreg.CloseKey(k)
            return float(v)
        except Exception:
            return None

    def read_ghz(self):
        """Live frequency in GHz (base × performance%), or None."""
        if not self.ok or not self.base_mhz:
            return None
        try:
            if (self._pdh.PdhCollectQueryData(self._q) & 0xFFFFFFFF) != 0:
                return None
            val = _PDH_FMT_COUNTERVALUE(); typ = _wt.DWORD(0)
            st = self._pdh.PdhGetFormattedCounterValue(
                self._c, _PDH_FMT_DOUBLE, ctypes.byref(typ), ctypes.byref(val)) & 0xFFFFFFFF
            if st != 0:
                return None
            return (self.base_mhz * val.doubleValue / 100.0) / 1000.0
        except Exception:
            return None

# ── Widget ─────────────────────────────────────────────────────────────
FONT_SCALES = {'small': (10, 9), 'normal': (12, 10), 'large': (14, 12)}

class Widget:
    COLORS = {'up': '#3fb950', 'dn': '#79c0ff', 'sep': '#2d333b'}

    def __init__(self):
        self._first_run = not os.path.exists(CONFIG_PATH)
        self.cfg = load_config()
        self.lang = self.cfg.get('language') or detect_language()
        if self.lang not in T:
            self.lang = 'en'
        self.root = tk.Tk()
        # Safety net: never let a stray callback error crash the widget
        def _rce(exc, val, tb):
            try:
                _log('CALLBACK EXC:\n' + ''.join(traceback.format_exception(exc, val, tb)))
            except Exception:
                pass
        self.root.report_callback_exception = _rce
        self._micons = self._load_menu_icons()
        self._wx_icons = self._load_wx_icons()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self._apply_bg_mode()

        _, taskbar_h, _ = get_taskbar_info()
        self.H = taskbar_h

        self._prev_net = psutil.net_io_counters()
        try:
            self._prev_disk = psutil.disk_io_counters()
        except Exception:
            self._prev_disk = None
        # tooltip + per-disk + process-sampler state
        self._perdisk_prev = None
        self._perdisk_rates = {}        # {disk: (read_bytes_s, write_bytes_s)}
        self._net_session = {'up': 0, 'dn': 0}
        self._percpu = []
        self._proc_top = {'cpu': [], 'mem': []}
        self._tip = None
        self._tip_hide_job = None
        self._tip_cells = []            # [(frame, kind, extra), ...]
        self._disk_lbls = {}            # {drive: label}
        self._update_tag = None         # set if a newer GitHub release exists
        self._has_batt = psutil.sensors_battery() is not None
        self._gpu = None
        self._gpu_mem = None
        self._vram_total = get_total_vram_gb()   # total dedicated VRAM (GB) or None
        self._gpu_counter = None
        self._gpu_running = False
        self._cpufreq = CpuFreq()
        self._weather = None
        self._weather_running = False
        self._weather_dirty = False
        # rolling history for sparklines
        from collections import deque
        self._hist = {'cpu': deque(maxlen=32), 'ram': deque(maxlen=32)}
        self._pending_rebuild = False
        self._rgb_targets = []
        self._sep_labels = []
        self._rgb_hue = 0.0
        self._rgb_color = '#39ff14'
        self._visible = True
        self._build_ui()
        self._bind_events()
        self._position()
        self._ensure_gpu_thread()
        self._ensure_weather_thread()

        self._update()
        self._animate()
        self._foreground_loop()
        self._setup_tray()
        threading.Thread(target=self._proc_sampler, daemon=True).start()
        threading.Thread(target=self._update_check_worker, daemon=True).start()

        # First launch: a Windows tray notification points to the settings icon.
        if self._first_run:
            save_config(self.cfg)          # mark as "seen" for next launches
            self.root.after(2500, self._first_run_notify)

    def _first_run_notify(self):
        try:
            if getattr(self, '_tray', None):
                self._tray.notify(HINTS.get(self.lang, HINTS['en']),
                                  'PulseBar')
        except Exception:
            pass

    # ── background mode (transparent vs. dark translucent) ─────────────
    def _apply_bg_mode(self):
        if self.cfg.get('transparent_bg'):
            # true transparency via chroma-key; only icons/numbers show.
            # (the keyed-out background is already click-through automatically;
            #  settings live in the tray, so we don't need the widget clickable.)
            self.bg = TRANSPARENT
            self.root.configure(bg=self.bg)
            self.root.attributes('-transparentcolor', self.bg)
            self.root.attributes('-alpha', 1.0)
        else:
            # dark translucent bar — fully clickable everywhere.
            self.bg = BG
            self.root.configure(bg=self.bg)
            try:
                self.root.attributes('-transparentcolor', '')
            except Exception:
                pass
            self.root.attributes('-alpha', self.cfg['opacity'])

    def _toggle_transparent(self):
        self._set('transparent_bg', not self.cfg.get('transparent_bg'))
        self._apply_bg_mode()
        self._pending_rebuild = True

    # ── System-tray icon (settings live here) ──────────────────────────
    def _ui(self, fn):
        """Run fn on the Tk thread (tray callbacks fire on another thread)."""
        try:
            self.root.after(0, fn)
        except Exception:
            pass

    # action helpers (always run on Tk thread)
    def _act_metric(self, key):
        keys = ('show_cpu','show_ram','show_net','show_disk','show_batt','show_gpu','show_weather')
        if self.cfg.get(key) and not any(self.cfg.get(o) for o in keys if o != key):
            return
        self._set(key, not self.cfg.get(key)); self._rebuild()
        if key == 'show_gpu' and self.cfg.get('show_gpu'):
            self._ensure_gpu_thread()
        if key == 'show_weather' and self.cfg.get('show_weather'):
            self._ensure_weather_thread()

    def _act_weather_unit(self, unit):
        self._set('weather_unit', unit)
        self._weather_dirty = True          # trigger a fast refetch

    def _act_set_city(self):
        try:
            from tkinter import simpledialog
            city = simpledialog.askstring('Weather', 'City (empty = auto by IP):',
                                          initialvalue=self.cfg.get('weather_city', ''),
                                          parent=self.root)
            if city is not None:
                self._set('weather_city', city.strip())
                self._weather_dirty = True
                self._ensure_weather_thread()
        except Exception:
            pass

    def _act_set_rebuild(self, key, val):
        self._set(key, val); self._rebuild()

    def _act_toggle(self, key):
        self._set(key, not self.cfg.get(key)); self._rebuild()

    def _act_reposition(self):
        """Snap back to the default spot (handy after a stray drag)."""
        self.cfg['free_pos'] = False
        self.cfg['pos_x'] = 0
        self.cfg['pos_y'] = 0
        self.cfg['align'] = 'left'
        save_config(self.cfg)
        self._position()

    def _act_lock(self):
        self._set('locked', not self.cfg.get('locked'))

    def _act_opacity(self, v):
        self._set('opacity', v)
        if not self.cfg.get('transparent_bg'):
            self.root.attributes('-alpha', v)

    def _act_interval(self, v):
        self._set('interval', v)

    def _act_language(self, code):
        self.lang = code; self._set('language', code)
        if getattr(self, '_tray', None):
            try:
                self._tray.menu = self._tray_menu()
                self._tray.update_menu()
            except Exception:
                pass

    def _act_transparent(self):
        self._toggle_transparent(); self._rebuild()

    def _act_bg(self, transparent, opacity=None):
        self._set('transparent_bg', transparent)
        if opacity is not None:
            self._set('opacity', opacity)
        self._apply_bg_mode()
        self._rebuild()

    def _act_quit(self):
        try:
            if getattr(self, '_tray', None):
                self._tray.stop()
        except Exception:
            pass
        self.root.destroy()

    def _setup_tray(self):
        try:
            import pystray
            from PIL import Image
        except Exception:
            return
        try:
            img = Image.open(os.path.join(_base_dir(), 'icons', 'tray.png'))
        except Exception:
            try:
                img = Image.open(os.path.join(_base_dir(), 'app.ico'))
            except Exception:
                img = Image.new('RGBA', (32, 32), (47, 129, 247, 255))
        self._pystray = pystray
        self._tray = pystray.Icon(APP_NAME, img, 'PulseBar', self._tray_menu())
        threading.Thread(target=self._tray.run, daemon=True).start()

    def _tray_menu(self):
        from pystray import Menu, MenuItem as MI
        ps = self._pystray
        t = self.t; c = self.cfg

        def metric(key, label):
            return MI(label, lambda i, it: self._ui(lambda: self._act_metric(key)),
                      checked=lambda it, k=key: bool(self.cfg.get(k)))

        def radio(key, val, label):
            return MI(label, lambda i, it: self._ui(lambda: self._act_set_rebuild(key, val)),
                      checked=lambda it, k=key, v=val: self.cfg.get(k) == v, radio=True)

        def toggle(key, label):
            return MI(label, lambda i, it: self._ui(lambda: self._act_toggle(key)),
                      checked=lambda it, k=key: bool(self.cfg.get(k)))

        metrics = Menu(
            metric('show_cpu', t('cpu')), metric('show_ram', t('ram')),
            metric('show_gpu', t('gpu')), metric('show_net', t('net')),
            metric('show_disk', t('disk')),
            *([metric('show_batt', t('batt'))] if self._has_batt else []),
            metric('show_weather', t('weather')),
        )
        weather = Menu(
            MI('°C', lambda i, it: self._ui(lambda: self._act_weather_unit('C')),
               checked=lambda it: self.cfg.get('weather_unit','C') == 'C', radio=True),
            MI('°F', lambda i, it: self._ui(lambda: self._act_weather_unit('F')),
               checked=lambda it: self.cfg.get('weather_unit') == 'F', radio=True),
            Menu.SEPARATOR,
            MI(t('setcity'), lambda i, it: self._ui(self._act_set_city)),
        )
        layout = Menu(
            radio('orientation', 'horizontal', t('horizontal')),
            radio('orientation', 'vertical', t('vertical')),
            Menu.SEPARATOR, toggle('stacked', t('stacked')),
        )
        size = Menu(radio('font_scale','small',t('small')), radio('font_scale','normal',t('normal')),
                    radio('font_scale','large',t('large')))
        def bg_op_item(v):
            return MI(f'{int(v*100)}%',
                      lambda i, it: self._ui(lambda: self._act_bg(False, v)),
                      checked=lambda it: (not self.cfg.get('transparent_bg')
                                          and abs(self.cfg.get('opacity', 1) - v) < 0.01),
                      radio=True)
        def iv_item(v, lab):
            return MI(lab, lambda i, it: self._ui(lambda: self._act_interval(v)),
                      checked=lambda it: self.cfg.get('interval') == v, radio=True)
        def th_item(n):
            return MI(n.capitalize(),
                      lambda i, it: self._ui(lambda: self._act_set_rebuild('theme', n)),
                      checked=lambda it: self.cfg.get('theme', 'default') == n, radio=True)
        def lng_item(code):
            return MI(LANG_NAMES[code],
                      lambda i, it: self._ui(lambda: self._act_language(code)),
                      checked=lambda it: self.lang == code, radio=True)

        background = Menu(
            MI(BG_TRANSP.get(self.lang, BG_TRANSP['en']),
               lambda i, it: self._ui(lambda: self._act_bg(True)),
               checked=lambda it: bool(self.cfg.get('transparent_bg')), radio=True),
            Menu.SEPARATOR,
            *[bg_op_item(v) for v in (0.5, 0.7, 0.85, 1.0)],
        )
        refresh = Menu(*[iv_item(v, lab) for v, lab in
                         ((500,'0.5s'),(1000,'1s'),(2000,'2s'),(5000,'5s'))])
        netunit = Menu(radio('net_unit','bytes',t('net_bytes')), radio('net_unit','bits',t('net_bits')))
        theme = Menu(*[th_item(n) for n in THEMES])
        language = Menu(*[lng_item(code) for code in LANGS])

        def disk_toggle(drive):
            def act():
                ds = list(self.cfg.get('disks', []))
                if drive in ds: ds.remove(drive)
                else: ds.append(drive)
                self.cfg['disks'] = ds; save_config(self.cfg)
                self._rebuild()
            return MI(drive, lambda i, it: self._ui(act),
                      checked=lambda it, d=drive: d in self.cfg.get('disks', []))
        disks_menu = Menu(*[disk_toggle(d) for d in list_drives()])

        return Menu(
            MI(lambda it: '⬆  ' + UPDATE_LABEL.get(self.lang, UPDATE_LABEL['en'])
                          + (f'  v{self._update_tag}' if self._update_tag else ''),
               lambda i, it: self._ui(self._open_releases),
               visible=lambda it: bool(getattr(self, '_update_tag', None))),
            MI(t('metrics'), metrics),
            MI(DISKS_LABEL.get(self.lang, DISKS_LABEL['en']), disks_menu),
            MI(t('weather'), weather),
            MI(t('layout'), layout),
            MI(t('size'), size), MI(BG_LABEL.get(self.lang, BG_LABEL['en']), background),
            MI(t('refresh'), refresh), MI(t('netunit'), netunit),
            MI(t('theme'), theme), MI(t('language'), language),
            Menu.SEPARATOR,
            toggle('sparklines', t('sparklines')),
            toggle('tooltips', TOOLTIPS_LABEL.get(self.lang, TOOLTIPS_LABEL['en'])),
            MI(LOCK_LABEL.get(self.lang, LOCK_LABEL['en']),
               lambda i, it: self._ui(self._act_lock),
               checked=lambda it: bool(self.cfg.get('locked'))),
            MI(t('reposition'), lambda i, it: self._ui(self._act_reposition)),
            toggle('check_updates', CHECKUPD_LABEL.get(self.lang, CHECKUPD_LABEL['en'])),
            MI(t('startup'),
               lambda i, it: self._ui(lambda: (set_startup(not is_startup_enabled()))),
               checked=lambda it: is_startup_enabled()),
            Menu.SEPARATOR,
            MI('\U0001F49C  ' + DONATE_LABEL.get(self.lang, DONATE_LABEL['en']),
               lambda i, it: self._ui(self._show_donate)),
            MI(f'{APP_NAME} v{VERSION}', None, enabled=False),
            MI(t('close'), lambda i, it: self._ui(self._act_quit)),
        )

    # ── GPU background polling (PDH) ───────────────────────────────────
    def _ensure_gpu_thread(self):
        if self.cfg.get('show_gpu') and not self._gpu_running:
            self._gpu_running = True
            threading.Thread(target=self._gpu_loop, daemon=True).start()

    def _gpu_loop(self):
        if self._gpu_counter is None:
            self._gpu_counter = GpuCounter()
        while self.cfg.get('show_gpu'):
            try:
                self._gpu, self._gpu_mem = self._gpu_counter.read()
            except Exception:
                self._gpu, self._gpu_mem = None, None
            time.sleep(1)
        self._gpu_running = False

    # ── Weather background polling ─────────────────────────────────────
    def _ensure_weather_thread(self):
        if self.cfg.get('show_weather') and not self._weather_running:
            self._weather_running = True
            threading.Thread(target=self._weather_loop, daemon=True).start()

    def _weather_loop(self):
        while self.cfg.get('show_weather'):
            self._weather = fetch_weather(self.cfg.get('weather_unit', 'C'),
                                          self.cfg.get('weather_city', ''))
            self._weather_dirty = False
            # refresh every ~20 min, but wake early if unit/city changed
            for _ in range(120):
                if not self.cfg.get('show_weather') or self._weather_dirty:
                    break
                time.sleep(10)
        self._weather_running = False

    def _welcome(self):
        """First-run clickable banner — tapping it reliably opens the menu."""
        win = tk.Toplevel(self.root); win.overrideredirect(True)
        win.attributes('-topmost', True); win.configure(bg='#1f6feb')
        lbl = tk.Label(win, text='⚙  ' + HINTS.get(self.lang, HINTS['en']),
                       fg='white', bg='#1f6feb', font=('Segoe UI', 10, 'bold'),
                       padx=16, pady=10, cursor='hand2')
        lbl.pack()
        win.update_idletasks()
        win.geometry(f'+{self.root.winfo_x()}+{max(0, self.root.winfo_y()-46)}')

        def open_settings(_e=None):
            x = win.winfo_x() + 10
            y = win.winfo_y()
            win.destroy()
            self.root.after(60, lambda: self._popup_menu(x, y))

        lbl.bind('<Button-1>', open_settings)
        win.bind('<Button-1>', open_settings)
        win.after(8000, lambda: win.winfo_exists() and win.destroy())

    def t(self, key):
        """Translate a key into the current language (fallback English)."""
        return T.get(self.lang, T['en']).get(key, T['en'].get(key, key))

    def tip(self, key):
        """Translate a tooltip-body string for the current language."""
        return TIP.get(self.lang, TIP['en']).get(key, TIP['en'].get(key, key))

    def _load_menu_icons(self):
        """Load the 16px menu icons once; return name->PhotoImage dict."""
        icons = {}
        mdir = os.path.join(ICON_DIR, 'menu')
        for name in ('metrics','position','size','opacity','clock','globe',
                     'refresh','fullscreen','power','language','info','close','heart'):
            try:
                icons[name] = tk.PhotoImage(file=os.path.join(mdir, name + '.png'))
            except Exception:
                icons[name] = None
        return icons

    def _load_wx_icons(self):
        """Load the weather condition icons once; return name->PhotoImage dict."""
        icons = {}
        for name in ('wx_clear','wx_partly','wx_cloudy','wx_fog','wx_rain','wx_snow','wx_storm'):
            try:
                icons[name] = tk.PhotoImage(file=os.path.join(ICON_DIR, name + '.png'))
            except Exception:
                icons[name] = None
        return icons

    def _bind_events(self):
        """Bind drag + right-click on the window AND every child widget,
        so clicks on the icons/numbers still work."""
        def bind_all(w):
            # only drag on the widget; all settings live in the tray icon
            w.bind('<Button-1>', self._drag_start)
            w.bind('<B1-Motion>', self._drag_move)
            w.bind('<ButtonRelease-1>', self._drag_end)
            for child in w.winfo_children():
                bind_all(child)
        bind_all(self.root)

    # ── positioning ───────────────────────────────────────────────────
    def _position(self):
        wa_bottom, taskbar_h, screen_w = get_taskbar_info()
        screen_h = wa_bottom + taskbar_h
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        on_tb = self.cfg.get('on_taskbar')
        # Lowest allowed top-y. In 'on taskbar' mode the widget may sit inside
        # the taskbar band (kept on top by an aggressive re-assert loop). In
        # 'above' mode it must NEVER enter the band — on Win11 the taskbar's
        # XAML surface paints over any window there, making it vanish.
        max_y = (screen_h - h) if on_tb else max(0, wa_bottom - h - 1)
        if self.cfg.get('free_pos'):
            # custom position from dragging
            x = min(max(0, int(self.cfg.get('pos_x', 0))), max(0, screen_w - w))
            y = min(max(0, int(self.cfg.get('pos_y', 0))), max(0, max_y))
        else:
            align = self.cfg['align']
            if align == 'center':
                x = (screen_w - w) // 2
            elif align == 'right':
                x = screen_w - w - 8
            else:
                x = 4
            if on_tb:
                # sit ON the taskbar, vertically centred in its band
                y = wa_bottom + max(0, (taskbar_h - h) // 2)
            else:
                # float just ABOVE the taskbar — always visible, any layout
                y = max(0, wa_bottom - h - 1)
        self.root.geometry(f'+{x}+{y}')
        # keep the colour key alive after any resize (Windows quirk)
        if self.cfg.get('transparent_bg'):
            try:
                self.root.attributes('-transparentcolor', self.bg)
            except Exception:
                pass

    # ── icon loader ───────────────────────────────────────────────────
    def _icon(self, name):
        try:
            img = tk.PhotoImage(file=os.path.join(ICON_DIR, name))
            self._imgs.append(img)
            tk.Label(self.root, image=img, bg=self.bg, bd=0).pack(side='left', padx=(4, 1))
        except Exception:
            pass   # never let a missing icon crash the widget

    def _rebuild(self):
        """Rebuild the UI safely (deferred until any menu grab is gone)."""
        try:
            if self.root.grab_current() is not None:
                self.root.after(50, self._rebuild)   # a menu is still up; wait
                return
        except Exception:
            pass
        _log('rebuild start')
        try:
            self._build_ui(); self._position()
            # Re-assert the colour key: after the window resizes, Windows can
            # stop keying out the background and show it as a dark box.
            if self.cfg.get('transparent_bg'):
                try:
                    self.root.attributes('-transparentcolor', self.bg)
                except Exception:
                    pass
            _log('rebuild done')
        except Exception:
            _log('rebuild EXC:\n' + traceback.format_exc())

    @property
    def theme(self):
        return THEMES.get(self.cfg.get('theme', 'default'), THEMES['default'])

    # ── UI ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        for w in self.root.winfo_children():
            w.destroy()
        self._imgs = []
        self._tip_cells = []     # [(frame, kind, extra)] for hover tooltips
        self._disk_lbls = {}     # {drive: label} for per-drive space %
        self._rgb_targets = []   # value labels recolored by RGB animation
        self._sep_labels = []    # separators recolored by RGB animation
        th = self.theme
        big, small = FONT_SCALES[self.cfg['font_scale']]
        vf = ('Consolas', big, 'bold')
        nf = ('Consolas', small, 'bold')
        valcol = th['val']
        vertical = self.cfg.get('orientation') == 'vertical'

        self.lbl_cpu = self.lbl_ram = self.lbl_up = self.lbl_dn = None
        self.lbl_disk_r = self.lbl_disk_w = self.lbl_batt = self.lbl_gpu = None
        self.spark_cpu = self.spark_ram = None

        # ── helpers (operate on a given parent frame = "cell") ──
        def icon(name, parent):
            try:
                img = tk.PhotoImage(file=os.path.join(ICON_DIR, name))
                self._imgs.append(img)
                tk.Label(parent, image=img, bg=self.bg, bd=0).pack(side='left', padx=(4, 1))
            except Exception:
                pass

        def val(parent, width):
            l = tk.Label(parent, text='', fg=valcol, width=width,
                         bg=self.bg, font=vf, pady=0, padx=2)
            l.pack(side='left'); self._rgb_targets.append(l); return l

        def spark(parent):
            if not self.cfg.get('sparklines'):
                return None
            c = tk.Canvas(parent, width=26, height=max(14, (self.H if not vertical else 18) - 6),
                          bg=self.bg, highlightthickness=0)
            c.pack(side='left', padx=(0, 2))
            return c

        # metrics container
        mc = tk.Frame(self.root, bg=self.bg)
        mc.pack(side='top', anchor='w')

        cells = []
        def new_cell():
            f = tk.Frame(mc, bg=self.bg)
            cells.append(f)
            return f

        cpu_w = 10 if self.cfg.get('cpu_freq') else 4
        ram_w = 9 if self.cfg.get('ram_gb') else 4
        stacked = self.cfg.get('stacked', True)
        self.lbl_cpu_top = self.lbl_ram_top = None

        def stat(icon_name, width, has_top):
            """A metric cell. Stacked = detail (e.g. GHz) on top, % below.
            Returns (cell, value_label, top_label_or_None)."""
            f = new_cell(); icon(icon_name, f)
            if stacked:
                col = tk.Frame(f, bg=self.bg); col.pack(side='left', padx=2)
                top = None
                if has_top:
                    top = tk.Label(col, text='', fg=valcol, bg=self.bg, font=nf,
                                   width=width, anchor='w', padx=0, pady=0)
                    top.pack(side='top', anchor='w'); self._rgb_targets.append(top)
                v = tk.Label(col, text='', fg=valcol, bg=self.bg, font=nf,
                             width=width, anchor='w', padx=0, pady=0)
                v.pack(side='top', anchor='w'); self._rgb_targets.append(v)
                return f, v, top
            return f, val(f, width), None

        sw = 7   # stacked column width fits "4.0 GHz" / "15.1 GB" / "100%"
        if self.cfg['show_cpu']:
            f, self.lbl_cpu, self.lbl_cpu_top = stat('cpu.png', sw if stacked else cpu_w, True)
            self.spark_cpu = spark(f); self._tip_cells.append((f, 'cpu', None))
        if self.cfg['show_ram']:
            f, self.lbl_ram, self.lbl_ram_top = stat('ram.png', sw if stacked else ram_w, True)
            self.spark_ram = spark(f); self._tip_cells.append((f, 'ram', None))
        if self.cfg.get('show_gpu'):
            f, self.lbl_gpu, self.lbl_gpu_top = stat('gpu.png', sw if stacked else 4, stacked)
            self._tip_cells.append((f, 'gpu', None))
        if self.cfg['show_net']:
            f = new_cell(); icon('net.png', f)
            nfr = tk.Frame(f, bg=self.bg); nfr.pack(side='left', padx=2)
            def net_row(arrow, color):
                row = tk.Frame(nfr, bg=self.bg); row.pack(side='top', anchor='w')
                tk.Label(row, text=arrow, fg=color, bg=self.bg, font=nf, padx=0).pack(side='left')
                v = tk.Label(row, text='  0K', fg=valcol, bg=self.bg,
                             font=nf, width=7, anchor='w', padx=1)
                v.pack(side='left'); self._rgb_targets.append(v); return v
            self.lbl_up = net_row('▲', self.COLORS['up'])
            self.lbl_dn = net_row('▼', self.COLORS['dn'])
            self._tip_cells.append((f, 'net', None))
        if self.cfg.get('show_disk'):
            f = new_cell(); icon('disk.png', f)
            dfr = tk.Frame(f, bg=self.bg); dfr.pack(side='left', padx=2)
            def disk_row(arrow, color):
                row = tk.Frame(dfr, bg=self.bg); row.pack(side='top', anchor='w')
                tk.Label(row, text=arrow, fg=color, bg=self.bg, font=nf, padx=0).pack(side='left')
                v = tk.Label(row, text='  0K', fg=valcol, bg=self.bg,
                             font=nf, width=7, anchor='w', padx=1)
                v.pack(side='left'); self._rgb_targets.append(v); return v
            self.lbl_disk_r = disk_row('R', self.COLORS['dn'])
            self.lbl_disk_w = disk_row('W', self.COLORS['up'])
            self._tip_cells.append((f, 'disk', None))
        # per-drive space % cells (e.g. C: 60%)
        for drive in self.cfg.get('disks', []):
            f = new_cell(); icon('disk.png', f)
            lbl = tk.Label(f, text=f'{drive[0]} ..', fg=valcol, bg=self.bg,
                           font=nf if stacked else vf, width=6, anchor='w', padx=2)
            lbl.pack(side='left'); self._rgb_targets.append(lbl)
            self._disk_lbls[drive] = lbl
            self._tip_cells.append((f, 'diskspace', drive))
        if self.cfg.get('show_batt') and self._has_batt:
            f, self.lbl_batt, _ = stat('battery.png', sw if stacked else 5, stacked)
            self._tip_cells.append((f, 'batt', None))
        self.lbl_wx = self.lbl_wx_icon = None
        if self.cfg.get('show_weather'):
            f = new_cell()
            self.lbl_wx_icon = tk.Label(f, image=self._wx_icons.get('wx_cloudy'),
                                        bg=self.bg, bd=0)
            self.lbl_wx_icon.pack(side='left', padx=(4, 1))
            self.lbl_wx = tk.Label(f, text='', fg=valcol, bg=self.bg,
                                   font=(vf if not stacked else nf), width=5, anchor='w', padx=2)
            self.lbl_wx.pack(side='left'); self._rgb_targets.append(self.lbl_wx)
            self._tip_cells.append((f, 'weather', None))

        # place cells according to orientation
        for i, f in enumerate(cells):
            if vertical:
                f.pack(side='top', anchor='w')
            else:
                if i > 0:
                    s = tk.Label(mc, text='│', fg=th['accent'], bg=self.bg,
                                 font=('Consolas', big+1), padx=3)
                    s.pack(side='left'); self._sep_labels.append(s)
                f.pack(side='left')

        # hover tooltips with details
        if self.cfg.get('tooltips'):
            for frame, kind, extra in self._tip_cells:
                self._bind_hover(frame, kind, extra)

        # (re)bind drag + right-click to all the new widgets
        if hasattr(self, '_show_menu'):
            self._bind_events()

    # ── colors ─────────────────────────────────────────────────────────
    def _load_color(self, p):
        if self.cfg.get('theme') == 'rgb':
            return self._rgb_color        # animation owns the color
        if p >= 85: return '#f85149'
        if p >= 70: return '#ff7b72'
        if p >= 50: return '#ffa657'
        return self.theme['val']

    def _spark_color(self):
        if self.cfg.get('theme') == 'rgb':
            return self._rgb_color
        return self.theme['spark']

    def _draw_spark(self, canvas, hist):
        if not canvas: return
        canvas.delete('all')
        if len(hist) < 2: return
        w = int(canvas['width']); h = int(canvas['height'])
        step = w / max(1, hist.maxlen - 1)
        pts = []
        for i, v in enumerate(hist):
            x = i * step
            y = h - 1 - (v / 100.0) * (h - 2)
            pts.append((x, y))
        flat = [c for p in pts for c in p]
        canvas.create_line(*flat, fill=self._spark_color(), width=2, smooth=True)

    # ── RGB animation (gaming theme) ───────────────────────────────────
    def _animate(self):
        try:
            if self.cfg.get('theme') == 'rgb' and self._visible:
                self._rgb_hue = (self._rgb_hue + 0.012) % 1.0
                self._rgb_color = hsv_to_hex(self._rgb_hue)
                # rainbow wave: each metric is offset along the spectrum
                n = max(1, len(self._rgb_targets))
                for i, w in enumerate(self._rgb_targets):
                    try: w.config(fg=hsv_to_hex((self._rgb_hue + i / n) % 1.0))
                    except Exception: pass
                comp = hsv_to_hex((self._rgb_hue + 0.5) % 1.0, 0.9, 0.5)
                for s in self._sep_labels:
                    try: s.config(fg=comp)
                    except Exception: pass
                if self.spark_cpu: self._draw_spark(self.spark_cpu, self._hist['cpu'])
                if self.spark_ram: self._draw_spark(self.spark_ram, self._hist['ram'])
                delay = 60
            else:
                delay = 400
        except Exception:
            delay = 400
        self.root.after(delay, self._animate)

    def _fmt(self, delta_bytes):
        """Format a per-interval byte delta as a per-second rate (bytes or bits)."""
        secs = max(0.001, self.cfg['interval'] / 1000.0)
        per_sec = delta_bytes / secs
        if self.cfg.get('net_unit') == 'bits':
            bits = per_sec * 8
            if bits >= 1e9: return f'{bits/1e9:.1f} Gb'
            if bits >= 1e6:
                mb = bits/1e6
                return f'{mb:.0f} Mb' if mb >= 100 else f'{mb:.1f} Mb'
            if bits >= 1e3: return f'{bits/1e3:.0f} Kb'
            return f'{bits:.0f} b'
        # bytes
        b = per_sec
        if b >= 1_073_741_824: return f'{b/1_073_741_824:.1f} G'
        if b >= 1_048_576:
            mb = b / 1_048_576
            return f'{mb:.0f} M' if mb >= 100 else f'{mb:.1f} M'
        if b >= 1024:          return f'{b/1024:.0f} K'
        return f'{b:.0f} B'

    # ── keep above games / fullscreen apps ─────────────────────────────
    def _keep_on_top(self):
        """Re-assert TOPMOST above every other window.

        'Above the taskbar' mode: a plain HWND_TOPMOST re-assert is enough.

        'On the taskbar' mode: the taskbar's own surface keeps re-stacking over
        us, and a plain HWND_TOPMOST is a *no-op* when we are already topmost —
        so it never lifts us back. Instead we briefly drop to NOTOPMOST and
        re-insert at the very TOP of the topmost band, which reliably raises us
        over the taskbar. Both calls run inside a single compositor frame, so
        there is no visible flicker."""
        try:
            u = ctypes.windll.user32
            hwnd = u.GetParent(self.root.winfo_id()) or self.root.winfo_id()
            HWND_TOPMOST = -1; HWND_NOTOPMOST = -2
            f = 0x0001 | 0x0002 | 0x0010   # NOSIZE | NOMOVE | NOACTIVATE
            if self.cfg.get('on_taskbar'):
                u.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, f)
                u.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, f)
                u.BringWindowToTop(hwnd)
            else:
                u.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, f)
        except Exception:
            pass

    def _foreground_loop(self):
        """Keep the widget reliably above all other windows."""
        if self._visible:
            self._keep_on_top()
        # When docked ON the taskbar we must out-race the taskbar's own repaints,
        # so re-assert TOPMOST very frequently; floating just above the bar needs
        # only a light periodic touch.
        interval = 30 if self.cfg.get('on_taskbar') else 250
        self.root.after(interval, self._foreground_loop)

    def _is_fullscreen_foreground(self):
        """True if a fullscreen app (game/video) is in front → taskbar is hidden."""
        try:
            u = ctypes.windll.user32
            hwnd = u.GetForegroundWindow()
            if not hwnd:
                return False
            buf = ctypes.create_unicode_buffer(256)
            u.GetClassNameW(hwnd, buf, 256)
            # ignore the desktop / shell / taskbar themselves
            if buf.value in ('Shell_TrayWnd', 'Progman', 'WorkerW', 'Windows.UI.Core.CoreWindow', ''):
                return False
            r = RECT()
            u.GetWindowRect(hwnd, ctypes.byref(r))
            sw = u.GetSystemMetrics(0); sh = u.GetSystemMetrics(1)
            return r.left <= 0 and r.top <= 0 and r.right >= sw and r.bottom >= sh
        except Exception:
            return False

    def _follow_taskbar(self):
        """Hide/show the widget together with the taskbar (like the clock)."""
        if not self.cfg.get('follow_taskbar', True):
            if not self._visible:
                self.root.deiconify(); self._visible = True
            self._keep_on_top()
            return
        hide = self._is_fullscreen_foreground()
        if hide and self._visible:
            self.root.withdraw(); self._visible = False
        elif not hide and not self._visible:
            self.root.deiconify(); self._visible = True
            self._keep_on_top()
        elif self._visible:
            self._keep_on_top()

    # ── process sampler (feeds the tooltips) ───────────────────────────
    def _proc_sampler(self):
        try:
            for p in psutil.process_iter():
                try: p.cpu_percent()
                except Exception: pass
        except Exception:
            pass
        ncpu = psutil.cpu_count() or 1
        while True:
            time.sleep(2.0)
            procs = []
            try:
                for p in psutil.process_iter(['name', 'memory_info']):
                    try:
                        nm = p.info.get('name') or '?'
                        if nm in ('System Idle Process', 'Idle') or p.pid == 0:
                            continue
                        mi = p.info.get('memory_info')
                        procs.append((nm, p.cpu_percent(), mi.rss if mi else 0))
                    except Exception:
                        continue
            except Exception:
                continue
            tc = sorted(procs, key=lambda x: x[1], reverse=True)[:3]
            tm = sorted(procs, key=lambda x: x[2], reverse=True)[:3]
            self._proc_top = {'cpu': [(n, c / ncpu) for n, c, m in tc],
                              'mem': [(n, m) for n, c, m in tm]}

    # ── auto-update check ──────────────────────────────────────────────
    def _update_check_worker(self):
        time.sleep(8)
        self._check_updates()

    def _check_updates(self):
        if not self.cfg.get('check_updates', True):
            return
        try:
            if time.time() - float(self.cfg.get('last_update_check', 0)) < 12 * 3600:
                return
        except Exception:
            pass
        try:
            data = _http_json(RELEASES_API, timeout=8)
            tag = (data.get('tag_name') or '').lstrip('vV')
            self.cfg['last_update_check'] = int(time.time())
            save_config(self.cfg)
            if tag and _ver_tuple(tag) > _ver_tuple(VERSION):
                self._update_tag = tag
                try:
                    if getattr(self, '_tray', None):
                        self._tray.notify(
                            f'PulseBar {tag} — ' + UPDATE_LABEL.get(self.lang, UPDATE_LABEL['en']),
                            'PulseBar')
                except Exception:
                    pass
        except Exception:
            pass

    def _open_releases(self):
        try:
            webbrowser.open(RELEASES_URL)
        except Exception:
            pass

    # ── hover tooltips ─────────────────────────────────────────────────
    def _all_widgets(self, w):
        out = [w]
        for c in w.winfo_children():
            out += self._all_widgets(c)
        return out

    def _bind_hover(self, frame, kind, extra):
        def on_enter(_e, k=kind, x=extra, fr=frame):
            if self._tip_hide_job:
                try: self.root.after_cancel(self._tip_hide_job)
                except Exception: pass
                self._tip_hide_job = None
            self._show_tip(k, x, fr)
        def on_leave(_e):
            self._tip_hide_job = self.root.after(180, self._hide_tip)
        for w in self._all_widgets(frame):
            w.bind('<Enter>', on_enter, add='+')
            w.bind('<Leave>', on_leave, add='+')

    def _hide_tip(self):
        self._tip_hide_job = None
        if self._tip is not None:
            try: self._tip.destroy()
            except Exception: pass
            self._tip = None

    @staticmethod
    def _hb(n):
        n = float(n)
        for u in ('B', 'KB', 'MB', 'GB', 'TB'):
            if n < 1024: return (f'{n:.0f} {u}' if u == 'B' else f'{n:.1f} {u}')
            n /= 1024
        return f'{n:.1f} PB'

    @staticmethod
    def _used_total(used, total):
        """Compact 'used/total' GB string that fits a 7-char column."""
        if not total:
            return f'{used:.1f}'
        if total >= 100:
            return f'{used:.0f}/{total:.0f}'
        return f'{used:.1f}/{total:.0f}'

    def _tip_content(self, kind, extra):
        GREEN='#3fb950'; ORANGE='#ffa657'; BLUE='#58a6ff'; PURPLE='#a371f7'
        tp = self.tip
        rows = []; bars = []; title = ('', '')
        try:
            if kind == 'cpu':
                cpu = sum(self._percpu)/len(self._percpu) if self._percpu else psutil.cpu_percent()
                ghz = self._cpufreq.read_ghz()
                title = ('CPU', f'{cpu:.0f}%' + (f'  ·  {ghz:.1f} GHz' if ghz else ''))
                rows.append((tp('top'), '', None))
                for n, c in self._proc_top.get('cpu', []) or [(tp('sampling'), None)]:
                    rows.append((n[:18], (f'{c:.1f}%' if c is not None else ''), ORANGE))
                bars = list(self._percpu)
            elif kind == 'ram':
                vm = psutil.virtual_memory()
                title = ('RAM', f'{vm.used/1073741824:.1f} / {vm.total/1073741824:.1f} GB')
                rows.append((tp('used'), f'{vm.percent:.0f}%', ORANGE))
                rows.append((tp('free'), f'{vm.available/1073741824:.1f} GB', GREEN))
                rows.append((tp('top'), '', None))
                for n, m in self._proc_top.get('mem', []) or [(tp('sampling'), None)]:
                    rows.append((n[:18], (self._hb(m) if m is not None else ''), GREEN))
            elif kind == 'gpu':
                title = ('GPU', (f'{self._gpu:.0f}%' if self._gpu is not None else 'n/a'))
                if self._gpu_mem is not None and self._vram_total:
                    rows.append(('VRAM', f'{self._gpu_mem:.1f} / {self._vram_total:.1f} GB', GREEN))
                    rows.append((tp('vramused'), f'{self._gpu_mem / self._vram_total * 100:.0f}%', ORANGE))
                elif self._gpu_mem is not None:
                    rows.append((tp('vramused'), f'{self._gpu_mem:.1f} GB', GREEN))
                elif self._vram_total:
                    rows.append(('VRAM', f'{self._vram_total:.1f} GB', GREEN))
                rows.append((tp('source'), '', None))
            elif kind == 'net':
                title = (self.t('net'), '')
                rows.append((tp('session') + ' ↑', self._hb(self._net_session['up']), BLUE))
                rows.append((tp('session') + ' ↓', self._hb(self._net_session['dn']), GREEN))
                io = psutil.net_io_counters()
                rows.append((tp('total') + ' ↑', self._hb(io.bytes_sent), None))
                rows.append((tp('total') + ' ↓', self._hb(io.bytes_recv), None))
            elif kind == 'disk':
                title = (self.t('disk') + ' I/O', '')
                rows.append((tp('perdisk'), '', None))
                if self._perdisk_rates:
                    for d, (rd, wr) in self._perdisk_rates.items():
                        rows.append((d[:14], f'{self._hb(rd)}/s · {self._hb(wr)}/s', PURPLE))
                else:
                    rows.append((tp('sampling'), '', None))
            elif kind == 'diskspace':
                u = psutil.disk_usage(extra + '\\')
                title = (extra, f'{u.percent:.0f}%')
                rows.append((tp('used'), self._hb(u.used), ORANGE))
                rows.append((tp('free'), self._hb(u.free), GREEN))
                rows.append((tp('total'), self._hb(u.total), None))
            elif kind == 'batt':
                b = psutil.sensors_battery()
                if b:
                    title = (self.t('batt'), f'{int(b.percent)}%')
                    rows.append((tp('status'),
                                 tp('charging') if b.power_plugged else tp('onbatt'), None))
                    if b.secsleft and b.secsleft > 0 and not b.power_plugged:
                        rows.append((tp('timeleft'), f'{b.secsleft//3600}h {(b.secsleft%3600)//60}m', None))
            elif kind == 'weather':
                title = (self.t('weather'), '')
                w = self._weather or {}
                if w:
                    unit = self.cfg.get('weather_unit', 'C')
                    if w.get('city'): rows.append((str(w.get('city')), '', None))
                    rows.append((tp('now'), f"{w.get('temp','?')}°{unit}", ORANGE))
                    if w.get('feels') is not None:
                        rows.append((tp('feels'), f"{w['feels']}°{unit}", None))
                    if w.get('humidity'):
                        rows.append((tp('humidity'), f"{w['humidity']}%", BLUE))
                    if w.get('wind') is not None:
                        rows.append((tp('wind'), f"{w['wind']} {w.get('wind_unit','km/h')}", None))
                    daily = w.get('daily') or []
                    if daily:
                        rows.append((tp('forecast'), '', None))
                        wd = WDAYS.get(self.lang, WDAYS['en'])
                        for dd in daily:
                            nm = wd[dd['wd']] if 0 <= dd.get('wd', 0) < 7 else ''
                            rows.append((nm, f"{dd['tmin']}° / {dd['tmax']}°", GREEN))
                else:
                    rows.append((tp('loading'), '', None))
        except Exception:
            rows.append(('—', '', None))
        return title, rows, bars

    def _show_tip(self, kind, extra, frame):
        if not self.cfg.get('tooltips') or not self._visible:
            return
        title, rows, bars = self._tip_content(kind, extra)
        self._hide_tip()
        PANEL='#161b22'; LINE='#2d333b'; GREY='#8b96a2'; WHITE='#ecf2f8'
        tcol = {'cpu':'#58a6ff','ram':'#3fb950','gpu':'#39d3c3','net':'#58a6ff',
                'disk':'#a371f7','diskspace':'#a371f7','batt':'#3fb950',
                'weather':'#ffa657'}.get(kind, '#58a6ff')
        tip = tk.Toplevel(self.root)
        tip.overrideredirect(True); tip.attributes('-topmost', True)
        try: tip.attributes('-alpha', 0.97)
        except Exception: pass
        outer = tk.Frame(tip, bg=LINE); outer.pack()
        inner = tk.Frame(outer, bg=PANEL); inner.pack(padx=1, pady=1)
        hdr = tk.Frame(inner, bg=PANEL); hdr.pack(fill='x', padx=12, pady=(9, 5))
        tk.Label(hdr, text=title[0], fg=tcol, bg=PANEL,
                 font=('Segoe UI', 10, 'bold')).pack(side='left')
        if title[1]:
            tk.Label(hdr, text='   '+title[1], fg=WHITE, bg=PANEL,
                     font=('Segoe UI', 10, 'bold')).pack(side='right')
        tk.Frame(inner, bg=LINE, height=1).pack(fill='x', padx=10)
        for label, value, vcol in rows:
            r = tk.Frame(inner, bg=PANEL); r.pack(fill='x', padx=12, pady=1)
            is_hdr = (value == '' or value is None)
            tk.Label(r, text=label, fg=(GREY if is_hdr else WHITE), bg=PANEL,
                     font=('Segoe UI', 9, 'bold' if is_hdr else 'normal')).pack(side='left')
            if not is_hdr:
                tk.Label(r, text=value, fg=vcol or WHITE, bg=PANEL,
                         font=('Segoe UI', 9, 'bold')).pack(side='right')
        if bars:
            bf = tk.Frame(inner, bg=PANEL); bf.pack(fill='x', padx=12, pady=(3, 9))
            tk.Label(bf, text=self.tip('cores'), fg=GREY, bg=PANEL,
                     font=('Segoe UI', 9)).pack(side='left', padx=(0, 8))
            cv = tk.Canvas(bf, width=len(bars)*9, height=18, bg=PANEL, highlightthickness=0)
            cv.pack(side='left')
            for i, v in enumerate(bars):
                h = max(1, int(16 * v / 100.0))
                cv.create_rectangle(i*9, 17-h, i*9+6, 17,
                                    fill=('#58a6ff' if v > 50 else '#2d5a96'), outline='')
        else:
            tk.Frame(inner, bg=PANEL, height=7).pack()
        tip.update_idletasks()
        tw = tip.winfo_reqwidth(); th = tip.winfo_reqheight()
        sw = self.root.winfo_screenwidth()
        fx, fy = frame.winfo_rootx(), frame.winfo_rooty()
        x = min(max(2, fx - 6), sw - tw - 4)
        y = fy - th - 6
        if y < 0: y = fy + frame.winfo_height() + 6
        tip.geometry(f'+{x}+{y}')
        self._tip = tip

    # ── update loop ────────────────────────────────────────────────────
    def _update(self):
        self._follow_taskbar()
        # CPU% is always sampled so history stays continuous for sparklines
        per = psutil.cpu_percent(percpu=True)
        self._percpu = per
        cpu = (sum(per) / len(per)) if per else psutil.cpu_percent()
        self._hist['cpu'].append(cpu)
        if self.lbl_cpu:
            ghz = self._cpufreq.read_ghz()
            if ghz is None:
                try:
                    f = psutil.cpu_freq()
                    if f and f.current:
                        ghz = f.current / 1000
                except Exception:
                    pass
            if self.lbl_cpu_top is not None:
                # stacked: GHz on top, % below
                self.lbl_cpu_top.config(text=(f'{ghz:.1f} GHz' if ghz else ''))
                self.lbl_cpu.config(text=f'{cpu:3.0f}%', fg=self._load_color(cpu))
            else:
                txt = f'{cpu:3.0f}%'
                if self.cfg.get('cpu_freq') and ghz:
                    txt += f' {ghz:.1f}G'
                self.lbl_cpu.config(text=txt, fg=self._load_color(cpu))
            self._draw_spark(self.spark_cpu, self._hist['cpu'])
        if self.lbl_ram:
            vm = psutil.virtual_memory()
            ram = vm.percent
            self._hist['ram'].append(ram)
            used_gb = vm.used / 1073741824
            if self.lbl_ram_top is not None:
                self.lbl_ram_top.config(text=self._used_total(used_gb, vm.total / 1073741824))
                self.lbl_ram.config(text=f'{ram:3.0f}%', fg=self._load_color(ram))
            else:
                txt = f'{ram:3.0f}%'
                if self.cfg.get('ram_gb'):
                    txt += f' {used_gb:.1f}G'
                self.lbl_ram.config(text=txt, fg=self._load_color(ram))
            self._draw_spark(self.spark_ram, self._hist['ram'])
        if self.lbl_up:
            net = psutil.net_io_counters()
            up = net.bytes_sent - self._prev_net.bytes_sent
            dn = net.bytes_recv - self._prev_net.bytes_recv
            self._prev_net = net
            self._net_session['up'] += max(0, up)
            self._net_session['dn'] += max(0, dn)
            self.lbl_up.config(text=f'{self._fmt(up):>6}')
            self.lbl_dn.config(text=f'{self._fmt(dn):>6}')
        if self.lbl_disk_r:
            try:
                d = psutil.disk_io_counters()
                if self._prev_disk:
                    rd = d.read_bytes  - self._prev_disk.read_bytes
                    wr = d.write_bytes - self._prev_disk.write_bytes
                    self.lbl_disk_r.config(text=f'{self._fmt(rd):>6}')
                    self.lbl_disk_w.config(text=f'{self._fmt(wr):>6}')
                self._prev_disk = d
            except Exception:
                pass
        # per-disk I/O rates (for the disk tooltip)
        if self.cfg.get('tooltips') and (self.lbl_disk_r or self._disk_lbls):
            try:
                pd = psutil.disk_io_counters(perdisk=True)
                if self._perdisk_prev:
                    secs = max(0.001, self.cfg['interval'] / 1000.0)
                    rates = {}
                    for k, v in pd.items():
                        p = self._perdisk_prev.get(k)
                        if p:
                            rates[k] = ((v.read_bytes - p.read_bytes) / secs,
                                        (v.write_bytes - p.write_bytes) / secs)
                    self._perdisk_rates = rates
                self._perdisk_prev = pd
            except Exception:
                pass
        # per-drive space %
        for drive, lbl in self._disk_lbls.items():
            try:
                u = psutil.disk_usage(drive + '\\')
                lbl.config(text=f'{drive[0]} {u.percent:.0f}%', fg=self._load_color(u.percent))
            except Exception:
                pass
        if self.lbl_batt:
            b = psutil.sensors_battery()
            if b is not None:
                pct = int(b.percent)
                col = '#f85149' if pct <= 15 else ('#ffa657' if pct <= 30 else self.theme['val'])
                plug = '⚡' if b.power_plugged else ''
                self.lbl_batt.config(text=f'{plug}{pct}%', fg=col)
        if self.lbl_gpu:
            g = self._gpu
            self.lbl_gpu.config(text=(f'{g:3.0f}%' if g is not None else '  —'),
                                fg=self._load_color(g if g is not None else 0))
            if getattr(self, 'lbl_gpu_top', None) is not None:
                self.lbl_gpu_top.config(
                    text=(self._used_total(self._gpu_mem, self._vram_total)
                          if self._gpu_mem is not None else ''))
        if getattr(self, 'lbl_wx', None):
            w = self._weather
            sym = '°' + (self.cfg.get('weather_unit', 'C'))
            if w:
                ic = self._wx_icons.get(weather_icon_name(w['code']))
                if ic is not None:
                    self.lbl_wx_icon.config(image=ic)
                self.lbl_wx.config(text=f"{w['temp']}{sym}")
            else:
                self.lbl_wx.config(text='—')
        self.root.after(self.cfg['interval'], self._update)

    # ── drag ───────────────────────────────────────────────────────────
    def _drag_start(self, e):
        if self.cfg.get('locked'): return
        self._dx, self._dy = e.x, e.y; self._dragging = False
    def _drag_move(self, e):
        if self.cfg.get('locked'): return
        wa_bottom, taskbar_h, screen_w = get_taskbar_info()
        w = self.root.winfo_width(); h = self.root.winfo_height()
        x = self.root.winfo_x() + e.x - self._dx
        y = self.root.winfo_y() + e.y - self._dy
        # In 'above' mode never enter the taskbar dead zone; in 'on taskbar'
        # mode the band is allowed (kept visible by the fast keep-on-top loop).
        max_y = (wa_bottom + taskbar_h - h) if self.cfg.get('on_taskbar') else (wa_bottom - h - 1)
        x = min(max(0, x), max(0, screen_w - w))
        y = min(max(0, y), max(0, max_y))
        self.root.geometry(f'+{x}+{y}')
        self._dragging = True

    def _drag_end(self, e):
        if self.cfg.get('locked'): return
        if getattr(self, '_dragging', False):
            self._dragging = False
            wa_bottom, taskbar_h, screen_w = get_taskbar_info()
            w = self.root.winfo_width(); h = self.root.winfo_height()
            max_y = (wa_bottom + taskbar_h - h) if self.cfg.get('on_taskbar') else (wa_bottom - h - 1)
            self.cfg['free_pos'] = True
            self.cfg['pos_x'] = min(max(0, self.root.winfo_x()), max(0, screen_w - w))
            self.cfg['pos_y'] = min(max(0, self.root.winfo_y()), max(0, max_y))
            save_config(self.cfg)

    # ── settings helpers ───────────────────────────────────────────────
    def _set(self, key, value):
        self.cfg[key] = value
        save_config(self.cfg)

    def _apply_rebuild(self):
        self._build_ui(); self._position(); self._update_once()

    def _update_once(self):
        # refresh values immediately after rebuild
        try: self.lbl_cpu and self.lbl_cpu.config(text='..')
        except Exception: pass

    def _set_opacity(self, v):
        self._set('opacity', v); self.root.attributes('-alpha', v)

    def _set_scale(self, v):
        self._set('font_scale', v); self._pending_rebuild = True

    def _set_interval(self, v):
        self._set('interval', v)

    def _toggle_metric(self, key):
        # keep at least one visible
        all_keys = ('show_cpu','show_ram','show_net','show_disk','show_batt','show_gpu')
        others = [k for k in all_keys if k != key]
        if self.cfg.get(key) and not any(self.cfg.get(o) for o in others):
            return
        _log(f'toggle_metric {key} -> {not self.cfg.get(key)}')
        self._set(key, not self.cfg.get(key))
        self._pending_rebuild = True
        if key == 'show_gpu' and self.cfg.get('show_gpu'):
            self.root.after(50, self._ensure_gpu_thread)

    def _set_theme(self, name):
        self._set('theme', name); self._pending_rebuild = True

    def _set_orientation(self, v):
        self._set('orientation', v); self._pending_rebuild = True

    def _toggle_sparklines(self):
        self._set('sparklines', not self.cfg.get('sparklines')); self._pending_rebuild = True

    def _toggle_detail(self, key):
        self._set(key, not self.cfg.get(key)); self._pending_rebuild = True

    # ── right-click menu ───────────────────────────────────────────────
    def _submenu(self, parent):
        return tk.Menu(parent, tearoff=0, bg='#161b22', fg='white',
                       activebackground='#21262d', font=('Segoe UI', 9))

    def _show_menu(self, e):
        self._popup_menu(e.x_root, e.y_root)

    def _popup_menu(self, px, py):
        c = self.cfg; t = self.t; ic = self._micons
        m = self._submenu(self.root)

        def cascade(icon, label, sub):
            m.add_cascade(label='  '+label, image=ic.get(icon),
                          compound='left', menu=sub)

        def item(icon, label, cmd):
            m.add_command(label='  '+label, image=ic.get(icon),
                          compound='left', command=cmd)

        # Metrics
        met = self._submenu(m)
        met.add_command(label=('☑ ' if c['show_cpu'] else '☐ ')+t('cpu'), command=lambda: self._toggle_metric('show_cpu'))
        met.add_command(label=('☑ ' if c['show_ram'] else '☐ ')+t('ram'), command=lambda: self._toggle_metric('show_ram'))
        met.add_command(label=('☑ ' if c['show_net'] else '☐ ')+t('net'), command=lambda: self._toggle_metric('show_net'))
        met.add_command(label=('☑ ' if c.get('show_gpu') else '☐ ')+t('gpu'), command=lambda: self._toggle_metric('show_gpu'))
        met.add_command(label=('☑ ' if c.get('show_disk') else '☐ ')+t('disk'), command=lambda: self._toggle_metric('show_disk'))
        if self._has_batt:
            met.add_command(label=('☑ ' if c.get('show_batt') else '☐ ')+t('batt'), command=lambda: self._toggle_metric('show_batt'))
        cascade('metrics', t('metrics'), met)

        # Details (extra readouts)
        det = self._submenu(m)
        det.add_command(label=('☑ ' if c.get('cpu_freq') else '☐ ')+t('cpu_freq'),
                        command=lambda: self._toggle_detail('cpu_freq'))
        det.add_command(label=('☑ ' if c.get('ram_gb') else '☐ ')+t('ram_gb'),
                        command=lambda: self._toggle_detail('ram_gb'))
        cascade('metrics', t('details'), det)

        # Layout (orientation + stacked)
        lay = self._submenu(m)
        for key in ('horizontal','vertical'):
            lay.add_command(label=('● ' if c.get('orientation','horizontal')==key else '○ ')+t(key),
                            command=lambda k=key: self._set_orientation(k))
        lay.add_separator()
        lay.add_command(label=('☑ ' if c.get('stacked',True) else '☐ ')+t('stacked'),
                        command=lambda: self._toggle_detail('stacked'))
        cascade('position', t('layout'), lay)

        # Size
        sz = self._submenu(m)
        for key in ('small','normal','large'):
            sz.add_command(label=('● ' if c['font_scale']==key else '○ ')+t(key),
                           command=lambda k=key: self._set_scale(k))
        cascade('size', t('size'), sz)

        # Opacity
        op = self._submenu(m)
        for v, lab in ((0.5,'50%'),(0.7,'70%'),(0.85,'85%'),(1.0,'100%')):
            op.add_command(label=('● ' if abs(c['opacity']-v)<0.01 else '○ ')+lab,
                           command=lambda vv=v: self._set_opacity(vv))
        cascade('opacity', t('opacity'), op)

        # Refresh interval
        iv = self._submenu(m)
        for v, lab in ((500,'0.5s'),(1000,'1s'),(2000,'2s'),(5000,'5s')):
            iv.add_command(label=('● ' if c['interval']==v else '○ ')+lab,
                           command=lambda vv=v: self._set_interval(vv))
        cascade('clock', t('refresh'), iv)

        # Network unit
        nu = self._submenu(m)
        nu.add_command(label=('● ' if c['net_unit']=='bytes' else '○ ')+t('net_bytes'),
                       command=lambda: self._set_net_unit('bytes'))
        nu.add_command(label=('● ' if c['net_unit']=='bits' else '○ ')+t('net_bits'),
                       command=lambda: self._set_net_unit('bits'))
        cascade('globe', t('netunit'), nu)

        # Theme
        thm = self._submenu(m)
        for name in THEMES:
            thm.add_command(label=('● ' if c.get('theme','default')==name else '○ ')+name.capitalize(),
                            command=lambda nn=name: self._set_theme(nn))
        cascade('size', t('theme'), thm)

        # Language
        lng = self._submenu(m)
        for code in LANGS:
            lng.add_command(label=('● ' if self.lang==code else '○ ')+LANG_NAMES[code],
                            command=lambda cc=code: self._set_language(cc))
        cascade('language', t('language'), lng)

        m.add_separator()
        sp = ('☑ ' if c.get('sparklines') else '☐ ') + t('sparklines')
        m.add_command(label='  '+sp, image=ic.get('metrics'),
                      compound='left', command=self._toggle_sparklines)
        tb = ('☑ ' if c.get('transparent_bg') else '☐ ') + TRANSP_LABEL.get(self.lang, TRANSP_LABEL['en'])
        m.add_command(label='  '+tb, image=ic.get('opacity'),
                      compound='left', command=self._toggle_transparent)
        otb = ('☑ ' if c.get('on_taskbar') else '☐ ') + ONTASKBAR_LABEL.get(self.lang, ONTASKBAR_LABEL['en'])
        m.add_command(label='  '+otb, image=ic.get('position'),
                      compound='left', command=self._toggle_on_taskbar)
        item('refresh', t('reposition'), self._act_reposition)
        ft = ('☑ ' if c['follow_taskbar'] else '☐ ') + t('fullscreen')
        m.add_command(label='  '+ft, image=ic.get('fullscreen'),
                      compound='left', command=self._toggle_follow)
        st = ('☑ ' if is_startup_enabled() else '☐ ') + t('startup')
        m.add_command(label='  '+st, image=ic.get('power'),
                      compound='left', command=self._toggle_startup)
        m.add_separator()
        m.add_command(label='  💜  ' + DONATE_LABEL.get(self.lang, DONATE_LABEL['en']),
                      image=ic.get('heart'), compound='left',
                      command=lambda: self.root.after(1, self._show_donate))
        m.add_command(label=f'  {APP_NAME} v{VERSION}', image=ic.get('info'),
                      compound='left', state='disabled')
        item('close', t('close'), self.root.destroy)
        # The widget is an unfocused utility window — without forcing focus,
        # the popup menu won't appear. Force focus, then release the grab.
        try:
            self.root.focus_force()
        except Exception:
            pass
        try:
            m.tk_popup(px, py)
        finally:
            m.grab_release()
        # The menu has now fully closed (tk_popup returned). It is safe to
        # rebuild the UI here — doing it inside the menu callback crashes Tk.
        self.root.after(1, self._process_pending)

    def _process_pending(self):
        if getattr(self, '_pending_rebuild', False):
            self._pending_rebuild = False
            self._rebuild()

    def _set_language(self, code):
        self.lang = code
        self._set('language', code)

    def _set_net_unit(self, v):
        self._set('net_unit', v)

    def _toggle_follow(self):
        self._set('follow_taskbar', not self.cfg['follow_taskbar'])

    def _toggle_on_taskbar(self):
        """Switch between sitting ON the taskbar and floating just above it."""
        self.cfg['on_taskbar'] = not self.cfg.get('on_taskbar')
        # snap to the clean default position for the chosen mode
        self.cfg['free_pos'] = False
        save_config(self.cfg)
        self._position()

    def _show_donate(self):
        """A small donation card with PayPal & Revolut buttons."""
        try:
            self._donate_impl()
        except Exception:
            pass

    def _donate_impl(self):
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes('-topmost', True)
        win.configure(bg='#161b22', highlightbackground='#30363d', highlightthickness=1)

        tk.Label(win, text='💜  ' + DONATE_LABEL.get(self.lang, DONATE_LABEL['en']),
                 fg='#ffffff', bg='#161b22', font=('Segoe UI', 13, 'bold'),
                 padx=20).pack(pady=(14, 4))
        tk.Label(win, text=DONATE_MSG.get(self.lang, DONATE_MSG['en']),
                 fg='#c9d1d9', bg='#161b22', font=('Segoe UI', 10),
                 justify='center', padx=20).pack(pady=(0, 12))

        btns = tk.Frame(win, bg='#161b22'); btns.pack(padx=20, pady=(0, 8))

        def open_link(url):
            try: webbrowser.open(url)
            except Exception: pass

        def mkbtn(parent, text, bg, url):
            b = tk.Label(parent, text=text, fg='white', bg=bg,
                         font=('Segoe UI', 10, 'bold'), padx=18, pady=8,
                         cursor='hand2')
            b.pack(side='left', padx=6)
            b.bind('<Button-1>', lambda e: open_link(url))
            # subtle hover
            b.bind('<Enter>', lambda e: b.config(bg=bg))
            return b

        mkbtn(btns, 'PayPal',  '#0070ba', DONATE_PAYPAL)
        mkbtn(btns, 'Revolut', '#000000', DONATE_REVOLUT)

        close = tk.Label(win, text='✕', fg='#8b949e', bg='#161b22',
                         font=('Segoe UI', 11, 'bold'), cursor='hand2')
        close.place(relx=1.0, x=-10, y=8, anchor='ne')
        close.bind('<Button-1>', lambda e: win.destroy())

        win.update_idletasks()
        # centre the card above the widget
        ww = win.winfo_reqwidth(); wh = win.winfo_reqheight()
        sx = self.root.winfo_x()
        x = max(8, sx)
        y = max(8, self.root.winfo_y() - wh - 8)
        win.geometry(f'+{x}+{y}')
        win.bind('<Escape>', lambda e: win.destroy())

    def _toast(self, msg, ms=2200):
        """Small popup bubble shown just above the widget."""
        win = tk.Toplevel(self.root); win.overrideredirect(True)
        win.attributes('-topmost', True); win.configure(bg='#161b22')
        tk.Label(win, text=msg, fg='white', bg='#161b22',
                 font=('Segoe UI', 10), padx=16, pady=10).pack()
        win.update_idletasks()
        win.geometry(f'+{self.root.winfo_x()}+{max(0, self.root.winfo_y()-44)}')
        win.after(ms, win.destroy)

    def _toggle_startup(self):
        enable = not is_startup_enabled()
        set_startup(enable)
        self._toast(self.t('toast_on') if enable else self.t('toast_off'))

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    if already_running():
        sys.exit(0)   # another copy is already on the taskbar
    sync_startup()    # keep auto-start path correct even if the .exe was moved
    Widget().run()
