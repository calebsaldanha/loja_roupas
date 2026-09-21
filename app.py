import streamlit as st
import pandas as pd
import re
import urllib.parse
import requests # Nova biblioteca para baixar as imagens

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

# Extrai apenas o ID do link
def extrair_id_drive(url):
    if pd.isna(url) or not isinstance(url, str):
        return None
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    return match.group(1) if match else None

# Baixa a imagem nos bastidores (com cache para não deixar o site lento)
@st.cache_data(show_spinner=False, ttl=3600)
def carregar_imagem_bytes(id_imagem):
    url = f"https://drive.google.com/uc?export=download&id={id_imagem}"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resposta = requests.get(url, headers=headers, timeout=10)
        if resposta.status_code == 200:
            return resposta.content
    except:
        return None
    return None

try:
    df = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# Seu número
numero_telemovel = "5511957602740" 

if df.empty:
    st.warning("De momento, não existem peças disponíveis no stock.")
else:
    colunas = st.columns(3)

    for index, row in df.reset_index(drop=True).iterrows():
        with colunas[index % 3]:
            with st.container(border=True):
                
                id_imagem = extrair_id_drive(row.get('Foto Link', None))
                
                if id_imagem:
                    img_bytes = carregar_imagem_bytes(id_imagem)
                    if img_bytes:
                        # width="stretch" resolve os avisos amarelos no terminal
                        st.image(img_bytes, width="stretch")
                    else:
                        st.info("📷 Imagem indisponível no Drive")
                else:
                    st.info("📷 Sem link cadastrado")
                    
                st.subheader(row.get('Descrição', 'Sem Descrição'))
                st.write(f"**Tamanho:** {row.get('Tamanho', '-')} | **Cor:** {row.get('Cor', '-')}")
                st.write(f"**Marca:** {row.get('Marca', '-')}")
                st.markdown(f"### R$ {row.get('Preço Venda (R$)', 0):.2f}")
                
                mensagem = f"Olá! Tenho interesse na peça: {row.get('Descrição', '')} (ID: {row.get('ID SKU', '')}, Tamanho: {row.get('Tamanho', '-')}). Ainda está disponível?"
                link_wpp = f"https://wa.me/{numero_telemovel}?text={urllib.parse.quote(mensagem)}"
                
                st.link_button("Tenho Interesse no WhatsApp", link_wpp, use_container_width=True)
