import streamlit as st
import json
import os
from datetime import date, timedelta
import locale
import gspread
from oauth2client.service_account import ServiceAccountCredentials


GOOGLE_SHEET_KEY = "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC3GZZxRv2aiE2w\\n-----END PRIVATE KEY-----\\n"
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
    return gspread.authorize(credentials)

def carica_dati_da_google_sheet():
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(GOOGLE_SHEET_KEY).sheet1
        records = sheet.get_all_records()

        return {
            "box1_maschi": int(records[0]["maschi"]),
            "box1_femmine": int(records[0]["femmine"]),
            "box2_maschi": int(records[1]["maschi"]),
            "box2_femmine": int(records[1]["femmine"])
        }
    except Exception as e:
        st.error(f"Errore caricamento Google Sheet: {e}")
        return carica_dati()

def salva_dati_su_google_sheet(dati):
    try:
        client = get_gspread_client()
        sheet = client.open(GOOGLE_SHEET).sheet1
        sheet.update('B2', [[dati["box1_maschi"]]])
        sheet.update('C2', [[dati["box1_femmine"]]])
        sheet.update('B3', [[dati["box2_maschi"]]])
        sheet.update('C3', [[dati["box2_femmine"]]])
    except Exception as e:
        st.error(f"Errore salvataggio su Google Sheet: {e}")



PASSWORD_CORRETTA = "pollo25"

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.title("🔐 Inserisci la password per accedere")
    password = st.text_input("Password", type="password")
    if st.button("Entra"):
        if password == PASSWORD_CORRETTA:
            st.session_state.autenticato = True
            
        else:
            st.error("Password errata.")
    st.stop()

FILE_DATI = "dati_polli.json"

# Carica dati da file o inizializza
def carica_dati():
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r") as f:
            return json.load(f)
    else:
        return {
            "box1_maschi": 0,
            "box1_femmine": 0,
            "box2_maschi": 0,
            "box2_femmine": 0,
        }

# Salva dati su file
def salva_dati(dati):
    with open(FILE_DATI, "w") as f:
        json.dump(dati, f)

# Calcolo durata mangime
def calcola_durata_mangime(maschi, femmine, mangime, giorno_iniziale):
    if giorno_iniziale < 1:
        raise ValueError("Il giorno iniziale deve essere almeno 1.")

    # Carico dati performance
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
    # Setta locale italiano, su Windows potrebbe non funzionare, togli se problemi
    try:
        locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
    except:
        pass

    if mangime_rimasto < 0:
        return (f"Il mangime durerà fino a: {futura.strftime('%A %d %B %Y')}\n"
                f"(giorno {indice})\nIl {futura.strftime('%A %d %B %Y')} ci saranno "
                f"{mangime_rimasto + consumo_totale:.3f} kg di mangime, non sufficienti per il giorno successivo")
    elif mangime_rimasto == 0:
        return (f"Il mangime durerà fino a: {futura.strftime('%A %d %B %Y')}\n"
                f"Da {futura.strftime('%A %d %B %Y')} non ci sarà più mangime a disposizione")
    else:
        return (f"Il mangime è sufficiente fino al giorno {giorni} ({futura.strftime('%A %d %B %Y')}).\n"
                f"Resteranno {mangime_rimasto:.3f} kg di mangime.")

# Inizializza session_state dati_salvati
if "dati_salvati" not in st.session_state:
    st.session_state.dati_salvati = carica_dati_da_google_sheet()

st.title("Gestione Polli e Mangime")

# Sidebar con dati attuali
st.sidebar.header("Dati attuali")
dati = st.session_state.dati_salvati
st.sidebar.write(f"BOX 1\nMaschi: {dati['box1_maschi']}\nFemmine: {dati['box1_femmine']}")
st.sidebar.write(f"BOX 2\nMaschi: {dati['box2_maschi']}\nFemmine: {dati['box2_femmine']}")

# Menu principale
opzioni_menu = [
    "Modifica BOX 1",
    "Modifica BOX 2",
    "Inserisci polli morti",
    "Calcolo mangime misto",
    "Calcolo solo maschi",
    "Calcolo solo femmine"
]
scelta = st.sidebar.radio("Menu", opzioni_menu)

# Funzioni di aggiornamento dati
def aggiorna_box(box_num, maschi, femmine):
    st.session_state.dati_salvati[f"box{box_num}_maschi"] = maschi
    st.session_state.dati_salvati[f"box{box_num}_femmine"] = femmine
    salva_dati(st.session_state.dati_salvati)
    salva_dati_su_google_sheet(st.session_state.dati_salvati)
    st.success(f"Dati BOX {box_num} aggiornati.")

def inserisci_morti(box_num, morti_m, morti_f):
    dati = st.session_state.dati_salvati
    dati[f"box{box_num}_maschi"] = max(0, dati[f"box{box_num}_maschi"] - morti_m)
    dati[f"box{box_num}_femmine"] = max(0, dati[f"box{box_num}_femmine"] - morti_f)
    salva_dati(dati)
    salva_dati_su_google_sheet(dati)
    st.session_state.dati_salvati = dati
    st.success("Dati aggiornati dopo inserimento morti.")

# Logica menu
if scelta.startswith("Modifica BOX"):
    box_num = int(scelta[-1])
    st.header(f"Modifica dati BOX {box_num}")
    maschi = st.number_input("Maschi", min_value=0, step=1, value=dati[f"box{box_num}_maschi"])
    femmine = st.number_input("Femmine", min_value=0, step=1, value=dati[f"box{box_num}_femmine"])
    if st.button("Conferma modifica"):
        aggiorna_box(box_num, maschi, femmine)

elif scelta == "Inserisci polli morti":
    st.header("Inserisci Polli Morti")
    box_num = st.radio("Seleziona il BOX:", [1, 2])
    morti_m = st.number_input("Maschi morti", min_value=0, step=1, value=0)
    morti_f = st.number_input("Femmine morte", min_value=0, step=1, value=0)
    if st.button("Conferma morti"):
        inserisci_morti(box_num, morti_m, morti_f)

elif scelta in ["Calcolo mangime misto", "Calcolo solo maschi", "Calcolo solo femmine"]:
    st.header("Calcolo durata mangime")
    tipo = {
        "Calcolo mangime misto": "misto",
        "Calcolo solo maschi": "maschi",
        "Calcolo solo femmine": "femmine"
    }[scelta]

    maschi = 0
    femmine = 0
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
