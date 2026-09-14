# 📘 Manual de Uso — CALC MARKUP

**LM - Importing 2U® — Sistema de Gestão e Precificação**

**Versão 1.0 — 13/09/2026**

---

## Introdução

Bem-vindo ao **CALC MARKUP**! Este é o sistema completo de gestão e precificação da **LM - Importing 2U®**.

Este manual foi criado para guiar você **passo a passo** por todas as funcionalidades do sistema, do cadastro de produtos até a geração de relatórios.

**Como usar este manual:**

- Use as abas acima para navegar entre os tópicos
- Cada seção explica **passo a passo** como executar as tarefas
- Você pode baixar este manual em **HTML** (para ler no navegador) ou **Markdown** (para editar)

---

## 1. Visão Geral

### O que é o CALC MARKUP?

O **CALC MARKUP** é o sistema de gestão e precificação da **LM - Importing 2U®**.

### O que você pode fazer aqui

- 📦 **Cadastrar produtos** com custo, frete, markup e preço de venda
- 📥 **Importar produtos em lote** via CSV ou Excel
- 📊 **Visualizar dashboards** com métricas por categoria
- 🧮 **Calcular preços** com margem, impostos e taxas
- 🏷️ **Simular descontos** e promoções
- 🛒 **Definir estratégias de atacado** por volume
- 📋 **Controlar estoque**
- 📄 **Gerar relatórios** e exportar dados
- 👥 **Gerenciar usuários** e permissões

### Stack técnico

- **Interface:** Streamlit (Python)
- **Banco de dados:** SQLite (`database.db`)
- **Autenticação:** SHA-256 + sessões

---

## 2. Login

### Como fazer login

1. Abra o app no navegador
2. Digite o **usuário** no campo "Usuário" (padrão: `admin`)
3. Digite a **senha** no campo "Senha" (padrão: `admin123`)
4. Clique em **Entrar no Sistema**

### Credenciais padrão (1º acesso)

| Campo | Valor |
|---|---|
| Usuário | `admin` |
| Senha | `admin123` |

⚠️ **Importante:** troque essa senha após o primeiro acesso (veja a seção **Usuários & Logs**).

### Como sair

No menu lateral (barra esquerda), clique em **Sair / Trocar Usuário**.

### Senha esquecida

Se esquecer a senha do `admin`, execute este script Python no terminal:

```python
import sqlite3, hashlib
conn = sqlite3.connect("database.db")
nova = hashlib.sha256("novasenha123".encode()).hexdigest()
conn.execute("UPDATE users SET password = ? WHERE username = 'admin'", (nova,))
conn.commit()
conn.close()
print("Senha do admin redefinida para: novasenha123")
```

### Erros comuns

- **"Credenciais inválidas"** → verifique maiúsculas/minúsculas
- **Não lembra a senha** → use o script acima

---

## 3. Início (Home)

### Objetivo

Tela de boas-vindas com atalhos rápidos.

### O que você vê

- 🏠 Título "Bem-vindo(a) ao CALC MARKUP"
- 3 cards informativos: **Visão Geral**, **Novo Produto**, **Calculadora Rápida**

### O que fazer aqui

Não há ação direta. Use o **menu lateral** para navegar às demais páginas.

---

## 4. Dashboard & Gráficos

### Objetivo

Ver métricas consolidadas e comparativos visuais de preços.

### Cartões de métrica (topo)

| Métrica | O que mostra |
|---|---|
| 📦 Produtos Cadastrados | Total de produtos no banco |
| 📈 Markup Médio | Média dos markups |
| 💰 Preço Médio (Venda) | Preço médio praticado |
| 🌐 Canais Integrados | Olist, Amazon, Shopee |

### Como usar

1. Menu lateral → **Dashboard & Gráficos**
2. No dropdown **Filtrar por categoria**, escolha:
   - `(todas)` → todos os produtos
   - `Cameras` → só protetores de câmera
   - `Cabos_Transparentes` → só cabos transparentes
   - `Cabos_Coloridos` → só cabos coloridos
   - `Kits` → só kits combinados
3. Observe os cartões e o gráfico atualizando automaticamente

### Dicas

- Use o filtro para **comparar margens** entre categorias
- Passe o mouse nas barras do gráfico para ver valores exatos

---

## 5. Cadastrar Produto

### Objetivo

Cadastrar um produto individual com cálculo automático de preço.

### Passo a passo

1. Menu lateral → **Cadastrar Produto**
2. Preencha os campos:

