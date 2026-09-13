# 📘 Manual de Uso — CALC MARKUP

Bem-vindo ao manual interativo do **CALC MARKUP - LM - Importing 2U®**.

Use as abas acima para navegar pelos tópicos.

---

## 1. Visão Geral

O **CALC MARKUP** é o sistema de gestão e precificação da **LM - Importing 2U®**.

**O que você pode fazer aqui:**

- 📦 Cadastrar produtos com custo, frete, markup e preço
- 📥 Importar produtos em lote via **CSV** ou **Excel**
- 📊 Visualizar **dashboards** com métricas por categoria
- 🧮 Calcular preços com **margem, impostos e taxas**
- 🏷️ Simular **descontos e promoções**
- 🛒 Definir estratégias de **atacado** por volume
- 📋 Controlar **estoque**
- 📄 Gerar **relatórios** e exportar dados
- 👥 Gerenciar **usuários** e permissões

**Stack técnico:**
- Interface: Streamlit (Python)
- Banco de dados: SQLite (`database.db`)
- Autenticação: SHA-256 + sessões

---

## 2. Login

### Credenciais padrão (1º acesso)

| Campo | Valor |
|---|---|
| Usuário | `admin` |
| Senha | `admin123` |

⚠️ **Importante:** troque essa senha após o primeiro acesso (veja a seção **Usuários & Logs**).

### Como fazer login

1. Digite o **usuário**
2. Digite a **senha**
3. Clique em **Entrar no Sistema**

### Como sair

No menu lateral, clique em **Sair / Trocar Usuário**.

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