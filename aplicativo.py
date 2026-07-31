from fastapi import FastAPI, Depends, HTTPException, Form, Request
from pydantic import BaseModel
from Tabelas import CadastroTable
from PYtoBD.Banco import get_db, Base, engine
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # 1. Importe o StaticFile
import time
import Tabelas

app = FastAPI()

templates = Jinja2Templates(directory="Front-end")

#define onde o jinja vai agir.
app.mount("/Front-end", StaticFiles(directory="Front-end"), name="static")

#just to open the menu page
@app.get("/catatau")
def pagina_menu(request: Request):
    return templates.TemplateResponse(
    request=request, 
    name="index.html"
)

#just to open the profile page
@app.get("/usuario")
def pagina_profile(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="usuarios/user.html",
        context={"erro": "As senhas não coincidem!"}
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
    nome: str = Form(...), # Bate com o name="nome" do HTML
    senha: str = Form(...),
    db: Session = Depends(get_db) # Sua injeção de dependência do banco
):
    nameORemail_onDB = db.query(CadastroTable).filter(CadastroTable.nome == nome).first() and db.query(CadastroTable).filter(CadastroTable.senha == senha).first()
    if nameORemail_onDB:
        return templates.TemplateResponse(
            request=request, 
            name="index.html",
            context={"right": "Login feito com sucesso"}
        )
    else:
        return templates.TemplateResponse(
            request=request, 
            name="login/Menu.html",
            context={"erro": "Falha ao logar"}
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