| Campo | Exemplo |
|---|---|
| Nome do Produto | Protetor de Cabo Silicone Tipo C |
| SKU / Código | PROT-TC-04 |
| Custo Unitário (R$) | 1.50 |
| Frete Internacional (R$) | 0.80 |
| Categoria | Cabos |
| Imposto de Importação (%) | 60 |
| ICMS (%) | 18 |
| Comissão do Marketplace (%) | 16 |
| Margem de Lucro Alvo (%) | 30 |

3. Clique em **Salvar e Calcular Preço**
4. Aguarde a mensagem verde: `Produto 'X' salvo! Preço Sugerido: R$ Y.YY`

### Fórmula usada

```
custo_total = (custo_unit × 5.5) + frete_unit
markup = 2.5 (fixo)
preco_venda = custo_total × markup
```

### Erros comuns

- **"Preencha o Nome e o SKU"** → ambos são obrigatórios
- **SKU duplicado** → o app não bloqueia, mas é boa prática usar únicos

---

## 6. Importar CSV / Excel

### Objetivo

Importar produtos em **lote** a partir de arquivo CSV ou Excel.

### Formato do CSV recomendado

```csv
nome;categoria;custo_unit;frete_unit;preco_venda
Protetor de Cabo Silicone Tipo C;Cabos;0.04;0.80;5.30
Protetor de Privacidade de Câmera;Cameras;0.02;0.50;3.80
```

### Passo a passo completo

#### 🔹 Etapa 1 — Upload

1. Menu lateral → **Importar CSV**
2. Clique em **Selecione o arquivo**
3. Escolha `.csv`, `.xlsx` ou `.xls`
4. Aguarde a mensagem verde: `✅ CSV lido! Separador=';', Encoding='utf-8' — N linhas, M colunas.`

**Se você enviou Excel com múltiplas abas:**

- Aparece um dropdown `Aba:` para escolher qual importar

#### 🔹 Etapa 2 — Mapeamento de Colunas

Confirme os 6 dropdowns (vêm **pré-selecionados** automaticamente):

| Campo do banco | Coluna do CSV |
|---|---|
| Nome do Produto | `nome` |
| SKU / Código | `(nenhuma)` se não tiver |
| Custo Unitário (R$) | `custo_unit` |
| Frete Unitário (R$) | `frete_unit` |
| Preço de Venda (R$) | `preco_venda` |
| Categoria | `categoria` |

⚠️ **Se algum dropdown estiver errado**, clique nele e escolha a coluna correta.

#### 🔹 Etapa 3 — Opções de Importação

| Opção | Quando usar |
|---|---|
| **Inserir todos (append)** | Sempre cria novos produtos |
| **Atualizar se SKU existir (upsert)** | Atualiza existentes (precisa de SKU) |

✅ Marque **Pular linhas sem nome de produto** para evitar linhas vazias.

#### 🔹 Etapa 4 — Prévia

Role para baixo e confira a tabela de prévia com os dados normalizados.

Se algo estiver errado, **volte ao mapeamento** e ajuste.

#### 🔹 Etapa 5 — Simulação (recomendado!)

1. Clique em **🔍 Simular (dry-run)**
2. Aguarde a mensagem: `🔍 Simulação concluída! Inseridos: X | Atualizados: Y | Erros: Z`
3. Se os 3 números estiverem OK → prossiga

#### 🔹 Etapa 6 — Importar de verdade

1. Clique em **🚀 Processar Lote**
2. Aguarde a mensagem final: `✅ Importação concluída! Inseridos: X | Atualizados: Y | Erros: Z`

### Baixar modelo de CSV

Se nenhum arquivo está carregado, aparece o botão **⬇️ Baixar modelo (CSV)** no final da página.

### Erros comuns

| Erro | Solução |
|---|---|
| Não foi possível ler o CSV | Veja o separador no Bloco de Notas |
| `nan` na coluna SKU | Deixe o dropdown em `(nenhuma)` |
| Preços zerados | Mapeie corretamente a coluna `preco_venda` |
| Erros > 0 na simulação | Veja os detalhes e corrija o CSV |

---

## 7. Produtos

### Objetivo

Listar todos os produtos cadastrados, com filtros por categoria.

### Como usar

1. Menu lateral → **Produtos**
2. Use o dropdown **Filtrar por categoria** para segmentar:
   - `(todas)` → todos os produtos
   - `Cameras`, `Cabos_Transparentes`, `Cabos_Coloridos`, `Kits`
3. Clique nos cabeçalhos das colunas para **ordenar** (crescente ou decrescente)
4. Role horizontalmente para ver todas as colunas

