import streamlit as st

def aplicar_estilo_sentinela():
    st.markdown("""
        <style>
        /* Título e Barra Principal */
        .titulo-principal {
            font-size: 36px;
            font-weight: bold;
            color: #FF4B11;
            margin-bottom: 0px;
        }
        .barra-laranja {
            height: 5px;
            width: 100px;
            background-color: #FF4B11;
            margin-bottom: 25px;
            border-radius: 5px;
        }
        
        /* FLAG DO MÓDULO RET: VERDE COM BORDINHA QUANDO ATIVO */
        /* Estiliza o track do switch quando checkado */
        div[data-testid="stWidgetLabel"] + div [aria-checked="true"] > div:first-child {
            background-color: #28a745 !important;
            border: 2px solid #1e7e34 !important;
        }
        
        /* Estiliza a bolinha do switch quando checkado */
        div[data-testid="stWidgetLabel"] + div [aria-checked="true"] [data-testid="stTooltipHoverTarget"] > div {
            background-color: white !important;
        }

        /* Estilo das Abas Mestre e Sub-abas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            background-color: #f0f2f6;
            border-radius: 5px 5px 0px 0px;
            padding: 8px 16px;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FF4B11 !important;
            color: white !important;
            border-bottom: 2px solid #FF4B11;
        }

        /* Container de Sucesso/Status */
        .status-container {
            padding: 15px;
            border-radius: 8px;
            background-color: #e8f5e9;
            border: 1px solid #28a745;
            color: #1b5e20;
            text-align: center;
            font-weight: bold;
        }

        /* Ajuste de inputs e botões para arredondar mais como solicitado anteriormente */
        .stButton>button {
            border-radius: 10px;
        }
        .stTextInput>div>div>input {
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)
