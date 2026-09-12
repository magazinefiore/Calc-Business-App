import streamlit as st
import os
from PIL import Image
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
# CARREGAMENTO DE IMAGEM COM TRANSPARÊNCIA FORÇADA E CACHE LIMPO
# ---------------------------------------------------------
def load_png_image(image_filename):
    """
    Carrega a imagem do disco ignorando o cache, remove fundos brancos 
    e garante transparência nativa para o tema escuro.
    """
    base_name = os.path.splitext(image_filename)[0]
    extensions = ['.png', '.PNG', '.jpg', '.JPG', '.jpeg']
    
    for ext in extensions:
        file_path = base_name + ext
        if os.path.exists(file_path):
            try:
                img = Image.open(file_path).convert("RGBA")
                width, height = img.size
                pixels = img.load()
                
                # Remove qualquer tom branco ou cinza muito claro remanescente
                for y in range(height):
                    for x in range(width):
                        r, g, b, a = pixels[x, y]
                        if r > 225 and g > 225 and b > 225:
                            pixels[x, y] = (255, 255, 255, 0)
                            
                return img
            except Exception:
                pass
    return None

# ---------------------------------------------------------
# ESTILIZAÇÃO CSS (TRANSPARÊNCIA E SOBREPOSIÇÃO DO CARTÃO)
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

    /* ELIMINA QUALQUER FUNDO BRANCO NAS IMAGENS DO STREAMLIT */
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
        border-radius: 12px;
    }

    /* CARTÃO FLUTUANTE TRANSLÚCIDO E SOBREPOSTO */
    .welcome-overlay-card {
        position: relative;
        margin-top: -95px; /* Puxa o cartão para cima, sobrepondo a imagem */
        margin-left: auto;
        margin-right: auto;
        width: 80%;
        max-width: 580px;
        background: rgba(22, 27, 34, 0.70); /* Alta transparência (Vidro fumê) */
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.18);
        text-align: center;
        z-index: 99;
        color: #ffffff;
    }
    
    .welcome-overlay-card h2 {
        color: #ffffff !important;
        font-weight: 800;
        font-size: 24px;
        margin-bottom: 6px;
    }
    
    .welcome-overlay-card p {
        color: #e5e7eb !important;
        font-size: 14px;
        margin-bottom: 4px;
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
                user = st.text_input("Usuário", value="admin")
                password = st.text_input("Senha", type="password", value="admin123")
                submit = st.form_submit_button("Entrar no Sistema", use_container_width=True)
                if submit:
                    if user == "admin" and password == "admin123":
                        st.session_state.authenticated = True
                        st.session_state.user_name = user
                        st.session_state.user_role = "Administrador"
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    render_login_screen()
    st.stop()

# ---------------------------------------------------------
# SIDEBAR / MENU LATERAL
# ---------------------------------------------------------
with st.sidebar:
    logo_img = load_png_image("logo.png")
    if logo_img:
        st.image(logo_img, use_container_width=True)
    
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
    
    home_img = load_png_image("abertura.png")
    if not home_img:
        home_img = load_png_image("home.png")
        
    # Organiza em colunas para diminuir o tamanho horizontal da imagem na tela
    col1, col2, col3 = st.columns([0.5, 5, 0.5])
    with col2:
        if home_img:
            st.image(home_img, use_container_width=True)
        
        st.markdown("""
            <div class="welcome-overlay-card">
                <h2>Bem-vindo ao CALC MARKUP</h2>
                <p>Sua ferramenta inteligente para precificar importações.</p>
                <p style="font-size: 13px; color: #38bdf8; margin-top: 6px;">Clique em <b>'🛒 Cadastrar Produto'</b> no menu lateral para começar.</p>
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
