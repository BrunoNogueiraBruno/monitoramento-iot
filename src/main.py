import network
import time
from simple import MQTTClient # blbioteca simple deve ser baixada no pip
import json
import random
from machine import Pin


led_status = Pin("LED", Pin.OUT)

# Configurações de Wi-Fi
SSID = "iPhone de ANDERSON"
PASSWORD = "123456789"

# Configurações do Wegnolog
BROKER = "broker.app.wnology.io"
PORT = 1883
ACCESS_KEY = "15560796-cb50-4daa-aab6-f82ea00a2297"
ACCESS_SECRET = "db2cabb1266af852d357a36589933ed3895b1456e51c4ec5620ad839f4b5126d"
DEVICE_ID = "67530faff3a509dde65767d2"


'''
Application Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzUzMTA3M2YzYTUwOWRkZTY1NzZhOTYiLCJzdWJ0eXBlIjoiYXBpVG9rZW4iLCJzY29wZSI6WyJhbGwuQXBwbGljYXRpb24iXSwiaWF0IjoxNzMzNDk2OTQ3LCJpc3MiOiJhcHAud25vbG9neS5pbyJ9.L-8WKDXlg-7oMipFi4X9MZNtqqAv2u1cycoBJwd6tuc

Application ID: 67530f02bad082895f35a33a

Scope: all.Application

Access Key:
15560796-cb50-4daa-aab6-f82ea00a2297

Access Secret:
db2cabb1266af852d357a36589933ed3895b1456e51c4ec5620ad839f4b5126d

Device ID:
67530faff3a509dde65767d2
'''


# Tópicos
TOPIC_PUBLISH = f"wnology/{DEVICE_ID}/state"
TOPIC_SUBSCRIBE = f"wnology/{DEVICE_ID}/command"

# Conecta ao Wi-Fi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print("Conectando ao Wi-Fi...")
    while not wlan.isconnected():
        led_status.value(not led_status.value())
        time.sleep(1)
    print("Conectado:", wlan.ifconfig())


# Callback para mensagens recebidas
def message_callback(topic, msg):
    print(f"Mensagem recebida no tópico {topic}: {msg}")

        # Decodificando e extraindo a chave `payload`
    try:
        # Decodifica a mensagem para string e converte em JSON
        data = json.loads(msg.decode('utf-8'))

        # Verifica se a chave `payload` existe e extrai o valor
        if 'payload' in data:
            payload_value = data['payload']
            print(f"Valor do payload: {payload_value}")
            led_status.value(payload_value)
        else:
            print("Chave 'payload' não encontrada na mensagem.")

    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")



# Publica dados no Wegnolog
def publish_data(client, topic, data):
    payload = json.dumps(data)
    client.publish(topic, payload)
    print(f"Dados enviados: {payload}")


# Função para gerar valores aleatórios de temperatura e umidade
def generate_temperature_humidity():
    temperature = round(random.uniform(-20.0, 60.0), 1)  # Temperatura entre -20.0°C e 60.0°C
    humidity = round(random.uniform(20.0, 100.0), 1)     # Umidade entre 20.0% e 100.0%
    return temperature, humidity


# Configuração principal
try:
    connect_wifi(SSID, PASSWORD)

    # Configura o cliente MQTT com Access Key e Secret
    client_id = DEVICE_ID  # Identificação do cliente MQTT
    client = MQTTClient(client_id, BROKER, user=ACCESS_KEY, password=ACCESS_SECRET, port=PORT)
    client.set_callback(message_callback)
    client.connect()

    # Assina o tópico de comandos
    client.subscribe(TOPIC_SUBSCRIBE)
    print(f"Assinado no tópico {TOPIC_SUBSCRIBE}")

    # Loop principal
    while True:
        # Publica um valor simulado (ex.: temperatura e umidade)
        temperatura, umidade = generate_temperature_humidity()
        publish_data(client, TOPIC_PUBLISH,{"data" : {"temperatura" : temperatura, "umidade" : umidade}})

        # Aguarda mensagens
        client.check_msg()

        # Atraso antes do próximo envio
        time.sleep(10)

except Exception as e:
    print("Erro:", e)
finally:
    client.disconnect()
    print("Desconectado do MQTT.")
