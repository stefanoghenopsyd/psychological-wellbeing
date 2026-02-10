import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
 
# --- 1. CONFIGURAZIONE E TESTI ---
# Fattori del modello di Ryff
FATTORI = [
    "Autoaccettazione", "Relazioni Positive", "Autonomia", 
    "Padronanza Ambientale", "Scopo nella Vita", "Crescita Personale"
]
 
# Definizione dei 12 item (2 per fattore)
VOCI_QUESTIONARIO = [
    {"testo": "In generale, mi sento fiducioso e positivo verso me stesso.", "fattore": "Autoaccettazione"},
    {"testo": "Mi piacciono la maggior parte degli aspetti della mia personalità.", "fattore": "Autoaccettazione"},
    {"testo": "Sento di avere relazioni calde e basate sulla fiducia con gli altri.", "fattore": "Relazioni Positive"},
    {"testo": "Mi considero una persona capace di dare affetto e sostegno.", "fattore": "Relazioni Positive"},
    {"testo": "Ho fiducia nelle mie opinioni, anche se diverse da quelle della massa.", "fattore": "Autonomia"},
    {"testo": "Prendo decisioni basate su ciò che ritengo giusto, non sulle pressioni altrui.", "fattore": "Autonomia"},
    {"testo": "Sento di essere in grado di influenzare l'ambiente che mi circonda.", "fattore": "Padronanza Ambientale"},
    {"testo": "Riesco a gestire bene le responsabilità della mia vita quotidiana.", "fattore": "Padronanza Ambientale"},
    {"testo": "Ho una chiara direzione e uno scopo nella mia vita.", "fattore": "Scopo nella Vita"},
    {"testo": "Le mie attività quotidiane mi sembrano dotate di senso.", "fattore": "Scopo nella Vita"},
    {"testo": "Sento di continuare a imparare e crescere come persona.", "fattore": "Crescita Personale"},
    {"testo": "Sono aperto a nuove esperienze che mettono alla prova le mie visioni.", "fattore": "Crescita Personale"}
]
 
# --- 2. FUNZIONI LOGICHE ---
def salva_su_google_sheet(riga):
    """Salva i dati su Google Sheets utilizzando le credenziali st.secrets[cite: 20]."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # Nome del file su Drive (deve essere creato prima)
        sheet = client.open("Database_Benessere_Ryff").sheet1
        sheet.append_row(riga)
        return True
    except Exception as e:
        st.error(f"Errore nel salvataggio dei dati: {e}") [cite: 23]
        return False
 
def crea_radar_chart(punteggi):
    """Genera grafico radar con colori ispirati al logo."""
    labels = list(punteggi.keys())
    values = list(punteggi.values())
    
    # Colori GENERA (esempio teal/verde professionale)
    color_line = "#1a5e5e"
    color_fill = "#a8dadc"
 
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
 
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color=color_fill, alpha=0.4)
    ax.plot(angles, values, color=color_line, linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 6)
    return fig
 
# --- 3. MAIN APP ---
def main():
    # Prima istruzione Streamlit obbligatoria [cite: 26]
    st.set_page_config(page_title="Autovalutazione Benessere Ryff", layout="centered")
 
    # Layout Logo e Titolo (Ridimensionamento automatico)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("GENERA Logo Colore.png", use_container_width=True) [cite: 42]
        st.markdown("<h2 style='text-align: center;'>Autovalutazione Risorse di Benessere</h2>", unsafe_allow_html=True)
 
    # Introduzione
    st.markdown("""
    ### Il Modello di Carol Ryff
    Il benessere psicologico non è solo assenza di malessere, ma la realizzazione del proprio potenziale (prospettiva eudaimonica). 
    Questo strumento analizza 6 fattori chiave: Autoaccettazione, Relazioni Positive, Autonomia, Padronanza Ambientale, Scopo nella Vita e Crescita Personale.
    
    **Obiettivo:** Riflettere sulle proprie risorse di benessere psicologico.
    """)
    st.write("proseguendo nella compilazione acconsento a che i dati raccolti saranno utilizzati in forma aggregata ed esclusivamente per finalità statistiche")
 
    # Inizializzazione stato per gestione ricarica [cite: 27-28]
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
        # Randomizzazione item solo all'inizio
        st.session_state.items_random = random.sample(VOCI_QUESTIONARIO, len(VOCI_QUESTIONARIO))
 
    if not st.session_state.submitted:
        # Form per invio unico dei dati [cite: 29-30]
        with st.form("questionario"):
            st.subheader("Informazioni Socio-Anagrafiche")
            identificativo = st.text_input("Nome o Nickname")
            genere = st.selectbox("Genere", ["maschile", "femminile", "non binario", "non risponde"])
            eta = st.selectbox("Età", ["fino a 20 anni", "21-30 anni", "31-40 anni", "41-50 anni", "51-60 anni", "61-70 anni", "più di 70 anni"])
            studio = st.selectbox("Titolo di studio", ["licenza media", "qualifica professionale", "diploma di maturità", "laurea triennale", "laurea magistrale (o ciclo unico)", "titolo post lauream"])
            job = st.selectbox("Job", ["imprenditore", "top manager", "middle manager", "impiegato", "operaio", "tirocinante", "libero professionista"])
 
            st.subheader("Questionario")
            risposte = {}
            for i, item in enumerate(st.session_state.items_random):
                risposte[item['testo']] = st.select_slider(
                    f"{item['testo']}",
                    options=[1, 2, 3, 4, 5, 6],
                    key=f"item_{i}"
                )
 
            submit = st.form_submit_button("Invia Valutazione")
 
            if submit:
                if not identificativo:
                    st.error("Per favore, inserisci un nome o nickname.")
                else:
                    # Calcolo punteggi per fattore
                    punteggi_finali = {f: [] for f in FATTORI}
                    for item in st.session_state.items_random:
                        punteggi_finali[item['fattore']].append(risposte[item['testo']])
                    
                    media_fattori = {f: np.mean(v) for f, v in punteggi_finali.items()}
                    
                    # Preparazione riga database: id, genere, età, studio, job, item_scores...
                    # Nota: l'ordine degli item nel DB segue l'ordine di VOCI_QUESTIONARIO originale
                    voti_ordinati = [risposte[item['testo']] for item in VOCI_QUESTIONARIO]
                    riga_db = [identificativo, genere, eta, studio, job] + voti_ordinati
                    
                    if salva_su_google_sheet(riga_db):
                        st.session_state.media_fattori = media_fattori
                        st.session_state.submitted = True
                        st.rerun()
    else:
        # FEEDBACK
        st.success("Analisi Completata!")
        medie = st.session_state.media_fattori
        
        # Grafico Radar
        st.pyplot(crea_radar_chart(medie))
 
        # Analisi descrittiva
        sorted_f = sorted(medie.items(), key=lambda x: x[1], reverse=True)
        st.write(f"### Risorse principali: **{sorted_f[0][0]}** e **{sorted_f[1][0]}**")
        st.write(f"### Aree da rafforzare: **{sorted_f[-1][0]}** e **{sorted_f[-2][0]}**")
 
        # Orientamento eudaimonico
        punteggio_totale = sum(medie.values())
        media_teorica = 3.5 * 6 # Media Likert (3.5) per 6 fattori
        if punteggio_totale > media_teorica:
            st.balloons()
            st.info("Il tuo profilo indica un forte orientamento eudaimonico al benessere.")
 
    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; font-size: 0.8em;'>Powered by GÉNERA</p>", unsafe_allow_html=True)
 
if __name__ == "__main__": [cite: 34-35]
    main()
