import streamlit as st
import pandas as pd
from datetime import date

# Configuration de la page
st.set_page_config(page_title="Système de Gestion de Présences et d'Absences", layout="centered")

# Titre et description
st.title("📅 Système de Gestion de Présences et d'Absences - CHU")
st.write("Cette application permet de gérer les présences et absences en important des fichiers Excel et en générant des rapports par période.")

# Fonction pour traiter les présences
def process_attendance_data(df):
    if not {'Nom', 'Heure'}.issubset(df.columns):
        st.error("Le fichier doit contenir les colonnes 'Nom' et 'Heure'.")
        return None
    df['Heure'] = pd.to_datetime(df['Heure'])
    df['Date'] = df['Heure'].dt.date
    df = df.sort_values(by=['Nom', 'Date', 'Heure'])
    df_filtered = df.groupby(['Nom', 'Date']).agg(
        Heure_Arrive=('Heure', 'first'),
        Heure_Sortie=('Heure', 'last')
    ).reset_index()
    df_filtered['Heure d\'arrive et de sortie'] = (
        df_filtered['Heure_Arrive'].dt.strftime('%H:%M:%S') + ' - ' + df_filtered['Heure_Sortie'].dt.strftime('%H:%M:%S')
    )
    return df_filtered[['Date', 'Nom', 'Heure d\'arrive et de sortie']]

# Fonction pour traiter les absences
def process_absence_data(df):
    if not {'Nom', 'Heure'}.issubset(df.columns):
        st.error("Le fichier doit contenir les colonnes 'Nom' et 'Heure'.")
        return None
    df['Date'] = pd.to_datetime(df['Heure']).dt.date
    all_dates = pd.date_range(df['Date'].min(), df['Date'].max()).date
    unique_names = df['Nom'].unique()
    absence_data = [{'Nom': name, 'Date': date} for name in unique_names 
                    for date in all_dates if date not in df[df['Nom'] == name]['Date'].unique()]
    return pd.DataFrame(absence_data)

# Fonction pour générer le rapport
def generate_report(df, period):
    df['Date'] = pd.to_datetime(df['Date'])
    if period == 'Jour':
        report = df.groupby(df['Date'].dt.date).size().reset_index(name="Nombre de présences")
    elif period == 'Semaine':
        report = df.groupby(df['Date'].dt.isocalendar().week).size().reset_index(name="Nombre de présences")
    elif period == 'Mois':
        report = df.groupby(df['Date'].dt.to_period('M')).size().reset_index(name="Nombre de présences")
    elif period == 'Trimestre':
        report = df.groupby(df['Date'].dt.to_period('Q')).size().reset_index(name="Nombre de présences")
    elif period == 'Année':
        report = df.groupby(df['Date'].dt.year).size().reset_index(name="Nombre de présences")
    report.columns = [period, "Nombre de présences"]
    return report

# Interface utilisateur Streamlit
uploaded_file = st.file_uploader("📁 Importez un fichier Excel", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("Fichier importé avec succès.")

    option = st.selectbox("Sélectionnez l'action", ["Présences", "Absences", "Rapport par période"])

    if option == "Présences":
        processed_data = process_attendance_data(df)
        if processed_data is not None:
            st.write("Tableau des Présences", processed_data)
            st.download_button("💾 Télécharger les présences en Excel", data=processed_data.to_excel(index=False), file_name="presences.xlsx")

    elif option == "Absences":
        absence_data = process_absence_data(df)
        if absence_data is not None:
            st.write("Tableau des Absences", absence_data)
            st.download_button("💾 Télécharger les absences en Excel", data=absence_data.to_excel(index=False), file_name="absences.xlsx")

    elif option == "Rapport par période":
        period = st.selectbox("Choisissez la période", ["Jour", "Semaine", "Mois", "Trimestre", "Année"])
        report = generate_report(df, period)
        if report is not None:
            st.write(f"Rapport de Présences par {period}", report)
            st.download_button("💾 Télécharger le rapport en Excel", data=report.to_excel(index=False), file_name=f"rapport_{period}.xlsx")

st.sidebar.write("🎨 Personnalisez l'interface")
st.sidebar.color_picker("Choisissez une couleur de fond")
