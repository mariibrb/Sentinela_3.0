import streamlit as st

def aplicar_estilo_sentinela():
    st.markdown("""
        <style>
        /* FONTE E FUNDO PROFISSIONAL */
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        
        .main {
            background-color: #f4f4f2; /* Cinza claro neutro */
            font-family: 'Roboto Mono', monospace;
        }

        /* TÍTULO IMPACTANTE MAS LIMPO */
        .titulo-principal {
            font-size: 32px;
            font-weight: 700;
            color: #1a1a1a;
            letter-spacing: 2px;
            margin-bottom: 0px;
        }
        .barra-laranja {
            height: 4px;
            width: 80px;
            background-color: #FF4B11;
            margin-bottom: 30px;
        }

        /* SIDEBAR TÁTICA */
        section[data-testid="stSidebar"] {
            background-color: #262730 !important; /* Cinza escuro militar */
        }
        section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label {
            color: #ffffff !important;
        }

        /* BOTÃO RET - VERDE COM BORDA (O QUE VOCÊ GOSTA) */
        div[data-testid="stWidgetLabel"] + div [aria-checked="true"] > div:first-child {
            background-color: #28a745 !important;
            border: 2px solid #1e7e34 !important;
        }

        /* ABAS RETAS (ESTILO MILITAR) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            background-color: #e0e0e0;
            border-radius: 0px; /* Quadradas */
            border: 1px solid #d0d0d0;
            padding: 10px 20px;
            color: #666;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FF4B11 !important;
            color: white !important;
            border: 1px solid #FF4B11;
        }

        /* BOTÃO DE EXECUÇÃO (ROBUSTO) */
        .stButton>button {
            width: 100%;
            background-color: #1a1a1a !important;
            color: #FF4B11 !important;
            border: 2px solid #FF4B11 !important;
            border-radius: 0px !important;
            font-weight: bold;
            height: 50px;
            text-transform: uppercase;
        }
        .stButton>button:hover {
            background-color: #FF4B11 !important;
            color: white !important;
        }

        /* ENQUADRAMENTO DOS UPLOADS */
        [data-testid="stFileUploader"] {
            border: 1px solid #ccc;
            background-color: white;
            padding: 15px;
        }
        </style>
    """, unsafe_allow_html=True)
