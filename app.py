import streamlit as st
import pandas as pd
import hashlib

# ----- CSS Personalizado -----
def inject_custom_css():
    st.markdown("""
        <style>
        .main {
            background-color: #ffffff;
        }
        .stButton button {
            background-color: #f25c19;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            height: 3em;
            width: 100%;
        }
        .login-box {
            max-width: 400px;
            margin: auto;
            padding: 30px;
        }
        .rocket-img {
            max-width: 100%;
            height: auto;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        </style>
    """, unsafe_allow_html=True)

# ----- Banco de dados de usuários (simulado) -----
def load_users():
    try:
        return pd.read_csv("users.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["email", "password_hash"])

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(email, password):
    users = load_users()
    user = users[users["email"] == email]
    if not user.empty and user["password_hash"].values[0] == hash_password(password):
        return True
    return False

# ----- Página de Login -----
def login_page():
    inject_custom_css()
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🔐 Login")
        st.markdown("Acesse sua conta para cadastrar ou visualizar fornecedores.")
        with st.form("login_form"):
            email = st.text_input("E-mail", key="email_login")
            password = st.text_input("Senha", type="password", key="password_login")
            lembrar = st.checkbox("Lembrar de mim", key="lembrar")

            submitted = st.form_submit_button("Entrar")
            if submitted:
                if check_login(email, password):
                    st.success("Login realizado com sucesso!")
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                else:
                    st.error("E-mail ou senha inválidos.")

        st.markdown("[Esqueci minha senha](#)")
        st.markdown("Não tem conta? [Cadastre-se](#)")

    with col2:
        st.image("rocket_login.png", caption="", use_column_width=True)

# ----- Controle de sessão -----
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        st.success(f"Você está logado como {st.session_state.user_email}")
        st.write("👉 A próxima etapa será o painel principal do app.")

if __name__ == "__main__":
    main()
