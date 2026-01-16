import pandas as pd
from datetime import datetime

def gerar_aba_resumo(writer):
    """Cria a aba de abertura do relatório de auditoria."""
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    dados_resumo = {
        "INFORMAÇÕES DO RELATÓRIO": [
            "SISTEMA", 
            "VERSÃO", 
            "DATA DA AUDITORIA", 
            "STATUS",
            "MÓDULOS ATIVOS"
        ],
        "DETALHES": [
            "SENTINELA FISCAL", 
            "3.0 - MODULAR", 
            data_hora, 
            "CONCLUÍDO COM SUCESSO",
            "ICMS, IPI, PIS/COFINS, DIFAL, RET MG"
        ]
    }
    
    df_resumo = pd.DataFrame(dados_resumo)
    df_resumo.to_excel(writer, sheet_name='RESUMO_GERAL', index=False)
    
    # Ajuste de largura de coluna (opcional, via XlsxWriter)
    worksheet = writer.sheets['RESUMO_GERAL']
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 50)
