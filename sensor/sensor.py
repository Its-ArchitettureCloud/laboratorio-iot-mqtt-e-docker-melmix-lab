import json
import os
import random
import socket
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", "1883"))
USERNAME = os.getenv("MQTT_USERNAME", "melissio")
PASSWORD = os.getenv("MQTT_PASSWORD", "mqtt123")
SENSOR_ID = os.getenv("SENSOR_ID", "sensore1")
TOPIC = os.getenv("MQTT_TOPIC", f"stanza/{SENSOR_ID}/temperatura")
INTERVAL = int(os.getenv("SEND_INTERVAL", "5"))


def wait_for_broker(host, port):
    print(f"[WAIT] Attendo broker MQTT {host}:{port}", flush=True)

    while True:
        try:
            with socket.create_connection((host, port), timeout=5):
                print("[WAIT] Broker MQTT raggiungibile", flush=True)
                return
        except OSError as error:
            print(f"[WAIT] Broker non disponibile ({error}), ritento...", flush=True)
            time.sleep(2)


print(f"[BOOT] Sensore {SENSOR_ID} avviato", flush=True)
print(f"[BOOT] Broker MQTT: {BROKER}:{PORT}", flush=True)
print(f"[BOOT] Topic: {TOPIC}", flush=True)
print(f"[BOOT] Intervallo invio: {INTERVAL}s", flush=True)

wait_for_broker(BROKER, PORT)

client = mqtt.Client(
    client_id=SENSOR_ID,
    protocol=mqtt.MQTTv311,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
)

client.username_pw_set(USERNAME, PASSWORD)
client.connect(BROKER, PORT)
client.loop_start()

print("[MQTT] Connesso al broker", flush=True)

while True:
    temperatura = round(random.uniform(18, 35), 1)
    payload = {
        "sensore": SENSOR_ID,
        "temperatura": temperatura,
        "unita": "C",
        "origine": "docker-sensor",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    result = client.publish(TOPIC, json.dumps(payload), qos=0)
    print(f"[PUBLISH] {TOPIC} -> {payload} (rc={result.rc})", flush=True)

    time.sleep(INTERVAL)
