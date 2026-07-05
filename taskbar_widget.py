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
import socket
import random

APP_NAME = 'PulseDeck'       # internal identity: config dir, mutex, registry, Store package
DISPLAY_NAME = 'PulseDeck'   # user-visible product name (rebrand)
VERSION  = '2.9.3'

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
# ── earthquakes (v2.6) ──
QUAKES_LABEL = {
 'en':'Earthquakes','el':'Σεισμοί','es':'Terremotos','de':'Erdbeben',
 'fr':'Tremblements de terre','it':'Terremoti','pt':'Terramotos','ru':'Землетрясения',
}
QUAKES_FELT_LABEL = {
 'en':'Felt level','el':'Επίπεδο αίσθησης','es':'Nivel de percepción',
 'de':'Spürbarkeit','fr':'Niveau perçu','it':'Livello percepito',
 'pt':'Nível percetível','ru':'Уровень восприятия',
}
QUAKES_LEVELS = {  # MMI thresholds shown in the menu
 'en':[('Subtle (felt indoors)',3.0),('Noticeable (widely felt)',4.0),
       ('Strong (objects move)',5.0),('Severe (damage)',6.0)],
 'el':[('Διακριτικό (μέσα σε σπίτι)',3.0),('Αισθητό (ευρέως)',4.0),
       ('Δυνατό (κουνιούνται αντικείμενα)',5.0),('Έντονο (ζημιές)',6.0)],
 'es':[('Sutil (en interior)',3.0),('Notable (ampliamente sentido)',4.0),
       ('Fuerte (mueve objetos)',5.0),('Severo (daños)',6.0)],
 'de':[('Subtil (innen spürbar)',3.0),('Spürbar (weithin)',4.0),
       ('Stark (Objekte bewegen sich)',5.0),('Schwer (Schäden)',6.0)],
 'fr':[('Subtil (à l\'intérieur)',3.0),('Notable (largement ressenti)',4.0),
       ('Fort (objets bougent)',5.0),('Sévère (dégâts)',6.0)],
 'it':[('Sottile (al chiuso)',3.0),('Notevole (ampiamente)',4.0),
       ('Forte (oggetti si muovono)',5.0),('Severo (danni)',6.0)],
 'pt':[('Subtil (no interior)',3.0),('Notável (amplamente sentido)',4.0),
       ('Forte (objetos movem-se)',5.0),('Severo (danos)',6.0)],
 'ru':[('Слабое (в помещении)',3.0),('Заметное (повсеместно)',4.0),
       ('Сильное (предметы двигаются)',5.0),('Тяжелое (разрушения)',6.0)],
}
QUAKES_TOAST_LABEL = {
 'en':'Toast notifications','el':'Ειδοποιήσεις (toast)','es':'Notificaciones',
 'de':'Toast-Benachrichtigungen','fr':'Notifications toast',
 'it':'Notifiche toast','pt':'Notificações toast','ru':'Уведомления',
}
QUAKES_MUTE_LABEL = {
 'en':'Mute all','el':'Σίγαση όλων','es':'Silenciar todo','de':'Alles stumm',
 'fr':'Tout couper','it':'Silenzia tutto','pt':'Silenciar tudo','ru':'Отключить все',
}
QUAKES_RECENT_LABEL = {
 'en':'Recent events…','el':'Πρόσφατα συμβάντα…','es':'Eventos recientes…',
 'de':'Letzte Ereignisse…','fr':'Événements récents…','it':'Eventi recenti…',
 'pt':'Eventos recentes…','ru':'Недавние события…',
}
QUAKES_TOAST_TITLE = {
 'en':'Earthquake felt','el':'Αισθητός σεισμός','es':'Terremoto sentido',
 'de':'Erdbeben gespürt','fr':'Tremblement de terre ressenti',
 'it':'Terremoto avvertito','pt':'Terramoto sentido','ru':'Землетрясение',
}
# ── power consumption (v2.7) ──
POWER_LABEL = {
 'en':'Power','el':'Ισχύς','es':'Potencia','de':'Leistung',
 'fr':'Puissance','it':'Potenza','pt':'Potência','ru':'Мощность',
}
# ── Customize Window labels (v2.6) ──
CUST_LABELS = {
 'en':{'title':'PulseDeck — Customize','general':'General','metrics':'Metrics',
       'appearance':'Appearance','alerts':'Alerts','system':'System','about':'About',
       'superuser':'Superuser',
       'su_sub':'Shortcuts into advanced, normally-hidden Windows panels.',
       'su_god':'God Mode','su_god_d':'Every Control Panel task in one searchable list',
       'su_dev':'Developer Mode','su_dev_d':'Open Settings → For developers (sideloading, terminal…)',
       'su_msconfig':'System Configuration','su_msconfig_d':'msconfig — boot options, services, startup',
       'su_regedit':'Registry Editor','su_regedit_d':'regedit — edit the Windows registry (careful!)',
       'su_gpedit':'Group Policy Editor','su_gpedit_d':'gpedit.msc — local policies (Pro editions)',
       'su_services':'Services','su_services_d':'services.msc — start/stop Windows services',
       'su_startup':'Startup folder','su_startup_d':'shell:startup — apps that launch at sign-in',
       'su_sys32':'System32 folder','su_sys32_d':'Open the Windows System32 directory',
       'reset':'Reset to defaults','apply':'Apply','close':'Close',
       'live_hint':'Click Apply to save',
       'show_hide':'Show & order','drag_hint':'Drag ☰ to reorder',
       'always_last':'Always last (recommended)',
       'manage_drives':'Drives to show','set_city':'Set city',
       'refresh_rate':'Refresh rate','language':'Language',
       'lock_pos':'Lock position','reset_pos':'Reset position',
       'startup':'Start with Windows','check_upd':'Check for updates',
       'theme':'Theme','size':'Size','background':'Background',
       'orientation':'Orientation','stacked':'Two rows (stacked)',
       'sparklines':'Mini graphs','on_taskbar':'Sit on taskbar',
       'tooltips':'Hover details','hide_fs':'Hide when an app goes fullscreen',
       'quakes_on':'Earthquake alerts','sources':'Sources','felt_level':'Felt level',
       'manual_loc':'Manual location','recent_evt':'Recent events',
       'donate':'Donate','github':'View on GitHub','store':'Microsoft Store',
       'website':'Website','version':'Version'},
 'el':{'title':'PulseDeck — Προσαρμογή','general':'Γενικά','metrics':'Ενδείξεις',
       'appearance':'Εμφάνιση','alerts':'Ειδοποιήσεις','system':'Σύστημα','about':'Σχετικά',
       'superuser':'Superuser',
       'su_sub':'Συντομεύσεις σε προχωρημένους, κρυμμένους πίνακες των Windows.',
       'su_god':'God Mode','su_god_d':'Όλες οι εργασίες του Πίνακα Ελέγχου σε μία λίστα',
       'su_dev':'Λειτουργία προγραμματιστή','su_dev_d':'Άνοιγμα Ρυθμίσεις → Για προγραμματιστές',
       'su_msconfig':'Ρύθμιση συστήματος','su_msconfig_d':'msconfig — εκκίνηση, υπηρεσίες, startup',
       'su_regedit':'Επεξεργαστής μητρώου','su_regedit_d':'regedit — επεξεργασία μητρώου (προσοχή!)',
       'su_gpedit':'Πολιτικές ομάδας','su_gpedit_d':'gpedit.msc — τοπικές πολιτικές (εκδόσεις Pro)',
       'su_services':'Υπηρεσίες','su_services_d':'services.msc — έναρξη/διακοπή υπηρεσιών',
       'su_startup':'Φάκελος εκκίνησης','su_startup_d':'shell:startup — εφαρμογές που ξεκινούν στην είσοδο',
       'su_sys32':'Φάκελος System32','su_sys32_d':'Άνοιγμα του φακέλου System32 των Windows',
       'reset':'Επαναφορά προεπιλογών','apply':'Εφαρμογή','close':'Κλείσιμο',
       'live_hint':'Πάτα Εφαρμογή για αποθήκευση',
       'show_hide':'Εμφάνιση & σειρά','drag_hint':'Σύρε το ☰ για αλλαγή σειράς',
       'always_last':'Πάντα τελευταίο (συνιστάται)',
       'manage_drives':'Δίσκοι','set_city':'Ορισμός πόλης',
       'refresh_rate':'Ανανέωση','language':'Γλώσσα',
       'lock_pos':'Κλείδωμα θέσης','reset_pos':'Επαναφορά θέσης',
       'startup':'Εκκίνηση με Windows','check_upd':'Έλεγχος ενημερώσεων',
       'theme':'Θέμα','size':'Μέγεθος','background':'Φόντο',
       'orientation':'Διάταξη','stacked':'Δύο σειρές',
       'sparklines':'Mini γραφήματα','on_taskbar':'Πάνω στη μπάρα',
       'tooltips':'Λεπτομέρειες (hover)','hide_fs':'Κρύψιμο όταν κάτι είναι σε πλήρη οθόνη',
       'quakes_on':'Ειδοποιήσεις σεισμών','sources':'Πηγές','felt_level':'Επίπεδο αίσθησης',
       'manual_loc':'Χειροκίνητη τοποθεσία','recent_evt':'Πρόσφατα συμβάντα',
       'donate':'Δωρεά','github':'Στο GitHub','store':'Microsoft Store',
       'website':'Ιστότοπος','version':'Έκδοση'},
 'es':{'title':'PulseDeck — Personalizar','general':'General','metrics':'Métricas',
       'appearance':'Apariencia','alerts':'Alertas','system':'Sistema','about':'Acerca de',
       'superuser':'Superuser',
       'reset':'Restablecer','apply':'Aplicar','close':'Cerrar',
       'live_hint':'Los cambios se aplican en vivo',
       'show_hide':'Mostrar y ordenar','drag_hint':'Arrastrar para reordenar',
       'always_last':'Siempre al final (recomendado)',
       'manage_drives':'Discos','set_city':'Establecer ciudad',
       'refresh_rate':'Frecuencia','language':'Idioma',
       'lock_pos':'Bloquear posición','reset_pos':'Restablecer posición',
       'startup':'Iniciar con Windows','check_upd':'Buscar actualizaciones',
       'theme':'Tema','size':'Tamaño','background':'Fondo',
       'orientation':'Orientación','stacked':'Dos filas',
       'sparklines':'Mini gráficos','on_taskbar':'En la barra',
       'tooltips':'Detalles al pasar',
       'quakes_on':'Alertas sísmicas','sources':'Fuentes','felt_level':'Nivel percibido',
       'manual_loc':'Ubicación manual','recent_evt':'Eventos recientes',
       'donate':'Donar','github':'Ver en GitHub','store':'Microsoft Store',
       'website':'Sitio web','version':'Versión'},
 'de':{'title':'PulseDeck — Anpassen','general':'Allgemein','metrics':'Werte',
       'appearance':'Aussehen','alerts':'Warnungen','system':'System','about':'Info',
       'superuser':'Superuser',
       'reset':'Standard wiederherstellen','apply':'Übernehmen','close':'Schließen',
       'live_hint':'Änderungen werden live übernommen',
       'show_hide':'Anzeigen & ordnen','drag_hint':'Ziehen zum Neuordnen',
       'always_last':'Immer zuletzt (empfohlen)',
       'manage_drives':'Laufwerke','set_city':'Stadt festlegen',
       'refresh_rate':'Aktualisierung','language':'Sprache',
       'lock_pos':'Position sperren','reset_pos':'Position zurücksetzen',
       'startup':'Mit Windows starten','check_upd':'Nach Updates suchen',
       'theme':'Design','size':'Größe','background':'Hintergrund',
       'orientation':'Ausrichtung','stacked':'Zwei Zeilen',
       'sparklines':'Mini-Diagramme','on_taskbar':'Auf Taskleiste',
       'tooltips':'Hover-Details',
       'quakes_on':'Erdbeben-Warnungen','sources':'Quellen','felt_level':'Spürbarkeit',
       'manual_loc':'Manueller Standort','recent_evt':'Letzte Ereignisse',
       'donate':'Spenden','github':'Auf GitHub','store':'Microsoft Store',
       'website':'Website','version':'Version'},
 'fr':{'title':'PulseDeck — Personnaliser','general':'Général','metrics':'Mesures',
       'appearance':'Apparence','alerts':'Alertes','system':'Système','about':'À propos',
       'superuser':'Superuser',
       'reset':'Réinitialiser','apply':'Appliquer','close':'Fermer',
       'live_hint':'Modifications appliquées en direct',
       'show_hide':'Afficher & ordonner','drag_hint':'Glisser pour réorganiser',
       'always_last':'Toujours en dernier (recommandé)',
       'manage_drives':'Disques','set_city':'Définir la ville',
       'refresh_rate':'Rafraîchissement','language':'Langue',
       'lock_pos':'Verrouiller la position','reset_pos':'Réinitialiser la position',
       'startup':'Démarrer avec Windows','check_upd':'Rechercher des MAJ',
       'theme':'Thème','size':'Taille','background':'Arrière-plan',
       'orientation':'Orientation','stacked':'Deux lignes',
       'sparklines':'Mini graphiques','on_taskbar':'Sur la barre',
       'tooltips':'Détails au survol',
       'quakes_on':'Alertes sismiques','sources':'Sources','felt_level':'Niveau perçu',
       'manual_loc':'Emplacement manuel','recent_evt':'Événements récents',
       'donate':'Faire un don','github':'Sur GitHub','store':'Microsoft Store',
       'website':'Site web','version':'Version'},
 'it':{'title':'PulseDeck — Personalizza','general':'Generale','metrics':'Misure',
       'appearance':'Aspetto','alerts':'Avvisi','system':'Sistema','about':'Info',
       'superuser':'Superuser',
       'reset':'Ripristina','apply':'Applica','close':'Chiudi',
       'live_hint':'Le modifiche si applicano in tempo reale',
       'show_hide':'Mostra e ordina','drag_hint':'Trascina per riordinare',
       'always_last':'Sempre per ultimo (consigliato)',
       'manage_drives':'Dischi','set_city':'Imposta città',
       'refresh_rate':'Aggiornamento','language':'Lingua',
       'lock_pos':'Blocca posizione','reset_pos':'Reimposta posizione',
       'startup':'Avvia con Windows','check_upd':'Cerca aggiornamenti',
       'theme':'Tema','size':'Dimensione','background':'Sfondo',
       'orientation':'Orientamento','stacked':'Due righe',
       'sparklines':'Mini grafici','on_taskbar':'Sulla barra',
       'tooltips':'Dettagli al passaggio',
       'quakes_on':'Avvisi sismici','sources':'Fonti','felt_level':'Livello percepito',
       'manual_loc':'Posizione manuale','recent_evt':'Eventi recenti',
       'donate':'Dona','github':'Su GitHub','store':'Microsoft Store',
       'website':'Sito web','version':'Versione'},
 'pt':{'title':'PulseDeck — Personalizar','general':'Geral','metrics':'Métricas',
       'appearance':'Aparência','alerts':'Alertas','system':'Sistema','about':'Sobre',
       'superuser':'Superuser',
       'reset':'Repor padrões','apply':'Aplicar','close':'Fechar',
       'live_hint':'Alterações aplicadas em tempo real',
       'show_hide':'Mostrar e ordenar','drag_hint':'Arrastar para reordenar',
       'always_last':'Sempre por último (recomendado)',
       'manage_drives':'Discos','set_city':'Definir cidade',
       'refresh_rate':'Atualização','language':'Idioma',
       'lock_pos':'Bloquear posição','reset_pos':'Repor posição',
       'startup':'Iniciar com o Windows','check_upd':'Procurar atualizações',
       'theme':'Tema','size':'Tamanho','background':'Fundo',
       'orientation':'Orientação','stacked':'Duas linhas',
       'sparklines':'Mini gráficos','on_taskbar':'Na barra',
       'tooltips':'Detalhes ao passar',
       'quakes_on':'Alertas sísmicos','sources':'Fontes','felt_level':'Nível percetível',
       'manual_loc':'Localização manual','recent_evt':'Eventos recentes',
       'donate':'Doar','github':'No GitHub','store':'Microsoft Store',
       'website':'Site','version':'Versão'},
 'ru':{'title':'PulseDeck — Настройка','general':'Общие','metrics':'Метрики',
       'appearance':'Внешний вид','alerts':'Уведомления','system':'Система','about':'О программе',
       'superuser':'Superuser',
       'reset':'Сбросить','apply':'Применить','close':'Закрыть',
       'live_hint':'Изменения применяются мгновенно',
       'show_hide':'Показать и упорядочить','drag_hint':'Перетащите для переупорядочивания',
       'always_last':'Всегда в конце (рекомендуется)',
       'manage_drives':'Диски','set_city':'Указать город',
       'refresh_rate':'Обновление','language':'Язык',
       'lock_pos':'Заблокировать позицию','reset_pos':'Сбросить позицию',
       'startup':'Запуск с Windows','check_upd':'Проверять обновления',
       'theme':'Тема','size':'Размер','background':'Фон',
       'orientation':'Ориентация','stacked':'Две строки',
       'sparklines':'Мини-графики','on_taskbar':'На панели',
       'tooltips':'Подсказки при наведении',
       'quakes_on':'Уведомления о землетрясениях','sources':'Источники','felt_level':'Уровень восприятия',
       'manual_loc':'Местоположение вручную','recent_evt':'Недавние события',
       'donate':'Поддержать','github':'На GitHub','store':'Microsoft Store',
       'website':'Сайт','version':'Версия'},
}
# v2.7 additions — merged into CUST_LABELS below to keep the blocks above tidy.
CUST_EXTRA = {
 'en':{'single_row':'Single row shows','row_percent':'Percent','row_detail':'Details (GHz/GB)',
       'loading_sys':'Loading system information…',
       'felt_near':'Recent felt events near you','no_felt':'No felt events recently.',
       'sys_mobo':'Motherboard','sys_monitor':'Monitor','sys_audio':'Audio',
       'sys_optical':'Optical drive','sys_storage':'Storage','sys_network':'Network',
       'sys_machine':'System','sys_battery':'Battery','sys_drives':'Drives',
       'sys_security':'Security','sys_summary':'Summary','sys_advanced':'Advanced',
       'sys_windows':'Windows','sys_ram':'RAM','copy_all':'Copy all','copied':'Copied!',
       'paypal':'PayPal','revolut':'Revolut','quake_dist':'Alert radius (km)',
       'quake_dur':'Alert duration (min)'},
 'el':{'single_row':'Η μονή σειρά δείχνει','row_percent':'Ποσοστό','row_detail':'Λεπτομέρεια (GHz/GB)',
       'loading_sys':'Φόρτωση πληροφοριών συστήματος…',
       'felt_near':'Πρόσφατα αισθητά συμβάντα κοντά σου','no_felt':'Κανένα αισθητό συμβάν πρόσφατα.',
       'sys_mobo':'Μητρική','sys_monitor':'Οθόνη','sys_audio':'Ήχος',
       'sys_optical':'Οπτικός δίσκος','sys_storage':'Αποθήκευση','sys_network':'Δίκτυο',
       'sys_machine':'Σύστημα','sys_battery':'Μπαταρία','sys_drives':'Δίσκοι',
       'sys_security':'Ασφάλεια','sys_summary':'Σύνοψη','sys_advanced':'Προχωρημένα',
       'sys_windows':'Windows','sys_ram':'RAM','copy_all':'Αντιγραφή όλων','copied':'Αντιγράφηκε!',
       'paypal':'PayPal','revolut':'Revolut','quake_dist':'Ακτίνα ειδοποίησης (km)',
       'quake_dur':'Διάρκεια ειδοποίησης (λεπτά)'},
 'es':{'single_row':'La fila única muestra','row_percent':'Porcentaje','row_detail':'Detalles (GHz/GB)',
       'loading_sys':'Cargando información del sistema…',
       'felt_near':'Eventos sentidos cerca de ti','no_felt':'No hay eventos sentidos recientemente.',
       'sys_mobo':'Placa base','sys_monitor':'Monitor','sys_audio':'Audio',
       'sys_optical':'Unidad óptica','sys_storage':'Almacenamiento','sys_network':'Red',
       'sys_windows':'Windows','sys_ram':'RAM','copy_all':'Copiar todo','copied':'¡Copiado!',
       'paypal':'PayPal','revolut':'Revolut','quake_dist':'Radio de alerta (km)',
       'quake_dur':'Duración de alerta (min)'},
 'de':{'single_row':'Einzelne Zeile zeigt','row_percent':'Prozent','row_detail':'Details (GHz/GB)',
       'loading_sys':'Systeminformationen werden geladen…',
       'felt_near':'Spürbare Ereignisse in der Nähe','no_felt':'Keine spürbaren Ereignisse kürzlich.',
       'sys_mobo':'Hauptplatine','sys_monitor':'Monitor','sys_audio':'Audio',
       'sys_optical':'Optisches Laufwerk','sys_storage':'Speicher','sys_network':'Netzwerk',
       'sys_windows':'Windows','sys_ram':'RAM','copy_all':'Alles kopieren','copied':'Kopiert!',
       'paypal':'PayPal','revolut':'Revolut','quake_dist':'Warnradius (km)',
       'quake_dur':'Warndauer (Min.)'},
 'fr':{'single_row':'La ligne unique affiche','row_percent':'Pourcentage','row_detail':'Détails (GHz/Go)',
       'loading_sys':'Chargement des informations système…',
       'felt_near':'Événements ressentis près de vous','no_felt':'Aucun événement ressenti récemment.',
       'sys_mobo':'Carte mère','sys_monitor':'Écran','sys_audio':'Audio',
       'sys_optical':'Lecteur optique','sys_storage':'Stockage','sys_network':'Réseau',
       'sys_windows':'Windows','sys_ram':'RAM','copy_all':'Tout copier','copied':'Copié !',
       'paypal':'PayPal','revolut':'Revolut','quake_dist':'Rayon d’alerte (km)',
       'quake_dur':'Durée d’alerte (min)'},
 'it':{'single_row':'La riga singola mostra','row_percent':'Percentuale','row_detail':'Dettagli (GHz/GB)',
       'loading_sys':'Caricamento informazioni di sistema…',
       'felt_near':'Eventi percepiti vicino a te','no_felt':'Nessun evento percepito di recente.',
       'sys_mobo':'Scheda madre','sys_monitor':'Monitor','sys_audio':'Audio',
       'sys_optical':'Unità ottica','sys_storage':'Archiviazione','sys_network':'Rete',
       'sys_windows':'Windows','sys_ram':'RAM','copy_all':'Copia tutto','copied':'Copiato!',
       'paypal':'PayPal','revolut':'Revolut','quake_dist':'Raggio di avviso (km)',
       'quake_dur':'Durata avviso (min)'},
 'pt':{'single_row':'A linha única mostra','row_percent':'Percentagem','row_detail':'Detalhes (GHz/GB)',
       'loading_sys':'A carregar informações do sistema…',
       'felt_near':'Eventos sentidos perto de si','no_felt':'Nenhum evento sentido recentemente.',
       'sys_mobo':'Placa-mãe','sys_monitor':'Monitor','sys_audio':'Áudio',
       'sys_optical':'Unidade ótica','sys_storage':'Armazenamento','sys_network':'Rede',
       'sys_windows':'Windows','sys_ram':'RAM','copy_all':'Copiar tudo','copied':'Copiado!',
       'paypal':'PayPal','revolut':'Revolut','quake_dist':'Raio de alerta (km)',
       'quake_dur':'Duração do alerta (min)'},
 'ru':{'single_row':'Одна строка показывает','row_percent':'Процент','row_detail':'Детали (ГГц/ГБ)',
       'loading_sys':'Загрузка сведений о системе…',
       'felt_near':'Недавние ощутимые события рядом','no_felt':'Недавно ощутимых событий нет.',
       'sys_mobo':'Материнская плата','sys_monitor':'Монитор','sys_audio':'Звук',
       'sys_optical':'Оптический привод','sys_storage':'Хранилище','sys_network':'Сеть',
       'sys_windows':'Windows','sys_ram':'ОЗУ','copy_all':'Копировать всё','copied':'Скопировано!',
       'paypal':'PayPal','revolut':'Revolut','quake_dist':'Радиус оповещения (км)',
       'quake_dur':'Длительность оповещения (мин)'},
}
for _lng, _d in CUST_EXTRA.items():
    CUST_LABELS.setdefault(_lng, {}).update(_d)

# ── Bottleneck / live-performance labels (v2.8) ────────────────────────
# Component names (CPU/GPU/RAM/VRAM/Disk) stay as universal tech terms;
# only the surrounding phrases are localized.
BN_EXTRA = {
 'en':{'sys_perf':'Performance (live)','bn_label':'Limiting factor',
       'bn_idle':'Idle — system not under load',
       'bn_none':'Balanced — all components have headroom',
       'bn_cpu':'CPU-bound','bn_gpu':'GPU-bound','bn_ram':'RAM near full',
       'bn_vram':'VRAM near full','bn_disk':'Disk-bound (I/O)'},
 'el':{'sys_perf':'Επιδόσεις (ζωντανά)','bn_label':'Περιοριστικός παράγοντας',
       'bn_idle':'Σε αδράνεια — χωρίς φόρτο',
       'bn_none':'Ισορροπημένο — όλα έχουν περιθώριο',
       'bn_cpu':'Όριο CPU','bn_gpu':'Όριο GPU','bn_ram':'RAM σχεδόν πλήρης',
       'bn_vram':'VRAM σχεδόν πλήρης','bn_disk':'Όριο δίσκου (I/O)'},
 'es':{'sys_perf':'Rendimiento (en vivo)','bn_label':'Factor limitante',
       'bn_idle':'Inactivo — sin carga',
       'bn_none':'Equilibrado — todo tiene margen',
       'bn_cpu':'Límite de CPU','bn_gpu':'Límite de GPU','bn_ram':'RAM casi llena',
       'bn_vram':'VRAM casi llena','bn_disk':'Límite de disco (E/S)'},
 'de':{'sys_perf':'Leistung (live)','bn_label':'Begrenzender Faktor',
       'bn_idle':'Leerlauf — keine Last',
       'bn_none':'Ausgewogen — alle haben Reserven',
       'bn_cpu':'CPU-limitiert','bn_gpu':'GPU-limitiert','bn_ram':'RAM fast voll',
       'bn_vram':'VRAM fast voll','bn_disk':'Datenträger-limitiert (E/A)'},
 'fr':{'sys_perf':'Performances (en direct)','bn_label':'Facteur limitant',
       'bn_idle':'Inactif — aucune charge',
       'bn_none':'Équilibré — tout a de la marge',
       'bn_cpu':'Limité par le CPU','bn_gpu':'Limité par le GPU','bn_ram':'RAM presque pleine',
       'bn_vram':'VRAM presque pleine','bn_disk':'Limité par le disque (E/S)'},
 'it':{'sys_perf':'Prestazioni (live)','bn_label':'Fattore limitante',
       'bn_idle':'Inattivo — nessun carico',
       'bn_none':'Bilanciato — tutto ha margine',
       'bn_cpu':'Limite CPU','bn_gpu':'Limite GPU','bn_ram':'RAM quasi piena',
       'bn_vram':'VRAM quasi piena','bn_disk':'Limite disco (I/O)'},
 'pt':{'sys_perf':'Desempenho (ao vivo)','bn_label':'Fator limitante',
       'bn_idle':'Inativo — sem carga',
       'bn_none':'Equilibrado — tudo com margem',
       'bn_cpu':'Limite de CPU','bn_gpu':'Limite de GPU','bn_ram':'RAM quase cheia',
       'bn_vram':'VRAM quase cheia','bn_disk':'Limite de disco (E/S)'},
 'ru':{'sys_perf':'Производительность (вживую)','bn_label':'Ограничивающий фактор',
       'bn_idle':'Простой — нет нагрузки',
       'bn_none':'Сбалансировано — есть запас',
       'bn_cpu':'Упор в CPU','bn_gpu':'Упор в GPU','bn_ram':'ОЗУ почти заполнена',
       'bn_vram':'VRAM почти заполнена','bn_disk':'Упор в диск (I/O)'},
}
for _lng, _d in BN_EXTRA.items():
    CUST_LABELS.setdefault(_lng, {}).update(_d)

# ── Tools tab labels (v2.8) ────────────────────────────────────────────
TOOL_I18N = {
 'en':{'tools':'Tools','tools_sub':'Shortcuts to built-in Windows tools',
       'cat_cleanup':'Cleanup & Storage','cat_diag':'Diagnostics & Health',
       'cat_perf':'Performance & Power','cat_net':'Network','cat_sys':'System & Security',
       't_diskcleanup':'Disk Cleanup','t_storage':'Storage settings','t_optimize':'Optimize drives',
       't_apps':'Apps & uninstall','t_tempfolder':'Open Temp folder','t_cleartemp':'Clear Temp files',
       't_recyclebin':'Empty Recycle Bin','t_ramcheck':'Memory check (RAM)','t_taskmgr':'Task Manager',
       't_resmon':'Resource Monitor','t_msinfo':'System Information','t_reliability':'Reliability Monitor',
       't_dxdiag':'DirectX Diagnostics','t_power':'Power options','t_startup':'Startup apps',
       't_visualfx':'Visual effects','t_graphics':'Graphics settings','t_netstatus':'Network status',
       't_adapters':'Network adapters','t_flushdns':'Flush DNS cache','t_update':'Windows Update',
       't_security':'Windows Security','t_restore':'System Restore','t_devmgr':'Device Manager',
       'cf_yes':'Yes','cf_no':'Cancel',
       'cf_temp':'Delete temporary files? In-use files are skipped.',
       'cf_bin':'Empty the Recycle Bin? Its contents are permanently deleted.',
       'tt_dns':'DNS cache flushed ✓','tt_temp':'Temp cleared — {n} freed ✓',
       'tt_bin':'Recycle Bin emptied ✓','tt_open':'Opening…'},
 'el':{'tools':'Εργαλεία','tools_sub':'Συντομεύσεις σε ενσωματωμένα εργαλεία των Windows',
       'cat_cleanup':'Καθαρισμός & Χώρος','cat_diag':'Διαγνωστικά & Υγεία',
       'cat_perf':'Επιδόσεις & Ισχύς','cat_net':'Δίκτυο','cat_sys':'Σύστημα & Ασφάλεια',
       't_diskcleanup':'Καθαρισμός δίσκου','t_storage':'Ρυθμίσεις αποθήκευσης','t_optimize':'Βελτιστοποίηση δίσκων',
       't_apps':'Εφαρμογές & απεγκατάσταση','t_tempfolder':'Άνοιγμα φακέλου Temp','t_cleartemp':'Καθαρισμός Temp',
       't_recyclebin':'Άδειασμα Κάδου','t_ramcheck':'Έλεγχος μνήμης (RAM)','t_taskmgr':'Διαχείριση εργασιών',
       't_resmon':'Παρακολούθηση πόρων','t_msinfo':'Πληροφορίες συστήματος','t_reliability':'Παρακολούθηση αξιοπιστίας',
       't_dxdiag':'Διαγνωστικά DirectX','t_power':'Επιλογές ενέργειας','t_startup':'Εφαρμογές εκκίνησης',
       't_visualfx':'Οπτικά εφέ','t_graphics':'Ρυθμίσεις γραφικών','t_netstatus':'Κατάσταση δικτύου',
       't_adapters':'Προσαρμογείς δικτύου','t_flushdns':'Καθαρισμός DNS','t_update':'Windows Update',
       't_security':'Ασφάλεια των Windows','t_restore':'Επαναφορά συστήματος','t_devmgr':'Διαχείριση συσκευών',
       'cf_yes':'Ναι','cf_no':'Άκυρο',
       'cf_temp':'Διαγραφή προσωρινών αρχείων; Τα αρχεία σε χρήση παραλείπονται.',
       'cf_bin':'Άδειασμα του Κάδου Ανακύκλωσης; Τα περιεχόμενα διαγράφονται οριστικά.',
       'tt_dns':'Η μνήμη DNS καθαρίστηκε ✓','tt_temp':'Καθαρίστηκαν τα Temp — {n} ✓',
       'tt_bin':'Ο Κάδος άδειασε ✓','tt_open':'Άνοιγμα…'},
 'es':{'tools':'Herramientas','tools_sub':'Accesos directos a herramientas de Windows',
       'cat_cleanup':'Limpieza y almacenamiento','cat_diag':'Diagnóstico y estado',
       'cat_perf':'Rendimiento y energía','cat_net':'Red','cat_sys':'Sistema y seguridad',
       't_diskcleanup':'Liberador de espacio','t_storage':'Ajustes de almacenamiento','t_optimize':'Optimizar unidades',
       't_apps':'Aplicaciones y desinstalar','t_tempfolder':'Abrir carpeta Temp','t_cleartemp':'Limpiar archivos Temp',
       't_recyclebin':'Vaciar papelera','t_ramcheck':'Prueba de memoria (RAM)','t_taskmgr':'Administrador de tareas',
       't_resmon':'Monitor de recursos','t_msinfo':'Información del sistema','t_reliability':'Monitor de confiabilidad',
       't_dxdiag':'Diagnóstico DirectX','t_power':'Opciones de energía','t_startup':'Apps de inicio',
       't_visualfx':'Efectos visuales','t_graphics':'Configuración de gráficos','t_netstatus':'Estado de la red',
       't_adapters':'Adaptadores de red','t_flushdns':'Vaciar caché DNS','t_update':'Windows Update',
       't_security':'Seguridad de Windows','t_restore':'Restaurar sistema','t_devmgr':'Administrador de dispositivos',
       'cf_yes':'Sí','cf_no':'Cancelar',
       'cf_temp':'¿Eliminar archivos temporales? Se omiten los archivos en uso.',
       'cf_bin':'¿Vaciar la papelera? Su contenido se elimina permanentemente.',
       'tt_dns':'Caché DNS vaciada ✓','tt_temp':'Temp limpiado — {n} ✓',
       'tt_bin':'Papelera vaciada ✓','tt_open':'Abriendo…'},
 'de':{'tools':'Werkzeuge','tools_sub':'Verknüpfungen zu integrierten Windows-Tools',
       'cat_cleanup':'Bereinigung & Speicher','cat_diag':'Diagnose & Zustand',
       'cat_perf':'Leistung & Energie','cat_net':'Netzwerk','cat_sys':'System & Sicherheit',
       't_diskcleanup':'Datenträgerbereinigung','t_storage':'Speichereinstellungen','t_optimize':'Laufwerke optimieren',
       't_apps':'Apps & Deinstallation','t_tempfolder':'Temp-Ordner öffnen','t_cleartemp':'Temp-Dateien löschen',
       't_recyclebin':'Papierkorb leeren','t_ramcheck':'Speichertest (RAM)','t_taskmgr':'Task-Manager',
       't_resmon':'Ressourcenmonitor','t_msinfo':'Systeminformationen','t_reliability':'Zuverlässigkeitsverlauf',
       't_dxdiag':'DirectX-Diagnose','t_power':'Energieoptionen','t_startup':'Autostart-Apps',
       't_visualfx':'Visuelle Effekte','t_graphics':'Grafikeinstellungen','t_netstatus':'Netzwerkstatus',
       't_adapters':'Netzwerkadapter','t_flushdns':'DNS-Cache leeren','t_update':'Windows Update',
       't_security':'Windows-Sicherheit','t_restore':'Systemwiederherstellung','t_devmgr':'Geräte-Manager',
       'cf_yes':'Ja','cf_no':'Abbrechen',
       'cf_temp':'Temporäre Dateien löschen? Dateien in Verwendung werden übersprungen.',
       'cf_bin':'Papierkorb leeren? Der Inhalt wird endgültig gelöscht.',
       'tt_dns':'DNS-Cache geleert ✓','tt_temp':'Temp geleert — {n} ✓',
       'tt_bin':'Papierkorb geleert ✓','tt_open':'Wird geöffnet…'},
 'fr':{'tools':'Outils','tools_sub':'Raccourcis vers les outils intégrés de Windows',
       'cat_cleanup':'Nettoyage & stockage','cat_diag':'Diagnostic & état',
       'cat_perf':'Performances & alimentation','cat_net':'Réseau','cat_sys':'Système & sécurité',
       't_diskcleanup':'Nettoyage de disque','t_storage':'Paramètres de stockage','t_optimize':'Optimiser les lecteurs',
       't_apps':'Applications & désinstaller','t_tempfolder':'Ouvrir le dossier Temp','t_cleartemp':'Effacer les fichiers Temp',
       't_recyclebin':'Vider la corbeille','t_ramcheck':'Test mémoire (RAM)','t_taskmgr':'Gestionnaire des tâches',
       't_resmon':'Moniteur de ressources','t_msinfo':'Informations système','t_reliability':'Moniteur de fiabilité',
       't_dxdiag':'Diagnostic DirectX','t_power':'Options d’alimentation','t_startup':'Applications de démarrage',
       't_visualfx':'Effets visuels','t_graphics':'Paramètres graphiques','t_netstatus':'État du réseau',
       't_adapters':'Cartes réseau','t_flushdns':'Vider le cache DNS','t_update':'Windows Update',
       't_security':'Sécurité Windows','t_restore':'Restauration du système','t_devmgr':'Gestionnaire de périphériques',
       'cf_yes':'Oui','cf_no':'Annuler',
       'cf_temp':'Supprimer les fichiers temporaires ? Les fichiers en cours d’utilisation sont ignorés.',
       'cf_bin':'Vider la corbeille ? Son contenu est supprimé définitivement.',
       'tt_dns':'Cache DNS vidé ✓','tt_temp':'Temp nettoyé — {n} ✓',
       'tt_bin':'Corbeille vidée ✓','tt_open':'Ouverture…'},
 'it':{'tools':'Strumenti','tools_sub':'Scorciatoie agli strumenti integrati di Windows',
       'cat_cleanup':'Pulizia e archiviazione','cat_diag':'Diagnostica e stato',
       'cat_perf':'Prestazioni e alimentazione','cat_net':'Rete','cat_sys':'Sistema e sicurezza',
       't_diskcleanup':'Pulizia disco','t_storage':'Impostazioni archiviazione','t_optimize':'Ottimizza unità',
       't_apps':'App e disinstalla','t_tempfolder':'Apri cartella Temp','t_cleartemp':'Pulisci file Temp',
       't_recyclebin':'Svuota cestino','t_ramcheck':'Test memoria (RAM)','t_taskmgr':'Gestione attività',
       't_resmon':'Monitor risorse','t_msinfo':'Informazioni di sistema','t_reliability':'Monitor affidabilità',
       't_dxdiag':'Diagnostica DirectX','t_power':'Opzioni risparmio energia','t_startup':'App all’avvio',
       't_visualfx':'Effetti visivi','t_graphics':'Impostazioni grafica','t_netstatus':'Stato della rete',
       't_adapters':'Schede di rete','t_flushdns':'Svuota cache DNS','t_update':'Windows Update',
       't_security':'Sicurezza di Windows','t_restore':'Ripristino configurazione','t_devmgr':'Gestione dispositivi',
       'cf_yes':'Sì','cf_no':'Annulla',
       'cf_temp':'Eliminare i file temporanei? I file in uso vengono ignorati.',
       'cf_bin':'Svuotare il cestino? Il contenuto viene eliminato definitivamente.',
       'tt_dns':'Cache DNS svuotata ✓','tt_temp':'Temp pulito — {n} ✓',
       'tt_bin':'Cestino svuotato ✓','tt_open':'Apertura…'},
 'pt':{'tools':'Ferramentas','tools_sub':'Atalhos para ferramentas integradas do Windows',
       'cat_cleanup':'Limpeza e armazenamento','cat_diag':'Diagnóstico e estado',
       'cat_perf':'Desempenho e energia','cat_net':'Rede','cat_sys':'Sistema e segurança',
       't_diskcleanup':'Limpeza de disco','t_storage':'Definições de armazenamento','t_optimize':'Otimizar unidades',
       't_apps':'Aplicações e desinstalar','t_tempfolder':'Abrir pasta Temp','t_cleartemp':'Limpar ficheiros Temp',
       't_recyclebin':'Esvaziar reciclagem','t_ramcheck':'Teste de memória (RAM)','t_taskmgr':'Gestor de tarefas',
       't_resmon':'Monitor de recursos','t_msinfo':'Informações do sistema','t_reliability':'Monitor de fiabilidade',
       't_dxdiag':'Diagnóstico DirectX','t_power':'Opções de energia','t_startup':'Apps de arranque',
       't_visualfx':'Efeitos visuais','t_graphics':'Definições de gráficos','t_netstatus':'Estado da rede',
       't_adapters':'Placas de rede','t_flushdns':'Limpar cache DNS','t_update':'Windows Update',
       't_security':'Segurança do Windows','t_restore':'Restauro do sistema','t_devmgr':'Gestor de dispositivos',
       'cf_yes':'Sim','cf_no':'Cancelar',
       'cf_temp':'Eliminar ficheiros temporários? Os ficheiros em uso são ignorados.',
       'cf_bin':'Esvaziar a reciclagem? O conteúdo é eliminado permanentemente.',
       'tt_dns':'Cache DNS limpa ✓','tt_temp':'Temp limpo — {n} ✓',
       'tt_bin':'Reciclagem esvaziada ✓','tt_open':'A abrir…'},
 'ru':{'tools':'Инструменты','tools_sub':'Ярлыки к встроенным средствам Windows',
       'cat_cleanup':'Очистка и хранилище','cat_diag':'Диагностика и состояние',
       'cat_perf':'Производительность и питание','cat_net':'Сеть','cat_sys':'Система и безопасность',
       't_diskcleanup':'Очистка диска','t_storage':'Параметры хранилища','t_optimize':'Оптимизация дисков',
       't_apps':'Приложения и удаление','t_tempfolder':'Открыть папку Temp','t_cleartemp':'Очистить файлы Temp',
       't_recyclebin':'Очистить корзину','t_ramcheck':'Проверка памяти (RAM)','t_taskmgr':'Диспетчер задач',
       't_resmon':'Монитор ресурсов','t_msinfo':'Сведения о системе','t_reliability':'Монитор стабильности',
       't_dxdiag':'Средство DirectX','t_power':'Электропитание','t_startup':'Автозагрузка',
       't_visualfx':'Визуальные эффекты','t_graphics':'Параметры графики','t_netstatus':'Состояние сети',
       't_adapters':'Сетевые адаптеры','t_flushdns':'Очистить кэш DNS','t_update':'Центр обновления',
       't_security':'Безопасность Windows','t_restore':'Восстановление системы','t_devmgr':'Диспетчер устройств',
       'cf_yes':'Да','cf_no':'Отмена',
       'cf_temp':'Удалить временные файлы? Используемые файлы пропускаются.',
       'cf_bin':'Очистить корзину? Содержимое удаляется безвозвратно.',
       'tt_dns':'Кэш DNS очищен ✓','tt_temp':'Temp очищен — {n} ✓',
       'tt_bin':'Корзина очищена ✓','tt_open':'Открытие…'},
}
for _lng, _d in TOOL_I18N.items():
    CUST_LABELS.setdefault(_lng, {}).update(_d)

