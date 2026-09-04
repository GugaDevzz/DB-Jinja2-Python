from models.Tabelas import CadastroTable
from database.Banco import get_db
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # 1. Importe o StaticFile
from sqlalchemy import or_
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette import status
from fastapi import FastAPI, Depends, Form, Request
from starlette import status

app = FastAPI()

templates = Jinja2Templates(directory="templates")
#define onde o jinja vai agir.
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return {"status": "Servidor no ar"}

@app.get("/lanche1")
def pagina_lanche1(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="cardapio/envlanches/Whopper®Grogu.html"
    )

@app.get("/contato")
def pagina_contato(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="contato/sobre-nos.html"
    )

@app.get("/cardapio")
def pagina_menu_deslogado(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="cardapio/lanches.html",
        context=""
    )


@app.get("/catatau/{nome}")
def pagina_menu(request: Request, nome: str, db: Session = Depends(get_db)):
    # Busca o usuário no banco
    usuario_banco = db.query(CadastroTable).filter(CadastroTable.nome == nome).first()
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "page_user": usuario_banco  # <--- Aqui está a variável que o HTML espera
        }
    )

@app.get("/catatau")
def pagina_menu_deslogado(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"page_user": None}
    )

#responseclass vai entender qual o endreço que ja ta sendo 
#adiantado para ser entendido, que no caso ta sendo passado pelo return do /cadastro
@app.get("/usuario/{nome}", response_class=HTMLResponse) 
def pagina_profile(
    request: Request,
    nome: str,
    db: Session = Depends(get_db)
):
    
    usuario_db = db.query(CadastroTable).filter(CadastroTable.nome == nome).first()

    # Monta o dicionário com as informações trazidas da tabela CadastroTable
    dados_usuario = {
        "nome": usuario_db.nome,
        "email": usuario_db.email,
        "cpf": usuario_db.cpf,
        "telefone": usuario_db.telefone,
        "data_nascimento": "Não informado",
        "genero": "Não informado",
    }
    
    # Renderiza a tela usuarios/user.html preenchendo a tabela
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

@app.get("/login")

@app.post("/login", response_class=HTMLResponse)    #response serve para o html que esta no retorno tomar conta do endereço, nao esqueça, sem isso a pagina muda mas ainda fica no /login
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
                "page_user": usuario_db  # <--- Aqui está a variável que o HTML espera
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

    return RedirectResponse(
        url=f"/usuario/{nome}", 
        status_code=status.HTTP_303_SEE_OTHER # nao é necessário colocar esse, vai rodar sem tambem!
    )





























@app.get("/administrator")
def mostrar_geral(db: Session = Depends(get_db)):
    all_users = db.query(CadastroTable).all()
    return all_users