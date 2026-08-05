from PYtoBD.Banco import Base, engine
import Tabelas

#------------------------------------------------------
# AVISO: Antes de testar e mandar as tabelas, coloca
# o server correto da string de conexao. De nada!
# Confere na string de conexao o nome exato do DATABASE.
#-------------------------------------------------------

try:
 #essa liha carrega todas as tabelas que existem e joga para o sql armazenar
 Base.metadata.create_all(bind=engine)
 print("As tabelas foram injetadas ao SQL com sucesso!")
 #essa linha testa se esse motor para lançamento ta ok
 conexao = engine.connect()
 print("Conexão com SQL Server OK!")
 conexao.close()
except Exception as e:
 print(f"Erro: {e}")
