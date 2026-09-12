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
# LOCALIZAÇÃO NATIVA DE IMAGENS (MÁXIMA NITIDEZ)
# ---------------------------------------------------------
def get_image_path(image_filename):
    """
    Retorna o caminho real do arquivo de imagem para ser renderizado 
    nativamente pelo Streamlit, garantindo 100% de nitidez e qualidade original.
    """
    base_name = os.path.splitext(image_filename)[0]
    extensions = ['.png', '.PNG', '.jpg', '.JPG', '.jpeg']
    
    for ext in extensions:
        file_path = base_name + ext
        if os.path.exists(file_path):
            return file_path
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

    /* EXIBIÇÃO NATIVA DE IMAGENS SEM PERDA DE QUALIDADE */
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
        image-rendering: -webkit-optimize-contrast; /* Melhora a nitidez em navegadores Webkit */
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
# GERENCIAMENTO SEGURO DE LOGIN (CAMPOS EM BRANCO)
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
                user = st.text_input("Usuário", value="")
                password = st.text_input("Senha", type="password", value="")
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
    logo_path = get_image_path("logo.png")
    if logo_path:
        st.image(logo_path, use_container_width=True)
    
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
    
    home_path = get_image_path("abertura.png")
    if not home_path:
        home_path = get_image_path("home.png")
        
    # Organiza em colunas para manter a proporção e centralização perfeita
    col1, col2, col3 = st.columns([0.5, 5, 0.5])
    with col2:
        if home_path:
            st.image(home_path, use_container_width=True)
        
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