# ── Tools search + Uptime labels (v2.8) ────────────────────────────────
EXTRA_28 = {
 'en':{'tool_search':'Search tools…','no_match':'No matching tools',
       'sys_uptime':'Uptime','sys_booted':'Booted'},
 'el':{'tool_search':'Αναζήτηση εργαλείων…','no_match':'Κανένα εργαλείο',
       'sys_uptime':'Χρόνος λειτουργίας','sys_booted':'Εκκίνηση'},
 'es':{'tool_search':'Buscar herramientas…','no_match':'Sin coincidencias',
       'sys_uptime':'Tiempo activo','sys_booted':'Iniciado'},
 'de':{'tool_search':'Werkzeuge suchen…','no_match':'Keine Treffer',
       'sys_uptime':'Betriebszeit','sys_booted':'Gestartet'},
 'fr':{'tool_search':'Rechercher des outils…','no_match':'Aucun outil',
       'sys_uptime':'Temps de fonctionnement','sys_booted':'Démarré'},
 'it':{'tool_search':'Cerca strumenti…','no_match':'Nessuno strumento',
       'sys_uptime':'Tempo di attività','sys_booted':'Avviato'},
 'pt':{'tool_search':'Procurar ferramentas…','no_match':'Nenhuma ferramenta',
       'sys_uptime':'Tempo ativo','sys_booted':'Iniciado'},
 'ru':{'tool_search':'Поиск инструментов…','no_match':'Ничего не найдено',
       'sys_uptime':'Время работы','sys_booted':'Запуск'},
}
for _lng, _d in EXTRA_28.items():
    CUST_LABELS.setdefault(_lng, {}).update(_d)

# ── Tools layout toggle labels (v2.8) ──────────────────────────────────
LAYOUT_I18N = {
 'en':{'view_list':'List','view_grid':'Tiles'},
 'el':{'view_list':'Λίστα','view_grid':'Πλακίδια'},
 'es':{'view_list':'Lista','view_grid':'Mosaico'},
 'de':{'view_list':'Liste','view_grid':'Kacheln'},
 'fr':{'view_list':'Liste','view_grid':'Tuiles'},
 'it':{'view_list':'Elenco','view_grid':'Riquadri'},
 'pt':{'view_list':'Lista','view_grid':'Mosaicos'},
 'ru':{'view_list':'Список','view_grid':'Плитки'},
}
for _lng, _d in LAYOUT_I18N.items():
    CUST_LABELS.setdefault(_lng, {}).update(_d)

# ── DNS Boost tab labels (v2.8) ────────────────────────────────────────
DNS_I18N = {
 'en':{'dns':'DNS','dns_sub':'Find the fastest DNS for your connection',
       'dns_find':'Find fastest DNS','dns_again':'Test again','dns_testing':'Testing…',
       'dns_best':'Fastest','dns_copy':'Copy','dns_copied':'Copied ✓',
       'dns_opennet':'Open network settings','dns_no_ipv6':'IPv6 not available here',
       'dns_howto':'To change: open network settings → your adapter → DNS, then paste the address.'},
 'el':{'dns':'DNS','dns_sub':'Βρες το γρηγορότερο DNS για τη σύνδεσή σου',
       'dns_find':'Εύρεση γρηγορότερου DNS','dns_again':'Ξανά','dns_testing':'Έλεγχος…',
       'dns_best':'Γρηγορότερο','dns_copy':'Αντιγραφή','dns_copied':'Αντιγράφηκε ✓',
       'dns_opennet':'Άνοιγμα ρυθμίσεων δικτύου','dns_no_ipv6':'Το IPv6 δεν είναι διαθέσιμο',
       'dns_howto':'Για αλλαγή: ρυθμίσεις δικτύου → προσαρμογέας → DNS, και επικόλλησε τη διεύθυνση.'},
 'es':{'dns':'DNS','dns_sub':'Encuentra el DNS más rápido para tu conexión',
       'dns_find':'Buscar DNS más rápido','dns_again':'Repetir','dns_testing':'Probando…',
       'dns_best':'Más rápido','dns_copy':'Copiar','dns_copied':'Copiado ✓',
       'dns_opennet':'Abrir configuración de red','dns_no_ipv6':'IPv6 no disponible',
       'dns_howto':'Para cambiar: configuración de red → adaptador → DNS, y pega la dirección.'},
 'de':{'dns':'DNS','dns_sub':'Finde das schnellste DNS für deine Verbindung',
       'dns_find':'Schnellstes DNS finden','dns_again':'Erneut','dns_testing':'Test läuft…',
       'dns_best':'Schnellstes','dns_copy':'Kopieren','dns_copied':'Kopiert ✓',
       'dns_opennet':'Netzwerkeinstellungen öffnen','dns_no_ipv6':'IPv6 nicht verfügbar',
       'dns_howto':'Zum Ändern: Netzwerkeinstellungen → Adapter → DNS, Adresse einfügen.'},
 'fr':{'dns':'DNS','dns_sub':'Trouvez le DNS le plus rapide pour votre connexion',
       'dns_find':'Trouver le DNS le plus rapide','dns_again':'Relancer','dns_testing':'Test…',
       'dns_best':'Le plus rapide','dns_copy':'Copier','dns_copied':'Copié ✓',
       'dns_opennet':'Ouvrir les paramètres réseau','dns_no_ipv6':'IPv6 indisponible',
       'dns_howto':'Pour changer : paramètres réseau → carte → DNS, puis collez l’adresse.'},
 'it':{'dns':'DNS','dns_sub':'Trova il DNS più veloce per la tua connessione',
       'dns_find':'Trova DNS più veloce','dns_again':'Riprova','dns_testing':'Test…',
       'dns_best':'Più veloce','dns_copy':'Copia','dns_copied':'Copiato ✓',
       'dns_opennet':'Apri impostazioni di rete','dns_no_ipv6':'IPv6 non disponibile',
       'dns_howto':'Per cambiare: impostazioni di rete → scheda → DNS, e incolla l’indirizzo.'},
 'pt':{'dns':'DNS','dns_sub':'Encontra o DNS mais rápido para a tua ligação',
       'dns_find':'Encontrar DNS mais rápido','dns_again':'Repetir','dns_testing':'A testar…',
       'dns_best':'Mais rápido','dns_copy':'Copiar','dns_copied':'Copiado ✓',
       'dns_opennet':'Abrir definições de rede','dns_no_ipv6':'IPv6 indisponível',
       'dns_howto':'Para mudar: definições de rede → adaptador → DNS, e cola o endereço.'},
 'ru':{'dns':'DNS','dns_sub':'Найдите самый быстрый DNS для вашего подключения',
       'dns_find':'Найти быстрый DNS','dns_again':'Заново','dns_testing':'Проверка…',
       'dns_best':'Быстрейший','dns_copy':'Копировать','dns_copied':'Скопировано ✓',
       'dns_opennet':'Открыть параметры сети','dns_no_ipv6':'IPv6 недоступен',
       'dns_howto':'Чтобы сменить: параметры сети → адаптер → DNS, вставьте адрес.'},
}
for _lng, _d in DNS_I18N.items():
    CUST_LABELS.setdefault(_lng, {}).update(_d)
# "DNS Boost" tool label is the same brand term in every language
for _lng in CUST_LABELS:
    CUST_LABELS[_lng]['t_dnsboost'] = 'DNS Boost'
# "Current" (the machine's current DNS, shown for comparison)
_DNS_CUR = {'en':'Current','el':'Τρέχων','es':'Actual','de':'Aktuell',
            'fr':'Actuel','it':'Attuale','pt':'Atual','ru':'Текущий'}
for _lng, _v in _DNS_CUR.items():
    CUST_LABELS.setdefault(_lng, {})['dns_current'] = _v

# ── One-line "what it does" descriptions shown on hover in the Tools tab ──
TOOL_DESC = {
 'en':{'t_diskcleanup':'Free up disk space','t_storage':'Storage usage & cleanup',
       't_optimize':'Defragment / optimize drives','t_apps':'Installed apps & uninstall',
       't_tempfolder':'Open the Temp files folder','t_cleartemp':'Delete temporary files',
       't_recyclebin':'Empty the Recycle Bin','t_ramcheck':'Test your RAM for errors',
       't_taskmgr':'Processes & performance','t_resmon':'Live CPU/RAM/disk/network use',
       't_msinfo':'Full hardware & system report','t_reliability':'Stability & crash history',
       't_dxdiag':'DirectX & GPU diagnostics','t_power':'Power plan settings',
       't_startup':'Apps that run at startup','t_visualfx':'Animations & visual effects',
       't_graphics':'Per-app GPU preference','t_dnsboost':'Find the fastest DNS server',
       't_netstatus':'Network status & properties','t_adapters':'Network adapter settings',
       't_flushdns':'Clear the DNS cache','t_update':'Check for Windows updates',
       't_security':'Antivirus & firewall','t_restore':'Restore to an earlier point',
       't_devmgr':'Manage hardware devices'},
 'el':{'t_diskcleanup':'Ελευθέρωσε χώρο στον δίσκο','t_storage':'Χρήση & καθαρισμός αποθήκευσης',
       't_optimize':'Ανασυγκρότηση / βελτιστοποίηση','t_apps':'Εγκατεστημένες εφαρμογές & απεγκατάσταση',
       't_tempfolder':'Άνοιγμα φακέλου Temp','t_cleartemp':'Διαγραφή προσωρινών αρχείων',
       't_recyclebin':'Άδειασμα Κάδου','t_ramcheck':'Έλεγχος RAM για σφάλματα',
       't_taskmgr':'Διεργασίες & επιδόσεις','t_resmon':'Ζωντανή χρήση CPU/RAM/δίσκου/δικτύου',
       't_msinfo':'Πλήρης αναφορά υλικού','t_reliability':'Σταθερότητα & ιστορικό σφαλμάτων',
       't_dxdiag':'Διαγνωστικά DirectX & GPU','t_power':'Ρυθμίσεις σχεδίου ενέργειας',
       't_startup':'Εφαρμογές που ξεκινούν με τα Windows','t_visualfx':'Κινήσεις & οπτικά εφέ',
       't_graphics':'Προτίμηση GPU ανά εφαρμογή','t_dnsboost':'Βρες τον γρηγορότερο DNS',
       't_netstatus':'Κατάσταση & ιδιότητες δικτύου','t_adapters':'Ρυθμίσεις προσαρμογέα δικτύου',
       't_flushdns':'Καθαρισμός μνήμης DNS','t_update':'Έλεγχος για ενημερώσεις Windows',
       't_security':'Antivirus & τείχος προστασίας','t_restore':'Επαναφορά σε προηγούμενο σημείο',
       't_devmgr':'Διαχείριση συσκευών υλικού'},
 'es':{'t_diskcleanup':'Liberar espacio en disco','t_storage':'Uso y limpieza de almacenamiento',
       't_optimize':'Desfragmentar / optimizar','t_apps':'Apps instaladas y desinstalar',
       't_tempfolder':'Abrir la carpeta Temp','t_cleartemp':'Eliminar archivos temporales',
       't_recyclebin':'Vaciar la papelera','t_ramcheck':'Probar la RAM en busca de errores',
       't_taskmgr':'Procesos y rendimiento','t_resmon':'Uso en vivo CPU/RAM/disco/red',
       't_msinfo':'Informe completo del sistema','t_reliability':'Estabilidad e historial de fallos',
       't_dxdiag':'Diagnóstico DirectX y GPU','t_power':'Opciones del plan de energía',
       't_startup':'Apps que inician con Windows','t_visualfx':'Animaciones y efectos visuales',
       't_graphics':'Preferencia de GPU por app','t_dnsboost':'Encuentra el DNS más rápido',
       't_netstatus':'Estado y propiedades de red','t_adapters':'Configuración del adaptador',
       't_flushdns':'Vaciar la caché DNS','t_update':'Buscar actualizaciones de Windows',
       't_security':'Antivirus y firewall','t_restore':'Restaurar a un punto anterior',
       't_devmgr':'Administrar dispositivos'},
 'de':{'t_diskcleanup':'Speicherplatz freigeben','t_storage':'Speichernutzung & Bereinigung',
       't_optimize':'Defragmentieren / optimieren','t_apps':'Installierte Apps & Deinstallation',
       't_tempfolder':'Temp-Ordner öffnen','t_cleartemp':'Temporäre Dateien löschen',
       't_recyclebin':'Papierkorb leeren','t_ramcheck':'RAM auf Fehler testen',
       't_taskmgr':'Prozesse & Leistung','t_resmon':'Live CPU/RAM/Disk/Netz-Nutzung',
       't_msinfo':'Vollständiger Systembericht','t_reliability':'Stabilität & Absturzverlauf',
       't_dxdiag':'DirectX- & GPU-Diagnose','t_power':'Energieplan-Einstellungen',
       't_startup':'Autostart-Apps','t_visualfx':'Animationen & visuelle Effekte',
       't_graphics':'GPU-Präferenz pro App','t_dnsboost':'Schnellsten DNS finden',
       't_netstatus':'Netzwerkstatus & Eigenschaften','t_adapters':'Netzwerkadapter-Einstellungen',
       't_flushdns':'DNS-Cache leeren','t_update':'Nach Windows-Updates suchen',
       't_security':'Antivirus & Firewall','t_restore':'Auf früheren Punkt zurücksetzen',
       't_devmgr':'Geräte verwalten'},
 'fr':{'t_diskcleanup':'Libérer de l’espace disque','t_storage':'Stockage & nettoyage',
       't_optimize':'Défragmenter / optimiser','t_apps':'Applications & désinstallation',
       't_tempfolder':'Ouvrir le dossier Temp','t_cleartemp':'Supprimer les fichiers temporaires',
       't_recyclebin':'Vider la corbeille','t_ramcheck':'Tester la RAM',
       't_taskmgr':'Processus & performances','t_resmon':'Usage CPU/RAM/disque/réseau en direct',
       't_msinfo':'Rapport système complet','t_reliability':'Stabilité & historique des pannes',
       't_dxdiag':'Diagnostic DirectX & GPU','t_power':'Options d’alimentation',
       't_startup':'Applications au démarrage','t_visualfx':'Animations & effets visuels',
       't_graphics':'Préférence GPU par appli','t_dnsboost':'Trouver le DNS le plus rapide',
       't_netstatus':'État & propriétés du réseau','t_adapters':'Paramètres de la carte réseau',
       't_flushdns':'Vider le cache DNS','t_update':'Rechercher des mises à jour',
       't_security':'Antivirus & pare-feu','t_restore':'Restaurer à un point antérieur',
       't_devmgr':'Gérer les périphériques'},
 'it':{'t_diskcleanup':'Libera spazio su disco','t_storage':'Uso & pulizia archiviazione',
       't_optimize':'Deframmenta / ottimizza','t_apps':'App installate & disinstalla',
       't_tempfolder':'Apri la cartella Temp','t_cleartemp':'Elimina file temporanei',
       't_recyclebin':'Svuota il cestino','t_ramcheck':'Verifica la RAM',
       't_taskmgr':'Processi & prestazioni','t_resmon':'Uso live CPU/RAM/disco/rete',
       't_msinfo':'Report completo del sistema','t_reliability':'Stabilità & cronologia errori',
       't_dxdiag':'Diagnostica DirectX & GPU','t_power':'Opzioni risparmio energia',
       't_startup':'App all’avvio','t_visualfx':'Animazioni & effetti visivi',
       't_graphics':'Preferenza GPU per app','t_dnsboost':'Trova il DNS più veloce',
       't_netstatus':'Stato & proprietà di rete','t_adapters':'Impostazioni scheda di rete',
       't_flushdns':'Svuota la cache DNS','t_update':'Cerca aggiornamenti di Windows',
       't_security':'Antivirus & firewall','t_restore':'Ripristina a un punto precedente',
       't_devmgr':'Gestisci dispositivi'},
 'pt':{'t_diskcleanup':'Libertar espaço em disco','t_storage':'Uso & limpeza de armazenamento',
       't_optimize':'Desfragmentar / otimizar','t_apps':'Apps instaladas & desinstalar',
       't_tempfolder':'Abrir a pasta Temp','t_cleartemp':'Eliminar ficheiros temporários',
       't_recyclebin':'Esvaziar a reciclagem','t_ramcheck':'Testar a RAM',
       't_taskmgr':'Processos & desempenho','t_resmon':'Uso ao vivo CPU/RAM/disco/rede',
       't_msinfo':'Relatório completo do sistema','t_reliability':'Estabilidade & histórico de falhas',
       't_dxdiag':'Diagnóstico DirectX & GPU','t_power':'Opções de energia',
       't_startup':'Apps no arranque','t_visualfx':'Animações & efeitos visuais',
       't_graphics':'Preferência de GPU por app','t_dnsboost':'Encontra o DNS mais rápido',
       't_netstatus':'Estado & propriedades de rede','t_adapters':'Definições da placa de rede',
       't_flushdns':'Limpar a cache DNS','t_update':'Procurar atualizações do Windows',
       't_security':'Antivírus & firewall','t_restore':'Restaurar a um ponto anterior',
       't_devmgr':'Gerir dispositivos'},
 'ru':{'t_diskcleanup':'Освободить место на диске','t_storage':'Хранилище и очистка',
       't_optimize':'Дефрагментация / оптимизация','t_apps':'Приложения и удаление',
       't_tempfolder':'Открыть папку Temp','t_cleartemp':'Удалить временные файлы',
       't_recyclebin':'Очистить корзину','t_ramcheck':'Проверить ОЗУ на ошибки',
       't_taskmgr':'Процессы и производительность','t_resmon':'Живое использование ресурсов',
       't_msinfo':'Полный отчёт о системе','t_reliability':'Стабильность и история сбоев',
       't_dxdiag':'Диагностика DirectX и GPU','t_power':'Параметры электропитания',
       't_startup':'Автозагрузка приложений','t_visualfx':'Анимации и визуальные эффекты',
       't_graphics':'Предпочтение GPU для приложений','t_dnsboost':'Найти самый быстрый DNS',
       't_netstatus':'Состояние и свойства сети','t_adapters':'Параметры сетевого адаптера',
       't_flushdns':'Очистить кэш DNS','t_update':'Проверить обновления Windows',
       't_security':'Антивирус и брандмауэр','t_restore':'Восстановить к точке',
       't_devmgr':'Управление устройствами'},
}
for _lng, _d in TOOL_DESC.items():
    CUST_LABELS.setdefault(_lng, {}).update({'desc__' + k: v for k, v in _d.items()})

# ── Bar marker (icons vs text) labels (v2.8) ───────────────────────────
MARKER_I18N = {
 'en':{'bar_marker':'Bar marker','marker_icon':'Icons','marker_text':'Text'},
 'el':{'bar_marker':'Μπάρα','marker_icon':'Εικονίδια','marker_text':'Κείμενο'},
 'es':{'bar_marker':'Barra','marker_icon':'Iconos','marker_text':'Texto'},
 'de':{'bar_marker':'Leiste','marker_icon':'Symbole','marker_text':'Text'},
 'fr':{'bar_marker':'Barre','marker_icon':'Icônes','marker_text':'Texte'},
 'it':{'bar_marker':'Barra','marker_icon':'Icone','marker_text':'Testo'},
 'pt':{'bar_marker':'Barra','marker_icon':'Ícones','marker_text':'Texto'},
 'ru':{'bar_marker':'Панель','marker_icon':'Значки','marker_text':'Текст'},
}
for _lng, _d in MARKER_I18N.items():
    CUST_LABELS.setdefault(_lng, {}).update(_d)

# "Rate" — Store review link (tray menu uses T, About tab uses CUST_LABELS)
_RATE = {'en':'Rate','el':'Αξιολόγηση','es':'Valorar','de':'Bewerten',
         'fr':'Noter','it':'Valuta','pt':'Avaliar','ru':'Оценить'}
for _lng, _v in _RATE.items():
    CUST_LABELS.setdefault(_lng, {})['rate'] = _v
    if _lng in T:
        T[_lng]['rate'] = _v

# ── Weather location settings (moved into Appearance from the old tray) ──
WEATHER_I18N = {
 'en':{'weather_lbl':'Weather','weather_city':'Weather city','weather_city_hint':'Leave empty to locate automatically by your IP.'},
 'el':{'weather_lbl':'Καιρός','weather_city':'Πόλη καιρού','weather_city_hint':'Άφησέ το κενό για αυτόματο εντοπισμό μέσω IP.'},
 'es':{'weather_lbl':'Tiempo','weather_city':'Ciudad del tiempo','weather_city_hint':'Déjalo vacío para localizar automáticamente por IP.'},
 'de':{'weather_lbl':'Wetter','weather_city':'Wetter-Stadt','weather_city_hint':'Leer lassen, um automatisch per IP zu lokalisieren.'},
 'fr':{'weather_lbl':'Météo','weather_city':'Ville météo','weather_city_hint':'Laissez vide pour localiser automatiquement par IP.'},
 'it':{'weather_lbl':'Meteo','weather_city':'Città meteo','weather_city_hint':'Lascia vuoto per localizzare automaticamente tramite IP.'},
 'pt':{'weather_lbl':'Tempo','weather_city':'Cidade do tempo','weather_city_hint':'Deixe vazio para localizar automaticamente por IP.'},
 'ru':{'weather_lbl':'Погода','weather_city':'Город погоды','weather_city_hint':'Оставьте пустым для автоопределения по IP.'},
}
for _lng, _d in WEATHER_I18N.items():
    CUST_LABELS.setdefault(_lng, {}).update(_d)

# ── Diagnostics labels (v2.8.2) ───────────────────────────────────────
DIAG_I18N = {
 'en':{'run_diag':'Run diagnostics','diag_done':'{ok}/{n} OK · copied to clipboard',
       'diag_fail':'Diagnostics failed','diag_hint':'Paste this in a bug report so we can help.'},
 'el':{'run_diag':'Εκτέλεση διαγνωστικών','diag_done':'{ok}/{n} OK · αντιγράφηκε',
       'diag_fail':'Αποτυχία διαγνωστικών','diag_hint':'Επικόλλησέ το σε αναφορά σφάλματος για να βοηθήσουμε.'},
 'es':{'run_diag':'Ejecutar diagnóstico','diag_done':'{ok}/{n} OK · copiado al portapapeles',
       'diag_fail':'Diagnóstico falló','diag_hint':'Pégalo en un informe de error para ayudarte.'},
 'de':{'run_diag':'Diagnose ausführen','diag_done':'{ok}/{n} OK · in Zwischenablage',
       'diag_fail':'Diagnose fehlgeschlagen','diag_hint':'Füge dies in einen Fehlerbericht ein.'},
 'fr':{'run_diag':'Lancer le diagnostic','diag_done':'{ok}/{n} OK · copié dans le presse-papiers',
       'diag_fail':'Diagnostic échoué','diag_hint':'Collez ceci dans un rapport de bug.'},
 'it':{'run_diag':'Esegui diagnostica','diag_done':'{ok}/{n} OK · copiato negli appunti',
       'diag_fail':'Diagnostica fallita','diag_hint':'Incollalo in una segnalazione di bug.'},
 'pt':{'run_diag':'Executar diagnóstico','diag_done':'{ok}/{n} OK · copiado para a área',
       'diag_fail':'Diagnóstico falhou','diag_hint':'Cole isto num relatório de erro.'},
 'ru':{'run_diag':'Запустить диагностику','diag_done':'{ok}/{n} OK · скопировано',
       'diag_fail':'Диагностика не удалась','diag_hint':'Вставьте это в отчёт об ошибке.'},
}
for _lng, _d in DIAG_I18N.items():
    CUST_LABELS.setdefault(_lng, {}).update(_d)

# ── More tools (GPU reset, lock, restart Explorer, hibernate, sound, …) ──
NEW_TOOLS_I18N = {
 'en':{'t_gpureset':'Reset GPU driver','t_explorer':'Restart Explorer',
       't_hibernate':'Hibernate now','t_lock':'Lock screen',
       't_sound':'Sound devices','t_micpriv':'Microphone privacy',
       't_campriv':'Camera privacy','t_proxy':'Proxy settings','t_vpn':'VPN',
       't_classicmenu':'Classic right-click menu',
       'desc__t_classicmenu':'Toggle the Windows 10 style context menu',
       'cf_ctx_on':'Switch to the classic (Windows 10) right-click menu? Explorer will restart.',
       'cf_ctx_off':'Restore the Windows 11 right-click menu? Explorer will restart.',
       'tt_ctx_on':'Classic right-click menu enabled ✓',
       'tt_ctx_off':'Windows 11 right-click menu restored ✓',
       'desc__t_gpureset':'Recover from a frozen GPU (Win+Ctrl+Shift+B)',
       'desc__t_explorer':'Refresh the taskbar & desktop',
       'desc__t_hibernate':'Save your session and power off',
       'desc__t_lock':'Lock the workstation (Win+L)',
       'desc__t_sound':'Playback / recording devices',
       'desc__t_micpriv':'Which apps can use the microphone',
       'desc__t_campriv':'Which apps can use the camera',
       'desc__t_proxy':'Manual / automatic proxy', 'desc__t_vpn':'VPN connections',
       'cf_gpu':'Reset the graphics driver? The screen will briefly black out — no data is lost.',
       'cf_expl':'Restart Explorer? Open File Explorer windows will close.',
       'cf_hib':'Hibernate the PC now? Your open work is saved.'},
 'el':{'t_gpureset':'Reset GPU driver','t_explorer':'Επανεκκίνηση Explorer',
       't_hibernate':'Αδρανοποίηση','t_lock':'Κλείδωμα οθόνης',
       't_sound':'Συσκευές ήχου','t_micpriv':'Απόρρητο μικροφώνου',
       't_campriv':'Απόρρητο κάμερας','t_proxy':'Ρυθμίσεις proxy','t_vpn':'VPN',
       't_classicmenu':'Κλασικό δεξί κλικ (Win10)',
       'desc__t_classicmenu':'Εναλλαγή στο μενού δεξιού κλικ τύπου Windows 10',
       'cf_ctx_on':'Αλλαγή στο κλασικό (Windows 10) μενού δεξιού κλικ; Θα γίνει επανεκκίνηση του Explorer.',
       'cf_ctx_off':'Επαναφορά του μενού δεξιού κλικ των Windows 11; Θα γίνει επανεκκίνηση του Explorer.',
       'tt_ctx_on':'Ενεργοποιήθηκε το κλασικό μενού ✓',
       'tt_ctx_off':'Επαναφέρθηκε το μενού των Windows 11 ✓',
       'desc__t_gpureset':'Επαναφορά κολλημένης GPU (Win+Ctrl+Shift+B)',
       'desc__t_explorer':'Ανανέωση μπάρας & επιφάνειας εργασίας',
       'desc__t_hibernate':'Αποθήκευση συνεδρίας και απενεργοποίηση',
       'desc__t_lock':'Κλείδωμα σταθμού (Win+L)',
       'desc__t_sound':'Συσκευές αναπαραγωγής / εγγραφής',
       'desc__t_micpriv':'Ποιες εφαρμογές χρησιμοποιούν το μικρόφωνο',
       'desc__t_campriv':'Ποιες εφαρμογές χρησιμοποιούν την κάμερα',
       'desc__t_proxy':'Χειροκίνητο / αυτόματο proxy','desc__t_vpn':'Συνδέσεις VPN',
       'cf_gpu':'Επαναφορά οδηγού γραφικών; Η οθόνη θα μαυρίσει στιγμιαία — δεν χάνεται τίποτα.',
       'cf_expl':'Επανεκκίνηση Explorer; Τα ανοιχτά παράθυρα του File Explorer θα κλείσουν.',
       'cf_hib':'Αδρανοποίηση τώρα; Η εργασία σου αποθηκεύεται.'},
 'es':{'t_gpureset':'Reset GPU driver','t_explorer':'Reiniciar Explorer',
       't_hibernate':'Hibernar ahora','t_lock':'Bloquear pantalla',
       't_sound':'Dispositivos de sonido','t_micpriv':'Privacidad del micrófono',
       't_campriv':'Privacidad de la cámara','t_proxy':'Proxy','t_vpn':'VPN',
       't_classicmenu':'Menú clásico (clic derecho)',
       'desc__t_gpureset':'Recupera una GPU congelada (Win+Ctrl+Shift+B)',
       'desc__t_explorer':'Refrescar barra y escritorio',
       'desc__t_hibernate':'Guarda la sesión y apaga','desc__t_lock':'Bloquear (Win+L)',
       'desc__t_sound':'Reproducción / grabación',
       'desc__t_micpriv':'Apps con acceso al micrófono',
       'desc__t_campriv':'Apps con acceso a la cámara',
       'desc__t_proxy':'Proxy manual / automático','desc__t_vpn':'Conexiones VPN',
       'cf_gpu':'¿Reiniciar el controlador de gráficos? La pantalla parpadeará — no se pierden datos.',
       'cf_expl':'¿Reiniciar Explorer? Las ventanas abiertas se cerrarán.',
       'cf_hib':'¿Hibernar ahora? Tu trabajo se guarda.'},
 'de':{'t_gpureset':'GPU-Treiber zurücksetzen','t_explorer':'Explorer neu starten',
       't_hibernate':'Ruhezustand','t_lock':'Bildschirm sperren',
       't_sound':'Audiogeräte','t_micpriv':'Mikrofon-Privatsphäre',
       't_campriv':'Kamera-Privatsphäre','t_proxy':'Proxy','t_vpn':'VPN',
       't_classicmenu':'Klassisches Rechtsklickmenü',
       'desc__t_gpureset':'Hängende GPU zurücksetzen (Win+Strg+Umsch+B)',
       'desc__t_explorer':'Taskleiste & Desktop aktualisieren',
       'desc__t_hibernate':'Sitzung speichern und ausschalten',
       'desc__t_lock':'Arbeitsplatz sperren (Win+L)',
       'desc__t_sound':'Wiedergabe / Aufnahme',
       'desc__t_micpriv':'Welche Apps das Mikrofon nutzen',
       'desc__t_campriv':'Welche Apps die Kamera nutzen',
       'desc__t_proxy':'Manueller / automatischer Proxy','desc__t_vpn':'VPN-Verbindungen',
       'cf_gpu':'Grafiktreiber zurücksetzen? Der Bildschirm wird kurz schwarz — keine Daten gehen verloren.',
       'cf_expl':'Explorer neu starten? Offene Fenster werden geschlossen.',
       'cf_hib':'PC jetzt in Ruhezustand? Ihre Arbeit wird gespeichert.'},
 'fr':{'t_gpureset':'Réinitialiser le pilote GPU','t_explorer':'Redémarrer Explorer',
       't_hibernate':'Veille prolongée','t_lock':'Verrouiller',
       't_sound':'Périphériques audio','t_micpriv':'Confidentialité micro',
       't_campriv':'Confidentialité caméra','t_proxy':'Proxy','t_vpn':'VPN',
       't_classicmenu':'Menu clic droit classique',
       'desc__t_gpureset':'Récupérer une GPU figée (Win+Ctrl+Maj+B)',
       'desc__t_explorer':'Actualiser barre et bureau',
       'desc__t_hibernate':'Enregistre la session et éteint',
       'desc__t_lock':'Verrouiller (Win+L)',
       'desc__t_sound':'Lecture / enregistrement',
       'desc__t_micpriv':'Applications utilisant le micro',
       'desc__t_campriv':'Applications utilisant la caméra',
       'desc__t_proxy':'Proxy manuel / automatique','desc__t_vpn':'Connexions VPN',
       'cf_gpu':'Réinitialiser le pilote graphique ? L\'écran clignote — aucune donnée perdue.',
       'cf_expl':'Redémarrer Explorer ? Les fenêtres ouvertes se fermeront.',
       'cf_hib':'Mettre en veille prolongée ? Votre travail est sauvegardé.'},
 'it':{'t_gpureset':'Reset driver GPU','t_explorer':'Riavvia Explorer',
       't_hibernate':'Sospensione','t_lock':'Blocca schermo',
       't_sound':'Dispositivi audio','t_micpriv':'Privacy microfono',
       't_campriv':'Privacy fotocamera','t_proxy':'Proxy','t_vpn':'VPN',
       't_classicmenu':'Menu classico (tasto destro)',
       'desc__t_gpureset':'Recupera GPU bloccata (Win+Ctrl+Maiusc+B)',
       'desc__t_explorer':'Aggiorna barra e desktop',
       'desc__t_hibernate':'Salva sessione e spegne',
       'desc__t_lock':'Blocca (Win+L)','desc__t_sound':'Riproduzione / registrazione',
       'desc__t_micpriv':'App che usano il microfono',
       'desc__t_campriv':'App che usano la fotocamera',
       'desc__t_proxy':'Proxy manuale / automatico','desc__t_vpn':'Connessioni VPN',
       'cf_gpu':'Resettare il driver grafico? Lo schermo lampeggia — nessun dato perso.',
       'cf_expl':'Riavviare Explorer? Le finestre aperte si chiuderanno.',
       'cf_hib':'Sospendere ora? Il tuo lavoro viene salvato.'},
 'pt':{'t_gpureset':'Reset driver GPU','t_explorer':'Reiniciar Explorer',
       't_hibernate':'Hibernar agora','t_lock':'Bloquear ecrã',
       't_sound':'Dispositivos de som','t_micpriv':'Privacidade do microfone',
       't_campriv':'Privacidade da câmara','t_proxy':'Proxy','t_vpn':'VPN',
       't_classicmenu':'Menu clássico (clique direito)',
       'desc__t_gpureset':'Recupera GPU bloqueada (Win+Ctrl+Shift+B)',
       'desc__t_explorer':'Atualizar barra e ambiente',
       'desc__t_hibernate':'Guarda a sessão e desliga',
       'desc__t_lock':'Bloquear (Win+L)','desc__t_sound':'Reprodução / gravação',
       'desc__t_micpriv':'Apps que usam o microfone',
       'desc__t_campriv':'Apps que usam a câmara',
       'desc__t_proxy':'Proxy manual / automático','desc__t_vpn':'Ligações VPN',
       'cf_gpu':'Reiniciar o driver gráfico? O ecrã pisca — não se perdem dados.',
       'cf_expl':'Reiniciar o Explorer? As janelas abertas serão fechadas.',
       'cf_hib':'Hibernar agora? O seu trabalho é guardado.'},
 'ru':{'t_gpureset':'Сброс GPU','t_explorer':'Перезапуск Explorer',
       't_hibernate':'Гибернация','t_lock':'Блокировка экрана',
       't_sound':'Звуковые устройства','t_micpriv':'Конфиденциальность микрофона',
       't_campriv':'Конфиденциальность камеры','t_proxy':'Прокси','t_vpn':'VPN',
       't_classicmenu':'Классическое меню ПКМ',
       'desc__t_gpureset':'Восстановить зависшую GPU (Win+Ctrl+Shift+B)',
       'desc__t_explorer':'Обновить панель и рабочий стол',
       'desc__t_hibernate':'Сохранить сеанс и выключить',
       'desc__t_lock':'Блокировать (Win+L)',
       'desc__t_sound':'Воспроизведение / запись',
       'desc__t_micpriv':'Какие приложения используют микрофон',
       'desc__t_campriv':'Какие приложения используют камеру',
       'desc__t_proxy':'Ручной / автоматический прокси','desc__t_vpn':'VPN-подключения',
       'cf_gpu':'Сбросить графический драйвер? Экран мигнёт — данные не теряются.',
       'cf_expl':'Перезапустить Explorer? Открытые окна закроются.',
       'cf_hib':'Включить гибернацию? Ваша работа сохраняется.'},
}
for _lng, _d in NEW_TOOLS_I18N.items():
    CUST_LABELS.setdefault(_lng, {}).update(_d)

