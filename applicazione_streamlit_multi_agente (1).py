import streamlit as st
from openai import OpenAI
import markdown
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(
    page_title="Team Agenti IA per la Didattica",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Utilizziamo st.session_state per conservare i risultati degli agenti durante i re-render della pagina
if "ricerca_eseguita" not in st.session_state:
    st.session_state.ricerca_eseguita = False
if "punti_chiave" not in st.session_state:
    st.session_state.punti_chiave = ""
if "post_docenti" not in st.session_state:
    st.session_state.post_docenti = ""

st.sidebar.title("🔑 Configurazione Credenziali")
st.sidebar.markdown(
    "Inserisci le tue API key e credenziali email per abilitare gli Agenti IA e l'invio dei report."
)

# Campi di input nella sidebar con nascondimento password per sicurezza
openrouter_key = st.sidebar.text_input(
    "OpenRouter API Key",
    type="password",
    help="Ottieni una chiave API su openrouter.ai"
)

st.sidebar.markdown("---")
st.sidebar.subheader("📧 Configurazione SMTP Gmail")

sender_email = st.sidebar.text_input(
    "Email Gmail Mittente",
    placeholder="tuamail@gmail.com"
)

gmail_app_password = st.sidebar.text_input(
    "App Password Gmail (16 caratteri)",
    type="password",
    help="Password per le app generata dalle impostazioni di sicurezza del tuo account Google (Verifica in due passaggi)"
)

recipient_email = st.sidebar.text_input(
    "Email Destinatario",
    placeholder="destinatario@scuola.it"
)

st.title("🎓 Team Agenti IA per la Didattica")
st.markdown("""
Questa applicazione web serverless sfrutta un'architettura **Multi-Agente Collaborativa** 
per assistere i docenti nella preparazione di sintesi ed elementi divulgativi su qualsiasi argomento didattico.
""")

# Campo di testo per l'argomento della lezione
argomento_lezione = st.text_area(
    "🎯 Inserisci l'argomento o tema della lezione:",
    placeholder="Es. L'impatto dell'Intelligenza Artificiale nella letteratura moderna, oppure La fotosintesi clorofilliana...",
    height=100
)

def esegui_flusso_agenti(topic: str, api_key: str):
    """
    Funzione per gestire la collaborazione sequenziale tra i due agenti IA tramite OpenRouter.
    - Agente 1 (Ricercatore): Estrae 3 punti chiave in grassetto Markdown.
    - Agente 2 (Scrittore): Elabora un post divulgativo di circa 100 parole per docenti.
    """
    # Inizializzazione client OpenAI puntando agli endpoint OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    # -------------------------------------------------------------
    # AGENTE 1: Ricercatore Didattico
    # -------------------------------------------------------------
    prompt_agente_1 = f"""
    Sei uno specialista e Ricercatore Didattico. Analizza il seguente argomento: '{topic}'.
    Estrai esattamente 3 punti chiave sintetici ed essenziali per una lezione.
    
    REQUISITO FONDAMENTALE:
    Formatta ciascuno dei 3 punti mettendo il titolo/concetto principale in **grassetto Markdown**.
    Es:
    1. **Concetto 1**: Spiegazione sintetica.
    2. **Concetto 2**: Spiegazione sintetica.
    3. **Concetto 3**: Spiegazione sintetica.
    """

    response_agente_1 = client.chat.completions.create(
        model="openrouter/auto",
        messages=[
            {"role": "system", "content": "Sei un esperto Ricercatore Didattico focalizzato su sinteticità e precisione."},
            {"role": "user", "content": prompt_agente_1}
        ]
    )
    risultato_ricercatore = response_agente_1.choices[0].message.content

    # -------------------------------------------------------------
    # AGENTE 2: Scrittore / Divulgatore Didattico
    # -------------------------------------------------------------
    prompt_agente_2 = f"""
    Sei uno Scrittore e Comunicatore Esperto per la scuola primaria e secondaria.
    Prendi in input i seguenti 3 punti chiave focalizzati sull'argomento '{topic}':
    
    {risultato_ricercatore}
    
    Crea un post divulgativo e coinvolgente rivolto ai docenti di circa 100 parole. 
    Il tono deve essere professionale, motivante e chiaro, spiegando l'importanza di insegnare questo tema oggi.
    """

    response_agente_2 = client.chat.completions.create(
        model="openrouter/auto",
        messages=[
            {"role": "system", "content": "Sei un abile copywriter ed educatore scientifico e umanistico."},
            {"role": "user", "content": prompt_agente_2}
        ]
    )
    risultato_scrittore = response_agente_2.choices[0].message.content

    return risultato_ricercatore, risultato_scrittore

def invia_email_report(sender: str, password: str, recipient: str, topic: str, punti_md: str, post_md: str):
    """
    Funzione per convertire i testi Markdown in HTML elegante e inviarli tramite SMTP Gmail (SSL porta 465).
    """
    # Conversione da Markdown ad HTML pulito
    html_punti = markdown.markdown(punti_md)
    html_post = markdown.markdown(post_md)

    # Costruzione del messaggio email in formato multipart/alternative per supporto HTML
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎓 Report Didattico IA: {topic}"
    msg["From"] = sender
    msg["To"] = recipient

    # Template HTML professionale con stili inline e sezioni colorate per i due agenti
    corpo_html = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                background-color: #f4f6f9;
                color: #2c3e50;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 650px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            }}
            .header {{
                background: linear-gradient(135deg, #1E88E5, #1565C0);
                color: #ffffff;
                padding: 25px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 22px;
                font-weight: 600;
            }}
            .header p {{
                margin: 5px 0 0 0;
                font-size: 14px;
                opacity: 0.9;
            }}
            .content {{
                padding: 25px;
            }}
            .agent-card {{
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                border-left: 5px solid;
            }}
            .ricercatore-card {{
                background-color: #f0f7ff;
                border-color: #1E88E5;
            }}
            .scrittore-card {{
                background-color: #f0fdf4;
                border-color: #2E7D32;
            }}
            .agent-title {{
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .ricercatore-title {{ color: #1565C0; }}
            .scrittore-title {{ color: #2E7D32; }}
            .footer {{
                background-color: #f8f9fa;
                padding: 15px;
                text-align: center;
                font-size: 12px;
                color: #7f8c8d;
                border-top: 1px solid #e9ecef;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Report Didattico Automatizzato</h1>
                <p>Tema della lezione: <strong>{topic}</strong></p>
            </div>
            <div class="content">
                
                <!-- SEZIONE AGENTE 1 -->
                <div class="agent-card ricercatore-card">
                    <div class="agent-title ricercatore-title">🔍 Agente 1: Ricercatore Didattico</div>
                    <div>{html_punti}</div>
                </div>

                <!-- SEZIONE AGENTE 2 -->
                <div class="agent-card scrittore-card">
                    <div class="agent-title scrittore-title">✍️ Agente 2: Scrittore & Divulgatore</div>
                    <div>{html_post}</div>
                </div>

            </div>
            <div class="footer">
                Generato automaticamente dal <strong>Team Agenti IA per la Didattica</strong>.
            </div>
        </div>
    </body>
    </html>
    """

    # Collegamento della versione HTML alla mail
    msg.attach(MIMEText(corpo_html, "html"))

    # Invio sicuro tramite SMTP SSL su porta 465
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

st.markdown("---")

col_btn1, col_btn2 = st.columns(2)

# PULSANTE 1: Generazione del Report tramite Agenti IA
with col_btn1:
    if st.button("🚀 Pulsante 1: Genera Report con Agenti", use_container_width=True):
        # Validazione degli input
        if not openrouter_key:
            st.error("⚠️ Inserisci la chiave API di OpenRouter nella barra laterale!")
        elif not argomento_lezione.strip():
            st.warning("⚠️ Inserisci un argomento o tema di lezione prima di procedere.")
        else:
            with st.spinner("🤖 Gli agenti stanno collaborando alla creazione del report..."):
                try:
                    punti, post = esegui_flusso_agenti(argomento_lezione, openrouter_key)
                    # Salvataggio nello stato della sessione per persistenza
                    st.session_state.punti_chiave = punti
                    st.session_state.post_docenti = post
                    st.session_state.ricerca_eseguita = True
                    st.success("✨ Report generato con successo!")
                except Exception as e:
                    st.error(f"❌ Si è verificato un errore durante la generazione: {e}")

# Mostra i dati se presenti nella sessione
if st.session_state.ricerca_eseguita:
    st.markdown("---")
    st.subheader("📄 Risultati del Report Generato")
    
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.info("🔍 **Agente 1 - Ricercatore Didattico**\n\n3 Punti Chiave dell'Argomento:")
        st.markdown(st.session_state.punti_chiave)
        
    with col_res2:
        st.success("✍️ **Agente 2 - Scrittore & Divulgatore**\n\nPost Divulgativo per Docenti (~100 parole):")
        st.markdown(st.session_state.post_docenti)

# PULSANTE 2: Invio Report via Email
with col_btn2:
    if st.button("📧 Pulsante 2: Invia Report via Email", use_container_width=True):
        # Validazioni per l'invio della mail
        if not st.session_state.ricerca_eseguita:
            st.warning("⚠️ Genera prima il report usando il 'Pulsante 1'.")
        elif not sender_email or not gmail_app_password or not recipient_email:
            st.error("⚠️ Completa tutti i campi relativi all'email nella barra laterale!")
        else:
            with st.spinner("✉️ Invio dell'email in corso tramite server Gmail SMTP..."):
                try:
                    invia_email_report(
                        sender=sender_email,
                        password=gmail_app_password,
                        recipient=recipient_email,
                        topic=argomento_lezione,
                        punti_md=st.session_state.punti_chiave,
                        post_md=st.session_state.post_docenti
                    )
                    st.success(f"🎉 Email inviata con successo a {recipient_email}!")
                except Exception as e:
                    st.error(f"❌ Errore durante l'invio dell'email: {e}\n\nVerifica le credenziali o la App Password di Gmail.")