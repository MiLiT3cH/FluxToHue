from phue import Bridge
import os
import json

HUE_BRIDGE_IP = '192.168.1.104'
CONFIG_FILE = 'gateway.conf'

# Ottieni la directory corrente in cui viene eseguito lo script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Definisci il percorso del file di configurazione per phue
phue_config_file = os.path.join(current_directory, 'phue_config.json')

# Funzione per ottenere l'username dal bridge Philips Hue
def get_hue_username(ip):
    bridge = Bridge(ip, config_file_path=phue_config_file)
    try:
        bridge.connect()  # Segui le istruzioni sul pulsante del bridge
        username = bridge.username
        print(f"Username ottenuto: {username}")
        return username
    except Exception as e:
        print(f"Errore di connessione al bridge: {e}")
        exit(1)

# Funzione per salvare l'username nel file di configurazione
def save_username_to_file(ip, username, config_file):
    config = {ip: {"username": username}}
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f)
        print(f"File di configurazione creato con successo: {config_file}")
    except Exception as e:
        print(f"Errore durante la creazione del file di configurazione: {e}")
        exit(1)

username = get_hue_username(HUE_BRIDGE_IP)
save_username_to_file(HUE_BRIDGE_IP, username, CONFIG_FILE)