import pandas as pd
import io, zipfile, xml.etree.ElementTree as ET, re, os, openpyxl
import streamlit as st
from datetime import datetime
from copy import copy

# --- IMPORTAÇÃO BLINDADA (Não trava se faltar arquivo) ---
try:
    from Auditorias.audit_icms import processar_icms
except:
    def processar_icms(*args): pass

try:
    from Auditorias.audit_ipi import processar_ipi
except:
    def processar_ipi(*args): pass

try:
    from Auditorias.audit_pis_cofins import processar_pc
except:
    def processar_pc(*args): pass

try:
    from Auditorias.audit_difal import processar_difal
except:
    def processar_difal(*args): pass

try:
    from Gerenciais.audit_gerencial import gerar_abas_gerenciais
except:
    def gerar_abas_gerenciais(*args): pass

try:
    from Apuracoes.apuracao_difal import gerar_resumo_uf
except:
    def gerar_resumo_uf(*args): pass

# --- FUNÇÕES DE APOIO ---
def safe_float(v):
    if v is None or pd.isna(v): return 0.0
    txt = str(v).strip().upper().replace('R$', '').replace(' ', '').replace('%', '')
    try:
        if ',' in txt and '.' in txt: txt = txt.replace('.', '').replace(',', '.')
        elif ',' in txt: txt = txt.replace(',', '.')
        return round(float(txt), 4)
    except: return 0.0

def buscar_tag_recursiva(tag_alvo, no):
    if no is None: return ""
    for elemento in no.iter():
        if elemento.tag.split('}')[-1] == tag_alvo: return elemento.text if elemento.text else ""
    return ""

def processar_conteudo_xml(content, dados_lista, cnpj_alvo):
    try:
        xml_str = content.decode('utf-8', errors='replace')
        xml_str = re.sub(r'\sxmlns(:\w+)?="[^"]+"', '', xml_str) 
        root = ET.fromstring(xml_str)
        inf = root.find('.//infNFe')
        ide = root.find('.//ide'); emit = root.find('.//emit'); dest = root.find('.//dest')
        
        cnpj_emit = re.sub(r'\D', '', buscar_tag_recursiva('CNPJ', emit))
        tipo_op = "SAIDA" if (cnpj_emit == re.sub(r'\D', '', str(cnpj_alvo))) else "ENTRADA"
        
        for det in root.findall('.//det'):
            prod = det.find('prod'); imp = det.find('imposto')
            icms = det.find('.//ICMS'); ipi = det.find('.//IPI')
            pis = det.find('.//PIS'); cof = det.find('.//COFINS')
            
            linha = {
                "TIPO_SISTEMA": tipo_op, "CHAVE_ACESSO": inf.attrib.get('Id', '')[3:],
                "NUM_NF": buscar_tag_recursiva('nNF', ide), "DATA_EMISSAO": buscar_tag_recursiva('dhEmi', ide),
                "CNPJ_EMIT": cnpj_emit, "CNPJ_DEST": re.sub(r'\D', '', buscar_tag_recursiva('CNPJ', dest)),
                "INDIEDEST": buscar_tag_recursiva('indIEDest', dest),
                "UF_EMIT": buscar_tag_recursiva('UF', emit), "UF_DEST": buscar_tag_recursiva('UF', dest),
                "CFOP": buscar_tag_recursiva('CFOP', prod), "NCM": buscar_tag_recursiva('NCM', prod),
                "VPROD": safe_float(buscar_tag_recursiva('vProd', prod)),
                "CST-ICMS": buscar_tag_recursiva('CST', icms) or buscar_tag_recursiva('CSOSN', icms),
                "BC-ICMS": safe_float(buscar_tag_recursiva('vBC', icms)), 
                "ALQ-ICMS": safe_float(buscar_tag_recursiva('pICMS', icms)),
                "VLR-ICMS": safe_float(buscar_tag_recursiva('vICMS', icms)),
                "VLR-IPI": safe_float(buscar_tag_recursiva('vIPI', ipi)),
                "CST-IPI": buscar_tag_recursiva('CST', ipi),
                "CST-PIS": buscar_tag_recursiva('CST', pis), "VLR-PIS": safe_float(buscar_tag_recursiva('vPIS', pis)),
                "CST-COFINS": buscar_tag_recursiva('CST', cof), "VLR-COFINS": safe_float(buscar_tag_recursiva('vCOFINS', cof)),
                "VAL-DIFAL": safe_float(buscar_tag_recursiva('vICMSUFDest', imp)) + safe_float(buscar_tag_recursiva('vFCPUFDest', imp))
            }
            dados_lista.append(linha)
    except: pass

def extrair_dados_xml_recursivo(files, cnpj):
    dados = []
    for f in (files if isinstance(files, list) else [files]):
        f.seek(0)
        if f.name.endswith('.xml'): processar_conteudo_xml(f.read(), dados, cnpj)
        elif f.name.endswith('.zip'):
            with zipfile.ZipFile(f) as z:
                for name in z.namelist():
                    if name.endswith('.xml'): processar_conteudo_xml(z.read(name), dados, cnpj)
    df = pd.DataFrame(dados)
    if df.empty: return pd.DataFrame(), pd.DataFrame()
    return df[df['TIPO_SISTEMA']=="ENTRADA"].copy(), df[df['TIPO_SISTEMA']=="SAIDA"].copy()

def gerar_excel_final(df_xe, df_xs, ae, as_f, ge, gs, cod, regime, is_ret):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Capa
        try:
            from audit_resumo import gerar_aba_resumo
            gerar_aba_resumo(writer)
        except: pass
        
        # Gerenciais
        gerar_abas_gerenciais(writer, ge, gs)
        
        if not df_xs.empty:
            df_xs['Situação Nota'] = 'Autorizada' 
            processar_icms(df_xs, writer, cod, df_xe)
            processar_ipi(df_xs, writer, cod)
            processar_pc(df_xs, writer, cod, regime)
            processar_difal(df_xs, writer)
            gerar_resumo_uf(df_xs, writer, df_xe)
            
    return output.getvalue()
