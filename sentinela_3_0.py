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

# 3. FUNÇÃO DE CARREGAMENTO (CLIENTES ATIVOS)
def carregar_clientes_ativos():
    caminho_lista = "Clientes Ativos.xlsx"
    if os.path.exists(caminho_lista):
        try:
            df = pd.read_excel(caminho_lista, dtype=str)
            df.columns = [str(c).upper().strip() for c in df.columns]
            col_cod = next((c for c in df.columns if any(k in c for k in ['COD', 'ID']) and 'CIDADE' not in c), df.columns[0])
            col_nome = next((c for c in df.columns if any(k in c for k in ['NOME', 'CLIENTE', 'RAZAO', 'EMPRESA']) and 'CIDADE' not in c), df.columns[1])
            col_cnpj = next((c for c in df.columns if 'CNPJ' in c), None)
            df['DISPLAY'] = df[col_cod].str.strip() + " - " + df[col_nome].str.strip()
            df['COD_S'] = df[col_cod].str.strip()
            df['CNPJ_S'] = df[col_cnpj].str.replace(r'\D', '', regex=True) if col_cnpj else ""
            return df[['DISPLAY', 'COD_S', 'CNPJ_S']]
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
        cnpj_auditado = dados_sel['CNPJ_S']
        st.text_input("CNPJ", value=cnpj_auditado, disabled=True)
        st.markdown("---")
        st.markdown("### ⚖️ Passo 2: Regras Fiscais")
        opcoes_reg = ["-- SELECIONE O REGIME --", "Lucro Real", "Lucro Presumido", "Simples Nacional"]
        escolha_reg = st.selectbox("Regime Tributário", options=opcoes_reg)
        regime_ok = escolha_reg != "-- SELECIONE O REGIME --"
        
        if regime_ok:
            is_ret = st.toggle("Habilitar Módulo RET")
            st.markdown("---")
            tipo_ipi = st.selectbox("Contribuinte de IPI?", ["Não", "Sim - Industrial", "Sim - Equiparada"])
            is_ipi = tipo_ipi != "Não"

# 6. CORPO DA PÁGINA (ABAS ORGANIZADAS)
if empresa_ok and (regime_ok if 'regime_ok' in locals() else False):
    st.markdown("### 📂 Auditoria e Conferência Domínio")
    
    tabs = st.tabs([
        "📦 XMLs e Gerenciais (Origem)", 
        "🛡️ ICMS / IPI", 
        "🔒 ST (Subst. Tributária)",
        "💰 PIS / COFINS", 
        "🚛 DIFAL", 
        "🏢 RET"
    ])
    
    with tabs[0]:
        st.markdown("#### Origem: Confronto XML vs Gerencial do Cliente")
        if 'reset_xml' not in st.session_state: st.session_state.reset_xml = 0
        col_xml1, col_xml2 = st.columns(2)
        with col_xml1:
            xmls = st.file_uploader("Upload XMLs/ZIP (Transmitido)", type=['zip', 'xml'], accept_multiple_files=True, key=f"xml_{st.session_state.reset_xml}")
        with col_xml2:
            ge_cli = st.file_uploader("Gerencial Entradas (Sistema Cliente)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            gs_cli = st.file_uploader("Gerencial Saídas (Sistema Cliente)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
        if xmls and st.button("🗑️ Limpar Arquivos de Origem"):
            st.session_state.reset_xml += 1; st.rerun()

    with tabs[1]:
        st.markdown("#### Domínio: ICMS Próprio e IPI")
        gs_icms_ipi = st.file_uploader("Gerencial Saídas (Domínio - ICMS/IPI)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
        ge_icms_ipi = st.file_uploader("Gerencial Entradas (Domínio - ICMS/IPI)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)

    with tabs[2]:
        st.markdown("#### Domínio: Substituição Tributária (ST)")
        gs_st = st.file_uploader("Gerencial Saídas (Domínio - ST)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
        ge_st = st.file_uploader("Gerencial Entradas (Domínio - ST)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)

    with tabs[3]:
        st.markdown("#### Domínio: PIS / COFINS")
        col_pc1, col_pc2 = st.columns(2)
        with col_pc1:
            rel_pc = st.file_uploader("Relatório de Apuração PIS/COFINS", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
        with col_pc2:
            gs_pc = st.file_uploader("Gerencial Saídas (Domínio - PIS/COFINS)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            ge_pc = st.file_uploader("Gerencial Entradas (Domínio - PIS/COFINS)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)

    with tabs[4]:
        st.markdown("#### Domínio: DIFAL")
        rel_difal = st.file_uploader("Relatório DIFAL (Domínio)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)

    with tabs[5]:
        if is_ret:
            st.markdown("#### Domínio: RET")
            col_ret1, col_ret2 = st.columns(2)
            with col_ret1:
                rel_ret = st.file_uploader("Relatório de Apuração RET", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            with col_ret2:
                gs_ret = st.file_uploader("Gerencial Saídas (Domínio - RET)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
                ge_ret = st.file_uploader("Gerencial Entradas (Domínio - RET)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
        else:
            st.warning("Habilite o Módulo RET no menu lateral.")
            rel_ret, gs_ret, ge_ret = None, None, None

    # 7. EXECUÇÃO
    st.markdown("---")
    if st.button("🚀 EXECUTAR CONFERÊNCIA COMPLETA", use_container_width=True):
        if xmls:
            with st.spinner("Cruzando XMLs vs Gerenciais Cliente vs Domínio..."):
                try:
                    df_ent, df_sai = extrair_dados_xml_recursivo(xmls, cnpj_auditado)
                    # O Motor agora recebe todos os gerenciais separados por tributo
                    relatorio = gerar_excel_final(
                        df_ent, df_sai, ge_cli, gs_cli,           # Origem
                        gs_icms_ipi, ge_icms_ipi,               # ICMS/IPI
                        gs_st, ge_st,                           # ST
                        rel_pc, gs_pc, ge_pc,                   # PIS/COFINS
                        rel_difal,                              # DIFAL
                        rel_ret, gs_ret, ge_ret,                # RET
                        cod_cliente, escolha_reg, is_ret, is_ipi
                    )
                    st.success("✅ Relatório gerado com sucesso!")
                    st.download_button("💾 BAIXAR SENTINELA", data=relatorio, file_name=f"SENTINELA_{cod_cliente}.xlsx", use_container_width=True)
                except Exception as e: st.error(f"Erro: {e}")
        else:
            st.warning("⚠️ Carregue os XMLs na primeira aba para iniciar.")
