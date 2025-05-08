import streamlit as st
import sqlite3
import uuid
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz

# Configurações iniciais
load_dotenv()
st.set_page_config(page_title="EventosPro", layout="wide")

# ------------ CONFIGURAÇÕES GLOBAIS ------------
SMTP_CONFIG = {
    "server": os.getenv('SMTP_SERVER'),
    "port": int(os.getenv('SMTP_PORT')),
    "email": os.getenv('EMAIL_FROM'),
    "password": os.getenv('EMAIL_PASSWORD')
}

# ------------ FUNÇÕES DO BANCO DE DADOS ------------
def init_db():
    conn = sqlite3.connect('eventos.db')
    c = conn.cursor()
    
    # Tabela de Fornecedores
    c.execute('''CREATE TABLE IF NOT EXISTS suppliers
                 (id INTEGER PRIMARY KEY,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  cnpj TEXT UNIQUE NOT NULL,
                  phone1 TEXT NOT NULL,
                  phone2 TEXT,
                  city TEXT NOT NULL,
                  category TEXT NOT NULL,
                  description TEXT NOT NULL,
                  validation_token TEXT UNIQUE,
                  validation_expires DATETIME,
                  is_validated BOOLEAN DEFAULT 0,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabela de Usuários
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  is_admin BOOLEAN DEFAULT 0,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

# ------------ FUNÇÕES DE E-MAIL ------------
def send_validation_email(supplier):
    try:
        validation_link = f"{os.getenv('APP_URL')}/validar?token={supplier['validation_token']}"
        
        msg = MIMEText(f"""\
            <html>
                <body>
                    <h2>Validação de Cadastro - EventosPro</h2>
                    <p>Clique no link abaixo para validar seu cadastro:</p>
                    <p><a href="{validation_link}">Validar Cadastro</a></p>
                    <p>Ou use este código manualmente: {supplier['validation_token']}</p>
                    <p>Este link expira em 24 horas.</p>
                </body>
            </html>
        """, 'html')
        
        msg['Subject'] = 'Valide seu cadastro no EventosPro'
        msg['From'] = SMTP_CONFIG['email']
        msg['To'] = supplier['email']
        
        with smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port']) as server:
            server.starttls()
            server.login(SMTP_CONFIG['email'], SMTP_CONFIG['password'])
            server.sendmail(SMTP_CONFIG['email'], supplier['email'], msg.as_string())
            
        return True
    except Exception as e:
        st.error(f"Erro no envio do e-mail: {str(e)}")
        return False

# ------------ FUNÇÕES DE VALIDAÇÃO ------------
def validate_token(token):
    conn = sqlite3.connect('eventos.db')
    c = conn.cursor()
    
    c.execute('''SELECT * FROM suppliers 
              WHERE validation_token = ? 
              AND validation_expires > ?''',
              (token, datetime.now(pytz.utc)))
    
    supplier = c.fetchone()
    
    if supplier:
        c.execute('''UPDATE suppliers 
                  SET is_validated = 1,
                      validation_token = NULL,
                      validation_expires = NULL
                  WHERE id = ?''', (supplier[0],))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

# ------------ FORMULÁRIOS ------------
def supplier_registration_form():
    with st.form("Novo Fornecedor"):
        st.header("📝 Cadastro de Novo Fornecedor")
        
        supplier = {
            'name': st.text_input("Nome Completo *"),
            'email': st.text_input("E-mail *"),
            'cnpj': st.text_input("CNPJ *"),
            'phone1': st.text_input("Telefone Principal *"),
            'phone2': st.text_input("Telefone Secundário"),
            'city': st.text_input("Cidade *"),
            'category': st.selectbox("Categoria *", ["Hotelaria", "A&B", "Transporte", "Tecnologia", "Segurança"]),
            'description': st.text_area("Descrição dos Serviços *"),
            'validation_token': str(uuid.uuid4()),
            'validation_expires': datetime.now(pytz.utc) + timedelta(hours=24)
        }
        
        if st.form_submit_button("Cadastrar Fornecedor"):
            conn = sqlite3.connect('eventos.db')
            c = conn.cursor()
            
            try:
                c.execute('''INSERT INTO suppliers 
                          (name, email, cnpj, phone1, phone2, city, category, description, validation_token, validation_expires)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (supplier['name'], supplier['email'], supplier['cnpj'], 
                           supplier['phone1'], supplier['phone2'], supplier['city'],
                           supplier['category'], supplier['description'], 
                           supplier['validation_token'], supplier['validation_expires']))
                
                if send_validation_email(supplier):
                    st.success("✅ Cadastro realizado! Verifique seu e-mail para validar")
                else:
                    st.error("❌ Erro no envio do e-mail de confirmação")
                
                conn.commit()
            except sqlite3.IntegrityError as e:
                st.error(f"❌ Erro: {str(e)}")
                if "UNIQUE constraint failed: suppliers.cnpj" in str(e):
                    st.error("CNPJ já cadastrado")
                elif "UNIQUE constraint failed: suppliers.email" in str(e):
                    st.error("E-mail já cadastrado")
            finally:
                conn.close()

# ------------ PÁGINAS ------------
def main_page():
    st.header("🏨 Fornecedores Validados")
    conn = sqlite3.connect('eventos.db')
    c = conn.cursor()
    
    c.execute('''SELECT name, category, city, description 
              FROM suppliers 
              WHERE is_validated = 1
              ORDER BY created_at DESC''')
    
    suppliers = c.fetchall()
    
    if not suppliers:
        st.info("Nenhum fornecedor cadastrado ainda")
    else:
        for supplier in suppliers:
            with st.expander(f"{supplier[0]} ({supplier[1]} - {supplier[2]})"):
                st.write(supplier[3])
    
    conn.close()

def validation_page():
    token = st.experimental_get_query_params().get("token", [None])[0]
    
    if token:
        if validate_token(token):
            st.success("🎉 Cadastro validado com sucesso!")
            st.balloons()
        else:
            st.error("❌ Token inválido ou expirado")

# ------------ MAIN APP ------------
def main():
    init_db()
    
    # Página de Validação
    validation_page()
    
    # Menu Principal
    st.sidebar.title("🎪 EventosPro")
    st.sidebar.image("https://via.placeholder.com/150x50.png?text=Logo", width=150)
    
    menu = st.sidebar.radio("Navegação", ["🏠 Início", "📝 Cadastrar Fornecedor"])
    
    if menu == "🏠 Início":
        main_page()
    elif menu == "📝 Cadastrar Fornecedor":
        supplier_registration_form()

if __name__ == "__main__":
    main()
