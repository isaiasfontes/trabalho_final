import streamlit as st
from sqlalchemy import create_engine, MetaData
import pandas as pd
import pymysql

# Configurações de conexão com o MySQL
DB_HOST = "localhost"
DB_NAME = "app_db"
DB_USER = "admin"
DB_PASS = "unifor@2024"
DB_PORT = "3306"

# Função para criar a conexão com o banco de dados
def init_connection():
    return create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# Função para criar a tabela de cadastro se não existir
def create_table(engine):
    with engine.connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100),
            email VARCHAR(100),
            idade INT
        );
        """)

# Função para inserir uma nova pessoa
def add_person(engine, nome, email, idade):
    with engine.connect() as conn:
        conn.execute(f"INSERT INTO pessoas (nome, email, idade) VALUES ('{nome}', '{email}', {idade})")

# Função para checar o status do banco
def check_db_status(engine):
    with engine.connect() as conn:
        # Obter lista de tabelas e contar o número de linhas de cada tabela
        metadata = MetaData(bind=engine)
        metadata.reflect()
        table_status = []
        for table in metadata.tables:
            result = conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = result.fetchone()[0]
            table_status.append((table, count))
        return table_status

# Interface do Streamlit
st.title('Cadastro de Pessoas')

# Abas
tab1, tab2 = st.tabs(["Formulário de Cadastro", "Status do Banco de Dados"])

# Conexão inicial com o banco de dados
engine = init_connection()
create_table(engine)

# Aba 1: Formulário de cadastro
with tab1:
    st.header("Preencha os dados abaixo:")
    with st.form(key='form_cadastro'):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        idade = st.number_input("Idade", min_value=0, step=1)
        submit_button = st.form_submit_button(label="Cadastrar")

    # Quando o botão de submit é pressionado
    if submit_button:
        add_person(engine, nome, email, idade)
        st.success(f"Cadastro de {nome} realizado com sucesso!")

# Aba 2: Status do Banco de Dados
with tab2:
    st.header("Status do Banco de Dados")
    status = check_db_status(engine)
    if status:
        for table, count in status:
            st.write(f"Tabela: {table}, Linhas: {count}")
    else:
        st.warning("Nenhuma tabela encontrada no banco de dados.")
