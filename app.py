import streamlit as st
import pandas as pd
import re
import urllib.parse

# ==========================================
# CONFIGURAÇÃO DE IDENTIDADE VISUAL
# ==========================================
URL_BANNER_GITHUB = "https://raw.githubusercontent.com/calebsaldanha/loja_roupas/main/Gemini_Generated_Image_gr7w93gr7w93gr7w.jpg"

st.set_page_config(
    page_title="SALDANHA OUTLET | Moda Exclusiva",
    layout="wide"
)

# CSS Ajustado para Dark Mode e Imagem de Fundo na Tela Inteira
st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(20, 5, 15, 0.8), rgba(20, 5, 15, 0.9)), url("{URL_BANNER_GITHUB}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    .header-text {{
        text-align: center;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }}
    .brand-title {{
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: 4px;
        color: #ffffff;
        text-transform: uppercase;
        margin-bottom: -10px;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
    }}
    .brand-subtitle {{
        font-size: 1.5rem;
        letter-spacing: 8px;
        color: #d896a8;
        font-weight: 600;
        text-transform: uppercase;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.7);
        margin-bottom: 20px;
    }}
    
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background-color: rgba(30, 10, 20, 0.6);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, border-color 0.3s ease;
        padding: 10px;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        transform: translateY(-5px);
        border-color: rgba(216, 150, 168, 0.5);
    }}
    
    div[data-testid="stVerticalBlockBorderWrapper"] p, 
    div[data-testid="stVerticalBlockBorderWrapper"] h3 {{
        color: #f0f0f0 !important;
    }}

    .stButton button {{
        background-color: #8c2452;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.2s ease;
    }}
    .stButton button:hover {{
        background-color: #6a1a3d;
        border-color: rgba(255,255,255,0.5);
    }}
    
    .preco-tag {{
        font-size: 1.4rem;
        font-weight: 900;
        color: #e5a4b5;
        margin: 5px 0 15px 0;
    }}

    section[data-testid="stSidebar"] {{
        background-color: rgba(20, 5, 15, 0.85);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }}
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] h3 {{
        color: #e0e0e0;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-text">
        <div class="brand-title">Saldanha</div>
        <div class="brand-subtitle">Outlet</div>
    </div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados():
    url_csv_drive = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRSTYykXVwTQG1NMcrNJ5eKX8QF21qsqaaW6ynaOWFmQsqqu_kU-7mmJEO6Jy4VALKhhoIh24pM0f2L/pub?gid=0&single=true&output=csv"
    df = pd.read_csv(url_csv_drive)
    df['Estoque Atual'] = pd.to_numeric(df['Estoque Atual'], errors='coerce')
    df = df[df['Estoque Atual'] > 0]
    return df

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

try:
    df = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = {}

numero_telemovel = "5511957602740" 

# ==========================================
# BARRA LATERAL (FILTROS E CARRINHO CORRIGIDO)
# ==========================================
with st.sidebar:
    st.markdown("### 🔍 Filtrar Vitrine")
    
    categorias_disponiveis = ["Todas"] + sorted(df['Categoria'].dropna().unique().tolist())
    categoria_selecionada = st.selectbox("Categoria", categorias_disponiveis)
    
    tamanhos_disponiveis = ["Todos"] + sorted(df['Tamanho'].dropna().astype(str).unique().tolist())
    tamanho_selecionado = st.selectbox("Tamanho", tamanhos_disponiveis)
    
    marcas_disponiveis = ["Todas"] + sorted(df['Marca'].dropna().unique().tolist())
    marca_selecionada = st.selectbox("Marca", marcas_disponiveis)
    
    st.divider()
    
    st.markdown("### 🛒 Seu Carrinho")
    
    if not st.session_state.carrinho:
        st.info("O seu carrinho está vazio.")
    else:
        total_geral = 0
        
        for sku, qtd in st.session_state.carrinho.items():
            peca = df[df['ID SKU'] == sku]
            if not peca.empty:
                row_peca = peca.iloc[0]
                nome = row_peca.get('Descrição', 'Peça')
                preco = float(row_peca.get('Preço Venda (R$)', 0))
                subtotal = preco * qtd
                total_geral += subtotal
                
                st.markdown(f"**{nome}**")
                st.caption(f"Tam: {row_peca.get('Tamanho', '-')} | {row_peca.get('Marca', '-')}")
                st.text(f"{qtd}x R$ {preco:.2f} = R$ {subtotal:.2f}")
                
                col_sub, col_add, col_del = st.columns(3)
                
                # Botão Subtrair (-) corrigido
                if col_sub.button("➖", key=f"sub_{sku}"):
                    if st.session_state.carrinho[sku] > 1:
                        st.session_state.carrinho[sku] -= 1
                    else:
                        del st.session_state.carrinho[sku]
                    st.rerun()
                
                # Botão Somar (+)
                if col_add.button("➕", key=f"add_{sku}"):
                    estoque_max = int(row_peca.get('Estoque Atual', 1))
                    if st.session_state.carrinho[sku] < estoque_max:
                        st.session_state.carrinho[sku] += 1
                    else:
                        st.warning("Estoque máximo.")
                    st.rerun()
                    
                # Botão Deletar (Lixeira) corrigido
                if col_del.button("🗑️", key=f"del_{sku}"):
                    del st.session_state.carrinho[sku]
                    st.rerun()
                
                st.divider()
            
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
# FILTRAGEM DOS DADOS
# ==========================================
df_filtrado = df.copy()
if categoria_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria_selecionada]
if tamanho_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Tamanho'].astype(str) == tamanho_selecionado]
if marca_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Marca'] == marca_selecionada]

# ==========================================
# AGRUPAMENTO DE PRODUTOS E VITRINE
# ==========================================
if df_filtrado.empty:
    st.warning("Nenhuma peça encontrada com os filtros selecionados.")
else:
    coluna_link_principal = 'Foto Nova Link' if 'Foto Nova Link' in df_filtrado.columns else 'Foto Link'
    df_filtrado['Foto_Usada'] = df_filtrado[coluna_link_principal].fillna(df_filtrado.get('Foto Link', ''))
    
    df_filtrado['Cor_Grupo'] = df_filtrado['Cor'].fillna('-')
    df_filtrado['Marca_Grupo'] = df_filtrado['Marca'].fillna('-')
    df_filtrado['Desc_Grupo'] = df_filtrado['Descrição'].fillna('Sem Descrição')

    grupos = df_filtrado.groupby(['Desc_Grupo', 'Cor_Grupo', 'Marca_Grupo', 'Preço Venda (R$)', 'Foto_Usada'])

    produtos_agrupados = []
    for (desc, cor, marca, preco, foto), dados_grupo in grupos:
        produtos_agrupados.append({
            'desc': desc,
            'cor': cor,
            'marca': marca,
            'preco': preco,
            'foto': foto if foto != '' else None,
            'variacoes': dados_grupo.to_dict('records')
        })

    colunas = st.columns(3)

    for i, prod in enumerate(produtos_agrupados):
        with colunas[i % 3]:
            with st.container(border=True):
                
                id_imagem = extrair_id_drive(prod['foto'])
                if id_imagem:
                    url_img_direta = f"https://drive.google.com/thumbnail?id={id_imagem}&sz=w800"
                    st.image(url_img_direta, width="stretch")
                else:
                    st.info("📷 Sem imagem")
                    
                st.markdown(f"### {prod['desc']}")
                st.markdown(f" **Marca:** {prod['marca']} | **Cor:** {prod['cor']}")
                st.markdown(f"<div class='preco-tag'>R$ {prod['preco']:.2f}</div>", unsafe_allow_html=True)
                
                mapa_tamanhos = {str(v.get('Tamanho', '-')): v for v in prod['variacoes']}
                lista_tamanhos = list(mapa_tamanhos.keys())
                
                tamanho_escolhido = st.selectbox(
                    "Tamanho:", 
                    lista_tamanhos, 
                    key=f"sel_tam_{i}"
                )
                
                item_escolhido = mapa_tamanhos[tamanho_escolhido]
                sku_atual = item_escolhido.get('ID SKU')
                estoque_atual = int(item_escolhido.get('Estoque Atual', 1))
                
                st.caption(f"📦 Em estoque: **{estoque_atual}** unidade(s)")
                
                qtd_carrinho = st.session_state.carrinho.get(sku_atual, 0)
                
                if st.button("🛒 Adicionar ao Carrinho", key=f"btn_add_{i}", width="stretch"):
                    if qtd_carrinho < estoque_atual:
                        st.session_state.carrinho[sku_atual] = qtd_carrinho + 1
                        st.success(f"Tamanho {tamanho_escolhido} adicionado!")
                        st.rerun()
                    else:
                        st.error("Estoque máximo atingido.")
