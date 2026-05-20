# Laboratorio IoT - MQTT, Node-RED, MailHog e InfluxDB

Repository GitHub Classroom per il laboratorio IoT con Docker Compose.

## Stato del lavoro

La consegna base richiesta dal PDF e' completata e pushata. Include:

- broker MQTT Mosquitto;
- 10 sensori MQTT containerizzati;
- Node-RED come consumer MQTT;
- dashboard FlowFuse multi-sensore;
- MailHog per gli alert email.

L'estensione locale aggiunge:

- 10 sensori HTTP containerizzati;
- endpoint HTTP Node-RED /sensor;
- normalizzazione comune dei dati MQTT e HTTP;
- dashboard con protocollo e latenza;
- InfluxDB per salvare lo storico delle temperature.

## Servizi

| Servizio | Porta | Ruolo |
| --- | --- | --- |
| Mosquitto | 1883 | Broker MQTT |
| Node-RED | 1880 | Flow, dashboard, alert, endpoint HTTP |
| MailHog | 8025, 1025 | UI email e SMTP di test |
| InfluxDB | 8086 | Database time-series |

## Credenziali

MQTT Mosquitto:

- username: melissio
- password: mqtt123

InfluxDB:

- URL: http://localhost:8086
- username: melissio
- password: influx12345
- org: its
- bucket: iot
- token: its-iot-token

## Avvio

Dalla cartella del repository:

```bash
docker compose up --build
```

Se Docker richiede permessi di amministratore:

```bash
sudo docker compose up --build
```

## URL utili

- Node-RED editor: http://localhost:1880
- Dashboard: http://localhost:1880/dashboard/aula-iot
- MailHog: http://localhost:8025
- InfluxDB: http://localhost:8086

## Flusso MQTT

I sensori MQTT sono definiti in `docker-compose.yml` come `sensor_1` ... `sensor_10`.
Usano tutti la stessa immagine costruita da `sensor/Dockerfile` e lo stesso codice `sensor/sensor.py`.

Esempi di topic:

```text
iot/aula/sensor01/temperatura
iot/aula/sensor02/temperatura
iot/aula/sensor10/temperatura
```

Node-RED ascolta tutti i topic con:

```text
iot/aula/+/temperatura
```

## Flusso HTTP

I sensori HTTP sono definiti in `docker-compose.yml` come `sensor_http_1` ... `sensor_http_10`.
Usano il codice in `http-sensor/sensorHttp.py` e inviano POST a:

```text
http://nodered:1880/sensor
```

Test manuale dell'endpoint HTTP:

```bash
curl -X POST http://localhost:1880/sensor \
  -H "Content-Type: application/json" \
  -d '{"sensor_id":"postman-01","temperatura":31.5,"unita":"C"}'
```

## InfluxDB

Node-RED scrive nel bucket `iot`, measurement `temperatura`.

Campi principali:

- `valore`: temperatura numerica;
- `latency_ms`: latenza calcolata.

Tag principali:

- `sensore`;
- `protocollo` con valore `mqtt` o `http`.

Query Flux per controllare gli ultimi dati:

```flux
from(bucket: "iot")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "temperatura")
  |> filter(fn: (r) => r._field == "valore" or r._field == "latency_ms")
```

Media latenza per protocollo:

```flux
from(bucket: "iot")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "temperatura")
  |> filter(fn: (r) => r._field == "latency_ms")
  |> group(columns: ["protocollo"])
  |> mean()
```

## Alert email

Node-RED invia email a MailHog quando `temperatura > 30`.
Il flow include un cooldown di 5 minuti per sensore, cosi' lo stesso sensore non genera email continue.

## Verifiche rapide

Lista servizi Compose:

```bash
docker compose config --services
```

Verifica MQTT:

```bash
sudo docker exec mqtt-broker mosquitto_sub \
  -h localhost -p 1883 -u melissio -P mqtt123 \
  -t 'iot/aula/+/temperatura' -C 5
```

Verifica InfluxDB:

```bash
curl http://localhost:8086/health
```
