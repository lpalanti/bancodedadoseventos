import streamlit as st
import sqlite3
import uuid
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configurações iniciais
load_dotenv()
st.set_page_config(page_title="EventosPro", layout="wide")

# ------------ CONFIGURAÇÕES DO BANCO DE DADOS ------------
def init_db():
    conn = sqlite3.connect('eventos.db')
    c = conn.cursor()
    
    # Verifica se a tabela já existe
    c.execute('''SELECT count(name) FROM sqlite_master 
              WHERE type='table' AND name='suppliers' ''')
    
    if c.fetchone()[0] == 0:
        # Criação da tabela suppliers
        c.execute('''
            CREATE TABLE suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                cnpj TEXT UNIQUE NOT NULL,
                phone1 TEXT NOT NULL,
                phone2 TEXT,
                city TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                validation_token TEXT UNIQUE,
                validation_expires TEXT,
                is_validated BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    
    conn.close()

# ------------ FUNÇÕES DE E-MAIL ------------
def send_validation_email(supplier):
    try:
        msg = MIMEText(f"""
        Valide seu cadastro em: {os.getenv('APP_URL')}/validar?token={supplier['validation_token']}
        """)
        msg['Subject'] = 'Valide seu cadastro - EventosPro'
        msg['From'] = os.getenv('EMAIL_FROM')
        msg['To'] = supplier['email']
        
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
            server.starttls()
            server.login(os.getenv('EMAIL_FROM'), os.getenv('EMAIL_PASSWORD'))
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Erro no envio: {str(e)}")
        return False

# ------------ FORMULÁRIO DE CADASTRO ------------
def supplier_registration_form():
    with st.form("Novo Fornecedor"):
        st.header("📝 Cadastro de Fornecedor")
        
        supplier = {
            'name': st.text_input("Nome Completo *"),
            'email': st.text_input("E-mail *"),
            'cnpj': st.text_input("CNPJ *"),
            'phone1': st.text_input("Telefone Principal *"),
            'phone2': st.text_input("Telefone Secundário"),
            'city': st.text_input("Cidade *"),
            'category': st.selectbox("Categoria *", ["Hotelaria", "A&B", "Transporte"]),
            'description': st.text_area("Descrição dos Serviços *"),
            'validation_token': str(uuid.uuid4()),
            'validation_expires': (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        if st.form_submit_button("Cadastrar"):
            try:
                # Validação básica
                required = ['name', 'email', 'cnpj', 'phone1', 'city', 'category', 'description']
                for field in required:
                    if not supplier[field]:
                        raise ValueError(f"Campo obrigatório: {field}")
                
                conn = sqlite3.connect('eventos.db')
                c = conn.cursor()
                
                c.execute('''
                    INSERT INTO suppliers (
                        name, email, cnpj, phone1, phone2, city, 
                        category, description, validation_token, validation_expires
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    supplier['name'],
                    supplier['email'],
                    supplier['cnpj'],
                    supplier['phone1'],
                    supplier['phone2'] or None,
                    supplier['city'],
                    supplier['category'],
                    supplier['description'],
                    supplier['validation_token'],
                    supplier['validation_expires']
                ))
                
                if send_validation_email(supplier):
                    st.success("Cadastro realizado! Verifique seu e-mail.")
                
                conn.commit()
                conn.close()
                
            except sqlite3.IntegrityError as e:
                st.error(f"Erro: {str(e)}")
                if "UNIQUE" in str(e):
                    st.error("CNPJ ou e-mail já cadastrado")
            except Exception as e:
                st.error(f"Erro inesperado: {str(e)}")

# ------------ PÁGINA PRINCIPAL ------------
def main():
    init_db()
    
    st.sidebar.title("🎪 EventosPro")
    menu = st.sidebar.radio("Menu", ["🏠 Início", "📝 Cadastrar"])
    
    if menu == "🏠 Início":
        st.header("Fornecedores Validados")
        conn = sqlite3.connect('eventos.db')
        c = conn.cursor()
        c.execute('SELECT name, category, city FROM suppliers WHERE is_validated=1')
        for row in c.fetchall():
            st.write(f"- {row[0]} ({row[1]}, {row[2]})")
        conn.close()
    
    elif menu == "📝 Cadastrar":
        supplier_registration_form()

if __name__ == "__main__":
    main()
