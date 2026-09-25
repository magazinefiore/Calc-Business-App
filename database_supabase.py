"""
database_supabase.py
--------------------
Camada de acesso ao banco de dados usando Supabase (PostgreSQL).
Substitui o antigo database.py (SQLite).

Autor: LM Importing 2U
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# ============================================================
# CONEXÃO COM O SUPABASE
# ============================================================

@st.cache_resource
def get_supabase() -> Client:
    """Cria e retorna o cliente Supabase (com cache para não reconectar a cada ação)."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()


# ============================================================
# INICIALIZAÇÃO DAS TABELAS (CRIA SE NÃO EXISTIREM)
# ============================================================

def init_db():
    """
    Cria as tabelas básicas se não existirem.
    No Supabase (PostgreSQL), precisamos criar via SQL.
    Vamos executar as criações via RPC ou SQL direto.
    """
    try:
        # Tenta buscar produtos — se der erro, é porque a tabela não existe
        supabase.table("products").select("id").limit(1).execute()
    except Exception:
        # Tabela não existe — avisa o usuário para rodar o SQL de criação
        pass


# ============================================================
# FUNÇÕES DE USUÁRIOS
# ============================================================

def get_user_by_username(username: str):
    """Busca um usuário pelo username."""
    try:
        resp = supabase.table("users").select("*").eq("username", username).execute()
        if resp.data and len(resp.data) > 0:
            return resp.data[0]
        return None
    except Exception as e:
        st.error(f"Erro ao buscar usuário: {e}")
        return None


def create_user(username: str, password_hash: str, role: str, name: str = "Usuário"):
    """Cria um novo usuário."""
    try:
        resp = supabase.table("users").insert({
            "username": username,
            "password_hash": password_hash,
            "role": role,
            "name": name,
            "data_criacao": datetime.now().isoformat()
        }).execute()
        return True, "Usuário criado com sucesso!"
    except Exception as e:
        return False, f"Erro ao criar usuário: {e}"


def list_users():
    """Lista todos os usuários cadastrados."""
    try:
        resp = supabase.table("users").select("id, username, role, data_criacao").order("id").execute()
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao listar usuários: {e}")
        return pd.DataFrame()


# ============================================================
# FUNÇÕES DE PRODUTOS
# ============================================================

def get_all_products():
    """Retorna todos os produtos cadastrados."""
    try:
        resp = supabase.table("products").select("*").order("nome").execute()
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao buscar produtos: {e}")
        return pd.DataFrame()


def get_products_by_category(category: str):
    """Retorna produtos filtrados por categoria."""
    try:
        resp = supabase.table("products").select("*").eq("categoria", category).order("nome").execute()
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao buscar produtos: {e}")
        return pd.DataFrame()


def insert_product(data: dict, username: str = "sistema"):
    """Insere um novo produto."""
    try:
        resp = supabase.table("products").insert(data).execute()
        log_audit(username, "Cadastro de Produto", f"SKU: {data.get('sku', 'N/A')} | Nome: {data.get('nome', 'N/A')}")
        return True, "Produto cadastrado com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar produto: {e}"


def update_product(product_id: int, data: dict, username: str = "sistema"):
    """Atualiza um produto existente."""
    try:
        supabase.table("products").update(data).eq("id", product_id).execute()
        log_audit(username, "Atualização de Produto", f"ID: {product_id}")
        return True, "Produto atualizado com sucesso!"
    except Exception as e:
        return False, f"Erro ao atualizar produto: {e}"


def delete_product(product_id: int, username: str = "sistema"):
    """Deleta um produto."""
    try:
        supabase.table("products").delete().eq("id", product_id).execute()
        log_audit(username, "Exclusão de Produto", f"ID: {product_id}")
        return True, "Produto excluído com sucesso!"
    except Exception as e:
        return False, f"Erro ao excluir produto: {e}"


# ============================================================
# FUNÇÕES DE AUDITORIA
# ============================================================

def log_audit(user: str, action: str, details: str = ""):
    """Registra uma ação na trilha de auditoria."""
    try:
        supabase.table("audit_logs").insert({
            "user": user,
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }).execute()
    except Exception:
        pass  # Não interrompe o app se a auditoria falhar


def get_audit_logs(limit: int = 100):
    """Retorna os últimos logs de auditoria."""
    try:
        resp = supabase.table("audit_logs").select("*").order("id", desc=True).limit(limit).execute()
        return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao buscar logs: {e}")
        return pd.DataFrame()


# ============================================================
# FUNÇÕES DE ESTOQUE
# ============================================================

def update_stock(product_id: int, movement_type: str, qty: int, username: str = "sistema", notes: str = ""):
    """Atualiza o estoque de um produto (entrada ou saída)."""
    try:
        # Busca estoque atual
        resp = supabase.table("products").select("current_stock, sku, nome").eq("id", product_id).execute()
        if not resp.data:
            return False, "Produto não encontrado"
        
        produto = resp.data[0]
        estoque_atual = produto.get("current_stock", 0) or 0
        
        # Calcula novo estoque
        if movement_type == "ENTRADA":
            novo_estoque = estoque_atual + qty
        else:
            novo_estoque = max(0, estoque_atual - qty)
        
        # Atualiza o produto
        supabase.table("products").update({"current_stock": novo_estoque}).eq("id", product_id).execute()
        
        # Registra a movimentação
        supabase.table("stock_movements").insert({
            "product_id": product_id,
            "type": movement_type,
            "quantity": qty,
            "user": username,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }).execute()
        
        log_audit(username, f"Ajuste de Estoque ({movement_type})", 
                 f"Produto: {produto['nome']} (SKU: {produto['sku']}) | Qtd: {qty}")
        
        return True, f"Estoque atualizado! Novo saldo: {novo_estoque}"
    except Exception as e:
        return False, f"Erro ao atualizar estoque: {e}"
