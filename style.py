import streamlit as st

def aplicar_estilo_sentinela():
    """
    Aplica a identidade visual Premium do Sentinela 3.0.
    Cores: Laranja (#FF6F00) e Branco (#FFFFFF).
    """
    st.markdown("""
    <style>
        /* 1. LIMPEZA DE INTERFACE: Remove menus e rodapés do Streamlit */
        header {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
        
        /* 2. FUNDO DO APP */
        .stApp { background-color: #F0F2F6; }

        /* 3. SIDEBAR CUSTOMIZADA: Branca com borda direita laranja */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 4px solid #FF6F00;
        }

        /* 4. BOTÕES PÍLULA (GRADIENTE): Para botões de ação e download */
        div.stDownloadButton > button, 
        div.stButton > button {
            background: linear-gradient(135deg, #FF6F00 0%, #FF9100 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 0.8rem 2rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            box-shadow: 0 4px 15px rgba(255, 111, 0, 0.3) !important;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            width: 100% !important;
            cursor: pointer !important;
        }

        /* Efeito de hover nos botões (levanta e aumenta sombra) */
        div.stDownloadButton > button:hover, 
        div.stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(255, 111, 0, 0.4) !important;
            color: #FFFFFF !important;
        }

        /* 5. TÍTULOS E ELEMENTOS VISUAIS */
        .titulo-principal { 
            color: #FF6F00; 
            font-weight: 900; 
            font-size: 2.5rem; 
            margin-bottom: 5px;
            letter-spacing: -1px;
        }

        .barra-laranja {
            height: 3px;
            background: linear-gradient(to right, #FF6F00, #FF9100, transparent);
            margin-bottom: 30px;
            border-radius: 10px;
        }
        
        /* 6. CONTAINERS DE STATUS (CARDS) */
        .status-container {
            padding: 20px;
            border-left: 6px solid #FF6F00;
            background-color: #FFFFFF;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            margin-bottom: 25px;
            color: #31333F;
        }

        /* 7. CUSTOMIZAÇÃO DE INPUTS (OPCIONAL) */
        .stTextInput > div > div > input {
            border-radius: 10px !important;
        }
        
    </style>
    """, unsafe_allow_html=True)
