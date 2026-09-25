import streamlit as st
import pandas as pd
import re
import urllib.parse
import requests
import io
from PIL import Image

# Configuração da página e layout elegante
st.set_page_config(
    page_title="Saldanha Outlet | Vitrine Online",
    page_icon="🛍️",
    layout="wide"
)

# Estilização CSS customizada para deixar o visual mais moderno e profissional
st.markdown("""
    <style>
    .main {
        background-color: #fafafa;
    }
    h1 {
        color: #111111;
        font-weight: 700;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        border: 1px solid #eaeaea;
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Título Principal da Loja
st.title("🛍️ Saldanha Outlet — Peças Novas com Etiqueta")
st.markdown("Explore o nosso catálogo, adicione os itens ao carrinho e feche a compra diretamente pelo WhatsApp de forma rápida!")
st.divider()

@st.cache_data(ttl=60)
def carregar_dados():
    url_csv_drive = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSTYykXVwTQG1NMcrNJ5eKX8QF21qsqaaW6ynaOWFmQsqqu_kU-7mmJEO6Jy4VALKhhoIh24pM0f2L/pub?gid=0&single=true&output=csv"
    df = pd.read_csv(url_csv_drive)
    
    df['Estoque Atual'] = pd.to_numeric(df['Estoque Atual'], errors='coerce')
    df = df[df['Estoque Atual'] > 0]
    return df

# Extrai o ID do link do Google Drive
def extrair_id_drive(url):
    if pd.isna(url) or not isinstance(url, str):
        return None
    match_d = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if match_d:
        return match_d.group(1)
    match_id = re.search(r'id=([a-zA-Z0-9-_]+)', url)
    if match_id:
        return match_id.group(1)
    return None

# Baixa a imagem do Drive via bytes com validação
@st.cache_data(show_spinner=False, ttl=3600)
def carregar_imagem_bytes(id_imagem):
    url = f"https://drive.google.com/uc?export=download&id={id_imagem}"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resposta = requests.get(url, headers=headers, timeout=10)
        if resposta.status_code == 200:
            img = Image.open(io.BytesIO(resposta.content))
            img.verify()
            return resposta.content
    except Exception:
        return None
    return None

try:
    df = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# Inicializa o Carrinho na sessão do usuário
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = {}

# Seu número de telemóvel (WhatsApp)
numero_telemovel = "5511957602740" 

# ==========================================
# BARRA LATERAL (FILTROS E CARRINHO)
# ==========================================
with st.sidebar:
    st.header("🔍 Filtros de Busca")
    
    # Filtro de Categoria
    categorias_disponiveis = ["Todas"] + sorted(df['Categoria'].dropna().unique().tolist())
    categoria_selecionada = st.selectbox("Filtrar por Categoria", categorias_disponiveis)
    
    # Filtro de Tamanho
    tamanhos_disponiveis = ["Todos"] + sorted(df['Tamanho'].dropna().astype(str).unique().tolist())
    tamanho_selecionado = st.selectbox("Filtrar por Tamanho", tamanhos_disponiveis)
    
    st.divider()
    
    st.subheader("🛒 Seu Carrinho")
    
    if not st.session_state.carrinho:
        st.info("O carrinho está vazio.")
    else:
        total_geral = 0
        itens_para_remover = []
        
        for sku, qtd in st.session_state.carrinho.items():
            peca = df[df['ID SKU'] == sku]
            if not peca.empty:
                row_peca = peca.iloc[0]
                nome = row_peca.get('Descrição', 'Peça')
                preco = float(row_peca.get('Preço Venda (R$)', 0))
                subtotal = preco * qtd
                total_geral += subtotal
                
                st.write(f"**{nome}** (Tam: {row_peca.get('Tamanho', '-')})")
                st.text(f"Qtd: {qtd} x R$ {preco:.2f} = R$ {subtotal:.2f}")
                
                col_sub, col_add, col_del = st.columns(3)
                if col_sub.button("➖", key=f"sub_{sku}"):
                    if st.session_state.carrinho[sku] > 1:
                        st.session_state.carrinho[sku] -= 1
                    else:
                        itens_para_remover.append(sku)
                    st.rerun()
                
                if col_add.button("➕", key=f"add_{sku}"):
                    estoque_max = int(row_peca.get('Estoque Atual', 1))
                    if st.session_state.carrinho[sku] < estoque_max:
                        st.session_state.carrinho[sku] += 1
                    else:
                        st.warning("Limite de estoque.")
                    st.rerun()
                    
                if col_del.button("🗑️", key=f"del_{sku}"):
                    itens_para_remover.append(sku)
                    st.rerun()
                
                st.divider()

        for sku in itens_para_remover:
            del st.session_state.carrinho[sku]
            
        if st.session_state.carrinho:
            st.markdown(f"### Total: R$ {total_geral:.2f}")
            
            msg_wpp = "Olá! Gostaria de finalizar o pedido com os seguintes itens:\n\n"
            for sku, qtd in st.session_state.carrinho.items():
                peca = df[df['ID SKU'] == sku].iloc[0]
                sub = float(peca.get('Preço Venda (R$)', 0)) * qtd
                msg_wpp += f"- {qtd}x {peca.get('Descrição')} (ID: {sku}, Tam: {peca.get('Tamanho')}) - R$ {sub:.2f}\n"
            msg_wpp += f"\n*Valor Total: R$ {total_geral:.2f}*\nPode confirmar a disponibilidade?"
            
            link_finalizar = f"https://wa.me/{numero_telemovel}?text={urllib.parse.quote(msg_wpp)}"
            st.link_button("📲 Finalizar no WhatsApp", link_finalizar, width="stretch")
            
            if st.button("Limpar Carrinho", width="stretch"):
                st.session_state.carrinho = {}
                st.rerun()

# ==========================================
# APLICAÇÃO DOS FILTROS NO DATAFRAME
# ==========================================
df_filtrado = df.copy()
if categoria_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria_selecionada]
if tamanho_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Tamanho'].astype(str) == tamanho_selecionado]

# ==========================================
# CORPO DA PÁGINA (VITRINE COM LAYOUT MELHORADO)
# ==========================================
if df_filtrado.empty:
    st.warning("Nenhuma peça encontrada com os filtros selecionados.")
else:
    colunas = st.columns(3)

    for index, row in df_filtrado.reset_index(drop=True).iterrows():
        with colunas[index % 3]:
            with st.container(border=True):
                
                coluna_link = 'Foto Nova Link' if 'Foto Nova Link' in row and pd.notna(row['Foto Nova Link']) else 'Foto Link'
                id_imagem = extrair_id_drive(row.get(coluna_link, None))
                
                if id_imagem:
                    img_bytes = carregar_imagem_bytes(id_imagem)
                    if img_bytes:
                        st.image(img_bytes, width="stretch")
                    else:
                        st.info("📷 Imagem indisponível no Drive")
                else:
                    st.info("📷 Sem link cadastrado")
                    
                st.subheader(row.get('Descrição', 'Sem Descrição'))
                
                # Tags de informações estilizadas
                st.markdown(f"🏷️ **Marca:** {row.get('Marca', '-')}  \n"
                            f"📐 **Tamanho:** {row.get('Tamanho', '-')} | 🎨 **Cor:** {row.get('Cor', '-')}")
                
                st.markdown(f"### R$ {row.get('Preço Venda (R$)', 0):.2f}")
                
                sku_atual = row.get('ID SKU')
                
                if st.button("🛒 Adicionar ao Carrinho", key=f"btn_{sku_atual}", width="stretch"):
                    estoque_atual = int(row.get('Estoque Atual', 1))
                    qtd_atual_carrinho = st.session_state.carrinho.get(sku_atual, 0)
                    
                    if qtd_atual_carrinho < estoque_atual:
                        st.session_state.carrinho[sku_atual] = qtd_atual_carrinho + 1
                        st.success("Adicionado!")
                        st.rerun()
                    else:
                        st.error("Estoque máximo atingido.")
