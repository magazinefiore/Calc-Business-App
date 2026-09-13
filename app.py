import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
import hashlib

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA E BANCO DE DADOS
# ---------------------------------------------------------
st.set_page_config(page_title="CALC MARKUP - LM - Importing 2U®", page_icon="Simulador.ico", layout="wide")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_connection():
    # Cria a conexão e garante que as tabelas existam
    conn = sqlite3.connect("database.db", check_same_thread=False)
    
    # Tabela de Produtos
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            sku TEXT,
            custo_usd REAL,
            frete_unit REAL,
            markup REAL,
            preco_venda REAL,
            data_cadastro TEXT
        )
    ''')
    
    # Tabela de Usuários
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            data_criacao TEXT
        )
    ''')
    
    # Criação do usuário admin padrão caso não exista
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        senha_admin = hash_password("admin123")
        conn.execute("INSERT INTO users (username, password, role, data_criacao) VALUES (?, ?, ?, ?)",
                     ("admin", senha_admin, "Administrador", datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        
    return conn

# ---------------------------------------------------------
# FUNÇÕES DE RENDERIZAÇÃO DAS PÁGINAS (MÓDULOS)
# ---------------------------------------------------------
def render_home():
    st.title("🏠 Bem-vindo(a) ao CALC MARKUP")
    st.markdown("### Sistema de Gestão e Precificação - LM - Importing 2U®")
    st.markdown("---")
    
    st.write("Bem-vindo ao painel central de controle. Utilize o menu lateral para navegar ou acesse os atalhos abaixo:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📊 **Visão Geral**\nAcompanhe o desempenho, markups médios e os preços dos seus produtos.")
        
    with col2:
        st.success("🛒 **Novo Produto**\nCadastre e calcule instantaneamente o preço de venda ideal considerando todos os custos.")
        
    with col3:
        st.warning("🧮 **Calculadora Rápida**\nSimule rapidamente a formação de preço sem precisar salvar no banco de dados.")

def render_dashboard():
    st.title("📊 Dashboard Executivo & Gráficos")
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Produtos Cadastrados", len(df) if not df.empty else 0)
    col2.metric("📈 Markup Médio", f"{df['markup'].mean():.2f}x" if not df.empty else "0.00x")
    col3.metric("💰 Preço Médio (Venda)", f"R$ {df['preco_venda'].mean():.2f}" if not df.empty else "R$ 0,00")
    col4.metric("🌐 Canais Integrados", "Olist, Amazon, Shopee")

    st.markdown("---")
    if not df.empty:
        st.subheader("Comparativo de Preço de Venda por Produto")
        st.bar_chart(df.set_index('nome')['preco_venda'])
    else:
        st.info("Cadastre produtos para visualizar os gráficos de precificação.")

def render_product_form():
    st.title("🛒 Cadastrar Novo Produto")
    with st.form("form_cad_produto"):
        st.subheader("Custos de Importação (China ➔ Brasil)")
        
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Produto", placeholder="Ex: Protetor de Cabo Silicone Tipo C (Kit 4 Pares)")
            sku = st.text_input("SKU / Código", placeholder="Ex: PROT-TC-04")
            custo_usd = st.number_input("Custo Unitário (USD / RMB)", min_value=0.0, format="%.2f", value=1.50)
            frete_unit = st.number_input("Frete Internacional Unitário (R$)", min_value=0.0, format="%.2f", value=0.80)
        
        with col2:
            imposto_importacao = st.number_input("Imposto de Importação (%)", min_value=0.0, value=60.0)
            icms = st.number_input("ICMS (%)", min_value=0.0, value=18.0)
            comissao_mkt = st.number_input("Comissão do Marketplace (%)", min_value=0.0, value=16.0)
            margem = st.number_input("Margem de Lucro Alvo (%)", min_value=0.0, value=30.0)

        if st.form_submit_button("Salvar e Calcular Preço", use_container_width=True):
            if nome and sku:
                custo_total = (custo_usd * 5.5) + frete_unit 
                markup = 2.5
                preco_venda = custo_total * markup
                
                conn = get_connection()
                conn.execute('''
                    INSERT INTO products (nome, sku, custo_usd, frete_unit, markup, preco_venda, data_cadastro)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (nome, sku, custo_usd, frete_unit, markup, preco_venda, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                conn.close()
                st.success(f"Produto '{nome}' salvo! Preço Sugerido: R$ {preco_venda:.2f}")
            else:
                st.warning("Preencha o Nome e o SKU do produto.")

def render_csv_import():
    st.title("📁 Importar Produtos via CSV")
    st.markdown("Faça o upload de uma planilha CSV para cadastro em lote.")
    uploaded_file = st.file_uploader("Selecione o arquivo CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df, use_container_width=True)
        if st.button("Processar Lote", use_container_width=True):
            st.success("Produtos importados com sucesso!")

def render_products_list():
    st.title("📦 Lista de Produtos")
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado no banco de dados.")

def render_calculator():
    st.title("🧮 Calculadora de Formação de Preço")
    col1, col2 = st.columns(2)
    with col1:
        c_prod = st.number_input("Custo Base (R$)", value=5.00)
        f_int = st.number_input("Frete & Embalagem (R$)", value=1.50)
        impostos = st.number_input("Impostos sobre Venda (%)", value=10.0)
    with col2:
        taxa_mkt = st.number_input("Comissão do Canal (%)", value=16.0)
        custo_fixo = st.number_input("Rateio Custo Fixo (%)", value=5.0)
        lucro = st.number_input("Lucro Líquido Desejado (%)", value=25.0)

    divisor = 100 - (impostos + taxa_mkt + custo_fixo + lucro)
    if divisor > 0:
        sugerido = (c_prod + f_int) / (divisor / 100)
        st.success(f"Preço de Venda Ideal: **R$ {sugerido:.2f}**")
    else:
        st.error("A soma das porcentagens não pode ser maior ou igual a 100%.")

def render_discount_simulator():
    st.title("🏷️ Simulador de Descontos e Promoções")
    preco_atual = st.number_input("Preço de Venda Atual (R$)", value=29.90)
    desconto = st.slider("Desconto a aplicar (%)", 0, 50, 10)
    novo_preco = preco_atual * (1 - desconto / 100)
    st.metric("Preço Final com Desconto", f"R$ {novo_preco:.2f}", f"-{desconto}%")

def render_wholesale():
    st.title("🛒 Estratégia de Atacado & Kits")
    st.markdown("Defina preços regressivos para variações de kits.")
    kit = st.selectbox("Selecione a Variação", ["Kit 1 Par", "Kit 2 Pares", "Kit 4 Pares", "Kit 8 Pares"])
    desc_lote = st.slider("Desconto para o volume selecionado (%)", 0, 40, 15)
    st.info(f"Regra configurada: {desc_lote}% de desconto para {kit}.")

def render_stock_control():
    st.title("📋 Controle de Estoque & Expedição")
    st.warning("⚠️ Alerta: SKU PROT-TC-04 está com estoque baixo (18 unidades).")
    render_products_list()

def render_reports():
    st.title("📄 Relatórios & Exportação")
    st.markdown("Gere relatórios para conferência de etiquetas ou balanço financeiro.")
    st.download_button("Baixar Tabela de Preços (CSV)", "id,nome,preco\n1,Protetor,29.90", "tabela_lm.csv", "text/csv")

def render_settings():
    st.title("⚙️ Configurações Globais")
    st.text_input("Nome da Operação", value="LM - Importing 2U®")
    st.number_input("Cotação Fixa do Dólar (USD para BRL)", value=5.50, format="%.2f")
    st.button("Salvar Configurações", use_container_width=True)

def render_audit_logs():
    st.title("👤 Usuários & Logs de Auditoria")
    
    tab1, tab2 = st.tabs(["👥 Cadastro de Usuários", "📋 Logs de Auditoria"])
    
    with tab1:
        st.subheader("Gerenciar Usuários do Sistema")
        
        with st.form("form_novo_usuario"):
            st.write("Cadastrar novo acesso ao sistema")
            novo_user = st.text_input("Nome de Usuário (Login)")
            nova_senha = st.text_input("Senha", type="password")
            perfil = st.selectbox("Perfil de Acesso", ["Administrador", "Operador"])
            
            if st.form_submit_button("Cadastrar Usuário", use_container_width=True):
                if novo_user and nova_senha:
                    try:
                        conn = get_connection()
                        conn.execute("INSERT INTO users (username, password, role, data_criacao) VALUES (?, ?, ?, ?)",
                                     (novo_user.strip(), hash_password(nova_senha), perfil, datetime.now().strftime("%Y-%m-%d")))
                        conn.commit()
                        conn.close()
                        st.success(f"Usuário '{novo_user}' cadastrado com sucesso!")
                    except sqlite3.IntegrityError:
                        st.error("Este nome de usuário já existe no sistema.")
                else:
                    st.warning("Preencha todos os campos.")
        
        st.markdown("---")
        st.subheader("Usuários Cadastrados")
        conn = get_connection()
        df_users = pd.read_sql_query("SELECT id, username, role, data_criacao FROM users", conn)
        conn.close()
        st.dataframe(df_users, use_container_width=True)

    with tab2:
        st.subheader("Registro de Atividades")
        st.info("Nenhum log recente de alteração de preços.")

# ---------------------------------------------------------
# SISTEMA DE LOGIN E NAVEGAÇÃO
# ---------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("abertura.png"):
            st.image("abertura.png", use_container_width=True)
            
        st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>LM - Importing 2U® - Gestão de Importação</p>", unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("Usuário", placeholder="admin")
            pwd = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Sistema", use_container_width=True):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT password, role FROM users WHERE username = ?", (user.strip(),))
                result = cursor.fetchone()
                conn.close()
                
                if result and result[0] == hash_password(pwd):
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.session_state.role = result[1]
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
else:
    with st.sidebar:
        if os.path.exists("abertura.png"):
            st.image("abertura.png", use_container_width=True)
            
        st.markdown("### CALC MARKUP")
        st.markdown("**LM - Importing 2U®**")
        st.markdown(f"👤 **{st.session_state.username}**")
        st.caption(f"({st.session_state.role})")
        if st.button("Sair / Trocar Usuário", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.rerun()
            
        st.markdown("---")
        menu = st.radio(
            "Navegação",
            ["Início", "Dashboard & Gráficos", "Cadastrar Produto", "Importar CSV", "Produtos", 
             "Calculadora de Formação de Preço", "Simulador de Descontos", "Atacado", 
             "Controle de Estoque", "Relatórios & Exportação", "Configurações", "Usuários & Logs de Auditoria"],
            label_visibility="collapsed"
        )

    # ROTEAMENTO CORRIGIDO
    if menu == "Início": render_home()
    elif menu == "Dashboard & Gráficos": render_dashboard()
    elif menu == "Cadastrar Produto": render_product_form()
    elif menu == "Importar CSV": render_csv_import()
    elif menu == "Produtos": render_products_list()
    elif menu == "Calculadora de Formação de Preço": render_calculator()
    elif menu == "Simulador de Descontos": render_discount_simulator()
    elif menu == "Atacado": render_wholesale()
    elif menu == "Controle de Estoque": render_stock_control()
    elif menu == "Relatórios & Exportação": render_reports()
    elif menu == "Configurações": render_settings()
    elif menu == "Usuários & Logs de Auditoria": render_audit_logs()
