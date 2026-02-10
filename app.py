import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
from io import BytesIO

# --- CONFIGURAZIONE ---
FATTORI = ["Autoaccettazione", "Relazioni Positive", "Autonomia", "Padronanza Ambientale", "Scopo nella Vita", "Crescita Personale"]

ITEM_POOL = [
    {"testo": "In generale, mi sento fiducioso e positivo verso me stesso.", "dim": "Autoaccettazione"},
    {"testo": "Mi piacciono la maggior parte degli aspetti della mia personalità.", "dim": "Autoaccettazione"},
    {"testo": "Sento di avere relazioni calde e basate sulla fiducia con gli altri.", "dim": "Relazioni Positive"},
    {"testo": "Mi considero una persona capace di dare affetto e sostegno.", "dim": "Relazioni Positive"},
    {"testo": "Ho fiducia nelle mie opinioni, anche se diverse da quelle della massa.", "dim": "Autonomia"},
    {"testo": "Prendo decisioni basate su ciò che ritengo giusto, non sulle pressioni altrui.", "dim": "Autonomia"},
    {"testo": "Sento di essere in grado di influenzare l'ambiente che mi circonda.", "dim": "Padronanza Ambientale"},
    {"testo": "Riesco a gestire bene le responsabilità della mia vita quotidiana.", "dim": "Padronanza Ambientale"},
    {"testo": "Ho una chiara direzione e uno scopo nella mia vita.", "dim": "Scopo nella Vita"},
    {"testo": "Le mie attività quotidiane mi sembrano dotate di senso e valore.", "dim": "Scopo nella Vita"},
    {"testo": "Sento di continuare a imparare e crescere come persona.", "dim": "Crescita Personale"},
    {"testo": "Sono aperto a nuove esperienze che sfidano il mio modo di vedere me stesso.", "dim": "Crescita Personale"}
]

# Colonne per il file CSV e Database
COLONNE_ANAGRAFICA = ["identificativo", "genere", "età", "titolo di studio", "job"]
COLONNE_ITEM = [it['testo'] for it in ITEM_POOL]

def salva_online(riga):
    """Tenta il salvataggio su Google Sheets [cite: 20-23]."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("Database_Benessere_Ryff").sheet1
        sheet.append_row(riga)
        return True
    except:
        return False

def genera_radar(punteggi):
    labels = list(punteggi.keys())
    values = list(punteggi.values())
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color="#457b9d", alpha=0.4)
    ax.plot(angles, values, color="#1d3557", linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 6)
    return fig

def main():
    st.set_page_config(page_title="GENERA - Benessere Ryff", layout="centered")

    # Header
    st.image("GENERA Logo Colore.png", use_container_width=True)
    st.markdown("<h2 style='text-align: center;'>Autovalutazione Risorse di Benessere</h2>", unsafe_allow_html=True)

    # Introduzione
    st.write("Il modello di Carol Ryff analizza il benessere eudaimonico attraverso 6 fattori chiave.")
    st.info("proseguendo nella compilazione acconsento a che i dati raccolti saranno utilizzati in forma aggregata ed esclusivamente per finalità statistiche")

    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
        st.session_state.ordine = random.sample(ITEM_POOL, len(ITEM_POOL))

    if not st.session_state.submitted:
        with st.form("questionario"):
            st.subheader("Dati Socio-Anagrafici")
            id_utente = st.text_input("Nome o nickname")
            gen = st.selectbox("Genere", ["maschile", "femminile", "non binario", "non risponde"])
            eta = st.selectbox("Età", ["fino a 20 anni", "21-30 anni", "31-40 anni", "41-50 anni", "51-60 anni", "61-70 anni", "più di 70 anni"])
            edu = st.selectbox("Titolo di studio", ["licenza media", "qualifica professionale", "diploma di maturità", "laurea triennale", "laurea magistrale (o ciclo unico)", "titolo post lauream"])
            job = st.selectbox("Job", ["imprenditore", "top manager", "middle manager", "impiegato", "operaio", "tirocinante", "libero professionista"])

            st.subheader("Questionario")
            risposte = {}
            for i, item in enumerate(st.session_state.ordine):
                risposte[item['testo']] = st.radio(item['testo'], [1,2,3,4,5,6], horizontal=True, key=f"q_{i}")

            if st.form_submit_button("Visualizza Risultati"):
                if not id_utente:
                    st.error("Inserisci un identificativo.")
                else:
                    # Calcolo Medie
                    medie = {f: np.mean([risposte[it['testo']] for it in ITEM_POOL if it['dim'] == f]) for f in FATTORI}
                    
                    # Preparazione riga dati
                    riga_completa = [id_utente, gen, eta, edu, job] + [risposte[it['testo']] for it in ITEM_POOL]
                    
                    # Tentativo salvataggio
                    successo_online = salva_online(riga_completa)
                    
                    # Salvataggio in sessione
                    st.session_state.medie = medie
                    st.session_state.riga_completa = riga_completa
                    st.session_state.successo_online = successo_online
                    st.session_state.submitted = True
                    st.rerun()
    else:
        # FEEDBACK
        if not st.session_state.successo_online:
            st.warning("⚠️ Non è stato possibile salvare i dati nel database centralizzato. Puoi scaricare i tuoi risultati localmente usando il pulsante in fondo alla pagina.")
        else:
            st.success("✅ Dati salvati con successo nel database GENERA.")

        st.pyplot(genera_radar(st.session_state.medie))
        
        res = sorted(st.session_state.medie.items(), key=lambda x: x[1], reverse=True)
        st.write(f"### Risorse principali: **{res[0][0]}** e **{res[1][0]}**")
        st.write(f"### Da rafforzare: **{res[-1][0]}** e **{res[-2][0]}**")

        # Download Sezione
        df_download = pd.DataFrame([st.session_state.riga_completa], columns=COLONNE_ANAGRAFICA + COLONNE_ITEM)
        csv = df_download.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Scarica i tuoi risultati (CSV)",
            data=csv,
            file_name=f"risultati_ryff_{st.session_state.riga_completa[0]}.csv",
            mime="text/csv",
        )

        if st.button("Ricomincia"):
            st.session_state.submitted = False
            st.rerun()

    st.markdown("---")
    st.markdown("<p style='text-align: center;'>Powered by GÉNERA</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
