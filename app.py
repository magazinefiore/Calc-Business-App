import streamlit as st
import pandas as pd
import database as db
import auth
import utils

# Configuração Geral do Streamlit
st.set_page_config(
    page_title="CALC BUSINESS - LM Importing 2U",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Banco de Dados
db.init_db()
auth.create_initial_admin()

# Estilização CSS Customizada
st.markdown("""
<style>
    .main-title {
        color: #1E3A8A;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #4B5563;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }
    .stMetric {
        background-color: #F3F4F6;
        padding: 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Gerenciamento de Sessão de Login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

# --- TELA DE LOGIN ---
if not st.session_state['logged_in']:
    st.markdown("<div class='main-title'>CALC BUSINESS</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>LM Importing 2U - Sistema de Precificação e Gestão</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔑 Acesso ao Sistema")
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit:
                user = auth.authenticate_user(username, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_info'] = user
                    db.log_audit(user['username'], "Login", "Usuário autenticado no sistema.")
                    st.success(f"Bem-vindo(a), {user['name']}!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.stop()

# --- SIDEBAR (NAVEGAÇÃO) ---
st.sidebar.markdown("## **CALC BUSINESS**")
st.sidebar.markdown("##### *LM Importing 2U*")
st.sidebar.write(f"👤 **{st.session_state['user_info']['name']}** ({st.session_state['user_info']['role']})")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Navegação:",
    [
        "📊 Dashboard & Gráficos",
        "🛒 Cadastro de Produtos",
        "🧮 Calculadora de Formação de Preço",
        "🏷️ Simulador de Descontos",
        "📦 Controle de Estoque",
        "📄 Relatórios & Exportação",
        "👤 Usuários & Logs de Auditoria"
    ]
)

st.sidebar.divider()
if st.sidebar.button("🚪 Sair (Logout)", use_container_width=True):
    db.log_audit(st.session_state['user_info']['username'], "Logout", "Usuário encerrou a sessão.")
    st.session_state['logged_in'] = False
    st.session_state['user_info'] = None
    st.rerun()

# --- MÓDULO 1: DASHBOARD & GRÁFICOS ---
if menu == "📊 Dashboard & Gráficos":
    st.title("📊 Dashboard Executivo & Gráficos")
    st.caption("Visão geral de produtos, lucratividade e estoque da LM Importing 2U.")

    df_products = db.get_all_products()

    if df_products.empty:
        st.warning("Nenhum produto cadastrado até o momento. Acesse '🛒 Cadastro de Produtos' para iniciar.")
    else:
        # KPIs Superiores
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        total_items = len(df_products)
        total_stock = df_products['current_stock'].sum()
        total_investment = (df_products['c_base'] * df_products['current_stock']).sum()

        # Cálculo de Venda Estimada Total
        total_est_sales = 0
        for _, r in df_products.iterrows():
            p_res = utils.calculate_pricing(r['c_base'], r['tax_pct'], r['marketplace_pct'], r['shipping_fixed'], r['margin_desired_pct'])
            total_est_sales += p_res['pv_suggested'] * r['current_stock']

        kpi1.metric("Total de Produtos", f"{total_items} SKUs")
        kpi2.metric("Itens em Estoque", f"{total_stock} un")
        kpi3.metric("Investimento em Custos", f"R$ {total_investment:,.2f}")
        kpi4.metric("Faturamento Estimado", f"R$ {total_est_sales:,.2f}")

        st.divider()

        # Gráficos
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_bar = utils.create_bar_comparison_chart(df_products)
            if fig_bar:
                st.plotly_chart(fig_bar, use_container_width=True)

        with col_g2:
            fig_scatter = utils.create_margin_stock_scatter(df_products)
            if fig_scatter:
                st.plotly_chart(fig_scatter, use_container_width=True)

# --- MÓDULO 2: CADASTRO DE PRODUTOS ---
elif menu == "🛒 Cadastro de Produtos":
    st.title("🛒 Cadastro & Gestão de Produtos")
    
    tab1, tab2 = st.tabs(["📝 Cadastro Manual", "📁 Importação em Lote (.xlsx/.csv)"])

    with tab1:
        st.subheader("Cadastrar Novo Item")
        with st.form("form_add_product", clear_on_submit=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                sku = st.text_input("SKU / Código do Produto*", placeholder="Ex: CABO-SIL-01")
                name = st.text_input("Nome do Produto*", placeholder="Ex: Protetor de Cabo USB Silicone")
                category = st.text_input("Categoria", value="Acessórios")
                supplier = st.text_input("Fornecedor", value="China Import")
            
            with col_b:
                c_base = st.number_input("Custo de Aquisição/Importação (R$)*", min_value=0.01, value=10.0, step=0.5)
                tax_pct = st.number_input("Impostos / Simples Nacional (%)*", min_value=0.0, value=6.0, step=0.5)
                marketplace_pct = st.number_input("Taxa de Marketplace / Comissão (%)*", min_value=0.0, value=18.0, step=0.5)
            
            with col_c:
                shipping_fixed = st.number_input("Frete Fixo / Custo Operacional (R$)*", min_value=0.0, value=5.0, step=0.5)
                margin_desired_pct = st.number_input("Margem de Lucro Desejada (%)*", min_value=0.0, value=20.0, step=1.0)
                current_stock = st.number_input("Estoque Inicial (unidades)", min_value=0, value=50, step=1)
                min_stock = st.number_input("Estoque Mínimo (Alerta)", min_value=0, value=10, step=1)

            submit_prod = st.form_submit_button("Salvar Produto", use_container_width=True)

            if submit_prod:
                if not sku or not name:
                    st.error("Por favor, preencha os campos obrigatórios (SKU e Nome).")
                else:
                    data = {
                        "sku": sku, "name": name, "category": category, "supplier": supplier,
                        "c_base": c_base, "tax_pct": tax_pct, "marketplace_pct": marketplace_pct,
                        "shipping_fixed": shipping_fixed, "margin_desired_pct": margin_desired_pct,
                        "min_stock": min_stock, "current_stock": current_stock
                    }
                    try:
                        db.insert_product(data, st.session_state['user_info']['username'])
                        st.success(f"Produto '{name}' cadastrado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao salvar produto (SKU duplicado?): {e}")

    with tab2:
        st.subheader("Importar Planilha de Produtos")
        st.write("Baixe a planilha modelo para preencher os dados corretamente antes de importar.")
        
        template_bytes = utils.generate_excel_template()
        st.download_button(
            label="📥 Baixar Planilha Modelo (.xlsx)",
            data=template_bytes,
            file_name="modelo_cadastro_lm_importing.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        uploaded_file = st.file_uploader("Selecione o arquivo Excel ou CSV", type=["xlsx", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)
                
                st.write("📌 **Prévia dos dados carregados:**")
                st.dataframe(df_upload.head(), use_container_width=True)
                
                if st.button("Confirmar Importação de Todos os Itens"):
                    count = 0
                    for _, row in df_upload.iterrows():
                        p_data = {
                            "sku": str(row["SKU"]),
                            "name": str(row["Nome"]),
                            "category": str(row.get("Categoria", "Geral")),
                            "supplier": str(row.get("Fornecedor", "Importação")),
                            "c_base": float(row["Custo_Base"]),
                            "tax_pct": float(row["Imposto_Pct"]),
                            "marketplace_pct": float(row["Marketplace_Pct"]),
                            "shipping_fixed": float(row["Frete_Fixo"]),
                            "margin_desired_pct": float(row["Margem_Desejada_Pct"]),
                            "min_stock": int(row.get("Estoque_Minimo", 5)),
                            "current_stock": int(row.get("Estoque_Inicial", 0))
                        }
                        try:
                            db.insert_product(p_data, st.session_state['user_info']['username'])
                            count += 1
                        except:
                            pass
                    st.success(f"{count} produtos importados com sucesso!")
            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")

# --- MÓDULO 3: CALCULADORA DE FORMAÇÃO DE PREÇO ---
elif menu == "🧮 Calculadora de Formação de Preço":
    st.title("🧮 Calculadora & Motor de Precificação")
    st.caption("Simule ou recalcule individualmente a formação do preço de venda de um produto.")

    df_p = db.get_all_products()
    
    use_preset = st.checkbox("Carregar dados de um produto já cadastrado")
    
    if use_preset and not df_p.empty:
        selected_prod_name = st.selectbox("Selecione o Produto:", df_p['name'].tolist())
        prod_row = df_p[df_p['name'] == selected_prod_name].iloc[0]
        
        c_base = prod_row['c_base']
        tax_pct = prod_row['tax_pct']
        mkt_pct = prod_row['marketplace_pct']
        shipping_fixed = prod_row['shipping_fixed']
        margin_pct = prod_row['margin_desired_pct']
    else:
        c_base = st.number_input("Custo Base (R$)", value=20.0, step=1.0)
        tax_pct = st.number_input("Imposto / Simples (%)", value=6.0, step=0.5)
        mkt_pct = st.number_input("Comissão Marketplace (%)", value=18.0, step=0.5)
        shipping_fixed = st.number_input("Frete Fixo / Embalagem (R$)", value=6.0, step=0.5)
        margin_pct = st.number_input("Margem Desejada (%)", value=20.0, step=1.0)

    # Executa o Motor de Cálculo
    res = utils.calculate_pricing(c_base, tax_pct, mkt_pct, shipping_fixed, margin_pct)

    st.divider()
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Preço de Venda Sugerido", f"R$ {res['pv_suggested']:.2f}")
    col_r2.metric("Ponto de Equilíbrio (Mínimo)", f"R$ {res['pv_breakeven']:.2f}")
    col_r3.metric("Lucro Líquido (R$)", f"R$ {res['net_profit']:.2f}")
    col_r4.metric("Margem Líquida Real (%)", f"{res['real_net_margin']:.2f}%")

    st.divider()
    
    col_m1, col_m2 = st.columns([1, 1])
    with col_m1:
        st.subheader("📋 Resumo da Decomposição de Custos")
        st.write(f"- **Custo Base:** R$ {c_base:.2f}")
        st.write(f"- **Frete Fixo / Embalagem:** R$ {shipping_fixed:.2f}")
        st.write(f"- **Impostos Calculados:** R$ {res['tax_val']:.2f} ({tax_pct}%)")
        st.write(f"- **Taxa de Marketplace:** R$ {res['mkt_val']:.2f} ({mkt_pct}%)")
        st.write(f"- **Lucro Bruto (PV - Custo Base):** R$ {res['gross_profit']:.2f}")
        st.write(f"- **Lucro Líquido Final:** R$ {res['net_profit']:.2f}")
    
    with col_m2:
        fig_pie = utils.create_cost_pie_chart(c_base, shipping_fixed, res['tax_val'], res['mkt_val'], res['net_profit'])
        st.plotly_chart(fig_pie, use_container_width=True)

# --- MÓDULO 4: SIMULADOR DE DESCONTOS ---
elif menu == "🏷️ Simulador de Descontos":
    st.title("🏷️ Simulador Interativo de Descontos")
    st.caption("Verifique o impacto financeiro de concessão de descontos e proteja a margem de lucro.")

    df_p = db.get_all_products()
    if df_p.empty:
        st.warning("Cadastre produtos antes de utilizar o simulador.")
    else:
        selected_p = st.selectbox("Selecione o Produto para Simulação:", df_p['name'].tolist())
        p_info = df_p[df_p['name'] == selected_p].iloc[0]

        # Cálculo do Preço Original
        orig_res = utils.calculate_pricing(
            p_info['c_base'], p_info['tax_pct'], p_info['marketplace_pct'],
            p_info['shipping_fixed'], p_info['margin_desired_pct']
        )
        pv_original = orig_res['pv_suggested']
        pv_breakeven = orig_res['pv_breakeven']

        st.info(f"**Preço Original Tabela:** R$ {pv_original:.2f} | **Ponto de Equilíbrio (Custo Zero Lucro):** R$ {pv_breakeven:.2f}")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            discount_type = st.radio("Tipo de Desconto:", ["Percentual (%)", "Valor Fixo (R$)"])
        with col_d2:
            if discount_type == "Percentual (%)":
                discount_pct = st.slider("Desconto (%)", 0.0, 50.0, 5.0, step=0.5)
                discount_val = pv_original * (discount_pct / 100.0)
            else:
                discount_val = st.number_input("Valor do Desconto (R$)", min_value=0.0, max_value=pv_original, value=5.0)
                discount_pct = (discount_val / pv_original * 100.0) if pv_original > 0 else 0

        pv_final = pv_original - discount_val
        
        # Recalcular métricas para o novo preço final
        tax_val_new = pv_final * (p_info['tax_pct'] / 100.0)
        mkt_val_new = pv_final * (p_info['marketplace_pct'] / 100.0)
        new_net_profit = pv_final - (p_info['c_base'] + p_info['shipping_fixed'] + tax_val_new + mkt_val_new)
        new_margin_pct = (new_net_profit / pv_final * 100.0) if pv_final > 0 else 0.0

        st.divider()

        # Indicadores Visuais de Segurança
        if pv_final < pv_breakeven:
            st.error(f"🔴 **OPERAÇÃO NO PREJUÍZO!** O preço final (R$ {pv_final:.2f}) está abaixo do Ponto de Equilíbrio (R$ {pv_breakeven:.2f}). Lucro Líquido: R$ {new_net_profit:.2f}")
            status_flag = "VERMELHO (Prejuízo)"
        elif new_margin_pct < p_info['margin_desired_pct']:
            st.warning(f"🟡 **ATENÇÃO:** A margem final ({new_margin_pct:.2f}%) ficou abaixo da margem desejada ({p_info['margin_desired_pct']}%), mas a operação ainda gera lucro (R$ {new_net_profit:.2f}).")
            status_flag = "AMARELO (Abaixo do Meta)"
        else:
            st.success(f"🟢 **MARGEM SEGURA!** A margem final ({new_margin_pct:.2f}%) atende à meta estabelecida. Lucro Líquido: R$ {new_net_profit:.2f}")
            status_flag = "VERDE (Seguro)"

        # Tabela Comparativa Dinâmica
        st.subheader("📊 Relatório Dinâmico da Operação")
        df_sim = pd.DataFrame([{
            "Produto": p_info['name'],
            "Preço Original": f"R$ {pv_original:.2f}",
            "Desconto Aplicado": f"{discount_pct:.1f}% (R$ {discount_val:.2f})",
            "Preço Final": f"R$ {pv_final:.2f}",
            "Novo Lucro (R$)": f"R$ {new_net_profit:.2f}",
            "Nova Margem (%)": f"{new_margin_pct:.2f}%",
            "Status": status_flag,
            "Usuário Responsável": st.session_state['user_info']['name']
        }])
        st.dataframe(df_sim, use_container_width=True)

        if st.button("Registrar Concessão de Desconto em Trilha de Auditoria"):
            db.log_audit(
                st.session_state['user_info']['username'],
                "Simulação / Concessão de Desconto",
                f"Produto: {p_info['name']} | Desc: {discount_pct:.1f}% | Preço Final: R$ {pv_final:.2f} | Status: {status_flag}"
            )
            st.success("Ação registrada com sucesso no Log de Auditoria!")

# --- MÓDULO 5: CONTROLE DE ESTOQUE ---
elif menu == "📦 Controle de Estoque":
    st.title("📦 Controle & Movimentação de Estoque")

    df_p = db.get_all_products()
    if df_p.empty:
        st.warning("Nenhum produto em estoque.")
    else:
        # Alerta de Estoque Baixo
        low_stock = df_p[df_p['current_stock'] <= df_p['min_stock']]
        if not low_stock.empty:
            st.error(f"⚠️ **Atenção:** Existem {len(low_stock)} produto(s) com nível de estoque abaixo do mínimo parametrizado!")
            st.dataframe(low_stock[['sku', 'name', 'current_stock', 'min_stock']], use_container_width=True)

        st.divider()

        st.subheader("Registrar Movimentação de Estoque")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            prod_selected = st.selectbox("Selecione o Produto", df_p['name'].tolist())
            prod_id = df_p[df_p['name'] == prod_selected]['id'].values[0]
        
        with col_m2:
            mtype = st.selectbox("Tipo de Movimento", ["ENTRADA", "SAIDA"])
        
        with col_m3:
            qty = st.number_input("Quantidade", min_value=1, value=10, step=1)
        
        with col_m4:
            notes = st.text_input("Observação / Motivo", value="Ajuste Manual")

        if st.button("Gravar Movimentação", use_container_width=True):
            db.update_stock(prod_id, mtype, qty, st.session_state['user_info']['username'], notes)
            st.success("Movimentação registrada e estoque atualizado!")
            st.rerun()

        st.divider()
        st.subheader("Estoque Atual Consolidado")
        st.dataframe(df_p[['sku', 'name', 'category', 'current_stock', 'min_stock', 'c_base']], use_container_width=True)

# --- MÓDULO 6: RELATÓRIOS & EXPORTAÇÃO ---
elif menu == "📄 Relatórios & Exportação":
    st.title("📄 Relatórios Consolidados & Exportação")
    st.caption("Gere e faça o download dos relatórios completos do sistema.")

    df_products = db.get_all_products()
    
    if df_products.empty:
        st.warning("Sem dados suficientes para gerar relatórios.")
    else:
        # Tabela com cálculos completos
        report_data = []
        for _, row in df_products.iterrows():
            res = utils.calculate_pricing(row['c_base'], row['tax_pct'], row['marketplace_pct'], row['shipping_fixed'], row['margin_desired_pct'])
            report_data.append({
                "SKU": row['sku'],
                "Produto": row['name'],
                "Categoria": row['category'],
                "Fornecedor": row['supplier'],
                "Estoque Atual": row['current_stock'],
                "Custo Base (R$)": row['c_base'],
                "Imposto (%)": row['tax_pct'],
                "Marketplace (%)": row['marketplace_pct'],
                "Frete Fixo (R$)": row['shipping_fixed'],
                "Margem Meta (%)": row['margin_desired_pct'],
                "Preço Sugerido (R$)": round(res['pv_suggested'], 2),
                "Ponto Equilíbrio (R$)": round(res['pv_breakeven'], 2),
                "Lucro Líquido (R$)": round(res['net_profit'], 2),
                "Margem Real (%)": round(res['real_net_margin'], 2)
            })

        df_report = pd.DataFrame(report_data)
        st.dataframe(df_report, use_container_width=True)

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            excel_bytes = utils.export_df_to_excel(df_report)
            st.download_button(
                label="📥 Exportar Relatório em Excel (.xlsx)",
                data=excel_bytes,
                file_name="relatorio_precificacao_lm_importing.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_e2:
            csv_data = df_report.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar Relatório em CSV (.csv)",
                data=csv_data,
                file_name="relatorio_precificacao_lm_importing.csv",
                mime="text/csv",
                use_container_width=True
            )

# --- MÓDULO 7: USUÁRIOS & LOGS DE AUDITORIA ---
elif menu == "👤 Usuários & Logs de Auditoria":
    st.title("👤 Gestão de Usuários & Trilha de Auditoria")

    tab_u1, tab_u2 = st.tabs(["🔒 Cadastrar Novo Usuário", "📜 Log de Auditoria"])

    with tab_u1:
        st.subheader("Novo Usuário do Sistema")
        with st.form("form_new_user", clear_on_submit=True):
            new_username = st.text_input("Usuário (Login)")
            new_name = st.text_input("Nome Completo")
            new_email = st.text_input("E-mail")
            new_role = st.selectbox("Perfil / Função", ["Administrador", "Gerente", "Operador"])
            new_password = st.text_input("Senha", type="password")

            if st.form_submit_button("Cadastrar Usuário"):
                if new_username and new_password:
                    success, msg = auth.register_user(
                        new_username, new_password, new_name, new_email, new_role,
                        st.session_state['user_info']['username']
                    )
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.error("Preencha Usuário e Senha.")

    with tab_u2:
        st.subheader("Histórico de Ações (Audit Log)")
        df_logs = db.get_audit_logs()
        st.dataframe(df_logs, use_container_width=True)