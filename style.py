import streamlit as st

def aplicar_estilo_sentinela():
    st.markdown("""
        <style>
        /* FONTE TÉCNICA E LIMPA */
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
        
        .main {
            background-color: #fcfcfc; /* Branco gelo */
            font-family: 'Space Mono', monospace;
        }

        /* CABEÇALHO COM ESTILO DE FORMULÁRIO TÉCNICO */
        .titulo-principal {
            font-size: 28px;
            font-weight: 700;
            color: #111;
            letter-spacing: -1px;
            text-transform: uppercase;
        }
        .barra-laranja {
            height: 6px;
            width: 60px;
            background-color: #FF4B11;
            margin-bottom: 40px;
            border-radius: 0px;
        }

        /* SIDEBAR SÓBRIA */
        section[data-testid="stSidebar"] {
            background-color: #f0f0ee !important;
            border-right: 1px solid #ddd;
        }
        section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label {
            color: #333 !important;
            font-size: 13px;
        }

        /* TOGGLE DO RET: VERDE OPERACIONAL COM BORDA */
        div[data-testid="stWidgetLabel"] + div [aria-checked="true"] > div:first-child {
            background-color: #28a745 !important;
            border: 1px solid #1e7e34 !important;
        }

        /* ABAS: ESTILO DE FICHÁRIO INDUSTRIAL (RETAS) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            background-color: #f8f8f8;
            border: 1px solid #eee;
            border-radius: 0px; 
            padding: 8px 20px;
            font-size: 12px;
            color: #999;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ffffff !important;
            color: #FF4B11 !important;
            border: 1px solid #ddd !important;
            border-bottom: 2px solid #FF4B11 !important;
        }

        /* BOTÃO DE EXECUÇÃO: DESIGN DE COMANDO ÚNICO */
        .stButton>button {
            width: 100%;
            background-color: #ffffff !important;
            color: #111 !important;
            border: 1px solid #111 !important;
            border-radius: 0px !important;
            font-weight: 700;
            height: 45px;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: 0.2s;
        }
        .stButton>button:hover {
            background-color: #111 !important;
            color: #FF4B11 !important;
        }

        /* ESTILIZAÇÃO DOS DROPS DE ARQUIVOS */
        [data-testid="stFileUploader"] {
            border: 1px solid #eee;
            background-color: #fafafa;
            border-radius: 0px;
        }
        
        /* LINHAS DE DIVISÃO TÁTICAS */
        hr {
            border: 0;
            border-top: 1px solid #eee;
            margin: 25px 0;
        }
        </style>
    """, unsafe_allow_html=True)
