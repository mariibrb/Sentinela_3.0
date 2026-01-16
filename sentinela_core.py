import pandas as pd
import os

# --- CONFIGURAÇÃO DA ABA ---
NOME_ABA = 'ICMS_AUDIT'
COLUNAS_ANALISE = ['ICMS_CST_ESPERADA', 'ICMS_ALQ_ESPERADA', 'ICMS_DIAG_CST', 'ICMS_DIAG_VALOR', 'ICMS_STATUS_BASE', 'ICMS_VALOR_COMPLEMENTAR', 'ICMS_FUNDAMENTAÇÃO']

def processar_icms(df, writer, cod_cliente, df_entradas=pd.DataFrame()):
    df_i = df.copy()
    
    # --- 1. CARREGAMENTO DO GABARITO (PASTA DE DADOS) ---
    caminho_base = f"Bases_Tributárias/{cod_cliente}-Bases_Tributarias.xlsx"
    base_gabarito = pd.DataFrame()
    if os.path.exists(caminho_base):
        try:
            base_gabarito = pd.read_excel(caminho_base, dtype=str)
            base_gabarito.columns = [str(c).upper().strip() for c in base_gabarito.columns]
            if 'NCM' in base_gabarito.columns:
                base_gabarito['NCM'] = base_gabarito['NCM'].str.replace(r'\D', '', regex=True).str.zfill(8)
        except:
            pass

    def audit_linha(r):
        ncm = str(r.get('NCM', '')).strip().zfill(8)
        cst_xml = str(r.get('CST-ICMS', '')).strip().zfill(2)
        vlr_icms_xml = float(r.get('VLR-ICMS', 0.0))
        bc_icms = float(r.get('BC-ICMS', 0.0))
        
        # Valores Padrão (Caso não ache no gabarito)
        cst_esp = "00"
        alq_esp = 18.0
        status_base = "Regra Geral (18%)"

        # --- CONSULTA AO GABARITO ---
        if not base_gabarito.empty and ncm in base_gabarito['NCM'].values:
            g = base_gabarito[base_gabarito['NCM'] == ncm].iloc[0]
            cst_esp = str(g.get('CST_INTERNA', '00')).strip().zfill(2)
            alq_esp = float(g.get('ALIQ_INTERNA', 18.0))
            status_base = "Localizado no Gabarito"

        # --- CÁLCULOS ---
        vlr_icms_devido = round(bc_icms * (alq_esp / 100), 2)
        comp = max(0.0, round(vlr_icms_devido - vlr_icms_xml, 2))

        # --- DIAGNÓSTICOS ---
        diag_cst = "✅ OK" if cst_xml == cst_esp else f"❌ Erro (Esp: {cst_esp})"
        diag_vlr = "✅ OK" if comp < 0.11 else f"❌ Faltou R$ {comp}"
        
        motivo = f"NCM {ncm} auditado com alíquota de {alq_esp}%."
        if comp > 0:
            motivo = f"Divergência: Alíquota esperada {alq_esp}% resultaria em R$ {vlr_icms_devido}."

        return pd.Series([cst_esp, alq_esp, diag_cst, diag_vlr, status_base, comp, motivo])

    # Executa a auditoria
    df_i[COLUNAS_ANALISE] = df_i.apply(audit_linha, axis=1)

    # --- ORGANIZAÇÃO FINAL (PADRÃO SENTINELA) ---
    cols_xml = [c for c in df_i.columns if c != 'Situação Nota' and c not in COLUNAS_ANALISE]
    col_status = ['Situação Nota'] if 'Situação Nota' in df_i.columns else []
    
    df_final = pd.concat([df_i[cols_xml], df_i[col_status], df_i[COLUNAS_ANALISE]], axis=1)
    
    # Gravação
    df_final.to_excel(writer, sheet_name=NOME_ABA, index=False)
