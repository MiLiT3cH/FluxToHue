import os
import json
import time
import subprocess
import threading
from phue import Bridge
import asyncio
from colormath.color_objects import xyYColor, sRGBColor
from colormath.color_conversions import convert_color

# Configurazione del Bridge Philips Hue
HUE_BRIDGE_IP = '192.168.1.104'
CONFIG_FILE = 'gateway.conf'

# Configurazione del dispositivo LED
LED_IP = '192.168.1.9'

# Ottieni la directory corrente in cui viene eseguito lo script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Funzione per leggere il file di configurazione
def load_config(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"File di configurazione letto con successo: {config_file}")
        print(f"Contenuto del file di configurazione: {config}")
        return config
    except Exception as e:
        print(f"Errore durante la lettura del file di configurazione: {e}")
        exit(1)

# Carica la configurazione
config = load_config(os.path.join(current_directory, CONFIG_FILE))
username = config.get(HUE_BRIDGE_IP, {}).get('username')

# Connessione al bridge Philips Hue
bridge = Bridge(HUE_BRIDGE_IP, username=username, config_file_path=os.path.join(current_directory, 'phue_config.json'))
bridge.connect()

# Funzione per convertire xy e luminosità in esadecimale
def convert_xy_bri_to_hex(x, y, bri):
    # Convert xy and brightness (Y) to xyY color object
    Y = bri / 255.0  # Normalize brightness to [0, 1]
    xyY = xyYColor(x, y, Y)
    
    # Convert xyY to sRGB
    rgb = convert_color(xyY, sRGBColor)
    
    # Ensure RGB values are within bounds and convert to integers
    r = int(max(0, min(rgb.rgb_r * 255, 255)))
    g = int(max(0, min(rgb.rgb_g * 255, 255)))
    b = int(max(0, min(rgb.rgb_b * 255, 255)))
    
    # Convert RGB to hexadecimal
    hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
    return hex_color

# Funzione asincrona per comandare la lampada LED tramite flux_led
async def control_led(ip, command):
    try:
        result = await asyncio.create_subprocess_exec(
            'flux_led', ip, *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await result.communicate()
        print("Output del comando:", stdout.decode())
        if result.returncode == 0:
            print(f"Comando {command} eseguito con successo sulla lampada con IP {ip}")
        else:
            print(f"Errore durante l'esecuzione del comando sulla lampada: {stderr.decode()}")
    except Exception as e:
        print(f"Errore durante l'esecuzione del comando sulla lampada: {e}")

# Funzione per ottenere lo stato reale della lampada dal bridge Philips Hue
def get_real_hue_light_state():
    try:
        emulated_light = bridge.get_light_objects('name').get('Emulated Light')
        if emulated_light is not None:
            return {
                "on": emulated_light.on,
                "xy": emulated_light.xy,
                "brightness": emulated_light.brightness
            }
        else:
            print("Lampada emulata non trovata nel bridge.")
            return None
    except Exception as e:
        print("Errore durante il recupero dello stato reale della lampada:", e)
        return None

# Funzione asincrona per sincronizzare lo stato della luce Hue con la lampada LED
async def sync_lights():
    try:
        # Ottieni lo stato della lampada emulata
        light_state = get_real_hue_light_state()
        if light_state is None:
            return

        print("Stato della luce emulata:", light_state)

        # Sincronizza lo stato di accensione/spegnimento
        command = ['--on'] if light_state["on"] else ['--off']
        await control_led(LED_IP, command)

        # Sincronizza il colore
        if light_state["on"]:
            hue_xy = light_state["xy"]
            hue_brightness = light_state["brightness"]
            print("Valori xy e luminosità della lampada emulata:", hue_xy, hue_brightness)
            hex_color = convert_xy_bri_to_hex(hue_xy[0], hue_xy[1], hue_brightness)
            print("Valore esadecimale calcolato:", hex_color)
            await control_led(LED_IP, ['-c', hex_color])
    except Exception as e:
        print("Errore durante la sincronizzazione delle luci:", e)

# Funzione per sincronizzare le luci in background
async def sync_lights_background():
    while True:
        await sync_lights()
        await asyncio.sleep(0.1)

# Avvia il loop principale di asyncio
async def main():
    await sync_lights_background()

# Avvia il programma asincrono
asyncio.run(main())