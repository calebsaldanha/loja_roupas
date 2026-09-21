import streamlit as st
import pandas as pd
import re
import urllib.parse

# Configuração da página
st.set_page_config(page_title="Vitrine de Peças", layout="wide")
st.title("🛍️ Vitrine Disponível")

@st.cache_data(ttl=60)
def carregar_dados():
    url_csv_drive = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSTYykXVwTQG1NMcrNJ5eKX8QF21qsqaaW6ynaOWFmQsqqu_kU-7mmJEO6Jy4VALKhhoIh24pM0f2L/pub?gid=0&single=true&output=csv"
    df = pd.read_csv(url_csv_drive)
    
    df['Estoque Atual'] = pd.to_numeric(df['Estoque Atual'], errors='coerce')
    df = df[df['Estoque Atual'] > 0]
    return df

def extrair_link_direto_drive(url):
    if pd.isna(url) or not isinstance(url, str):
        return None
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if match:
        # Nova rota usando a API de Thumbnail do Google Drive para evitar o bloqueio de segurança
        return f"https://drive.google.com/thumbnail?id={match.group(1)}&sz=w800"
    return url

try:
    df = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# Substitua pelo seu número de WhatsApp
numero_telemovel = "5511957602740" 

if df.empty:
    st.warning("De momento, não existem peças disponíveis no stock.")
else:
    colunas = st.columns(3)

    for index, row in df.reset_index(drop=True).iterrows():
        with colunas[index % 3]:
            with st.container(border=True):
                
                link_original = row.get('Foto Link', None)
                img_url = extrair_link_direto_drive(link_original)
                
                if img_url:
                    # Usando o parâmetro correto para a sua versão do Streamlit
                    st.image(img_url, use_container_width=True)
                else:
                    st.info("📷 Imagem não disponível")
                    
                st.subheader(row.get('Descrição', 'Sem Descrição'))
                st.write(f"**Tamanho:** {row.get('Tamanho', '-')} | **Cor:** {row.get('Cor', '-')}")
                st.write(f"**Marca:** {row.get('Marca', '-')}")
                st.markdown(f"### R$ {row.get('Preço Venda (R$)', 0):.2f}")
                
                mensagem = f"Olá! Tenho interesse na peça: {row.get('Descrição', '')} (ID: {row.get('ID SKU', '')}, Tamanho: {row.get('Tamanho', '-')}). Ainda está disponível?"
                link_wpp = f"https://wa.me/{numero_telemovel}?text={urllib.parse.quote(mensagem)}"
                
                st.link_button("Tenho Interesse no WhatsApp", link_wpp, use_container_width=True)