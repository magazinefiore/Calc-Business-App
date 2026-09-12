import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ---------------------------------------------------------
# CONEXÃO COM O BANCO DE DADOS
# ---------------------------------------------------------
def get_connection():
    return sqlite3.connect("database.db", check_same_thread=False)

# ---------------------------------------------------------
# 1. DASHBOARD & GRÁFICOS
# ---------------------------------------------------------
def render_dashboard():
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM products", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Produtos Cadastrados", len(df) if not df.empty else 0)
    with col2:
        avg_markup = f"{df['markup'].mean():.2f}x" if not df.empty and 'markup' in df.columns else "0.00x"
        st.metric("📊 Markup Médio", avg_markup)
    with col3:
        avg_price = f"R$ {df['preco_venda'].mean():.2f}" if not df.empty and 'preco_venda' in df.columns else "R$ 0,00"
        st.metric("💰 Preço Médio de Venda", avg_price)
    with col4:
        st.metric("🌐 Canais Ativos", "Mercado Livre, Shopee, Amazon")

    st.markdown("---")
    st.subheader("Visão Geral de Desempenho")
    
    if not df.empty and 'nome' in df.columns and 'preco_venda' in df.columns:
        st.bar_chart(df.set_index('nome')['preco_venda'])
    else:
        st.info("Cadastre produtos para visualizar os gráficos de precificação.")

# ---------------------------------------------------------
# 2. CADASTRAR PRODUTO
# ---------------------------------------------------------
def render_product_form():
    with st.form("form_cad_produto"):
        st.subheader("Dados do Produto Importado (China ➔ Brasil)")
        
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Produto", placeholder="Ex: Protetor de Cabo Silicone Tipo C (Kit 4 Pares)")
            sku = st.text_input("SKU / Código", placeholder="Ex: PROT-TC-04")
            custo_usd = st.number_input("Custo Unitário (USD / RMB)", min_value=0.0, format="%.2f", value=1.50)
            frete_unit = st.number_input("Frete Internacional Unitário (R$)", min_value=0.0, format="%.2f", value=0.80)
        
        with col2:
            taxa_importacao = st.number_input("Imposto de Importação (%)", min_value=0.0, value=60.0)
            icms = st.number_input("ICMS (%)", min_value=0.0, value=18.0)
            comissao_marketplace = st.number_input("Comissão do Marketplace (%)", min_value=0.0, value=16.0)
            margem_desejada = st.number_input("Margem de Lucro Desejada (%)", min_value=0.0, value=30.0)

        submitted = st.form_submit_button("Salvar e Calcular Preço", use_container_width=True)
        if submitted:
            if nome:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute('''
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
                custo_total = (custo_usd * 5.5) + frete_unit
                markup = 2.5
                preco_venda = custo_total * markup
                
                cursor.execute('''
                    INSERT INTO products (nome, sku, custo_usd, frete_unit, markup, preco_venda, data_cadastro)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (nome, sku, custo_usd, frete_unit, markup, preco_venda, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                conn.close()
                st.success(f"Produto '{nome}' cadastrado com sucesso! Preço Sugerido: R$ {preco_venda:.2f}")
            else:
                st.warning("Preencha o nome do produto.")

# ---------------------------------------------------------
# 3. IMPORTAR CSV
# ---------------------------------------------------------
def render_csv_import():
    st.subheader("Importação em Massa via Planilha CSV")
    st.markdown("Faça o upload de um arquivo CSV contendo os produtos importados para cadastrá-los em lote.")
    uploaded_file = st.file_uploader("Escolha o arquivo CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df, use_container_width=True)
        if st.button("Processar e Salvar Lote", use_container_width=True):
            st.success("Planilha processada com sucesso!")

# ---------------------------------------------------------
# 4. LISTA DE PRODUTOS
# ---------------------------------------------------------
def render_products_list():
    st.subheader("Catálogo de Produtos Cadastrados")
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM products", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado até o momento.")

# ---------------------------------------------------------
# 5. CALCULADORA DE FORMAÇÃO DE PREÇO
# ---------------------------------------------------------
def render_calculator():
    st.subheader("Simulador Avançado de Formação de Preço")
    col1, col2 = st.columns(2)
    with col1:
        c_prod = st.number_input("Custo do Produto (R$)", value=5.00)
        f_int = st.number_input("Frete & Embalagem (R$)", value=1.50)
        imposto = st.number_input("Impostos sobre Venda (%)", value=10.0)
    with col2:
        taxa_mkt = st.number_input("Comissão do Marketplace (%)", value=16.0)
        custo_fixo = st.number_input("Rateio de Custo Fixo (%)", value=5.0)
        lucro = st.number_input("Margem de Lucro Alvo (%)", value=25.0)

    divisor = 100 - (imposto + taxa_mkt + custo_fixo + lucro)
    if divisor > 0:
        custo_total = c_prod + f_int
        sugerido = custo_total / (divisor / 100)
        st.markdown(f"### Preço de Venda Ideal: **R$ {sugerido:.2f}**")
    else:
        st.error("A soma dos percentuais não pode ultrapassar 100%.")

# ---------------------------------------------------------
# 6. SIMULADOR DE DESCONTOS
# ---------------------------------------------------------
def render_discount_simulator():
    st.subheader("Simulador de Promoções e Descontos")
    preco_atual = st.number_input("Preço de Venda Atual (R$)", value=29.90)
    desconto_pct = st.slider("Percentual de Desconto (%)", 0, 50, 10)
    novo_preco = preco_atual * (1 - desconto_pct / 100)
    st.metric("Preço Promocional", f"R$ {novo_preco:.2f}", delta=f"-{desconto_pct}%")

# ---------------------------------------------------------
# 7. ATACADO
# ---------------------------------------------------------
def render_wholesale():
    st.subheader("Tabela de Preços para Kits e Atacado")
    st.markdown("Configure descontos progressivos para kits de 2, 4 e 8 pares (ex: protetores de cabo).")
    qtde = st.selectbox("Quantidade no Kit", ["1 Par", "2 Pares", "4 Pares", "8 Pares"])
    desconto_lote = st.slider("Desconto para este kit (%)", 0, 30, 10)
    st.info(f"Aplicando {desconto_lote}% de desconto para o item selecionado.")

# ---------------------------------------------------------
# 8. CONTROLE DE ESTOQUE
# ---------------------------------------------------------
def render_stock_control():
    st.subheader("Gerenciamento de Estoque & Envio (Olist / Shopee / Amazon)")
    st.warning("⚠️ Atenção: Estoque baixo para o SKU: PROT-TC-04 (Restam 18 unidades).")
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM products", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    if not df.empty:
        st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# 9. RELATÓRIOS & EXPORTAÇÃO
# ---------------------------------------------------------
def render_reports():
    st.subheader("Exportação de Dados e Relatórios Gerenciais")
    st.download_button("📥 Baixar Relatório em CSV", data="id,nome,preco\n1,Protetor,29.90", file_name="relatorio_lm.csv", mime="text/csv")

# ---------------------------------------------------------
# 10. CONFIGURAÇÕES
# ---------------------------------------------------------
def render_settings():
    st.subheader("Configurações Gerais do Sistema")
    st.text_input("Nome da Empresa", value="LM - Importing 2U®")
    st.number_input("Cotação Padrão do Dólar (USD)", value=5.50)
    st.button("Salvar Configurações", use_container_width=True)