# ── v2.9 feature strings for the remaining languages (en/el already defined
#    inline above). Values use double quotes so apostrophes need no escaping. ──
NEW_V29_I18N = {
 'es': {
   'sys_machine':"Sistema", 'sys_battery':"Batería", 'sys_drives':"Discos",
   'sys_security':"Seguridad", 'sys_summary':"Resumen", 'sys_advanced':"Avanzado",
   'hide_fs':"Ocultar cuando una app pasa a pantalla completa",
   'desc__t_classicmenu':"Alternar el menú contextual estilo Windows 10",
   'cf_ctx_on':"¿Cambiar al menú contextual clásico (Windows 10)? Se reiniciará el Explorador.",
   'cf_ctx_off':"¿Restaurar el menú contextual de Windows 11? Se reiniciará el Explorador.",
   'tt_ctx_on':"Menú clásico activado ✓", 'tt_ctx_off':"Menú de Windows 11 restaurado ✓",
   'su_sub':"Accesos directos a paneles avanzados y normalmente ocultos de Windows.",
   'su_god':"God Mode", 'su_god_d':"Todas las tareas del Panel de control en una lista",
   'su_dev':"Modo de desarrollador", 'su_dev_d':"Abrir Configuración → Para desarrolladores",
   'su_msconfig':"Configuración del sistema", 'su_msconfig_d':"msconfig — arranque, servicios, inicio",
   'su_regedit':"Editor del Registro", 'su_regedit_d':"regedit — editar el Registro de Windows (¡cuidado!)",
   'su_gpedit':"Editor de directivas de grupo", 'su_gpedit_d':"gpedit.msc — directivas locales (ediciones Pro)",
   'su_services':"Servicios", 'su_services_d':"services.msc — iniciar/detener servicios de Windows",
   'su_startup':"Carpeta de inicio", 'su_startup_d':"shell:startup — apps que se abren al iniciar sesión",
   'su_sys32':"Carpeta System32", 'su_sys32_d':"Abrir el directorio System32 de Windows",
 },
 'de': {
   'sys_machine':"System", 'sys_battery':"Akku", 'sys_drives':"Laufwerke",
   'sys_security':"Sicherheit", 'sys_summary':"Übersicht", 'sys_advanced':"Erweitert",
   'hide_fs':"Ausblenden, wenn eine App in den Vollbildmodus wechselt",
   'desc__t_classicmenu':"Klassisches Kontextmenü (Windows 10) umschalten",
   'cf_ctx_on':"Zum klassischen (Windows 10) Kontextmenü wechseln? Der Explorer wird neu gestartet.",
   'cf_ctx_off':"Das Windows-11-Kontextmenü wiederherstellen? Der Explorer wird neu gestartet.",
   'tt_ctx_on':"Klassisches Menü aktiviert ✓", 'tt_ctx_off':"Windows-11-Menü wiederhergestellt ✓",
   'su_sub':"Verknüpfungen zu erweiterten, normalerweise versteckten Windows-Bereichen.",
   'su_god':"God Mode", 'su_god_d':"Alle Systemsteuerungs-Aufgaben in einer Liste",
   'su_dev':"Entwicklermodus", 'su_dev_d':"Einstellungen → Für Entwickler öffnen",
   'su_msconfig':"Systemkonfiguration", 'su_msconfig_d':"msconfig — Start, Dienste, Autostart",
   'su_regedit':"Registrierungs-Editor", 'su_regedit_d':"regedit — Windows-Registry bearbeiten (Vorsicht!)",
   'su_gpedit':"Gruppenrichtlinien-Editor", 'su_gpedit_d':"gpedit.msc — lokale Richtlinien (Pro-Editionen)",
   'su_services':"Dienste", 'su_services_d':"services.msc — Windows-Dienste starten/stoppen",
   'su_startup':"Autostart-Ordner", 'su_startup_d':"shell:startup — Apps, die bei der Anmeldung starten",
   'su_sys32':"System32-Ordner", 'su_sys32_d':"Windows-System32-Verzeichnis öffnen",
 },
 'fr': {
   'sys_machine':"Système", 'sys_battery':"Batterie", 'sys_drives':"Disques",
   'sys_security':"Sécurité", 'sys_summary':"Résumé", 'sys_advanced':"Avancé",
   'hide_fs':"Masquer quand une appli passe en plein écran",
   'desc__t_classicmenu':"Basculer le menu contextuel style Windows 10",
   'cf_ctx_on':"Passer au menu contextuel classique (Windows 10) ? L'Explorateur redémarrera.",
   'cf_ctx_off':"Restaurer le menu contextuel de Windows 11 ? L'Explorateur redémarrera.",
   'tt_ctx_on':"Menu classique activé ✓", 'tt_ctx_off':"Menu Windows 11 restauré ✓",
   'su_sub':"Raccourcis vers des panneaux Windows avancés, normalement cachés.",
   'su_god':"God Mode", 'su_god_d':"Toutes les tâches du Panneau de configuration en une liste",
   'su_dev':"Mode développeur", 'su_dev_d':"Ouvrir Paramètres → Pour les développeurs",
   'su_msconfig':"Configuration du système", 'su_msconfig_d':"msconfig — démarrage, services, applications",
   'su_regedit':"Éditeur du Registre", 'su_regedit_d':"regedit — modifier le Registre Windows (prudence !)",
   'su_gpedit':"Éditeur de stratégie de groupe", 'su_gpedit_d':"gpedit.msc — stratégies locales (éditions Pro)",
   'su_services':"Services", 'su_services_d':"services.msc — démarrer/arrêter les services Windows",
   'su_startup':"Dossier de démarrage", 'su_startup_d':"shell:startup — applis lancées à la connexion",
   'su_sys32':"Dossier System32", 'su_sys32_d':"Ouvrir le répertoire System32 de Windows",
 },
 'it': {
   'sys_machine':"Sistema", 'sys_battery':"Batteria", 'sys_drives':"Dischi",
   'sys_security':"Sicurezza", 'sys_summary':"Riepilogo", 'sys_advanced':"Avanzate",
   'hide_fs':"Nascondi quando un'app va a schermo intero",
   'desc__t_classicmenu':"Attiva/disattiva il menu contestuale stile Windows 10",
   'cf_ctx_on':"Passare al menu contestuale classico (Windows 10)? Explorer verrà riavviato.",
   'cf_ctx_off':"Ripristinare il menu contestuale di Windows 11? Explorer verrà riavviato.",
   'tt_ctx_on':"Menu classico attivato ✓", 'tt_ctx_off':"Menu di Windows 11 ripristinato ✓",
   'su_sub':"Scorciatoie verso pannelli avanzati e solitamente nascosti di Windows.",
   'su_god':"God Mode", 'su_god_d':"Tutte le attività del Pannello di controllo in un elenco",
   'su_dev':"Modalità sviluppatore", 'su_dev_d':"Apri Impostazioni → Per gli sviluppatori",
   'su_msconfig':"Configurazione di sistema", 'su_msconfig_d':"msconfig — avvio, servizi, esecuzione automatica",
   'su_regedit':"Editor del Registro", 'su_regedit_d':"regedit — modifica il Registro di Windows (attenzione!)",
   'su_gpedit':"Editor Criteri di gruppo", 'su_gpedit_d':"gpedit.msc — criteri locali (edizioni Pro)",
   'su_services':"Servizi", 'su_services_d':"services.msc — avvia/ferma i servizi di Windows",
   'su_startup':"Cartella Esecuzione automatica", 'su_startup_d':"shell:startup — app avviate all'accesso",
   'su_sys32':"Cartella System32", 'su_sys32_d':"Apri la directory System32 di Windows",
 },
 'pt': {
   'sys_machine':"Sistema", 'sys_battery':"Bateria", 'sys_drives':"Discos",
   'sys_security':"Segurança", 'sys_summary':"Resumo", 'sys_advanced':"Avançado",
   'hide_fs':"Ocultar quando uma app entra em ecrã inteiro",
   'desc__t_classicmenu':"Alternar o menu de contexto estilo Windows 10",
   'cf_ctx_on':"Mudar para o menu de contexto clássico (Windows 10)? O Explorador reiniciará.",
   'cf_ctx_off':"Restaurar o menu de contexto do Windows 11? O Explorador reiniciará.",
   'tt_ctx_on':"Menu clássico ativado ✓", 'tt_ctx_off':"Menu do Windows 11 restaurado ✓",
   'su_sub':"Atalhos para painéis avançados e normalmente ocultos do Windows.",
   'su_god':"God Mode", 'su_god_d':"Todas as tarefas do Painel de Controlo numa lista",
   'su_dev':"Modo de programador", 'su_dev_d':"Abrir Definições → Para programadores",
   'su_msconfig':"Configuração do sistema", 'su_msconfig_d':"msconfig — arranque, serviços, iniciar",
   'su_regedit':"Editor de Registo", 'su_regedit_d':"regedit — editar o Registo do Windows (cuidado!)",
   'su_gpedit':"Editor de Políticas de Grupo", 'su_gpedit_d':"gpedit.msc — políticas locais (edições Pro)",
   'su_services':"Serviços", 'su_services_d':"services.msc — iniciar/parar serviços do Windows",
   'su_startup':"Pasta de arranque", 'su_startup_d':"shell:startup — apps que abrem ao iniciar sessão",
   'su_sys32':"Pasta System32", 'su_sys32_d':"Abrir o diretório System32 do Windows",
 },
 'ru': {
   'sys_machine':"Система", 'sys_battery':"Батарея", 'sys_drives':"Диски",
   'sys_security':"Безопасность", 'sys_summary':"Сводка", 'sys_advanced':"Подробно",
   'hide_fs':"Скрывать, когда приложение в полноэкранном режиме",
   'desc__t_classicmenu':"Переключить контекстное меню в стиле Windows 10",
   'cf_ctx_on':"Переключить на классическое меню (Windows 10)? Проводник перезапустится.",
   'cf_ctx_off':"Восстановить меню Windows 11? Проводник перезапустится.",
   'tt_ctx_on':"Классическое меню включено ✓", 'tt_ctx_off':"Меню Windows 11 восстановлено ✓",
   'su_sub':"Ярлыки к расширенным, обычно скрытым панелям Windows.",
   'su_god':"God Mode", 'su_god_d':"Все задачи Панели управления в одном списке",
   'su_dev':"Режим разработчика", 'su_dev_d':"Открыть Параметры → Для разработчиков",
   'su_msconfig':"Конфигурация системы", 'su_msconfig_d':"msconfig — загрузка, службы, автозагрузка",
   'su_regedit':"Редактор реестра", 'su_regedit_d':"regedit — редактирование реестра Windows (осторожно!)",
   'su_gpedit':"Редактор групповой политики", 'su_gpedit_d':"gpedit.msc — локальные политики (выпуски Pro)",
   'su_services':"Службы", 'su_services_d':"services.msc — запуск/остановка служб Windows",
   'su_startup':"Папка автозагрузки", 'su_startup_d':"shell:startup — приложения при входе",
   'su_sys32':"Папка System32", 'su_sys32_d':"Открыть каталог System32 Windows",
 },
}
for _lng, _d in NEW_V29_I18N.items():
    CUST_LABELS.setdefault(_lng, {}).update(_d)

# Expose the Superuser item descriptions as Tools-tab hover hints
# (the Tools tab looks up 'desc__<toolkey>').
for _lng in list(CUST_LABELS):
    for _k in ('su_god', 'su_dev', 'su_msconfig', 'su_regedit',
               'su_gpedit', 'su_services', 'su_startup', 'su_sys32'):
        _dv = CUST_LABELS[_lng].get(_k + '_d')
        if _dv:
            CUST_LABELS[_lng]['desc__' + _k] = _dv

# Cell metadata for the Metrics tab (id -> friendly name, icon glyph, config key)
CELL_META = (
    ('cpu',     'CPU',         '💻', 'show_cpu'),
    ('ram',     'RAM',         '🧠', 'show_ram'),
    ('gpu',     'GPU',         '🎮', 'show_gpu'),
    ('net',     'Network',     '🌐', 'show_net'),
    ('disk',    'Disk I/O',    '💿', 'show_disk'),
    ('batt',    'Battery',     '🔋', 'show_batt'),
    ('power',   'Power',       '⚡', 'show_power'),
)
DEFAULT_CELL_ORDER = [c[0] for c in CELL_META]
# Customize Window theme (matches the future PulseDeck dashboard)
CUST_THEME = {
    'bg':       '#0b0f18',
    'bg2':      '#131a28',
    'panel':    '#161b22',
    'line':     '#2d333b',
    'text':     '#ecf2f8',
    'muted':    '#8a9cba',
    'cyan':     '#3fc3ff',
    'blue':     '#58a6ff',
    'green':    '#3fb950',
    'orange':   '#ffa657',
    'red':      '#f85149',
    'magenta':  '#d96bff',
    'titlebar': '#0a1018',
}
RELEASES_URL = 'https://github.com/FokionPapanikolaou/PulseDeck/releases/latest'
RELEASES_API = 'https://api.github.com/repos/FokionPapanikolaou/PulseDeck/releases/latest'

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
    kernel32.CreateMutexW(None, False, 'Global\\PulseDeck_SingleInstance')
    return kernel32.GetLastError() == ERROR_ALREADY_EXISTS

# ── Windows work area ──────────────────────────────────────────────────
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong), ("rcMonitor", RECT),
                ("rcWork", RECT), ("dwFlags", ctypes.c_ulong)]

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

# ── Power consumption estimate (v2.7) ──────────────────────────────────
# Reports a best-effort live wattage figure for CPU + GPU.
# Strategy, in order of accuracy:
#   1) NVIDIA NVML (via nvidia-smi)  -> exact GPU power if NVIDIA
#   2) Battery discharge rate         -> exact full-system power on laptops
#   3) Estimate: TDP × utilisation%   -> universal fallback (~15% accuracy)
#
# The TDP tables are intentionally short and approximate — a 65/95/105/125W
# CPU classification is enough for the bar (precision isn't the point; trends
# are). For the GPU we use a small map of recent AMD/NVIDIA cards and fall
# back to 150W generic.

_CPU_TDP_HINTS = (
    # patterns -> TDP watts
    ('Core i3', 65), ('Core i5', 65), ('Core i7', 125), ('Core i9', 125),
    ('Ryzen 3', 65), ('Ryzen 5', 65), ('Ryzen 7', 105),
    ('Ryzen 9 7950', 170), ('Ryzen 9 7900', 170), ('Ryzen 9 5950', 105),
    ('Ryzen 9 5900', 105), ('Ryzen Threadripper', 280),
    ('Atom', 10), ('Celeron', 15), ('Pentium', 35), ('Xeon', 150),
    ('AMD A', 65), ('FX-', 95),
)
_GPU_TDP_HINTS = (
    # pattern -> TDP watts
    ('RTX 4090', 450), ('RTX 4080', 320), ('RTX 4070 Ti', 285), ('RTX 4070', 200),
    ('RTX 4060 Ti', 165), ('RTX 4060', 115), ('RTX 4050', 115),
    ('RTX 3090', 350), ('RTX 3080', 320), ('RTX 3070', 220),
    ('RTX 3060 Ti', 200), ('RTX 3060', 170), ('RTX 3050', 130),
    ('RTX 2080', 215), ('RTX 2070', 175), ('RTX 2060', 160),
    ('GTX 1660', 120), ('GTX 1650', 75), ('GTX 1060', 120),
    # AMD
    ('RX 9070', 220), ('RX 9060', 160), ('RX 7900 XTX', 355), ('RX 7900 XT', 315),
    ('RX 7800 XT', 263), ('RX 7700 XT', 245), ('RX 7600', 165),
    ('RX 6950', 335), ('RX 6900', 300), ('RX 6800', 250), ('RX 6700', 230),
    ('RX 6600', 132), ('RX 6500', 107),
    # Intel
    ('Arc A770', 225), ('Arc A750', 225), ('Arc A580', 175), ('Arc A380', 75),
    # Integrated / generic
    ('Vega', 15), ('UHD Graphics', 15), ('Iris', 25), ('Radeon Graphics', 15),
)

def _match_tdp(name, hints, default):
    if not name: return default
    up = str(name)
    for pat, w in hints:
        if pat.lower() in up.lower():
            return w
    return default

def get_cpu_tdp_w(name):
    return _match_tdp(name, _CPU_TDP_HINTS, 65)

def get_gpu_tdp_w(name):
    return _match_tdp(name, _GPU_TDP_HINTS, 150)

_NVSMI_OK = None   # None = untested, False = missing (never retry), True = works

def _nvidia_smi_power():
    """Return GPU power draw in watts via nvidia-smi, or None.
    Caches availability: spawning a subprocess every poll on systems WITHOUT
    nvidia-smi (AMD/Intel) cost 10-50 ms on the calling thread per tick and
    caused visible UI stutter."""
    global _NVSMI_OK
    if _NVSMI_OK is False:
        return None
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        r = subprocess.run(
            ['nvidia-smi', '--query-gpu=power.draw', '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=2, startupinfo=si)
        out = (r.stdout or '').strip().splitlines()
        if out:
            _NVSMI_OK = True
            return float(out[0].strip())
        _NVSMI_OK = False
    except Exception:
        _NVSMI_OK = False
    return None

def _battery_discharge_w():
    """Return discharge wattage from battery (positive value), or None.
    Uses GetSystemPowerStatus + per-battery WMI if available."""
    try:
        import ctypes.wintypes as _wt
        class SPS(ctypes.Structure):
            _fields_ = [('ACLineStatus', ctypes.c_ubyte),
                        ('BatteryFlag', ctypes.c_ubyte),
                        ('BatteryLifePercent', ctypes.c_ubyte),
                        ('SystemStatusFlag', ctypes.c_ubyte),
                        ('BatteryLifeTime', _wt.DWORD),
                        ('BatteryFullLifeTime', _wt.DWORD)]
        sps = SPS()
        if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(sps)):
            return None
        if sps.ACLineStatus == 1:
            return None  # on AC, can't read discharge
        # Walk WMI Win32_Battery for EstimatedRunTime + DesignCapacity
        # to compute rate. Simpler: psutil already exposes secsleft.
        b = psutil.sensors_battery()
        if not b or b.power_plugged:
            return None
        # Without instantaneous discharge rate, we can't compute exact watts.
        # Return None so the estimate path is used instead.
    except Exception:
        return None
    return None

def get_power_estimate(cpu_util, gpu_util, cpu_name='', gpu_name='', nvidia_w=None):
    """Return {'cpu': float, 'gpu': float, 'total': float, 'source': str}.

    cpu_util, gpu_util are percentages (0..100). source is one of:
      'nvml'      — GPU value came from nvidia-smi (exact); CPU estimated
      'battery'   — battery discharge rate (laptops); whole system
      'estimate'  — TDP × utilisation (~15% accuracy)
    nvidia_w: cached watt reading from _SlowPoller (avoids blocking the main thread).
    """
    cpu_tdp = get_cpu_tdp_w(cpu_name)
    gpu_tdp = get_gpu_tdp_w(gpu_name)
    # idle baseline: ~10-15% of TDP for CPU, ~8-12% for GPU (PCIe + memory)
    cpu_idle = cpu_tdp * 0.12
    gpu_idle = gpu_tdp * 0.10
    cpu_w = cpu_idle + (cpu_tdp - cpu_idle) * max(0.0, min(100.0, float(cpu_util or 0))) / 100.0
    nvml = nvidia_w  # pre-fetched by _SlowPoller; never blocks the main thread
    if nvml is not None:
        return {'cpu': cpu_w, 'gpu': nvml, 'total': cpu_w + nvml, 'source': 'nvml',
                'cpu_tdp': cpu_tdp, 'gpu_tdp': gpu_tdp}
    batt = _battery_discharge_w()
    if batt is not None:
        # whole-system; expose as 'total', leave components blank
        return {'cpu': None, 'gpu': None, 'total': batt, 'source': 'battery',
                'cpu_tdp': cpu_tdp, 'gpu_tdp': gpu_tdp}
    gpu_w = gpu_idle + (gpu_tdp - gpu_idle) * max(0.0, min(100.0, float(gpu_util or 0))) / 100.0
    return {'cpu': cpu_w, 'gpu': gpu_w, 'total': cpu_w + gpu_w, 'source': 'estimate',
            'cpu_tdp': cpu_tdp, 'gpu_tdp': gpu_tdp}

def get_gpu_name():
    """Return the primary discrete GPU name from the display adapter registry."""
    candidates = []
    base = r'SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}'
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base)
        i = 0
        while True:
            try: sub = winreg.EnumKey(k, i); i += 1
            except OSError: break
            if not sub.isdigit(): continue
            try:
                sk = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base + '\\' + sub)
                try:
                    name, _ = winreg.QueryValueEx(sk, 'DriverDesc')
                    # try to read the qwMemorySize so we can rank by VRAM
                    mem = 0
                    for vn in ('HardwareInformation.qwMemorySize',
                               'HardwareInformation.MemorySize'):
                        try:
                            v, _ = winreg.QueryValueEx(sk, vn)
                            if isinstance(v, bytes):
                                v = int.from_bytes(v, 'little')
                            mem = max(mem, int(v))
                            break
                        except (FileNotFoundError, OSError, ValueError):
                            continue
                    candidates.append((name, mem))
                finally:
                    winreg.CloseKey(sk)
            except (FileNotFoundError, OSError):
                continue
        winreg.CloseKey(k)
    except OSError:
        pass
    # Prefer the adapter with the largest VRAM (i.e. the discrete one)
    candidates.sort(key=lambda x: x[1], reverse=True)
    for name, _mem in candidates:
        # skip pure-iGPU labels if a discrete option exists
        if name:
            return name
    return ''

# ── Live bottleneck analysis (v2.8) ────────────────────────────────────
# Identify which component is the current limiting factor, using only the OS
# performance metrics the widget already gathers. This is *live* load analysis
# (which resource is pegged right now), NOT a static "your CPU is weaker than
# your GPU" benchmark score — that needs a hardware database and can't be
# derived from the OS.
def analyze_bottleneck(cpu, percpu, gpu, ram, vram_pct, disk_active):
    """Return the live limiting component as a dict.

    Inputs are smoothed 0-100 percentages; any may be None when unavailable.
    `percpu` is the per-core utilisation list (catches single-thread loads
    that hide behind a low average). Returns:
        {'key':     'cpu'|'gpu'|'ram'|'vram'|'disk'|'balanced'|'idle',
         'load':    float | None,   # the limiter's utilisation %
         'metrics': str}            # e.g. "CPU 98%  ·  GPU 61%  ·  RAM 44%"
    """
    def _n(x):
        return None if x is None else max(0.0, min(100.0, float(x)))
    cpu = _n(cpu); gpu = _n(gpu); ram = _n(ram)
    vram_pct = _n(vram_pct); disk_active = _n(disk_active)
    max_core = max(percpu) if percpu else None

    # one-line metric summary for the UI
    bits = []
    if cpu is not None:         bits.append(f'CPU {cpu:.0f}%')
    if gpu is not None:         bits.append(f'GPU {gpu:.0f}%')
    if ram is not None:         bits.append(f'RAM {ram:.0f}%')
    if vram_pct is not None:    bits.append(f'VRAM {vram_pct:.0f}%')
    if disk_active is not None: bits.append(f'Disk {disk_active:.0f}%')
    metrics = '  ·  '.join(bits)

    # effective CPU load: a single pegged core bottlenecks too (single-thread
    # games sit at ~100% on one core while the average looks low)
    cpu_eff = cpu
    if cpu_eff is not None and max_core is not None:
        cpu_eff = max(cpu_eff, max_core)

    # idle: nothing is really working and memory isn't tight
    busy = any(v is not None and v >= 20 for v in (cpu_eff, gpu, disk_active))
    if (not busy and (ram is None or ram < 85)
            and (vram_pct is None or vram_pct < 90)):
        return {'key': 'idle', 'load': None, 'metrics': metrics}

    # memory exhaustion first — it causes the worst stutter / swapping
    if vram_pct is not None and vram_pct >= 95:
        return {'key': 'vram', 'load': vram_pct, 'metrics': metrics}
    if ram is not None and ram >= 90:
        return {'key': 'ram', 'load': ram, 'metrics': metrics}
    # disk I/O wait
    if disk_active is not None and disk_active >= 85:
        return {'key': 'disk', 'load': disk_active, 'metrics': metrics}
    # GPU-bound: GPU pegged while the CPU still has headroom (classic gaming)
    if gpu is not None and gpu >= 97 and (cpu_eff is None or cpu_eff < 90):
        return {'key': 'gpu', 'load': gpu, 'metrics': metrics}
    # CPU-bound: whole CPU saturated or a single thread maxed out
    if cpu_eff is not None and (cpu_eff >= 90
                                or (max_core is not None and max_core >= 98)):
        return {'key': 'cpu', 'load': cpu_eff, 'metrics': metrics}
    # GPU pegged with the CPU also high → the GPU is still the wall
    if gpu is not None and gpu >= 97:
        return {'key': 'gpu', 'load': gpu, 'metrics': metrics}
    # everything has headroom
    return {'key': 'balanced', 'load': None, 'metrics': metrics}

# ── System Info collector (v2.7) ───────────────────────────────────────
# Gathers a comprehensive read-only snapshot of the machine for display in
# the "System" tab. No admin needed; falls back gracefully when a field
# isn't available.

def _wmi_query(cls, *cols):
    """Lightweight WMI via PowerShell (no admin needed). Returns list of dicts."""
    try:
        attrs = ','.join(cols) if cols else '*'
        cmd = ['powershell', '-NoProfile', '-NonInteractive', '-Command',
               f"Get-CimInstance -ClassName {cls} | Select-Object {attrs} | ConvertTo-Json -Compress -Depth 2"]
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # 20 s (not 6 s): on some machines the WMI/CIM subsystem is "cold" and
        # the *first* Get-CimInstance can take 10-12 s to warm up. A short
        # timeout killed that first query, so the whole System tab came back
        # empty. Once warmed, subsequent queries return in well under a second.
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20, startupinfo=si)
        if not r.stdout: return []
        data = json.loads(r.stdout)
        return data if isinstance(data, list) else [data]
    except Exception:
        return []

def _wmi_batch():
    """Fetch every system-info CIM class in ONE PowerShell process.

    Spawning a separate PowerShell per class is punishingly slow on some
    laptops — each launch costs ~5-7 s, so the ~10 classes the System tab
    needs added up to ~70 s. Running them all in a single invocation pays
    that startup cost exactly once (~10 s total). ReleaseDate is formatted
    to a plain yyyy-MM-dd string here so the CIM /Date(…)/ wrapper never
    reaches Python. Returns {key: [rows…]} with [] for anything that failed.
    """
    keys = ('cpu', 'mem', 'gpu', 'os', 'cs', 'mobo', 'bios',
            'audio', 'optical', 'battery', 'monitors', 'drives', 'tpm',
            'memarray', 'activation', 'tpmpnp')
    empty = {k: [] for k in keys}
    ps = (
        "$ErrorActionPreference='SilentlyContinue';$o=[ordered]@{};"
        "$o['cpu']=@(Get-CimInstance Win32_Processor|Select-Object Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed,L2CacheSize,L3CacheSize,SocketDesignation,Manufacturer,VirtualizationFirmwareEnabled);"
        "$o['mem']=@(Get-CimInstance Win32_PhysicalMemory|Select-Object Capacity,Speed,Manufacturer,PartNumber,DeviceLocator,SMBIOSMemoryType,ConfiguredClockSpeed);"
        "$o['memarray']=@(Get-CimInstance Win32_PhysicalMemoryArray|Select-Object MemoryDevices,MaxCapacity,MaxCapacityEx);"
        "$o['gpu']=@(Get-CimInstance Win32_VideoController|Select-Object Name,AdapterRAM,DriverVersion,CurrentHorizontalResolution,CurrentVerticalResolution,CurrentRefreshRate,VideoProcessor,AdapterCompatibility,CurrentBitsPerPixel,@{n='DriverDate';e={if($_.DriverDate){$_.DriverDate.ToString('yyyy-MM-dd')}else{''}}});"
        "$o['os']=@(Get-CimInstance Win32_OperatingSystem|Select-Object Caption,Version,BuildNumber,OSArchitecture,@{n='InstallDate';e={if($_.InstallDate){$_.InstallDate.ToString('yyyy-MM-dd')}else{''}}});"
        "$o['activation']=@(Get-CimInstance SoftwareLicensingProduct -Filter \"ApplicationID='55c92734-d682-4d71-983e-d6ec3f16059f' AND PartialProductKey IS NOT NULL\"|Select-Object LicenseStatus,Description);"
        "$o['cs']=@(Get-CimInstance Win32_ComputerSystem|Select-Object Manufacturer,Model,SystemFamily,SystemType,PCSystemType,Name,UserName,Domain,PartOfDomain,Workgroup);"
        "$o['mobo']=@(Get-CimInstance Win32_BaseBoard|Select-Object Manufacturer,Product,Version,SerialNumber);"
        "$o['bios']=@(Get-CimInstance Win32_BIOS|Select-Object Manufacturer,SMBIOSBIOSVersion,@{n='ReleaseDate';e={if($_.ReleaseDate){$_.ReleaseDate.ToString('yyyy-MM-dd')}else{''}}});"
        "$o['audio']=@(Get-CimInstance Win32_SoundDevice|Select-Object Name,Manufacturer,Status);"
        "$o['optical']=@(Get-CimInstance Win32_CDROMDrive|Select-Object Name,Manufacturer,MediaType,Drive);"
        "$o['battery']=@(Get-CimInstance Win32_Battery|Select-Object Name,Chemistry,DesignVoltage);"
        "$o['drives']=@(Get-CimInstance Win32_DiskDrive|Select-Object Model,Size,InterfaceType,MediaType,Partitions,Status);"
        "$o['tpm']=@(Get-CimInstance -Namespace root/cimv2/Security/MicrosoftTpm -ClassName Win32_Tpm|Select-Object IsEnabled_InitialValue,IsActivated_InitialValue,SpecVersion,ManufacturerIdTxt);"
        "$o['tpmpnp']=@(Get-CimInstance Win32_PnPEntity -Filter \"Name LIKE 'Trusted Platform Module%'\"|Select-Object Name);"
        "$o['monitors']=@(Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorID|Select-Object ManufacturerName,UserFriendlyName,ProductCodeID,YearOfManufacture);"
        "$o|ConvertTo-Json -Depth 4 -Compress"
    )
    try:
        cmd = ['powershell', '-NoProfile', '-NonInteractive', '-Command', ps]
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # 60 s: the very first (cold) call after boot can be slow, especially
        # while the widget's other background probes are running. A timeout
        # here would drop every WMI-based section at once, so we err generous —
        # this runs off the UI thread behind a spinner, so a long worst case is
        # invisible in the common (warm, ~10 s) path.
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, startupinfo=si)
        if not r.stdout:
            return empty
        data = json.loads(r.stdout)
        out = {}
        for k in keys:
            v = data.get(k)
            if v is None:
                v = []
            elif not isinstance(v, list):
                v = [v]
            out[k] = v
        return out
    except Exception:
        return empty

def _reg_bios_info():
    """Motherboard / BIOS / system identity straight from the registry — fast,
    admin-free and always available. Used as a fallback because the WMI batch
    can intermittently return these classes empty under load."""
    out = {}
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r'HARDWARE\DESCRIPTION\System\BIOS')
        def _g(name):
            try:
                v, _ = winreg.QueryValueEx(k, name)
                return str(v).strip()
            except OSError:
                return ''
        out = {
            'bb_mfr': _g('BaseBoardManufacturer'),
            'bb_product': _g('BaseBoardProduct'),
            'bb_version': _g('BaseBoardVersion'),
            'bios_vendor': _g('BIOSVendor'),
            'bios_version': _g('BIOSVersion'),
            'bios_date': _g('BIOSReleaseDate'),
            'sys_mfr': _g('SystemManufacturer'),
            'sys_product': _g('SystemProductName'),
            'sys_family': _g('SystemFamily'),
        }
        winreg.CloseKey(k)
    except OSError:
        pass
    return out

def _human_bytes(n):
    n = float(n or 0)
    for u in ('B','KB','MB','GB','TB','PB'):
        if n < 1024: return f'{n:.1f} {u}' if u != 'B' else f'{int(n)} {u}'
        n /= 1024
    return f'{n:.1f} EB'

def _uptime_str():
    try:
        secs = int(time.time() - psutil.boot_time())
        d, r = divmod(secs, 86400); h, r = divmod(r, 3600); m, _ = divmod(r, 60)
        if d: return f'{d}d {h}h {m}m'
        if h: return f'{h}h {m}m'
        return f'{m}m'
    except Exception:
        return '—'

