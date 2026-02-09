import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Autovalutazione Benessere Ryff", layout="centered")

# --- FUNZIONI UTILI ---

def mostra_logo():
    """Tenta di caricare il logo, gestisce il caso in cui il file manchi."""
    nome_file = "GENERA Logo Colore.png"
    if os.path.exists(nome_file):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(nome_file, use_container_width=True)
    else:
        st.warning(f"Nota: Immagine '{nome_file}' non trovata nella directory.")

def calcola_punteggi(risposte, mappatura):
    """Calcola i punteggi medi per ogni dimensione."""
    punteggi = {}
    for dimensione, items in mappatura.items():
        valori = [risposte[item] for item in items]
        punteggi[dimensione] = sum(valori) / len(valori)
    return punteggi

def crea_grafico_radar(punteggi):
    """Genera il grafico radar con Plotly."""
    categorie = list(punteggi.keys())
    valori = list(punteggi.values())
    
    # Chiudere il cerchio del radar
    valori += values[:1]
    categorie += categories[:1]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=valori,
        theta=categorie,
        fill='toself',
        name='Il tuo profilo',
        line_color='#4CAF50'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 6]  # Scala da 0 a 6
            )),
        showlegend=False,
        title="Mappa delle Risorse di Benessere"
    )
    return fig

# --- DATI DEL MODELLO RYFF (ITEMS E DIMENSIONI) ---
# Nota: Questi sono items adattati a scopo dimostrativo basati sul modello Ryff.
# In un contesto clinico reale, vanno usati gli item validati e protetti da copyright.

domande = {
    "AUT1": "Tendo a essere influenzato/a da persone con opinioni forti.", # Inverso
    "AUT2": "Ho fiducia nelle mie opinioni, anche se sono contrarie al consenso generale.",
    "PAD1": "In generale, sento di essere responsabile della situazione in cui vivo.",
    "PAD2": "Le richieste della vita quotidiana spesso mi abbattono.", # Inverso
    "CRE1": "Penso che sia importante avere nuove esperienze che sfidino il modo in cui penso a me stesso/a e al mondo.",
    "CRE2": "Non mi interessa molto provare a migliorare o cambiare me stesso/a.", # Inverso
    "REL1": "So che posso fidarmi dei miei amici, e loro sanno che possono fidarsi di me.",
    "REL2": "Spesso mi sento solo/a perché ho pochi amici intimi con cui condividere le mie preoccupazioni.", # Inverso
    "SCO1": "Ho un senso di direzione e uno scopo nella vita.",
    "SCO2": "Non ho una chiara idea di cosa sto cercando di realizzare nella vita.", # Inverso
    "ACC1": "Quando guardo alla storia della mia vita, sono soddisfatto/a di come sono andate le cose.",
    "ACC2": "In molti modi, mi sento deluso/a dai miei risultati nella vita." # Inverso
}

# Mappatura Item -> Dimensione
mappa_dimensioni = {
    "Autonomia": ["AUT1", "AUT2"],
    "Padronanza Ambientale": ["PAD1", "PAD2"],
    "Crescita Personale": ["CRE1", "CRE2"],
    "Relazioni Positive": ["REL1", "REL2"],
    "Scopo di Vita": ["SCO1", "SCO2"],
    "Autoaccettazione": ["ACC1", "ACC2"]
}

# Items che necessitano di inversione del punteggio (se 6 diventa 1, ecc.)
items_inversi = ["AUT1", "PAD2", "CRE2", "REL2", "SCO2", "ACC2"]

# --- INTERFACCIA UTENTE ---

# 1. Header e Logo
mostra_logo()
st.title("Autovalutazione del Benessere Psicologico")
st.markdown("---")

# 2. Introduzione
st.markdown("""
### Il Modello di Carol Ryff
Benvenuto/a. Questa applicazione si basa sul modello del **Psychological Well-being (PWB)** elaborato dalla psicologa Carol Ryff. 
A differenza della visione edonica (benessere come semplice piacere), questo modello adotta una **prospettiva eudaimonica**: 
il benessere è inteso come la realizzazione del proprio potenziale umano.

L'obiettivo di questa autovalutazione non è fornire una diagnosi, ma **offrirti uno spunto di riflessione** sulle tue attuali risorse 
psicologiche, aiutandoti a capire su quali punti di forza puoi contare e quali aree potresti voler nutrire.
""")

st.info("Compila i dati anagrafici e rispondi alle domande per visualizzare il tuo profilo.")

