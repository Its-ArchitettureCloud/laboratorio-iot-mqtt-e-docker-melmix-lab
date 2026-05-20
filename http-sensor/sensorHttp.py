import json
import os
import random
import time
from datetime import datetime, timezone

import requests

SENSOR_ID = os.getenv("SENSOR_ID", "sensor-http-01")
TARGET_URL = os.getenv("TARGET_URL", "http://nodered:1880/sensor")
INTERVAL = int(os.getenv("SEND_INTERVAL", "5"))


print(f"[BOOT] Sensore HTTP {SENSOR_ID} avviato", flush=True)
print(f"[BOOT] Target URL: {TARGET_URL}", flush=True)
print(f"[BOOT] Intervallo invio: {INTERVAL}s", flush=True)

while True:
    sent_at = datetime.now(timezone.utc)

    payload = {
        "sensore": SENSOR_ID,
        "sensor_id": SENSOR_ID,
        "temperatura": round(random.uniform(18, 35), 1),
        "unita": "C",
        "origine": "docker-http-sensor",
        "protocollo": "http",
        "timestamp": sent_at.isoformat(),
        "sent_at": sent_at.isoformat(),
    }

    try:
        response = requests.post(TARGET_URL, json=payload, timeout=5)
        print(
            f"[POST] {TARGET_URL} -> {payload} "
            f"(status={response.status_code})",
            flush=True,
        )
    except requests.RequestException as error:
        print(f"[ERROR] Invio HTTP fallito: {error}", flush=True)

    time.sleep(INTERVAL)