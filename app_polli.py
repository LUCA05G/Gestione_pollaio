import streamlit as st
import json
import os
from datetime import date, timedelta
import locale

FILE_DATI = "dati_polli.json"

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

def salva_dati(dati):
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f)

def esegui_calcolo(maschi, femmine, mangime, giorno_iniziale):
    try:
        with open("Performance Femmine.txt", "r", encoding="utf-8") as fileF:
            valoriF = [float(line.strip().split()[1]) for line in fileF]

        with open("Performance Maschi.txt", "r", encoding="utf-8") as fileM:
            valoriM = [float(line.strip().split()[1]) for line in fileM]

        indice = giorno_iniziale - 1

        if indice < 0 or indice >= len(valoriM) or indice >= len(valoriF):
            return "Errore: giorno iniziale fuori range dati."

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
        locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')

        if mangime < 0:
            risultato = f"Il mangime durerà fino a: {futura.strftime('%A %d %B %Y')}\n(giorno {indice})\n" \
                       f"Il {futura.strftime('%A %d %B %Y')} ci saranno {mangime + consumoF + consumoM:.3f} kg di mangime, non sufficienti per il giorno successivo"
        elif mangime == 0:
            risultato = f"Il mangime durerà fino a: {futura.strftime('%A %d %B %Y')}\n" \
                       f"Da {futura.strftime('%A %d %B %Y')} non ci sarà più mangime a disposizione"
        else:
            risultato = f"Il mangime è sufficiente fino al giorno {giorni} ({futura.strftime('%A %d %B %Y')}).\n" \
                       f"Restano {mangime:.3f} kg di mangime."

        return risultato

    except Exception as e:
        return f"Errore nel calcolo: {str(e)}"

# Inizializza dati
if "dati_salvati" not in st.session_state:
    st.session_state.dati_salvati = carica_dati()

# Variabili temporanee per morti (in session state)
if "morti_m_temp" not in st.session_state:
    st.session_state.morti_m_temp = 0
if "morti_f_temp" not in st.session_state:
    st.session_state.morti_f_temp = 0
if "box_scelto_temp" not in st.session_state:
    st.session_state.box_scelto_temp = 1

# Sidebar: modifica dati box
st.sidebar.header("Dati Box")

for box_num in [1, 2]:
    maschi_key = f"box{box_num}_maschi"
    femmine_key = f"box{box_num}_femmine"
    st.session_state.dati_salvati[maschi_key] = st.sidebar.number_input(
        f"Maschi BOX {box_num}",
        min_value=0,
        value=st.session_state.dati_salvati[maschi_key],
        key=maschi_key
    )
    st.session_state.dati_salvati[femmine_key] = st.sidebar.number_input(
        f"Femmine BOX {box_num}",
        min_value=0,
        value=st.session_state.dati_salvati[femmine_key],
        key=femmine_key
    )

# Input morti in sidebar, aggiornati in variabili temporanee
st.sidebar.header("Inserisci Polli Morti")
st.session_state.box_scelto_temp = st.sidebar.radio("Seleziona BOX", [1, 2], index=st.session_state.box_scelto_temp - 1, key="box_scelto_temp")
st.session_state.morti_m_temp = st.sidebar.number_input("Maschi morti", min_value=0, step=1, value=st.session_state.morti_m_temp, key="morti_m_temp")
st.session_state.morti_f_temp = st.sidebar.number_input("Femmine morte", min_value=0, step=1, value=st.session_state.morti_f_temp, key="morti_f_temp")

# Pulsante salva dati applica anche morti
if st.sidebar.button("Salva dati"):
    dati = st.session_state.dati_salvati
    # Applica morti temporanei
    box = st.session_state.box_scelto_temp
    morti_m = st.session_state.morti_m_temp
    morti_f = st.session_state.morti_f_temp

    if box == 1:
        dati["box1_maschi"] = max(0, dati["box1_maschi"] - morti_m)
        dati["box1_femmine"] = max(0, dati["box1_femmine"] - morti_f)
    else:
        dati["box2_maschi"] = max(0, dati["box2_maschi"] - morti_m)
        dati["box2_femmine"] = max(0, dati["box2_femmine"] - morti_f)

    salva_dati(dati)
    st.success("Dati aggiornati e salvati correttamente.")
    # Reset morti temporanei a zero dopo salvataggio
    st.session_state.morti_m_temp = 0
    st.session_state.morti_f_temp = 0

# Main app
st.title("Gestione Polli e Mangime")

# Visualizza dati correnti
st.subheader("Dati attuali box")
dati = st.session_state.dati_salvati
st.write(f"BOX 1 - Maschi: {dati['box1_maschi']}, Femmine: {dati['box1_femmine']}")
st.write(f"BOX 2 - Maschi: {dati['box2_maschi']}, Femmine: {dati['box2_femmine']}")

# Calcolo durata mangime
st.header("Calcola durata mangime")

tipo = st.selectbox("Tipo calcolo", ["misto", "solo maschi", "solo femmine"])
maschi = femmine = 0
if tipo in ["misto", "solo maschi"]:
    maschi = st.number_input("Numero maschi", min_value=0, step=1, key="calcolo_maschi")
if tipo in ["misto", "solo femmine"]:
    femmine = st.number_input("Numero femmine", min_value=0, step=1, key="calcolo_femmine")

mangime = st.number_input("Mangime disponibile (kg)", min_value=0.0, step=0.1, format="%.3f", key="calcolo_mangime")
giorno_iniziale = st.number_input("Giorno iniziale (1 = primo giorno)", min_value=1, step=1, key="calcolo_giorno")

if st.button("Calcola durata mangime"):
    risultato = esegui_calcolo(maschi, femmine, mangime, giorno_iniziale)
    st.success(risultato)
