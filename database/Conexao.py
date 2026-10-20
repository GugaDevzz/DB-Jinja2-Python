# 🚨 ESSENCIAL: Importar o arquivo das suas tabelas para registrá-las no Base
from Banco import Base, engine
from Tabelas import Cliente, Produto, Pedido, ItemPedido

def criar_tabelas():
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

    try:
        conexao = engine.connect()
        print("Conexão com SQL Server OK!")
        conexao.close()

        criar_tabelas()
    except Exception as e:
        print(f"Erro: {e}")
