import mysql.connector
from mysql.connector import Error
import streamlit as st
import pandas as pd
import time
import paho.mqtt.client as mqtt

# ===============================
# MQTT CONFIG
# ===============================
MQTT_BROKER = "e445acd18dcb449b8d6d6f510cc62409.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC = "weight"
MQTT_USER = "pepa2025"
MQTT_PASSWORD = "Pepa2025"

client = mqtt.Client()

# Ajouter user + password
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    st.sidebar.success("MQTT connecté")
    client.loop_start()
    
   result = client.publish(MQTT_TOPIC, str(val))
   st.sidebar.write(result.rc)   # doit afficher 0 si OK
except Exception as e:
    st.sidebar.error(f"Erreur MQTT : {e}")

# ===============================
# Sidebar : envoi MQTT
# ===============================
st.sidebar.header("Envoi MQTT")

val = st.sidebar.number_input("Choisir un chiffre :", min_value=0, max_value=9999, value=0)

if st.sidebar.button("Envoyer sur MQTT"):
    client.publish(MQTT_TOPIC, str(val))
    st.sidebar.success(f"Envoyé : {val}")

# ===============================
# Sidebar widgets
# ===============================
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

# ===============================
# MySQL
# ===============================
host = "sql7.freesqldatabase.com"
user = "sql7810321"
password = "BwpCu2zT9b"
database = "sql7810321"

try:
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    if connection.is_connected():
        st.success("Connexion réussie à la base de données")

        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM poids ORDER BY Time DESC LIMIT 50;"
        cursor.execute(query)
        results = cursor.fetchall()

        df = pd.DataFrame(results)

except Error as e:
    st.error(f"Erreur lors de la connexion MySQL : {e}")
    df = pd.DataFrame()

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()

# ===============================
# Affichage graphique
# ===============================
if not df.empty:
    st.subheader("Graphique des poids dans le temps")

    df['Time'] = pd.to_datetime(df['Time'])
    df = df.sort_values('Time')

    chart = st.line_chart(df.iloc[:1][['Valeurs']].set_index(df.iloc[:1]['Time']))

    for i in range(1, len(df)):
        next_row = df.iloc[i:i+1]
        chart.add_rows(next_row.set_index('Time')[['Valeurs']])
        progress = int((i+1)/len(df) * 100)
        status_text.text(f"{progress}% complete")
        progress_bar.progress(progress)
        time.sleep(0.05)

progress_bar.empty()
st.button("Rerun")

