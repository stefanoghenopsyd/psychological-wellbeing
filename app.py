import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random

# --- CONFIGURAZIONE E MODELLO ---
DIMENSIONI = [
    "Autoaccettazione", "Relazioni Positive", "Autonomia", 
    "Padronanza Ambientale", "Scopo nella Vita", "Crescita Personale"
]

# Database degli item (2 per dimensione)
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

def salva_su_google_drive(riga):
    """Gestisce la connessione sicura e il salvataggio dati [cite: 20-23]."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # Assicurati che il nome del file su Drive sia identico a questo:
        sheet = client.open("Database_Benessere_Ryff").sheet1
        sheet.append_row(riga)
        return True
    except Exception as e:
        st.error(f"Errore di connessione al database: {e}")
        return False

def genera_radar(punteggi):
    """Crea il grafico con colori ispirati al logo GENERA."""
    labels = list(punteggi.keys())
    values = list(punteggi.values())
    
    # Colori GENERA: Verde scuro e Teal
    color_line = "#004b49" 
    color_fill = "#7fb3b2"

    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color=color_fill, alpha=0.4)
    ax.plot(angles, values, color=color_line, linewidth=2, marker='o')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 6)
    return fig

def main():
    st.set_page_config(page_title="Benessere Ryff - GENERA", layout="centered") [cite: 26]

    # Logo centrato e adattivo
    st.image("GENERA Logo Colore.png", use_container_width=True) [cite: 42]
    st.markdown("<h2 style='text-align: center;'>Autovalutazione del Benessere Psicologico</h2>", unsafe_allow_html=True)

    # Introduzione
    st.markdown("""
    Il modello dello **Psychological Wellbeing di Carol Ryff** individua 6 fattori fondamentali che concorrono al benessere 
    secondo una prospettiva **eudaimonica** (realizzazione del potenziale umano).
    
    L'obiettivo di questa autovalutazione è promuovere una riflessione sulle proprie risorse interiori.
    """)
    st.caption("Proseguendo nella compilazione acconsento a che i dati raccolti saranno utilizzati in forma aggregata ed esclusivamente per finalità statistiche.")

    # Gestione dello stato e randomizzazione [cite: 27-28]
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
        st.session_state.item_ordine = random.sample(ITEM_POOL, len(ITEM_POOL))

    if not st.session_state.submitted:
        with st.form("main_form"): [cite: 29]
            st.subheader("Dati Socio-Anagrafici")
            nome = st.text_input("Nome o Nickname")
            gen = st.selectbox("Genere", ["maschile", "femminile", "non binario", "non risponde"])
            eta = st.selectbox("Età", ["fino a 20 anni", "21-30 anni", "31-40 anni", "41-50 anni", "51-60 anni", "61-70 anni", "più di 70 anni"])
            edu = st.selectbox("Titolo di studio", ["licenza media", "qualifica professionale", "diploma di maturità", "laurea triennale", "laurea magistrale (o ciclo unico)", "titolo post lauream"])
            job = st.selectbox("Job", ["imprenditore", "top manager", "middle manager", "impiegato", "operaio", "tirocinante", "libero professionista"])

            st.subheader("Questionario")
            st.info("Valuta quanto sei d'accordo con le seguenti affermazioni da 1 (min) a 6 (max)")
            
            risposte = {}
            for i, item in enumerate(st.session_state.item_ordine):
                risposte[item['testo']] = st.radio(item['testo'], [1,2,3,4,5,6], horizontal=True, key=f"q_{i}")

            if st.form_submit_button("Analizza le mie risorse"):
                if not nome:
                    st.warning("Per favore, inserisci un nome o nickname.")
                else:
                    # Calcolo medie per dimensione
                    punteggi_dim = {d: [] for d in DIMENSIONI}
                    for item in ITEM_POOL:
                        punteggi_dim[item['dim']].append(risposte[item['testo']])
                    
                    medie = {d: np.mean(v) for d, v in punteggi_dim.items()}
                    
                    # Preparazione riga DB (ordine richiesto)
                    item_values = [risposte[item['testo']] for item in ITEM_POOL]
                    riga_db = [nome, gen, eta, edu, job] + item_values
                    
                    if salva_su_google_drive(riga_db):
                        st.session_state.medie = medie
                        st.session_state.submitted = True
                        st.rerun()
    else:
        # FEEDBACK VISIVO
        st.pyplot(genera_radar(st.session_state.medie))
        
        # FEEDBACK DESCRITTIVO
        res = sorted(st.session_state.medie.items(), key=lambda x: x[1], reverse=True)
        st.markdown(f"### Le tue risorse principali: **{res[0][0]}** e **{res[1][0]}**")
        st.markdown(f"### Risorse da rafforzare: **{res[-1][0]}** e **{res[-2][0]}**")
        
        # Orientamento eudaimonico
        punteggio_medio_totale = sum(st.session_state.medie.values()) / 6
        if punteggio_medio_totale > 3.5:
            st.success("🌟 Il tuo profilo mostra un solido orientamento eudaimonico al benessere!")
        
        if st.button("Compila di nuovo"):
            st.session_state.submitted = False
            st.rerun()

    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray;'>Powered by GÉNERA</p>", unsafe_allow_html=True)

if __name__ == "__main__": [cite: 34-36]
    main()
