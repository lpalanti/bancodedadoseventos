import streamlit as st
import sqlite3
import uuid
import os
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from dotenv import load_dotenv

# Configurações iniciais
load_dotenv()
st.set_page_config(page_title="EventosPro", layout="wide")

# ------------ FUNÇÕES DO BANCO DE DADOS ------------
def init_db():
    conn = sqlite3.connect('eventos.db')
    c = conn.cursor()
    
    # Tabela de Usuários
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, 
                  username TEXT UNIQUE, 
                  email TEXT, 
                  password TEXT, 
                  subscription_type TEXT)''')
    
    # Tabela de Fornecedores
    c.execute('''CREATE TABLE IF NOT EXISTS suppliers
                 (id INTEGER PRIMARY KEY,
                  name TEXT,
                  email TEXT,
                  cnpj TEXT UNIQUE,
                  phone1 TEXT,
                  phone2 TEXT,
                  city TEXT,
                  category TEXT,
                  description TEXT,
                  validation_token TEXT,
                  is_validated BOOLEAN)''')
    
    conn.commit()
    conn.close()

# ------------ FUNÇÕES DE AUTENTICAÇÃO ------------
def login():
    with st.form("Login"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        
        if st.form_submit_button("Entrar"):
            conn = sqlite3.connect('eventos.db')
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
            user = c.fetchone()
            conn.close()
            
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Credenciais inválidas")

# ------------ FUNÇÕES DE MENSAGEM ------------
def send_validation(supplier):
    # Envio por WhatsApp (Twilio)
    try:
        client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
        message = client.messages.create(
            body=f"""Confirme seu cadastro:
            1 - Confirmar
            2 - Corrigir
            3 - Remover
            Token: {supplier['validation_token']}""",
            from_='whatsapp:+14155238886',
            to=f'whatsapp:{supplier["phone1"]}'
        )
    except Exception as e:
        st.error(f"Erro no WhatsApp: {e}")

    # Envio por E-mail
    try:
        msg = MIMEText(f"""Valide seu cadastro:
        Token: {supplier['validation_token']}
        """)
        msg['Subject'] = 'Valide seu cadastro - EventosPro'
        msg['From'] = os.getenv('EMAIL_FROM')
        msg['To'] = supplier['email']
        
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT')) as server:
            server.starttls()
            server.login(os.getenv('EMAIL_FROM'), os.getenv('EMAIL_PASS'))
            server.sendmail(os.getenv('EMAIL_FROM'), supplier['email'], msg.as_string())
    except Exception as e:
        st.error(f"Erro no e-mail: {e}")

# ------------ FORMULÁRIO DE CADASTRO ------------
def supplier_form():
    with st.form("Novo Fornecedor"):
        st.header("Cadastro de Novo Fornecedor")
        data = {
            'name': st.text_input("Nome Completo"),
            'email': st.text_input("E-mail"),
            'cnpj': st.text_input("CNPJ"),
            'phone1': st.text_input("Telefone Principal"),
            'phone2': st.text_input("Telefone Secundário"),
            'city': st.text_input("Cidade"),
            'category': st.selectbox("Categoria", ["Hotelaria", "A&B", "Transporte"]),
            'description': st.text_area("Descrição dos Serviços"),
            'validation_token': str(uuid.uuid4())
        }
        
        if st.form_submit_button("Cadastrar"):
            conn = sqlite3.connect('eventos.db')
            c = conn.cursor()
            try:
                c.execute('''INSERT INTO suppliers 
                          (name, email, cnpj, phone1, phone2, city, category, description, validation_token, is_validated)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (data['name'], data['email'], data['cnpj'], data['phone1'], data['phone2'],
                           data['city'], data['category'], data['description'], data['validation_token'], False))
                conn.commit()
                send_validation(data)
                st.success("Cadastro realizado! Verifique seu WhatsApp e e-mail para validar")
            except sqlite3.IntegrityError:
                st.error("CNPJ já cadastrado")
            finally:
                conn.close()

# ------------ PÁGINA PRINCIPAL ------------
def main():
    init_db()
    
    if 'user' not in st.session_state:
        login()
        st.stop()
    
    st.sidebar.title(f"Bem-vindo, {st.session_state.user[1]}!")
    if st.sidebar.button("Sair"):
        del st.session_state.user
        st.rerun()
    
    menu = st.sidebar.radio("Menu", ["Dashboard", "Cadastro", "Perfil"])
    
    if menu == "Dashboard":
        st.header("Fornecedores Cadastrados")
        conn = sqlite3.connect('eventos.db')
        c = conn.cursor()
        c.execute('SELECT name, category, city FROM suppliers WHERE is_validated=1')
        for row in c.fetchall():
            st.write(f"**{row[0]}** ({row[1]}) - {row[2]}")
        conn.close()
    
    elif menu == "Cadastro":
        supplier_form()

if __name__ == "__main__":
    main()
