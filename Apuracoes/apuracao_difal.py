import pandas as pd

def gerar_resumo_uf(df, writer, df_xe):
    # Filtra apenas o que é interestadual e tem valor de DIFAL
    df_f = df[(df['UF_EMIT'] != df['UF_DEST']) & (df['VAL-DIFAL'] > 0)].copy()
    
    if not df_f.empty:
        resumo = df_f.groupby('UF_DEST').agg({
            'NUM_NF': 'count',
            'VPROD': 'sum',
            'VAL-DIFAL': 'sum'
        }).reset_index()
        
        resumo.columns = ['UF_DESTINO', 'QTD_NOTAS', 'TOTAL_PRODUTOS', 'TOTAL_DIFAL_DEVIDO']
        resumo.to_excel(writer, sheet_name='APURAÇÃO_DIFAL_UF', index=False)
