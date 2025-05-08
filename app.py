import streamlit as st
import pandas as pd
import hashlib

# Simula um banco de dados de usuários
def load_users():
    try:
        return pd.read_csv("users.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["email", "password_hash"])

# Função para gerar hash da senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Verifica se o usuário e senha conferem
def check_login(email, password):
    users = load_users()
    user = users[users["email"] == email]
    if not user.empty and user["password_hash"].values[0] == hash_password(password):
        return True
    return False

# Página de login
def login_page():
    st.title("🔐 Login - Banco de Fornecedores")
    st.write("Acesse sua conta para cadastrar ou visualizar fornecedores.")
    email = st.text_input("E-mail", key="email")
    password = st.text_input("Senha", type="password", key="password")

    if st.button("Entrar"):
        if check_login(email, password):
            st.success("Login realizado com sucesso!")
            st.session_state.logged_in = True
            st.session_state.user_email = email
        else:
            st.error("E-mail ou senha inválidos.")

    st.markdown("[Esqueci minha senha](#)")
    st.markdown("Não tem conta? [Cadastre-se](#)")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    st.success(f"Você está logado como {st.session_state.user_email}")
    st.write("👉 A próxima etapa será o painel principal do app.")

if __name__ == "__main__":
    main()
