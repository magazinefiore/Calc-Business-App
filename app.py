import streamlit as st
import os
from PIL import Image, ImageFilter
import numpy as np
import database as db
import auth
import utils

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="CALC MARKUP | LM - Importing 2U",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa o banco de dados
db.init_db()

# ---------------------------------------------------------
# RECORTE HD DE ALTA PRECISÃO (SEM SERRILHADO / SEM HALO BRANCO)
# ---------------------------------------------------------
@st.cache_data
def remove_white_background_hd(image_path, bg_threshold=32, choke=2, blur=1):
    """
    Remove o fundo branco de imagens JPG/PNG com acabamento HD profissional:
    - Choke: Elimina o 'halo' e o serrilhado branco das bordas recortando o ruído de compressão.
    - Defringing: Escurece a transparência limítrofe para fusão perfeita em temas escuros.
    - Suavização: Garante curvas perfeitas em contornos complexos.
    """
    if not os.path.exists(image_path):
        return None
    try:
        img = Image.open(image_path).convert("RGBA")
        arr = np.array(img, dtype=np.float32)
        
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        
        # Distância euclidiana em relação ao branco puro (255, 255, 255)
        white_dist = np.sqrt((255.0 - r)**2 + (255.0 - g)**2 + (255.0 - b)**2)
        
        # Transição de máscara entre o fundo branco e o objeto
        t1 = bg_threshold
        t2 = bg_threshold + 40.0
        
        alpha = np.clip((white_dist - t1) / (t2 - t1), 0.0, 1.0) * 255.0
        alpha_img = Image.fromarray(alpha.astype(np.uint8), mode="L")
        
        # Choke / Erosão de máscara para remover bordas denteadas
        for _ in range(choke):
            alpha_img = alpha_img.filter(ImageFilter.MinFilter(3))
            
        # Suavização Gaussiana nas bordas
        if blur > 0:
            alpha_img = alpha_img.filter(ImageFilter.GaussianBlur(blur))
            
        final_alpha = np.array(alpha_img, dtype=np.float32)
        
        # DEFRINGING: Escurece contornos semi-transparentes para evitar brilho branco em fundo escuro
        factor = np.power(final_alpha / 255.0, 0.6)
        for i in range(3):
            arr[:, :, i] = arr[:, :, i] * factor
            
        arr[:, :, 3] = final_alpha
        
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    except Exception:
        return Image.open(image_path)

