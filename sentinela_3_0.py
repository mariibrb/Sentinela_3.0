import streamlit as st
import os
import pandas as pd

# 1. TENTA IMPORTAR O ESTILO E O MOTOR
try:
    from style import aplicar_estilo_sentinela
    from sentinela_core import extrair_dados_xml_recursivo, gerar_excel_final
except ImportError as e:
    st.error(f"❌ Erro de Estrutura: O arquivo '{e.name}' não foi encontrado.")
    st.stop()

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Sentinela 3.0 | Central de Fechamento", page_icon="🧡", layout="wide")
aplicar_estilo_sentinela()

# 3. FUNÇÃO PARA CARREGAR CLIENTES ATIVOS
def carregar_clientes_ativos():
    caminho_lista = "Clientes Ativos.xlsx"
    if os.path.exists(caminho_lista):
        try:
            df = pd.read_excel(caminho_lista, dtype=str)
            cols_upper = [str(c).upper().strip() for c in df.columns]
            df.columns = cols_upper
            col_cod = next((c for c in cols_upper if any(k in c for k in ['COD', 'ID'])), cols_upper[0])
            col_nome = next((c for c in cols_upper if any(k in c for k in ['NOME', 'CLIENTE', 'RAZAO'])), cols_upper[1])
            col_cnpj = next((c for c in cols_upper if 'CNPJ' in c), None)
            col_seg = next((c for c in cols_upper if 'SEGMENTO' in c), None)
            
            df['DISPLAY'] = df[col_cod].astype(str).str.strip() + " - " + df[col_nome].astype(str).str.strip()
            df['COD_S'] = df[col_cod].astype(str).str.strip(); df['CNPJ_S'] = df[col_cnpj] if col_cnpj else ""
            df['SEG_S'] = df[col_seg].str.upper().strip() if col_seg else "NÃO INFORMADO"
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

df_clientes = carregar_clientes_ativos()

# 4. CABEÇALHO
st.markdown("<div class='titulo-principal'>SENTINELA 3.0</div><div class='barra-laranja'></div>", unsafe_allow_html=True)

# 5. PAINEL LATERAL
with st.sidebar:
    st.markdown("### ⚙️ Passo 1: Identificação")
    opcoes_emp = ["-- SELECIONE UMA EMPRESA --"]
    if not df_clientes.empty: opcoes_emp.extend(df_clientes['DISPLAY'].unique().tolist())
    
    escolha_emp = st.selectbox("Selecione a Empresa", options=opcoes_emp)
    empresa_ok = escolha_emp != "-- SELECIONE UMA EMPRESA --"

    if empresa_ok:
        dados_sel = df_clientes[df_clientes['DISPLAY'] == escolha_emp].iloc[0]
        cod_cliente = dados_sel['COD_S']
        st.text_input("CNPJ", value=dados_sel['CNPJ_S'], disabled=True)
        
        st.markdown("---")
        st.markdown("### ⚖️ Passo 2: Regras Fiscais")
        opcoes_reg = ["-- SELECIONE O REGIME --", "Lucro Real", "Lucro Presumido", "Simples Nacional"]
        escolha_reg = st.selectbox("Regime Tributário", options=opcoes_reg)
        regime_ok = escolha_reg != "-- SELECIONE O REGIME --"
        
        if regime_ok:
            is_ret = st.toggle("Habilitar Módulo RET")
            tipo_ipi = st.selectbox("Contribuinte de IPI?", ["Não", "Sim - Industrial", "Sim - Equiparada"])
            is_ipi = tipo_ipi != "Não"

# 6. CORPO DA PÁGINA (ABAS)
if empresa_ok and regime_ok:
    tab_xml, tab_dominio = st.tabs(["📂 1. Auditoria XML (Origem)", "🖥️ 2. Auditoria Domínio (Conferência)"])
    
    with tab_xml:
        st.markdown("#### XMLs do Cliente")
        if 'reset_xml' not in st.session_state: st.session_state.reset_xml = 0
        xmls = st.file_uploader("Upload XMLs/ZIP", type=['zip', 'xml'], accept_multiple_files=True, key=f"xml_{st.session_state.reset_xml}")
        if xmls and st.button("🗑️ Limpar XMLs"):
            st.session_state.reset_xml += 1; st.rerun()

    with tab_dominio:
        st.markdown("#### Relatórios da Domínio Sistemas")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("**Básico (ICMS/IPI/PIS/COFINS)**")
            ge = st.file_uploader("Gerencial de Entradas", type=['csv', 'txt'], accept_multiple_files=True)
            gs = st.file_uploader("Gerencial de Saídas", type=['csv', 'txt'], accept_multiple_files=True)
        
        with col_g2:
            st.markdown("**Relatórios Próprios (Específicos)**")
            rel_pc = st.file_uploader("Relatório PIS/COFINS (Domínio)", type=['csv', 'txt'], accept_multiple_files=True)
            rel_ret = st.file_uploader("Relatório RET (Domínio)", type=['csv', 'txt'], accept_multiple_files=True) if is_ret else None

    # 7. BOTÃO DE EXECUÇÃO
    st.markdown("---")
    if st.button("🚀 GERAR RELATÓRIO DE FECHAMENTO", use_container_width=True):
        if xmls:
            with st.spinner("Comparando XML vs Domínio..."):
                try:
                    df_ent, df_sai = extrair_dados_xml_recursivo(xmls, dados_sel['CNPJ_S'])
                    # O Motor agora recebe os gerenciais básicos e os relatórios próprios
                    relatorio = gerar_excel_final(df_ent, df_sai, ge, gs, rel_pc, rel_ret, cod_cliente, escolha_reg, is_ret, is_ipi)
                    st.markdown("<div class='status-container'>✅ Auditoria Concluída!</div>", unsafe_allow_html=True)
                    st.download_button("💾 BAIXAR RELATÓRIO", data=relatorio, file_name=f"SENTINELA_{cod_cliente}.xlsx", use_container_width=True)
                except Exception as e: st.error(f"Erro: {e}")
        else: st.warning("⚠️ Carregue os XMLs.")
else:
    st.warning("Aguardando configurações no menu lateral...")
