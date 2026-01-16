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

# 3. FUNÇÃO DE BUSCA ULTRA-RESISTENTE PARA O EXCEL DE CLIENTES
def carregar_clientes_ativos():
    arquivos_na_pasta = os.listdir('.')
    arquivo_alvo = None
    
    # Procura qualquer arquivo que contenha "CLIENTES" e "ATIVOS" no nome
    for f in arquivos_na_pasta:
        nome_normalizado = f.upper().replace(" ", "")
        if "CLIENTESATIVOS" in nome_normalizado and f.endswith('.xlsx'):
            arquivo_alvo = f
            break
    
    if arquivo_alvo:
        try:
            # Lê o arquivo Excel
            df = pd.read_excel(arquivo_alvo)
            
            # Limpa e padroniza os nomes das colunas
            df.columns = [str(c).upper().strip() for c in df.columns]

            # Identifica as colunas necessárias por palavras-chave
            col_cod = next((c for c in df.columns if any(k in c for k in ['COD', 'ID']) and 'CIDADE' not in c), df.columns[0])
            col_nome = next((c for c in df.columns if any(k in c for k in ['NOME', 'CLIENTE', 'RAZAO', 'EMPRESA']) and 'CIDADE' not in c), df.columns[1])
            col_cnpj = next((c for c in df.columns if 'CNPJ' in c), None)
            col_seg = next((c for c in df.columns if 'SEGMENTO' in c or 'ATIVIDADE' in c), None)

            # --- CORREÇÃO DO ERRO 'Series' object has no attribute 'strip' ---
            # Convertemos cada coluna para string e removemos espaços com funções seguras
            def limpar_texto(val):
                return str(val).strip() if pd.notna(val) else ""

            df['COD_S'] = df[col_cod].apply(limpar_texto)
            df['NOME_S'] = df[col_nome].apply(limpar_texto)
            df['CNPJ_S'] = df[col_cnpj].apply(limpar_texto).str.replace(r'\D', '', regex=True) if col_cnpj else ""
            df['SEG_S'] = df[col_seg].apply(limpar_texto).upper() if col_seg else "NÃO INFORMADO"
            
            # Cria a coluna de exibição: "CÓDIGO - NOME"
            df['DISPLAY'] = df['COD_S'] + " - " + df['NOME_S']
            
            return df[['DISPLAY', 'COD_S', 'CNPJ_S', 'SEG_S']]
        except Exception as e:
            st.error(f"Erro ao processar o conteúdo do arquivo: {e}")
            return pd.DataFrame()
    else:
        st.sidebar.error("❌ Arquivo 'Clientes Ativos.xlsx' não encontrado no GitHub.")
        return pd.DataFrame()

df_clientes = carregar_clientes_ativos()

# 4. CABEÇALHO
st.markdown("<div class='titulo-principal'>SENTINELA 3.0</div><div class='barra-laranja'></div>", unsafe_allow_html=True)

# 5. PAINEL LATERAL
with st.sidebar:
    st.markdown("### ⚙️ Passo 1: Identificação")
    
    if df_clientes.empty:
        st.warning("⚠️ A lista de empresas está vazia.")
        escolha_emp = "-- SELECIONE UMA EMPRESA --"
    else:
        opcoes_emp = ["-- SELECIONE UMA EMPRESA --"] + df_clientes['DISPLAY'].unique().tolist()
        escolha_emp = st.selectbox("Selecione a Empresa", options=opcoes_emp)
    
    empresa_ok = escolha_emp != "-- SELECIONE UMA EMPRESA --"

    if empresa_ok:
        dados_sel = df_clientes[df_clientes['DISPLAY'] == escolha_emp].iloc[0]
        cod_cliente = dados_sel['COD_S']
        st.text_input("CNPJ", value=dados_sel['CNPJ_S'], disabled=True)
        st.markdown(f"**Segmento:** `{dados_sel['SEG_S']}`")
        
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
if empresa_ok and (regime_ok if 'regime_ok' in locals() else False):
    tab_xml, tab_dominio = st.tabs(["📂 1. Auditoria XML (Origem)", "🖥️ 2. Auditoria Domínio (Conferência)"])
    
    with tab_xml:
        st.markdown("#### XMLs do Cliente")
        if 'reset_xml' not in st.session_state: st.session_state.reset_xml = 0
        xmls = st.file_uploader("Upload XML/ZIP", type=['zip', 'xml'], accept_multiple_files=True, key=f"xml_{st.session_state.reset_xml}")
        if xmls and st.button("🗑️ Limpar XMLs"):
            st.session_state.reset_xml += 1; st.rerun()

    with tab_dominio:
        st.markdown("#### Relatórios da Domínio Sistemas")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("**Básico (ICMS/IPI)**")
            ge = st.file_uploader("Gerencial Entradas", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            gs = st.file_uploader("Gerencial Saídas", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
        with col_g2:
            st.markdown("**Específicos**")
            rel_pc = st.file_uploader("Relatório PIS/COFINS", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True)
            rel_ret = st.file_uploader("Relatório RET", type=['csv', 'txt', 'xlsx'], accept_multiple_files=True) if is_ret else None

    # 7. BOTÃO DE EXECUÇÃO
    st.markdown("---")
    if st.button("🚀 GERAR RELATÓRIO DE FECHAMENTO", use_container_width=True):
        if xmls:
            with st.spinner("Comparando XML vs Domínio..."):
                try:
                    df_ent, df_sai = extrair_dados_xml_recursivo(xmls, dados_sel['CNPJ_S'])
                    relatorio = gerar_excel_final(df_ent, df_sai, ge, gs, rel_pc, rel_ret, cod_cliente, escolha_reg, is_ret, is_ipi)
                    st.success("✅ Auditoria Concluída!")
                    st.download_button("💾 BAIXAR RELATÓRIO", data=relatorio, file_name=f"SENTINELA_{cod_cliente}.xlsx", use_container_width=True)
                except Exception as e: st.error(f"Erro no processamento: {e}")
        else: st.warning("⚠️ Carregue os XMLs.")
else:
    st.warning("Aguardando configurações laterais...")
