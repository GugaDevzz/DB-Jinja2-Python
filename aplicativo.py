from fastapi import FastAPI, Depends, HTTPException, Form, Request
from pydantic import BaseModel
from Tabelas import CadastroTable
from PYtoBD.Banco import get_db, Base, engine
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # 1. Importe o StaticFile
from sqlalchemy import or_

app = FastAPI()

templates = Jinja2Templates(directory="Front-end")

#define onde o jinja vai agir.
app.mount("/Front-end", StaticFiles(directory="Front-end"), name="static")

@app.get("/")
def home():
    return {"status": "Servidor no ar"}

#just to open the menu page
@app.get("/catatau")
def pagina_menu(request: Request):
    return templates.TemplateResponse(
    request=request, 
    name="index.html"
)

#just to open the profile page
@app.get("/usuario/{nome}")
def pagina_profile(
    request: Request,
    nome: str,
    db: Session = Depends(get_db)
):
    
    usuario_db = db.query(CadastroTable).filter(CadastroTable.nome == nome).first()

    if not usuario_db:
        return templates.TemplateResponse(
            request=request, 
            name="login/Menu.html",
            context={"erro": "Usuário não encontrado."}
        )

    # Monta o dicionário com as informações trazidas da tabela CadastroTable
    dados_usuario = {
        "nome": usuario_db.nome,
        "email": usuario_db.email,
        "cpf": usuario_db.cpf,
        "telefone": usuario_db.telefone,
        "data_nascimento": "Não informado",
        "genero": "Não informado"
    }
    
    # Renderiza a tela usuarios/user.html (imagem 3) preenchendo a tabela
    return templates.TemplateResponse(
        request=request, 
        name="usuarios/user.html",
        context={"usuario": dados_usuario}
    )

#just to open the login page
@app.get("/login")
def pagina_login(request: Request):
    return templates.TemplateResponse(
    request=request, 
    name="login/Menu.html"
)

@app.post("/login")
def verify_login(
    request: Request,
    login_input: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    # Busca por Nome ou Email + Senha
    usuario_db = db.query(CadastroTable).filter(
        or_(
            CadastroTable.nome == login_input,
            CadastroTable.email == login_input
        ),
        CadastroTable.senha == senha
    ).first()

    if usuario_db:
        # Passa o OBJETO COMPLETO 'usuario_db' para o Jinja poder ler {{ page_user.nome }}
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "page_user": usuario_db, #o python entende que é o nome pq la no html ta chamando variavel.nome, esse .nome especifica quem da lista usuario_db ele chama
                "right": "Login feito com sucesso" #validação de dados carretos nao funcionou
            }
        )
    
    return templates.TemplateResponse(
        request=request, 
        name="login/Menu.html",
        context={"erro": "Usuário ou senha incorretos!"}
    )

    
#just to open the register page
@app.get("/cadastro")
def pagina_cadastro(request: Request):
    return templates.TemplateResponse(
    request=request, 
    name="cadastro/menu.html"
)

@app.post("/cadastro")
def cadastrar_usuario(

    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    CPF: str = Form(...),         # Bate com o name="CPF" do HTML
    ddd: str = Form(...),         # Bate com o name="ddd" do HTML
    numero: str = Form(...),      # Bate com o name="numero" do HTML
    senha: str = Form(...),
    repetir_senha: str = Form(...),
    db: Session = Depends(get_db) # Sua injeção de dependência do banco
):
    
    # Validando se as senhas são iguais antes de avançar
    if senha != repetir_senha:
        return templates.TemplateResponse(
            request=request,
            name="cadastro/menu.html",
            context={"erro": "As senhas não coincidem!"},  # Envia o erro para o HTML
        )

    #verifica se tem nomes emails ou cpfs iguais
    verify = db.query(CadastroTable).filter(CadastroTable.nome == nome).first() or db.query(CadastroTable).filter(CadastroTable.cpf == CPF).first()
    if verify:
        return templates.TemplateResponse(
            request=request,
            name="cadastro/menu.html",
            context={"erro": "Esse usuário já existe!\n Tente fazer seu login. "}  # Envia o erro para o HTML
        )

    # Juntando o DDD e o Número em uma única string
    telefone_completo = f"{ddd}" + " " + f"{numero}"

    # Criando o objeto para salvar no banco via SQLAlchemy
    novo_usuario = CadastroTable(
        nome=nome,
        email=email,
        cpf=CPF,
        telefone=telefone_completo,  # Salvando o telefone unificado
        senha=senha
    )

    db.add(novo_usuario)
    db.commit()

    #lista apontada para user.html, jinja acionado com {{}}
    dados_usuario = {
        "nome": nome,
        "cpf": CPF,
        "email": email,
        "telefone": telefone_completo,
        "data_nascimento": "Não informado", 
        "genero": "Não informado"
    }

    return templates.TemplateResponse(
        request=request,
        name="usuarios/user.html", # Nome do seu arquivo HTML de perfil
        context={"usuario": dados_usuario} # == "oq vem do {{html}}": oq o usuario ve 
        #apenas usuario pq todas as tags estao com esse prefixo EX: usuario.nome
    )





























@app.get("/administrator")
def mostrar_geral(db: Session = Depends(get_db)):
    all_users = db.query(CadastroTable).all()
    return all_users