# 3. Informazioni Socio-Anagrafiche
with st.expander("📝 I tuoi dati (Clicca per espandere)", expanded=True):
    col_a, col_b = st.columns(2)
    
    with col_a:
        nome = st.text_input("Nome o Nickname")
        eta = st.selectbox("Età", [
            "Fino a 20 anni", "21-30 anni", "31-40 anni", 
            "41-50 anni", "51-60 anni", "61-70 anni", "Più di 70 anni"
        ])
        titolo_studio = st.selectbox("Titolo di studio", [
            "Licenza media", "Qualifica professionale", "Diploma di maturità", 
            "Laurea triennale", "Laurea magistrale (o ciclo unico)", "Titolo post lauream"
        ])

    with col_b:
        genere = st.radio("Genere", ["Maschile", "Femminile", "Non binario", "Non risponde"])
        ruolo = st.selectbox("Ruolo professionale", [
            "Imprenditore", "Top manager", "Middle manager", "Impiegato", 
            "Operaio", "Tirocinante", "Libero professionista"
        ])

# 4. Questionario
st.markdown("### Il Questionario")
st.write("Indica quanto sei d'accordo con le seguenti affermazioni su una scala da 1 (Per nulla d'accordo) a 6 (Completamente d'accordo).")

form = st.form(key='questionario_ryff')
risposte_raw = {}

# Opzioni Likert
opzioni_likert = {
    1: "1 - Fortemente in disaccordo",
    2: "2 - In disaccordo",
    3: "3 - Leggermente in disaccordo",
    4: "4 - Leggermente d'accordo",
    5: "5 - D'accordo",
    6: "6 - Fortemente d'accordo"
}

for codice, testo in domande.items():
    st.write(f"**{testo}**")
    # Usiamo uno slider o radio button. Radio è più preciso per Likert discreta.
    risposte_raw[codice] = st.radio(
        f"Seleziona per: {testo}", 
        options=[1, 2, 3, 4, 5, 6], 
        format_func=lambda x: opzioni_likert[x],
        horizontal=True,
        key=codice,
        label_visibility="collapsed"
    )
    st.markdown("---")

submit_button = form.form_submit_button(label='Calcola il mio Profilo di Benessere')

# --- ELABORAZIONE E FEEDBACK ---

if submit_button:
    if not nome:
        st.error("Per favore, inserisci un nome o nickname per procedere.")
    else:
        # 1. Normalizzazione Punteggi (Gestione Inversi)
        risposte_elaborate = {}
        for k, v in risposte_raw.items():
            if k in items_inversi:
                risposte_elaborate[k] = 7 - v  # Inversione su scala 6 (7 - x)
            else:
                risposte_elaborate[k] = v

        # 2. Calcolo Medie per Dimensione
        punteggi_dim = calcola_punteggi(risposte_elaborate, mappa_dimensioni)
        
        # 3. Preparazione Dati Grafici
        categories = list(punteggi_dim.keys())
        values = list(punteggi_dim.values())

        # 4. Visualizzazione Risultati
        st.markdown(f"## Risultati per {nome}")
        
        # Grafico Radar
        col_graph, col_desc = st.columns([1, 1])
        
        with col_graph:
            fig = crea_grafico_radar(punteggi_dim)
            st.plotly_chart(fig, use_container_width=True)

        # Logica per il Feedback Descrittivo
        punteggi_ordinati = sorted(punteggi_dim.items(), key=lambda x: x[1], reverse=True)
        top_2 = punteggi_ordinati[:2]
        bottom_2 = punteggi_ordinati[-2:]
        
        media_totale = sum(values) / len(values)
        media_teorica = 3.5 # Scala 1-6

        with col_desc:
            st.markdown("### Feedback Descrittivo")
            
            # Punti di Forza
            st.success(f"🌟 **Le tue risorse principali:**\n\n"
                       f"Le aree in cui mostri maggiore solidità sono **{top_2[0][0]}** e **{top_2[1][0]}**. "
                       f"Questi sono i pilastri su cui puoi contare nei momenti di difficoltà.")
            
            # Aree di Miglioramento
            st.warning(f"🌱 **Aree da rafforzare:**\n\n"
                       f"I punteggi suggeriscono che potresti trarre beneficio lavorando su **{bottom_2[1][0]}** e **{bottom_2[0][0]}**. "
                       f"Non vederli come deficit, ma come opportunità di crescita personale.")

            # Orientamento Eudaimonico
            st.markdown("---")
            if media_totale > media_teorica:
                st.markdown("""
                🎯 **Orientamento Eudaimonico Rilevato**
                
                Il tuo punteggio complessivo supera la media teorica. Questo indica un **buon orientamento al benessere eudaimonico**: 
                sembri impegnato/a non solo nella ricerca della soddisfazione momentanea, ma nella costruzione di senso e nella 
                realizzazione del tuo potenziale.
                """)
            else:
                st.markdown("""
                🎯 **Riflessione sull'Orientamento**
                
                Il tuo punteggio complessivo è vicino o sotto la media teorica. Questo potrebbe indicare un momento di stanchezza o 
                una fase di transizione. È un ottimo momento per fermarsi e chiedersi cosa dà davvero significato alla tua quotidianità.
                """)
