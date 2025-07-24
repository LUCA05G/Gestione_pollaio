import streamlit as st
from datetime import date, timedelta
import locale
import json
import os




st.set_page_config(title="Gestione Polli e Mangime", page_icon=Image.open("icona.ico"), layout="centered")
locale.setlocale(locale.LC_TIME, 'it_IT')




def login():
    password = st.text_input("Inserisci la password per accedere:", type="password")
    if password == "PolLarino":
        return True
    else:
        if password:
            st.error("Password errata!")
        return False

if login():
    st.write("Benvenuto nella app!")
    # resto dell'app qui
else:
    st.stop()


def carica_dati():
    if "dati_salvati" not in st.session_state:
        if os.path.exists(FILE_DATI):
            with open(FILE_DATI, "r") as f:
                st.session_state.dati_salvati = json.load(f)
        else:
            st.session_state.dati_salvati = {
                "box1_maschi": 0,
                "box1_femmine": 0,
                "box2_maschi": 0,
                "box2_femmine": 0
            }

def salva_dati():
    with open(FILE_DATI, "w") as f:
        json.dump(st.session_state.dati_salvati, f)


def calcola_mangime(maschi, femmine, mangime, giorno_iniziale):
    with open("Performance Femmine.txt", "r", encoding="utf-8") as f:
        valoriF = [float(riga.split()[1]) for riga in f]
    with open("Performance Maschi.txt", "r", encoding="utf-8") as f:
        valoriM = [float(riga.split()[1]) for riga in f]

    if giorno_iniziale < 1:
        return "✅ Il giorno iniziale deve essere almeno 1."

    indice = giorno_iniziale - 1
    if indice >= len(valoriM) or indice >= len(valoriF):
        return  "Giorno iniziale oltre i dati disponibili."

    giorni = 0
    while mangime > 0 and indice < len(valoriM):
        mangime -= maschi * valoriM[indice] + femmine * valoriF[indice]
        if mangime >= 0:
            giorni += 1
            indice += 1
        else:
            break

    futura = date.today() + timedelta(days=giorni)
    if mangime < 0:
        return f"❌ Mangime finisce il {futura.strftime('%A %d %B %Y')} (giorno {giorno_iniziale + giorni}). Mancano {abs(mangime):.3f} kg."
    elif mangime == 0:
        return f"✅ Mangime finisce esattamente il {futura.strftime('%A %d %B %Y')} (giorno {giorno_iniziale + giorni})."
    else:
        return f"✅ Mangime sufficiente fino al {futura.strftime('%A %d %B %Y')} (giorno {giorno_iniziale + giorni}). Rimangono {mangime:.3f} kg."




# --- Funzione per aggiornare dati BOX ---
def aggiorna_box(box_num, maschi, femmine):
    st.session_state.dati_salvati[f"box{box_num}_maschi"] = maschi
    st.session_state.dati_salvati[f"box{box_num}_femmine"] = femmine
    salva_dati()

# --- Funzione per inserire morti ---
def inserisci_morti(box_num, morti_m, morti_f):
    dati = st.session_state.dati_salvati
    dati[f"box{box_num}_maschi"] = max(0, dati[f"box{box_num}_maschi"] - morti_m)
    dati[f"box{box_num}_femmine"] = max(0, dati[f"box{box_num}_femmine"] - morti_f)
    salva_dati()

# --- App Streamlit ---
st.title("🐔 Gestione Polli e Mangime 🐔")




carica_dati()

# Mostra stato attuale
st.subheader("Stato attuale dei BOX")
st.write(f"BOX 1 - Maschi: {st.session_state.dati_salvati['box1_maschi']}, Femmine: {st.session_state.dati_salvati['box1_femmine']}")
st.write(f"BOX 2 - Maschi: {st.session_state.dati_salvati['box2_maschi']}, Femmine: {st.session_state.dati_salvati['box2_femmine']}")

# Sidebar per navigazione funzionalità
st.sidebar.title("Seleziona funzione")
funzione = st.sidebar.radio("", ["Modifica BOX", "Inserisci Polli Morti", "Calcolo Mangime"])

if funzione == "Modifica BOX":
    st.header("Modifica dati BOX")
    box_sel = st.selectbox("Seleziona BOX:", [1, 2])
    dati = st.session_state.dati_salvati
    maschi_in = st.number_input(f"Maschi BOX {box_sel}:", min_value=0, value=dati[f"box{box_sel}_maschi"])
    femmine_in = st.number_input(f"Femmine BOX {box_sel}:", min_value=0, value=dati[f"box{box_sel}_femmine"])

    if st.button("Aggiorna BOX"):
        aggiorna_box(box_sel, maschi_in, femmine_in)
        st.success(f"Dati BOX {box_sel} aggiornati!")

elif funzione == "Inserisci Polli Morti":
    st.header("Inserisci Polli Morti")
    box_sel = st.selectbox("Seleziona BOX:", [1, 2])
    morti_m = st.number_input("Maschi morti:", min_value=0, value=0)
    morti_f = st.number_input("Femmine morte:", min_value=0, value=0)

    if st.button("Aggiorna dati morti"):
        inserisci_morti(box_sel, morti_m, morti_f)
        st.success(f"Dati aggiornati per BOX {box_sel} dopo inserimento morti.")

elif funzione == "Calcolo Mangime":
    st.header("Calcolo durata mangime")
    tipo_calcolo = st.radio("Seleziona tipo calcolo:", ["Misto", "Solo maschi", "Solo femmine"])

    maschi_input = femmine_input = 0
    if tipo_calcolo in ["Misto", "Solo maschi"]:
        maschi_input = st.number_input("Numero maschi:", min_value=0, value=0)
    if tipo_calcolo in ["Misto", "Solo femmine"]:
        femmine_input = st.number_input("Numero femmine:", min_value=0, value=0)

    mangime_disponibile = st.number_input("Mangime disponibile (kg):", min_value=0.0, format="%.2f")

    if st.button("Calcola durata mangime"):
        risultato = calcola_giorni(maschi_input, femmine_input, mangime_disponibile)
        st.success(risultato)
