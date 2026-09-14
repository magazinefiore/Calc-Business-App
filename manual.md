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
