"""
Módulo de Ajuda Contextual do CALC MARKUP
Exibe balões de ajuda 💡 em cada página do app.
"""

import streamlit as st


def ajuda_pagina(chave: str):
    """
    Exibe um botão 💡 com popover de ajuda contextual.

    Args:
        chave: identificador da página (ex: "dashboard", "produtos")
    """
    dados = AJUDAS.get(chave)
    if not dados:
        return

    with st.popover("💡", help="Clique para ver a ajuda desta página"):
        st.markdown(f"### {dados['titulo']}")
        st.markdown(f"**🎯 Objetivo:** {dados['objetivo']}")

        if dados.get("passos"):
            st.markdown("**📋 Como usar:**")
            for passo in dados["passos"]:
                st.markdown(f"- {passo}")

        if dados.get("dicas"):
            st.markdown("**💡 Dicas importantes:**")
            for dica in dados["dicas"]:
                st.markdown(f"- {dica}")

        if dados.get("atencao"):
            st.markdown("**⚠️ Atenção:**")
            for at in dados["atencao"]:
                st.markdown(f"- {at}")

        st.markdown("---")
        st.caption(f"📖 Consulte a aba **{dados['manual']}** no menu 📘 Manual.")


# =====================================================================
# CONTEÚDO DAS AJUDAS POR PÁGINA
# =====================================================================

