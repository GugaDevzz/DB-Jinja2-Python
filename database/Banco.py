import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

caminho_driver = r"ODBC Driver 17 for SQL Server"

string_conexao = (
    f"DRIVER={{{caminho_driver}}};"
    r"SERVER=(localdb)\MSSQLLocalDB;"
    r"DATABASE=DBCATATAU;"
    r"Trusted_Connection=yes;"
    r"TrustServerCertificate=yes;"
)

params_conexao = urllib.parse.quote_plus(string_conexao)
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params_conexao}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()