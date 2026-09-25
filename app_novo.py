"""
CALC MARKUP - LM Importing 2U
==============================
Sistema de Gestão e Precificação

Versão 2.0 — Integração com Supabase
Autor: Luiz Lopes Teixeira Neto
Data: Setembro 2026
"""

import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime
import hashlib

# Importação do módulo de ajuda contextual
from ajudas import ajuda_pagina

# Importação do módulo de banco de dados (Supabase)
try:
    from database_supabase import (
        get_supabase,
        get_all_products,
        get_products_by_category,
        insert_product,
        update_product,
        delete_product,
        get_user_by_username,
        create_user,
        list_users,
        log_audit,
        get_audit_logs,
        update_stock,
    )
    SUPABASE_OK = True
except Exception as e:
    SUPABASE_OK = False
    st.error(f"⚠️ Erro ao conectar com Supabase: {e}")


# =============================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================
st.set_page_config(
    page_title="CALC MARKUP - LM Importing 2U®",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================
# CSS PERSONALIZADO
# =============================================================
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        height: 50px;
        font-weight: bold;
        font-size: 16px;
        border-radius: 10px;
        background-color: #4CAF50;
        color: white;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    .stSelectbox > div > div > select {
        border-radius: 8px;
    }
    .card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================
# FUNÇÕES AUXILIARES
# =============================================================
def hash_password(password: str) -> str:
    """Gera o hash SHA-256 da senha."""
    return hashlib.sha256(password.encode()).hexdigest()


def to_float(v) -> float:
    """Converte um valor em float, tolerando vírgulas e símbolos."""
    if pd.isna(v):
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace("R$", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


# =============================================================
# SESSÃO
# =============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""


# =============================================================
# TELA DE LOGIN
# =============================================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("abertura.png"):
            st.image("abertura.png", use_container_width=True)
        st.markdown(
            "<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align: center; color: gray;'>LM - Importing 2U® - Gestão de Importação</p>",
            unsafe_allow_html=True
        )
        with st.form("login_form"):
            user = st.text_input("Usuário", placeholder="admin")
            pwd = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Sistema", use_container_width=True):
                if not SUPABASE_OK:
                    st.error("Erro: Supabase não configurado corretamente.")
                else:
                    user_data = get_user_by_username(user.strip())
                    if user_data and user_data.get("password_hash") == hash_password(pwd):
                        st.session_state.logged_in = True
                        st.session_state.username = user
                        st.session_state.role = user_data.get("role", "Operador")
                        log_audit(user, "Login", "Acesso bem-sucedido")
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas.")

# =============================================================
# APP PRINCIPAL (após login)
# =============================================================
else:
    # ---------- SIDEBAR ----------
    with st.sidebar:
        if os.path.exists("abertura.png"):
            st.image("abertura.png", use_container_width=True)
        st.markdown("### CALC MARKUP")
        st.markdown("**LM - Importing 2U®**")
        st.markdown(f"👤 **{st.session_state.username}**")
        st.caption(f"({st.session_state.role})")
        if st.button("Sair / Trocar Usuário", use_container_width=True):
            log_audit(st.session_state.username, "Logout", "Sessão encerrada")
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.rerun()

        st.markdown("---")
        menu = st.radio(
            "Navegação",
            [
                "Início",
                "Dashboard & Gráficos",
                "Cadastrar Produto",
                "Importar CSV",
                "Produtos",
                "Calculadora de Formação de Preço",
                "Simulador de Descontos",
                "Atacado",
                "Controle de Estoque",
                "Relatórios & Exportação",
                "Configurações",
                "Usuários & Logs de Auditoria",
                "📘 Manual",
            ],
            label_visibility="collapsed"
        )

    # ========== RENDERIZAÇÃO DAS PÁGINAS ==========
    if menu == "Início":
        render_home()
    elif menu == "Dashboard & Gráficos":
        render_dashboard()
    elif menu == "Cadastrar Produto":
        render_product_form()
    elif menu == "Importar CSV":
        render_csv_import()
    elif menu == "Produtos":
        render_products_list()
    elif menu == "Calculadora de Formação de Preço":
        render_calculator()
    elif menu == "Simulador de Descontos":
        render_discount_simulator()
    elif menu == "Atacado":
        render_wholesale()
    elif menu == "Controle de Estoque":
        render_stock_control()
    elif menu == "Relatórios & Exportação":
        render_reports()
    elif menu == "Configurações":
        render_settings()
    elif menu == "Usuários & Logs de Auditoria":
        render_audit_logs()
    elif menu == "📘 Manual":
        render_manual()


# =============================================================
# FUNÇÕES DAS PÁGINAS
# =============================================================

def render_home():
    """Página Início — Painel central de boas-vindas."""
    col_titulo, col_ajuda = st.columns([15, 1])
    with col_titulo:
        st.title("🏠 Bem-vindo(a) ao CALC MARKUP")
    with col_ajuda:
        ajuda_pagina("inicio")

    st.markdown("### Sistema de Gestão e Precificação - LM - Importing 2U®")
    st.markdown("---")
    st.write("Bem-vindo ao painel central de controle.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 **Visão Geral**\nAcompanhe o desempenho, markups médios e preços.")
    with col2:
        st.success("🛒 **Novo Produto**\nCadastre e calcule instantaneamente o preço ideal.")
    with col3:
        st.warning("🧮 **Calculadora Rápida**\nSimule formação de preço sem salvar no banco.")


def render_dashboard():
    """Página Dashboard — Métricas e gráficos."""
    col_titulo, col_ajuda = st.columns([15, 1])
    with col_titulo:
        st.title("📊 Dashboard Executivo & Gráficos")
    with col_ajuda:
        ajuda_pagina("dashboard")

    df = get_all_products()

    categorias = ["(todas)"] + sorted(
        [c for c in df["categoria"].dropna().unique().tolist() if c]
    ) if not df.empty else ["(todas)"]

    cat_escolhida = st.selectbox("Filtrar por categoria", categorias, index=0)
    if cat_escolhida != "(todas)":
        df = df[df["categoria"] == cat_escolhida]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Produtos Cadastrados", len(df) if not df.empty else 0)
    col2.metric("📈 Markup Médio",
                f"{df['markup'].mean():.2f}x" if not df.empty else "0.00x")
    col3.metric("💰 Preço Médio (Venda)",
                f"R$ {df['preco_venda'].mean():.2f}" if not df.empty else "R$ 0,00")
    col4.metric("🌐 Canais Integrados", "Olist, Amazon, Shopee")

    st.markdown("---")
    if not df.empty:
        st.subheader("Comparativo de Preço de Venda por Produto")
        st.bar_chart(df.set_index('nome')['preco_venda'])
    else:
        st.info("Cadastre produtos para visualizar os gráficos de precificação.")


def render_product_form():
    """Página Cadastrar Produto."""
    col_titulo, col_ajuda = st.columns([15, 1])
    with col_titulo:
        st.title("🛒 Cadastrar Novo Produto")
    with col_ajuda:
        ajuda_pagina("cadastrar")

    with st.form("form_cad_produto"):
        st.subheader("Custos de Importação (China ➔ Brasil)")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Produto",
                                 placeholder="Ex: Protetor de Cabo Silicone Tipo C")
            sku = st.text_input("SKU / Código", placeholder="Ex: PROT-TC-04")
            custo_unit = st.number_input("Custo Unitário (R$)", min_value=0.0,
                                         format="%.2f", value=1.50)
            frete_unit = st.number_input("Frete Internacional Unitário (R$)",
                                         min_value=0.0, format="%.2f", value=0.80)
        with col2:
            categoria = st.text_input("Categoria", value="Geral")
            imposto_importacao = st.number_input("Imposto de Importação (%)",
                                                 min_value=0.0, value=60.0)
            icms = st.number_input("ICMS (%)", min_value=0.0, value=18.0)
            comissao_mkt = st.number_input("Comissão do Marketplace (%)",
                                           min_value=0.0, value=16.0)
            margem = st.number_input("Margem de Lucro Alvo (%)",
                                     min_value=0.0, value=30.0)

        if st.form_submit_button("Salvar e Calcular Preço", use_container_width=True):
            if nome and sku:
                custo_total = (custo_unit * 5.5) + frete_unit
                markup = 2.5
                preco_venda = custo_total * markup

                dados = {
                    "sku": sku,
                    "nome": nome,
                    "categoria": categoria or "Geral",
                    "c_base": custo_unit,
                    "custo_unit": custo_unit,
                    "frete_unit": frete_unit,
                    "embalagem": 0.5,
                    "tax_pct": imposto_importacao,
                    "icms_pct": icms,
                    "marketplace_pct": comissao_mkt,
                    "margin_desired_pct": margem,
                    "markup": markup,
                    "preco_venda": preco_venda,
                    "current_stock": 0,
                    "min_stock": 5,
                }
                ok, msg = insert_product(dados, st.session_state.username)
                if ok:
                    st.success(f"Produto '{nome}' salvo! Preço Sugerido: R$ {preco_venda:.2f}")
                else:
                    st.error(msg)
            else:
                st.warning("Preencha o Nome e o SKU do produto.")


def render_csv_import():
    """Página Importar CSV/Excel."""
    col_titulo, col_ajuda = st.columns([15, 1])
    with col_titulo:
        st.title("📁 Importar Produtos via CSV / Excel")
    with col_ajuda:
        ajuda_pagina("importar")

    st.markdown("Faça o upload de uma planilha **CSV** ou **Excel (.xlsx)**.")
    uploaded_file = st.file_uploader("Selecione o arquivo", type=["csv", "xlsx", "xls"])

    if not uploaded_file:
        st.markdown("---")
        st.subheader("📤 Exportar modelo de CSV")
        exemplo = pd.DataFrame([
            {"nome": "Protetor de Cabo Silicone Tipo C", "categoria": "Cabos",
             "custo_unit": 0.04, "frete_unit": 0.80,
             "markup": 2.5, "preco_venda": 5.30},
        ])
        csv_buffer = io.StringIO()
        exemplo.to_csv(csv_buffer, index=False, sep=";", encoding="utf-8-sig")
        st.download_button(
            "⬇️ Baixar modelo (CSV)",
            data=csv_buffer.getvalue().encode("utf-8-sig"),
            file_name="modelo_importacao_produtos.csv",
            mime="text/csv",
            use_container_width=True,
        )
        return

    st.info("📌 Funcionalidade de importação completa será configurada após validação do Bloco 3.")


def render_products_list():
    """Página Lista de Produtos."""
    col_titulo, col_ajuda = st.columns([15, 1])
    with col_titulo:
        st.title("📦 Lista de Produtos")
    with col_ajuda:
        ajuda_pagina("produtos")

    df = get_all_products()

    if df.empty:
        st.info("Nenhum produto cadastrado no banco de dados.")
        return

    categorias = ["(todas)"] + sorted(
        [c for c in df["categoria"].dropna().unique().tolist() if c]
    )
    cat = st.selectbox("Filtrar por categoria", categorias)
    if cat != "(todas)":
        df = df[df["categoria"] == cat]

    st.dataframe(df, use_container_width=True)
    st.caption(f"{len(df)} produtos exibidos.")


def render_calculator():
    """Página Calculadora de Formação de Preço."""
    col_titulo, col_ajuda = st.columns([15, 1])
    with col_titulo:
        st.title("🧮 Calculadora de Formação de Preço")
    with col_ajuda:
        ajuda_pagina("calculadora")

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
    """Página Simulador de Descontos."""
    col_titulo, col_ajuda = st.columns([15, 1])
    with col_titulo:
        st.title("🏷️ Simulador de Descontos e Promoções")
    with col_ajuda:
        ajuda_pagina("simulador")

    preco_atual = st.number_input("Preço de Venda Atual (R$)", value=29.90)
    desconto = st.slider("Desconto a aplicar (%)", 0, 50, 10)
    novo_preco = preco_atual * (1 - desconto / 100)
    st.metric("Preço Final com Desconto",
              f"R$ {novo_preco:.2f}", f"-{desconto}%")


def render_wholesale():
    """Página Estratégia de Atacado & Kits."""
    col_titulo, col_ajuda = st.columns([15, 1])
    with col_titulo:
        st.title("🛒 Estratégia de Atacado & Kits")
    with col_ajuda:
        ajuda_pagina("atacado")

    kit = st.selectbox("Selecione a Variação",
                       ["Kit 1 Par", "Kit 2 Pares", "Kit 4 Pares", "Kit 8 Pares"])
    desc_lote = st.slider("Desconto para o volume selecionado (%)", 0, 40, 15)
    st.info(f"Regra configurada: {desc_lote}% de desconto para {kit}.")


def render_stock_control():
    """Página Controle de Estoque."""
    col_titulo, col_ajuda = st.columns([15, 1])
    with col_titulo:
        st.title("📋 Controle de Estoque & Expedição")
    with col_ajuda:
        ajuda_pagina("estoque")

    st.warning("⚠️ Alerta: SKU PROT-TC-04 está com estoque baixo (18 unidades).")
    render_products_list()


def render_reports():
    """Página Relatórios & Exportação."""
    col_titulo, col_ajuda = st.columns([15, 1])
    with col_titulo:
        st.title("📄 Relatórios & Exportação")
    with col_ajuda:
        ajuda_pagina("relatorios")

    st.markdown("Gere relatórios para conferência ou balanço financeiro.")
    st.download_button("Baixar Tabela de Preços (CSV)",
                       "id,nome,preco\n1,Protetor,29.90",
                       "tabela_lm.csv", "text/csv")


def render_settings():
    """Página Configurações Globais."""
    col_titulo, col_ajuda = st.columns([15, 1])
    with col_titulo:
        st.title("⚙️ Configurações Globais")
    with col_ajuda:
        ajuda_pagina("configuracoes")

    st.text_input("Nome da Operação", value="LM - Importing 2U®")
    st.number_input("Cotação Fixa do Dólar (USD para BRL)",
                    value=5.50, format="%.2f")
    st.button("Salvar Configurações", use_container_width=True)


def render_audit_logs():
    """Página Usuários & Logs de Auditoria."""
    col_titulo, col_ajuda = st.columns([15, 1])
    with col_titulo:
        st.title("👤 Usuários & Logs de Auditoria")
    with col_ajuda:
        ajuda_pagina("usuarios")

    tab1, tab2 = st.tabs(["👥 Cadastro de Usuários", "📋 Logs de Auditoria"])

    with tab1:
        st.subheader("Gerenciar Usuários do Sistema")
        with st.form("form_novo_usuario"):
            novo_user = st.text_input("Nome de Usuário (Login)")
            nova_senha = st.text_input("Senha", type="password")
            perfil = st.selectbox("Perfil de Acesso", ["Administrador", "Operador"])
            if st.form_submit_button("Cadastrar Usuário", use_container_width=True):
                if novo_user and nova_senha:
                    ok, msg = create_user(
                        username=novo_user.strip(),
                        password_hash=hash_password(nova_senha),
                        role=perfil,
                        name=novo_user.strip()
                    )
                    if ok:
                        st.success(f"Usuário '{novo_user}' cadastrado com sucesso!")
                    else:
                        st.error(msg)
                else:
                    st.warning("Preencha todos os campos.")

        st.markdown("---")
        st.subheader("Usuários Cadastrados")
        df_users = list_users()
        if not df_users.empty:
            st.dataframe(df_users, use_container_width=True)
        else:
            st.info("Nenhum usuário cadastrado.")

    with tab2:
        st.subheader("Registro de Atividades")
        df_logs = get_audit_logs(limit=100)
        if not df_logs.empty:
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("Nenhum log registrado até o momento.")


def render_manual():
    """Página Manual de Uso."""
    st.title("📘 Manual de Uso — CALC MARKUP")
    st.markdown("Bem-vindo ao manual interativo. Navegue pelas abas abaixo.")
    st.markdown("---")

    manual_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual.md")

    if not os.path.exists(manual_path):
        st.error("❌ Arquivo `manual.md` não encontrado na pasta do app.")
        return

    try:
        with open(manual_path, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except Exception as e:
        st.error(f"❌ Erro ao ler o `manual.md`: {e}")
        return

    # Separa o manual em seções (## Título)
    secoes = {}
    secao_atual = "Introdução"
    secoes[secao_atual] = []

    for linha in conteudo.splitlines():
        if linha.startswith("## "):
            secao_atual = linha.replace("## ", "", 1).strip()
            secoes[secao_atual] = []
        else:
            secoes[secao_atual].append(linha)

    for k in list(secoes.keys()):
        secoes[k] = "\n".join(secoes[k]).strip()

    if not secoes.get("Introdução", ""):
        del secoes["Introdução"]

    if not secoes:
        st.warning("Nenhuma seção encontrada no `manual.md`.")
        return

    # Gera HTML para download
    try:
        import markdown as md_lib
        html_body = md_lib.markdown(
            conteudo,
            extensions=["extra", "toc", "tables", "fenced_code"]
        )
    except ImportError:
        html_body = conteudo.replace("\n", "<br>")

    html_completo = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Manual de Uso — CALC MARKUP</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 960px; margin: 40px auto; padding: 20px; line-height: 1.6; color: #2d3748; background: #f7fafc; }}
h1 {{ color: #1a365d; border-bottom: 3px solid #3182ce; padding-bottom: 12px; }}
h2 {{ color: #2c5282; border-bottom: 2px solid #bee3f8; padding-bottom: 8px; }}
code {{ background: #edf2f7; color: #c53030; padding: 2px 6px; border-radius: 4px; }}
pre {{ background: #2d3748; color: #f7fafc; padding: 16px; border-radius: 8px; overflow-x: auto; white-space: pre; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th, td {{ border: 1px solid #cbd5e0; padding: 10px; text-align: left; }}
th {{ background: #3182ce; color: white; }}
.header {{ text-align: center; padding: 20px; background: linear-gradient(135deg, #3182ce, #2c5282); color: white; border-radius: 12px; margin-bottom: 30px; }}
.header h1 {{ color: white; border: none; }}
</style>
</head>
<body>
<div class="header">
    <h1>📘 Manual de Uso — CALC MARKUP</h1>
    <p>LM - Importing 2U® — Sistema de Gestão e Precificação</p>
</div>
{html_body}
<hr>
<p style="text-align: center; color: #718096; font-size: 0.9em;">
Manual v1.0 — em constante atualização — LM - Importing 2U®
</p>
</body>
</html>"""

    nomes_abas = list(secoes.keys())
    abas = st.tabs([f"📄 {nome}" for nome in nomes_abas])

    for aba, nome in zip(abas, nomes_abas):
        with aba:
            st.markdown(secoes[nome])

    st.markdown("---")
    st.markdown("### 📥 Baixar o Manual")
    st.caption("Escolha o formato ideal para o seu uso:")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Baixar Manual (HTML)",
            data=html_completo.encode("utf-8"),
            file_name="Manual_CALC_MARKUP.html",
            mime="text/html",
            use_container_width=True,
        )
        st.caption("🖥️ **HTML** — abre bonito no navegador")

    with col2:
        st.download_button(
            label="⬇️ Baixar Manual (Markdown)",
            data=conteudo.encode("utf-8"),
            file_name="Manual_CALC_MARKUP.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.caption("✏️ **Markdown** — editável em qualquer editor")

    st.caption("💡 Manual v1.0 — em constante atualização.")
