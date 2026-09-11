from database.Tabelas import Cliente, Produto
import json
from database.Banco import get_db
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # 1. Importe o StaticFile
from sqlalchemy import or_
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette import status
from fastapi import FastAPI, Depends, Form, Request
from starlette import status
from typing import Annotated
from fastapi import FastAPI, Depends, Form, Request, Cookie  # <--- Adicionado Cookie


app = FastAPI()

templates = Jinja2Templates(directory="templates")
#define onde o jinja vai agir.
app.mount("/static", StaticFiles(directory="static"), name="static")


def carregar_carrinho_do_cookie(request: Request, db: Session):
    carrinho_cookie = request.cookies.get("carrinho_catatau")
    itens_carrinho = []
    total = 0.0

    if carrinho_cookie:
        carrinho_dict = json.loads(carrinho_cookie) # Formato: {"1": 2, "3": 1}
        
        for prod_id_str, quantidade in carrinho_dict.items():
            produto = db.query(Produto).filter(Produto.id == int(prod_id_str)).first()
            if produto:
                subtotal = produto.valor * quantidade
                total += subtotal
                itens_carrinho.append({
                    "id": produto.id,
                    "nome": produto.nome,
                    "preco": produto.valor,
                    "quantidade": quantidade,
                    "subtotal": subtotal,
                    "imagem": f"/static/imagens/lanches/{produto.nome}.png"
                })

    return itens_carrinho, total


@app.get("/")
def home():
    return {"status": "Servidor no ar"}

#just to open the login page
@app.get("/login")
def pagina_login(request: Request):
    return templates.TemplateResponse(
    request=request, 
    name="login/Menu.html"
)

@app.get("/cadastro")
def pagina_cadastro(request: Request):
    return templates.TemplateResponse(
    request=request, 
    name="cadastro/menu.html"
)

@app.get("/lanche1")
def pagina_lanche1(
    request: Request, 
    db: Session = Depends(get_db)
):
    itens_carrinho, total = carregar_carrinho_do_cookie(request, db)
    
    return templates.TemplateResponse(
        request=request,
        name="cardapio/envlanches/Whopper®Grogu.html",
        context={
            "carrinho": itens_carrinho,
            "total_carrinho": total
        }
    )

@app.get("/contato")
def pagina_contato(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="contato/sobre-nos.html"
    )

@app.get("/cardapio")
def pagina_menu_deslogado(
    request: Request,
    db: Session = Depends(get_db)):
    
    itens_carrinho, total = carregar_carrinho_do_cookie(request, db)

    return templates.TemplateResponse(
        request=request,
        name="cardapio/lanches.html",
        context={
            "carrinho": itens_carrinho,
            "total_carrinho": total
        }
    )

@app.get("/catatau")
def pagina_menu(
    request: Request,
    user_id: Annotated[str | None, Cookie()] = None,  # Captura o cookie salvo no navegador
    db: Session = Depends(get_db)
):
    usuario_banco = None
    
    # Se o cookie existir (significa que o usuário fez login há menos de 1 hora)
    if user_id:
        usuario_banco = db.query(Cliente).filter(Cliente.id == int(user_id)).first()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "page_user": usuario_banco  # Passa o usuário se logado, ou None se deslogado
        }
    )

#responseclass vai entender qual o endreço que ja ta sendo 
@app.get("/usuario/{nome}", response_class=HTMLResponse) 
def pagina_profile(
    request: Request,
    nome: str,
    db: Session = Depends(get_db)
):
    
    usuario_db = db.query(Cliente).filter(Cliente.nome == nome).first()

    # Monta o dicionário com as informações trazidas da tabela Cliente
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



@app.post("/login", response_class=HTMLResponse)
def verify_login(
    request: Request,
    login_input: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    # Sua consulta no banco de dados continua igual
    usuario_db = db.query(Cliente).filter(
        or_(
            Cliente.nome == login_input,
            Cliente.email == login_input
        ),
        Cliente.senha == senha
    ).first()

    if usuario_db:
        # 1. Armazena a resposta em uma variável
        response = templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"page_user": usuario_db}
        )
        
        # 2. Injeta o cookie identificando o usuário logado
        response.set_cookie(
            key="user_id",               # Nome do cookie
            value=str(usuario_db.id),     # Valor (guardamos o ID do usuário)
            httponly=True,               # Segurança: impede JS no navegador de acessar esse cookie
            max_age=3600,                # Expira em 1 hora (3600 segundos)
            samesite="lax"               # Proteção contra ataques CSRF
        )
        
        # 3. Retorna a resposta com o cookie gravado
        return response

    # Se a senha estiver incorreta
    return templates.TemplateResponse(
        request=request,
        name="login/Menu.html",
        context={"erro": "Usuário ou senha incorretos!"}
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
    verify = db.query(Cliente).filter(Cliente.nome == nome).first() or db.query(Cliente).filter(Cliente.cpf == CPF).first()
    if verify:
        return templates.TemplateResponse(
            request=request,
            name="cadastro/menu.html",
            context={"erro": "Esse usuário já existe!\n Tente fazer seu login. "}  # Envia o erro para o HTML
        )

    # Juntando o DDD e o Número em uma única string
    telefone_completo = f"{ddd}" + " " + f"{numero}"

    # Criando o objeto para salvar no banco via SQLAlchemy
    novo_usuario = Cliente(
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


@app.post("/carrinho/atualizar")
def atualizar_carrinho(
    request: Request,
    item_id: int = Form(...),
    acao: str = Form(...)
):
    carrinho_cookie = request.cookies.get("carrinho_catatau")
    carrinho_dict = json.loads(carrinho_cookie) if carrinho_cookie else {}
    
    key = str(item_id)
    if key in carrinho_dict:
        if acao == "aumentar":
            carrinho_dict[key] += 1
        elif acao == "diminuir":
            carrinho_dict[key] -= 1
            if carrinho_dict[key] <= 0:
                del carrinho_dict[key]

    referer = request.headers.get("referer", "/cardapio")
    response = RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="carrinho_catatau", value=json.dumps(carrinho_dict), httponly=True)
    return response


@app.post("/carrinho/remover")
def remover_do_carrinho(
    request: Request,
    item_id: int = Form(...)
):
    carrinho_cookie = request.cookies.get("carrinho_catatau")
    carrinho_dict = json.loads(carrinho_cookie) if carrinho_cookie else {}
    
    key = str(item_id)
    if key in carrinho_dict:
        del carrinho_dict[key]

    referer = request.headers.get("referer", "/cardapio")
    response = RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="carrinho_catatau", value=json.dumps(carrinho_dict), httponly=True)
    return response


@app.post("/carrinho/adicionar")
def adicionar_ao_carrinho(
    request: Request,
    item_id: int = Form(...)
):
    carrinho_cookie = request.cookies.get("carrinho_catatau")
    carrinho_dict = json.loads(carrinho_cookie) if carrinho_cookie else {}
    
    key = str(item_id)
    carrinho_dict[key] = carrinho_dict.get(key, 0) + 1

    referer = request.headers.get("referer", "/cardapio")
    response = RedirectResponse(url=referer, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="carrinho_catatau", value=json.dumps(carrinho_dict), httponly=True)
    return response



@app.get("/logout")
def logout():
    response = RedirectResponse(url="/catatau", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="user_id")  # Apaga o cookie do navegador
    return response




























@app.get("/administrator")
def mostrar_geral(db: Session = Depends(get_db)):
    all_users = db.query(Cliente).all()
    return all_users