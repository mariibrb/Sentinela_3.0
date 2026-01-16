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
    # Lista todos os arquivos na pasta para não errar o nome
    arquivos_na_pasta = os.listdir('.')
    
    # Procura qualquer arquivo .xlsx que contenha "CLIENTE" e "ATIVO" no nome
    arquivo_alvo = None
    for f in arquivos_na_pasta:
        nome_normalizado = f.upper().replace(" ", "")
        if "CLIENTESATIVOS" in nome_normalizado and f.endswith('.xlsx'):
            arquivo_alvo = f
            break
    
    if arquivo_alvo:
        try:
            # Lê o arquivo forçando tudo como texto para não perder o CNPJ
            df = pd.read_excel(arquivo_alvo, dtype=str)
            
            # Padroniza os nomes das colunas (tira espaços e põe em maiúsculo)
            df.columns = [str(c).upper().strip() for c in df.columns]

            # Identifica as colunas necessárias
            col_cod = next((c for c in df.columns if any(k in c for k in ['COD', 'ID']) and 'CIDADE' not in c), df.columns[0])
            col_nome = next((c for c in df.columns if any(k in c for k in ['NOME', 'CLIENTE', 'RAZAO', 'EMPRESA']) and 'CIDADE' not in c), df.columns[1])
            col_cnpj = next((c for c in df.columns if 'CNPJ' in c), None)
            col_seg = next((c for c in df.columns if 'SEGMENTO' in c or 'ATIVIDADE' in c), None)

            # Cria as colunas de trabalho do Sentinela
            df['DISPLAY'] = df[col_cod].astype(str).str.strip() + " - " + df[col_nome].astype(str).str.strip()
            df['COD_S'] = df[col_cod].astype(str).str.strip()
            df['CNPJ_S'] = df[col_cnpj].str.replace(r'\D', '', regex=True) if col_cnpj else ""
            df['SEG_S'] = df[col_seg].str.upper().strip() if col_seg else "NÃO INFORMADO"
            
            return df[['DISPLAY', 'COD_S', 'CNPJ_S', 'SEG_S']]
        except Exception as e:
            st.error(f"Erro ao processar o conteúdo do arquivo: {e}")
            return pd.DataFrame()
    else:
        # Se não achou o arquivo, avisa qual o nome exato ele deveria ter
        st.sidebar.error("❌ Arquivo 'Clientes Ativos.xlsx' não encontrado no GitHub.")
        return pd.DataFrame()

df_clientes = carregar_clientes_ativos()

# 4. CABEÇALHO
st.markdown("<div class='titulo-principal'>SENTINELA 3.0</div><div class='barra-laranja'></div>", unsafe_allow_html=True)

# 5. PAINEL LATERAL
with st.sidebar:
    st.markdown("### ⚙️ Passo 1: Identificação")
    
    if df_clientes.empty:
        st.warning("⚠️ A lista de empresas está vazia. Verifique o arquivo no GitHub.")
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
            with st.spinner("Processando..."):
                try:
                    df_ent, df_sai = extrair_dados_xml_recursivo(xmls, dados_sel['CNPJ_S'])
                    relatorio = gerar_excel_final(df_ent, df_sai, ge, gs, rel_pc, rel_ret, cod_cliente, escolha_reg, is_ret, is_ipi)
                    st.success("✅ Concluído!")
                    st.download_button("💾 BAIXAR RELATÓRIO", data=relatorio, file_name=f"SENTINELA_{cod_cliente}.xlsx", use_container_width=True)
                except Exception as e: st.error(f"Erro: {e}")
else:
    st.warning("Aguardando configurações laterais...")