def collect_system_info():
    """Snapshot of CPU/RAM/GPU/OS/Disk/Network info. Best-effort."""
    out = {'cpu': {}, 'ram': {}, 'gpu': [], 'os': {}, 'disks': [], 'net': [],
           'mobo': {}, 'bios': {}, 'audio': [], 'monitors': [], 'optical': [],
           'machine': {}, 'battery': {}, 'drives': [], 'security': {},
           'net_info': {}}
    # One PowerShell process fetches every CIM class at once (see _wmi_batch);
    # doing them one-by-one cost ~70 s on slower laptops.
    W = _wmi_batch()
    # WMI can return some classes empty under load. mem/mobo/cs should always
    # exist on a real PC — if any came back empty, run once more and merge the
    # two results (fill blanks) so sections like RAM speed don't vanish.
    if not (W.get('mem') and W.get('mobo') and W.get('cs')):
        W2 = _wmi_batch()
        for _k in list(W):
            if not W.get(_k) and W2.get(_k):
                W[_k] = W2[_k]
    # SMBIOS-based classes (esp. Win32_PhysicalMemory) can come back empty from
    # the big combined batch under load even though a small dedicated query
    # succeeds. Fall back to those so RAM speed/type never go missing.
    if not W.get('mem'):
        W['mem'] = _wmi_query('Win32_PhysicalMemory', 'Capacity', 'Speed',
                              'Manufacturer', 'PartNumber', 'DeviceLocator',
                              'SMBIOSMemoryType', 'ConfiguredClockSpeed')
    if not W.get('memarray'):
        W['memarray'] = _wmi_query('Win32_PhysicalMemoryArray', 'MemoryDevices',
                                   'MaxCapacity', 'MaxCapacityEx')
    # Registry copy of motherboard / BIOS / system identity — always available,
    # so these sections survive even if WMI returns them empty under load.
    REG = _reg_bios_info()
    # ── Machine (make / model — e.g. "HP Laptop 15-bw0xx") ──
    try:
        cs = W['cs']
        if cs:
            c = cs[0]
            PC_TYPE = {1: 'Desktop', 2: 'Laptop', 3: 'Workstation',
                       4: 'Enterprise Server', 5: 'SOHO Server',
                       6: 'Appliance PC', 7: 'Performance Server', 8: 'Tablet'}
            # UserName comes as DOMAIN\user — show just the user part
            user = str(c.get('UserName', '') or '').strip()
            if '\\' in user: user = user.split('\\')[-1]
            out['machine'] = {
                'manufacturer': str(c.get('Manufacturer', '') or '').strip(),
                'model': str(c.get('Model', '') or '').strip(),
                'family': str(c.get('SystemFamily', '') or '').strip(),
                'type': str(c.get('SystemType', '') or '').strip(),
                'form': PC_TYPE.get(c.get('PCSystemType'), ''),
                'name': str(c.get('Name', '') or '').strip(),
                'user': user,
            }
            if c.get('PartOfDomain'):
                out['machine']['domain'] = str(c.get('Domain', '') or '').strip()
            else:
                out['machine']['workgroup'] = str(c.get('Workgroup', '') or '').strip()
        # registry fallback when WMI ComputerSystem came back empty
        if not out['machine'].get('model') and REG.get('sys_product'):
            out['machine'].update({
                'manufacturer': out['machine'].get('manufacturer') or REG.get('sys_mfr', ''),
                'model': REG['sys_product'],
                'family': out['machine'].get('family') or REG.get('sys_family', ''),
            })
    except Exception: pass
    # ── Physical drives (SSD/HDD model + size) ──
    try:
        for d in W['drives']:
            model = str(d.get('Model', '') or '').strip()
            if not model: continue
            size = int(d.get('Size') or 0)
            bus = str(d.get('InterfaceType', '') or '').strip()
            # infer SSD vs HDD from the model string (Win32 MediaType is vague)
            ml = model.lower()
            kind = 'SSD' if ('ssd' in ml or 'nvme' in ml) else ''
            out['drives'].append({
                'model': model, 'size': size, 'bus': bus, 'kind': kind,
                'status': str(d.get('Status', '') or '').strip(),
            })
    except Exception: pass
    try:
        cpu = W['cpu']
        if cpu:
            c = cpu[0]
            out['cpu'] = {
                'name': str(c.get('Name','') or '').strip(),
                'manufacturer': c.get('Manufacturer',''),
                'cores': c.get('NumberOfCores'),
                'threads': c.get('NumberOfLogicalProcessors'),
                'base_mhz': c.get('MaxClockSpeed'),
                'l2_kb': c.get('L2CacheSize'),
                'l3_kb': c.get('L3CacheSize'),
                'socket': c.get('SocketDesignation',''),
                'virt': c.get('VirtualizationFirmwareEnabled'),
            }
        else:
            # WMI unavailable — fall back to the registry + psutil so the CPU
            # section still shows name / core count / clock.
            out['cpu'] = {
                'name': get_cpu_name(),
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
            }
        try:
            f = psutil.cpu_freq()
            if f:
                out['cpu']['current_mhz'] = int(f.current) or None
                if not out['cpu'].get('base_mhz'):
                    out['cpu']['base_mhz'] = int(f.max) or None
        except Exception: pass
    except Exception: pass
    try:
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()
        out['ram'] = {'total': vm.total, 'used': vm.used, 'free': vm.available,
                      'percent': vm.percent,
                      'swap_total': sm.total, 'swap_used': sm.used}
        mods = W['mem']
        out['ram']['modules'] = [{
            'capacity': int(m.get('Capacity', 0) or 0),
            # ConfiguredClockSpeed is the actual running speed; Speed is rated
            'speed': m.get('ConfiguredClockSpeed') or m.get('Speed'),
            'mfr': str(m.get('Manufacturer','') or '').strip(),
            'part': str(m.get('PartNumber','') or '').strip(),
            'slot': m.get('DeviceLocator',''),
        } for m in mods]
        # memory generation (DDR3/DDR4/DDR5) from SMBIOSMemoryType
        _DDR = {20: 'DDR', 21: 'DDR2', 24: 'DDR3', 26: 'DDR4', 34: 'DDR5',
                22: 'DDR2 FB-DIMM', 25: 'DDR3'}
        if mods:
            out['ram']['type'] = _DDR.get(mods[0].get('SMBIOSMemoryType'), '')
        # slot count + max supported capacity (Win32_PhysicalMemoryArray)
        ma = W['memarray']
        if ma:
            slots = ma[0].get('MemoryDevices')
            if slots: out['ram']['slots'] = int(slots)
            maxcap = ma[0].get('MaxCapacityEx') or ma[0].get('MaxCapacity')
            # MaxCapacity is in KB, MaxCapacityEx in KB too (per WMI docs)
            if maxcap: out['ram']['max_bytes'] = int(maxcap) * 1024
    except Exception: pass
    try:
        gpus = W['gpu']
        for g in gpus:
            name = str(g.get('Name','') or '').strip()
            if not name: continue
            out['gpu'].append({
                'name': name,
                'vram': int(g.get('AdapterRAM') or 0),
                'driver': g.get('DriverVersion'),
                'driver_date': str(g.get('DriverDate','') or '').strip(),
                'processor': str(g.get('VideoProcessor','') or '').strip(),
                'vendor': str(g.get('AdapterCompatibility','') or '').strip(),
                'bpp': g.get('CurrentBitsPerPixel'),
                'res': (g.get('CurrentHorizontalResolution'),
                        g.get('CurrentVerticalResolution')),
                'hz': g.get('CurrentRefreshRate'),
            })
        if not out['gpu']:
            # fallback: registry-based GPU name + VRAM only
            gn = get_gpu_name(); gv = get_total_vram_gb()
            if gn: out['gpu'].append({'name': gn, 'vram': int((gv or 0) * 1073741824)})
    except Exception: pass
    try:
        osinfo = W['os']
        if osinfo:
            o = osinfo[0]
            out['os'] = {
                'name': str(o.get('Caption','') or '').strip(),
                'version': o.get('Version'),
                'build': o.get('BuildNumber'),
                'arch': o.get('OSArchitecture'),
                'installed': str(o.get('InstallDate','') or '').strip(),
                'uptime': _uptime_str(),
            }
            # activation status (SoftwareLicensingProduct.LicenseStatus: 1=activated)
            act = W['activation']
            if act:
                out['os']['activated'] = (act[0].get('LicenseStatus') == 1)
        else:
            # WMI unavailable — fall back to the platform module.
            import platform as _pf
            ver = _pf.version()   # e.g. '10.0.26200'
            out['os'] = {
                'name': f"{_pf.system()} {_pf.release()}".strip(),
                'version': ver,
                'build': ver.split('.')[-1] if ver else '',
                'arch': _pf.machine(),
                'uptime': _uptime_str(),
            }
    except Exception: pass
    try:
        for p in psutil.disk_partitions(all=False):
            try:
                u = psutil.disk_usage(p.mountpoint)
                out['disks'].append({
                    'device': p.device.rstrip('\\'),
                    'fstype': p.fstype,
                    'total': u.total, 'used': u.used, 'free': u.free,
                    'percent': u.percent,
                })
            except Exception: continue
    except Exception: pass
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for name, addr_list in addrs.items():
            st = stats.get(name)
            if not st or not st.isup: continue
            ip4 = next((a.address for a in addr_list if a.family.name == 'AF_INET'), None)
            mac = next((a.address for a in addr_list if a.family.name == 'AF_LINK'), None)
            if not ip4 and not mac: continue
            out['net'].append({
                'name': name, 'ip': ip4, 'mac': mac,
                'speed_mbps': st.speed,
            })
    except Exception: pass
    # gateway / DNS / public IP for the active connection
    try:
        out['net_info'] = _net_extra()
    except Exception: pass
    # ── Battery (laptops) ──
    try:
        b = psutil.sensors_battery()
        if b is not None:
            secs = b.secsleft
            if secs in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN) or secs is None or secs < 0:
                left = ''
            else:
                h, m = divmod(int(secs) // 60, 60)
                left = f'{h}h {m}m'
            out['battery'] = {
                'percent': round(b.percent),
                'plugged': bool(b.power_plugged),
                'left': left,
            }
        # enrich with static WMI details (name / chemistry) when available
        bw = W['battery']
        if bw and out['battery'] is not None:
            CHEM = {1: 'Other', 2: 'Unknown', 3: 'Lead Acid', 4: 'NiCd',
                    5: 'NiMH', 6: 'Li-ion', 7: 'Zinc-air', 8: 'Li-polymer'}
            out.setdefault('battery', {})
            out['battery']['name'] = str(bw[0].get('Name', '') or '').strip()
            out['battery']['chemistry'] = CHEM.get(bw[0].get('Chemistry'), '')
            dv = bw[0].get('DesignVoltage')
            if dv: out['battery']['voltage'] = round(int(dv) / 1000.0, 2)  # mV → V
        # health / capacity / cycles (root/wmi, no admin)
        if out['battery'].get('percent') is not None:
            bh = _battery_health()
            if bh.get('full_mwh'):   out['battery']['full_mwh'] = bh['full_mwh']
            if bh.get('design_mwh'): out['battery']['design_mwh'] = bh['design_mwh']
            if bh.get('design_mwh') and bh.get('full_mwh'):
                out['battery']['health'] = round(bh['full_mwh'] / bh['design_mwh'] * 100)
            if bh.get('cycles'):     out['battery']['cycles'] = bh['cycles']
    except Exception: pass
    # ── Security (Secure Boot + TPM) ──
    try:
        sec = {}
        # Secure Boot state — readable from the registry without admin.
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r'SYSTEM\CurrentControlSet\Control\SecureBoot\State')
            val, _ = winreg.QueryValueEx(k, 'UEFISecureBootEnabled')
            winreg.CloseKey(k)
            sec['secure_boot'] = bool(val)
        except OSError:
            sec['secure_boot'] = None   # unknown (e.g. legacy BIOS boot)
        # Firmware mode: the SecureBoot control key only exists on UEFI systems.
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r'SYSTEM\CurrentControlSet\Control\SecureBoot\State')
            winreg.CloseKey(k)
            sec['firmware'] = 'UEFI'
        except OSError:
            sec['firmware'] = 'Legacy (BIOS)'
        # TPM (may be empty without elevation — then we just omit it)
        tpm = W['tpm']
        if tpm:
            t = tpm[0]
            sec['tpm_present'] = True
            sec['tpm_enabled'] = bool(t.get('IsEnabled_InitialValue'))
            sec['tpm_version'] = str(t.get('SpecVersion', '') or '').split(',')[0].strip()
        # non-admin fallback: the TPM also appears as a PnP device
        if not sec.get('tpm_present'):
            pnp = W.get('tpmpnp') or []
            if pnp:
                nm = str(pnp[0].get('Name', '') or '')
                sec['tpm_present'] = True
                ver = nm.replace('Trusted Platform Module', '').strip()
                if ver: sec['tpm_version'] = ver   # e.g. "2.0"
        out['security'] = sec
    except Exception: pass
    # ── Motherboard ──
    try:
        mb = W['mobo']
        if mb:
            m = mb[0]
            out['mobo'] = {
                'manufacturer': str(m.get('Manufacturer','') or '').strip(),
                'product': str(m.get('Product','') or '').strip(),
                'version': str(m.get('Version','') or '').strip(),
                'serial': str(m.get('SerialNumber','') or '').strip(),
            }
        # registry fallback when WMI BaseBoard came back empty
        if not (out['mobo'].get('product') or out['mobo'].get('manufacturer')) \
                and (REG.get('bb_product') or REG.get('bb_mfr')):
            out['mobo'] = {
                'manufacturer': REG.get('bb_mfr', ''),
                'product': REG.get('bb_product', ''),
                'version': REG.get('bb_version', ''),
                'serial': '',
            }
        bios = W['bios']
        if bios:
            b = bios[0]
            # ReleaseDate is already formatted as yyyy-MM-dd by _wmi_batch
            out['bios'] = {
                'manufacturer': str(b.get('Manufacturer','') or '').strip(),
                'version': str(b.get('SMBIOSBIOSVersion','') or '').strip(),
                'date': str(b.get('ReleaseDate','') or '').strip(),
            }
        # registry fallback for BIOS
        if not out['bios'].get('version') and REG.get('bios_version'):
            out['bios'] = {
                'manufacturer': REG.get('bios_vendor', ''),
                'version': REG.get('bios_version', ''),
                'date': REG.get('bios_date', ''),
            }
    except Exception: pass
    # ── Audio devices ──
    try:
        audios = W['audio']
        for a in audios:
            name = str(a.get('Name','') or '').strip()
            if not name: continue
            out['audio'].append({
                'name': name,
                'manufacturer': str(a.get('Manufacturer','') or '').strip(),
                'status': str(a.get('Status','') or '').strip(),
            })
    except Exception: pass
    # ── Monitors (via WmiMonitorID under root/wmi) ──
    try:
        data = W['monitors']
        if data:
            EDID_MFR = {  # 3-letter EDID codes → friendly name
                'AOC':'AOC','ACI':'Asus','AUS':'Asus','ACR':'Acer','AUO':'AU Optronics',
                'BNQ':'BenQ','BOE':'BOE','CMN':'Innolux','DEL':'Dell',
                'GSM':'LG','HPN':'HP','HSD':'HannStar','HWP':'HP',
                'IVM':'Iiyama','LEN':'Lenovo','LGD':'LG Display','MEI':'Panasonic',
                'MSI':'MSI','MTC':'Mitsubishi','NEC':'NEC','PHL':'Philips',
                'SAM':'Samsung','SEC':'Samsung','SHP':'Sharp','SNY':'Sony',
                'VSC':'ViewSonic',
            }
            for m in data:
                def _dec(lst):
                    try:
                        return ''.join(chr(c) for c in lst if isinstance(c, int) and 0 < c < 128).strip()
                    except Exception:
                        return ''
                mfr_raw = _dec(m.get('ManufacturerName') or [])
                mfr = EDID_MFR.get(mfr_raw, mfr_raw)
                model = _dec(m.get('UserFriendlyName') or [])
                code = _dec(m.get('ProductCodeID') or [])
                year = m.get('YearOfManufacture')
                if not (mfr or model or code): continue
                out['monitors'].append({
                    'manufacturer': mfr, 'model': model,
                    'code': code, 'year': year,
                })
    except Exception: pass
    # ── Optical drives ──
    try:
        opts = W['optical']
        for o in opts:
            name = str(o.get('Name','') or '').strip()
            if not name: continue
            out['optical'].append({
                'name': name,
                'manufacturer': str(o.get('Manufacturer','') or '').strip(),
                'media': str(o.get('MediaType','') or '').strip(),
                'drive': str(o.get('Drive','') or '').strip(),
            })
    except Exception: pass
    return out

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
    'show_weather': False, # weather removed
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
    'bar_labels': 'icon',    # bar metric marker: 'icon' (glyph) or 'text' (CPU/RAM/…)
    'tools_layout': 'list',  # Tools tab view: 'list' or 'grid' (responsive tiles)
    'sys_view': 'summary',   # System tab view: 'summary' (Speccy-like) or 'advanced'
    'check_updates': True,   # check GitHub for a newer release on launch
    'last_update_check': 0,  # epoch seconds of the last check (throttle)
    # ── earthquakes (v2.6) ──
    'quakes_on': False,      # earthquake alerts removed
    'quakes_emsc': True,     # EMSC (Europe-centric) source
    'quakes_usgs': True,     # USGS (global) source
    'quakes_min_mmi': 3.0,   # alert when felt MMI >= this (3 = subtle, 4 = noticeable, 5 = strong, 6 = severe)
    'quakes_min_mag': 2.5,   # pre-filter quakes below this magnitude
    'quakes_max_age_min': 30,  # ignore events older than this many minutes
    'quakes_max_dist_km': 100, # hide events farther than this from user
    'quakes_alert_min':   20,  # how long the bar dot stays lit (minutes)
    'quakes_toasts': True,   # show Windows toast on a felt quake
    'quakes_mute': False,    # silence everything (no toast, no dot)
    'quakes_lat': None,      # manual override (otherwise IP-derived)
    'quakes_lon': None,
    'quakes_seen': [],       # ids of already-alerted quakes (anti-spam)
    # ── power consumption (v2.7) ──
    'show_power': False,     # show estimated CPU+GPU power on the bar
    'power_unit': 'W',       # only 'W' for now (kW reserved for future)
    # ── customize: cell ordering ──
    'cell_order': None,      # None = use DEFAULT_CELL_ORDER; else list of ids
    'critical_last': True,   # always force the quake alert cell to the end
    'single_row_mode': 'percent',  # when stacked is OFF: 'percent' | 'detail'
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
REG_NAME = 'PulseDeck'
STARTUP_TASK_ID = 'PulseBarStartup'   # must match AppxManifest.xml (Store package identity)

def _is_msix():
    """True if we are running inside the MSIX (Store) container.
    The container exposes its full package name via the GetCurrentPackageFullName
    Win32 API; outside a package it returns APPMODEL_ERROR_NO_PACKAGE (15700)."""
    try:
        kernel32 = ctypes.windll.kernel32
        length = ctypes.c_uint32(0)
        rc = kernel32.GetCurrentPackageFullName(ctypes.byref(length), None)
        return rc != 15700   # any value except NO_PACKAGE means we're packaged
    except Exception:
        return False

def _startup_cmd():
    """The Run-key command that should launch THIS exe/script from its current
    location. Recomputed every launch so a moved portable .exe stays correct."""
    if getattr(sys, 'frozen', False):
        return f'"{sys.executable}"'
    script = os.path.abspath(__file__)
    pythonw = sys.executable.replace('python.exe', 'pythonw.exe')
    return f'"{pythonw}" "{script}"'

# ── MSIX StartupTask backend ──────────────────────────────────────────
# In the Store/MSIX container, the HKCU\...\Run registry key is virtualised
# and ignored by the shell at logon. The supported path is the
# desktop:Extension/startupTask declared in AppxManifest.xml. The manifest
# defaults to Enabled="true", so out-of-the-box the app runs at logon.
# Users manage startup the canonical Windows way: Settings -> Apps -> Startup.
# When the user clicks the startup item in our tray menu under MSIX we just
# open that page (the same pattern most Store apps use).

def _open_startup_settings():
    """Open Settings -> Apps -> Startup. MSIX-mode counterpart of toggling
    the Run-key. Works on Windows 10 1803+."""
    try:
        os.startfile('ms-settings:startupapps')
    except Exception:
        pass

def is_startup_enabled():
    # In MSIX mode startup is managed by Windows Settings, so we report False
    # here (the tray item below becomes an "Open settings..." link instead of
    # a checkbox). Outside MSIX, read the Run-key as before.
    if _is_msix():
        return False
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_READ)
        winreg.QueryValueEx(k, REG_NAME)
        winreg.CloseKey(k)
        return True
    except FileNotFoundError:
        return False

def set_startup(enable: bool):
    # In MSIX mode hand the user to Windows Settings; outside MSIX flip the
    # Run-key in the registry.
    if _is_msix():
        _open_startup_settings()
        return
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
    """Self-heal the registry Run-key entry for the non-Store build: if it is
    enabled but points to an old path (e.g. the portable .exe was moved),
    rewrite it. No-op inside the MSIX container (StartupTask manages itself)."""
    if _is_msix():
        return
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

# ── Tools: safe shortcuts to built-in Windows utilities (v2.8) ─────────
# Every entry just *opens* a tool Windows already ships — PulseDeck never
# changes a setting on its own. The three "action" items (flush DNS, clear
# Temp, empty Recycle Bin) are the only ones that do something, are 100%
# reversible-safe, and always ask for confirmation first. This keeps the
# feature fully Microsoft-Store compliant inside the MSIX sandbox.
def _sys32(name):
    return os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'System32', name)

def _silent_startupinfo():
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return si

def launch_tool(action):
    """Open a built-in Windows tool. `action` is (kind, target).
    settings/protocol URIs go through os.startfile; classic tools launch from
    System32 so the MSIX sandbox can't redirect the path. Returns True on
    success. Read-only: opens the tool, changes nothing."""
    kind, target = action
    try:
        if kind in ('settings', 'shell'):
            os.startfile(os.path.expandvars(target))
        elif kind == 'exe':
            subprocess.Popen([_sys32(target[0])] + list(target[1:]))
        elif kind == 'win':   # executable in the Windows dir, e.g. regedit.exe
            win = os.environ.get('WINDIR', r'C:\Windows')
            subprocess.Popen([os.path.join(win, target[0])] + list(target[1:]))
        elif kind == 'applet':
            subprocess.Popen([_sys32('control.exe'), target])
        elif kind == 'msc':
            subprocess.Popen([_sys32('mmc.exe'), _sys32(target)])
        else:
            return False
        return True
    except Exception:
        try:
            os.startfile(target if isinstance(target, str) else target[0])
            return True
        except Exception:
            return False

def _dir_size(path):
    total = 0
    for root, _dirs, files in os.walk(path):
        for f in files:
            try: total += os.path.getsize(os.path.join(root, f))
            except Exception: pass
    return total

def action_flush_dns():
    """ipconfig /flushdns — harmless, no admin needed."""
    try:
        subprocess.run([_sys32('ipconfig.exe'), '/flushdns'],
                       startupinfo=_silent_startupinfo(), timeout=10,
                       capture_output=True)
        return True
    except Exception:
        return False

def action_clear_temp():
    """Delete what we can from %TEMP%; locked/in-use files are skipped.
    Returns bytes freed. Same scope as Disk Cleanup's temp pass."""
    import shutil
    base = os.environ.get('TEMP') or os.environ.get('TMP')
    if not base or not os.path.isdir(base):
        return 0
    freed = 0
    for name in os.listdir(base):
        p = os.path.join(base, name)
        try:
            if os.path.isfile(p) or os.path.islink(p):
                sz = os.path.getsize(p); os.remove(p); freed += sz
            elif os.path.isdir(p):
                sz = _dir_size(p); shutil.rmtree(p, ignore_errors=True); freed += sz
        except Exception:
            pass   # in use → leave it
    return freed

def action_empty_recyclebin():
    """SHEmptyRecycleBin on all drives, no extra prompts/sound."""
    try:
        SHERB_NOCONFIRMATION = 0x1; SHERB_NOPROGRESSUI = 0x2; SHERB_NOSOUND = 0x4
        ctypes.windll.shell32.SHEmptyRecycleBinW(
            None, None,
            SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND)
        return True
    except Exception:
        return False

def action_reset_gpu_driver():
    """Send Win + Ctrl + Shift + B — the Windows shortcut to reset the
    display driver. Briefly blacks the screen and beeps; the desktop redraws
    a moment later. Safe (no apps/data lost) and built into Windows."""
    try:
        u = ctypes.windll.user32
        KEYEVENTF_KEYUP = 0x0002
        VK_LWIN, VK_CTRL, VK_SHIFT, VK_B = 0x5B, 0x11, 0x10, 0x42
        for k in (VK_LWIN, VK_CTRL, VK_SHIFT, VK_B):
            u.keybd_event(k, 0, 0, 0)
        for k in (VK_B, VK_SHIFT, VK_CTRL, VK_LWIN):
            u.keybd_event(k, 0, KEYEVENTF_KEYUP, 0)
        return True
    except Exception:
        return False

def action_lock_screen():
    """Lock the workstation (same as Win+L)."""
    try:
        ctypes.windll.user32.LockWorkStation()
        return True
    except Exception:
        return False

def action_restart_explorer():
    """Kill and relaunch explorer.exe — refreshes the taskbar/desktop without
    a reboot. Useful when icons stop responding."""
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'],
                       startupinfo=_silent_startupinfo(), timeout=10,
                       capture_output=True)
        # Let the shell fully tear down so the relaunch reads registry changes
        # (e.g. the classic context-menu CLSID — a too-short wait raced Windows'
        # own auto-restart and the tweak didn't apply). Then start explorer only
        # if it hasn't come back on its own — a bare explorer.exe while the shell
        # is already running would just open a stray File Explorer window.
        time.sleep(2.0)
        try:
            tl = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq explorer.exe'],
                                startupinfo=_silent_startupinfo(), timeout=8,
                                capture_output=True, text=True)
            running = 'explorer.exe' in (tl.stdout or '').lower()
        except Exception:
            running = False
        if not running:
            try:
                subprocess.Popen([os.path.join(os.environ.get('WINDIR', r'C:\Windows'),
                                                'explorer.exe')])
            except Exception:
                try: os.startfile('explorer.exe')
                except Exception: pass
        return True
    except Exception:
        return False

# The shell CLSID that, when given an empty InprocServer32 default value,
# restores the classic (Windows 10) right-click context menu on Windows 11.
_CTX_CLSID = (r'Software\Classes\CLSID'
              r'\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}')

def is_classic_context():
    """True if the classic (Windows 10) right-click menu is currently on."""
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           _CTX_CLSID + r'\InprocServer32')
        winreg.CloseKey(k)
        return True
    except OSError:
        return False

def action_classic_context(enable):
    """Toggle the Windows 11 classic right-click menu (per-user, no admin).

    Enabling creates CLSID\\…\\InprocServer32 with an empty default value;
    disabling deletes the CLSID key so Windows 11's own menu returns. Explorer
    is restarted so the change takes effect right away."""
    try:
        if enable:
            k = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                 _CTX_CLSID + r'\InprocServer32')
            winreg.SetValueEx(k, '', 0, winreg.REG_SZ, '')
            winreg.CloseKey(k)
        else:
            # a key must be empty before it can be deleted → remove the child first
            for sub in (_CTX_CLSID + r'\InprocServer32', _CTX_CLSID):
                try: winreg.DeleteKey(winreg.HKEY_CURRENT_USER, sub)
                except OSError: pass
        action_restart_explorer()
        return True
    except Exception:
        return False

def action_hibernate():
    """Put the PC into hibernation. Falls back gracefully if hibernation is
    disabled in power settings."""
    try:
        ctypes.windll.powrprof.SetSuspendState(True, False, False)
        return True
    except Exception:
        return False

# catalog: (category_key, icon, [(tool_key, icon, (kind, target)), ...])
TOOLS_CATALOG = [
    ('cat_cleanup', '🧹', [
        ('t_diskcleanup', '🧽', ('exe', ['cleanmgr.exe'])),
        ('t_storage',     '💾', ('settings', 'ms-settings:storagesense')),
        ('t_optimize',    '🧩', ('exe', ['dfrgui.exe'])),
        ('t_apps',        '📦', ('settings', 'ms-settings:appsfeatures')),
        ('t_tempfolder',  '📂', ('shell', '%TEMP%')),
        ('t_cleartemp',   '✨', ('action', 'clear_temp')),
        ('t_recyclebin',  '🗑', ('action', 'empty_recyclebin')),
    ]),
    ('cat_diag', '🩺', [
        ('t_ramcheck',    '🧠', ('exe', ['mdsched.exe'])),
        ('t_taskmgr',     '📋', ('exe', ['taskmgr.exe'])),
        ('t_resmon',      '📈', ('exe', ['resmon.exe'])),
        ('t_msinfo',      'ℹ', ('exe', ['msinfo32.exe'])),
        ('t_reliability', '📊', ('exe', ['perfmon.exe', '/rel'])),
        ('t_dxdiag',      '🎮', ('exe', ['dxdiag.exe'])),
        ('t_gpureset',    '⚡', ('action', 'reset_gpu')),
    ]),
    ('cat_perf', '⚡', [
        ('t_power',       '🔋', ('applet', 'powercfg.cpl')),
        ('t_startup',     '🚀', ('settings', 'ms-settings:startupapps')),
        ('t_visualfx',    '🎚', ('exe', ['SystemPropertiesPerformance.exe'])),
        ('t_graphics',    '🖥', ('settings', 'ms-settings:display-advancedgraphics')),
        ('t_explorer',    '🔄', ('action', 'restart_explorer')),
        ('t_hibernate',   '🛌', ('action', 'hibernate')),
    ]),
    ('cat_net', '🌐', [
        ('t_dnsboost',    '🚀', ('action', 'dns_boost')),
        ('t_netstatus',   '📶', ('settings', 'ms-settings:network-status')),
        ('t_adapters',    '🔌', ('applet', 'ncpa.cpl')),
        ('t_flushdns',    '♻', ('action', 'flush_dns')),
        ('t_proxy',       '🔐', ('settings', 'ms-settings:network-proxy')),
        ('t_vpn',         '🛡', ('settings', 'ms-settings:network-vpn')),
    ]),
    ('cat_sys', '🛡', [
        ('t_update',      '⬇', ('settings', 'ms-settings:windowsupdate')),
        ('t_security',    '🛡', ('settings', 'windowsdefender:')),
        ('t_restore',     '⏮', ('exe', ['rstrui.exe'])),
        ('t_devmgr',      '🧷', ('msc', 'devmgmt.msc')),
        ('t_lock',        '🔒', ('action', 'lock_screen')),
        ('t_classicmenu', '🖱', ('action', 'classic_context')),
        ('t_sound',       '🔊', ('exe', ['mmsys.cpl'])),
        ('t_micpriv',     '🎤', ('settings', 'ms-settings:privacy-microphone')),
        ('t_campriv',     '📷', ('settings', 'ms-settings:privacy-webcam')),
    ]),
    ('superuser', '🛠', [
        ('su_god',      '👑', ('shell', 'shell:::{ED7BA470-8E54-465E-825C-99712043E01C}')),
        ('su_dev',      '🔧', ('settings', 'ms-settings:developers')),
        ('su_msconfig', '🧾', ('exe', ['msconfig.exe'])),
        ('su_regedit',  '📝', ('win', ['regedit.exe'])),
        ('su_gpedit',   '🧩', ('msc', 'gpedit.msc')),
        ('su_services', '🛎', ('msc', 'services.msc')),
        ('su_startup',  '🚀', ('shell', 'shell:startup')),
        ('su_sys32',    '📁', ('shell', r'%WINDIR%\System32')),
    ]),
]

# ── DNS Boost: benchmark popular resolvers, IPv4 + IPv6 (v2.8) ──────────
# Pure measurement — sends real DNS queries over UDP/53 and times the reply,
# like DNS Benchmark. PulseDeck never changes the system DNS itself (that
# needs admin and is blocked in the MSIX sandbox); it shows the fastest and
# lets the user switch via Windows' own network settings.
import struct as _struct

DNS_PROVIDERS = [
    ('Cloudflare',         ['1.1.1.1', '1.0.0.1'],
                           ['2606:4700:4700::1111', '2606:4700:4700::1001']),
    ('Google',             ['8.8.8.8', '8.8.4.4'],
                           ['2001:4860:4860::8888', '2001:4860:4860::8844']),
    ('Quad9',              ['9.9.9.9', '149.112.112.112'],
                           ['2620:fe::fe', '2620:fe::9']),
    ('OpenDNS',            ['208.67.222.222', '208.67.220.220'],
                           ['2620:119:35::35', '2620:119:53::53']),
    ('AdGuard',            ['94.140.14.14', '94.140.15.15'],
                           ['2a10:50c0::ad1:ff', '2a10:50c0::ad2:ff']),
    ('Cloudflare Malware', ['1.1.1.2', '1.0.0.2'],
                           ['2606:4700:4700::1112', '2606:4700:4700::1002']),
    ('Quad9 Unsecured',    ['9.9.9.10', '149.112.112.10'],
                           ['2620:fe::10', '2620:fe::fe:10']),
    ('DNS.SB',             ['185.222.222.222', '45.11.45.11'],
                           ['2a09::', '2a11::']),
    ('Mullvad',            ['194.242.2.2', '194.242.2.3'],
                           ['2a07:e340::2', '2a07:e340::3']),
    ('ControlD',           ['76.76.2.0', '76.76.10.0'],
                           ['2606:1a40::', '2606:1a40:1::']),
    ('CleanBrowsing',      ['185.228.168.9', '185.228.169.9'],
                           ['2a0d:2a00:1::2', '2a0d:2a00:2::2']),
    ('Yandex',             ['77.88.8.8', '77.88.8.1'],
                           ['2a02:6b8::feed:0ff', '2a02:6b8:0:1::feed:0ff']),
    ('Verisign',           ['64.6.64.6', '64.6.65.6'],
                           ['2620:74:1b::1:1', '2620:74:1c::2:2']),
    ('Comodo Secure',      ['8.26.56.26', '8.20.247.20'], ['']),
    ('Level3',             ['4.2.2.1', '4.2.2.2'], ['']),
]

def _dns_query_packet(hostname, qtype=1):
    """Build a minimal DNS query packet. Returns (transaction_id, bytes)."""
    tid = random.randint(0, 0xFFFF)
    header = _struct.pack('>HHHHHH', tid, 0x0100, 1, 0, 0, 0)  # RD set
    q = b''.join(bytes([len(p)]) + p.encode('ascii')
                 for p in hostname.split('.')) + b'\x00'
    q += _struct.pack('>HH', qtype, 1)   # QTYPE, QCLASS=IN
    return tid, header + q

