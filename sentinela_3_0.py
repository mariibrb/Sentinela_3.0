import streamlit as st
from style import aplicar_estilo_sentinela
from sentinela_core import extrair_dados_xml_recursivo, gerar_excel_final

st.set_page_config(page_title="Sentinela 3.0", layout="wide")
aplicar_estilo_sentinela()

st.markdown("<div class='titulo-principal'>SENTINELA 3.0</div><div class='barra-laranja'></div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Painel de Auditoria")
    cod_cliente = st.text_input("Código do Cliente")
    cnpj_auditado = st.text_input("CNPJ da Empresa")
    regime = st.selectbox("Regime", ["Lucro Real", "Lucro Presumido"])
    is_ret = st.toggle("RET MG")

xmls = st.file_uploader("Upload de XMLs", type=['zip', 'xml'], accept_multiple_files=True)

if st.button("🚀 INICIAR ANÁLISE"):
    if xmls and cnpj_auditado:
        with st.spinner("Auditando..."):
            df_e, df_s = extrair_dados_xml_recursivo(xmls, cnpj_auditado)
            relat = gerar_excel_final(df_e, df_s, None, None, None, None, cod_cliente, regime, is_ret)
            st.markdown("<div class='status-container'>✅ Auditoria Finalizada!</div>", unsafe_allow_html=True)
            st.download_button("💾 BAIXAR EXCEL", relat, f"Audit_{cod_cliente}.xlsx")
