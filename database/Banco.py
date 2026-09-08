import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base

caminho_driver = r"ODBC Driver 17 for SQL Server"

string_conexao = (
    #nao esqueça que nao pode espaços entre o "=" e o conteudo else cannot open database
    #precisa ficar junto!
    f"DRIVER={{{caminho_driver}}};"
    r"SERVER=DESKTOP-KS4DVSL;"
    r"DATABASE=CatatauDB;" #nome do banco la no sqlserver
    r"Trusted_Connection=yes;"
    r"TrustServerCertificate=yes;"
)

params_conexao = urllib.parse.quote_plus(string_conexao)

DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params_conexao}"

#de fato o motor geral que conversa com o banco de dados
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# passa base no parametro das classes que voce cria as tabelas, para o banco entender quais sao as tabelas
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
  


