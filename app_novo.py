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
