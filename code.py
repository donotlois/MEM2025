import mysql.connector
from mysql.connector import Error
import streamlit as st
import pandas as pd
import time

# ===============================
# Sidebar widgets
# ===============================
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

# ===============================
# Paramètres de connexion MySQL
# ===============================
host = "sql7.freesqldatabase.com"
user = "sql7810321"
password = "BwpCu2zT9b"
database = "sql7810321"

# ===============================
# Connexion et récupération des données
# ===============================
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
        query = "SELECT * FROM poids ORDER BY Time DESC LIMIT 500;"  # Tri par Time
        cursor.execute(query)
        results = cursor.fetchall()

        # Convertir en DataFrame pour le graphique
        df = pd.DataFrame(results)

except Error as e:
    st.error(f"Erreur lors de la connexion à MySQL : {e}")
    df = pd.DataFrame()  # dataframe vide en cas d'erreur

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()

# ===============================
# Affichage du graphique
# ===============================
if not df.empty:
    st.subheader("Graphique des poids dans le temps")

    # S'assurer que 'Time' est bien au format datetime
    df['Time'] = pd.to_datetime(df['Time'])
    df = df.sort_values('Time')

    # Initialiser le graphique avec la première ligne
    chart = st.line_chart(df.iloc[:1][['Valeurs']].set_index(df.iloc[:1]['Time']))

    # Ajouter les lignes suivantes progressivement
    for i in range(1, len(df)):
        next_row = df.iloc[i:i+1]
        chart.add_rows(next_row.set_index('Time')[['Valeurs']])
        progress = int((i+1)/len(df)*100)
        status_text.text(f"{progress}% complete")
        progress_bar.progress(progress)
        time.sleep(0.05)  # petite pause pour simuler l'animation

progress_bar.empty()
st.button("Rerun")