### Colunas exibidas

| Coluna | Descrição |
|---|---|
| `id` | ID interno (auto-incremento) |
| `nome` | Nome do produto |
| `sku` | Código único |
| `custo_unit` | Custo unitário (R$) |
| `frete_unit` | Frete unitário (R$) |
| `markup` | Fator de markup |
| `preco_venda` | Preço de venda (R$) |
| `categoria` | Categoria do produto |
| `data_cadastro` | Data em que foi cadastrado |

### Dicas

- Use o filtro para **conferir duplicados** dentro de uma categoria
- Ordene por `preco_venda` para identificar produtos com preço fora da curva
- Se um produto não aparece, verifique se a categoria dele está correta

---

## 8. Calculadora de Formação de Preço

### Objetivo

Simular o preço ideal de um produto **sem salvar** no banco de dados.

### Campos disponíveis

| Campo | Descrição |
|---|---|
| Custo Base (R$) | Custo de compra do produto |
| Frete & Embalagem (R$) | Custos logísticos somados |
| Impostos sobre Venda (%) | Total de impostos sobre a venda |
| Comissão do Canal (%) | Taxa do marketplace |
| Rateio Custo Fixo (%) | Rateio de despesas fixas |
| Lucro Líquido Desejado (%) | Margem desejada |

### Como usar

1. Menu lateral → **Calculadora de Formação de Preço**
2. Preencha os 6 campos
3. O resultado aparece em verde automaticamente

### Fórmula

### Exemplo prático

- Custo Base: R$ 5,00
- Frete & Embalagem: R$ 1,50
- Impostos: 10%
- Comissão: 16%
- Custo Fixo: 5%
- Lucro Desejado: 25%

**Resultado:**

### Erros comuns

- **"A soma das porcentagens não pode ser ≥ 100%"** → diminua os percentuais
- **Resultado R$ 0,00** → verifique se o divisor ficou negativo

---

## 9. Simulador de Descontos

### Objetivo

Ver o impacto de um desconto no preço final **em tempo real**.

### Como usar

1. Menu lateral → **Simulador de Descontos**
2. Digite o **preço de venda atual**
3. Arraste o **slider** para escolher o desconto (0 a 50%)
4. Leia o resultado em tempo real

### Exemplo

- Preço atual: R$ 29,90
- Desconto: 10%
- **Novo preço: R$ 26,91** (economia de R$ 2,99)

### Dica importante

Antes de aplicar uma promoção, use a **Calculadora de Formação de Preço** para garantir que a margem continua positiva.

---

## 10. Atacado

### Objetivo

Definir regras de desconto por volume (kits maiores).

### Como usar

1. Menu lateral → **Atacado**
2. Escolha a **variação** no dropdown:
   - Kit 1 Par
   - Kit 2 Pares
   - Kit 4 Pares
   - Kit 8 Pares
3. Ajuste o **slider** de desconto (0 a 40%)
4. Veja a regra configurada na caixa azul

### Observação

Esta página atualmente é apenas **informativa** — não grava a regra no banco.

Para tornar dinâmica (com persistência), seria necessário adicionar uma tabela `regras_atacado` no banco.

---

## 11. Controle de Estoque

### Objetivo

Monitorar estoque e emitir alertas de reposição.

### Como usar

1. Menu lateral → **Controle de Estoque**
2. Veja o alerta no topo (se houver)
3. A tabela abaixo é a mesma da página **Produtos**

### Observação

O alerta atual está **fixo no código** (SKU `PROT-TC-04` com estoque baixo). Para tornar dinâmico:

- Seria necessário adicionar coluna `estoque_atual` na tabela `products`
- E definir um **limite mínimo** por produto
- Aí o alerta seria calculado automaticamente

---

## 12. Relatórios & Exportação

### Objetivo

Gerar arquivos para conferência, backup ou envio por e-mail.

### Como usar

1. Menu lateral → **Relatórios & Exportação**
2. Clique no botão **Baixar Tabela de Preços (CSV)**
3. O arquivo `tabela_lm.csv` é baixado

### Observação

Hoje o botão baixa um CSV **fixo de exemplo** (`id,nome,preco`). Para exportar os dados reais do banco, é necessário implementar a query SQL e gerar o arquivo dinamicamente.

### Ideias futuras de relatórios

- 📊 Tabela completa de produtos (com todos os campos)
- 💰 Relatório de lucro por categoria
- 📦 Relatório de estoque baixo
- 📈 Comparativo de preços entre marketplaces
- 🧾 Nota fiscal / etiquetas de envio
