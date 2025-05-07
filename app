import streamlit as st
from streamlit_authenticator import Authenticate
import yaml
from yaml.loader import SafeLoader
import sqlite3
from utils.auth import *
from utils.db import *
import os

# Configuração inicial
st.set_page_config(page_title="EventosPro", page_icon="🎪", layout="wide")

# Carregar CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Sistema de Autenticação
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Página de Login
if not st.session_state.get("authentication_status"):
    login(authenticator)
    st.stop()

# Logout
if st.sidebar.button("Logout"):
    logout(authenticator)

# Menu Principal
st.sidebar.title(f"Bem-vindo, {st.session_state['name']}!")
menu_options = get_menu_options(st.session_state['subscription_type'])
choice = st.sidebar.radio("Menu:", menu_options)

# Rotas
if choice == "🏠 Dashboard":
    show_dashboard()
elif choice == "📝 Novo Fornecedor":
    add_supplier_form()
elif choice == "⚙️ Perfil":
    user_profile(authenticator)
elif choice == "💳 Planos e Pagamentos":
    show_plans()
