from sqlalchemy import Column, Integer, String, Float
from PYtoBD.Banco import Base

class CadastroTable(Base):
    __tablename__ = "cadastro"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True)
    cpf = Column(String(255), nullable=False)
    telefone = Column(String(20), unique=True)
    senha = Column(String(255), nullable=False)
