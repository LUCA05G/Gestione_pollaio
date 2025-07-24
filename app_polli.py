import streamlit as st
from datetime import date, timedelta
import locale
import json
import os

FILE_DATI = "dati_polli.json"

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

def calcola_durata_mangime(maschi, femmine, mangime, giorno_iniziale):
    if giorno_iniziale < 1:
        raise ValueError("Il giorno iniziale deve essere almeno 1.")
    with open("Performance Femmine.txt", "r", encoding="utf-8") as fileF:
        valoriF = [float(line.strip().split()[1]) for line in fileF]

    with open("Performance Maschi.txt", "r", encoding="utf-8") as fileM:
        valoriM = [float(line.strip().split()[1]) for line in fileM]

    indice = giorno_iniziale - 1
    if indice >= len(valoriM) or indice >= len(valoriF):
        raise ValueError("Il giorno iniziale è oltre l'ultimo giorno disponibile nei dati.")

    giorni = 0
    mangime_rimasto = mangime

    while mangime_rimasto > 0 and indice < len(valoriM):
        consumoM = maschi * valoriM[indice]
        consumoF = femmine * valoriF[indice]
        consumo_totale = consumoM + consumoF
        mangime_rimasto -= consumo_totale
        if mangime_rimasto >= 0:
            giorni += 1
            indice += 1
        else:
            break

    oggi = date.today()
    futura = oggi + timedelta(days=giorni)
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')

    if mangime_rimasto < 0:
        risultato = f"Il mangime durerà fino a: {futura.strftime('%A %d %B %Y')}\n (giorno {indice})\nIl {futura.strftime('%A %d %B %Y')} ci saranno {mangime_rimasto + consumo_totale:.3f} kg di mangime, non sufficienti per il giorno successivo"
    elif mangime_rimasto == 0:
        risultato = f"Il mangime durerà fino a: {futura.strftime('%A %d %B %Y')}\nDa {futura.strftime('%A %d %B %Y')} non ci sarà più mangime a disposizione"
    else:
        risultato = (f"Il mangime è sufficiente per tutti i giorni disponibili fino al 56esimo ({futura.strftime('%A %d %B %Y')}),\n"
                     f"Il {futura.strftime('%A %d %B %Y')} resteranno {mangime_rimasto:.3f} kg di mangime.")

    return risultato

# --- Inizio app Streamlit ---

st.title("Gestione Polli e Mangime")

# Caricamento dati
if "dati_salvati" not in st.session_state:
    st.session_state.dati_salvati = carica_dati()

def aggiorna_dati_box(box_num, maschi, femmine):
    st.session_state.dati_salvati[f"box{box_num}_maschi"] = maschi
    st.session_state.dati_salvati[f"box{box_num}_femmine"] = femmine
    salva_dati(st.session_state.dati_salvati)
    st.success(f"Dati BOX {box_num} aggiornati.")

def inserisci_morti(box_num, morti_m, morti_f):
    dati = st.session_state.dati_salvati
    dati[f"box{box_num}_maschi"] = max(0, dati[f"box{box_num}_maschi"] - morti_m)
    dati[f"box{box_num}_femmine"] = max(0, dati[f"box{box_num}_femmine"] - morti_f)
    salva_dati(dati)
    st.session_state.dati_salvati = dati
    st.success("Dati aggiornati dopo inserimento morti.")

# Sidebar: mostra contatori attuali
st.sidebar.header("Dati attuali")
st.sidebar.write(f"BOX 1\nMaschi: {st.session_state.dati_salvati['box1_maschi']}\nFemmine: {st.session_state.dati_salvati['box1_femmine']}")
st.sidebar.write(f"BOX 2\nMaschi: {st.session_state.dati_salvati['box2_maschi']}\nFemmine: {st.session_state.dati_salvati['box2_femmine']}")

menu = st.sidebar.selectbox("Menu", [
    "Modifica BOX 1",
    "Modifica BOX 2",
    "Inserisci polli morti",
    "Calcolo mangime misto",
    "Calcolo solo maschi",
    "Calcolo solo femmine"
])

if menu.startswith("Modifica BOX"):
    box_num = int(menu[-1])
    st.header(f"Modifica dati BOX {box_num}")
    maschi = st.number_input("Maschi", min_value=0, value=st.session_state.dati_salvati[f"box{box_num}_maschi"], step=1)
    femmine = st.number_input("Femmine", min_value=0, value=st.session_state.dati_salvati[f"box{box_num}_femmine"], step=1)
    if st.button("Conferma modifica"):
        aggiorna_dati_box(box_num, maschi, femmine)

elif menu == "Inserisci polli morti":
    st.header("Inserisci Polli Morti")
    box_num = st.radio("Seleziona il BOX:", [1, 2])
    morti_m = st.number_input("Maschi morti", min_value=0, step=1, value=0)
    morti_f = st.number_input("Femmine morte", min_value=0, step=1, value=0)
    if st.button("Conferma morti"):
        inserisci_morti(box_num, morti_m, morti_f)

elif menu in ["Calcolo mangime misto", "Calcolo solo maschi", "Calcolo solo femmine"]:
    st.header("Calcolo durata mangime")
    tipo = {
        "Calcolo mangime misto": "misto",
        "Calcolo solo maschi": "maschi",
        "Calcolo solo femmine": "femmine"
    }[menu]

    maschi = femmine = 0
    if tipo in ["misto", "maschi"]:
        maschi = st.number_input("Numero di maschi:", min_value=0, step=1, value=0)
    if tipo in ["misto", "femmine"]:
        femmine = st.number_input("Numero di femmine:", min_value=0, step=1, value=0)
    mangime = st.number_input("Mangime disponibile (kg):", min_value=0.0, step=0.1, format="%.3f", value=0.0)
    giorno_iniziale = st.number_input("Giorno iniziale (es. 1 per primo giorno):", min_value=1, step=1, value=1)

    if st.button("Calcola"):
        try:
            risultato = calcola_durata_mangime(maschi, femmine, mangime, giorno_iniziale)
            st.success(risultato)
        except Exception as e:
            st.error(f"Errore: {e}")
