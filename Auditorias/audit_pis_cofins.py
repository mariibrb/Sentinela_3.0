import pandas as pd
import os

# --- CONFIGURAÇÃO DA ABA ---
NOME_ABA = 'PIS_COFINS_AUDIT'
COLUNAS_ANALISE = ['PC_CST_ESP', 'PIS_ALQ_ESP', 'COF_ALQ_ESP', 'PC_DIAG_CST', 'PC_VALOR_COMPLEMENTAR', 'PC_FUNDAMENTAÇÃO']

def processar_pc(df, writer, cod_cliente, regime):
    df_pc = df.copy()
    
    # Carregamento do Gabarito
    path = f"Bases_Tributárias/{cod_cliente}-Bases_Tributarias.xlsx"
    base = pd.read_excel(path, dtype=str) if os.path.exists(path) else pd.DataFrame()
    if not base.empty: base.columns = [c.upper().strip() for c in base.columns]

    def audit(r):
        ncm = str(r.get('NCM', '')).strip().zfill(8)
        vprod = float(r.get('VPROD', 0.0))
        
        # Lógica por Regime
        if regime == "Lucro Real":
            alq_pis_padrao, alq_cof_padrao = 1.65, 7.6
            cst_padrao = "01"
        else:
            alq_pis_padrao, alq_cof_padrao = 0.65, 3.0
            cst_padrao = "01"

        # Soberania do Gabarito (Monofásicos, Alíquota Zero, etc)
        if not base.empty and ncm in base['NCM'].values:
            g = base[base['NCM'] == ncm].iloc[0]
            cst_esp = str(g.get('CST_PC_ESPERADA', cst_padrao)).zfill(2)
            alq_p = float(g.get('ALQ_PIS_ESPERADA', alq_pis_padrao))
            alq_c = float(g.get('ALQ_COF_ESPERADA', alq_cof_padrao))
        else:
            cst_esp, alq_p, alq_c = cst_padrao, alq_pis_padrao, alq_cof_padrao

        vlr_p_xml = float(r.get('VLR-PIS', 0.0))
        vlr_c_xml = float(r.get('VLR-COFINS', 0.0))
        
        vlr_p_devido = round(vprod * (alq_p / 100), 2)
        vlr_c_devido = round(vprod * (alq_c / 100), 2)
        
        comp = max(0.0, round((vlr_p_devido + vlr_c_devido) - (vlr_p_xml + vlr_c_xml), 2))
        
        return pd.Series([cst_esp, alq_p, alq_c, "✅ OK" if str(r.get('CST-PIS','')) == cst_esp else "❌ Erro", comp, f"Regime: {regime}"])

    df_pc[COLUNAS_ANALISE] = df_pc.apply(audit, axis=1)
    
    cols_xml = [c for c in df_pc.columns if c != 'Situação Nota' and c not in COLUNAS_ANALISE]
    df_final = pd.concat([df_pc[cols_xml], df_pc[['Situação Nota']], df_pc[COLUNAS_ANALISE]], axis=1)
    df_final.to_excel(writer, sheet_name=NOME_ABA, index=False)
