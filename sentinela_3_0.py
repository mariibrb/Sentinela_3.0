import streamlit as st
import os
import pandas as pd

# 1. TENTA IMPORTAR O ESTILO E O MOTOR (Trava de segurança inicial)
try:
    from style import aplicar_estilo_sentinela
    from sentinela_core import extrair_dados_xml_recursivo, gerar_excel_final
except ImportError as e:
    st.error(f"❌ Erro de Estrutura: O arquivo '{e.name}' não foi encontrado na raiz.")
    st.stop()

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Sentinela 3.0 | Central de Fechamento", page_icon="🧡", layout="wide")
aplicar_estilo_sentinela()

# 3. FUNÇÃO INTELIGENTE PARA CARREGAR LISTAGEM DE EMPRESAS
def carregar_empresas_inteligente():
    arquivos_raiz = os.listdir('.')
    caminho_lista = next((f for f in arquivos_raiz if f.endswith(('.xlsx', '.xls')) and 
                         ('LISTAGEM' in f.upper() or 'CLIENTES' in f.upper())), None)
    
    if caminho_lista:
        try:
            df = pd.read_excel(caminho_lista, dtype=str)
            cols_upper = [str(c).upper().strip() for c in df.columns]
            df.columns = cols_upper
            # Prioriza Código e Nome, ignora cidades
            col_cod = next((c for c in cols_upper if any(k in c for k in ['COD', 'ID']) and 'CIDADE' not in c), cols_upper[0])
            col_nome = next((c for c in cols_upper if any(k in c for k in ['NOME', 'CLIENTE', 'RAZAO']) and 'CIDADE' not in c), cols_upper[1])
            col_cnpj = next((c for c in cols_upper if 'CNPJ' in c), None)
            
            df['DISPLAY'] = df[col_cod].astype(str) + " - " + df[col_nome].astype(str)
            df['COD_S'] = df[col_cod].astype(str); df['CNPJ_S'] = df[col_cnpj] if col_cnpj else ""
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

df_empresas = carregar_empresas_inteligente()

# 4. CABEÇALHO
st.markdown("<div class='titulo-principal'>SENTINELA 3.0</div><div class='barra-laranja'></div>", unsafe_allow_html=True)

# 5. PAINEL LATERAL (Configurações e Travas)
with st.sidebar:
    st.markdown("### ⚙️ Passo 1: Identificação")
    
    opcoes_emp = ["-- SELECIONE UMA EMPRESA --"]
    if not df_empresas.empty: opcoes_emp.extend(df_empresas['DISPLAY'].unique().tolist())
    
    escolha_emp = st.selectbox("Selecione a Empresa", options=opcoes_emp)
    empresa_ok = escolha_emp != "-- SELECIONE UMA EMPRESA --"

    if not empresa_ok:
        st.info("👆 Selecione a empresa para liberar o sistema.")
        cod_cliente, cnpj_auditado = None, None
    else:
        dados_sel = df_empresas[df_empresas['DISPLAY'] == escolha_emp].iloc[0]
        cod_cliente = dados_sel['COD_S']
        cnpj_auditado = st.text_input("CNPJ (Confirmar)", value=dados_sel['CNPJ_S'])
        
        st.markdown("---")
        st.markdown("### ⚖️ Passo 2: Regras Fiscais")
        opcoes_reg = ["-- SELECIONE O REGIME --", "Lucro Real", "Lucro Presumido", "Simples Nacional"]
        escolha_reg = st.selectbox("Regime Tributário", options=opcoes_reg)
        regime_ok = escolha_reg != "-- SELECIONE O REGIME --"
        
        if not regime_ok:
            st.warning("⚠️ Selecione o Regime para liberar os módulos.")
        else:
            st.success(f"Regime {escolha_reg} Ativado")
            is_ret = st.toggle("Habilitar Módulo RET (Construção Civil)")
            is_ipi = st.toggle("Habilitar Módulo IPI")

# 6. CORPO DA PÁGINA (Abas de Trabalho)
if empresa_ok and regime_ok:
    # Criamos abas dentro do site para organizar os uploads
    tab_xml, tab_dominio = st.tabs(["📂 1. Auditoria XML (Origem)", "🖥️ 2. Auditoria Domínio (Conferência)"])
    
    with tab_xml:
        st.markdown("#### Envie os XMLs do Cliente")
        if 'reset_xml' not in st.session_state: st.session_state.reset_xml = 0
        
        xmls = st.file_uploader("Arraste XMLs ou ZIP aqui", type=['zip', 'xml'], accept_multiple_files=True, key=f"xml_{st.session_state.reset_xml}")
        
        if xmls:
            if st.button("🗑️ Limpar Todos os XMLs"):
                st.session_state.reset_xml += 1
                st.rerun()

    with tab_dominio:
        st.markdown("#### Envie os Relatórios da Domínio Sistemas")
        st.caption("Relatórios de Saídas/Entradas em CSV ou TXT para comparar com os XMLs e Gabaritos.")
        ge = st.file_uploader("Gerencial de Entradas (Domínio)", type=['csv', 'txt'], accept_multiple_files=True)
        gs = st.file_uploader("Gerencial de Saídas (Domínio)", type=['csv', 'txt'], accept_multiple_files=True)

    # 7. BOTÃO DE EXECUÇÃO FINAL
    st.markdown("---")
    if st.button("🚀 GERAR RELATÓRIO DE FECHAMENTO", use_container_width=True):
        if xmls:
            with st.spinner("O Sentinela está auditando XMLs e conferindo lançamentos da Domínio..."):
                try:
                    df_ent, df_sai = extrair_dados_xml_recursivo(xmls, cnpj_auditado)
                    relatorio = gerar_excel_final(df_ent, df_sai, ge, gs, cod_cliente, escolha_reg, is_ret)
                    
                    st.markdown("<div class='status-container'>✅ Auditoria e Apuração Concluídas!</div>", unsafe_allow_html=True)
                    st.download_button("💾 BAIXAR RELATÓRIO COMPLETO (.XLSX)", data=relatorio, file_name=f"SENTINELA_3.0_{cod_cliente}.xlsx", use_container_width=True)
                except Exception as e:
                    st.error(f"Erro no processamento: {e}")
        else:
            st.warning("⚠️ Você precisa carregar pelo menos os XMLs para iniciar.")
else:
    if not empresa_ok:
        st.warning("Aguardando seleção da Empresa no menu lateral...")
    elif not regime_ok:
        st.warning("Aguardando definição do Regime Tributário no menu lateral...")
