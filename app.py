import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
import hashlib
import io

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="CALC MARKUP - LM - Importing 2U®",
    page_icon="Simulador.ico",
    layout="wide"
)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------------------------------------------------
# MIGRAÇÃO AUTOMÁTICA DO BANCO
# ---------------------------------------------------------
def migrar_banco(conn):
    """
    Executa migrações idempotentes:
    - Renomeia products.custo_usd -> custo_unit (se existir)
    - Adiciona products.categoria (se não existir)
    """
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            sku TEXT,
            custo_unit REAL,
            frete_unit REAL,
            markup REAL,
            preco_venda REAL,
            categoria TEXT,
            data_cadastro TEXT
        )
    ''')

    cursor.execute("PRAGMA table_info(products)")
    colunas = [row[1] for row in cursor.fetchall()]

    if "custo_usd" in colunas and "custo_unit" not in colunas:
        cursor.execute("ALTER TABLE products RENAME COLUMN custo_usd TO custo_unit")
        conn.commit()

    if "categoria" not in colunas:
        cursor.execute("ALTER TABLE products ADD COLUMN categoria TEXT DEFAULT 'Geral'")
        conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            data_criacao TEXT
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        senha_admin = hash_password("admin123")
        conn.execute(
            "INSERT INTO users (username, password, role, data_criacao) VALUES (?, ?, ?, ?)",
            ("admin", senha_admin, "Administrador", datetime.now().strftime("%Y-%m-%d"))
        )
        conn.commit()


def get_connection():
    conn = sqlite3.connect("database.db", check_same_thread=False)
    migrar_banco(conn)
    return conn

# ---------------------------------------------------------
# FUNÇÕES AUXILIARES DE IMPORTAÇÃO
# ---------------------------------------------------------
SINONIMOS_COLUNAS = {
    "nome":       ["nome", "produto", "descrição", "descricao", "item", "name", "product"],
    "sku":        ["sku", "código", "codigo", "cod", "ref", "referência", "referencia"],
    "custo_unit": ["custo_unit", "custo usd", "custo", "cost", "custo unitário",
                   "custo unitario", "custo origem", "valor unit", "valor unitário"],
    "frete_unit": ["frete_unit", "frete unit", "frete unitário", "frete unitario",
                   "frete", "shipping", "taxa de frete", "taxa frete"],
    "markup":     ["markup", "mark up", "fator", "multiplicador"],
    "preco_venda":["preco_venda", "preço venda", "preco venda", "preço de venda",
                   "preco de venda", "valor de venda", "preco final", "preço final",
                   "preco", "preço", "price", "valor do produto"],
    "categoria":  ["categoria", "category", "grupo", "planilha", "aba", "tipo"],
}


def detectar_coluna(df_colunas, campo_interno):
    sinonimos = SINONIMOS_COLUNAS.get(campo_interno, [])
    cols_lower = {c.lower().strip(): c for c in df_colunas}
    for sin in sinonimos:
        if sin in cols_lower:
            return cols_lower[sin]
    for sin in sinonimos:
        for col_lower, col_orig in cols_lower.items():
            if sin in col_lower or col_lower in sin:
                return col_orig
    return None


def ler_arquivo_tolerante(uploaded_file):
    """Lê CSV (múltiplas tentativas) ou XLSX."""
    nome = uploaded_file.name.lower()

    if nome.endswith((".xlsx", ".xls")):
        try:
            xls = pd.ExcelFile(uploaded_file)
            if len(xls.sheet_names) == 1:
                df = xls.parse(xls.sheet_names[0])
                return df, {"tipo": "xlsx", "aba": xls.sheet_names[0],
                            "abas_disponiveis": xls.sheet_names}
            return xls, {"tipo": "xlsx_multi", "abas_disponiveis": xls.sheet_names}
        except Exception as e:
            return None, {"tipo": "erro", "msg": f"Falha ao ler Excel: {e}"}

    tentativas = [
        {'sep': ',',  'encoding': 'utf-8'},
        {'sep': ';',  'encoding': 'utf-8'},
        {'sep': ',',  'encoding': 'latin-1'},
        {'sep': ';',  'encoding': 'latin-1'},
        {'sep': ',',  'encoding': 'utf-8-sig'},
        {'sep': ';',  'encoding': 'utf-8-sig'},
        {'sep': '\t', 'encoding': 'utf-8'},
    ]
    for params in tentativas:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, on_bad_lines='skip', engine='python', **params)
            if df.shape[1] > 1:
                return df, {"tipo": "csv", **params}
        except Exception:
            continue
    return None, {"tipo": "erro", "msg": "Não foi possível ler o CSV."}


def to_float(v):
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

# ---------------------------------------------------------
# PÁGINAS
# ---------------------------------------------------------
def render_home():
    st.title("🏠 Bem-vindo(a) ao CALC MARKUP")
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
    st.title("📊 Dashboard Executivo & Gráficos")
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM products", conn)

    categorias = ["(todas)"] + sorted(
        [c for c in df["categoria"].dropna().unique().tolist() if c]
    ) if not df.empty else ["(todas)"]
    cat_escolhida = st.selectbox("Filtrar por categoria", categorias, index=0)
    if cat_escolhida != "(todas)":
        df = df[df["categoria"] == cat_escolhida]

    conn.close()

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
    st.title("🛒 Cadastrar Novo Produto")
    with st.form("form_cad_produto"):
        st.subheader("Custos de Importação (China ➔ Brasil)")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Produto",
                                 placeholder="Ex: Protetor de Cabo Silicone Tipo C (Kit 4 Pares)")
            sku = st.text_input("SKU / Código", placeholder="Ex: PROT-TC-04")
            custo_unit = st.number_input("Custo Unitário (R$)", min_value=0.0,
                                         format="%.2f", value=1.50)
            frete_unit = st.number_input("Frete Internacional Unitário (R$)",
                                         min_value=0.0, format="%.2f", value=0.80)
        with col2:
            categoria = st.text_input("Categoria", value="Geral",
                                      placeholder="Ex: Cameras, Cabos, Kits")
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
                conn = get_connection()
                conn.execute('''
                    INSERT INTO products
                    (nome, sku, custo_unit, frete_unit, markup, preco_venda, categoria, data_cadastro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (nome, sku, custo_unit, frete_unit, markup, preco_venda,
                      categoria or "Geral", datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                conn.close()
                st.success(f"Produto '{nome}' salvo! Preço Sugerido: R$ {preco_venda:.2f}")
            else:
                st.warning("Preencha o Nome e o SKU do produto.")


# ---------------------------------------------------------
# IMPORTAÇÃO COM CATEGORIA + DRY-RUN
# ---------------------------------------------------------
def render_csv_import():
    st.title("📁 Importar Produtos via CSV / Excel")
    st.markdown("Faça o upload de uma planilha **CSV** ou **Excel (.xlsx)**.")

    uploaded_file = st.file_uploader("Selecione o arquivo",
                                     type=["csv", "xlsx", "xls"])

    if not uploaded_file:
        st.markdown("---")
        st.subheader("📤 Exportar modelo de CSV")
        exemplo = pd.DataFrame([
            {"nome": "Protetor de Cabo Silicone Tipo C", "categoria": "Cabos",
             "custo_unit": 0.04, "frete_unit": 0.80,
             "markup": 2.5, "preco_venda": 5.30},
            {"nome": "Protetor de Privacidade de Câmera", "categoria": "Cameras",
             "custo_unit": 0.02, "frete_unit": 0.50,
             "markup": 2.5, "preco_venda": 3.80},
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

    df, info = ler_arquivo_tolerante(uploaded_file)

    if info["tipo"] == "xlsx_multi":
        st.info("O arquivo Excel contém várias abas. Escolha uma para importar:")
        aba = st.selectbox("Aba", info["abas_disponiveis"])
        df = df.parse(aba)
        info = {"tipo": "xlsx", "aba": aba}

    if df is None or (hasattr(df, "shape") and df.shape[1] < 2):
        st.error("❌ Não foi possível ler o arquivo.")
        st.stop()

    if info["tipo"] == "csv":
        st.success(f"✅ CSV lido! Separador='{info['sep']}', "
                   f"Encoding='{info['encoding']}' — "
                   f"{len(df)} linhas, {df.shape[1]} colunas.")
    else:
        st.success(f"✅ Excel lido! Aba='{info['aba']}' — "
                   f"{len(df)} linhas, {df.shape[1]} colunas.")

    with st.expander("👀 Ver dados brutos importados", expanded=False):
        st.dataframe(df.head(50), use_container_width=True)

    st.markdown("### 🔧 Mapeamento de Colunas")
    st.caption("Pré-selecionado automaticamente quando possível.")

    colunas_csv = ["(nenhuma)"] + list(df.columns)

    def idx_detectado(campo):
        col = detectar_coluna(df.columns, campo)
        if col is None:
            return 0
        try:
            return colunas_csv.index(col)
        except ValueError:
            return 0

    col1, col2 = st.columns(2)
    with col1:
        col_nome      = st.selectbox("Coluna → Nome do Produto",
                                     colunas_csv, index=idx_detectado("nome"))
        col_sku       = st.selectbox("Coluna → SKU / Código",
                                     colunas_csv, index=idx_detectado("sku"))
        col_custo     = st.selectbox("Coluna → Custo Unitário (R$)",
                                     colunas_csv, index=idx_detectado("custo_unit"))
    with col2:
        col_frete     = st.selectbox("Coluna → Frete Unitário (R$)",
                                     colunas_csv, index=idx_detectado("frete_unit"))
        col_preco     = st.selectbox("Coluna → Preço de Venda (R$)",
                                     colunas_csv, index=idx_detectado("preco_venda"))
        col_categoria = st.selectbox("Coluna → Categoria",
                                     colunas_csv, index=idx_detectado("categoria"))

    st.markdown("### ⚙️ Opções de Importação")
    opt1, opt2 = st.columns(2)
    with opt1:
        modo = st.radio(
            "Modo de gravação",
            ["Inserir todos (append)", "Atualizar se SKU existir (upsert)"],
            help="Upsert precisa de SKU preenchido."
        )
    with opt2:
        pular_sem_nome = st.checkbox("Pular linhas sem nome de produto", value=True)

    st.markdown("### 🔎 Prévia do que será gravado")
    preview_rows = []
    for _, row in df.iterrows():
        nome      = str(row[col_nome]).strip()      if col_nome      != "(nenhuma)" else ""
        sku       = str(row[col_sku]).strip()       if col_sku       != "(nenhuma)" else ""
        custo     = to_float(row[col_custo])        if col_custo     != "(nenhuma)" else 0.0
        frete     = to_float(row[col_frete])        if col_frete     != "(nenhuma)" else 0.0
        preco     = to_float(row[col_preco])        if col_preco     != "(nenhuma)" else 0.0
        categoria = str(row[col_categoria]).strip() if col_categoria != "(nenhuma)" else "Geral"

        if pular_sem_nome and not nome:
            continue

        markup = 2.5
        if preco == 0.0:
            preco = ((custo * 5.5) + frete) * markup

        preview_rows.append({
            "nome": nome,
            "sku": sku,
            "custo_unit": round(custo, 4),
            "frete_unit": round(frete, 4),
            "markup": markup,
            "preco_venda": round(preco, 2),
            "categoria": categoria or "Geral",
        })

    if not preview_rows:
        st.warning("Nenhuma linha válida para importar.")
        st.stop()

    df_preview = pd.DataFrame(preview_rows)
    st.dataframe(df_preview, use_container_width=True)
    st.caption(f"Total de **{len(df_preview)}** linhas válidas "
               f"de **{len(df)}** linhas lidas.")

    st.markdown("### 🚀 Executar")
    btn1, btn2 = st.columns(2)
    with btn1:
        simular = st.button("🔍 Simular (dry-run)", use_container_width=True)
    with btn2:
        processar = st.button("🚀 Processar Lote", use_container_width=True, type="primary")

    if simular or processar:
        conn = get_connection()
        inseridos = atualizados = erros = 0
        log_erros = []

        for linha in preview_rows:
            try:
                if modo.startswith("Atualizar") and linha["sku"]:
                    cur = conn.execute("SELECT id FROM products WHERE sku = ?",
                                       (linha["sku"],))
                    existente = cur.fetchone()
                    if existente:
                        if processar:
                            conn.execute('''
                                UPDATE products
                                   SET nome=?, custo_unit=?, frete_unit=?, markup=?,
                                       preco_venda=?, categoria=?, data_cadastro=?
                                 WHERE id=?
                            ''', (linha["nome"], linha["custo_unit"],
                                  linha["frete_unit"], linha["markup"],
                                  linha["preco_venda"], linha["categoria"],
                                  datetime.now().strftime("%Y-%m-%d"),
                                  existente[0]))
                        atualizados += 1
                        continue

                if processar:
                    conn.execute('''
                        INSERT INTO products
                        (nome, sku, custo_unit, frete_unit, markup,
                         preco_venda, categoria, data_cadastro)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (linha["nome"], linha["sku"], linha["custo_unit"],
                          linha["frete_unit"], linha["markup"],
                          linha["preco_venda"], linha["categoria"],
                          datetime.now().strftime("%Y-%m-%d")))
                inseridos += 1
            except Exception as e:
                erros += 1
                log_erros.append(str(e))

        if processar:
            conn.commit()
        conn.close()

        titulo = "🔍 Simulação concluída" if simular else "✅ Importação concluída"
        st.success(
            f"{titulo}! Inseridos: **{inseridos}** | "
            f"Atualizados: **{atualizados}** | Erros: **{erros}**"
            + ("\n\n_(Nenhum dado foi gravado — apenas simulação.)_" if simular else "")
        )
        if log_erros:
            with st.expander("Ver detalhes dos erros"):
                for e in log_erros[:20]:
                    st.code(e)


def render_products_list():
    st.title("📦 Lista de Produtos")
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

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
    st.metric("Preço Final com Desconto",
              f"R$ {novo_preco:.2f}", f"-{desconto}%")


def render_wholesale():
    st.title("🛒 Estratégia de Atacado & Kits")
    kit = st.selectbox("Selecione a Variação",
                       ["Kit 1 Par", "Kit 2 Pares", "Kit 4 Pares", "Kit 8 Pares"])
    desc_lote = st.slider("Desconto para o volume selecionado (%)", 0, 40, 15)
    st.info(f"Regra configurada: {desc_lote}% de desconto para {kit}.")


def render_stock_control():
    st.title("📋 Controle de Estoque & Expedição")
    st.warning("⚠️ Alerta: SKU PROT-TC-04 está com estoque baixo (18 unidades).")
    render_products_list()


def render_reports():
    st.title("📄 Relatórios & Exportação")
    st.markdown("Gere relatórios para conferência ou balanço financeiro.")
    st.download_button("Baixar Tabela de Preços (CSV)",
                       "id,nome,preco\n1,Protetor,29.90",
                       "tabela_lm.csv", "text/csv")


def render_settings():
    st.title("⚙️ Configurações Globais")
    st.text_input("Nome da Operação", value="LM - Importing 2U®")
    st.number_input("Cotação Fixa do Dólar (USD para BRL)",
                    value=5.50, format="%.2f")
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
                        conn.execute(
                            "INSERT INTO users (username, password, role, data_criacao) VALUES (?, ?, ?, ?)",
                            (novo_user.strip(), hash_password(nova_senha),
                             perfil, datetime.now().strftime("%Y-%m-%d"))
                        )
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
        df_users = pd.read_sql_query(
            "SELECT id, username, role, data_criacao FROM users", conn)
        conn.close()
        st.dataframe(df_users, use_container_width=True)

    with tab2:
        st.subheader("Registro de Atividades")
        st.info("Nenhum log recente de alteração de preços.")


# ---------------------------------------------------------
# 📘 PÁGINA: MANUAL (abas + downloads HTML e Markdown)
# ---------------------------------------------------------
def render_manual():
    """Renderiza a página do Manual de Uso em abas temáticas + downloads HTML/MD."""
    st.title("📘 Manual de Uso — CALC MARKUP")
    st.markdown("Bem-vindo ao manual interativo. Navegue pelas abas abaixo.")
    st.markdown("---")

    manual_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manual.md")

    if not os.path.exists(manual_path):
        st.error("❌ Arquivo `manual.md` não encontrado na pasta do app.")
        st.info("Certifique-se de que o `manual.md` está no mesmo diretório do `app.py`.")
        return

    try:
        with open(manual_path, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except Exception as e:
        st.error(f"❌ Erro ao ler o `manual.md`: {e}")
        return

    # Divide o manual em seções (cada "## X" vira uma aba)
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
        st.warning("Nenhuma seção encontrada no `manual.md`. Verifique o formato.")
        return

    # Gera HTML com CSS embutido
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
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Manual de Uso — CALC MARKUP</title>
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                     "Helvetica Neue", Arial, sans-serif;
        max-width: 960px;
        margin: 40px auto;
        padding: 20px 40px;
        line-height: 1.65;
        color: #2d3748;
        background-color: #f7fafc;
    }}
    h1 {{ color: #1a365d; border-bottom: 3px solid #3182ce; padding-bottom: 12px; margin-top: 40px; }}
    h2 {{ color: #2c5282; border-bottom: 2px solid #bee3f8; padding-bottom: 8px; margin-top: 36px; }}
    h3 {{ color: #2b6cb0; margin-top: 24px; }}
    code {{
        background-color: #edf2f7; color: #c53030; padding: 2px 6px;
        border-radius: 4px; font-family: "Consolas", "Monaco", monospace; font-size: 0.9em;
    }}
    pre {{
        background-color: #2d3748; color: #f7fafc; padding: 16px;
        border-radius: 8px; overflow-x: auto; line-height: 1.5;
    }}
    pre code {{ background-color: transparent; color: inherit; padding: 0; }}
    table {{
        border-collapse: collapse; width: 100%; margin: 20px 0;
        background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}
    th, td {{ border: 1px solid #cbd5e0; padding: 10px 14px; text-align: left; }}
    th {{ background-color: #3182ce; color: #ffffff; font-weight: 600; }}
    tr:nth-child(even) {{ background-color: #f7fafc; }}
    blockquote {{
        border-left: 4px solid #3182ce; padding-left: 16px; margin-left: 0;
        color: #4a5568; background-color: #ebf8ff; padding: 12px 16px; border-radius: 4px;
    }}
    ul, ol {{ padding-left: 28px; }}
    li {{ margin: 6px 0; }}
    hr {{ border: none; border-top: 2px solid #e2e8f0; margin: 32px 0; }}
    a {{ color: #3182ce; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .header {{
        text-align: center; margin-bottom: 40px; padding: 20px;
        background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%);
        color: white; border-radius: 12px;
    }}
    .header h1 {{ color: white; border: none; margin: 0; }}
    .header p {{ margin: 8px 0 0 0; opacity: 0.9; }}
    @media print {{
        body {{ background-color: white; margin: 0; padding: 20px; }}
        .header {{ background: #3182ce !important; -webkit-print-color-adjust: exact; }}
    }}
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

    # Renderiza as abas no app
    nomes_abas = list(secoes.keys())
    abas = st.tabs([f"📄 {nome}" for nome in nomes_abas])

    for aba, nome in zip(abas, nomes_abas):
        with aba:
            st.markdown(secoes[nome])

    st.markdown("---")

    # Botões de download
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
            help="Abre com duplo-clique em qualquer navegador, já formatado.",
        )
        st.caption("🖥️ **HTML** — abre bonito no navegador")

    with col2:
        st.download_button(
            label="⬇️ Baixar Manual (Markdown)",
            data=conteudo.encode("utf-8"),
            file_name="Manual_CALC_MARKUP.md",
            mime="text/markdown",
            use_container_width=True,
            help="Formato editável, abre no VSCode ou Bloco de Notas.",
        )
        st.caption("✏️ **Markdown** — editável em qualquer editor de texto")

    st.caption("💡 Manual v1.0 — em constante atualização.")


# ---------------------------------------------------------
# LOGIN E NAVEGAÇÃO
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
        st.markdown("<h2 style='text
