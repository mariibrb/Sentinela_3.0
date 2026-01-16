import streamlit as st
import os
import pandas as pd

# 1. TENTA IMPORTAR O ESTILO E O MOTOR
try:
    from style import aplicar_estilo_sentinela
    from sentinela_core import extrair_dados_xml_recursivo, gerar_excel_final
except ImportError as e:
    st.error(f"❌ Erro de Estrutura: O arquivo '{e.name}' não foi encontrado na raiz do repositório.")
    st.info("Certifique-se de que 'style.py' e 'sentinela_core.py' estão na mesma pasta que este arquivo principal.")
    st.stop()

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Sentinela 3.0 | Auditoria Fiscal", page_icon="🧡", layout="wide")
aplicar_estilo_sentinela()

# 3. FUNÇÃO PARA CARREGAR LISTAGEM DE EMPRESAS
def carregar_empresas():
    caminho_lista = "listagem_empresas.xlsx"
    if os.path.exists(caminho_lista):
        try:
            df_lista = pd.read_excel(caminho_lista, dtype=str)
            # Cria uma coluna formatada para o usuário ver: "1001 - Empresa Exemplo"
            df_lista['DISPLAY'] = df_lista['CODIGO'] + " - " + df_lista['NOME']
            return df_lista
        except:
            return pd.DataFrame(columns=['CODIGO', 'NOME', 'DISPLAY', 'CNPJ'])
    return pd.DataFrame(columns=['CODIGO', 'NOME', 'DISPLAY', 'CNPJ'])

df_empresas = carregar_empresas()

# 4. CABEÇALHO PERSONALIZADO
st.markdown("<div class='titulo-principal'>SENTINELA 3.0</div><div class='barra-laranja'></div>", unsafe_allow_html=True)

# 5. PAINEL LATERAL (CONFIGURAÇÕES)
with st.sidebar:
    st.markdown("### ⚙️ Configurações da Auditoria")
    
    if not df_empresas.empty:
        # Se a lista existir, mostra o seletor bonitinho
        empresa_selecionada = st.selectbox("Selecione a Empresa", df_empresas['DISPLAY'].tolist())
        # Extrai apenas o código para o processamento
        cod_cliente = empresa_selecionada.split(" - ")[0]
        # Busca o CNPJ automático da lista se existir
        cnpj_sugerido = df_empresas[df_empresas['CODIGO'] == cod_cliente]['CNPJ'].values[0] if 'CNPJ' in df_empresas.columns else ""
        cnpj_auditado = st.text_input("CNPJ da Empresa Auditada", value=cnpj_sugerido)
    else:
        # Se não houver lista, mantém o modo manual
        st.info("💡 Dica: Suba o arquivo 'listagem_empresas.xlsx' para habilitar a lista de seleção.")
        cod_cliente = st.text_input("Código do Cliente (Ex: 1001)", placeholder="Digite o código...")
        cnpj_auditado = st.text_input("CNPJ da Empresa Auditada", placeholder="Apenas números...")
    
    regime = st.selectbox("Regime Fiscal", ["Lucro Real", "Lucro Presumido", "Simples Nacional"])
    is_ret = st.toggle("Habilitar Módulo RET MG")
    
    st.markdown("---")
    st.caption("Sentinela Fiscal v3.0 - Inteligência Tributária")

# 6. ÁREA DE UPLOAD
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📥 Arquivos XML")
    xmls = st.file_uploader("Arraste os XMLs ou ZIPs aqui", type=['zip', 'xml'], accept_multiple_files=True)

with col2:
    st.markdown("### 📑 Arquivos Auxiliares (Opcional)")
    ge = st.file_uploader("Relatório Gerencial de Entradas (CSV)", type=['csv', 'txt'], accept_multiple_files=True)
    gs = st.file_uploader("Relatório Gerencial de Saídas (CSV)", type=['csv', 'txt'], accept_multiple_files=True)

# 7. EXECUÇÃO DA MÁQUINA
if st.button("🚀 INICIAR AUDITORIA COMPLETA"):
    if not xmls or not cnpj_auditado or not cod_cliente:
        st.warning("⚠️ Verifique se o Código do Cliente, o CNPJ e os XMLs foram fornecidos.")
    else:
        with st.spinner("O Sentinela está processando os dados e consultando os gabaritos..."):
            try:
                # Chama o Core (Motor)
                df_ent, df_sai = extrair_dados_xml_recursivo(xmls, cnpj_auditado)
                
                if df_ent.empty and df_sai.empty:
                    st.error("❌ Nenhum dado válido foi extraído dos XMLs. Verifique os arquivos.")
                else:
                    # Gera o Excel final chamando todos os módulos das subpastas
                    relatorio = gerar_excel_final(df_ent, df_sai, None, None, ge, gs, cod_cliente, regime, is_ret)
                    
                    st.markdown("""
                        <div class='status-container'>
                            <h2 style='color: #FF6F00; margin-top: 0;'>✅ AUDITORIA CONCLUÍDA!</h2>
                            <p>Todos os tributos foram analisados com base nos gabaritos da pasta <b>Bases_Tributárias</b>.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.download_button(
                        label="💾 BAIXAR RELATÓRIO FINAL (.XLSX)",
                        data=relatorio,
                        file_name=f"SENTINELA_3.0_{cod_cliente}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"❌ Erro Crítico durante o processamento: {e}")
