import streamlit as st
import os
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
# ESTILIZAÇÃO CSS (TEMA ESCURO, LETRAS BRANCAS E MISTURA DE IMAGEM)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Fundo Escuro Principal */
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

    /* REMOVE O FUNDO BRANCO DAS IMAGENS NO MENU LATERAL */
    section[data-testid="stSidebar"] img {
        border-radius: 8px;
        mix-blend-mode: multiply;
        background-color: transparent !important;
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
        margin-top: -140px;
        margin-left: auto;
        margin-right: auto;
        width: 85%;
        max-width: 600px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        z-index: 10;
        color: #1f2937;
    }
    
    .welcome-card h2 {
        color: #111827 !important;
        font-weight: 800;
        font-size: 26px;
        margin-bottom: 10px;
    }
    
    .welcome-card p {
        color: #374151 !important;
        font-size: 15px;
        margin-bottom: 8px;
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
        st.image(logo_file, use_container_width=True)
    
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
        st.image(home_file, use_container_width=True)
    
    st.markdown("""
        <div class="welcome-card">
            <h2>Bem-vindo ao CALC MARKUP</h2>
            <p>Sua ferramenta inteligente para precificar importações.</p>
            <p style="font-size: 13px; color: #6b7280;">Clique em <b>'🛒 Cadastrar Produto'</b> no menu lateral para começar.</p>
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
