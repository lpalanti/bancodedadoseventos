import streamlit as st
import sqlite3
import uuid
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Configurações iniciais
load_dotenv()
st.set_page_config(page_title="EventosPro", layout="wide")

# ------------ FUNÇÕES DO BANCO DE DADOS ------------
def init_db():
    conn = sqlite3.connect('eventos.db')
    c = conn.cursor()
    
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

# ------------ FUNÇÕES DE MENSAGEM ------------
def send_validation(supplier):
    # Versão simplificada sem WhatsApp
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
        st.success("E-mail de confirmação enviado!")
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
            except sqlite3.IntegrityError:
                st.error("CNPJ já cadastrado")
            finally:
                conn.close()

# ------------ PÁGINA PRINCIPAL ------------
def main():
    init_db()
    
    st.sidebar.title("EventosPro")
    
    menu = st.sidebar.radio("Menu", ["Dashboard", "Cadastro"])
    
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


import smtplib

def test_smtp():
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("seuemail@gmail.com", "sua_senha_app")
            print("Conexão bem-sucedida!")
    except Exception as e:
        print(f"Erro: {e}")

test_smtp()
