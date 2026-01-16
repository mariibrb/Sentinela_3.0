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

# 3. FUNÇÃO DE CARREGAMENTO ORIGINAL
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
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

df_clientes = carregar_clientes_ativos()

# 4. CABEÇALHO
st.markdown("<div class='titulo-principal'>SENTINELA 3.0</div><div class='barra-laranja'></div>", unsafe_allow_html=True)

# 5. PAINEL LATERAL
with st.sidebar:
    st.markdown("### ⚙️ Passo 1: Identificação")
    opcoes_emp = ["-- SELECIONE UMA EMPRESA --"]
    if not df_clientes.empty:
        opcoes_emp.extend(df_clientes['DISPLAY'].unique().tolist())
    
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
            st.markdown("---")
            tipo_ipi = st.selectbox("Contribuinte de IPI?", ["Não", "Sim - Industrial", "Sim - Equiparada"])
            is_ipi = tipo_ipi != "Não"

# 6. CORPO DA PÁGINA - SEPARAÇÃO POR ABAS MESTRE
if empresa_ok and (regime_ok if 'regime_ok' in locals() else False):
    
    aba_mestre_xml, aba_mestre_dominio = st.tabs(["🔍 Auditoria XML", "🖥️ Auditoria Domínio"])

    # --- ABA 1: AUDITORIA XML ---
    with aba_mestre_xml:
        st.markdown("#### Dados de Origem (Confronto XML vs Sistema do Cliente)")
        col_xml1, col_xml2 = st.columns(2)
        with col_xml1:
            if 'reset_xml' not in st.session_state: st.session_state.reset_xml = 0
            xmls = st.file_uploader("Upload XMLs/ZIP (Transmitido)", type=['zip', 'xml'], accept_multiple_files=True, key=f"xml_{st.session_state.reset_xml}")
        with col_xml2:
            ge_cli = st.file_uploader("Gerencial Entradas (Sistema Cliente)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            gs_cli = st.file_uploader("Gerencial Saídas (Sistema Cliente)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
        
        if xmls and st.button("🗑️ Limpar Arquivos de Origem"):
            st.session_state.reset_xml += 1; st.rerun()

    # --- ABA 2: AUDITORIA DOMÍNIO ---
    with aba_mestre_dominio:
        st.markdown("#### Conformidade Domínio Sistemas")
        
        # Ordem e nomes das abas conforme solicitado
        sub_tab_icms, sub_tab_ret, sub_tab_st, sub_tab_difal, sub_tab_pc = st.tabs([
            "🛡️ ICMS/IPI", "🏢 RET", "🔒 ST", "🚛 Difal", "💰 Pis e Cofins"
        ])
        
        with sub_tab_icms:
            gs_icms_ipi = st.file_uploader("Domínio: Gerencial Saídas (ICMS/IPI)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            ge_icms_ipi = st.file_uploader("Domínio: Gerencial Entradas (ICMS/IPI)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)

        with sub_tab_ret:
            if is_ret:
                cr1, cr2 = st.columns(2)
                with cr1:
                    rel_ret = st.file_uploader("Domínio: Apuração RET", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
                with cr2:
                    gs_ret = st.file_uploader("Domínio: Gerencial Saídas (RET)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
                    ge_ret = st.file_uploader("Domínio: Gerencial Entradas (RET)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            else:
                st.warning("Módulo RET desativado no menu lateral.")
                rel_ret, gs_ret, ge_ret = None, None, None

        with sub_tab_st:
            gs_st = st.file_uploader("Domínio: Gerencial Saídas (ST)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            ge_st = st.file_uploader("Domínio: Gerencial Entradas (ST)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)

        with sub_tab_difal:
            rel_difal = st.file_uploader("Domínio: Relatório Difal", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)

        with sub_tab_pc:
            c1, c2 = st.columns(2)
            with c1:
                rel_pc = st.file_uploader("Domínio: Apuração PIS/COFINS", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            with c2:
                gs_pc = st.file_uploader("Domínio: Gerencial Saídas (PIS/COFINS)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
                ge_pc = st.file_uploader("Domínio: Gerencial Entradas (PIS/COFINS)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)

    # 7. BOTÃO DE EXECUÇÃO
    st.markdown("---")
    if st.button("🚀 EXECUTAR PROCESSO DE FECHAMENTO", use_container_width=True):
        if xmls:
            with st.spinner("Auditando XML e Domínio..."):
                try:
                    df_ent, df_sai = extrair_dados_xml_recursivo(xmls, dados_sel['CNPJ_S'])
                    relatorio = gerar_excel_final(
                        df_ent, df_sai, ge_cli, gs_cli,
                        gs_icms_ipi, ge_icms_ipi,
                        gs_st, ge_st,
                        rel_pc, gs_pc, ge_pc,
                        rel_difal,
                        rel_ret, gs_ret, ge_ret,
                        cod_cliente, escolha_reg, is_ret, is_ipi
                    )
                    st.success("✅ Fechamento concluído!")
                    st.download_button("💾 BAIXAR SENTINELA", data=relatorio, file_name=f"SENTINELA_{cod_cliente}.xlsx", use_container_width=True)
                except Exception as e: st.error(f"Erro: {e}")
        else:
            st.warning("⚠️ Carregue os XMLs na aba 'Auditoria XML' para começar.")
else:
    st.warning("Selecione a Empresa e o Regime para liberar as abas.")