def dns_latency(server, is_ipv6=False, qtype=1, timeout=1.0,
                host='www.microsoft.com'):
    """One DNS query latency in ms, or None on timeout/error."""
    tid, pkt = _dns_query_packet(host, qtype)
    fam = socket.AF_INET6 if is_ipv6 else socket.AF_INET
    s = socket.socket(fam, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        t0 = time.perf_counter()
        s.sendto(pkt, (server, 53))
        data, _ = s.recvfrom(512)
        dt = (time.perf_counter() - t0) * 1000.0
        if len(data) >= 2 and _struct.unpack('>H', data[:2])[0] == tid:
            return dt
        return None
    except Exception:
        return None
    finally:
        try: s.close()
        except Exception: pass

def benchmark_dns(server, is_ipv6=False, rounds=4):
    """Median latency (ms) over a few queries; None if every query failed."""
    vals = []
    for _ in range(rounds):
        ms = dns_latency(server, is_ipv6)
        if ms is not None:
            vals.append(ms)
    if not vals:
        return None
    vals.sort()
    return vals[len(vals) // 2]

def _ipv6_available():
    """True if the machine can reach any well-known IPv6 resolver. Probes a few
    so a single down/slow resolver doesn't hide IPv6 entirely."""
    if not socket.has_ipv6:
        return False
    for ip in ('2606:4700:4700::1111', '2001:4860:4860::8888',
               '2620:fe::fe', '2a10:50c0::ad1:ff'):
        if dns_latency(ip, is_ipv6=True, timeout=1.5) is not None:
            return True
    return False

def get_current_dns():
    """The IPv4 DNS server(s) the machine is currently using, so the user can
    compare their latency against the public resolvers. Best-effort."""
    try:
        cmd = ['powershell', '-NoProfile', '-NonInteractive', '-Command',
               '(Get-DnsClientServerAddress -AddressFamily IPv4).ServerAddresses']
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=6,
                           startupinfo=_silent_startupinfo())
        out = []
        for line in (r.stdout or '').splitlines():
            a = line.strip()
            if (a and a not in out and not a.startswith('127.')
                    and not a.startswith('169.254.') and ':' not in a):
                out.append(a)
        return out
    except Exception:
        return []

def _net_extra():
    """Active connection's default gateway, DNS servers and public IP.
    Best-effort — each part is independent and degrades to blank."""
    out = {'gateway': '', 'dns': [], 'public_ip': ''}
    try:
        cmd = ['powershell', '-NoProfile', '-NonInteractive', '-Command',
               "(Get-CimInstance Win32_NetworkAdapterConfiguration -Filter "
               "'IPEnabled=True' | Where-Object {$_.DefaultIPGateway} | "
               "Select-Object -First 1).DefaultIPGateway"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=8,
                           startupinfo=_silent_startupinfo())
        for line in (r.stdout or '').splitlines():
            a = line.strip()
            if a and ':' not in a:      # first IPv4 gateway
                out['gateway'] = a; break
    except Exception: pass
    try:
        out['dns'] = get_current_dns()
    except Exception: pass
    try:
        import urllib.request
        req = urllib.request.Request('https://api.ipify.org',
                                     headers={'User-Agent': 'PulseDeck'})
        out['public_ip'] = urllib.request.urlopen(req, timeout=4).read().decode().strip()
    except Exception: pass
    return out

def _battery_health():
    """Battery design vs full-charge capacity (→ wear %) and cycle count, from
    the root/wmi battery classes. No admin. Any field may be missing per laptop."""
    out = {}
    try:
        cmd = ['powershell', '-NoProfile', '-NonInteractive', '-Command',
               "$d=(Get-CimInstance -Namespace root/wmi -ClassName BatteryStaticData -EA 0).DesignedCapacity;"
               "$f=(Get-CimInstance -Namespace root/wmi -ClassName BatteryFullChargedCapacity -EA 0).FullChargedCapacity;"
               "$c=(Get-CimInstance -Namespace root/wmi -ClassName BatteryCycleCount -EA 0).CycleCount;"
               "[pscustomobject]@{design=$d;full=$f;cycles=$c}|ConvertTo-Json -Compress"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=8,
                           startupinfo=_silent_startupinfo())
        if r.stdout:
            d = json.loads(r.stdout)
            def _num(v):
                if isinstance(v, list): v = v[0] if v else None
                try: return int(v)
                except (TypeError, ValueError): return None
            out['design_mwh'] = _num(d.get('design'))
            out['full_mwh'] = _num(d.get('full'))
            out['cycles'] = _num(d.get('cycles'))
    except Exception: pass
    return out

# ── Diagnostics: hardware self-test (v2.8.2) ───────────────────────────
# Runs every read-only hardware probe and collects what worked / what failed.
# Users hit "Copy" and paste the report into a bug ticket so we can fix things
# on hardware we don't own (e.g. the AMD VRAM bug was a single missing data
# point that this report would have caught at first launch).
def run_diagnostics():
    out = []
    def probe(label, fn):
        try:
            v = fn()
            ok = v not in (None, '', [], 0) and not isinstance(v, bool) or v is True
            out.append((label, 'OK' if ok else 'EMPTY', repr(v)[:120]))
        except Exception as e:
            out.append((label, 'FAIL', f'{type(e).__name__}: {e}'[:120]))
    # CPU / RAM / battery via psutil
    probe('psutil cpu_percent',        lambda: psutil.cpu_percent(0.05))
    probe('psutil cpu_count',          lambda: psutil.cpu_count())
    probe('psutil cpu_freq',           lambda: getattr(psutil.cpu_freq(), 'current', None))
    probe('psutil virtual_memory',     lambda: psutil.virtual_memory().percent)
    probe('psutil sensors_battery',    lambda: getattr(psutil.sensors_battery(), 'percent', None))
    probe('psutil net_io_counters',    lambda: psutil.net_io_counters().bytes_sent)
    probe('psutil disk_io_counters',   lambda: psutil.disk_io_counters().read_bytes)
    probe('psutil disk_partitions',    lambda: len(psutil.disk_partitions(all=False)))
    # Registry / Win32 hardware identity
    probe('CPU name (registry)',       lambda: get_cpu_name())
    probe('GPU name (registry)',       lambda: get_gpu_name())
    probe('VRAM total (registry GB)',  lambda: get_total_vram_gb())
    probe('Taskbar info',              lambda: get_taskbar_info())
    # PDH counters
    probe('CpuFreq PDH',               lambda: CpuFreq().read_ghz())
    def _gpu_probe():
        g = GpuCounter()
        return g.read() if g.ok else None
    probe('GpuCounter PDH',            _gpu_probe)
    # Optional/external
    probe('nvidia-smi power',          _nvidia_smi_power)
    probe('Battery discharge W',       _battery_discharge_w)
    probe('WMI Win32_Processor',       lambda: _wmi_query('Win32_Processor', 'Name')[:1])
    probe('Current DNS',               get_current_dns)
    return out

def format_diagnostics(rows):
    head = (f'PulseDeck {VERSION} — diagnostics\n'
            f'OS: {sys.platform}  ·  Python: {sys.version.split()[0]}\n'
            f'{"-"*68}\n')
    lines = [f'{lbl:30}  {status:5}  {detail}' for lbl, status, detail in rows]
    fails = sum(1 for _, s, _ in rows if s != 'OK')
    summary = f'\n{"-"*68}\n{len(rows) - fails}/{len(rows)} probes OK  ·  {fails} failing'
    return head + '\n'.join(lines) + summary

# ── Weather (Open-Meteo, free, no API key) ─────────────────────────────
def _http_json(url, timeout=6):
    req = urllib.request.Request(url, headers={'User-Agent': 'PulseDeck'})
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

# ── Earthquakes (EMSC + USGS, free, no API key) ────────────────────────
# Uses the Bakun-Wentworth model to estimate Modified Mercalli Intensity
# at the user's location, so we only alert on quakes that would actually
# be felt locally — not every distant quake anywhere in the country.

import math as _math

def _hypocentral_km(lat1, lon1, lat2, lon2, depth_km):
    """Great-circle surface distance + depth → hypocentral distance (km)."""
    R = 6371.0
    p1 = _math.radians(lat1); p2 = _math.radians(lat2)
    dp = _math.radians(lat2 - lat1); dl = _math.radians(lon2 - lon1)
    a = _math.sin(dp/2)**2 + _math.cos(p1) * _math.cos(p2) * _math.sin(dl/2)**2
    surf = 2 * R * _math.asin(_math.sqrt(a))
    return _math.sqrt(surf**2 + (depth_km or 10)**2)

def _felt_intensity_mmi(magnitude, hypocentral_km):
    """Estimate MMI at a site from M and hypocentral distance.
    Bakun & Wentworth (1997) intensity attenuation, clamped to [0, 12]."""
    R = max(1.0, hypocentral_km)
    mmi = 3.67 + 0.98 * magnitude - 1.10 * _math.log10(R) - 0.0033 * R
    return max(0.0, min(12.0, mmi))

def _mmi_label(mmi):
    """Friendly description of a MMI level."""
    if mmi < 2:   return 'imperceptible'
    if mmi < 3:   return 'barely felt'
    if mmi < 4:   return 'felt'
    if mmi < 5:   return 'widely felt'
    if mmi < 6:   return 'strong'
    if mmi < 7:   return 'very strong'
    if mmi < 8:   return 'severe'
    if mmi < 9:   return 'violent'
    return 'extreme'

def _emsc_recent(min_mag=2.5, limit=200):
    """Recent quakes from EMSC (FDSN-event JSON). Best-effort, returns list."""
    try:
        import datetime as _dt
        start = (_dt.datetime.utcnow() - _dt.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S')
        url = ('https://www.seismicportal.eu/fdsnws/event/1/query?'
               f'format=json&limit={limit}&minmag={min_mag}&start={start}')
        data = _http_json(url, timeout=8) or {}
        out = []
        for f in data.get('features', []):
            p = f.get('properties', {}) or {}
            g = f.get('geometry', {}) or {}
            coords = (g.get('coordinates') or [None, None, None])
            lon, lat, dep = coords[0], coords[1], coords[2] if len(coords) > 2 else 10
            try:
                mag = float(p.get('mag'))
                lat = float(lat); lon = float(lon)
                dep = float(dep) if dep is not None else 10.0
            except Exception:
                continue
            out.append({
                'id': str(f.get('id') or p.get('unid') or p.get('source_id') or ''),
                'mag': mag, 'lat': lat, 'lon': lon, 'depth': abs(dep),
                'time': p.get('time') or '',
                'region': p.get('flynn_region') or p.get('region') or '',
                'source': 'EMSC',
            })
        return out
    except Exception:
        return []

def _usgs_recent(min_mag=2.5):
    """Recent quakes from USGS (past hour, all M2.5+). Best-effort."""
    try:
        url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_hour.geojson'
        data = _http_json(url, timeout=8) or {}
        out = []
        for f in data.get('features', []):
            p = f.get('properties', {}) or {}
            g = f.get('geometry', {}) or {}
            coords = (g.get('coordinates') or [None, None, None])
            lon, lat, dep = coords[0], coords[1], coords[2] if len(coords) > 2 else 10
            try:
                mag = float(p.get('mag'))
                if mag < min_mag: continue
                lat = float(lat); lon = float(lon)
                dep = float(dep) if dep is not None else 10.0
            except Exception:
                continue
            out.append({
                'id': str(f.get('id') or ''),
                'mag': mag, 'lat': lat, 'lon': lon, 'depth': abs(dep),
                'time': p.get('time') or '',     # epoch ms
                'region': p.get('place') or '',
                'source': 'USGS',
            })
        return out
    except Exception:
        return []

def fetch_quakes(user_lat, user_lon, sources=('emsc', 'usgs'), min_mag=2.5):
    """Combine EMSC + USGS, annotate each with hypocentral distance, MMI
    and a friendly relative time. Returns a list sorted by time desc."""
    import datetime as _dt
    if user_lat is None or user_lon is None:
        return []
    all_q = []
    if 'emsc' in sources: all_q += _emsc_recent(min_mag=min_mag)
    if 'usgs' in sources: all_q += _usgs_recent(min_mag=min_mag)
    # de-dup by (rounded lat/lon/time/mag) — EMSC & USGS often list the same event
    seen = set()
    uniq = []
    for q in all_q:
        # time may be ISO string (EMSC) or epoch ms int (USGS); normalise to a
        # rounded second-bucket for de-dup
        t = q.get('time')
        if isinstance(t, (int, float)):
            t_key = int(t / 60000)   # minute bucket
        else:
            t_key = (str(t) or '')[:16]
        key = (round(q['lat'], 1), round(q['lon'], 1), round(q['mag'], 1), t_key)
        if key in seen: continue
        seen.add(key)
        uniq.append(q)
    now = _dt.datetime.utcnow()
    for q in uniq:
        q['dist_km'] = _hypocentral_km(user_lat, user_lon, q['lat'], q['lon'], q['depth'])
        q['mmi']     = _felt_intensity_mmi(q['mag'], q['dist_km'])
        q['mmi_label'] = _mmi_label(q['mmi'])
        # parse time → seconds ago
        t = q.get('time') or ''
        secs = None
        try:
            if isinstance(t, (int, float)):
                secs = (now - _dt.datetime.utcfromtimestamp(t / 1000.0)).total_seconds()
            elif t:
                s = t.replace('Z', '').replace('T', ' ').split('.')[0]
                secs = (now - _dt.datetime.fromisoformat(s)).total_seconds()
        except Exception:
            pass
        q['age_sec'] = secs if secs is not None and secs >= 0 else None
    uniq.sort(key=lambda q: q['age_sec'] if q['age_sec'] is not None else 1e12)
    return uniq

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
    PATH_UTIL      = r'\GPU Engine(*engtype_3D)\Utilization Percentage'
    PATH_MEM       = r'\GPU Process Memory(*)\Dedicated Usage'
    PATH_MEM_LIMIT = r'\GPU Adapter Memory(*)\Dedicated Limit'

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
            cm = _wt.HANDLE()   # VRAM usage counter is optional
            if self._pdh.PdhAddEnglishCounterW(self._q, self.PATH_MEM, 0, ctypes.byref(cm)) == 0:
                self._cm = cm
            cl = _wt.HANDLE()   # VRAM limit counter is optional
            self._cl = None
            if self._pdh.PdhAddEnglishCounterW(self._q, self.PATH_MEM_LIMIT, 0, ctypes.byref(cl)) == 0:
                self._cl = cl
            self._pdh.PdhCollectQueryData(self._q)   # prime
            self.ok = True
        except Exception:
            self.ok = False

    def _read_counter(self, counter, aggregate='sum'):
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
        result = 0.0
        for i in range(count.value):
            v = max(0.0, items[i].FmtValue.doubleValue)
            if aggregate == 'max':
                result = max(result, v)
            else:
                result += v
        return result

    def _sum(self, counter):
        return self._read_counter(counter, 'sum')

    def read(self):
        """Returns (utilization_percent | None, vram_used_gb | None, vram_total_gb | None)."""
        if not self.ok:
            return (None, None, None)
        try:
            if (self._pdh.PdhCollectQueryData(self._q) & 0xFFFFFFFF) != 0:
                return (None, None, None)
            util = self._sum(self._c)
            mem = self._sum(self._cm)
            limit = self._read_counter(self._cl, 'max')
            upct = int(min(100, round(util))) if util is not None else None
            mgb = (mem / 1073741824) if mem else None
            lgb = (limit / 1073741824) if limit else None
            return (upct, mgb, lgb)
        except Exception:
            return (None, None, None)

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

# ── Background slow-hardware poller ───────────────────────────────────
class _SlowPoller(threading.Thread):
    """Polls slow hardware reads (~1 s interval) off the main thread.

    nvidia-smi, sensors_battery, disk_io perdisk and cpu_freq can each
    block 10–500 ms.  Caching them here keeps _update_tick() non-blocking.
    CPython's GIL makes single-attribute writes/reads of simple types atomic,
    so no explicit lock is needed for these cached values.
    """
    def __init__(self):
        super().__init__(daemon=True, name='SlowPoller')
        self.cpu_freq_ghz = None   # float | None
        self.battery      = None   # psutil battery namedtuple | None
        self.disk_perdisk = {}     # {disk_name: sdiskio namedtuple}
        self.nvidia_w     = None   # float | None  (GPU watts from nvidia-smi)
        self._stop        = False

    def run(self):
        while not self._stop:
            self._poll()
            time.sleep(1.0)

    def _poll(self):
        try:
            f = psutil.cpu_freq()
            self.cpu_freq_ghz = (f.current / 1000.0) if (f and f.current) else None
        except Exception:
            pass
        try:
            self.battery = psutil.sensors_battery()
        except Exception:
            pass
        try:
            self.disk_perdisk = psutil.disk_io_counters(perdisk=True) or {}
        except Exception:
            pass
        try:
            self.nvidia_w = _nvidia_smi_power()
        except Exception:
            pass

    def stop(self):
        self._stop = True

def _entry_focus(widget):
    """Give keyboard focus to an Entry in the Customize window.

    The Customize window is a normal (non-overrideredirect) activatable
    window whose native title bar is stripped via Win32 (see
    CustomizeWindow.open), so it can be the real keyboard-foreground window
    and a plain focus_set() reliably delivers keystrokes to the Entry.
    """
    try:
        widget.focus_set()
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetFocus(widget.winfo_id())
    except Exception:
        pass

# ── Customize Window (v2.6) ────────────────────────────────────────────
class CustomizeWindow:
    """Custom-chrome settings window with tabbed sections. Live preview."""
    def __init__(self, widget):
        self.w = widget                    # back-ref to Widget
        self.lang = widget.lang
        self.L = CUST_LABELS.get(self.lang, CUST_LABELS['en'])
        self.T = CUST_THEME
        self._win = None
        self._tabs = {}
        self._active_tab = 'metrics'
        self._drag_data = None             # for reordering rows
        self._row_widgets = []             # ordered rows in metrics tab
        self._pending = {}                 # staged changes (applied on Apply)
        self._dirty = False
        self._apply_btn = None
        self._status_lbl = None
        self.open()

    # ── window chrome ──
    def open(self):
        if self._win and tk.Toplevel.winfo_exists(self._win):
            self._win.lift(); self._win.focus_force(); return
        win = tk.Toplevel(self.w.root)
        win.title('PulseDeck')
        # Borderless custom-chrome window.  overrideredirect keeps it out of the
        # taskbar/Alt-Tab (so no stray "python.exe" entry) and gives the clean
        # frameless look.  There are no text-input fields in here, so the
        # overrideredirect keyboard-focus limitation doesn't matter.
        win.overrideredirect(True)
        # Briefly mark it topmost so the borderless window surfaces in front on
        # open (an overrideredirect window does not activate itself, so without
        # this it can open hidden behind whatever app currently has focus). We
        # release topmost shortly after (see _drop_topmost) so other windows the
        # user opens afterwards are free to come in front of it.
        win.attributes('-topmost', True)
        self._minimized = False
        win.geometry('760x600')
        win.configure(bg=self.T['bg'])
        try: win.iconbitmap(os.path.join(_base_dir(), 'app.ico'))
        except Exception: pass
        self._win = win
        # center on screen
        win.update_idletasks()
        sw = win.winfo_screenwidth(); sh = win.winfo_screenheight()
        ww, wh = 760, 600
        win.geometry(f'{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2}')
        self._build_chrome()
        win.bind('<Escape>', lambda e: self.close())
        # ── resize grip (bottom-right) so the window can grow; tabs that use
        #    fill/expand (incl. the responsive Tools grid) adapt automatically ──
        grip = tk.Label(win, text='◢', fg=self.T['muted'], bg=self.T['titlebar'],
                        font=('Segoe UI', 9), cursor='size_nw_se')
        grip.place(relx=1.0, rely=1.0, anchor='se', x=-1, y=-1)
        grip.bind('<ButtonPress-1>', self._rz_press)
        grip.bind('<B1-Motion>', self._rz_drag)
        grip.bind('<ButtonRelease-1>', self._rz_release)
        try:
            self._round_corners(win, 12)
        except Exception:
            pass
        win.lift(); win.focus_force()
        # release always-on-top once it has surfaced, so other windows can be
        # brought in front of the settings window afterwards
        win.after(400, self._drop_topmost)
        # allow restore-from-minimize (see _minimize / _on_restore)
        win.bind('<Map>', self._on_restore)

    def _rz_press(self, e):
        self._rz = (e.x_root, e.y_root,
                    self._win.winfo_width(), self._win.winfo_height())

    def _rz_drag(self, e):
        rz = getattr(self, '_rz', None)
        if not rz:
            return
        x0, y0, w0, h0 = rz
        nw = max(620, w0 + (e.x_root - x0))
        nh = max(460, h0 + (e.y_root - y0))
        self._win.geometry(f'{nw}x{nh}')

    def _rz_release(self, e):
        self._rz = None
        try:
            self._round_corners(self._win, 12)
        except Exception:
            pass

    def _round_corners(self, win, radius):
        # Win32 SetWindowRgn for soft rounded look
        win.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id()) or win.winfo_id()
        w = win.winfo_width(); h = win.winfo_height()
        try:
            rgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, w, h, radius * 2, radius * 2)
            ctypes.windll.user32.SetWindowRgn(hwnd, rgn, True)
        except Exception:
            pass

    def _build_chrome(self):
        win = self._win; T = self.T
        # ── custom title bar ──
        tb = tk.Frame(win, bg=T['titlebar'], height=42)
        tb.pack(side='top', fill='x'); tb.pack_propagate(False)
        # drag area
        tb.bind('<ButtonPress-1>', self._tb_press)
        tb.bind('<B1-Motion>', self._tb_drag)
        # title
        try:
            emb = tk.PhotoImage(file=os.path.join(_base_dir(), 'icons', 'tray.png'))
            self._tb_emb = emb
            tk.Label(tb, image=emb, bg=T['titlebar']).pack(side='left', padx=(12, 8), pady=6)
        except Exception:
            pass
        tk.Label(tb, text=self.L['title'], fg=T['text'], bg=T['titlebar'],
                 font=('Segoe UI', 11, 'bold')).pack(side='left')
        # close button
        close_btn = tk.Label(tb, text='✕', fg=T['muted'], bg=T['titlebar'],
                             font=('Segoe UI', 14), padx=18, pady=6, cursor='hand2')
        close_btn.pack(side='right')
        close_btn.bind('<Button-1>', lambda e: self.close())
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg=T['red'], bg='#2a1518'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg=T['muted'], bg=T['titlebar']))
        # minimize button (left of close) — sends the window to the taskbar
        min_btn = tk.Label(tb, text='—', fg=T['muted'], bg=T['titlebar'],
                           font=('Segoe UI', 12, 'bold'), padx=16, pady=6,
                           cursor='hand2')
        min_btn.pack(side='right')
        min_btn.bind('<Button-1>', lambda e: self._minimize())
        min_btn.bind('<Enter>', lambda e: min_btn.config(fg=T['text'], bg='#1a2233'))
        min_btn.bind('<Leave>', lambda e: min_btn.config(fg=T['muted'], bg=T['titlebar']))
        # title bar bottom divider
        tk.Frame(win, bg=T['line'], height=1).pack(side='top', fill='x')
        # ── footer FIRST so it reserves bottom space; body fills what's left ──
        self._build_footer(win)
        # ── body: tab bar + content ──
        body = tk.Frame(win, bg=T['bg']); body.pack(side='top', fill='both', expand=True)
        tabs = tk.Frame(body, bg=T['bg2'], width=170)
        tabs.pack(side='left', fill='y'); tabs.pack_propagate(False)
        content = tk.Frame(body, bg=T['bg']); content.pack(side='left', fill='both', expand=True)
        self._content = content
        # tab buttons
        self._tab_buttons = {}
        for tid, key, icon in (
            ('general',    'general',    '⚙'),
            ('metrics',    'metrics',    '📊'),
            ('appearance', 'appearance', '🎨'),
            ('system',     'system',     '💻'),
            ('tools',      'tools',      '🧰'),
            ('about',      'about',      'ℹ'),
        ):
            b = tk.Label(tabs, text=f'  {icon}  {self.L[key]}', fg=T['muted'],
                         bg=T['bg2'], font=('Segoe UI', 10), padx=18, pady=12,
                         anchor='w', cursor='hand2')
            b.pack(fill='x')
            b.bind('<Button-1>', lambda e, t=tid: self.show_tab(t))
            b.bind('<Enter>', lambda e, b=b, t=tid: (b.config(bg='#1a2233') if t != self._active_tab else None))
            b.bind('<Leave>', lambda e, b=b, t=tid: (b.config(bg=T['bg2']) if t != self._active_tab else None))
            self._tab_buttons[tid] = b
        # show initial tab (footer was packed already, above the body)
        self.show_tab(self._active_tab)

    def _build_footer(self, win):
        T = self.T; L = self.L
        # divider
        tk.Frame(win, bg=T['line'], height=1).pack(side='bottom', fill='x')
        foot = tk.Frame(win, bg=T['titlebar'], height=52); foot.pack(side='bottom', fill='x')
        foot.pack_propagate(False)
        # Cancel button (right)
        cancel = tk.Label(foot, text=L['close'], fg=T['muted'], bg=T['titlebar'],
                          font=('Segoe UI', 10), padx=22, pady=10, cursor='hand2')
        cancel.pack(side='right', padx=(0, 10))
        cancel.bind('<Button-1>', lambda e: self._on_cancel())
        cancel.bind('<Enter>', lambda e: cancel.config(fg=T['text'], bg='#1a2233'))
        cancel.bind('<Leave>', lambda e: cancel.config(fg=T['muted'], bg=T['titlebar']))
        # Apply button (right of cancel)
        apply_btn = tk.Label(foot, text=L['apply'], fg='#0b0f18', bg=T['line'],
                             font=('Segoe UI', 10, 'bold'),
                             padx=28, pady=10, cursor='hand2')
        apply_btn.pack(side='right', padx=(0, 8))
        apply_btn.bind('<Button-1>', lambda e: self._on_apply())
        self._apply_btn = apply_btn
        # status text on the left (shows when there are pending changes)
        self._status_lbl = tk.Label(foot, text='', fg=T['muted'], bg=T['titlebar'],
                                    font=('Segoe UI', 9), padx=18)
        self._status_lbl.pack(side='left', pady=10)

    def _on_apply(self):
        """Apply changes and KEEP the window open. The bar rebuild happens
        in the next event-loop tick so the click event finishes first."""
        _log(f'_on_apply ENTER dirty={getattr(self, "_dirty", False)}')
        if not getattr(self, '_dirty', False):
            return
        try: self._win.after(20, self._do_apply_keep_open)
        except Exception: self._do_apply_keep_open()

    def _do_apply_keep_open(self):
        _log('_do_apply ENTER')
        try:
            # apply language first so subsequent rebuild speaks the new tongue
            if 'language' in self._pending:
                code = self._pending['language']
                self.w.cfg['language'] = code
                self.w.lang = code; self.lang = code
                self.L = CUST_LABELS.get(code, CUST_LABELS['en'])
                del self._pending['language']
            had_lang = 'language' in self._pending
            for k, v in self._pending.items():
                self.w.cfg[k] = v
            _log(f'  -> merged {list(self._pending.keys())}')
            save_config(self.w.cfg)
            self._pending = {}
            self._dirty = False
            # Rebuild the bar — no in-place repaint of this window, so no
            # half-redrawn state. Apply button just gets a brief "✓ Saved".
            try: self.w._rebuild()
            except Exception: pass
            try:
                self._apply_btn.config(text='✓ ' + self.L['apply'],
                                       bg=self.T['green'], fg='#0b0f18')
            except Exception: pass
            # Reset the Apply button after a short delay so the user knows
            # subsequent clicks are for new changes.
            try: self._win.after(1200, self._reset_apply_button)
            except Exception: pass
        except Exception as e:
            _log(f'_do_apply EXC: {e}\n' + traceback.format_exc())

    def _reset_apply_button(self):
        """After a successful Apply, dim the button back to its idle look."""
        try:
            self._apply_btn.config(text=self.L['apply'],
                                   bg=self.T['line'], fg='#0b0f18')
        except Exception: pass

    def _on_cancel(self):
        """Discard pending changes and close the window."""
        self._pending = {}
        self._dirty = False
        self.close()

    def _tb_press(self, e):
        self._drag_data = (e.x_root - self._win.winfo_x(), e.y_root - self._win.winfo_y())

    def _tb_drag(self, e):
        if not self._drag_data: return
        x = e.x_root - self._drag_data[0]
        y = e.y_root - self._drag_data[1]
        self._win.geometry(f'+{x}+{y}')

    def _drop_topmost(self):
        """Release always-on-top so the user can bring other windows in front."""
        try:
            if self._win: self._win.attributes('-topmost', False)
        except Exception:
            pass

    def _minimize(self):
        """Send the borderless window to the taskbar.

        An overrideredirect window can't be iconified and has no taskbar
        button, so we drop overrideredirect first — that gives Windows a real
        taskbar entry and lets iconify() work. _on_restore re-applies the
        custom chrome when the user clicks the taskbar button to restore it."""
        win = self._win
        if not win: return
        try:
            win.update_idletasks()
            self._minimized = True
            win.overrideredirect(False)
            win.iconify()
        except Exception:
            pass

    def _on_restore(self, e=None):
        """Re-apply the frameless chrome after a restore-from-minimize."""
        win = self._win
        if not win or not getattr(self, '_minimized', False):
            return
        try:
            if win.state() == 'normal':
                self._minimized = False
                win.overrideredirect(True)
                win.attributes('-topmost', True)
                win.lift(); win.focus_force()
                win.after(300, self._drop_topmost)
                try: self._round_corners(win, 12)
                except Exception: pass
        except Exception:
            pass

    def close(self):
        try: self._win.destroy()
        except Exception: pass
        self._win = None
        try: self.w._customize = None
        except Exception: pass

    # ── tabs ──
    def show_tab(self, tid):
        """ALWAYS deferred: destroying the widget that is currently
        dispatching the click event (e.g. a ▲ button inside the tab we're
        about to clear) freezes Tcl. Deferring by one tick guarantees the
        event handler returns before any widget is destroyed."""
        self._active_tab = tid
        try:
            self._win.after(15, lambda: self._show_tab_now(tid))
        except Exception:
            self._show_tab_now(tid)

    def _show_tab_now(self, tid):
        if tid != self._active_tab:
            return  # superseded by a newer request
        # update tab button styles
        for k, b in self._tab_buttons.items():
            if k == tid:
                b.config(bg=self.T['panel'], fg=self.T['cyan'],
                         font=('Segoe UI', 10, 'bold'))
            else:
                b.config(bg=self.T['bg2'], fg=self.T['muted'],
                         font=('Segoe UI', 10))
        # clear content (safe now — no event is being dispatched from inside)
        for c in self._content.winfo_children():
            c.destroy()
        # build the selected tab
        getattr(self, f'_tab_{tid}')()

    def _section(self, title, padx=24):
        T = self.T
        f = tk.Frame(self._content, bg=T['bg'])
        f.pack(side='top', fill='x', padx=padx, pady=(14, 6))
        tk.Label(f, text=title, fg=T['text'], bg=T['bg'],
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        tk.Frame(self._content, bg=T['line'], height=1).pack(side='top', fill='x', padx=padx)
        return f

    def _check_row(self, parent, label, cfg_key, on_toggle=None):
        T = self.T
        row = tk.Frame(parent, bg=T['bg']); row.pack(fill='x', padx=24, pady=4)
        var = tk.BooleanVar(value=bool(self.w.cfg.get(cfg_key)))
        cb = tk.Checkbutton(row, text=' ' + label, variable=var, fg=T['text'], bg=T['bg'],
                            selectcolor=T['bg2'], activebackground=T['bg'],
                            activeforeground=T['text'], font=('Segoe UI', 10),
                            bd=0, highlightthickness=0, anchor='w',
                            command=lambda: self._on_check(cfg_key, var.get(), on_toggle))
        cb.pack(side='left', fill='x', expand=True)
        return cb

    def _mark_dirty(self):
        """Flag that there are unsaved/unapplied changes."""
        self._dirty = True
        try:
            if getattr(self, '_apply_btn', None):
                self._apply_btn.config(state='normal',
                                       bg=self.T['cyan'], fg='#0b0f18',
                                       text='● ' + self.L['apply'])
        except Exception:
            pass

    def _on_check(self, key, val, on_toggle):
        # write to a staging dict; nothing applies until "Apply" is clicked.
        self._pending[key] = val
        self._mark_dirty()
        if on_toggle:
            # callback that has side-effects we want live (e.g. opening
            # Windows Settings); these are passed-through unchanged.
            try: self._win.after(1, lambda: on_toggle(val))
            except Exception: pass

    def _radio_group(self, parent, label, cfg_key, options, on_change=None):
        """options = [(value, label), ...]"""
        T = self.T
        row = tk.Frame(parent, bg=T['bg']); row.pack(fill='x', padx=24, pady=6)
        tk.Label(row, text=label, fg=T['muted'], bg=T['bg'],
                 font=('Segoe UI', 10), width=20, anchor='w').pack(side='left')
        # Tk's native radiobutton looks blurry on dark themes (no clear
        # selected-state contrast). Custom-drawn pills give clean feedback.
        current = self._pending.get(cfg_key, self.w.cfg.get(cfg_key))
        # collect the rendered pills so we can update them on click
        pills = []
        def render_pills():
            cur = self._pending.get(cfg_key, self.w.cfg.get(cfg_key))
            for val, btn in pills:
                # robust equality across int/float/str
                try:
                    sel = (val == cur) or (str(val) == str(cur)) \
                          or (isinstance(val, (int, float)) and
                              isinstance(cur, (int, float)) and abs(val - cur) < 1e-6)
                except Exception:
                    sel = (val == cur)
                btn.config(text=('● ' if sel else '○ ') + btn._label,
                           fg=(T['cyan'] if sel else T['muted']))
        def make_click(v):
            def _click(e=None):
                self._on_radio(cfg_key, v, on_change)
                render_pills()
            return _click
        for val, lbl in options:
            pill = tk.Label(row, text='○ ' + lbl, fg=T['muted'], bg=T['bg'],
                            font=('Segoe UI', 10), padx=8, pady=2, cursor='hand2')
            pill._label = lbl
            pill.pack(side='left', padx=4)
            pill.bind('<Button-1>', make_click(val))
            pill.bind('<Enter>', lambda e, p=pill:
                      p.config(bg='#1a2233') if 'bg' not in p._label else None)
            pill.bind('<Leave>', lambda e, p=pill: p.config(bg=T['bg']))
            pills.append((val, pill))
        render_pills()

    def _on_radio(self, key, val, on_change):
        self._pending[key] = val
        self._mark_dirty()
        if on_change:
            try: self._win.after(1, lambda: on_change(val))
            except Exception: pass

    # ── General tab ──
    def _tab_general(self):
        T = self.T; L = self.L
        self._section('⚙  ' + L['general'])
        body = tk.Frame(self._content, bg=T['bg']); body.pack(fill='both', expand=True)
        self._radio_group(body, L['refresh_rate'], 'interval',
                          [(500, '0.5s'), (1000, '1s'), (2000, '2s'), (5000, '5s')],
                          on_change=lambda v: None)
        # language dropdown via radio (compact)
        lr = tk.Frame(body, bg=T['bg']); lr.pack(fill='x', padx=24, pady=6)
        tk.Label(lr, text=L['language'], fg=T['muted'], bg=T['bg'],
                 font=('Segoe UI', 10), width=20, anchor='w').pack(side='left')
        # Custom dropdown — ttk.Combobox renders poorly on dark themes
        cur_lang = self._pending.get('language', self.w.cfg.get('language') or self.w.lang)
        btn = tk.Label(lr, text=LANG_NAMES.get(cur_lang, 'English') + '  ▾',
                       fg=T['text'], bg=T['panel'], padx=12, pady=4,
                       font=('Segoe UI', 10), cursor='hand2',
                       relief='solid', bd=1, highlightbackground=T['line'])
        btn.pack(side='left')
        def _show_lang_menu(_e=None):
            menu = tk.Toplevel(self._win); menu.overrideredirect(True)
            menu.configure(bg=T['panel'], highlightbackground=T['line'], highlightthickness=1)
            try: menu.attributes('-topmost', True)
            except Exception: pass
            x = btn.winfo_rootx(); y = btn.winfo_rooty() + btn.winfo_height() + 2
            menu.geometry(f'+{x}+{y}')
            for code in LANGS:
                row = tk.Label(menu, text=LANG_NAMES[code], fg=T['text'],
                               bg=T['panel'] if code != cur_lang else T['bg2'],
                               padx=18, pady=6, font=('Segoe UI', 10),
                               anchor='w', cursor='hand2', width=18)
                row.pack(fill='x')
                def _pick(c=code, m=menu, b=btn):
                    btn.config(text=LANG_NAMES[c] + '  ▾')
                    try: m.destroy()
                    except Exception: pass
                    self._on_lang_change(c)
                row.bind('<Button-1>', lambda e, p=_pick: p())
                row.bind('<Enter>', lambda e, r=row: r.config(bg=T['bg2']))
                row.bind('<Leave>', lambda e, r=row, c=code:
                         r.config(bg=T['panel'] if c != cur_lang else T['bg2']))
            # Close on click-outside / Escape via a modal grab. FocusOut is
            # unreliable here: the parent window is overrideredirect and never
            # holds keyboard focus, which made the menu close instantly.
            def _close(_e=None, m=menu):
                try: m.grab_release()
                except Exception: pass
                try: m.destroy()
                except Exception: pass
            def _outside(e, m=menu):
                try:
                    if not m.winfo_exists():
                        return
                    inside = (m.winfo_rootx() <= e.x_root <= m.winfo_rootx() + m.winfo_width()
                              and m.winfo_rooty() <= e.y_root <= m.winfo_rooty() + m.winfo_height())
                    if not inside:
                        _close()
                except Exception:
                    pass
            menu.bind('<Button-1>', _outside, add='+')
            menu.bind('<Escape>', _close)
            menu.update_idletasks()
            try: menu.grab_set()
            except Exception: pass
        btn.bind('<Button-1>', _show_lang_menu)
        btn.bind('<Enter>', lambda e: btn.config(bg=T['bg2']))
        btn.bind('<Leave>', lambda e: btn.config(bg=T['panel']))
        self._check_row(body, L['lock_pos'], 'locked')
        self._check_row(body, L['tooltips'], 'tooltips')
        self._check_row(body, L.get('hide_fs', 'Hide when an app goes fullscreen'),
                        'follow_taskbar')
        self._check_row(body, L['check_upd'], 'check_updates')
        # startup row: a button that opens Settings (MSIX) or toggles (Win32)
        srow = tk.Frame(body, bg=T['bg']); srow.pack(fill='x', padx=24, pady=10)
        if _is_msix():
            b = tk.Button(srow, text='🚀  ' + L['startup'] + '  →  Windows Settings',
                          command=lambda: _open_startup_settings(),
                          bg=T['panel'], fg=T['text'], bd=0,
                          font=('Segoe UI', 10), padx=16, pady=8,
                          activebackground=T['bg2'], activeforeground=T['cyan'],
                          cursor='hand2')
            b.pack(side='left')
        else:
            var = tk.BooleanVar(value=is_startup_enabled())
            cb = tk.Checkbutton(srow, text='  🚀  ' + L['startup'], variable=var,
                                fg=T['text'], bg=T['bg'], selectcolor=T['bg2'],
                                activebackground=T['bg'], activeforeground=T['text'],
                                font=('Segoe UI', 10), bd=0,
                                command=lambda: set_startup(var.get()))
            cb.pack(side='left')
        # reset position
        rp = tk.Button(self._content, text='⤺  ' + L['reset_pos'],
                       command=lambda: (self.w._act_reposition(),),
                       bg=T['panel'], fg=T['text'], bd=0,
                       font=('Segoe UI', 10), padx=14, pady=6,
                       activebackground=T['bg2'], activeforeground=T['cyan'],
                       cursor='hand2')
        rp.pack(side='top', anchor='w', padx=24, pady=10)

    def _on_lang_change(self, code):
        # Stage only — language switch happens on Apply.
        self._pending['language'] = code
        self._mark_dirty()

    # ── Metrics tab (with drag-reorder) ──
    def _tab_metrics(self):
        T = self.T; L = self.L
        self._section('📊  ' + L['show_hide'])
        hint = tk.Label(self._content, text='  ' + L['drag_hint'], fg=T['muted'],
                        bg=T['bg'], font=('Segoe UI', 9))
        hint.pack(anchor='w', padx=24)
        # rows container (no canvas needed — fits 9 rows easily)
        wrap = tk.Frame(self._content, bg=T['bg'])
        wrap.pack(fill='both', expand=True, padx=20, pady=8)
        self._row_widgets = []
        order = self._get_order()
        for cid in order:
            self._build_metric_row(wrap, cid)
        # reset button bottom
        rb = tk.Button(self._content, text='⤺  ' + L['reset'],
                       command=self._reset_order,
                       bg=T['panel'], fg=T['text'], bd=0,
                       font=('Segoe UI', 10), padx=14, pady=6,
                       activebackground=T['bg2'], activeforeground=T['cyan'],
                       cursor='hand2')
        rb.pack(side='top', anchor='w', padx=24, pady=8)

    def _build_metric_row(self, parent, cid):
        T = self.T
        meta = next((m for m in CELL_META if m[0] == cid), None)
        if not meta: return
        _, name, icon, cfg_key = meta
        # NO highlightthickness — the 1-px dark "border" the user reported
        # was Tk's default highlight rectangle around each row frame
        row = tk.Frame(parent, bg=T['panel'], height=42, bd=0, highlightthickness=0)
        row.pack(fill='x', pady=3); row.pack_propagate(False)
        # ☰ drag handle — drag the row up/down to reorder.
        # (The old freeze was never the drag itself: the bar's _bind_events
        #  was hijacking clicks inside this window. That's fixed, so the
        #  natural drag UX is back.)
        handle = tk.Label(row, text='☰', fg=T['muted'], bg=T['panel'],
                          font=('Segoe UI', 12), padx=12, cursor='hand2')
        handle.pack(side='left')
        handle.bind('<Enter>', lambda e, w=handle: w.config(fg=T['cyan']))
        handle.bind('<Leave>', lambda e, w=handle: w.config(fg=T['muted']))
        for w_ in (handle, row):
            w_.bind('<ButtonPress-1>', lambda e, r=row: self._row_press(e, r))
            w_.bind('<B1-Motion>', lambda e, r=row: self._row_drag(e, r))
            w_.bind('<ButtonRelease-1>', lambda e, r=row: self._row_release(e, r))
        # checkbox (custom-drawn for the dark theme)
        is_on = bool(self._pending.get(cfg_key, self.w.cfg.get(cfg_key)))
        chk = tk.Label(row, text=('☑' if is_on else '☐'),
                       fg=T['green'] if is_on else T['muted'],
                       bg=T['panel'], font=('Segoe UI', 14, 'bold'),
                       padx=10, cursor='hand2')
        chk.pack(side='left')
        def _toggle(e=None, k=cfg_key, lbl=chk):
            new = not bool(self._pending.get(k, self.w.cfg.get(k)))
            lbl.config(text='☑' if new else '☐',
                       fg=T['green'] if new else T['muted'])
            self._on_check(k, new, None)
        chk.bind('<Button-1>', _toggle)
        # icon + name
        tk.Label(row, text=icon + '  ' + name, fg=T['text'], bg=T['panel'],
                 font=('Segoe UI', 10)).pack(side='left', padx=4)
        row._cell_id = cid
        self._row_widgets.append(row)

    def _move_row(self, cid, direction):
        """Move a row up (direction=-1) or down (direction=+1) in the order."""
        order = self._get_order()
        try:
            i = order.index(cid)
        except ValueError:
            return
        j = i + direction
        if j < 0 or j >= len(order):
            return
        order[i], order[j] = order[j], order[i]
        self._pending['cell_order'] = order
        self._mark_dirty()
        # repaint the metrics tab to show the new order
        try: self.show_tab('metrics')
        except Exception: pass

    def _get_order(self):
        # staged order takes precedence over the saved one
        staged = self._pending.get('cell_order', 'unset')
        if staged != 'unset':
            order = staged or DEFAULT_CELL_ORDER
        else:
            order = self.w.cfg.get('cell_order') or DEFAULT_CELL_ORDER
        ids = set(c[0] for c in CELL_META)
        order = [c for c in order if c in ids]
        for c in DEFAULT_CELL_ORDER:
            if c not in order: order.append(c)
        return order

    # ── ghost-target drag: nothing moves DURING the drag (no repacking,
    #    no stale geometry, no oscillation). We only highlight the row the
    #    cursor is over; the single reorder happens at release. ──
    def _row_press(self, e, row):
        self._drag_row = row
        self._drag_target = None
        row.config(bg=self.T['bg2'])
        for c in row.winfo_children():
            try: c.config(bg=self.T['bg2'])
            except Exception: pass

    def _row_drag(self, e, row):
        if getattr(self, '_drag_row', None) != row: return
        # geometry is STABLE during the whole drag (nothing is repacked),
        # so winfo_rooty values are always correct here
        target = None
        for r in self._row_widgets:
            if r is row: continue
            try:
                y1 = r.winfo_rooty()
                if y1 <= e.y_root <= y1 + r.winfo_height():
                    target = r
                    break
            except Exception:
                continue
        old = getattr(self, '_drag_target', None)
        if target is old: return
        # clear previous target highlight
        if old is not None:
            try:
                old.config(bg=self.T['panel'])
                for c in old.winfo_children():
                    try: c.config(bg=self.T['panel'])
                    except Exception: pass
            except Exception: pass
        # highlight the new target
        if target is not None:
            try:
                target.config(bg='#1d3a52')
                for c in target.winfo_children():
                    try: c.config(bg='#1d3a52')
                    except Exception: pass
            except Exception: pass
        self._drag_target = target

    def _row_release(self, e, row):
        if getattr(self, '_drag_row', None) is None:
            return
        src = self._drag_row
        tgt = getattr(self, '_drag_target', None)
        self._drag_row = None
        self._drag_target = None
        # restore colours on both rows
        for r in (src, tgt):
            if r is None: continue
            try:
                r.config(bg=self.T['panel'])
                for c in r.winfo_children():
                    try: c.config(bg=self.T['panel'])
                    except Exception: pass
            except Exception: pass
        if tgt is None or tgt is src:
            return   # plain click / dropped on itself — nothing to do
        # single reorder: move src to tgt's position
        try:
            rows = self._row_widgets
            i, j = rows.index(src), rows.index(tgt)
            rows.insert(j, rows.pop(i))
            for rr in rows:
                rr.pack_forget()
            for rr in rows:
                rr.pack(fill='x', pady=3)
            self._pending['cell_order'] = [r._cell_id for r in rows]
            self._mark_dirty()
        except Exception:
            pass

    def _reset_order(self):
        self._pending['cell_order'] = None
        self._mark_dirty()
        # rebuild the metrics tab to show the default order visually
        self.show_tab('metrics')

    # ── Appearance tab ──
    def _tab_appearance(self):
        T = self.T; L = self.L
        self._section('🎨  ' + L['appearance'])
        body = tk.Frame(self._content, bg=T['bg']); body.pack(fill='both', expand=True)
        # theme dropdown
        tr = tk.Frame(body, bg=T['bg']); tr.pack(fill='x', padx=24, pady=8)
        tk.Label(tr, text=L['theme'], fg=T['muted'], bg=T['bg'],
                 font=('Segoe UI', 10), width=20, anchor='w').pack(side='left')
        # custom theme dropdown
        cur_theme = self._pending.get('theme', self.w.cfg.get('theme', 'default'))
        tbtn = tk.Label(tr, text=cur_theme.capitalize() + '  ▾',
                        fg=T['text'], bg=T['panel'], padx=12, pady=4,
                        font=('Segoe UI', 10), cursor='hand2',
                        relief='solid', bd=1, highlightbackground=T['line'])
        tbtn.pack(side='left')
        def _show_theme_menu(_e=None):
            menu = tk.Toplevel(self._win); menu.overrideredirect(True)
            menu.configure(bg=T['panel'], highlightbackground=T['line'], highlightthickness=1)
            try: menu.attributes('-topmost', True)
            except Exception: pass
            x = tbtn.winfo_rootx(); y = tbtn.winfo_rooty() + tbtn.winfo_height() + 2
            menu.geometry(f'+{x}+{y}')
            for name in THEMES:
                row = tk.Label(menu, text=name.capitalize(), fg=T['text'],
                               bg=T['panel'] if name != cur_theme else T['bg2'],
                               padx=18, pady=6, font=('Segoe UI', 10),
                               anchor='w', cursor='hand2', width=18)
                row.pack(fill='x')
                def _pick(n=name, m=menu, b=tbtn):
                    b.config(text=n.capitalize() + '  ▾')
                    try: m.destroy()
                    except Exception: pass
                    self._on_radio('theme', n, None)
                row.bind('<Button-1>', lambda e, p=_pick: p())
                row.bind('<Enter>', lambda e, r=row: r.config(bg=T['bg2']))
                row.bind('<Leave>', lambda e, r=row, n=name:
                         r.config(bg=T['panel'] if n != cur_theme else T['bg2']))
            # Close on click-outside / Escape via a modal grab (see lang menu).
            def _close(_e=None, m=menu):
                try: m.grab_release()
                except Exception: pass
                try: m.destroy()
                except Exception: pass
            def _outside(e, m=menu):
                try:
                    if not m.winfo_exists():
                        return
                    inside = (m.winfo_rootx() <= e.x_root <= m.winfo_rootx() + m.winfo_width()
                              and m.winfo_rooty() <= e.y_root <= m.winfo_rooty() + m.winfo_height())
                    if not inside:
                        _close()
                except Exception:
                    pass
            menu.bind('<Button-1>', _outside, add='+')
            menu.bind('<Escape>', _close)
            menu.update_idletasks()
            try: menu.grab_set()
            except Exception: pass
        tbtn.bind('<Button-1>', _show_theme_menu)
        tbtn.bind('<Enter>', lambda e: tbtn.config(bg=T['bg2']))
        tbtn.bind('<Leave>', lambda e: tbtn.config(bg=T['panel']))
        t = self.w.t
        self._radio_group(body, L['size'], 'font_scale',
                          [('small', t('small')), ('normal', t('normal')),
                           ('large', t('large'))])
        self._radio_group(body, L['orientation'], 'orientation',
                          [('horizontal', '⇔'), ('vertical', '⇕')])
        self._radio_group(body, L.get('bar_marker', 'Bar marker'), 'bar_labels',
                          [('icon', L.get('marker_icon', 'Icons')),
                           ('text', L.get('marker_text', 'Text'))])
        self._check_row(body, L['stacked'], 'stacked')
        # When two-row mode is OFF, which of the two rows survives?
        self._radio_group(body, '└ ' + L['single_row'], 'single_row_mode',
                          [('percent', L['row_percent']),
                           ('detail', L['row_detail'])])
        self._check_row(body, L['sparklines'], 'sparklines')
        self._check_row(body, L['on_taskbar'], 'on_taskbar')
        self._check_row(body, L['background'] + ' — transparent', 'transparent_bg')
        # opacity
        self._radio_group(body, L['background'] + ' — ' + 'opacity',
                          'opacity', [(0.5, '50%'), (0.7, '70%'),
                                      (0.85, '85%'), (1.0, '100%')])
        # network unit
        self._radio_group(body, 'Network', 'net_unit',
                          [('bytes', 'MB/s'), ('bits', 'Mbps')])

    def _weather_settings(self, body):
        """Weather unit (city input removed — weather auto-locates by IP)."""
        T = self.T; L = self.L
        self._radio_group(body, L.get('weather_lbl', 'Weather') + ' °', 'weather_unit',
                          [('C', '°C'), ('F', '°F')],
                          on_change=lambda v: setattr(self.w, '_weather_dirty', True))

    # ── Alerts tab ──
    def _tab_alerts(self):
        T = self.T; L = self.L
        self._section('🚨  ' + L['alerts'])
        body = tk.Frame(self._content, bg=T['bg']); body.pack(fill='both', expand=True)
        # weather location + unit (lives here now that the tray submenu is gone)
        tk.Label(body, text='🌤  ' + L.get('weather_lbl', 'Weather'), fg=T['cyan'],
                 bg=T['bg'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=24, pady=(6, 0))
        self._weather_settings(body)
        tk.Frame(body, bg=T['line'], height=1).pack(fill='x', padx=24, pady=(8, 4))
        self._check_row(body, L['quakes_on'], 'quakes_on',
                        on_toggle=lambda v: (self.w._rebuild(),
                                              self.w._ensure_quakes_thread() if v else None))
        # sources row
        sr = tk.Frame(body, bg=T['bg']); sr.pack(fill='x', padx=24, pady=6)
        tk.Label(sr, text=L['sources'], fg=T['muted'], bg=T['bg'],
                 font=('Segoe UI', 10), width=20, anchor='w').pack(side='left')
        for key, name in (('quakes_emsc', 'EMSC (Europe)'),
                          ('quakes_usgs', 'USGS (Global)')):
            var = tk.BooleanVar(value=bool(self.w.cfg.get(key)))
            tk.Checkbutton(sr, text=' ' + name, variable=var, fg=T['text'], bg=T['bg'],
                           selectcolor=T['bg2'], activebackground=T['bg'],
                           activeforeground=T['text'], font=('Segoe UI', 10),
                           bd=0, command=lambda k=key, v=var:
                           (self.w.cfg.update({k: v.get()}), save_config(self.w.cfg))
                           ).pack(side='left', padx=8)
        # felt level
        levels = QUAKES_LEVELS.get(self.lang, QUAKES_LEVELS['en'])
        self._radio_group(body, L['felt_level'], 'quakes_min_mmi',
                          [(th, lbl.split('(')[0].strip()) for lbl, th in levels])
        self._check_row(body, '🔔  Toast notifications', 'quakes_toasts')
        self._check_row(body, '🔇  Mute all', 'quakes_mute')
        # recent events button
        rb = tk.Button(self._content, text='📜  ' + L['recent_evt'],
                       command=self.w._show_quake_history,
                       bg=T['panel'], fg=T['text'], bd=0,
                       font=('Segoe UI', 10), padx=14, pady=6,
                       activebackground=T['bg2'], activeforeground=T['cyan'],
                       cursor='hand2')
        rb.pack(side='top', anchor='w', padx=24, pady=10)

    # ── About tab ──
    # ── System Info tab ──
    def _set_sys_view(self, mode):
        """Switch the System tab between the Summary and Advanced views. The
        hardware scan is cached (self._sysinfo), so switching is instant."""
        if self.w.cfg.get('sys_view') == mode:
            return
        self.w._set('sys_view', mode)
        self.show_tab('system')

    def _tab_system(self):
        T = self.T; L = self.L
        # Header + Summary/Advanced view toggle
        f = tk.Frame(self._content, bg=T['bg'])
        f.pack(side='top', fill='x', padx=24, pady=(14, 6))
        tk.Label(f, text='💻  ' + L['system'], fg=T['text'], bg=T['bg'],
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        cur_view = self.w.cfg.get('sys_view', 'summary')
        vt = tk.Frame(f, bg=T['bg']); vt.pack(side='right')
        for mode, lbl in (('summary',  L.get('sys_summary', 'Summary')),
                          ('advanced', L.get('sys_advanced', 'Advanced'))):
            sel = (mode == cur_view)
            b = tk.Label(vt, text=lbl, cursor='hand2', padx=12, pady=3,
                         font=('Segoe UI', 9, 'bold' if sel else 'normal'),
                         bg=(T['cyan'] if sel else T['panel']),
                         fg=('#0d1117' if sel else T['muted']))
            b.pack(side='left', padx=1)
            b.bind('<Button-1>', lambda e, m=mode: self._set_sys_view(m))
        tk.Frame(self._content, bg=T['line'], height=1).pack(
            side='top', fill='x', padx=24)
        # Reuse the cached scan when we already have it (e.g. toggling the view)
        cached = getattr(self, '_sysinfo', None)
        if cached is not None:
            self._render_system(cached, None)
            return
        loading_txt = '⏳  ' + self.L['loading_sys']
        loading = tk.Label(self._content, text=loading_txt,
                           fg=T['cyan'], bg=T['bg'],
                           font=('Segoe UI', 11))
        loading.pack(anchor='w', padx=24, pady=18)
        # animate the hourglass while WMI runs
        _frames = ['⏳', '⌛']
        _i = [0]
        def _tick():
            try:
                if loading.winfo_exists():
                    _i[0] = (_i[0] + 1) % 2
                    loading.config(text=_frames[_i[0]] + loading_txt[1:])
                    self._win.after(500, _tick)
            except Exception: pass
        self._win.after(500, _tick)
        # Collect in a thread so the UI stays responsive (WMI calls take ~1s)
        def _bg():
            info = collect_system_info()
            self._sysinfo = info          # cache for instant view switching
            try: self._win.after(0, lambda: self._render_system(info, loading))
            except Exception: pass
        threading.Thread(target=_bg, daemon=True).start()

    def _render_system(self, info, loading_lbl):
        # The hardware scan runs in a background thread; by the time it calls
        # back the user may have switched tabs. If System is no longer the
        # active tab, drop the result — otherwise we'd paint the System widgets
        # into whatever tab is now showing (e.g. Tools) and break the layout.
        if self._active_tab != 'system':
            return
        try: loading_lbl.destroy()
        except Exception: pass
        T = self.T
        # Scrollable body
        outer = tk.Frame(self._content, bg=T['bg'])
        outer.pack(fill='both', expand=True, padx=20, pady=4)
        canvas = tk.Canvas(outer, bg=T['bg'], highlightthickness=0, bd=0)
        sb = tk.Scrollbar(outer, orient='vertical', command=canvas.yview,
                          bg=T['panel'], troughcolor=T['bg2'],
                          activebackground=T['cyan'], bd=0, highlightthickness=0,
                          width=10)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        body = tk.Frame(canvas, bg=T['bg'])
        body_window = canvas.create_window((0, 0), window=body, anchor='nw')
        # value labels that should re-wrap when the window is resized (so long
        # values like the CPU model or BIOS string wrap instead of being clipped)
        sys_vals = []
        # keep body the same width as the canvas viewport so right-packed
        # children (brand logos) stay visible.
        def _resize_body(e, _wid=body_window):
            try:
                canvas.itemconfig(_wid, width=e.width)
                # leave room for the key column (~150 px) + paddings + scrollbar
                wl = max(140, e.width - 210)
                for vl in sys_vals:
                    try: vl.configure(wraplength=wl)
                    except Exception: pass
            except Exception: pass
        canvas.bind('<Configure>', _resize_body)
        body.bind('<Configure>',
                  lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind_all('<MouseWheel>',
                        lambda e: canvas.yview_scroll(int(-e.delta/120), 'units'))

        def _brand_logo(parent, name, bg_color):
            """Brand logo image. Returns a Label with a PNG, or None."""
            n = (name or '').lower()
            # Keyword → logo file key (in icons/brands/<key>.png)
            BRANDS = (
                (('nvidia', 'geforce', 'rtx', 'gtx', 'quadro'),   'nvidia'),
                (('radeon', 'ryzen', 'amd', 'authenticamd',
                  'epyc', 'threadripper'),                         'amd'),
                (('intel', 'genuineintel', 'core(tm)', 'celeron',
                  'pentium', 'xeon', 'arc '),                      'intel'),
                (('asustek', 'asus', 'rog '),                      'asus'),
                (('micro-star', 'msi'),                            'msi'),
                (('gigabyte', 'aorus'),                            'gigabyte'),
                (('asrock',),                                      'asrock'),
                (('samsung',),                                     'samsung'),
                (('lg ', 'lg electronics', 'lg display', 'goldstar'),'lg'),
                (('dell',),                                        'dell'),
                (('hewlett', 'hp '),                               'hp'),
                (('lenovo',),                                      'lenovo'),
                (('acer',),                                        'acer'),
                (('benq',),                                        'benq'),
                (('aoc',),                                         'aoc'),
                (('philips',),                                     'philips'),
                (('viewsonic',),                                   'viewsonic'),
                (('iiyama',),                                      'iiyama'),
                (('corsair',),                                     'corsair'),
                (('kingston', 'hyperx', 'fury'),                   'kingston'),
                (('g.skill', 'gskill', 'g skill'),                 'gskill'),
                (('crucial', 'micron'),                            'crucial'),
                (('western digital', 'wdc', ' wd '),               'wd'),
                (('seagate',),                                     'seagate'),
                (('sandisk',),                                     'sandisk'),
                (('toshiba', 'kioxia'),                            'kioxia'),
                (('realtek',),                                     'realtek'),
                (('creative',),                                    'creative'),
                (('logitech',),                                    'logitech'),
            )
            key = None
            for keys, k in BRANDS:
                if any(kw in n for kw in keys):
                    key = k; break
            if not key: return None
            # cache PhotoImage on the CustomizeWindow so refs live as long as
            # the Toplevel master used to create them.
            cache = getattr(self, '_brand_logo_cache', None)
            if cache is None:
                cache = {}
                self._brand_logo_cache = cache
            if key not in cache:
                path = os.path.join(_base_dir(), 'icons', 'brands', key + '.png')
                if not os.path.exists(path): return None
                try:
                    from PIL import Image, ImageTk
                    im = Image.open(path).convert('RGBA')
                    target_h = 32
                    w0, h0 = im.size
                    new_w = max(1, int(w0 * target_h / h0))
                    im = im.resize((new_w, target_h), Image.LANCZOS)
                    cache[key] = ImageTk.PhotoImage(im, master=self._win)
                except Exception:
                    return None
            img = cache[key]
            lbl = tk.Label(parent, image=img, bg=bg_color, bd=0,
                           width=img.width(), height=img.height())
            lbl.image = img
            return lbl

        def section(title, icon, color, badge_src=None):
            sf = tk.Frame(body, bg=T['panel'], bd=0, highlightthickness=0)
            sf.pack(fill='x', pady=(6, 4))
            hdr = tk.Frame(sf, bg=T['panel']); hdr.pack(fill='x', padx=12, pady=(8, 4))
            tk.Label(hdr, text=icon + '  ' + title, fg=color, bg=T['panel'],
                     font=('Segoe UI', 11, 'bold')).pack(side='left')
            # brand logo on the right
            logo = _brand_logo(hdr, badge_src, T['panel']) if badge_src else None
            if logo is not None:
                logo.pack(side='right', padx=(0, 4))
            return sf

        def kv(parent, k, v, value_color=None):
            if v in (None, ''): return
            r = tk.Frame(parent, bg=T['panel']); r.pack(fill='x', padx=18, pady=2)
            tk.Label(r, text=k, fg=T['muted'], bg=T['panel'],
                     font=('Segoe UI', 9), width=20, anchor='nw').pack(
                         side='left', anchor='n')
            vl = tk.Label(r, text=str(v), fg=(value_color or T['text']),
                          bg=T['panel'], font=('Segoe UI', 9), anchor='w',
                          justify='left', wraplength=480)
            vl.pack(side='left', fill='x', expand=True)
            sys_vals.append(vl)

        # ── Performance / live bottleneck (v2.8) ──
        L = self.L
        s = section(L.get('sys_perf', 'Performance (live)'), '⚡', T['cyan'])
        bn_row = tk.Frame(s, bg=T['panel']); bn_row.pack(fill='x', padx=18, pady=2)
        tk.Label(bn_row, text=L.get('bn_label', 'Limiting factor'),
                 fg=T['muted'], bg=T['panel'], font=('Segoe UI', 9),
                 width=20, anchor='w').pack(side='left')
        bn_val = tk.Label(bn_row, text='…', fg=T['text'], bg=T['panel'],
                          font=('Segoe UI', 9, 'bold'), anchor='w')
        bn_val.pack(side='left')
        bn_metrics = tk.Label(s, text='', fg=T['muted'], bg=T['panel'],
                              font=('Segoe UI', 8), anchor='w')
        bn_metrics.pack(fill='x', padx=18, pady=(0, 2))
        # uptime (live) + boot time (static)
        import datetime as _dt
        try:
            _boot_str = _dt.datetime.fromtimestamp(
                psutil.boot_time()).strftime('%d/%m/%Y  %H:%M')
        except Exception:
            _boot_str = '—'
        up_row = tk.Frame(s, bg=T['panel']); up_row.pack(fill='x', padx=18, pady=2)
        tk.Label(up_row, text=L.get('sys_uptime', 'Uptime'), fg=T['muted'],
                 bg=T['panel'], font=('Segoe UI', 9), width=20, anchor='w').pack(side='left')
        up_val = tk.Label(up_row, text=_uptime_str(), fg=T['green'], bg=T['panel'],
                          font=('Segoe UI', 9), anchor='w')
        up_val.pack(side='left')
        bt_row = tk.Frame(s, bg=T['panel']); bt_row.pack(fill='x', padx=18, pady=2)
        tk.Label(bt_row, text=L.get('sys_booted', 'Booted'), fg=T['muted'],
                 bg=T['panel'], font=('Segoe UI', 9), width=20, anchor='w').pack(side='left')
        tk.Label(bt_row, text=_boot_str, fg=T['text'], bg=T['panel'],
                 font=('Segoe UI', 9), anchor='w').pack(side='left')
        tk.Frame(s, bg=T['panel'], height=8).pack()

        # rolling smoothing buffers (~4 s) + per-disk busy-time tracker
        from collections import deque as _dq
        _buf = {k: _dq(maxlen=4) for k in ('cpu', 'gpu', 'ram', 'vram', 'disk')}
        _disk_prev = {}   # disk name -> (busy_time_ms, wall_time_s)
        _VERDICT = {
            'idle':     (L.get('bn_idle', 'Idle — system not under load'), T['green']),
            'balanced': (L.get('bn_none', 'Balanced — all components have headroom'), T['green']),
            'cpu':  (L.get('bn_cpu',  'CPU-bound'),        T['orange']),
            'gpu':  (L.get('bn_gpu',  'GPU-bound'),        T['orange']),
            'disk': (L.get('bn_disk', 'Disk-bound (I/O)'), T['orange']),
            'ram':  (L.get('bn_ram',  'RAM near full'),    T['red']),
            'vram': (L.get('bn_vram', 'VRAM near full'),   T['red']),
        }

        def _avg(dq):
            vals = [v for v in dq if v is not None]
            return (sum(vals) / len(vals)) if vals else None

        def _refresh_bn():
            try:
                if not bn_val.winfo_exists():
                    return   # tab switched or window closed → stop the loop
            except Exception:
                return
            w = self.w
            per = list(getattr(w, '_percpu', []) or [])
            cpu_now = (sum(per) / len(per)) if per else None
            gpu_now = getattr(w, '_gpu', None)
            vram_now = None
            gm = getattr(w, '_gpu_mem', None); vt = getattr(w, '_vram_total', None)
            if gm is not None and vt:
                vram_now = gm / vt * 100.0
            try:    ram_now = psutil.virtual_memory().percent
            except Exception: ram_now = None
            # disk active-time %: max busy ratio across physical disks
            disk_now = None
            try:
                now = time.time()
                for name, d in psutil.disk_io_counters(perdisk=True).items():
                    bt = getattr(d, 'busy_time', None)
                    if bt is None:
                        continue
                    prev = _disk_prev.get(name)
                    if prev is not None and now > prev[1]:
                        act = (bt - prev[0]) / ((now - prev[1]) * 1000.0) * 100.0
                        act = max(0.0, min(100.0, act))
                        disk_now = act if disk_now is None else max(disk_now, act)
                    _disk_prev[name] = (bt, now)
            except Exception:
                pass
            for k, v in (('cpu', cpu_now), ('gpu', gpu_now), ('ram', ram_now),
                         ('vram', vram_now), ('disk', disk_now)):
                _buf[k].append(v)
            res = analyze_bottleneck(_avg(_buf['cpu']), per, _avg(_buf['gpu']),
                                     _avg(_buf['ram']), _avg(_buf['vram']),
                                     _avg(_buf['disk']))
            label, color = _VERDICT.get(res['key'], (res['key'], T['text']))
            if res.get('load') is not None and res['key'] in (
                    'cpu', 'gpu', 'ram', 'vram', 'disk'):
                label = f"{label}  ({res['load']:.0f}%)"
            try:
                bn_val.config(text=label, fg=color)
                bn_metrics.config(text=res.get('metrics', ''))
                up_val.config(text=_uptime_str())
                self._win.after(1000, _refresh_bn)
            except Exception:
                pass

        _refresh_bn()

        def _footer():
            # ── Copy-all button ──
            _copy_lbl = '📋  ' + self.L['copy_all']
            def _copy_all():
                try:
                    txt = self._format_sysinfo_text(info)
                    self._win.clipboard_clear()
                    self._win.clipboard_append(txt)
                    cp_btn.config(text='✓  ' + self.L['copied'])
                    self._win.after(1500, lambda: cp_btn.config(text=_copy_lbl))
                except Exception: pass
            cp_btn = tk.Label(body, text=_copy_lbl, fg=T['cyan'], bg=T['bg'],
                              font=('Segoe UI', 10), padx=12, pady=6, cursor='hand2')
            cp_btn.pack(anchor='w', padx=4, pady=8)
            cp_btn.bind('<Button-1>', lambda e: _copy_all())
            # ── Diagnostics: hardware self-test ──
            _diag_lbl = '🩺  ' + self.L.get('run_diag', 'Run diagnostics')
            def _run_diag():
                try:
                    rows = run_diagnostics()
                    txt = format_diagnostics(rows)
                    self._win.clipboard_clear(); self._win.clipboard_append(txt)
                    fails = sum(1 for _, s, _ in rows if s != 'OK')
                    msg = self.L.get('diag_done', '{ok}/{n} OK · copied to clipboard').format(
                        ok=len(rows) - fails, n=len(rows))
                    diag_btn.config(text='✓  ' + msg)
                    self._win.after(3500, lambda: diag_btn.config(text=_diag_lbl))
                except Exception:
                    diag_btn.config(text='⚠  ' + self.L.get('diag_fail', 'Diagnostics failed'))
            diag_btn = tk.Label(body, text=_diag_lbl, fg=T['cyan'], bg=T['bg'],
                                font=('Segoe UI', 10), padx=12, pady=6, cursor='hand2')
            diag_btn.pack(anchor='w', padx=4, pady=(0, 8))
            diag_btn.bind('<Button-1>', lambda e: _run_diag())
            tk.Label(body, text='   ' + self.L.get('diag_hint',
                     'Paste this in a bug report so we can help.'),
                     fg=T['muted'], bg=T['bg'], font=('Segoe UI', 8),
                     anchor='w').pack(anchor='w', padx=4, pady=(0, 10))

        # ── View branch: Summary (Speccy-like) vs Advanced (full detail) ──
        if self.w.cfg.get('sys_view', 'summary') == 'summary':
            self._render_sys_summary(body, info, section, kv, sys_vals)
            _footer()
            return

        # ── Machine (make / model) ──
        mach = info.get('machine', {})
        if mach.get('model') or mach.get('manufacturer'):
            badge = (mach.get('manufacturer', '') + ' ' +
                     mach.get('model', '')).strip()
            s = section(L.get('sys_machine', 'System'), '🖥️', T['blue'],
                        badge_src=badge)
            if mach.get('manufacturer'): kv(s, 'Manufacturer', mach['manufacturer'])
            if mach.get('model'):        kv(s, 'Model', mach['model'])
            if mach.get('family') and mach['family'] != mach.get('model'):
                kv(s, 'Family', mach['family'])
            form = ' '.join(x for x in (mach.get('form', ''),
                                        mach.get('type', '')) if x)
            if form: kv(s, 'Type', form)
            if mach.get('name'): kv(s, 'Device name', mach['name'])
            if mach.get('user'): kv(s, 'Signed in', mach['user'])
            if mach.get('domain'):      kv(s, 'Domain', mach['domain'])
            elif mach.get('workgroup'): kv(s, 'Workgroup', mach['workgroup'])
            tk.Frame(s, bg=T['panel'], height=8).pack()

        # ── CPU ──
        cpu = info.get('cpu', {})
        s = section('CPU', '💻', T['cyan'], badge_src=cpu.get('name', ''))
        if cpu.get('name'): kv(s, 'Model', cpu['name'])
        if cpu.get('manufacturer'): kv(s, 'Vendor', cpu['manufacturer'])
        if cpu.get('cores'):
            kv(s, 'Cores / Threads',
               f"{cpu['cores']} / {cpu.get('threads', cpu['cores'])}")
        if cpu.get('base_mhz'):
            base_ghz = cpu['base_mhz'] / 1000
            cur = cpu.get('current_mhz')
            kv(s, 'Clock',
               f"{cpu.get('current_mhz', cpu['base_mhz'])/1000:.2f} GHz / base {base_ghz:.2f} GHz")
        if cpu.get('l2_kb'):
            kv(s, 'L2 cache', f"{cpu['l2_kb']/1024:.0f} MB")
        if cpu.get('l3_kb'):
            kv(s, 'L3 cache', f"{cpu['l3_kb']/1024:.0f} MB")
        if cpu.get('socket'):
            kv(s, 'Socket', cpu['socket'])
        if cpu.get('virt') is not None:
            kv(s, 'Virtualization', 'Enabled' if cpu['virt'] else 'Disabled',
               T['green'] if cpu['virt'] else T['muted'])
        tk.Frame(s, bg=T['panel'], height=8).pack()

        # ── RAM ──
        ram = info.get('ram', {})
        s = section('RAM', '🧠', T['green'])
        if ram.get('total'):
            kv(s, 'Total', _human_bytes(ram['total'])
               + (f"  ·  {ram['type']}" if ram.get('type') else ''))
            kv(s, 'In use', f"{_human_bytes(ram['used'])}  ({ram['percent']:.0f}%)",
               T['orange'])
            kv(s, 'Free', _human_bytes(ram['free']), T['green'])
        if ram.get('swap_total'):
            kv(s, 'Page file',
               f"{_human_bytes(ram['swap_used'])} / {_human_bytes(ram['swap_total'])}")
        if ram.get('slots'):
            used = len([m for m in ram.get('modules', []) if m.get('capacity')])
            sl = f"{used} / {ram['slots']} used"
            if ram.get('max_bytes'): sl += f"  ·  max {_human_bytes(ram['max_bytes'])}"
            kv(s, 'Slots', sl)
        for i, m in enumerate(ram.get('modules', [])[:8]):
            cap = _human_bytes(m['capacity']) if m['capacity'] else '?'
            spd = f"{m['speed']} MHz" if m.get('speed') else ''
            mfr = (m.get('mfr') or '').strip()
            slot = (m.get('slot') or '').strip()
            details = ' · '.join(x for x in (cap, spd, mfr) if x)
            kv(s, slot or f'Module {i+1}', details)
        tk.Frame(s, bg=T['panel'], height=8).pack()

        # ── GPU ──
        gpus = info.get('gpu', [])
        if gpus:
            s = section('GPU', '🎮', T['magenta'],
                        badge_src=gpus[0].get('name', ''))
            for g in gpus:
                kv(s, 'Model', g.get('name', '?'))
                if g.get('vendor'):    kv(s, 'Vendor', g['vendor'])
                if g.get('processor') and g['processor'] != g.get('name'):
                    kv(s, 'Processor', g['processor'])
                if g.get('vram'):
                    kv(s, 'VRAM', _human_bytes(g['vram']))
                if g.get('driver'):
                    kv(s, 'Driver', g['driver'])
                if g.get('driver_date'):
                    kv(s, 'Driver date', g['driver_date'])
                if g.get('res') and g['res'][0]:
                    res = f"{g['res'][0]} × {g['res'][1]}"
                    if g.get('hz'): res += f"  @ {g['hz']} Hz"
                    if g.get('bpp'): res += f"  ·  {g['bpp']}-bit"
                    kv(s, 'Resolution', res)
                tk.Frame(s, bg=T['panel'], height=6).pack()
            # live usage + VRAM in use (from the widget's own GPU counters)
            gu = getattr(self.w, '_gpu', None)
            if gu is not None:
                kv(s, 'Usage (live)', f"{gu:.0f}%",
                   T['orange'] if gu >= 80 else T['green'])
            gm = getattr(self.w, '_gpu_mem', None)
            vt = getattr(self.w, '_vram_total', None)
            if gm is not None and vt:
                kv(s, 'VRAM in use',
                   f"{gm:.1f} / {vt:.1f} GB  ({gm/vt*100:.0f}%)")
            tk.Frame(s, bg=T['panel'], height=2).pack()

        # ── Motherboard ──
        mb = info.get('mobo', {})
        if mb.get('product') or mb.get('manufacturer'):
            badge = mb.get('manufacturer','') + ' ' + mb.get('product','')
            s = section(self.L['sys_mobo'], '🔌', T['orange'], badge_src=badge)
            if mb.get('manufacturer'): kv(s, 'Vendor', mb['manufacturer'])
            if mb.get('product'):      kv(s, 'Model',  mb['product'])
            if mb.get('version'):      kv(s, 'Version', mb['version'])
            bios = info.get('bios', {})
            if bios.get('version'):
                bv = bios['version']
                if bios.get('date'): bv += '  ·  ' + bios['date']
                kv(s, 'BIOS', bv)
            tk.Frame(s, bg=T['panel'], height=8).pack()

        # ── Monitors ──
        mons = info.get('monitors', [])
        if mons:
            for i, m in enumerate(mons):
                title = self.L['sys_monitor'] + ('' if len(mons) == 1 else f' {i+1}')
                badge = (m.get('manufacturer','') + ' ' + m.get('model','')).strip()
                s = section(title, '🖥️', T['cyan'], badge_src=badge)
                if m.get('manufacturer'): kv(s, 'Vendor', m['manufacturer'])
                if m.get('model'):        kv(s, 'Model',  m['model'])
                if m.get('code'):         kv(s, 'Code',   m['code'])
                if m.get('year'):         kv(s, 'Year',   m['year'])
                tk.Frame(s, bg=T['panel'], height=8).pack()

        # ── Audio ──
        audios = info.get('audio', [])
        if audios:
            s = section(self.L['sys_audio'], '🎧', T['magenta'],
                        badge_src=audios[0].get('manufacturer','') + ' ' + audios[0].get('name',''))
            for a in audios:
                kv(s, a.get('manufacturer', '') or 'Device', a['name'][:60])
            tk.Frame(s, bg=T['panel'], height=8).pack()

        # ── Optical drives ──
        opts = info.get('optical', [])
        if opts:
            s = section(self.L['sys_optical'], '📀', T['orange'])
            for o in opts:
                lbl = o.get('drive', '') or o.get('manufacturer', '') or 'Drive'
                kv(s, lbl, o['name'][:60])
            tk.Frame(s, bg=T['panel'], height=8).pack()

        # ── OS ──
        os_ = info.get('os', {})
        s = section('Windows', '🪟', T['blue'])
        if os_.get('name'): kv(s, 'Edition', os_['name'])
        if os_.get('version'):
            v = os_['version']
            if os_.get('build'): v += f"  (build {os_['build']})"
            kv(s, 'Version', v)
        if os_.get('arch'): kv(s, 'Architecture', os_['arch'])
        if os_.get('installed'): kv(s, 'Installed', os_['installed'])
        if os_.get('activated') is not None:
            kv(s, 'Activation', 'Activated' if os_['activated'] else 'Not activated',
               T['green'] if os_['activated'] else T['orange'])
        # (uptime now lives in the live "Performance" section above)
        tk.Frame(s, bg=T['panel'], height=8).pack()

        # ── Security (Secure Boot + TPM) ──
        sec = info.get('security', {})
        if sec:
            s = section(L.get('sys_security', 'Security'), '🔐', T['green'])
            sb = sec.get('secure_boot')
            if sb is not None:
                kv(s, 'Secure Boot', 'On' if sb else 'Off',
                   T['green'] if sb else T['orange'])
            if sec.get('firmware'): kv(s, 'Firmware', sec['firmware'])
            if sec.get('tpm_present'):
                v = 'TPM ' + (sec.get('tpm_version') or '?')
                if not sec.get('tpm_enabled'): v += '  (disabled)'
                kv(s, 'TPM', v,
                   T['green'] if sec.get('tpm_enabled') else T['orange'])
            tk.Frame(s, bg=T['panel'], height=8).pack()

        # ── Physical drives (SSD/HDD hardware) ──
        drives = info.get('drives', [])
        if drives:
            s = section(L.get('sys_drives', 'Drives'), '🖴', T['orange'],
                        badge_src=drives[0].get('model', ''))
            for d in drives:
                bits = []
                if d.get('size'): bits.append(_human_bytes(d['size']))
                if d.get('kind'): bits.append(d['kind'])
                if d.get('bus'):  bits.append(d['bus'])
                kv(s, d.get('kind') or 'Drive', d['model'])
                if bits:
                    kv(s, '', '  ·  '.join(bits))
                if d.get('status'):
                    ok = d['status'].lower() == 'ok'
                    kv(s, '', ('✓ ' if ok else '⚠ ') + ('Healthy' if ok else d['status']),
                       T['green'] if ok else T['orange'])
            tk.Frame(s, bg=T['panel'], height=8).pack()

        # ── Disks ──
        disks = info.get('disks', [])
        if disks:
            s = section(self.L['sys_storage'], '💿', T['orange'])
            for d in disks:
                kv(s, d['device'],
                   f"{_human_bytes(d['used'])} used of {_human_bytes(d['total'])}  "
                   f"({d['percent']:.0f}%)  ·  {d.get('fstype','')}")
            tk.Frame(s, bg=T['panel'], height=8).pack()

        # ── Network ──
        nets = info.get('net', [])
        if nets:
            s = section(self.L['sys_network'], '🌐', T['cyan'])
            for n in nets:
                bits = []
                if n.get('ip'): bits.append(f"IP {n['ip']}")
                if n.get('mac'): bits.append(f"MAC {n['mac']}")
                if n.get('speed_mbps'):
                    bits.append(f"{n['speed_mbps']} Mbps")
                kv(s, n['name'][:30], '  ·  '.join(bits))
            ni = info.get('net_info', {})
            if ni.get('gateway'): kv(s, 'Gateway', ni['gateway'])
            if ni.get('dns'):     kv(s, 'DNS', ', '.join(ni['dns']))
            if ni.get('public_ip'): kv(s, 'Public IP', ni['public_ip'])
            tk.Frame(s, bg=T['panel'], height=8).pack()

        # ── Battery (kept near the bottom) ──
        batt = info.get('battery', {})
        if batt.get('percent') is not None:
            s = section(L.get('sys_battery', 'Battery'), '🔋', T['green'])
            pct = batt['percent']
            pct_col = T['green'] if pct > 40 else (T['orange'] if pct > 15 else T['red'])
            if batt.get('plugged'):
                state = 'Fully charged' if pct >= 99 else 'Charging'
            else:
                state = 'On battery (discharging)'
            if batt.get('left') and not batt.get('plugged'):
                state += f"  ·  {batt['left']} left"
            kv(s, 'Charge', f"{pct}%", pct_col)
            kv(s, 'Status', state)
            if batt.get('health') is not None:
                h = batt['health']
                kv(s, 'Health', f"{h}%  ({'Good' if h >= 80 else 'Fair' if h >= 60 else 'Poor'})",
                   T['green'] if h >= 80 else (T['orange'] if h >= 60 else T['red']))
            if batt.get('full_mwh'):
                cap = f"{batt['full_mwh']/1000:.1f} Wh"
                if batt.get('design_mwh'):
                    cap += f"  (design {batt['design_mwh']/1000:.1f} Wh)"
                kv(s, 'Capacity', cap)
            if batt.get('voltage'):   kv(s, 'Voltage', f"{batt['voltage']} V")
            if batt.get('cycles'):    kv(s, 'Cycles', str(batt['cycles']))
            if batt.get('name'):      kv(s, 'Model', batt['name'])
            if batt.get('chemistry'): kv(s, 'Chemistry', batt['chemistry'])
            tk.Frame(s, bg=T['panel'], height=8).pack()

        _footer()

    def _render_sys_summary(self, body, info, section, kv, sys_vals):
        """Compact "at a glance" view (Speccy-style) — the key specs only."""
        T = self.T; L = self.L
        mach = info.get('machine', {}); cpu = info.get('cpu', {})
        ram = info.get('ram', {}); gpus = info.get('gpu', [])
        os_ = info.get('os', {}); sec = info.get('security', {})
        badge = (mach.get('manufacturer', '') + ' ' + mach.get('model', '')).strip()
        s = section(L.get('sys_summary', 'Summary'), '⭐', T['cyan'], badge_src=badge)
        if mach.get('model'):
            mfr = (mach.get('manufacturer', '') + ' ') if mach.get('manufacturer') else ''
            kv(s, L.get('sys_machine', 'System'), mfr + mach['model'])
        if cpu.get('name'):
            extra = ''
            if cpu.get('cores'):
                extra += f"  ·  {cpu['cores']}C / {cpu.get('threads', cpu['cores'])}T"
            if cpu.get('base_mhz'):
                extra += f"  ·  {cpu['base_mhz']/1000:.2f} GHz"
            kv(s, 'CPU', cpu['name'] + extra)
        if ram.get('total'):
            rv = _human_bytes(ram['total'])
            mods = [m for m in ram.get('modules', []) if m.get('capacity')]
            if mods:
                rv += f"  ·  {len(mods)} DIMM"
                if ram.get('type'):      rv += f"  ·  {ram['type']}"
                if mods[0].get('speed'): rv += f"  ·  {mods[0]['speed']} MHz"
            if ram.get('slots'):
                rv += f"  ({len(mods)}/{ram['slots']} slots)"
            kv(s, 'RAM', rv)
        if gpus:
            kv(s, 'GPU', ', '.join(g.get('name', '') for g in gpus if g.get('name')))
        mb = info.get('mobo', {})
        if mb.get('product') or mb.get('manufacturer'):
            kv(s, L.get('sys_mobo', 'Motherboard'),
               (mb.get('manufacturer', '') + ' ' + mb.get('product', '')).strip())
        tot = sum(d.get('size', 0) for d in info.get('drives', [])) \
            or sum(d.get('total', 0) for d in info.get('disks', []))
        if tot:
            kv(s, L.get('sys_storage', 'Storage'), _human_bytes(tot))
        if gpus and gpus[0].get('res') and gpus[0]['res'][0]:
            g0 = gpus[0]
            disp = f"{g0['res'][0]} × {g0['res'][1]}"
            if g0.get('hz'): disp += f"  @ {g0['hz']} Hz"
            kv(s, L.get('sys_monitor', 'Display'), disp)
        if os_.get('name'):
            ov = os_['name']
            if os_.get('build'): ov += f"  (build {os_['build']})"
            if os_.get('activated') is not None:
                ov += '  ·  ' + ('activated' if os_['activated'] else 'not activated')
            kv(s, 'Windows', ov,
               (T['green'] if os_.get('activated') else None))
        bits = []
        if sec.get('secure_boot') is not None:
            bits.append('Secure Boot ' + ('On' if sec['secure_boot'] else 'Off'))
        if sec.get('firmware'): bits.append(sec['firmware'])
        if sec.get('tpm_present'): bits.append('TPM ' + (sec.get('tpm_version') or ''))
        if bits:
            kv(s, L.get('sys_security', 'Security'), '  ·  '.join(bits))
        batt = info.get('battery', {})
        if batt.get('percent') is not None:
            st = 'Charging' if batt.get('plugged') else 'On battery'
            bv = f"{batt['percent']}%  ·  {st}"
            if batt.get('left') and not batt.get('plugged'):
                bv += f"  ·  {batt['left']} left"
            pct = batt['percent']
            kv(s, L.get('sys_battery', 'Battery'), bv,
               T['green'] if pct > 40 else (T['orange'] if pct > 15 else T['red']))
        up = os_.get('uptime') or _uptime_str()
        if up: kv(s, L.get('sys_uptime', 'Uptime'), up)
        tk.Frame(s, bg=T['panel'], height=8).pack()

    def _format_sysinfo_text(self, info):
        """Plain-text version of the system info for clipboard / support."""
        lines = [f'{DISPLAY_NAME} System Info  ·  {time.strftime("%Y-%m-%d %H:%M")}', '']
        mach = info.get('machine', {})
        if mach.get('model') or mach.get('manufacturer'):
            lines.append('System')
            for k in ('manufacturer','model','family','form','type'):
                v = mach.get(k)
                if v: lines.append(f'  {k}: {v}')
            lines.append('')
        cpu = info.get('cpu', {})
        if cpu:
            lines.append('CPU')
            for k in ('name','manufacturer','cores','threads','base_mhz','current_mhz','l3_kb','socket'):
                v = cpu.get(k)
                if v: lines.append(f'  {k}: {v}')
            lines.append('')
        ram = info.get('ram', {})
        if ram:
            lines.append('RAM')
            lines.append(f"  total: {_human_bytes(ram.get('total',0))}")
            lines.append(f"  used:  {_human_bytes(ram.get('used',0))} ({ram.get('percent',0):.0f}%)")
            for m in ram.get('modules', []):
                lines.append(f"  module: {_human_bytes(m.get('capacity',0))} @ {m.get('speed','?')} MHz  ({m.get('mfr','?')})")
            lines.append('')
        for g in info.get('gpu', []):
            lines.append(f"GPU: {g.get('name')}  ·  VRAM {_human_bytes(g.get('vram',0))}  ·  driver {g.get('driver','?')}")
        if info.get('gpu'): lines.append('')
        os_ = info.get('os', {})
        if os_:
            lines.append(f"OS: {os_.get('name','?')}  ·  build {os_.get('build','?')}  ·  {os_.get('arch','?')}")
            if os_.get('installed'): lines.append(f"Installed: {os_['installed']}")
            lines.append(f"Uptime: {os_.get('uptime','?')}")
            lines.append('')
        sec = info.get('security', {})
        if sec:
            sb = sec.get('secure_boot')
            sb_txt = ('on' if sb else 'off') if sb is not None else 'unknown'
            line = f"Secure Boot: {sb_txt}"
            if sec.get('tpm_present'):
                line += f"  ·  TPM {sec.get('tpm_version','?')}" + (
                    '' if sec.get('tpm_enabled') else ' (disabled)')
            lines.append(line); lines.append('')
        for d in info.get('drives', []):
            bits = [x for x in (_human_bytes(d['size']) if d.get('size') else '',
                                d.get('kind',''), d.get('bus','')) if x]
            lines.append(f"Drive: {d['model']}" + (('  ·  ' + '  ·  '.join(bits)) if bits else ''))
        if info.get('drives'): lines.append('')
        for d in info.get('disks', []):
            lines.append(f"Disk {d['device']}: {_human_bytes(d['used'])} / {_human_bytes(d['total'])} ({d['percent']:.0f}%)")
        if info.get('disks'): lines.append('')
        for n in info.get('net', []):
            lines.append(f"Net {n['name']}: IP {n.get('ip','?')}  MAC {n.get('mac','?')}  speed {n.get('speed_mbps','?')} Mbps")
        batt = info.get('battery', {})
        if batt.get('percent') is not None:
            state = 'charging' if batt.get('plugged') else 'on battery'
            extra = f"  ·  {batt['left']} left" if batt.get('left') else ''
            lines.append('')
            lines.append(f"Battery: {batt['percent']}%  ·  {state}{extra}"
                         + (f"  ·  {batt.get('chemistry')}" if batt.get('chemistry') else ''))
        return '\n'.join(lines)

    # ── Tools tab (v2.8): safe shortcuts to built-in Windows utilities ──
    def _tab_tools(self):
        T = self.T; L = self.L
        # header + subtitle
        f = tk.Frame(self._content, bg=T['bg'])
        f.pack(side='top', fill='x', padx=24, pady=(14, 2))
        tk.Label(f, text='🧰  ' + L.get('tools', 'Tools'), fg=T['text'], bg=T['bg'],
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        # subtitle doubles as a hover hint: shows each tool's description on hover
        _default_sub = '   ' + L.get('tools_sub', '')
        sub_lbl = tk.Label(self._content, text=_default_sub, fg=T['muted'],
                           bg=T['bg'], font=('Segoe UI', 9), anchor='w')
        sub_lbl.pack(side='top', anchor='w', padx=24, fill='x')
        def _hint(tkey):
            d = L.get('desc__' + tkey, '')
            sub_lbl.config(text='   ' + d, fg=T['cyan']) if d else sub_lbl.config(
                text=_default_sub, fg=T['muted'])
        def _hint_clear():
            sub_lbl.config(text=_default_sub, fg=T['muted'])
        tk.Frame(self._content, bg=T['line'], height=1).pack(
            side='top', fill='x', padx=24, pady=(6, 0))
        # search box + layout toggle (one row)
        sr = tk.Frame(self._content, bg=T['bg'])
        sr.pack(side='top', fill='x', padx=24, pady=(10, 2))
        # layout toggle on the right (List / Tiles)
        toggle = tk.Frame(sr, bg=T['bg']); toggle.pack(side='right', padx=(8, 0))
        _btns = {}
        def _style_toggle():
            cur = self.w.cfg.get('tools_layout', 'list')
            for m, b in _btns.items():
                if m == cur:
                    b.config(bg=T['cyan'], fg='#0d1117')
                else:
                    b.config(bg=T['panel'], fg=T['muted'])
        def _set_layout(mode):
            if self.w.cfg.get('tools_layout') == mode:
                return
            self.w._set('tools_layout', mode)
            _last_q[0] = '\x00'      # force a rebuild: same query, new layout
            _style_toggle(); _paint()
        for mode, icon in (('list', '≣'), ('grid', '▦')):
            b = tk.Label(toggle, text=icon, font=('Segoe UI', 13), padx=10, pady=2,
                         bg=T['panel'], fg=T['muted'], cursor='hand2')
            b.pack(side='left', padx=1)
            b.bind('<Button-1>', lambda e, m=mode: _set_layout(m))
            _btns[mode] = b
        # section title on the left of the toggle row (search removed)
        tk.Label(sr, text=L.get('tools', 'Tools'), fg=T['muted'], bg=T['bg'],
                 font=('Segoe UI', 10), anchor='w').pack(side='left')
        svar = tk.StringVar()          # always empty → the list shows everything
        # scrollable body
        outer = tk.Frame(self._content, bg=T['bg'])
        outer.pack(fill='both', expand=True, padx=20, pady=4)
        canvas = tk.Canvas(outer, bg=T['bg'], highlightthickness=0, bd=0)
        sb = tk.Scrollbar(outer, orient='vertical', command=canvas.yview,
                          bg=T['panel'], troughcolor=T['bg2'], activebackground=T['cyan'],
                          bd=0, highlightthickness=0, width=10)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y'); canvas.pack(side='left', fill='both', expand=True)
        body = tk.Frame(canvas, bg=T['bg'])
        body_window = canvas.create_window((0, 0), window=body, anchor='nw')
        TILE_W = 150
        _grid_groups = []   # [(container_frame, [tile_widgets])]

        def _relayout_grid(cols=None):
            if cols is None:
                w = canvas.winfo_width() or 400
                cols = max(1, (w - 10) // TILE_W)
            for cont, tiles in _grid_groups:
                for c in range(cols):
                    cont.grid_columnconfigure(c, weight=1, uniform='tile')
                for i, t in enumerate(tiles):
                    t.grid(row=i // cols, column=i % cols, padx=4, pady=4, sticky='nsew')
            try: canvas.configure(scrollregion=canvas.bbox('all'))
            except Exception: pass

        def _on_canvas_configure(e, _wid=body_window):
            try: canvas.itemconfig(_wid, width=e.width)
            except Exception: pass
            if self.w.cfg.get('tools_layout') == 'grid' and _grid_groups:
                _relayout_grid()
        canvas.bind('<Configure>', _on_canvas_configure)
        body.bind('<Configure>',
                  lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind_all('<MouseWheel>',
                        lambda e: canvas.yview_scroll(int(-e.delta / 120), 'units'))

        def _tool_row(parent, tkey, ticon, label, action):
            destructive = action[0] == 'action' and action[1] not in (
                'flush_dns', 'classic_context')
            row = tk.Frame(parent, bg=T['panel'], cursor='hand2')
            row.pack(fill='x', padx=10, pady=2)
            inner = tk.Frame(row, bg=T['panel']); inner.pack(fill='x', padx=8, pady=7)
            tk.Label(inner, text=ticon, bg=T['panel'], fg=T['text'],
                     font=('Segoe UI', 11), width=2).pack(side='left')
            tk.Label(inner, text=label, bg=T['panel'],
                     fg=(T['orange'] if destructive else T['text']),
                     font=('Segoe UI', 10), anchor='w').pack(side='left', padx=(4, 0))
            tk.Label(inner, text='›', bg=T['panel'], fg=T['muted'],
                     font=('Segoe UI', 12)).pack(side='right')
            kids = [inner] + list(inner.winfo_children())
            def _enter(_e):
                row.config(bg=T['bg2'])
                for c in kids: c.config(bg=T['bg2'])
                _hint(tkey)
            def _leave(_e):
                row.config(bg=T['panel'])
                for c in kids: c.config(bg=T['panel'])
                _hint_clear()
            def _click(_e): self._run_tool(action)
            for wgt in (row, *kids):
                wgt.bind('<Enter>', _enter); wgt.bind('<Leave>', _leave)
                wgt.bind('<Button-1>', _click)

        def _tool_tile(parent, tkey, ticon, label, action):
            destructive = action[0] == 'action' and action[1] not in (
                'flush_dns', 'classic_context')
            tile = tk.Frame(parent, bg=T['panel'], cursor='hand2',
                            highlightbackground=T['line'], highlightthickness=1,
                            width=TILE_W - 14, height=82)
            tile.pack_propagate(False)
            tk.Label(tile, text=ticon, bg=T['panel'], fg=T['text'],
                     font=('Segoe UI', 16)).pack(pady=(13, 1))
            tk.Label(tile, text=label, bg=T['panel'],
                     fg=(T['orange'] if destructive else T['text']),
                     font=('Segoe UI', 8), wraplength=TILE_W - 24,
                     justify='center').pack()
            kids = [tile] + list(tile.winfo_children())
            def _enter(_e):
                for c in kids: c.config(bg=T['bg2'])
                _hint(tkey)
            def _leave(_e):
                for c in kids: c.config(bg=T['panel'])
                _hint_clear()
            def _click(_e): self._run_tool(action)
            for wgt in kids:
                wgt.bind('<Enter>', _enter); wgt.bind('<Leave>', _leave)
                wgt.bind('<Button-1>', _click)
            return tile

        _last_q = ['\x00']   # sentinel; closure-local so it resets per tab build
        def _paint(*_a):
            q = svar.get().strip().lower()
            # Only rebuild when the effective query actually changed.  Clearing
            # the placeholder ('' → '') yields the same list, so skipping the
            # destroy+rebuild here keeps the search Entry's keyboard focus alive
            # (rebuilding mid-click was stealing focus and reloading the tab).
            if q == _last_q[0]:
                return
            _last_q[0] = q
            for c in body.winfo_children():
                c.destroy()
            _grid_groups.clear()
            mode = self.w.cfg.get('tools_layout', 'list')
            shown = False
            for cat_key, cicon, tools in TOOLS_CATALOG:
                matches = [(tkey, ticon, action) for tkey, ticon, action in tools
                           if q in L.get(tkey, tkey).lower()]
                if not matches:
                    continue
                shown = True
                sf = tk.Frame(body, bg=T['panel']); sf.pack(fill='x', pady=(6, 4))
                hdr = tk.Frame(sf, bg=T['panel']); hdr.pack(fill='x', padx=12, pady=(8, 4))
                tk.Label(hdr, text=cicon + '  ' + L.get(cat_key, cat_key), fg=T['cyan'],
                         bg=T['panel'], font=('Segoe UI', 11, 'bold')).pack(side='left')
                if mode == 'grid':
                    cont = tk.Frame(sf, bg=T['panel'])
                    cont.pack(fill='x', padx=10, pady=(0, 8))
                    tiles = [_tool_tile(cont, tkey, ticon, L.get(tkey, tkey), action)
                             for tkey, ticon, action in matches]
                    _grid_groups.append((cont, tiles))
                else:
                    for tkey, ticon, action in matches:
                        _tool_row(sf, tkey, ticon, L.get(tkey, tkey), action)
                    tk.Frame(sf, bg=T['panel'], height=8).pack()
            if not shown:
                tk.Label(body, text=L.get('no_match', 'No matching tools'),
                         fg=T['muted'], bg=T['bg'], font=('Segoe UI', 10)).pack(pady=24)
            if mode == 'grid' and _grid_groups:
                self._win.after_idle(_relayout_grid)
            try: canvas.configure(scrollregion=canvas.bbox('all'))
            except Exception: pass

        _style_toggle()
        _paint()

    def _run_tool(self, action):
        """Open a tool, or run a confirmed safe action."""
        L = self.L
        kind, target = action
        if kind != 'action':
            launch_tool(action)
            return
        if target == 'dns_boost':
            self.show_tab('dns')          # full DNS Boost panel, returns via its Back link
            return
        if target == 'flush_dns':
            action_flush_dns()
            self._tool_toast(L.get('tt_dns', 'DNS cache flushed'))
        elif target == 'clear_temp':
            self._confirm(L.get('cf_temp', 'Delete temporary files?'),
                          self._do_clear_temp)
        elif target == 'empty_recyclebin':
            self._confirm(L.get('cf_bin', 'Empty the Recycle Bin?'),
                          self._do_empty_bin)
        elif target == 'reset_gpu':
            self._confirm(L.get('cf_gpu', 'Reset the graphics driver?'),
                          self._do_gpu_reset)
        elif target == 'restart_explorer':
            self._confirm(L.get('cf_expl', 'Restart Explorer? Your open File Explorer windows will close.'),
                          self._do_restart_explorer)
        elif target == 'hibernate':
            self._confirm(L.get('cf_hib', 'Hibernate the PC now? Open work will be saved.'),
                          self._do_hibernate)
        elif target == 'lock_screen':
            action_lock_screen()
        elif target == 'classic_context':
            if is_classic_context():
                self._confirm(L.get('cf_ctx_off',
                    'Restore the Windows 11 right-click menu? Explorer will restart.'),
                    lambda: self._do_classic_context(False))
            else:
                self._confirm(L.get('cf_ctx_on',
                    'Switch to the classic (Windows 10) right-click menu? Explorer will restart.'),
                    lambda: self._do_classic_context(True))

    def _do_classic_context(self, enable):
        if action_classic_context(enable):
            self._tool_toast(self.L.get('tt_ctx_on', 'Classic right-click menu enabled')
                             if enable else
                             self.L.get('tt_ctx_off', 'Windows 11 right-click menu restored'))

    def _do_clear_temp(self):
        freed = action_clear_temp()
        msg = self.L.get('tt_temp', 'Temp cleared — {n}').format(
            n=_human_bytes(freed))
        self._tool_toast(msg)

    def _do_empty_bin(self):
        action_empty_recyclebin()
        self._tool_toast(self.L.get('tt_bin', 'Recycle Bin emptied'))

    def _do_gpu_reset(self):
        action_reset_gpu_driver()
        # No toast — the screen blanks for ~0.5 s; another popup would feel busy.

    def _do_restart_explorer(self):
        action_restart_explorer()

    def _do_hibernate(self):
        action_hibernate()

    def _tool_toast(self, msg):
        try:
            self.w._toast(msg)
        except Exception:
            pass

    def _confirm(self, msg, on_yes):
        """Small modal yes/cancel dialog centered over the Customize window."""
        T = self.T; L = self.L
        W = 380   # fixed width so the message wraps predictably
        dlg = tk.Toplevel(self._win); dlg.overrideredirect(True)
        dlg.configure(bg=T['panel'], highlightbackground=T['line'],
                      highlightthickness=1)
        try: dlg.attributes('-topmost', True)
        except Exception: pass
        tk.Label(dlg, text=msg, fg=T['text'], bg=T['panel'], font=('Segoe UI', 10),
                 wraplength=W - 44, justify='left').pack(
                     anchor='w', padx=20, pady=(18, 14))
        btns = tk.Frame(dlg, bg=T['panel']); btns.pack(fill='x', padx=20, pady=(0, 16))
        def _close():
            try: dlg.grab_release()
            except Exception: pass
            try: dlg.destroy()
            except Exception: pass
        no = tk.Label(btns, text=L.get('cf_no', 'Cancel'), fg=T['muted'], bg=T['bg2'],
                      font=('Segoe UI', 10), padx=16, pady=6, cursor='hand2')
        no.pack(side='right')
        no.bind('<Button-1>', lambda e: _close())
        yes = tk.Label(btns, text=L.get('cf_yes', 'Yes'), fg='white', bg=T['red'],
                       font=('Segoe UI', 10, 'bold'), padx=16, pady=6, cursor='hand2')
        yes.pack(side='right', padx=(0, 8))
        def _go(_e):
            _close()
            try: on_yes()
            except Exception: pass
        yes.bind('<Button-1>', _go)
        # height from content (width is fixed), then center over the window
        dlg.update_idletasks()
        h_ = max(108, dlg.winfo_reqheight())
        px = self._win.winfo_rootx() + (self._win.winfo_width() - W) // 2
        py = self._win.winfo_rooty() + (self._win.winfo_height() - h_) // 2
        dlg.geometry(f'{W}x{h_}+{max(0, px)}+{max(0, py)}')
        dlg.lift(); dlg.update()
        try: dlg.grab_set()
        except Exception: pass

    # ── DNS Boost tab (v2.8): benchmark resolvers, no system changes ──
    def _tab_dns(self):
        T = self.T; L = self.L
        f = tk.Frame(self._content, bg=T['bg'])
        f.pack(side='top', fill='x', padx=24, pady=(14, 2))
        tk.Label(f, text='🚀  DNS Boost', fg=T['text'], bg=T['bg'],
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        # back to Tools (DNS Boost lives inside the Tools tab now)
        back = tk.Label(f, text='←  ' + L.get('tools', 'Tools'), fg=T['cyan'], bg=T['bg'],
                        font=('Segoe UI', 9), cursor='hand2')
        back.pack(side='right')
        back.bind('<Button-1>', lambda e: self.show_tab('tools'))
        tk.Label(self._content, text='   ' + L.get('dns_sub', ''), fg=T['muted'],
                 bg=T['bg'], font=('Segoe UI', 9)).pack(side='top', anchor='w', padx=24)
        tk.Frame(self._content, bg=T['line'], height=1).pack(
            side='top', fill='x', padx=24, pady=(6, 0))
        # action row
        ar = tk.Frame(self._content, bg=T['bg'])
        ar.pack(side='top', fill='x', padx=24, pady=(12, 6))
        find_btn = tk.Label(ar, text='🚀  ' + L.get('dns_find', 'Find fastest DNS'),
                            fg='white', bg=T['cyan'], font=('Segoe UI', 10, 'bold'),
                            padx=16, pady=8, cursor='hand2')
        find_btn.pack(side='left')
        status = tk.Label(ar, text='', fg=T['muted'], bg=T['bg'], font=('Segoe UI', 9))
        status.pack(side='left', padx=12)
        # bottom: open network settings + how-to (packed before the scroll body
        # so it always stays visible at the bottom)
        bottom = tk.Frame(self._content, bg=T['bg'])
        bottom.pack(side='bottom', fill='x', padx=24, pady=(4, 12))
        opennet = tk.Label(bottom, text='🔧  ' + L.get('dns_opennet', 'Open network settings'),
                           fg=T['cyan'], bg=T['panel'], font=('Segoe UI', 9),
                           padx=12, pady=6, cursor='hand2')
        opennet.pack(side='left')
        opennet.bind('<Button-1>', lambda e: launch_tool(('applet', 'ncpa.cpl')))
        tk.Label(bottom, text=L.get('dns_howto', ''), fg=T['muted'], bg=T['bg'],
                 font=('Segoe UI', 8), wraplength=420, justify='left').pack(
                     side='left', padx=12)
        # results area (scrollable)
        outer = tk.Frame(self._content, bg=T['bg'])
        outer.pack(fill='both', expand=True, padx=20, pady=4)
        canvas = tk.Canvas(outer, bg=T['bg'], highlightthickness=0, bd=0)
        sb = tk.Scrollbar(outer, orient='vertical', command=canvas.yview,
                          bg=T['panel'], troughcolor=T['bg2'], activebackground=T['cyan'],
                          bd=0, highlightthickness=0, width=10)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y'); canvas.pack(side='left', fill='both', expand=True)
        body = tk.Frame(canvas, bg=T['bg'])
        body_window = canvas.create_window((0, 0), window=body, anchor='nw')
        canvas.bind('<Configure>',
                    lambda e: canvas.itemconfig(body_window, width=e.width))
        body.bind('<Configure>',
                  lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind_all('<MouseWheel>',
                        lambda e: canvas.yview_scroll(int(-e.delta / 120), 'units'))

        def _copy(ip):
            try:
                self._win.clipboard_clear(); self._win.clipboard_append(ip)
                self.w._toast(L.get('dns_copied', 'Copied'))
            except Exception:
                pass

        def _ms(v):
            return f'{v:.0f} ms' if v is not None else '—'

        def _addr_line(parent, bg, tag, addr, ms, val_color):
            ln = tk.Frame(parent, bg=bg); ln.pack(fill='x', pady=1)
            tk.Label(ln, text=tag, fg=T['muted'], bg=bg, font=('Segoe UI', 8),
                     width=5, anchor='w').pack(side='left')
            tk.Label(ln, text=addr, fg=T['text'], bg=bg, font=('Consolas', 9),
                     anchor='w').pack(side='left')
            cp = tk.Label(ln, text='📋', fg=T['cyan'], bg=bg, font=('Segoe UI', 9),
                          cursor='hand2', padx=6)
            cp.pack(side='right')
            cp.bind('<Button-1>', lambda e, ip=addr: _copy(ip))
            tk.Label(ln, text=_ms(ms), fg=val_color, bg=bg, font=('Segoe UI', 9),
                     width=8, anchor='e').pack(side='right', padx=6)

        def _render(results, ipv6_ok):
            for c in body.winfo_children():
                c.destroy()
            # the fastest badge goes to the quickest non-current resolver
            best_i = None
            for i, r in enumerate(results):
                if not r[5] and r[2] is not None:
                    best_i = i; break
            for idx, (name, v4, v4ms, v6, v6ms, is_cur) in enumerate(results):
                best = idx == best_i
                rowbg = T['bg2'] if (best or is_cur) else T['panel']
                hicol = T['cyan'] if is_cur else (T['green'] if best else T['text'])
                row = tk.Frame(body, bg=rowbg); row.pack(fill='x', pady=2)
                hd = tk.Frame(row, bg=rowbg); hd.pack(fill='x', padx=12, pady=(7, 2))
                tk.Label(hd, text=name, fg=hicol, bg=rowbg,
                         font=('Segoe UI', 10, 'bold' if (best or is_cur) else 'normal'),
                         anchor='w').pack(side='left')
                if is_cur:
                    tk.Label(hd, text='📍 ' + L.get('dns_current', 'Current'), fg=T['cyan'],
                             bg=rowbg, font=('Segoe UI', 8, 'bold')).pack(side='left', padx=10)
                elif best:
                    tk.Label(hd, text='⚡ ' + L.get('dns_best', 'Fastest'), fg=T['green'],
                             bg=rowbg, font=('Segoe UI', 8, 'bold')).pack(side='left', padx=10)
                bf = tk.Frame(row, bg=rowbg); bf.pack(fill='x', padx=12, pady=(0, 7))
                _addr_line(bf, rowbg, 'IPv4', v4, v4ms, hicol)
                if v6:
                    _addr_line(bf, rowbg, 'IPv6', v6, v6ms, T['text'])
            if not ipv6_ok:
                tk.Label(body, text='ℹ ' + L.get('dns_no_ipv6', 'IPv6 not available'),
                         fg=T['muted'], bg=T['bg'], font=('Segoe UI', 8),
                         wraplength=440, justify='left').pack(anchor='w', pady=(8, 0))
            try: canvas.configure(scrollregion=canvas.bbox('all'))
            except Exception: pass

        def _worker():
            ipv6 = _ipv6_available()
            results = []
            total = len(DNS_PROVIDERS)
            for i, (name, v4s, v6s) in enumerate(DNS_PROVIDERS):
                try:
                    self._win.after(0, lambda i=i: status.config(
                        text=f"{L.get('dns_testing', 'Testing…')}  {i+1}/{total}")
                        if status.winfo_exists() else None)
                except Exception:
                    return   # window closed
                a = benchmark_dns(v4s[0], False)
                b = benchmark_dns(v6s[0], True) if ipv6 else None
                results.append([name, v4s[0], a, v6s[0], b, False])
            results.sort(key=lambda r: (r[2] is None, r[2] if r[2] is not None else 9e9))
            # prepend the machine's current DNS server(s) for comparison
            cur_rows = []
            for ip in get_current_dns()[:2]:
                ms = benchmark_dns(ip, False)
                cur_rows.append([L.get('dns_current', 'Current'), ip, ms, '', None, True])
            results = cur_rows + results
            def _finish():
                if not status.winfo_exists():
                    return
                _render(results, ipv6)
                status.config(text='')
                find_btn.config(text='🔄  ' + L.get('dns_again', 'Test again'))
                self._dns_running = False
            try: self._win.after(0, _finish)
            except Exception: pass

        def _start(_e=None):
            if getattr(self, '_dns_running', False):
                return
            self._dns_running = True
            status.config(text=L.get('dns_testing', 'Testing…'))
            find_btn.config(text='⏳  ' + L.get('dns_testing', 'Testing…'))
            threading.Thread(target=_worker, daemon=True).start()
        find_btn.bind('<Button-1>', _start)

    def _tab_about(self):
        T = self.T; L = self.L
        body = tk.Frame(self._content, bg=T['bg']); body.pack(fill='both', expand=True)
        # emblem
        try:
            emb = tk.PhotoImage(file=os.path.join(_base_dir(), 'icons', 'tray.png'))
            self._about_emb = emb
            tk.Label(body, image=emb, bg=T['bg']).pack(pady=(28, 8))
        except Exception:
            pass
        tk.Label(body, text=DISPLAY_NAME, fg=T['text'], bg=T['bg'],
                 font=('Segoe UI', 22, 'bold')).pack()
        tk.Label(body, text=L['version'] + ' ' + VERSION, fg=T['muted'], bg=T['bg'],
                 font=('Segoe UI', 10)).pack(pady=(0, 4))
        tk.Label(body, text="© 2026 Fokion Papanikolaou", fg=T['muted'], bg=T['bg'],
                 font=('Segoe UI', 9)).pack(pady=(0, 18))
        # ── link icons in a single horizontal row ──
        lrow = tk.Frame(body, bg=T['bg']); lrow.pack(pady=12)
        def link_btn(icon, text, url):
            b = tk.Label(lrow, text=f'{icon}\n{text}', fg=T['text'], bg=T['panel'],
                         font=('Segoe UI', 10), padx=22, pady=10,
                         cursor='hand2', justify='center')
            b.pack(side='left', padx=6)
            b.bind('<Button-1>', lambda e: webbrowser.open(url))
            b.bind('<Enter>', lambda e: b.config(bg=T['bg2'], fg=T['cyan']))
            b.bind('<Leave>', lambda e: b.config(bg=T['panel'], fg=T['text']))
        link_btn('🏪', L['store'].replace('Microsoft ', ''),
                 'https://apps.microsoft.com/detail/9P128R4SVXLC')
        link_btn('🐙', 'GitHub',
                 'https://github.com/FokionPapanikolaou/PulseDeck')
        link_btn('🌐', L['website'],
                 'https://fokionpapanikolaou.github.io/PulseDeck/')
        # ── rate: opens the Store review page directly (deep link in MSIX) ──
        rb = tk.Label(lrow, text='⭐\n' + L.get('rate', 'Rate'), fg=T['text'],
                      bg=T['panel'], font=('Segoe UI', 10), padx=22, pady=10,
                      cursor='hand2', justify='center')
        rb.pack(side='left', padx=6)
        rb.bind('<Button-1>', lambda e: self.w._open_review())
        rb.bind('<Enter>', lambda e: rb.config(bg=T['bg2'], fg='#ffd34d'))
        rb.bind('<Leave>', lambda e: rb.config(bg=T['panel'], fg=T['text']))
        # ── donate: direct in-window buttons (no extra popup) ──
        tk.Label(body, text='💜  ' + L['donate'], fg='#d8b6ff', bg=T['bg'],
                 font=('Segoe UI', 11, 'bold')).pack(pady=(18, 6))
        drow = tk.Frame(body, bg=T['bg']); drow.pack()
        def pay_btn(text, url, bbg, bfg, hbg):
            b = tk.Label(drow, text=text, fg=bfg, bg=bbg,
                         font=('Segoe UI', 10, 'bold'), padx=22, pady=8,
                         cursor='hand2')
            b.pack(side='left', padx=6)
            b.bind('<Button-1>', lambda e: webbrowser.open(url))
            b.bind('<Enter>', lambda e: b.config(bg=hbg))
            b.bind('<Leave>', lambda e: b.config(bg=bbg))
        pay_btn('PayPal',
                'https://www.paypal.com/donate/?hosted_button_id=PHZG592VLQAFA',
                '#0070ba', '#ffffff', '#1a8ad4')
        pay_btn('Revolut',
                'https://revolut.me/fokionpap',
                '#191c1f', '#ffffff', '#33383d')


# ── Widget ─────────────────────────────────────────────────────────────
FONT_SCALES = {'small': (9, 7), 'normal': (12, 10), 'large': (14, 12)}

class Widget:
    COLORS = {'up': '#3fb950', 'dn': '#79c0ff', 'sep': '#2d333b'}

    def __init__(self):
        self._first_run = not os.path.exists(CONFIG_PATH)
        self.cfg = load_config()
        # weather + earthquake features were removed — scrub them from any
        # existing saved config so old installs don't keep showing them.
        self.cfg['show_weather'] = False
        self.cfg['quakes_on'] = False
        if isinstance(self.cfg.get('cell_order'), list):
            self.cfg['cell_order'] = [c for c in self.cfg['cell_order']
                                      if c not in ('weather', 'quake')]
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

        # Every hardware read below is wrapped: a single failing reader (a
        # missing PDH counter, a stripped-down VM image, a quirky GPU driver,
        # an OS without disk I/O, …) must NEVER stop the app from starting.
        # When a value can't be read it falls back to a safe default; the
        # cell that needs it then shows "—" instead of crashing the widget.
        try:    _, taskbar_h, _ = get_taskbar_info()
        except Exception: taskbar_h = 40
        self.H = taskbar_h or 40

        try:    self._prev_net = psutil.net_io_counters()
        except Exception: self._prev_net = None
        try:    self._prev_disk = psutil.disk_io_counters()
        except Exception: self._prev_disk = None
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
        try:    self._has_batt = psutil.sensors_battery() is not None
        except Exception: self._has_batt = False
        self._gpu = None
        self._gpu_mem = None
        try:    self._vram_total = get_total_vram_gb()
        except Exception: self._vram_total = None
        self._gpu_counter = None
        self._gpu_running = False
        try:    self._cpufreq = CpuFreq()
        except Exception:
            class _NoFreq:
                ok = False
                def read_ghz(self): return None
            self._cpufreq = _NoFreq()
        self._weather = None
        self._weather_running = False
        self._weather_dirty = False
        # earthquakes (v2.6)
        self._quake_active = None      # the most recent felt quake (dict) or None
        self._quake_active_until = 0   # epoch when the dot should clear
        self._quake_recent = []        # last 20 felt events (for the menu)
        self._quakes_running = False
        # power (v2.7) — name lookups go through the registry/WMI; tolerate failure
        try:    self._cpu_name_cached = get_cpu_name()
        except Exception: self._cpu_name_cached = ''
        try:    self._gpu_name_cached = get_gpu_name()
        except Exception: self._gpu_name_cached = ''
        self._power = None             # last {'cpu','gpu','total','source','cpu_tdp','gpu_tdp'} or None
        # slow-hardware poller (keeps _update_tick non-blocking)
        self._slow = _SlowPoller()
        self._slow.start()
        # customize window (v2.6)
        self._customize = None
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

        self._update()
        self._animate()
        self._foreground_loop()
        self._setup_tray()
        threading.Thread(target=self._proc_sampler, daemon=True).start()
        threading.Thread(target=self._update_check_worker, daemon=True).start()
        # adapt the chroma key to the real taskbar colour (kills dark fringes).
        # Sample twice: an early pass for the common case, and a later one to
        # self-correct if the taskbar hadn't finished repainting yet (which on
        # a fast relaunch left a dark box behind the numbers).
        self.root.after(400, self._adapt_key_color)
        self.root.after(2000, self._adapt_key_color)

        # First launch: a Windows tray notification points to the settings icon.
        if self._first_run:
            save_config(self.cfg)          # mark as "seen" for next launches
            self.root.after(2500, self._first_run_notify)

    def _first_run_notify(self):
        try:
            if getattr(self, '_tray', None):
                self._tray.notify(HINTS.get(self.lang, HINTS['en']),
                                  DISPLAY_NAME)
        except Exception:
            pass

    # ── adaptive chroma key ────────────────────────────────────────────
    def _adapt_key_color(self):
        """Sample the taskbar colour behind the widget and use it as the
        chroma key. Anti-aliased fringes of icons/text then blend toward the
        REAL background instead of near-black, so no dark boxes appear on
        light taskbars. Re-run whenever the widget moves."""
        if not self.cfg.get('transparent_bg'):
            return
        try:
            from PIL import ImageGrab
            self.root.withdraw()
            self.root.update_idletasks()
            x = self.root.winfo_x(); y = self.root.winfo_y()
            w = max(60, self.root.winfo_width())
            h = max(20, self.root.winfo_height())
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            img = img.resize((24, 8))
            px = [p[:3] for p in img.getdata()]
            # Most-common colour = the taskbar surface behind us; this is what
            # made the numbers look clean. Ignores dark icon/text outliers that
            # an average would smear into a dark halo.
            from collections import Counter
            (r, g, b), _ = Counter(px).most_common(1)[0]
            # nudge one channel so the key is unlikely to collide with real
            # pixel values inside the icons/text
            b = b + 1 if b < 255 else b - 1
            new_key = f'#{r:02x}{g:02x}{b:02x}'
            old = getattr(self, '_adaptive_key', None)
            # tolerance: skip the (expensive) rebuild if the sampled colour
            # is within ±6 per channel of the current key
            def _close(c1, c2):
                if not c1 or not c2: return False
                try:
                    a = [int(c1[i:i+2], 16) for i in (1, 3, 5)]
                    bch = [int(c2[i:i+2], 16) for i in (1, 3, 5)]
                    return all(abs(x - y) <= 6 for x, y in zip(a, bch))
                except Exception:
                    return False
            if not _close(new_key, old):
                self._adaptive_key = new_key
                self._apply_bg_mode()
                self._build_ui()       # recreate children with the new bg
                self._position()
        except Exception:
            pass
        finally:
            try: self.root.deiconify()
            except Exception: pass

    # ── background mode (transparent vs. dark translucent) ─────────────
    def _apply_bg_mode(self):
        if self.cfg.get('transparent_bg'):
            # True transparency via chroma-key; only icons/numbers show.
            # Anti-aliased pixels in icons/text blend toward the key colour,
            # so the key must MATCH the taskbar behind us — otherwise dark
            # "boxes" appear around everything on light taskbars. We sample
            # the actual taskbar colour and use it as the key (adaptive).
            self.bg = getattr(self, '_adaptive_key', None) or TRANSPARENT
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
        keys = ('show_cpu','show_ram','show_net','show_disk','show_batt','show_gpu','show_power')
        if self.cfg.get(key) and not any(self.cfg.get(o) for o in keys if o != key):
            return
        self._set(key, not self.cfg.get(key)); self._rebuild()
        if key == 'show_gpu' and self.cfg.get('show_gpu'):
            self._ensure_gpu_thread()

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

    # ── earthquakes handlers ───────────────────────────────────────────
    def _act_quakes_mmi(self, threshold):
        self._set('quakes_min_mmi', float(threshold))

    def _show_quake_history(self):
        """Small popup listing the recent felt events near the user."""
        try:
            win = tk.Toplevel(self.root)
            win.title(QUAKES_LABEL.get(self.lang, QUAKES_LABEL['en']))
            win.configure(bg='#0d1117')
            try: win.iconbitmap(os.path.join(_base_dir(), 'app.ico'))
            except Exception: pass
            win.geometry('540x420'); win.resizable(False, False)
            try: win.attributes('-topmost', True)
            except Exception: pass
            HEAD = '#161b22'; LINE = '#2d333b'; GREY = '#8b96a2'; WHITE = '#ecf2f8'
            ORANGE = '#ffa657'; RED = '#f85149'; CYAN = '#3fc3ff'
            tk.Label(win, text='🚨  ' + QUAKES_LABEL.get(self.lang, QUAKES_LABEL['en']),
                     bg='#0d1117', fg=CYAN, font=('Segoe UI', 14, 'bold')).pack(anchor='w', padx=18, pady=(14, 6))
            _L = CUST_LABELS.get(self.lang, CUST_LABELS['en'])
            tk.Label(win, text=_L['felt_near'], bg='#0d1117', fg=GREY,
                     font=('Segoe UI', 9)).pack(anchor='w', padx=18)
            tk.Frame(win, bg=LINE, height=1).pack(fill='x', padx=18, pady=(8, 0))

            frame = tk.Frame(win, bg='#0d1117'); frame.pack(fill='both', expand=True, padx=18, pady=10)
            if not self._quake_recent:
                tk.Label(frame, bg='#0d1117', fg=GREY, text=_L['no_felt'],
                         font=('Segoe UI', 10)).pack(anchor='w', pady=20)
            else:
                # click any row to dismiss the matching active alert
                def _click_row(qq, rr):
                    try:
                        # if the clicked event IS the active one, dismiss it
                        act = self._quake_active
                        if act and act.get('id') and act['id'] == qq.get('id'):
                            self._dismiss_quake_alert()
                        # always mark as seen
                        if qq.get('id'):
                            seen = set(self.cfg.get('quakes_seen', []) or [])
                            seen.add(qq['id'])
                            self.cfg['quakes_seen'] = list(seen)[-200:]
                            save_config(self.cfg)
                        try: rr.destroy()
                        except Exception: pass
                    except Exception: pass
                for q in self._quake_recent[:10]:
                    row = tk.Frame(frame, bg=HEAD, highlightbackground=LINE,
                                   highlightthickness=1, cursor='hand2')
                    row.pack(fill='x', pady=3)
                    inner = tk.Frame(row, bg=HEAD, cursor='hand2')
                    inner.pack(fill='x', padx=10, pady=6)
                    row.bind('<Button-1>', lambda e, qq=q, rr=row: _click_row(qq, rr))
                    inner.bind('<Button-1>', lambda e, qq=q, rr=row: _click_row(qq, rr))
                    col = RED if q['mmi'] >= 5 else (ORANGE if q['mmi'] >= 4 else CYAN)
                    tk.Label(inner, text=f"M{q['mag']:.1f}", bg=HEAD, fg=col,
                             font=('Segoe UI', 12, 'bold'), width=6, anchor='w').pack(side='left')
                    detail = f"{q['dist_km']:.0f} km · MMI {q['mmi']:.1f} ({q['mmi_label']})"
                    region = q.get('region', '')[:60]
                    if region:
                        detail = f"{region}\n{detail}"
                    tk.Label(inner, text=detail, bg=HEAD, fg=WHITE, justify='left',
                             font=('Segoe UI', 9)).pack(side='left', padx=10)
                    age = q.get('age_sec')
                    if age is not None:
                        if age < 60:    ago = f"{int(age)}s"
                        elif age < 3600: ago = f"{int(age/60)}m"
                        else:           ago = f"{int(age/3600)}h"
                    else:
                        ago = ''
                    src = q.get('source', '')
                    tk.Label(inner, text=f"{ago}\n{src}", bg=HEAD, fg=GREY,
                             font=('Segoe UI', 8), justify='right').pack(side='right')
            tk.Button(win, text='Close', command=win.destroy,
                      bg=HEAD, fg=WHITE, bd=0, font=('Segoe UI', 10),
                      padx=20, pady=6, cursor='hand2').pack(pady=10)
        except Exception:
            pass

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
        self._tray = pystray.Icon(APP_NAME, img, DISPLAY_NAME, self._tray_menu())
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
            metric('show_power', '⚡ ' + POWER_LABEL.get(self.lang, POWER_LABEL['en'])),
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

        # ── Hybrid tray menu: Customize… + quick toggles + system items ──
        L = CUST_LABELS.get(self.lang, CUST_LABELS['en'])
        return Menu(
            MI(lambda it: '⬆  ' + UPDATE_LABEL.get(self.lang, UPDATE_LABEL['en'])
                          + (f'  v{self._update_tag}' if self._update_tag else ''),
               lambda i, it: self._ui(self._open_releases),
               visible=lambda it: bool(getattr(self, '_update_tag', None))),
            MI('🎨  ' + L['title'].split('—')[-1].strip() + '…',
               lambda i, it: self._ui(self._open_customize),
               default=True),
            Menu.SEPARATOR,
            # quick toggles that users hit often:
            MI(LOCK_LABEL.get(self.lang, LOCK_LABEL['en']),
               lambda i, it: self._ui(self._act_lock),
               checked=lambda it: bool(self.cfg.get('locked'))),
            Menu.SEPARATOR,
            MI('\U0001F49C  ' + DONATE_LABEL.get(self.lang, DONATE_LABEL['en']),
               lambda i, it: self._ui(self._show_donate)),
            MI(f'{APP_NAME} v{VERSION}', None, enabled=False),
            MI(t('close'), lambda i, it: self._ui(self._act_quit)),
        )

    def _open_customize(self):
        """Open the customize window. Only one instance at a time."""
        try:
            if getattr(self, '_customize', None) is not None:
                try:
                    self._customize._win.lift(); self._customize._win.focus_force()
                    return
                except Exception:
                    self._customize = None
            self._customize = CustomizeWindow(self)
        except Exception:
            import traceback as _tb
            _tb.print_exc()

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
                self._gpu, self._gpu_mem, _vram_limit = self._gpu_counter.read()
                if _vram_limit and _vram_limit > 0:
                    self._vram_total = _vram_limit
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
            try:
                self._weather = fetch_weather(self.cfg.get('weather_unit', 'C'),
                                              self.cfg.get('weather_city', ''))
            except Exception:
                # Network/API blip — keep the loop alive so we retry next cycle.
                pass
            self._weather_dirty = False
            # refresh every ~20 min, but wake early if unit/city changed
            for _ in range(120):
                if not self.cfg.get('show_weather') or self._weather_dirty:
                    break
                time.sleep(10)
        self._weather_running = False

    def _dismiss_quake_alert(self):
        """User clicked the bar's quake icon → clear the active alert."""
        try:
            q = self._quake_active
            if q and q.get('id'):
                # also mark this event as seen so polling won't re-trigger it
                seen = set(self.cfg.get('quakes_seen', []) or [])
                seen.add(q['id'])
                self.cfg['quakes_seen'] = list(seen)[-200:]
                save_config(self.cfg)
            self._quake_active = None
            self._quake_active_until = 0
            if getattr(self, 'lbl_quake', None):
                self.lbl_quake.config(text='')
        except Exception:
            pass

    # ── Earthquakes background polling ─────────────────────────────────
    def _ensure_quakes_thread(self):
        if self.cfg.get('quakes_on') and not self._quakes_running:
            self._quakes_running = True
            threading.Thread(target=self._quakes_loop, daemon=True).start()

    def _user_latlon(self):
        """User's coordinates: manual override > weather > ipapi."""
        lat = self.cfg.get('quakes_lat')
        lon = self.cfg.get('quakes_lon')
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            return float(lat), float(lon)
        # piggy-back on weather's geo if we already have it
        try:
            w = self._weather or {}
            if w.get('lat') is not None and w.get('lon') is not None:
                return float(w['lat']), float(w['lon'])
        except Exception:
            pass
        try:
            g = _http_json('https://ipapi.co/json/', timeout=6)
            return float(g['latitude']), float(g['longitude'])
        except Exception:
            return None, None

    def _quakes_loop(self):
        # wait a moment so the weather thread can grab geo first
        time.sleep(10)
        while self.cfg.get('quakes_on'):
            try:
                self._check_quakes_once()
            except Exception:
                pass
            # 5-minute poll, wake every 5s to react to config changes
            for _ in range(60):
                if not self.cfg.get('quakes_on'):
                    break
                time.sleep(5)
        self._quakes_running = False

    def _check_quakes_once(self):
        lat, lon = self._user_latlon()
        if lat is None: return
        # ── debug: inject a synthetic event from a trigger file (for tests) ──
        trigger = os.path.join(_exe_dir(), '_quake_test.json')
        if os.path.exists(trigger):
            try:
                with open(trigger, 'r', encoding='utf-8') as f:
                    fake = json.load(f)
                os.remove(trigger)
                # fill in derived fields if the test didn't
                if 'dist_km' not in fake and lat is not None:
                    fake['dist_km'] = _hypocentral_km(
                        lat, lon, fake.get('lat', lat), fake.get('lon', lon),
                        fake.get('depth', 10))
                if 'mmi' not in fake:
                    fake['mmi'] = _felt_intensity_mmi(fake.get('mag', 4.0),
                                                     fake.get('dist_km', 10))
                fake.setdefault('mmi_label', _mmi_label(fake['mmi']))
                fake.setdefault('age_sec', 60)
                fake.setdefault('source', 'TEST')
                fake.setdefault('id', f'test-{int(time.time())}')
                # show it
                self._quake_active = fake
                self._quake_active_until = time.time() + float(
                    self.cfg.get('quakes_alert_min', 20)) * 60
                self._quake_recent = [fake] + (self._quake_recent or [])
                title = QUAKES_TOAST_TITLE.get(self.lang, QUAKES_TOAST_TITLE['en'])
                body = (f"M{fake['mag']:.1f} · {fake['dist_km']:.0f} km · "
                        f"{fake.get('region','')[:60]}").strip(' ·')
                try:
                    if getattr(self, '_tray', None):
                        self._tray.notify(body, title)
                except Exception:
                    pass
                return
            except Exception:
                pass
        sources = []
        if self.cfg.get('quakes_emsc'): sources.append('emsc')
        if self.cfg.get('quakes_usgs'): sources.append('usgs')
        if not sources: return
        min_mag = float(self.cfg.get('quakes_min_mag', 2.5))
        events = fetch_quakes(lat, lon, sources=tuple(sources), min_mag=min_mag)
        max_age  = float(self.cfg.get('quakes_max_age_min', 30)) * 60.0
        max_dist = float(self.cfg.get('quakes_max_dist_km', 100))
        alert_min = float(self.cfg.get('quakes_alert_min', 20))
        min_mmi = float(self.cfg.get('quakes_min_mmi', 3.0))
        seen = set(self.cfg.get('quakes_seen', []) or [])
        # find new felt events (must be inside the radius the user wants)
        new_felt = []
        for q in events:
            if q['mmi'] < min_mmi: continue
            if q['dist_km'] is None or q['dist_km'] > max_dist: continue
            if q['age_sec'] is None or q['age_sec'] > max_age: continue
            if q['id'] and q['id'] in seen: continue
            new_felt.append(q)
        # build the "recent felt events" list (last 20, any time, any source)
        # also constrained by the user's radius
        felt_all = [q for q in events
                    if q['mmi'] >= min_mmi
                    and q.get('dist_km') is not None
                    and q['dist_km'] <= max_dist]
        self._quake_recent = felt_all[:20]
        # process new events: strongest first
        new_felt.sort(key=lambda q: q['mmi'], reverse=True)
        if new_felt:
            strongest = new_felt[0]
            self._quake_active = strongest
            # bar dot stays lit for the configured number of minutes
            self._quake_active_until = time.time() + alert_min * 60
            # toast notification (unless muted)
            if (self.cfg.get('quakes_toasts') and not self.cfg.get('quakes_mute')
                    and getattr(self, '_tray', None)):
                title = QUAKES_TOAST_TITLE.get(self.lang, QUAKES_TOAST_TITLE['en'])
                body = (f"M{strongest['mag']:.1f} · {strongest['dist_km']:.0f} km · "
                        f"{strongest.get('region','')[:60]}").strip(' ·')
                try:
                    self._tray.notify(body, title)
                except Exception:
                    pass
            # remember all alerted IDs so we don't re-fire (cap at 200)
            for q in new_felt:
                if q['id']: seen.add(q['id'])
            self.cfg['quakes_seen'] = list(seen)[-200:]
            save_config(self.cfg)

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
        """Bind drag on the bar window AND every bar child — but NEVER on
        Toplevel children (Customize window, popups, tooltips). Binding
        those made every click inside an open dialog start dragging the
        bar, which then stuck to the cursor and 'froze' the dialog."""
        def bind_all(w):
            w.bind('<Button-1>', self._drag_start)
            w.bind('<B1-Motion>', self._drag_move)
            w.bind('<ButtonRelease-1>', self._drag_end)
            for child in w.winfo_children():
                if isinstance(child, tk.Toplevel):
                    continue   # dialogs manage their own input
                bind_all(child)
        # bind the root's handlers manually (root itself is fine), then
        # recurse only into non-Toplevel children
        self.root.bind('<Button-1>', self._drag_start)
        self.root.bind('<B1-Motion>', self._drag_move)
        self.root.bind('<ButtonRelease-1>', self._drag_end)
        for child in self.root.winfo_children():
            if isinstance(child, tk.Toplevel):
                continue
            bind_all(child)

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
        path = os.path.join(ICON_DIR, name)
        img = None
        try:
            # Hard-threshold the alpha to binary: a pixel is either fully opaque
            # (the icon) or fully transparent. Transparent pixels fall through to
            # the Label's background colour, which is the chroma key and gets
            # keyed out cleanly — so there is NO pale/white fringe around the
            # icon (the old anti-aliased edges left semi-transparent pixels that
            # blended toward the key but never matched it exactly).
            from PIL import Image, ImageTk, ImageFilter
            icon = Image.open(path).convert('RGBA')
            r, g, b, a = icon.split()
            a = a.point(lambda v: 255 if v >= 110 else 0)
            # erode the alpha by 1px so the outermost (often light) anti-aliased
            # edge ring is dropped — kills the faint white outline on the bar.
            a = a.filter(ImageFilter.MinFilter(3))
            icon = Image.merge('RGBA', (r, g, b, a))
            img = ImageTk.PhotoImage(icon)
        except Exception:
            img = None
        if img is None:
            try: img = tk.PhotoImage(file=path)
            except Exception: return   # never let a missing icon crash the widget
        self._imgs.append(img)
        tk.Label(self.root, image=img, bg=self.bg, bd=0).pack(side='left', padx=(2, 0))

    def _rebuild(self, _attempts=0):
        """Rebuild the UI safely (deferred until any menu grab is gone)."""
        _log(f'_rebuild ENTER (attempts={_attempts}, rebuilding={getattr(self, "_rebuilding", False)})')
        # re-entrancy guard: silently drop overlapping calls
        if getattr(self, '_rebuilding', False):
            _log('  -> re-entry blocked')
            return
        try:
            gc = self.root.grab_current()
            if gc is not None and _attempts < 40:
                _log(f'  -> grab={gc}, deferring')
                self.root.after(50, lambda: self._rebuild(_attempts + 1))
                return
        except Exception as e:
            _log(f'  -> grab check EXC: {e}')
        self._rebuilding = True
        try:
            jid = getattr(self, '_pending_rebuild_after', None)
            if jid:
                try: self.root.after_cancel(jid)
                except Exception: pass
                self._pending_rebuild_after = None
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
        finally:
            self._rebuilding = False

    @property
    def theme(self):
        return THEMES.get(self.cfg.get('theme', 'default'), THEMES['default'])

    # ── UI ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Destroy only the bar cells — skip Toplevel children so that any
        # open dialogs (Customize window, donate card, history popup, etc.)
        # survive a rebuild.
        for w in self.root.winfo_children():
            try:
                if isinstance(w, tk.Toplevel): continue
            except Exception:
                pass
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
        ICON_TEXT = {'cpu.png': 'CPU', 'gpu.png': 'GPU', 'ram.png': 'RAM',
                     'net.png': 'NET', 'disk.png': 'DISK', 'battery.png': 'BAT'}
        text_mode = self.cfg.get('bar_labels') == 'text'

        def icon(name, parent):
            # text mode: show a short label instead of the glyph (weather/quake
            # have no sensible text form, so they keep their icon)
            if text_mode and name in ICON_TEXT:
                tk.Label(parent, text=ICON_TEXT[name], fg=th.get('accent', valcol),
                         bg=self.bg, font=('Consolas', small, 'bold'),
                         padx=2).pack(side='left', padx=(2, 1))
                return
            try:
                # binary-alpha + 1px erode so the chroma-key edges stay clean
                # (no pale fringe) — same treatment as the standalone _icon.
                key = self.bg if isinstance(self.bg, str) else ''
                if key.startswith('#') and len(key) == 7:
                    from PIL import Image, ImageTk, ImageFilter
                    im = Image.open(os.path.join(ICON_DIR, name)).convert('RGBA')
                    r, g, b, a = im.split()
                    a = a.point(lambda v: 255 if v >= 110 else 0)
                    a = a.filter(ImageFilter.MinFilter(3))
                    img = ImageTk.PhotoImage(Image.merge('RGBA', (r, g, b, a)))
                else:
                    img = tk.PhotoImage(file=os.path.join(ICON_DIR, name))
                self._imgs.append(img)
                tk.Label(parent, image=img, bg=self.bg, bd=0).pack(side='left', padx=(2, 0))
            except Exception:
                pass

        def val(parent, width):
            # natural width in transparent mode (otherwise the extra space
            # shows the dark taskbar through and looks like a black border)
            kw = dict(text='', fg=valcol, bg=self.bg, font=vf, pady=0, padx=2)
            if not self.cfg.get('transparent_bg'):
                kw['width'] = width
            l = tk.Label(parent, **kw)
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
            # In transparent mode, an oversize `width=` chunk of the label
            # background gets chroma-keyed → the dark taskbar shows through
            # and looks like a "black border" around the value. Use natural
            # width in transparent mode; keep fixed width only when opaque
            # (so columns align visually).
            use_width = None if self.cfg.get('transparent_bg') else width
            f_lbl = lambda: dict(text='', fg=valcol, bg=self.bg, font=nf,
                                 anchor='w', padx=2, pady=0,
                                 **({'width': use_width} if use_width else {}))
            if stacked:
                col = tk.Frame(f, bg=self.bg); col.pack(side='left', padx=2)
                top = None
                if has_top:
                    top = tk.Label(col, **f_lbl())
                    top.pack(side='top', anchor='w'); self._rgb_targets.append(top)
                v = tk.Label(col, **f_lbl())
                v.pack(side='top', anchor='w'); self._rgb_targets.append(v)
                return f, v, top
            return f, val(f, width), None

        sw = 7   # stacked column width fits "4.0 GHz" / "15.1 GB" / "100%"

        # Reset all labels (rebuild may have changed visibility / order)
        self.lbl_cpu = self.lbl_cpu_top = None
        self.lbl_ram = self.lbl_ram_top = None
        self.lbl_gpu = self.lbl_gpu_top = None
        self.lbl_up = self.lbl_dn = None
        self.lbl_disk_r = self.lbl_disk_w = None
        self.lbl_batt = None
        self.lbl_wx = self.lbl_wx_icon = None
        self.lbl_power = self.lbl_power_top = None
        self.lbl_quake = None

        # ── cell builders, keyed by cell id ──
        def b_cpu():
            f, self.lbl_cpu, self.lbl_cpu_top = stat('cpu.png', sw if stacked else cpu_w, True)
            self.spark_cpu = spark(f); self._tip_cells.append((f, 'cpu', None))
        def b_ram():
            f, self.lbl_ram, self.lbl_ram_top = stat('ram.png', sw if stacked else ram_w, True)
            self.spark_ram = spark(f); self._tip_cells.append((f, 'ram', None))
        def b_gpu():
            f, self.lbl_gpu, self.lbl_gpu_top = stat('gpu.png', sw if stacked else 4, stacked)
            self._tip_cells.append((f, 'gpu', None))
        def b_net():
            f = new_cell(); icon('net.png', f)
            nfr = tk.Frame(f, bg=self.bg); nfr.pack(side='left', padx=2)
            def net_row(arrow, color):
                row = tk.Frame(nfr, bg=self.bg); row.pack(side='top', anchor='w')
                tk.Label(row, text=arrow, fg=color, bg=self.bg, font=nf, padx=0).pack(side='left')
                # LOCKED width: in bits mode _fmt can yield 7 chars ("12.5 Mb",
                # "10.5 Gb") while other ticks are 6 → the cell kept resizing and
                # the layered window flashed a black strip on each grow (the
                # -transparentcolor key is only re-asserted in _position(), not
                # per tick). Consolas is monospaced, so a fixed width=7 box with
                # the value padded to exactly 7 chars (see :>7 in _update_once)
                # never changes size — and because text fills the box exactly,
                # there is no leftover transparent cell showing the dark taskbar
                # (the bug the old 'width=7 + :>6' combo caused).
                v = tk.Label(row, text='    0 K', fg=valcol, bg=self.bg,
                             font=nf, anchor='w', padx=2, width=7)
                v.pack(side='left'); self._rgb_targets.append(v); return v
            self.lbl_up = net_row('▲', self.COLORS['up'])
            self.lbl_dn = net_row('▼', self.COLORS['dn'])
            self._tip_cells.append((f, 'net', None))
        def b_disk():
            f = new_cell(); icon('disk.png', f)
            dfr = tk.Frame(f, bg=self.bg); dfr.pack(side='left', padx=2)
            def disk_row(arrow, color):
                row = tk.Frame(dfr, bg=self.bg); row.pack(side='top', anchor='w')
                tk.Label(row, text=arrow, fg=color, bg=self.bg, font=nf, padx=0).pack(side='left')
                # natural width to avoid showing the bare taskbar through
                v = tk.Label(row, text=' 0 K', fg=valcol, bg=self.bg,
                             font=nf, anchor='w', padx=2)
                v.pack(side='left'); self._rgb_targets.append(v); return v
            self.lbl_disk_r = disk_row('R', self.COLORS['dn'])
            self.lbl_disk_w = disk_row('W', self.COLORS['up'])
            self._tip_cells.append((f, 'disk', None))
            # per-drive space % cells (e.g. C: 60%) live with the disk cell
            for drive in self.cfg.get('disks', []):
                fd = new_cell(); icon('disk.png', fd)
                lbl = tk.Label(fd, text=f'{drive[0]} ..', fg=valcol, bg=self.bg,
                               font=nf if stacked else vf, width=6, anchor='w', padx=2)
                lbl.pack(side='left'); self._rgb_targets.append(lbl)
                self._disk_lbls[drive] = lbl
                self._tip_cells.append((fd, 'diskspace', drive))
        def b_batt():
            if not self._has_batt: return
            f, self.lbl_batt, _ = stat('battery.png', sw if stacked else 5, stacked)
            self._tip_cells.append((f, 'batt', None))
        def b_power():
            f = new_cell()
            tk.Label(f, text='⚡', fg='#ffd64a', bg=self.bg,
                     font=('Segoe UI', big), padx=2).pack(side='left')
            if stacked:
                col = tk.Frame(f, bg=self.bg); col.pack(side='left', padx=2)
                # natural width — no extra transparent space showing the bar
                # fixed width: "{watts} W" swings 3↔5 chars each tick → lock it
                # (like the net cell) so the bar never resizes / flashes black
                self.lbl_power_top = tk.Label(col, text='', fg=valcol, bg=self.bg,
                                              font=nf, anchor='w', padx=0, width=5)
                self.lbl_power_top.pack(side='top', anchor='w'); self._rgb_targets.append(self.lbl_power_top)
                self.lbl_power = tk.Label(col, text='', fg=valcol, bg=self.bg,
                                          font=nf, anchor='w', padx=0)
                self.lbl_power.pack(side='top', anchor='w'); self._rgb_targets.append(self.lbl_power)
            else:
                self.lbl_power_top = None
                self.lbl_power = tk.Label(f, text='', fg=valcol, bg=self.bg,
                                          font=vf, anchor='w', padx=2, width=5)
                self.lbl_power.pack(side='left'); self._rgb_targets.append(self.lbl_power)
            self._tip_cells.append((f, 'power', None))
        builders = {'cpu': b_cpu, 'ram': b_ram, 'gpu': b_gpu, 'net': b_net,
                    'disk': b_disk, 'batt': b_batt, 'power': b_power}
        visible_keys = {
            'cpu': 'show_cpu', 'ram': 'show_ram', 'gpu': 'show_gpu',
            'net': 'show_net', 'disk': 'show_disk', 'batt': 'show_batt',
            'power': 'show_power',
        }
        # Resolve order, then forcibly push critical cells to the end if asked
        order = list(self.cfg.get('cell_order') or DEFAULT_CELL_ORDER)
        for cid in DEFAULT_CELL_ORDER:
            if cid not in order: order.append(cid)
        if self.cfg.get('critical_last', True) and 'quake' in order:
            order.remove('quake'); order.append('quake')
        # Build cells in order
        for cid in order:
            if not self.cfg.get(visible_keys.get(cid, ''), False): continue
            try:
                builders[cid]()
            except Exception:
                pass

        # place cells according to orientation (no separators; tight spacing
        # to save taskbar room — just a small gap between cells)
        for i, f in enumerate(cells):
            if vertical:
                f.pack(side='top', anchor='w')
            else:
                f.pack(side='left', padx=(0 if i == 0 else 7, 0))

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
        """True if a fullscreen app (game/video) is in front → taskbar is hidden.
        Result is cached for 250 ms so Win32 API calls don't hit every tick."""
        now = time.monotonic()
        if now - getattr(self, '_fs_ts', 0.0) < 0.25:
            return getattr(self, '_fs_cache', False)
        self._fs_ts = now
        try:
            u = ctypes.windll.user32
            hwnd = u.GetForegroundWindow()
            if not hwnd:
                self._fs_cache = False; return False
            buf = ctypes.create_unicode_buffer(256)
            u.GetClassNameW(hwnd, buf, 256)
            if buf.value in ('Shell_TrayWnd', 'Progman', 'WorkerW', 'Windows.UI.Core.CoreWindow', ''):
                self._fs_cache = False; return False
            r = RECT()
            u.GetWindowRect(hwnd, ctypes.byref(r))
            # Distinguish TRUE fullscreen (game / fullscreen video) from a merely
            # MAXIMIZED window. Both can report IsZoomed=True (Chrome reports
            # fullscreen video as zoomed!), so IsZoomed is useless here. Instead:
            #   • fullscreen fills the monitor EXACTLY, flush to its corners
            #     (e.g. 0,0 … 1536,864).
            #   • maximized overhangs the monitor by the invisible resize border
            #     (e.g. -7,-7 … 1543,823) and stops short of the taskbar edge.
            # An exact (±2 px) match against the window's own monitor cleanly
            # tells them apart, on any monitor and at any DPI scaling.
            MONITOR_DEFAULTTONEAREST = 2
            hmon = u.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
            mi = MONITORINFO(); mi.cbSize = ctypes.sizeof(MONITORINFO)
            if hmon and u.GetMonitorInfoW(hmon, ctypes.byref(mi)):
                m = mi.rcMonitor
            else:
                m = RECT(); m.left = 0; m.top = 0
                m.right = u.GetSystemMetrics(0); m.bottom = u.GetSystemMetrics(1)
            tol = 2
            result = (abs(r.left - m.left) <= tol and abs(r.top - m.top) <= tol and
                      abs(r.right - m.right) <= tol and abs(r.bottom - m.bottom) <= tol)
            self._fs_cache = result
            return result
        except Exception:
            self._fs_cache = False
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
        # IMPORTANT: psutil.process_iter holds the Python GIL while scanning
        # all processes (200-500 ms on busy systems). That blocked the Tk
        # main thread every 2 s and made the customize window appear to
        # "freeze". We now:
        #   - skip the scan when no tooltip is currently visible
        #   - poll every 5 s instead of 2
        #   - warm up cpu_percent only ONCE at start (cheap)
        try:
            for p in psutil.process_iter():
                try: p.cpu_percent()
                except Exception: pass
        except Exception:
            pass
        ncpu = psutil.cpu_count() or 1
        while True:
            time.sleep(5.0)
            # only do the heavy scan when the user is actually looking at a tip
            if not (getattr(self, '_tip', None) is not None
                    or getattr(self, '_customize', None) is not None):
                continue
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
                            f'{DISPLAY_NAME} {tag} — ' + UPDATE_LABEL.get(self.lang, UPDATE_LABEL['en']),
                            DISPLAY_NAME)
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
            elif kind == 'power':
                title = (POWER_LABEL.get(self.lang, POWER_LABEL['en']), '')
                p = self._power or {}
                if p:
                    total = p.get('total')
                    if total is not None:
                        rows.append((POWER_LABEL.get(self.lang, POWER_LABEL['en']) + ' total',
                                     f'{int(round(total))} W', ORANGE))
                    if p.get('cpu') is not None:
                        rows.append(('CPU', f"{int(round(p['cpu']))} W / {int(round(p['cpu_tdp']))} W TDP", BLUE))
                    if p.get('gpu') is not None:
                        rows.append(('GPU', f"{int(round(p['gpu']))} W / {int(round(p['gpu_tdp']))} W TDP", GREEN))
                    if p.get('source'):
                        src_label = {'nvml': 'nvidia-smi (exact)',
                                     'battery': 'battery rate (exact)',
                                     'estimate': 'TDP × utilisation'}.get(p['source'], p['source'])
                        rows.append(('Source', src_label, None))
                    if self._cpu_name_cached:
                        rows.append((self._cpu_name_cached[:30], '', None))
                    if self._gpu_name_cached:
                        rows.append((self._gpu_name_cached[:30], '', None))
                else:
                    rows.append((tp('loading'), '', None))
            elif kind == 'quake':
                title = (QUAKES_LABEL.get(self.lang, QUAKES_LABEL['en']), '')
                q = self._quake_active
                if q is not None:
                    rows.append(('Magnitude', f"M{q['mag']:.1f}", ORANGE))
                    rows.append(('Distance', f"{q['dist_km']:.0f} km", None))
                    rows.append(('Intensity', f"MMI {q['mmi']:.1f} ({q['mmi_label']})", PURPLE))
                    if q.get('region'):
                        rows.append(('Region', str(q['region'])[:40], None))
                    if q.get('age_sec') is not None:
                        ageMin = q['age_sec'] / 60
                        rows.append(('Time', f"{ageMin:.0f} min ago", None))
                    rows.append(('Source', q.get('source', '—'), None))
                else:
                    rows.append(('No active alert', '', None))
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
        try:
            self._update_tick()
        except Exception:
            _log('update tick EXC:\n' + traceback.format_exc())
        # When a cell's text width changes (power watts, battery's ⚡ on plug-in,
        # GPU —/%, …) the layered window resizes. Windows does NOT
        # re-key the newly exposed strip, so a black band flashes unless we
        # re-assert -transparentcolor after the size settles. This is the same
        # remedy _position() applies after a rebuild, but applied per tick only
        # when the width actually changed (cheap no-op otherwise).
        if self.cfg.get('transparent_bg'):
            try:
                self.root.update_idletasks()
                w = self.root.winfo_reqwidth()
                if w != getattr(self, '_last_bar_w', None):
                    self._last_bar_w = w
                    self.root.attributes('-transparentcolor', self.bg)
            except Exception:
                pass
        # ALWAYS reschedule, no matter what: a single bad sample (a flaky
        # PDH counter, a transient psutil error) must not freeze the widget.
        try:
            self.root.after(self.cfg.get('interval', 1000), self._update)
        except Exception:
            pass

    def _update_tick(self):
        self._follow_taskbar()
        # CPU% is always sampled so history stays continuous for sparklines
        try:    per = psutil.cpu_percent(percpu=True)
        except Exception: per = []
        self._percpu = per
        try:
            cpu = (sum(per) / len(per)) if per else psutil.cpu_percent()
        except Exception:
            cpu = 0.0
        self._hist['cpu'].append(cpu)
        if self.lbl_cpu:
            ghz = self._cpufreq.read_ghz()
            if ghz is None:
                ghz = self._slow.cpu_freq_ghz  # pre-fetched by _SlowPoller
            if self.lbl_cpu_top is not None:
                # stacked: GHz on top, % below
                self.lbl_cpu_top.config(text=(f'{ghz:.1f} GHz' if ghz else ''))
                self.lbl_cpu.config(text=f'{cpu:3.0f}%', fg=self._load_color(cpu))
            else:
                # single row: show the row the user picked (percent or detail)
                if self.cfg.get('single_row_mode') == 'detail' and ghz:
                    txt = f'{ghz:.1f} GHz'
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
                if self.cfg.get('single_row_mode') == 'detail':
                    txt = self._used_total(used_gb, vm.total / 1073741824)
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
            # pad to 7 (the max _fmt width, e.g. "12.5 Mb"/"10.5 Gb") so the
            # monospaced, fixed-width=7 net cells never resize → no black strip
            self.lbl_up.config(text=f'{self._fmt(up):>7}')
            self.lbl_dn.config(text=f'{self._fmt(dn):>7}')
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
                pd = self._slow.disk_perdisk  # pre-fetched by _SlowPoller
                if pd and self._perdisk_prev:
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
        # per-drive space % — throttled to every 5s (free space moves slowly,
        # and disk_usage hits the filesystem on every call)
        if self._disk_lbls:
            now_d = time.time()
            if now_d - getattr(self, '_diskspace_last_ts', 0) >= 5.0:
                self._diskspace_last_ts = now_d
                for drive, lbl in self._disk_lbls.items():
                    try:
                        u = psutil.disk_usage(drive + '\\')
                        lbl.config(text=f'{drive[0]} {u.percent:.0f}%',
                                   fg=self._load_color(u.percent))
                    except Exception:
                        pass
        if self.lbl_batt:
            b = self._slow.battery  # pre-fetched by _SlowPoller
            if b is not None:
                pct = int(b.percent)
                col = '#f85149' if pct <= 15 else ('#ffa657' if pct <= 30 else self.theme['val'])
                plug = '⚡' if b.power_plugged else ''
                self.lbl_batt.config(text=f'{plug}{pct}%', fg=col)
        if self.lbl_gpu:
            g = self._gpu
            if (getattr(self, 'lbl_gpu_top', None) is None
                    and self.cfg.get('single_row_mode') == 'detail'
                    and self._gpu_mem is not None):
                # single row in 'detail' mode → VRAM used/total
                self.lbl_gpu.config(
                    text=self._used_total(self._gpu_mem, self._vram_total),
                    fg=self._load_color(g if g is not None else 0))
            else:
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
        # ── power label (CPU+GPU estimated watts) ──
        if getattr(self, 'lbl_power', None):
            # nvidia_w comes from _SlowPoller (no subprocess on main thread)
            gpu_util = self._gpu if self._gpu is not None else 0.0
            self._power = get_power_estimate(cpu, gpu_util,
                                             self._cpu_name_cached, self._gpu_name_cached,
                                             nvidia_w=self._slow.nvidia_w)
            p = self._power
            total = int(round(p.get('total') or 0))
            if self.lbl_power_top is not None:
                # stacked: total on top, GPU watts (if available) below
                # ':>3' keeps "  9 W"/" 45 W"/"120 W" the same width (no resize)
                self.lbl_power_top.config(text=f'{total:>3} W')
                gpu_w = p.get('gpu')
                detail = f'{int(round(gpu_w))} g' if gpu_w is not None else p.get('source','')
                self.lbl_power.config(text=detail)
            else:
                self.lbl_power.config(text=f'{total:>3} W')
        # ── earthquake dot: blink while active, clear when expired ──
        if getattr(self, 'lbl_quake', None):
            active = (self._quake_active is not None
                      and time.time() < self._quake_active_until
                      and not self.cfg.get('quakes_mute'))
            if active:
                # gentle blink driven by the existing animation tick
                col = '#f85149' if (int(time.time() * 2) % 2 == 0) else '#7a1d1d'
                self.lbl_quake.config(text='🚨', fg=col)
            else:
                self.lbl_quake.config(text='')
                if self._quake_active and time.time() >= self._quake_active_until:
                    self._quake_active = None
        # (reschedule happens in the _update() wrapper above, in a finally-like
        # path so a failing tick can't freeze the loop)

    # ── drag ───────────────────────────────────────────────────────────
    def _drag_start(self, e):
        if self.cfg.get('locked'): return
        # the press must land on the BAR itself — never trust events that
        # bubbled in from elsewhere (e.g. a dialog that got rebind-ed once)
        self._drag_armed = True
        self._dx, self._dy = e.x, e.y; self._dragging = False
    def _drag_move(self, e):
        if self.cfg.get('locked'): return
        if not getattr(self, '_drag_armed', False):
            return   # no valid press on the bar → ignore orphan motion
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
        self._drag_armed = False
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
            # the background under the new position may differ — resample key
            self.root.after(300, self._adapt_key_color)

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
        m.add_command(label='  ⭐  ' + self.t('rate'),
                      command=lambda: self.root.after(1, self._open_review))
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

    def _open_review(self):
        """Open the Microsoft Store review page for PulseDeck. Inside MSIX the
        deep link jumps straight to the rating dialog; otherwise it opens the
        Store product page (falling back to the web listing)."""
        pid = '9P128R4SVXLC'
        try:
            if _is_msix():
                os.startfile(f'ms-windows-store://review/?ProductId={pid}')
            else:
                os.startfile(f'ms-windows-store://pdp/?ProductId={pid}')
        except Exception:
            try:
                webbrowser.open(f'https://apps.microsoft.com/detail/{pid}')
            except Exception:
                pass

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
