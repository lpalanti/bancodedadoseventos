import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
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
    
def enviar_email_validacao(destinatario_email, nome):
    remetente = st.secrets["email_user"]
    senha = st.secrets["email_pass"]

    token = str(uuid.uuid4())[:8]  # Código único
    assunto = "Validação do seu cadastro - Banco de Fornecedores"
    corpo = f"""
Olá, {nome}!

Obrigado por se cadastrar em nossa plataforma.

Para validar seu cadastro, utilize o seguinte código:

📌 CÓDIGO DE VALIDAÇÃO: {token}

(Em breve, o sistema de validação por clique será ativado.)

Atenciosamente,
Equipe Banco de Fornecedores
"""

    msg = MIMEMultipart()
    msg["From"] = remetente
    msg["To"] = destinatario_email
    msg["Subject"] = assunto
    msg.attach(MIMEText(corpo, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(remetente, senha)
            servidor.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")
        return False


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

def salvar_fornecedor(data):
    try:
        df = pd.read_csv("fornecedores.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=data.keys())

    df = df.append(data, ignore_index=True)
    df.to_csv("fornecedores.csv", index=False)


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
        if st.button("Não tem conta? Cadastre-se aqui"):
            st.session_state.page = "register"


    with col2:
        st.image("rocket_login.png", caption="", use_container_width=True)

def register_page():
    st.title("📋 Cadastro de Fornecedor")
    st.markdown("Cadastre-se para ter acesso à plataforma.")

    with st.form("form_cadastro"):
        fornecedor = st.text_input("Nome do Fornecedor")
        documento = st.text_input("CNPJ ou CPF")
        telefone1 = st.text_input("Telefone Principal")
        telefone2 = st.text_input("Telefone Secundário")
        email = st.text_input("E-mail")
        linkedin = st.text_input("LinkedIn (opcional)")
        site = st.text_input("Site (opcional)")
        facebook = st.text_input("Facebook (opcional)")
        instagram = st.text_input("Instagram (opcional)")
        atuacao = st.text_area("Locais de Atuação")
        descricao = st.text_area("Descrição do tipo de serviço prestado")
        lgpd = st.checkbox("Autorizo o uso dos meus dados conforme a LGPD")

        submitted = st.form_submit_button("Cadastrar")

        if submitted:
            if not lgpd:
                st.error("Você precisa aceitar os termos da LGPD para continuar.")
            elif not (fornecedor and documento and telefone1 and email and atuacao and descricao):
                st.error("Preencha todos os campos obrigatórios.")
       
# ----- Controle de sessão -----
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()
    else:
        st.success(f"Você está logado como {st.session_state.user_email}")
        st.write("👉 A próxima etapa será o painel principal do app.")

if __name__ == "__main__":
    main()
