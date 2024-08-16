HueToFlux Server:
Questo script permette di controllare strisce LED cinesi (commandabili tramite libreria fluxled)
tramite controller Philips HUE.

Come Funziona?
 1) creando una finta lampada sul controller Philips Hue: "Emulated Light"
 2) riceve il suo stato e ne converte i dati
 3) le invia al controller cinese usando la libreria flux led

Setup:
 1) Modificare la stringa HUE_bridge_IP sullo script "configen.py"
 2) avviare lo script "configen.py" e premere il tasto di sync sul controller. Dovrebbe crearsi un file (gateway.conf) contenente le credenziali
 3) Creare una finta lampada HUE (usando pi-hue tramite l'interfaccia web creare una lampada chiamata "Emulated Light")
 3*) se volete sincronizzarla a una lampada esistente, modificare il parametro  sullo script "fluxbrindge.py" (emulated_light = bridge.get_light_objects('name').get('LA_TUA_LAMPADA_QUI'))
 4) modificare nello script fluxbridge: "HUE_bridge_IP=" l'ip del bridge philips hue , e su "LED_IP=" l'ip del controller cinese da commandare
 5) avviare lo script fluxbridge.py e testare
 
Testato personalmente con un controller pi-hub su docker e funzionava abbastanzaz bene