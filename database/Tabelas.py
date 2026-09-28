from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database.Banco import Base
from sqlalchemy.orm import relationship

class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True)
    cpf = Column(String(255), nullable=False)
    telefone = Column(String(20), unique=True)
    senha = Column(String(255), nullable=False)
    
class Produto(Base):
    __tablename__ = "produto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(150), nullable=True)
    valor = Column(Float, nullable=False)


class Pedido(Base):
    __tablename__ = "pedido"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_cliente = Column(String(100), nullable=True)
    num_mesa = Column(Integer, nullable=False)
    descricao = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False)
    valor_final = Column(Float, default=0.0)

    # Relacionamento com itens
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fk_id_pedido = Column(Integer, ForeignKey("pedido.id"), nullable=False)
    fk_id_produto = Column(Integer, ForeignKey("produto.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)

    # Relacionamentos para facilitar acessos diretos no Python
    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")
