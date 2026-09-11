import io
import pandas as pd
import plotly.express as px

def calculate_pricing(c_base: float, tax_pct: float, mkt_pct: float, shipping_fixed: float, margin_desired_pct: float):
    """
    Fórmula solicitada:
    PV = (C_base + F_fixo) / (1 - (I_% + M_% + L_%)/100)
    """
    total_rate_desired = (tax_pct + mkt_pct + margin_desired_pct) / 100.0
    total_rate_breakeven = (tax_pct + mkt_pct) / 100.0

    # Validação de alíquotas inválidas
    if total_rate_desired >= 1.0:
        pv_suggested = 0.0
    else:
        pv_suggested = (c_base + shipping_fixed) / (1.0 - total_rate_desired)

    if total_rate_breakeven >= 1.0:
        pv_breakeven = 0.0
    else:
        pv_breakeven = (c_base + shipping_fixed) / (1.0 - total_rate_breakeven)

    # Métricas calculadas para o Preço Sugerido
    tax_val = pv_suggested * (tax_pct / 100.0)
    mkt_val = pv_suggested * (mkt_pct / 100.0)
    gross_profit = pv_suggested - c_base
    net_profit = pv_suggested - (c_base + shipping_fixed + tax_val + mkt_val)
    real_net_margin = (net_profit / pv_suggested * 100.0) if pv_suggested > 0 else 0.0

    return {
        "pv_suggested": pv_suggested,
        "pv_breakeven": pv_breakeven,
        "tax_val": tax_val,
        "mkt_val": mkt_val,
        "gross_profit": gross_profit,
        "net_profit": net_profit,
        "real_net_margin": real_net_margin
    }

def generate_excel_template():
    df_template = pd.DataFrame([{
        "SKU": "PROD-001",
        "Nome": "Protetor Cabo Silicone USB (Par)",
        "Categoria": "Acessórios",
        "Fornecedor": "Shenzhen Supplier",
        "Custo_Base": 2.50,
        "Imposto_Pct": 6.0,
        "Marketplace_Pct": 18.0,
        "Frete_Fixo": 5.00,
        "Margem_Desejada_Pct": 25.0,
        "Estoque_Inicial": 100,
        "Estoque_Minimo": 10
    }])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_template.to_excel(writer, index=False, sheet_name='Modelo_Produtos')
    return output.getvalue()

def export_df_to_excel(df: pd.DataFrame):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    return output.getvalue()

def create_cost_pie_chart(c_base, shipping, tax_val, mkt_val, net_profit):
    data = {
        'Componente': ['Custo Base', 'Frete/Operacional', 'Impostos', 'Taxa Marketplace', 'Lucro Líquido'],
        'Valor (R$)': [c_base, shipping, tax_val, mkt_val, max(0, net_profit)]
    }
    df = pd.DataFrame(data)
    fig = px.pie(
        df, 
        values='Valor (R$)', 
        names='Componente', 
        title='Distribuição da Composição do Preço Final (R$)',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_bar_comparison_chart(df_products):
    if df_products.empty:
        return None
    
    chart_data = []
    for _, row in df_products.iterrows():
        res = calculate_pricing(row['c_base'], row['tax_pct'], row['marketplace_pct'], row['shipping_fixed'], row['margin_desired_pct'])
        chart_data.append({
            'Produto': row['name'],
            'Custo Base (R$)': row['c_base'],
            'Preço Venda (R$)': res['pv_suggested'],
            'Lucro Líquido (R$)': res['net_profit']
        })
    df_chart = pd.DataFrame(chart_data)
    fig = px.bar(
        df_chart, 
        x='Produto', 
        y=['Custo Base (R$)', 'Preço Venda (R$)', 'Lucro Líquido (R$)'],
        barmode='group',
        title='Comparativo: Custo vs. Preço de Venda vs. Lucro Líquido por Produto'
    )
    return fig

def create_margin_stock_scatter(df_products):
    if df_products.empty:
        return None
    
    data = []
    for _, row in df_products.iterrows():
        res = calculate_pricing(row['c_base'], row['tax_pct'], row['marketplace_pct'], row['shipping_fixed'], row['margin_desired_pct'])
        data.append({
            'Produto': row['name'],
            'Estoque': row['current_stock'],
            'Margem Líquida (%)': res['real_net_margin'],
            'Categoria': row['category']
        })
    df_scatter = pd.DataFrame(data)
    fig = px.scatter(
        df_scatter, 
        x='Estoque', 
        y='Margem Líquida (%)', 
        size='Estoque', 
        color='Categoria',
        hover_name='Produto',
        title='Relação: Margem Líquida (%) vs. Estoque Disponível'
    )
    return fig