
from typing import Optional
from database.Tabelas import Cliente, Produto, Pedido, ItemPedido, ProdutoEstoque, Ingrediente
import json
from database.Banco import get_db
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # 1. Importe o StaticFile
from sqlalchemy import or_
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette import status
from fastapi import FastAPI, Depends, Form, Request, Query
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

@app.get("/contato")
def pagina_contato(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="contato/sobre-nos.html"
    )
@app.get("/checkout")
def pagina_checkout(
    request: Request,
    db: Session = Depends(get_db)
):
    # Carrega os itens do carrinho
    itens_carrinho, total = carregar_carrinho_do_cookie(request, db)
    
    # Pega o user_id diretamente do cookie da requisição (igualzinho na rota /catatau)
    user_id = request.cookies.get("user_id")
    usuario_banco = None
    
    if user_id:
        usuario_banco = db.query(Cliente).filter(Cliente.id == int(user_id)).first()

    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "carrinho": itens_carrinho,
            "total_carrinho": total,
            "page_user": usuario_banco, # <- Certifique-se que no HTML o campo usa essa variável
        }
    )
@app.post("/checkout/enviar")
def enviar_pedido_cozinha(
    request: Request,
    mesa: str = Form(...),
    cliente: str = Form(...),
    descricao: Optional[str] = Form(None),  # <--- RECEBE A DESCRIÇÃO / OBSERVAÇÃO
    db: Session = Depends(get_db)
):
    itens_carrinho, total = carregar_carrinho_do_cookie(request, db)
    
    if not itens_carrinho:
        return RedirectResponse(url="/cardapio", status_code=status.HTTP_303_SEE_OTHER)

    novo_pedido = Pedido(
        nome_cliente=cliente,
        num_mesa=int(mesa) if mesa.isdigit() else 0,
        descricao=descricao,  # <--- SALVA A DESCRIÇÃO NO BANCO DE DADOS
        status="ESPERANDO",
        valor_final=total
    )

    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido) # Atualiza para obter o ID gerado

    # Salva os itens do carrinho corretamente
    for item in itens_carrinho:
        prod_id = item["id"] if isinstance(item, dict) else item.id
        qtd = item["quantidade"] if isinstance(item, dict) else item.quantidade

        item_bd = ItemPedido(
            fk_id_pedido=novo_pedido.id,
            fk_id_produto=prod_id,
            quantidade=qtd
        )
        db.add(item_bd)

        #aqui estou descontando os ingredientes de cada lanches na tabela de ingredientes
        associacoes_estoque = db.query(ProdutoEstoque).filter(ProdutoEstoque.fk_id_produto == prod_id).all()
        for assoc in associacoes_estoque:
            ingrediente = db.query(Ingrediente).filter(Ingrediente.id == assoc.fk_id_estoque).first()
            if ingrediente:
                total_gasto = assoc.quantidade_necessaria * qtd
                ingrediente.quantidade -= total_gasto

    db.commit() # Salva todos os ItemPedido no banco

    response = RedirectResponse(url="/catatau?enviado=true", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="carrinho_catatau")    
    return response


@app.get("/lanche/{nome}")
def pagina_lanche(
    nome: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # Carrega os itens do carrinho através do cookie (compartilhado entre todas as páginas)
    itens_carrinho, total = carregar_carrinho_do_cookie(request, db)
    
    # Monta o caminho do template dinamicamente usando o nome recebido na URL
    # Exemplo: se a URL for /lanche/whopper, vai procurar em cardapio/envlanches/whopper.html
    template_name = f"cardapio/envlanches/{nome}.html"

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={
            "carrinho": itens_carrinho,
            "total_carrinho": total
        }
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
    enviado: Annotated[str | None, Query()] = None,  # Captura se veio ?enviado=true na URL
    user_id: Annotated[str | None, Cookie()] = None,  # Captura o cookie do usuário logado
    db: Session = Depends(get_db)
):
    usuario_banco = None
    mensagem_pedido = None  # Começa vazia por padrão

    # Só preenche a mensagem se o parâmetro 'enviado' vier igual a "true" na URL
    if enviado == "true":
        mensagem_pedido = "SEU LANCHE FOI ENVIADO PARA A COZINHA \n SEU PEDIDO SERA ENTREGUE EM 10 MINUTOS!" 

    # Se o cookie existir, busca o usuário no banco
    if user_id:
        usuario_banco = db.query(Cliente).filter(Cliente.id == int(user_id)).first()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "page_user": usuario_banco,  
            "enviado": mensagem_pedido   # Vai ser None se não acabou de comprar, ou a mensagem se acabou de comprar
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