AJUDAS = {

    # ---------------------------------------------------------------
    "inicio": {
        "titulo": "💡 Ajuda — Início",
        "objetivo": "Painel central de boas-vindas com atalhos rápidos.",
        "passos": [
            "Use o **menu lateral** para navegar entre as seções do app",
            "Passe o mouse sobre os cards para ver descrições rápidas",
        ],
        "dicas": [
            "Boa página para se orientar na primeira vez que usar o app",
            "O menu lateral está sempre disponível em todas as páginas",
        ],
        "manual": "Introdução",
    },

    # ---------------------------------------------------------------
    "dashboard": {
        "titulo": "💡 Ajuda — Dashboard & Gráficos",
        "objetivo": "Ver métricas consolidadas e comparativos visuais de preços.",
        "passos": [
            "Selecione uma categoria no filtro para segmentar a análise",
            "Observe os 4 cartões de métrica (total, markup médio, preço médio, canais)",
            "Passe o mouse nas barras do gráfico para ver valores exatos",
        ],
        "dicas": [
            "Use o filtro para comparar margens entre **Cameras**, **Kits** e **Cabos**",
            "O gráfico ordena automaticamente os produtos pelo nome",
            "Produtos com preços fora da curva aparecem como barras muito altas",
        ],
        "manual": "4. Dashboard",
    },

    # ---------------------------------------------------------------
    "cadastrar": {
        "titulo": "💡 Ajuda — Cadastrar Produto",
        "objetivo": "Cadastrar um produto individual com cálculo automático de preço.",
        "passos": [
            "Preencha **Nome** e **SKU** (ambos obrigatórios)",
            "Informe **Custo Unitário** e **Frete Internacional** em R$",
            "Escolha a **Categoria** (ex: Cameras, Cabos, Kits)",
            "Ajuste os percentuais de impostos e margem se necessário",
            "Clique em **Salvar e Calcular Preço**",
        ],
        "dicas": [
            "Use SKU único para facilitar buscas futuras (ex: `PROT-TC-04`)",
            "O preço é calculado automaticamente pela fórmula interna",
            "Para adicionar vários produtos de uma vez, use **Importar CSV**",
        ],
        "atencao": [
            "Nome e SKU são obrigatórios",
            "SKUs duplicados não são bloqueados, mas evite repetir",
        ],
        "manual": "5. Cadastrar Produto",
    },

    # ---------------------------------------------------------------
    "importar": {
        "titulo": "💡 Ajuda — Importar CSV / Excel",
        "objetivo": "Cadastrar vários produtos de uma vez a partir de um arquivo.",
        "passos": [
            "Prepare o CSV com colunas: `nome;categoria;custo_unit;frete_unit;preco_venda`",
            "Faça o upload do arquivo .csv, .xlsx ou .xls",
            "Confirme o **mapeamento das colunas** (vem pré-selecionado)",
            "Revise a **prévia** com os dados normalizados",
            "Clique em **🔍 Simular (dry-run)** para testar sem gravar",
            "Se OK → **🚀 Processar Lote** para gravar de verdade",
        ],
        "dicas": [
            "Aceita CSV com separadores `,` `;` ou TAB e encodings UTF-8, Latin-1, UTF-8-sig",
            "Detecta automaticamente colunas comuns (nome, custo, preço, etc.)",
            "No modo **upsert**, atualiza produtos existentes pelo SKU",
        ],
        "atencao": [
            "Sempre faça **backup do banco** antes de importar em lote",
            "Use **🔍 Simular** antes de clicar em 🚀 Processar Lote",
            "⚠️ No Streamlit Cloud, os dados podem ser perdidos ao reiniciar",
        ],
        "manual": "6. Importar CSV",
    },

    # ---------------------------------------------------------------
    "produtos": {
        "titulo": "💡 Ajuda — Lista de Produtos",
        "objetivo": "Listar todos os produtos cadastrados com filtros e ordenação.",
        "passos": [
            "Use o dropdown **Filtrar por categoria** para segmentar",
            "Clique nos cabeçalhos das colunas para ordenar (crescente/decrescente)",
            "Role horizontalmente para ver todas as colunas",
        ],
        "dicas": [
            "Ordene por `preco_venda` para identificar produtos fora da curva",
            "Use o filtro para conferir duplicados em uma categoria",
            "A tabela é exportável — veja **Relatórios & Exportação**",
        ],
        "manual": "7. Produtos",
    },

    # ---------------------------------------------------------------
    "calculadora": {
        "titulo": "💡 Ajuda — Calculadora de Formação de Preço",
        "objetivo": "Calcular o preço ideal de um produto sem salvar no banco.",
        "passos": [
            "Informe o **Custo Base** e o **Frete & Embalagem** em R$",
            "Ajuste os percentuais de **Impostos**, **Comissão**, **Custo Fixo** e **Lucro**",
            "O preço ideal aparece em verde automaticamente",
        ],
        "dicas": [
            "Use para simular antes de cadastrar um produto novo",
            "Combina bem com o **Simulador de Descontos** para testar promoções",
            "Fórmula: `preço = (custo + frete) / (1 - soma%)`",
        ],
        "atencao": [
            "A soma das porcentagens não pode ser ≥ 100%",
            "Se o divisor ficar negativo ou zero, o preço é inválido",
        ],
        "manual": "8. Calculadora",
    },

    # ---------------------------------------------------------------
    "simulador": {
        "titulo": "💡 Ajuda — Simulador de Descontos",
        "objetivo": "Ver o impacto de um desconto no preço final em tempo real.",
        "passos": [
            "Digite o **preço de venda atual** em R$",
            "Arraste o slider de **desconto** (0 a 50%)",
            "Leia o novo preço calculado automaticamente",
        ],
        "dicas": [
            "Use antes de aplicar uma promoção real",
            "Combine com a **Calculadora** para verificar se a margem continua positiva",
            "Descontos acima de 30% geralmente comprometem a margem",
        ],
        "manual": "9. Simulador",
    },

    # ---------------------------------------------------------------
    "atacado": {
        "titulo": "💡 Ajuda — Estratégia de Atacado",
        "objetivo": "Definir regras de desconto por volume (kits maiores).",
        "passos": [
            "Escolha a **variação** no dropdown (Kit 1, 2, 4 ou 8 pares)",
            "Ajuste o slider de **desconto** (0 a 40%)",
            "Veja a regra configurada na caixa azul",
        ],
        "dicas": [
            "Kits maiores geralmente aceitam descontos maiores",
            "Use para padronizar a política de atacado",
        ],
        "atencao": [
            "Esta página é **apenas informativa** — não grava regra no banco",
        ],
        "manual": "10. Atacado",
    },

    # ---------------------------------------------------------------
    "estoque": {
        "titulo": "💡 Ajuda — Controle de Estoque",
        "objetivo": "Monitorar estoque e emitir alertas de reposição.",
        "passos": [
            "Veja o alerta no topo da página (se houver)",
            "A tabela abaixo mostra todos os produtos cadastrados",
            "Use o filtro de categoria para segmentar",
        ],
        "dicas": [
            "Produtos com estoque baixo aparecem em alerta vermelho",
            "Combine com a página **Produtos** para editar quantidades",
        ],
        "atencao": [
            "O alerta atual está fixo no código (SKU PROT-TC-04)",
            "Melhoria futura: adicionar coluna `estoque_atual` no banco",
        ],
        "manual": "11. Controle de Estoque",
    },

    # ---------------------------------------------------------------
    "relatorios": {
        "titulo": "💡 Ajuda — Relatórios & Exportação",
        "objetivo": "Gerar arquivos para conferência, backup ou envio por e-mail.",
        "passos": [
            "Escolha o tipo de relatório desejado",
            "Clique em **Baixar Tabela de Preços (CSV)**",
            "O arquivo será baixado automaticamente",
        ],
        "dicas": [
            "Use para conferência offline dos preços",
            "Combine com o **Dashboard** para análise visual",
        ],
        "atencao": [
            "Hoje o botão baixa um CSV fixo de exemplo",
            "Melhoria futura: exportar dados reais do banco",
        ],
        "manual": "12. Relatórios",
    },

    # ---------------------------------------------------------------
    "configuracoes": {
        "titulo": "💡 Ajuda — Configurações Globais",
        "objetivo": "Ajustar parâmetros globais do sistema.",
        "passos": [
            "Edite o **Nome da Operação** se necessário",
            "Ajuste a **Cotação Fixa do Dólar (USD → BRL)**",
            "Clique em **Salvar Configurações**",
        ],
        "dicas": [
            "A cotação do dólar é usada nos cálculos de importação",
            "Atualize periodicamente conforme o mercado",
        ],
        "atencao": [
            "Hoje as configurações **não persistem no banco** — são apenas visuais",
        ],
        "manual": "13. Configurações",
    },

    # ---------------------------------------------------------------
    "usuarios": {
        "titulo": "💡 Ajuda — Usuários & Logs de Auditoria",
        "objetivo": "Gerenciar usuários do sistema e ver registros de atividades.",
        "passos": [
            "Na aba **👥 Cadastro de Usuários**, preencha Login, Senha e Perfil",
            "Clique em **Cadastrar Usuário**",
            "Role para baixo para ver a lista de usuários cadastrados",
            "Na aba **📋 Logs de Auditoria**, veja os registros",
        ],
        "dicas": [
            "Use perfis **Administrador** para quem precisa de acesso total",
            "Use **Operador** para acesso limitado",
            "Crie usuários individuais em vez de compartilhar login",
        ],
        "atencao": [
            "Nomes de usuário duplicados são bloqueados",
            "Login e senha são obrigatórios",
            "⚠️ Troque a senha do admin após o primeiro acesso!",
        ],
        "manual": "14. Usuários & Logs",
    },
}
