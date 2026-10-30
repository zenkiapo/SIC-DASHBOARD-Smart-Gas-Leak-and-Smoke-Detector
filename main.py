import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import math

broker = "broker.hivemq.com"
port = 1883

gas_data = []
temp_data = []
hum_data = []

plt.style.use('dark_background')
plt.rcParams['axes.facecolor'] = '#1e1e2f'
plt.rcParams['figure.facecolor'] = '#1e1e2f'
plt.rcParams['grid.color'] = '#2c2c3f'
plt.rcParams['text.color'] = 'white'

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(" Terhubung ke Broker HiveMQ!")
        print(" Menunggu data dari sensor...")
        client.subscribe("bagaskara_v3/sic8/udara/gas")
        client.subscribe("bagaskara_v3/sic8/udara/suhu")
        client.subscribe("bagaskara_v3/sic8/udara/kelembapan")
    else:
        print(f"❌ Gagal terhubung! Kode: {reason_code}")

def on_message(client, userdata, msg):
    try:
        raw_payload = msg.payload.decode("utf-8").strip()
        topic = msg.topic
        print(f"[DEBUG MQTT] Topik: {topic} | Nilai: {raw_payload}")

        payload = float(raw_payload)

        if math.isnan(payload):
            return

        sensor_type = topic.split("/")[-1]

        if sensor_type == "gas":
            gas_data.append(payload)
            if len(gas_data) > 20: gas_data.pop(0)
        elif sensor_type == "suhu":
            temp_data.append(payload)
            if len(temp_data) > 20: temp_data.pop(0)
            print(f"-> Suhu masuk: {payload}")
        elif sensor_type == "kelembapan":
            hum_data.append(payload)
            if len(hum_data) > 20: hum_data.pop(0)
            print(f"-> Kelembapan masuk: {payload}")

    except Exception as e:
        print("❌ Error memproses data:", e)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port, 60)
client.loop_start()

plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [2, 1]})
fig.suptitle('Sistem Deteksi Kebocoran Gas & Asap', fontsize=16, fontweight='bold', color='#00d2d3')
fig.tight_layout(pad=4.0)

try:
    while True:
        ax1.clear()
        ax2.clear()

        if gas_data:
            color_gas = '#ff4757' if gas_data[-1] > 400 else '#1e90ff'
            ax1.plot(gas_data, color=color_gas, linewidth=3, marker='o', markersize=6, markerfacecolor='white')
            ax1.fill_between(range(len(gas_data)), gas_data, color=color_gas, alpha=0.1)

        ax1.set_title('Pemantauan Kebocoran Gas & Asap (PPM)', color='white', pad=15)
        ax1.set_ylabel('Konsentrasi (PPM)', color='#a0aabf')
        ax1.set_xlim(0, 19)
        ax1.set_ylim(0, 1000)
        ax1.axhline(y=400, color='#ff4757', linestyle='--', linewidth=2, label='Batas Bahaya (400 PPM)')
        ax1.legend(loc='upper right', facecolor='#2f3542', edgecolor='none')
        ax1.grid(True, linestyle='--', alpha=0.5)

        if temp_data:
            ax2.plot(temp_data, color='#ffa502', linewidth=2, marker='s', label='Suhu (°C)')
        if hum_data:
            ax2.plot(hum_data, color='#2ed573', linewidth=2, marker='^', label='Kelembapan (%)')

        ax2.set_title('Kondisi Lingkungan (DHT22 - Suhu & Kelembapan)', color='white', pad=10)
        ax2.set_ylabel('Nilai', color='#a0aabf')
        ax2.set_xlim(0, 19)
        ax2.set_ylim(0, 100)  # Skala 0-100 mencakup suhu (°C) dan kelembapan (%)
        ax2.legend(loc='upper right', facecolor='#2f3542', edgecolor='none')
        ax2.grid(True, linestyle='--', alpha=0.5)

        ax1.set_xticklabels([])
        ax2.set_xticklabels([])

        plt.pause(1)

except KeyboardInterrupt:
    print("Pemantauan dihentikan manual oleh pengguna.")

client.loop_stop()