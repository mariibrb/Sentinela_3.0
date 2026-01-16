import streamlit as st

def aplicar_estilo_sentinela():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
        
        .main {
            background-color: #fcfcfc;
            font-family: 'Space Mono', monospace;
        }

        .titulo-principal {
            font-size: 28px;
            font-weight: 700;
            color: #111;
            text-transform: uppercase;
        }

        /* ESTILO BASE DAS ABAS */
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            background-color: #f8f8f8;
            border: 1px solid #eee;
            font-size: 12px;
            color: #999;
            transition: 0.3s;
        }

        /* CORES INDIVIDUAIS POR ABA (QUANDO SELECIONADAS) */
        
        /* 1. ICMS/IPI - Azul Tático */
        .stTabs [data-baseweb="tab"]:nth-child(1)[aria-selected="true"] {
            border-bottom: 4px solid #007bff !important;
            color: #007bff !important;
            background-color: #ffffff !important;
        }

        /* 2. RET - Verde Operacional */
        .stTabs [data-baseweb="tab"]:nth-child(2)[aria-selected="true"] {
            border-bottom: 4px solid #28a745 !important;
            color: #28a745 !important;
            background-color: #ffffff !important;
        }

        /* 3. ST - Amarelo Alerta */
        .stTabs [data-baseweb="tab"]:nth-child(3)[aria-selected="true"] {
            border-bottom: 4px solid #ffc107 !important;
            color: #ffc107 !important;
            background-color: #ffffff !important;
        }

        /* 4. Difal - Roxo */
        .stTabs [data-baseweb="tab"]:nth-child(4)[aria-selected="true"] {
            border-bottom: 4px solid #6f42c1 !important;
            color: #6f42c1 !important;
            background-color: #ffffff !important;
        }

        /* 5. PIS e COFINS - Ciano/Teal */
        .stTabs [data-baseweb="tab"]:nth-child(5)[aria-selected="true"] {
            border-bottom: 4px solid #17a2b8 !important;
            color: #17a2b8 !important;
            background-color: #ffffff !important;
        }

        /* BOTÃO DE EXECUÇÃO */
        .stButton>button {
            width: 100%;
            background-color: #ffffff !important;
            color: #111 !important;
            border: 2px solid #111 !important;
            font-weight: 700;
            text-transform: uppercase;
        }
        .stButton>button:hover {
            background-color: #111 !important;
            color: #FF4B11 !important;
        }

        /* FLAG RET VERDE */
        div[data-testid="stWidgetLabel"] + div [aria-checked="true"] > div:first-child {
            background-color: #28a745 !important;
            border: 1px solid #1e7e34 !important;
        }
        </style>
    """, unsafe_allow_html=True)
