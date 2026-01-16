import streamlit as st
import os
import pandas as pd

# 1. TENTA IMPORTAR O ESTILO E O MOTOR
try:
    from style import aplicar_estilo_sentinela
    from sentinela_core import extrair_dados_xml_recursivo, gerar_excel_final
except ImportError as e:
    st.error(f"❌ Erro de Estrutura: O arquivo '{e.name}' não foi encontrado na raiz do repositório.")
    st.stop()

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Sentinela 3.0 | Auditoria Fiscal", page_icon="🧡", layout="wide")
aplicar_estilo_sentinela()

# 3. FUNÇÃO INTELIGENTE PARA CARREGAR EMPRESAS (CÓDIGO + NOME)
def carregar_empresas_inteligente():
    arquivos_raiz = os.listdir('.')
    # Busca por planilhas que possam conter a lista de clientes
    caminho_lista = next((f for f in arquivos_raiz if f.endswith(('.xlsx', '.xls')) and 
                         ('LISTAGEM' in f.upper() or 'CLIENTES' in f.upper() or 'EMPRESAS' in f.upper())), None)
    
    if caminho_lista:
        try:
            df = pd.read_excel(caminho_lista, dtype=str)
            cols_originais = df.columns.tolist()
            cols_upper = [str(c).upper().strip() for c in cols_originais]
            df.columns = cols_upper

            # --- LÓGICA DE SELEÇÃO DE COLUNAS ---
            # Procura Código (Evita colunas de cidade ou endereço)
            col_cod = next((c for c in cols_upper if any(k in c for k in ['CODIGO', 'COD.', 'COD', 'ID_EMPRESA']) 
                           and 'CIDADE' not in c and 'MUNICIPIO' not in c), cols_upper[0])
            
            # Procura Nome/Razão Social
            col_nome = next((c for c in cols_upper if any(k in c for k in ['NOME', 'CLIENTE', 'RAZAO', 'EMPRESA']) 
                            and 'CIDADE' not in c), cols_upper[1])
            
            # Procura CNPJ
            col_cnpj = next((c for c in cols_upper if 'CNPJ' in c), None)

            # Limpa os dados e cria o formato: "CÓDIGO - NOME"
            df['DISPLAY'] = df[col_cod].str.strip() + " - " + df[col_nome].str.strip()
            df['COD_SENTINELA'] = df[col_cod].str.strip()
            df['CNPJ_SENTINELA'] = df[col_cnpj].str.strip() if col_cnpj else ""
            
            return df[['DISPLAY', 'COD_SENTINELA', 'CNPJ_SENTINELA']]
        except Exception as e:
            st.error(f"Erro ao ler planilha: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

df_empresas = carregar_empresas_inteligente()

# 4. CABEÇALHO
st.markdown("<div class='titulo-principal'>SENTINELA 3.0</div><div class='barra-laranja'></div>", unsafe_allow_html=True)

# 5. PAINEL LATERAL
with st.sidebar:
    st.markdown("### ⚙️ Configurações da Auditoria")
    
    if not df_empresas.empty:
        # Mostra a lista no formato CÓDIGO - NOME
        lista_display = df_empresas['DISPLAY'].unique().tolist()
        empresa_selecionada = st.selectbox("Selecione a Empresa", lista_display)
        
        # Recupera os dados da linha selecionada
        dados_sel = df_empresas[df_empresas['DISPLAY'] == empresa_selecionada].iloc[0]
        cod_cliente = dados_sel['COD_SENTINELA']
        cnpj_sugerido = dados_sel['CNPJ_SENTINELA']
        
        # Exibe o CNPJ (pode ser editado se necessário)
        cnpj_auditado = st.text_input("CNPJ da Empresa Auditada", value=cnpj_sugerido)
    else:
        st.warning("⚠️ Planilha de Clientes não encontrada ou colunas não identificadas.")
        cod_cliente = st.text_input("Código do Cliente (Manual)")
        cnpj_auditado = st.text_input("CNPJ (Manual)")
    
    regime = st.selectbox("Regime Fiscal", ["Lucro Real", "Lucro Presumido", "Simples Nacional"])
    is_ret = st.toggle("Habilitar Módulo RET MG")
    
    st.markdown("---")
    st.caption("Sentinela Fiscal v3.0 | Inteligência Tributária")

# 6. ÁREA DE UPLOAD
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📥 Arquivos XML")
    xmls = st.file_uploader("Upload de XMLs ou ZIP", type=['zip', 'xml'], accept_multiple_files=True)

with col2:
    st.markdown("### 📑 Arquivos Auxiliares (Opcional)")
    ge = st.file_uploader("Gerencial Entradas (CSV/TXT)", type=['csv', 'txt'], accept_multiple_files=True)
    gs = st.file_uploader("Gerencial Saídas (CSV/TXT)", type=['csv', 'txt'], accept_multiple_files=True)

# 7. EXECUÇÃO
if st.button("🚀 INICIAR AUDITORIA COMPLETA"):
    if xmls and cnpj_auditado and cod_cliente:
        with st.spinner("Auditando..."):
            try:
                # Motor principal
                df_ent, df_sai = extrair_dados_xml_recursivo(xmls, cnpj_auditado)
                
                if not df_ent.empty or not df_sai.empty:
                    relatorio = gerar_excel_final(df_ent, df_sai, None, None, ge, gs, cod_cliente, regime, is_ret)
                    
                    st.markdown("<div class='status-container'>✅ Auditoria Concluída!</div>", unsafe_allow_html=True)
                    st.download_button(
                        label="💾 BAIXAR RELATÓRIO FINAL",
                        data=relatorio,
                        file_name=f"SENTINELA_{cod_cliente}.xlsx",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Nenhum dado encontrado nos XMLs.")
            except Exception as e:
                st.error(f"❌ Erro no processamento: {e}")
    else:
        st.warning("⚠️ Preencha os campos obrigatórios (Empresa e XMLs).")
