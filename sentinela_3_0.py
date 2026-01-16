import streamlit as st
import os
import pandas as pd

# 1. TENTA IMPORTAR O ESTILO E O MOTOR
try:
    from style import aplicar_estilo_sentinela
    from sentinela_core import extrair_dados_xml_recursivo, gerar_excel_final
except ImportError as e:
    st.error(f"❌ Erro de Estrutura: O arquivo '{e.name}' não foi encontrado na raiz do repositório.")
    st.info("Certifique-se de que 'style.py' e 'sentinela_core.py' estão na mesma pasta.")
    st.stop()

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Sentinela 3.0 | Auditoria Fiscal", page_icon="🧡", layout="wide")
aplicar_estilo_sentinela()

# 3. FUNÇÃO INTELIGENTE PARA CARREGAR EMPRESAS (PROCURA COLUNAS SOZINHA)
def carregar_empresas_inteligente():
    # Procura por qualquer arquivo que pareça ser a listagem na raiz
    arquivos_raiz = os.listdir('.')
    caminho_lista = next((f for f in arquivos_raiz if 'LISTAGEM' in f.upper() or 'CLIENTES' in f.upper()), None)
    
    if caminho_lista:
        try:
            df = pd.read_excel(caminho_lista, dtype=str)
            cols = [str(c).upper().strip() for c in df.columns]
            df.columns = cols

            # Identifica as colunas por palavras-chave
            col_cod = next((c for c in cols if any(k in c for k in ['COD', 'ID', 'CONTA'])), cols[0])
            col_nome = next((c for c in cols if any(k in c for k in ['NOME', 'CLIENTE', 'EMPRESA', 'RAZAO'])), cols[1])
            col_cnpj = next((c for c in cols if 'CNPJ' in c), None)

            df['DISPLAY'] = df[col_cod].astype(str) + " - " + df[col_nome].astype(str)
            df['COD_SENTINELA'] = df[col_cod]
            df['CNPJ_SENTINELA'] = df[col_cnpj] if col_cnpj else ""
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df_empresas = carregar_empresas_inteligente()

# 4. CABEÇALHO
st.markdown("<div class='titulo-principal'>SENTINELA 3.0</div><div class='barra-laranja'></div>", unsafe_allow_html=True)

# 5. PAINEL LATERAL
with st.sidebar:
    st.markdown("### ⚙️ Configurações da Auditoria")
    
    if not df_empresas.empty:
        empresa_selecionada = st.selectbox("Selecione a Empresa", df_empresas['DISPLAY'].tolist())
        dados_selecionados = df_empresas[df_empresas['DISPLAY'] == empresa_selecionada].iloc[0]
        
        cod_cliente = dados_selecionados['COD_SENTINELA']
        cnpj_sugerido = dados_selecionados['CNPJ_SENTINELA']
        cnpj_auditado = st.text_input("CNPJ da Empresa Auditada", value=cnpj_sugerido)
    else:
        st.warning("⚠️ Planilha de listagem não encontrada ou colunas irreconhecíveis.")
        cod_cliente = st.text_input("Código do Cliente (Manual)", placeholder="Digite o código...")
        cnpj_auditado = st.text_input("CNPJ (Manual)", placeholder="Apenas números...")
    
    regime = st.selectbox("Regime Fiscal", ["Lucro Real", "Lucro Presumido", "Simples Nacional"])
    is_ret = st.toggle("Habilitar Módulo RET MG")
    
    st.markdown("---")
    st.caption("Sentinela Fiscal v3.0")

# 6. ÁREA DE UPLOAD
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📥 Arquivos XML")
    xmls = st.file_uploader("Arraste os XMLs ou ZIPs", type=['zip', 'xml'], accept_multiple_files=True)

with col2:
    st.markdown("### 📑 Arquivos Auxiliares")
    ge = st.file_uploader("Gerencial Entradas (CSV)", type=['csv', 'txt'], accept_multiple_files=True)
    gs = st.file_uploader("Gerencial Saídas (CSV)", type=['csv', 'txt'], accept_multiple_files=True)

# 7. BOTÃO DE EXECUÇÃO
if st.button("🚀 INICIAR AUDITORIA COMPLETA"):
    if xmls and cnpj_auditado and cod_cliente:
        with st.spinner("Processando..."):
            try:
                df_ent, df_sai = extrair_dados_xml_recursivo(xmls, cnpj_auditado)
                if not df_ent.empty or not df_sai.empty:
                    relatorio = gerar_excel_final(df_ent, df_sai, None, None, ge, gs, cod_cliente, regime, is_ret)
                    st.markdown("<div class='status-container'>✅ Auditoria Concluída!</div>", unsafe_allow_html=True)
                    st.download_button("💾 BAIXAR RELATÓRIO FINAL", data=relatorio, file_name=f"SENTINELA_{cod_cliente}.xlsx", use_container_width=True)
                else:
                    st.error("❌ Nenhum dado extraído.")
            except Exception as e:
                st.error(f"❌ Erro: {e}")
    else:
        st.warning("⚠️ Preencha todos os campos obrigatórios.")
