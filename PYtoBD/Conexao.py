from Banco import engine
try:
 conexao = engine.connect()
 print("Conexão com SQL Server OK!")
 conexao.close()
except Exception as e:
 print(f"Erro: {e}")
