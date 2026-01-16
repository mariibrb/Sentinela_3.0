import pandas as pd
import os

# --- CONFIGURAÇÃO DA ABA ---
NOME_ABA = 'IPI_AUDIT'
COLUNAS_ANALISE = ['IPI_CST_ESP', 'IPI_ALQ_ESP', 'IPI_DIAG_CST', 'IPI_DIAG_VALOR', 'IPI_VALOR_COMPLEMENTAR', 'IPI_MOTIVO']

def processar_ipi(df, writer, cod_cliente):
    df_ipi = df.copy()
    
    # Carregamento do Gabarito
    caminho = f"Bases_Tributárias/{cod_cliente}-Bases_Tributarias.xlsx"
    base = pd.read_excel(caminho, dtype=str) if os.path.exists(caminho) else pd.DataFrame()
    if not base.empty: base.columns = [c.upper().strip() for c in base.columns]

    def audit(r):
        ncm = str(r.get('NCM', '')).strip().zfill(8)
        cst_xml = str(r.get('CST-IPI', '')).strip().zfill(2)
        vlr_ipi_xml = float(r.get('VLR-IPI', 0.0))
        vprod = float(r.get('VPROD', 0.0))
        
        # Padrão: Isento (CST 53 / 0%)
        cst_esp = "53"
        alq_esp = 0.0

        if not base.empty and ncm in base['NCM'].values:
            g = base[base['NCM'] == ncm].iloc[0]
            cst_esp = str(g.get('CST_IPI_ESPERADA', '53')).strip().zfill(2)
            alq_esp = float(g.get('ALQ_IPI_ESPERADA', 0.0))

        vlr_devido = round(vprod * (alq_esp / 100), 2)
        comp = max(0.0, round(vlr_devido - vlr_ipi_xml, 2))
        
        diag_cst = "✅ OK" if cst_xml == cst_esp else f"❌ Erro (Esp: {cst_esp})"
        diag_vlr = "✅ OK" if comp < 0.11 else "❌ Divergente"

        return pd.Series([cst_esp, alq_esp, diag_cst, diag_vlr, comp, f"Alíquota IPI: {alq_esp}%"])

    df_ipi[COLUNAS_ANALISE] = df_ipi.apply(audit, axis=1)
    
    cols_xml = [c for c in df_ipi.columns if c != 'Situação Nota' and c not in COLUNAS_ANALISE]
    df_final = pd.concat([df_ipi[cols_xml], df_ipi[['Situação Nota']], df_ipi[COLUNAS_ANALISE]], axis=1)
    df_final.to_excel(writer, sheet_name=NOME_ABA, index=False)
