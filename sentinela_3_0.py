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
        except: return pd.DataFrame()
    return pd.DataFrame()

df_clientes = carregar_clientes_ativos()

# 4. CABEÇALHO E ESTILO BASE
aplicar_estilo_sentinela()
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

# 6. CORPO DA PÁGINA COM CORES TOTAIS POR ABA
if empresa_ok and (regime_ok if 'regime_ok' in locals() else False):
    
    aba_mestre = st.radio("Selecione o Bloco de Auditoria", ["🔍 Auditoria XML", "🖥️ Auditoria Domínio"], horizontal=True)

    if aba_mestre == "🔍 Auditoria XML":
        # Cor de fundo para XML: Branco Gelo
        st.markdown("<style>.main { background-color: #fcfcfc !important; }</style>", unsafe_allow_html=True)
        st.markdown("#### Dados de Origem (xml)")
        if 'reset_xml' not in st.session_state: st.session_state.reset_xml = 0
        xmls = st.file_uploader("Upload XMLs/ZIP", type=['zip', 'xml'], accept_multiple_files=True, key=f"xml_{st.session_state.reset_xml}")
        if xmls and st.button("🗑️ Limpar XMLs"):
            st.session_state.reset_xml += 1; st.rerun()

    else:
        # SISTEMA DE CORES TOTAIS PARA DOMÍNIO
        # Usamos um selectbox ou radio para "simular" as abas e mudar a cor do fundo
        aba_dominio = st.radio(
            "Selecione o Tributo para Conferência", 
            ["🛡️ ICMS/IPI", "🏢 RET", "🔒 ST", "🚛 Difal", "💰 Pis e Cofins"], 
            horizontal=True
        )

        # Mapeamento de Cores Totais (Tons bem claros/pastéis para não cansar a vista)
        cores = {
            "🛡️ ICMS/IPI": "#e3f2fd", # Azul muito claro
            "🏢 RET": "#e8f5e9",      # Verde muito claro
            "🔒 ST": "#fffde7",       # Amarelo muito claro
            "🚛 Difal": "#f3e5f5",    # Roxo muito claro
            "💰 Pis e Cofins": "#e0f7fa" # Ciano muito claro
        }
        
        cor_selecionada = cores[aba_dominio]
        st.markdown(f"<style>.main {{ background-color: {cor_selecionada} !important; transition: 0.5s; }}</style>", unsafe_allow_html=True)

        st.markdown(f"#### Conformidade Domínio: {aba_dominio}")
        
        if aba_dominio == "🛡️ ICMS/IPI":
            gs_icms_ipi = st.file_uploader("Domínio: Gerencial Saídas (ICMS/IPI)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            ge_icms_ipi = st.file_uploader("Domínio: Gerencial Entradas (ICMS/IPI)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
        
        elif aba_dominio == "🏢 RET":
            if is_ret:
                c1, c2 = st.columns(2)
                rel_ret = c1.file_uploader("Domínio: Apuração RET", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
                gs_ret = c2.file_uploader("Domínio: Gerencial Saídas (RET)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
                ge_ret = c2.file_uploader("Domínio: Gerencial Entradas (RET)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            else: st.warning("Módulo RET desativado.")

        elif aba_dominio == "🔒 ST":
            c1, c2 = st.columns(2)
            rel_st = c1.file_uploader("Domínio: Apuração ST", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            gs_st = c2.file_uploader("Domínio: Gerencial Saídas (ST)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            ge_st = c2.file_uploader("Domínio: Gerencial Entradas (ST)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)

        elif aba_dominio == "🚛 Difal":
            c1, c2 = st.columns(2)
            rel_difal = c1.file_uploader("Domínio: Apuração Difal", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            xml_difal = c2.file_uploader("XML do Cliente (Base Difal)", type=['zip', 'xml'], accept_multiple_files=True)

        elif aba_dominio == "💰 Pis e Cofins":
            c1, c2 = st.columns(2)
            rel_pc = c1.file_uploader("Domínio: Apuração PIS/COFINS", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            gs_pc = c2.file_uploader("Domínio: Gerencial Saídas (PIS/COFINS)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            ge_pc = c2.file_uploader("Domínio: Gerencial Entradas (PIS/COFINS)", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)

    # 7. BOTÃO DE EXECUÇÃO
    st.markdown("---")
    if st.button("🚀 EXECUTAR PROCESSO DE FECHAMENTO", use_container_width=True):
        if 'xmls' in locals() and xmls:
            with st.spinner("Auditando..."):
                try:
                    df_ent, df_sai = extrair_dados_xml_recursivo(xmls, dados_sel['CNPJ_S'])
                    # Coleta de variáveis (garante que existam mesmo se não preenchidas)
                    args = [gs_icms_ipi if 'gs_icms_ipi' in locals() else None, ge_icms_ipi if 'ge_icms_ipi' in locals() else None,
                            rel_st if 'rel_st' in locals() else None, gs_st if 'gs_st' in locals() else None, ge_st if 'ge_st' in locals() else None,
                            rel_pc if 'rel_pc' in locals() else None, gs_pc if 'gs_pc' in locals() else None, ge_pc if 'ge_pc' in locals() else None,
                            rel_difal if 'rel_difal' in locals() else None, xml_difal if 'xml_difal' in locals() else None,
                            rel_ret if 'rel_ret' in locals() else None, gs_ret if 'gs_ret' in locals() else None, ge_ret if 'ge_ret' in locals() else None]
                    
                    relatorio = gerar_excel_final(df_ent, df_sai, *args, dados_sel['COD_S'], escolha_reg, is_ret, is_ipi)
                    st.success("✅ Concluído!")
                    st.download_button("💾 BAIXAR SENTINELA", data=relatorio, file_name=f"SENTINELA_{dados_sel['COD_S']}.xlsx", use_container_width=True)
                except Exception as e: st.error(f"Erro: {e}")
        else: st.warning("⚠️ Carregue os XMLs na Auditoria XML.")
