import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
from io import BytesIO

# --- 1. CONFIGURAZIONE E DESCRIZIONI ---
# Definiamo le descrizioni qui per riutilizzarle sia nell'intro che nel feedback
DESCRIZIONI_RYFF = {
    "Autoaccettazione": "Possedere un atteggiamento positivo verso se stessi, accettando i propri limiti e valorizzando le proprie qualità e le esperienze passate.",
    "Relazioni Positive": "Capacità di instaurare rapporti interpersonali profondi, caratterizzati da calore, fiducia, empatia e mutuo sostegno.",
    "Autonomia": "Capacità di autodeterminazione e indipendenza, riuscendo a resistere alle pressioni sociali e a valutare se stessi secondo i propri standard.",
    "Padronanza Ambientale": "Capacità di gestire l'ambiente circostante, sfruttando le opportunità e creando contesti adatti ai propri bisogni e valori.",
    "Scopo nella Vita": "Senso di direzionalità e convinzione che la propria vita sia dotata di significato, grazie a obiettivi chiari e progetti futuri.",
    "Crescita Personale": "Sentimento di continuo sviluppo e realizzazione del proprio potenziale, restando aperti a nuove esperienze e cambiamenti."
}

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
    {"testo": "Sono aperto a nuove esperienze che mettono alla prova le mie visioni.", "dim": "Crescita Personale"}
]

# --- 2. FUNZIONI DI SUPPORTO ---
def salva_online(riga):
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
    ax.plot(angles, values, color="#1d3557", linewidth=2, marker='o')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 6)
    return fig

# --- 3. MAIN APP ---
def main():
    st.set_page_config(page_title="GENERA - Benessere Ryff", layout="centered")

    # Logo e Titolo
    st.image("GENERA Logo Colore.png", use_container_width=True)
    st.markdown("<h2 style='text-align: center;'>Autovalutazione Risorse di Benessere</h2>", unsafe_allow_html=True)

    # Introduzione con definizioni
    st.markdown("### Il Modello di Carol Ryff")
    st.write("Il benessere psicologico secondo Carol Ryff si fonda su sei pilastri fondamentali. Ecco le definizioni delle dimensioni che andremo ad analizzare:")
    
    for dimensione, descrizione in DESCRIZIONI_RYFF.items():
        st.markdown(f"- **{dimensione}**: {descrizione}")
    
    st.write("\n**Obiettivo:** Questa autovalutazione serve a riflettere sulle tue risorse di benessere psicologico.")
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
            st.info("Valuta le seguenti affermazioni su una scala da 1 (min) a 6 (max)")
            risposte = {}
            for i, item in enumerate(st.session_state.ordine):
                risposte[item['testo']] = st.radio(item['testo'], [1,2,3,4,5,6], horizontal=True, key=f"q_{i}")

            if st.form_submit_button("Visualizza Risultati"):
                if not id_utente:
                    st.error("Inserisci un identificativo.")
                else:
                    # Calcolo Medie
                    medie = {f: np.mean([risposte[it['testo']] for it in ITEM_POOL if it['dim'] == f]) for f in DESCRIZIONI_RYFF.keys()}
                    riga_completa = [id_utente, gen, eta, edu, job] + [risposte[it['testo']] for it in ITEM_POOL]
                    
                    st.session_state.successo_online = salva_online(riga_completa)
                    st.session_state.medie = medie
                    st.session_state.riga_completa = riga_completa
                    st.session_state.submitted = True
                    st.rerun()
    else:
        # FEEDBACK
        if not st.session_state.successo_online:
            st.warning("⚠️ Salvataggio online non riuscito. Scarica i risultati localmente.")
        else:
            st.success("✅ Dati archiviati con successo.")

        st.pyplot(genera_radar(st.session_state.medie))
        
        # Analisi Descrittiva con spiegazioni
        res = sorted(st.session_state.medie.items(), key=lambda x: x[1], reverse=True)
        top_2 = res[:2]
        bottom_2 = res[-2:]

        st.markdown("### Le tue risorse principali")
        for dim, score in top_2:
            st.markdown(f"**{dim}** (Punteggio: {score:.2f})")
            st.write(f"_{DESCRIZIONI_RYFF[dim]}_")

        st.markdown("### Aree da rafforzare")
        for dim, score in bottom_2:
            st.markdown(f"**{dim}** (Punteggio: {score:.2f})")
            st.write(f"_{DESCRIZIONI_RYFF[dim]}_")

        # Pulsante Download
        df_download = pd.DataFrame([st.session_state.riga_completa], columns=["identificativo", "genere", "età", "studio", "job"] + [it['testo'] for it in ITEM_POOL])
        csv = df_download.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Scarica Risultati (CSV)", csv, f"risultati_{st.session_state.riga_completa[0]}.csv", "text/csv")

        if st.button("Ricomincia"):
            st.session_state.submitted = False
            st.rerun()

    st.markdown("---")
    st.markdown("<p style='text-align: center;'>Powered by GÉNERA</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
