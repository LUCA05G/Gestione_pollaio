# Versione Streamlit della tua app con icona personalizzata
import streamlit as st
import json
import os
from datetime import date, timedelta
from PIL import Image

FILE_DATI = "dati_polli.json"

# ---------------- Funzioni per i dati ---------------- #
def salva_dati(dati):
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f)

def carica_dati():
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r") as f:
            return json.load(f)
    else:
        return {
            "box1_maschi": 0,
            "box1_femmine": 0,
            "box2_maschi": 0,
            "box2_femmine": 0
        }

# ---------------- Funzione di calcolo ---------------- #
def esegui_calcolo(maschi, femmine, mangime, giorno_iniziale):
    try:
        with open("Performance Femmine.txt", "r", encoding="utf-8") as fileF:
            valoriF = [float(line.strip().split()[1]) for line in fileF]

        with open("Performance Maschi.txt", "r", encoding="utf-8") as fileM:
            valoriM = [float(line.strip().split()[1]) for line in fileM]

        indice = giorno_iniziale - 1

        if indice >= len(valoriM) or indice >= len(valoriF):
            return "Errore: il giorno iniziale supera i dati disponibili."

        giorni = 0
        while mangime > 0 and indice < len(valoriM):
            consumoM = maschi * valoriM[indice]
            consumoF = femmine * valoriF[indice]
            consumo_totale = consumoM + consumoF
            mangime -= consumo_totale
            if mangime >= 0:
                giorni += 1
                indice += 1
            else:
                break

        oggi = date.today()
        futura = oggi + timedelta(days=giorni)

        if mangime < 0:
            return (f"Mangime insufficiente dopo il giorno {indice}.\n"
                    f"Ultimo giorno completo: {futura.strftime('%A %d %B %Y')}\n"
                    f"Mangime residuo: {mangime + consumoF + consumoM:.3f} kg")
        elif mangime == 0:
            return f"Mangime terminato esattamente il {futura.strftime('%A %d %B %Y')}"
        else:
            return (f"Mangime sufficiente fino al {futura.strftime('%A %d %B %Y')}\n"
                    f"Mangime residuo: {mangime:.3f} kg")

    except Exception as e:
        return f"Errore: {str(e)}"

# ---------------- Gestione polli morti ---------------- #
def inserisci_morti():
    st.header("Inserisci polli morti")
    box = st.radio("Seleziona il BOX:", [1, 2], horizontal=True)
    morti_m = st.number_input("Maschi morti", min_value=0, step=1)
    morti_f = st.number_input("Femmine morte", min_value=0, step=1)
    if st.button("Conferma"):
        try:
            if box == 1:
                dati["box1_maschi"] = max(0, dati["box1_maschi"] - morti_m)
                dati["box1_femmine"] = max(0, dati["box1_femmine"] - morti_f)
            else:
                dati["box2_maschi"] = max(0, dati["box2_maschi"] - morti_m)
                dati["box2_femmine"] = max(0, dati["box2_femmine"] - morti_f)
            salva_dati(dati)
            st.success("Dati aggiornati dopo inserimento morti.")
        except Exception as e:
            st.error(f"Errore: {str(e)}")

# ---------------- Streamlit App ---------------- #
icon_path = "icona.ico"
if os.path.exists(icon_path):
    st.set_page_config(page_title="Gestione Polli", page_icon=Image.open(icon_path), layout="centered")
else:
    st.set_page_config(page_title="Gestione Polli", page_icon="🐔", layout="centered")

st.title("Gestione Polli e Mangime")
dati = carica_dati()

with st.sidebar:
    st.header("Dati Box")
    dati["box1_maschi"] = st.number_input("Box 1 - Maschi", 0, 1000, dati["box1_maschi"])
    dati["box1_femmine"] = st.number_input("Box 1 - Femmine", 0, 1000, dati["box1_femmine"])
    dati["box2_maschi"] = st.number_input("Box 2 - Maschi", 0, 1000, dati["box2_maschi"])
    dati["box2_femmine"] = st.number_input("Box 2 - Femmine", 0, 1000, dati["box2_femmine"])
    if st.button("Salva dati"):
        salva_dati(dati)
        st.success("Dati salvati correttamente.")

inserisci_morti()

st.header("Simula consumo mangime")
tipo = st.selectbox("Tipo calcolo", ["misto", "solo maschi", "solo femmine"])

maschi = femmine = 0
if tipo in ["misto", "solo maschi"]:
    maschi = st.number_input("Numero maschi", 0, 1000, 0)
if tipo in ["misto", "solo femmine"]:
    femmine = st.number_input("Numero femmine", 0, 1000, 0)

mangime = st.number_input("Mangime disponibile (kg)", 0.0, 9999.0, 0.0, step=0.1)
giorno = st.number_input("Giorno iniziale (1 = primo giorno)", 1, 100, 1)

if st.button("Calcola durata mangime"):
    risultato = esegui_calcolo(maschi, femmine, mangime, giorno)
    st.success(risultato)
