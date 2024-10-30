import os
import streamlit as st
from sqlalchemy import create_engine, MetaData, text
import pandas as pd
import pymysql

# Configurações de conexão com o MySQL
DB_HOST = os.getenv("RDS_ENDPOINT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# Verificação das variáveis de ambiente
if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS]):
    missing_vars = [var for var in ["RDS_ENDPOINT", "DB_NAME", "DB_USER", "DB_PASS"] if not os.getenv(var)]
    st.error(f"As seguintes variáveis de ambiente estão faltando: {', '.join(missing_vars)}")
else:
    # Função para criar a conexão com o banco de dados
    def init_connection():
        return create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}', echo=True)

    # Função para criar a tabela de cadastro se não existir
    def create_table(engine):
        with engine.connect() as conn:
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100),
                email VARCHAR(100),
                idade INT
            );
            """))

    # Função para inserir uma nova pessoa
    def add_person(engine, nome, email, idade):
        try:
            with engine.begin() as conn:
                conn.execute(
                    text("INSERT INTO pessoas (nome, email, idade) VALUES (:nome, :email, :idade)"),
                    {"nome": nome, "email": email, "idade": idade}
                )
            st.success(f"Cadastro de {nome} realizado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao inserir dados: {e}")

    # Função para checar o status do banco e contar o número de linhas
    def check_db_status(engine):
        with engine.connect() as conn:
            metadata = MetaData()
            metadata.reflect(bind=engine)
            table_status = []
            for table_name in metadata.tables.keys():
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.fetchone()[0]
                table_status.append((table_name, count))
            return table_status

    # Função para listar todas as pessoas cadastradas
    def list_people(engine):
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM pessoas"))
            return result.fetchall()

    # Inicializar valores padrão se não existirem no session_state
    if 'nome' not in st.session_state:
        st.session_state['nome'] = ""
    if 'email' not in st.session_state:
        st.session_state['email'] = ""
    if 'idade' not in st.session_state:
        st.session_state['idade'] = 0

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
            nome = st.text_input("Nome", key='nome', value=st.session_state['nome'])
            email = st.text_input("Email", key='email', value=st.session_state['email'])
            idade = st.number_input("Idade", min_value=0, step=1, key='idade', value=st.session_state['idade'])
            submit_button = st.form_submit_button(label="Cadastrar")

        # Quando o botão de submit é pressionado
        if submit_button:
            add_person(engine, st.session_state['nome'], st.session_state['email'], st.session_state['idade'])
            # Removida a limpeza dos campos
            # st.session_state['nome'] = ""
            # st.session_state['email'] = ""
            # st.session_state['idade'] = 0

    # Aba 2: Status do Banco de Dados
    with tab2:
        st.header("Status do Banco de Dados")
        status = check_db_status(engine)
        if status:
            for table, count in status:
                st.write(f"Tabela: {table}, Linhas: {count}")
                
            # Listar todos os registros da tabela "pessoas"
            st.subheader("Registros Cadastrados")
            people = list_people(engine)
            if people:
                df = pd.DataFrame(people, columns=["ID", "Nome", "Email", "Idade"])
                st.dataframe(df)
            else:
                st.write("Nenhum registro encontrado.")
        else:
            st.warning("Nenhuma tabela encontrada no banco de dados.")