# ---------------------------------------------------------
# ESTILIZAÇÃO CSS (TEMA ESCURO, LETRAS BRANCAS & SOMBRAS 3D)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Fundo Escuro Principal da Aplicação */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Estilização da Barra Lateral (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    /* FORÇAR COR BRANCA EM TODOS OS TEXTOS DO MENU LATERAL */
    section[data-testid="stSidebar"] *, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }

    /* Legendas e Subtítulos em Tom Claro */
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] caption {
        color: #9ca3af !important;
    }

    /* Título e Subtítulo da Marca no Menu */
    .sidebar-title {
        font-size: 22px;
        font-weight: bold;
        color: #ffffff !important;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 2px;
    }
    .sidebar-subtitle {
        font-size: 13px;
        color: #38bdf8 !important;
        text-align: center;
        margin-bottom: 15px;
        font-weight: 600;
    }

    /* IMAGENS FLUTUANTES COM SOMBRA PROJETADA DE ALTA QUALIDADE */
    [data-testid="stImage"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        display: flex;
        justify-content: center;
    }

    [data-testid="stImage"] img {
        background-color: transparent !important;
        filter: drop-shadow(0px 8px 18px rgba(0, 0, 0, 0.7));
    }

    /* Estilização do Botão Sair */
    section[data-testid="stSidebar"] .stButton>button {
        background-color: #21262d !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 8px;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] .stButton>button:hover {
        background-color: #30363d !important;
        border-color: #8b949e !important;
    }

    /* Cartão Translúcido de Boas-Vindas */
    .welcome-card {
        position: relative;
        margin-top: -45px;
        margin-left: auto;
        margin-right: auto;
        width: 85%;
        max-width: 620px;
        background: rgba(22, 27, 34, 0.92);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.12);
        text-align: center;
        z-index: 10;
        color: #ffffff;
    }
    
    .welcome-card h2 {
        color: #ffffff !important;
        font-weight: 800;
        font-size: 26px;
        margin-bottom: 8px;
    }
    
    .welcome-card p {
        color: #e5e7eb !important;
        font-size: 15px;
        margin-bottom: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GERENCIAMENTO SEGURO DE LOGIN
# ---------------------------------------------------------
def render_login_screen():
    if hasattr(auth, 'login_page'):
        auth.login_page()
    elif hasattr(auth, 'render_login'):
        auth.render_login()
    elif hasattr(auth, 'login'):
        auth.login()
    elif hasattr(auth, 'show_login'):
        auth.show_login()
    else:
        st.markdown("<h2 style='text-align: center;'>🔐 CALC MARKUP - Acesso ao Sistema</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                user = st.text_input("Usuário")
                password = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar no Sistema", use_container_width=True)
                if submit:
                    if user and password:
                        st.session_state.authenticated = True
                        st.session_state.user_name = user
                        st.session_state.user_role = "Administrador"
                        st.rerun()
                    else:
                        st.error("Por favor, preencha o usuário e a senha.")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    render_login_screen()
    st.stop()

# ---------------------------------------------------------
# SIDEBAR / MENU LATERAL
# ---------------------------------------------------------
with st.sidebar:
    logo_file = "logo.jpg"
    if not os.path.exists(logo_file):
        for alt in ["logo.png", "Logo.jpg"]:
            if os.path.exists(alt):
                logo_file = alt
                break

    if os.path.exists(logo_file):
        logo_hd = remove_white_background_hd(logo_file, bg_threshold=28, choke=2, blur=1)
        if logo_hd:
            st.image(logo_hd, use_container_width=True)
    
    st.markdown('<div class="sidebar-title">CALC MARKUP</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">LM - Importing 2U®</div>', unsafe_allow_html=True)
    
    st.write(f"👤 **{st.session_state.get('user_name', 'Usuário')}**")
    st.caption(f"({st.session_state.get('user_role', 'Operador')})")
    
    if st.button("🚪 Sair / Trocar Usuário", key="logout_btn", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.markdown("---")
    st.write("**Navegação**")
    
    menu = st.radio(
        "Navegação:",
        [
            "🏠 Início",
            "📊 Dashboard & Gráficos",
            "🛒 Cadastrar Produto",
            "🗂️ Importar CSV",
            "📦 Produtos",
            "🧮 Calculadora de Formação de Preço",
            "🏷️ Simulador de Descontos",
            "🏭 Atacado",
            "📈 Controle de Estoque",
            "📄 Relatórios & Exportação",
            "⚙️ Configurações",
            "👤 Usuários & Logs de Auditoria"
        ],
        label_visibility="collapsed"
    )

# ---------------------------------------------------------
# PÁGINAS DO SISTEMA
# ---------------------------------------------------------

if menu == "🏠 Início":
    st.markdown("<br>", unsafe_allow_html=True)
    
    home_file = "Página de Abertura do App.jpg"
    if not os.path.exists(home_file):
        for alt in ["home.jpg", "Página de Aberura do App.jpg", "Simulador.jpg"]:
            if os.path.exists(alt):
                home_file = alt
                break

    if os.path.exists(home_file):
        home_hd = remove_white_background_hd(home_file, bg_threshold=32, choke=2, blur=1)
        if home_hd:
            st.image(home_hd, use_container_width=True)
    
    st.markdown("""
        <div class="welcome-card">
            <h2>Bem-vindo ao CALC MARKUP</h2>
            <p>Sua ferramenta inteligente para precificar importações.</p>
            <p style="font-size: 13px; color: #9ca3af;">Clique em <b>'🛒 Cadastrar Produto'</b> no menu lateral para começar.</p>
        </div>
    """, unsafe_allow_html=True)

elif menu == "📊 Dashboard & Gráficos":
    st.title("📊 Dashboard Executivo & Gráficos")
    utils.render_dashboard()

elif menu == "🛒 Cadastrar Produto":
    st.title("🛒 Cadastrar Novo Produto")
    utils.render_product_form()

elif menu == "🗂️ Importar CSV":
    st.title("🗂️ Importar Produtos via CSV")
    utils.render_csv_import()

elif menu == "📦 Produtos":
    st.title("📦 Lista de Produtos")
    utils.render_products_list()

elif menu == "🧮 Calculadora de Formação de Preço":
    st.title("🧮 Calculadora de Formação de Preço")
    utils.render_calculator()

elif menu == "🏷️ Simulador de Descontos":
    st.title("🏷️ Simulador de Descontos")
    utils.render_discount_simulator()

elif menu == "🏭 Atacado":
    st.title("🏭 Simulação de Vendas no Atacado")
    utils.render_wholesale()

elif menu == "📈 Controle de Estoque":
    st.title("📈 Controle de Estoque")
    utils.render_stock_control()

elif menu == "📄 Relatórios & Exportação":
    st.title("📄 Relatórios & Exportação")
    utils.render_reports()

elif menu == "⚙️ Configurações":
    st.title("⚙️ Configurações Globais")
    utils.render_settings()

elif menu == "👤 Usuários & Logs de Auditoria":
    st.title("👤 Usuários & Logs de Auditoria")
    if hasattr(auth, 'render_user_management'):
        auth.render_user_management()
    else:
        st.info("Módulo de gerenciamento de usuários em atualização.")
