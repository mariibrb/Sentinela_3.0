import streamlit as st
import os
import pandas as pd

# 1. TENTA IMPORTAR O ESTILO E O MOTOR
try:
    from style import aplicar_estilo_sentinela
    from sentinela_core import extrair_dados_xml_recursivo, gerar_excel_final
except ImportError as e:
    st.error(f"❌ Erro de Estrutura: O arquivo '{e.name}' não foi encontrado na raiz.")
    st.stop()

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Sentinela 3.0 | Auditoria Fiscal", page_icon="🧡", layout="wide")
aplicar_estilo_sentinela()

# 3. FUNÇÃO INTELIGENTE PARA CARREGAR EMPRESAS
def carregar_empresas_inteligente():
    arquivos_raiz = os.listdir('.')
    caminho_lista = next((f for f in arquivos_raiz if f.endswith(('.xlsx', '.xls')) and 
                         ('LISTAGEM' in f.upper() or 'CLIENTES' in f.upper() or 'EMPRESAS' in f.upper())), None)
    
    if caminho_lista:
        try:
            df = pd.read_excel(caminho_lista, dtype=str)
            cols_upper = [str(c).upper().strip() for c in df.columns]
            df.columns = cols_upper

            col_cod = next((c for c in cols_upper if any(k in c for k in ['CODIGO', 'COD.', 'COD', 'ID_EMPRESA']) 
                           and 'CIDADE' not in c and 'MUNICIPIO' not in c), cols_upper[0])
            
            col_nome = next((c for c in cols_upper if any(k in c for k in ['NOME', 'CLIENTE', 'RAZAO', 'EMPRESA']) 
                            and 'CIDADE' not in c), cols_upper[1])
            
            col_cnpj = next((c for c in cols_upper if 'CNPJ' in c), None)

            df['DISPLAY'] = df[col_cod].str.strip() + " - " + df[col_nome].str.strip()
            df['COD_SENTINELA'] = df[col_cod].str.strip()
            df['CNPJ_SENTINELA'] = df[col_cnpj].str.strip() if col_cnpj else ""
            
            return df[['DISPLAY', 'COD_SENTINELA', 'CNPJ_SENTINELA']]
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df_empresas = carregar_empresas_inteligente()

# 4. CABEÇALHO
st.markdown("<div class='titulo-principal'>SENTINELA 3.0</div><div class='barra-laranja'></div>", unsafe_allow_html=True)

# 5. PAINEL LATERAL COM TRAVAS DE SELEÇÃO OBRIGATÓRIA
with st.sidebar:
    st.markdown("### ⚙️ Configurações da Auditoria")
    
    # --- PASSO 1: SELEÇÃO DA EMPRESA ---
    opcoes_emp = ["-- SELECIONE UMA EMPRESA --"]
    if not df_empresas.empty:
        opcoes_emp.extend(df_empresas['DISPLAY'].unique().tolist())
    
    escolha_emp = st.selectbox("1. Empresa", options=opcoes_emp)

    # Variáveis de controle de fluxo
    empresa_ok = escolha_emp != "-- SELECIONE UMA EMPRESA --"
    regime_ok = False
    cod_cliente = None
    regime_selecionado = None

    if not empresa_ok:
        st.info("👆 Selecione a empresa para continuar.")
    else:
        dados_sel = df_empresas[df_empresas['DISPLAY'] == escolha_emp].iloc[0]
        cod_cliente = dados_sel['COD_SENTINELA']
        cnpj_sugerido = dados_sel['CNPJ_SENTINELA']
        
        st.text_input("2. CNPJ da Empresa", value=cnpj_sugerido, disabled=True)
        
        # --- PASSO 2: SELEÇÃO DO REGIME (OBRIGATÓRIO) ---
        opcoes_reg = ["-- SELECIONE O REGIME --", "Lucro Real", "Lucro Presumido", "Simples Nacional"]
        escolha_reg = st.selectbox("3. Regime Fiscal", options=opcoes_reg)
        
        if escolha_reg == "-- SELECIONE O REGIME --":
            st.info("👆 Defina o regime fiscal para liberar os arquivos.")
        else:
            regime_ok = True
            regime_selecionado = escolha_reg
            is_ret = st.toggle("4. Habilitar Módulo RET MG")
        
    st.markdown("---")
    st.caption("Sentinela Fiscal v3.0")

# 6. ÁREA DE UPLOAD (Só aparece se Empresa E Regime forem selecionados)
if empresa_ok and regime_ok:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📥 Arquivos XML")
        xmls = st.file_uploader("Upload de XMLs ou ZIP", type=['zip', 'xml'], accept_multiple_files=True)

    with col2:
        st.markdown("### 📑 Arquivos Auxiliares (Opcional)")
        ge = st.file_uploader("Gerencial Entradas (CSV/TXT)", type=['csv', 'txt'], accept_multiple_files=True)
        gs = st.file_uploader("Gerencial Saídas (CSV/TXT)", type=['csv', 'txt'], accept_multiple_files=True)

    # 7. BOTÃO DE EXECUÇÃO
    if st.button("🚀 INICIAR AUDITORIA COMPLETA"):
        if xmls:
            with st.spinner("Auditando..."):
                try:
                    df_ent, df_sai = extrair_dados_xml_recursivo(xmls, dados_sel['CNPJ_SENTINELA'])
                    if not df_ent.empty or not df_sai.empty:
                        relatorio = gerar_excel_final(df_ent, df_sai, None, None, ge, gs, cod_cliente, regime_selecionado, is_ret)
                        st.markdown("<div class='status-container'>✅ Auditoria Concluída!</div>", unsafe_allow_html=True)
                        st.download_button(label="💾 BAIXAR RELATÓRIO", data=relatorio, file_name=f"SENTINELA_{cod_cliente}.xlsx", use_container_width=True)
                    else:
                        st.error("❌ Nenhum dado encontrado nos XMLs.")
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
        else:
            st.warning("⚠️ Carregue os XMLs antes de iniciar.")
else:
    # Mensagem de orientação no corpo da página
    st.warning("Aguardando preenchimento das configurações (Empresa e Regime) no menu lateral.")
