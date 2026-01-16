import streamlit as st

def aplicar_estilo_sentinela():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

        /* FUNDO E FONTE GLOBAL */
        .main {
            background-color: #0f110c; /* Cinza quase preto militar */
            font-family: 'JetBrains Mono', monospace;
        }

        /* TÍTULO SENTINELA (Estilo Estêncil/Militar) */
        .titulo-principal {
            font-size: 42px;
            font-weight: 800;
            color: #FF4B11;
            letter-spacing: 5px;
            text-transform: uppercase;
            text-shadow: 2px 2px #000;
            margin-bottom: 0px;
        }
        .barra-laranja {
            height: 4px;
            width: 150px;
            background-color: #FF4B11;
            margin-bottom: 30px;
            border: 1px solid #912a0a;
        }

        /* SIDEBAR MILITAR */
        section[data-testid="stSidebar"] {
            background-color: #1a1d16 !important;
            border-right: 2px solid #2d3326;
        }

        /* FLAG RET - VERDE OPERACIONAL COM BORDINHA */
        /* O switch agora parece um botão de painel de controle */
        div[data-testid="stWidgetLabel"] + div [aria-checked="true"] > div:first-child {
            background-color: #3e5c3e !important; /* Verde Musgo */
            border: 2px solid #b5ffb5 !important; /* Brilho verde */
            box-shadow: 0 0 10px #28a745;
        }
        
        /* ABAS (Estilo Pastas de Arquivo ou Abas de Radar) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 5px;
            background-color: #1a1d16;
            padding: 5px;
            border: 1px solid #2d3326;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            background-color: #24291e;
            color: #7d8570 !important;
            border: 1px solid #2d3326;
            border-radius: 0px; /* Abas quadradas militares */
            font-size: 12px;
            text-transform: uppercase;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FF4B11 !important;
            color: white !important;
            border: 1px solid #fff;
        }

        /* CAMPOS DE UPLOAD E INPUTS */
        div[data-testid="stFileUploader"] {
            border: 1px dashed #4e5741;
            background-color: #141710;
            padding: 10px;
        }

        /* BOTÃO DE EXECUÇÃO (ESTILO 'LAUNCH' / DISPARAR) */
        .stButton>button {
            width: 100%;
            background-color: #FF4B11 !important;
            color: white !important;
            border: 2px solid #912a0a !important;
            border-radius: 0px !important;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
            padding: 15px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #ff6a3d !important;
            box-shadow: 0 0 15px #FF4B11;
        }

        /* ALERTAS */
        .stAlert {
            background-color: #1a1d16;
            color: #ffcc00;
            border: 1px solid #ffcc00;
            border-radius: 0px;
        }

        /* EFEITO DE LINHAS DE MONITOR (OPCIONAL) */
        .main::before {
            content: " ";
            display: block;
            position: fixed;
            top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), 
                        linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
            z-index: 9999;
            background-size: 100% 4px, 3px 100%;
            pointer-events: none;
        }
        </style>
    """, unsafe_allow_html=True)
