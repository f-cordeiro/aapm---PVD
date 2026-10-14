# ============================================================
# controllers/pdv_controller.py — Ponto de Venda
# ============================================================

import json
import math

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.models.venda import Venda, ItemVenda
from app.auth import get_usuario_logado


router = APIRouter(prefix="/pdv", tags=["PDV"])

templates = Jinja2Templates(directory="app/templates")

DESCONTO_ASSOCIADO = 10.0

FORMAS_PAGAMENTO = {
    "dinheiro",
    "pix",
    "credito",
    "debito",
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def redirecionar_erro(db: Session, erro: str):
    """Desfaz alterações pendentes e retorna à tela do PDV."""
    db.rollback()

    return RedirectResponse(
        url=f"/pdv/?erro={erro}",
        status_code=303,
    )


def converter_valor(valor, padrao=0.0) -> float:
    """Converte um valor numérico sem permitir NaN ou infinito."""
    try:
        numero = float(valor)

        if not math.isfinite(numero):
            return padrao

        return numero

    except (TypeError, ValueError, OverflowError):
        return padrao


def valor_em_centavos(valor: float) -> int:
    """Converte dinheiro para centavos para evitar erros de comparação."""
    return int(round(valor * 100))


# ============================================================
# TELA PRINCIPAL DO PDV
# GET /pdv/
# ============================================================

@router.get("/", response_class=HTMLResponse)
def tela_pdv(
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado),
):
    produtos = (
        db.query(Produto)
        .filter(
            Produto.ativo.is_(True),
            Produto.estoque_atual > 0,
        )
        .order_by(Produto.nome.asc())
        .all()
    )

    clientes = (
        db.query(Cliente)
        .filter(Cliente.ativo.is_(True))
        .order_by(Cliente.nome.asc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="pdv/index.html",
        context={
            "request": request,
            "usuario": usuario,
            "produtos": produtos,
            "clientes": clientes,
            "desconto_associado": DESCONTO_ASSOCIADO,
        },
    )


# ============================================================
# FINALIZAR VENDA
# POST /pdv/finalizar
# ============================================================

@router.post("/finalizar")
def finalizar_venda(
    carrinho_json: str = Form(...),
    cliente_id: int = Form(0),
    observacao: str = Form(""),
    desconto_manual: float = Form(0),
    forma_pagamento_1: str = Form(...),
    valor_pagamento_1: float = Form(...),
    forma_pagamento_2: str = Form(""),
    valor_pagamento_2: float = Form(0),
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado),
):
    # --------------------------------------------------------
    # 1. Validar e interpretar o carrinho
    # --------------------------------------------------------

    try:
        itens = json.loads(carrinho_json)

    except (json.JSONDecodeError, TypeError, ValueError):
        return redirecionar_erro(db, "itens")

    if not isinstance(itens, list) or not itens:
        return redirecionar_erro(db, "vazio")

    # Soma quantidades repetidas do mesmo produto.
    quantidades = {}

    for item in itens:
        if not isinstance(item, dict):
            return redirecionar_erro(db, "itens")

        try:
            id_original = item["produto_id"]
            quantidade_original = item["quantidade"]

            # Booleanos são tratados como inválidos, embora em Python
            # bool seja uma subclasse de int.
            if (
                isinstance(id_original, bool)
                or isinstance(quantidade_original, bool)
            ):
                return redirecionar_erro(db, "itens")

            # Aceita inteiros ou strings inteiras, como 3 ou "3".
            # Rejeita valores fracionários, como 2.5 ou "2.5".
            if isinstance(id_original, int):
                produto_id = id_original
            elif (
                isinstance(id_original, str)
                and id_original.strip().isdigit()
            ):
                produto_id = int(id_original.strip())
            else:
                return redirecionar_erro(db, "itens")

            if isinstance(quantidade_original, int):
                quantidade = quantidade_original
            elif (
                isinstance(quantidade_original, str)
                and quantidade_original.strip().isdigit()
            ):
                quantidade = int(quantidade_original.strip())
            else:
                return redirecionar_erro(db, "quantidade")

        except (KeyError, TypeError, ValueError, OverflowError):
            return redirecionar_erro(db, "itens")

        if produto_id <= 0 or quantidade <= 0:
            return redirecionar_erro(db, "quantidade")

        quantidades[produto_id] = (
            quantidades.get(produto_id, 0) + quantidade
        )

    if not quantidades:
        return redirecionar_erro(db, "vazio")

    # --------------------------------------------------------
    # 2. Validar cliente
    # --------------------------------------------------------

    cliente = None

    if cliente_id:
        cliente = (
            db.query(Cliente)
            .filter(
                Cliente.id == cliente_id,
                Cliente.ativo.is_(True),
            )
            .first()
        )

        if cliente is None:
            return redirecionar_erro(db, "cliente")

    # --------------------------------------------------------
    # 3. Validar desconto
    # --------------------------------------------------------

    desconto_manual = converter_valor(desconto_manual, -1)

    if not 0 <= desconto_manual <= 100:
        return redirecionar_erro(db, "desconto")

    desconto_associado = (
        DESCONTO_ASSOCIADO
        if cliente and cliente.is_associado
        else 0.0
    )

    desconto_percentual = desconto_associado + desconto_manual

    if desconto_percentual > 100:
        return redirecionar_erro(db, "desconto")

    # --------------------------------------------------------
    # 4. Validar formas e valores de pagamento
    # --------------------------------------------------------

    forma_pagamento_1 = (forma_pagamento_1 or "").strip().lower()
    forma_pagamento_2 = (forma_pagamento_2 or "").strip().lower()

    valor_pagamento_1 = converter_valor(valor_pagamento_1, -1)
    valor_pagamento_2 = converter_valor(valor_pagamento_2, -1)

    if forma_pagamento_1 not in FORMAS_PAGAMENTO:
        return redirecionar_erro(db, "pagamento")

    if forma_pagamento_2 and forma_pagamento_2 not in FORMAS_PAGAMENTO:
        return redirecionar_erro(db, "pagamento")

    if valor_pagamento_1 < 0 or valor_pagamento_2 < 0:
        return redirecionar_erro(db, "pagamento")

    if not forma_pagamento_2 and valor_pagamento_2 > 0:
        return redirecionar_erro(db, "pagamento")

    if forma_pagamento_2 and valor_pagamento_2 <= 0:
        return redirecionar_erro(db, "pagamento")

    # --------------------------------------------------------
    # 5. Consultar produtos e conferir estoque
    # --------------------------------------------------------

    produtos = (
        db.query(Produto)
        .filter(Produto.id.in_(list(quantidades.keys())))
        .with_for_update()
        .all()
    )

    produtos_por_id = {produto.id: produto for produto in produtos}

    # Se algum ID do carrinho não existir ou o produto estiver
    # inativo, não permite concluir a venda.
    if len(produtos_por_id) != len(quantidades):
        return redirecionar_erro(db, "produto")

    total_bruto = 0.0

    for produto_id, quantidade in quantidades.items():
        produto = produtos_por_id[produto_id]

        if not produto.ativo:
            return redirecionar_erro(db, "produto")

        if quantidade > produto.estoque_atual:
            return redirecionar_erro(db, "estoque")

        preco_unitario = converter_valor(produto.preco, -1)

        if preco_unitario < 0:
            return redirecionar_erro(db, "produto")

        total_bruto += preco_unitario * quantidade

    # --------------------------------------------------------
    # 6. Calcular desconto e total líquido
    # --------------------------------------------------------

    valor_desconto = total_bruto * (desconto_percentual / 100)
    total_liquido = max(0.0, total_bruto - valor_desconto)

    # Arredonda os valores monetários para duas casas decimais.
    total_bruto = round(total_bruto, 2)
    total_liquido = round(total_liquido, 2)

    valor_pagado = valor_pagamento_1 + valor_pagamento_2

    if valor_em_centavos(valor_pagado) != valor_em_centavos(total_liquido):
        return redirecionar_erro(db, "pagamento")

    # Se não houver segunda forma de pagamento, guarda seus campos
    # como nulos para não registrar uma forma vazia.
    if not forma_pagamento_2:
        forma_pagamento_2_db = None
        valor_pagamento_2_db = 0.0
    else:
        forma_pagamento_2_db = forma_pagamento_2
        valor_pagamento_2_db = round(valor_pagamento_2, 2)

    # --------------------------------------------------------
    # 7. Criar a venda e os itens
    # --------------------------------------------------------

    try:
        venda = Venda(
            cliente_id=cliente.id if cliente else None,
            usuario_id=getattr(usuario, "id", None),
            desconto_percentual=desconto_percentual,
            total_bruto=total_bruto,
            total_liquido=total_liquido,
            forma_pagamento_1=forma_pagamento_1,
            valor_pagamento_1=round(valor_pagamento_1, 2),
            forma_pagamento_2=forma_pagamento_2_db,
            valor_pagamento_2=valor_pagamento_2_db,
            observacao=(observacao or "").strip()[:255] or None,
        )

        db.add(venda)
        db.flush()

        for produto_id, quantidade in quantidades.items():
            produto = produtos_por_id[produto_id]

            item_venda = ItemVenda(
                venda_id=venda.id,
                produto_id=produto.id,
                produto_nome=produto.nome,
                quantidade=quantidade,
                preco_unitario=round(float(produto.preco), 2),
            )

            db.add(item_venda)

            # Baixa o estoque somente após validar a quantidade.
            produto.estoque_atual -= quantidade

        db.commit()
        db.refresh(venda)

        return RedirectResponse(
            url=f"/pdv/venda/{venda.id}?sucesso=ok",
            status_code=303,
        )

    except Exception:
        db.rollback()
        return RedirectResponse(
            url="/pdv/?erro=interno",
            status_code=303,
        )


# ============================================================
# COMPROVANTE DA VENDA
# GET /pdv/venda/{venda_id}
# ============================================================

@router.get("/venda/{venda_id}", response_class=HTMLResponse)
def comprovante_venda(
    venda_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado),
):
    venda = (
        db.query(Venda)
        .options(
            joinedload(Venda.cliente),
            joinedload(Venda.itens).joinedload(ItemVenda.produto),
        )
        .filter(Venda.id == venda_id)
        .first()
    )

    if venda is None:
        return RedirectResponse(
            url="/pdv/historico?erro=venda_nao_encontrada",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="pdv/comprovante.html",
        context={
            "request": request,
            "usuario": usuario,
            "venda": venda,
        },
    )


# ============================================================
# HISTÓRICO DE VENDAS
# GET /pdv/historico
# ============================================================

@router.get("/historico", response_class=HTMLResponse)
def historico_vendas(
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado),
):
    vendas = (
        db.query(Venda)
        .options(joinedload(Venda.cliente))
        .order_by(Venda.criado_em.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="pdv/historico.html",
        context={
            "request": request,
            "usuario": usuario,
            "vendas": vendas,
        },
    )