import pandas as pd

def gerar_abas_gerenciais(writer, ge, gs):
    """
    Processa os arquivos gerenciais (CSV/TXT) enviados pelo usuário.
    ge: Lista de arquivos de Entrada
    gs: Lista de arquivos de Saída
    """
    # Cabeçalhos padrão para garantir que o Excel fique organizado
    cols_ent = ["NUM_NF", "DATA_EMISSAO", "CNPJ_EMIT", "UF_EMIT", "VLR_NF", "CFOP", "NCM", "QTDE", "VPROD", "CST-ICMS", "VLR-ICMS"]
    cols_sai = ["NF", "DATA_EMISSAO", "CNPJ_DEST", "UF_DEST", "VLR_TOTAL", "CFOP", "NCM", "QTDE", "VITEM", "CST", "ICMS"]

    # Processa Gerencial de Entradas
    if ge:
        try:
            list_df_e = []
            for f in (ge if isinstance(ge, list) else [ge]):
                f.seek(0)
                # Tenta ler com ponto e vírgula (padrão brasileiro)
                df_temp = pd.read_csv(f, sep=None, engine='python', encoding='latin-1', dtype=str)
                list_df_e.append(df_temp)
            
            df_final_e = pd.concat(list_df_e, ignore_index=True)
            df_final_e.to_excel(writer, sheet_name='GERENCIAL_ENTRADAS', index=False)
        except:
            pass
    
    # Processa Gerencial de Saídas
    if gs:
        try:
            list_df_s = []
            for f in (gs if isinstance(gs, list) else [gs]):
                f.seek(0)
                df_temp = pd.read_csv(f, sep=None, engine='python', encoding='latin-1', dtype=str)
                list_df_s.append(df_temp)
            
            df_final_s = pd.concat(list_df_s, ignore_index=True)
            df_final_s.to_excel(writer, sheet_name='GERENCIAL_SAIDAS', index=False)
        except:
            pass
