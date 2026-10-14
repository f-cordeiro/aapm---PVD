
import json
import logging

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.venda import Venda, ItemVenda
from app.models.produto import Produto
from app.models.cliente import Cliente
from app.auth import get_usuario_logado


# ============================================================
# CONFIGURAÇÕES
# ============================================================

router = APIRouter(prefix="/pdv", tags=["PDV"])
templates = Jinja2Templates(directory="app/templates")

logger = logging.getLogger(__name__)

DESCONTO_ASSOCIADO = 10.0
FORMAS_PAGAMENTO = {"dinheiro", "pix", "credito", "debito"}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def dinheiro(valor):
    """Arredonda um valor monetário para duas casas decimais."""
    return Decimal(str(valor)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def usuario_id_atual(usuario):
    """Obtém o ID do usuário, seja ele dicionário ou objeto."""
    if isinstance(usuario, dict):
        return usuario.get("id")

    return getattr(usuario, "id", None)


def redirecionar_erro(db, codigo):
    """Desfaz alterações pendentes e retorna ao PDV com um erro."""
    db.rollback()

    return RedirectResponse(
        url=f"/pdv/?erro={codigo}",
        status_code=303
    )


# ============================================================
# TELA PRINCIPAL DO PDV
# ============================================================

@router.get("/")
def tela_pdv(
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    produtos = (
        db.query(Produto)
        .filter(
            Produto.ativo.is_(True),
            Produto.estoque_atual > 0
        )
        .order_by(Produto.nome)
        .all()
    )

    clientes = (
        db.query(Cliente)
        .filter(Cliente.ativo.is_(True))
        .order_by(Cliente.nome)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "pdv/index.html",
        {
            "request": request,
            "usuario": usuario,
            "produtos": produtos,
            "clientes": clientes,
            "desconto_associado": DESCONTO_ASSOCIADO,
        }
    )


# ============================================================
# FINALIZAR VENDA
# ============================================================

@router.post("/finalizar")
def finalizar_venda(
    request: Request,
    carrinho_json: str = Form(...),
    cliente_id: int = Form(0),
    observacao: str = Form(""),
    desconto_manual: float = Form(0),
    forma_pagamento_1: str = Form(...),
    valor_pagamento_1: float = Form(...),
    forma_pagamento_2: str = Form(""),
    valor_pagamento_2: float = Form(0),
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    try:
        # ----------------------------------------------------
        # 1. Validar carrinho
        # ----------------------------------------------------

        itens = json.loads(carrinho_json)

        if not isinstance(itens, list) or not itens:
            return redirecionar_erro(db, "carrinho_vazio")

        # ----------------------------------------------------
        # 2. Validar desconto manual
        # ----------------------------------------------------

        desconto_manual = Decimal(str(desconto_manual))

        if (
            not desconto_manual.is_finite()
            or not Decimal("0") <= desconto_manual <= Decimal("100")
        ):
            return redirecionar_erro(db, "desconto")

        # ----------------------------------------------------
        # 3. Validar cliente
        # ----------------------------------------------------

        cliente = None

        if cliente_id:
            cliente = (
                db.query(Cliente)
                .filter(
                    Cliente.id == cliente_id,
                    Cliente.ativo.is_(True)
                )
                .first()
            )

            if not cliente:
                return redirecionar_erro(db, "cliente")

        # ----------------------------------------------------
        # 4. Calcular desconto total
        # ----------------------------------------------------

        desconto_associado = (
            Decimal("10")
            if cliente and cliente.is_associado
            else Decimal("0")
        )

        desconto_percentual = (
            desconto_associado + desconto_manual
        )

        if desconto_percentual > Decimal("100"):
            return redirecionar_erro(db, "desconto")

        # ----------------------------------------------------
        # 5. Consolidar e validar itens
        # ----------------------------------------------------

        quantidades = {}

        for item in itens:
            if not isinstance(item, dict):
                return redirecionar_erro(db, "itens")

            try:
                produto_id = int(item["produto_id"])
                quantidade = int(item["quantidade"])
            except (KeyError, TypeError, ValueError):
                return redirecionar_erro(db, "itens")

            # Não aceitar valores fracionários ou quantidades
            # que não sejam inteiros positivos.
            if produto_id <= 0 or quantidade <= 0:
                return redirecionar_erro(db, "quantidade")

            quantidades[produto_id] = (
                quantidades.get(produto_id, 0) + quantidade
            )

        # ----------------------------------------------------
        # 6. Buscar produtos e conferir estoque
        # ----------------------------------------------------

        produtos = (
            db.query(Produto)
            .filter(Produto.id.in_(quantidades.keys()))
            .order_by(Produto.id)
            .with_for_update()
            .all()
        )

        produtos_por_id = {produto.id: produto for produto in produtos}

        if len(produtos_por_id) != len(quantidades):
            return redirecionar_erro(db, "produto")

        itens_validados = []
        total_bruto = Decimal("0.00")

        for produto_id, quantidade in quantidades.items():
            produto = produtos_por_id[produto_id]

            if not produto.ativo:
                return redirecionar_erro(db, "produto")

            if produto.estoque_atual < quantidade:
                return redirecionar_erro(db, "estoque")

            preco = dinheiro(produto.preco)
            subtotal = dinheiro(preco * quantidade)

            total_bruto += subtotal

            itens_validados.append({
                "produto": produto,
                "quantidade": quantidade,
                "preco": preco,
                "subtotal": subtotal,
            })

        total_bruto = dinheiro(total_bruto)

        desconto_valor = dinheiro(
            total_bruto * desconto_percentual / Decimal("100")
        )

        total_liquido = dinheiro(total_bruto - desconto_valor)

        # ----------------------------------------------------
        # 7. Validar formas e valores de pagamento
        # ----------------------------------------------------

        forma1 = forma_pagamento_1.strip().lower()
        forma2 = forma_pagamento_2.strip().lower()

        if forma1 not in FORMAS_PAGAMENTO:
            return redirecionar_erro(db, "pagamento")

        valor1 = dinheiro(valor_pagamento_1)
        valor2 = dinheiro(valor_pagamento_2)

        if (
            not valor1.is_finite()
            or not valor2.is_finite()
            or valor1 < 0
            or valor2 < 0
        ):
            return redirecionar_erro(db, "pagamento")

        if forma2 and forma2 not in FORMAS_PAGAMENTO:
            return redirecionar_erro(db, "pagamento")

        if not forma2 and valor2 != Decimal("0.00"):
            return redirecionar_erro(db, "pagamento")

        if forma2 and valor2 <= 0:
            return redirecionar_erro(db, "pagamento")

        if dinheiro(valor1 + valor2) != total_liquido:
            return redirecionar_erro(db, "valores_pagamento")

        # ----------------------------------------------------
        # 8. Criar registro da venda
        # ----------------------------------------------------

        venda = Venda(
            cliente_id=cliente.id if cliente else None,
            usuario_id=usuario_id_atual(usuario),
            desconto_percentual=float(desconto_percentual),
            total_bruto=float(total_bruto),
            total_liquido=float(total_liquido),
            forma_pagamento_1=forma1,
            valor_pagamento_1=float(valor1),
            forma_pagamento_2=forma2 or None,
            valor_pagamento_2=float(valor2),
            observacao=observacao.strip() or None,
        )

        db.add(venda)

        # Gera o ID da venda antes de criar os itens.
        db.flush()

        # ----------------------------------------------------
        # 9. Registrar itens e atualizar estoque
        # ----------------------------------------------------

        for item in itens_validados:
            produto = item["produto"]

            registro_item = ItemVenda(
                venda_id=venda.id,
                produto_id=produto.id,
                produto_nome=produto.nome,
                quantidade=item["quantidade"],
                preco_unitario=float(item["preco"]),
            )

            db.add(registro_item)

            produto.estoque_atual -= item["quantidade"]

        # Guarda o ID antes de concluir a transação.
        venda_id = venda.id

        # Persiste a venda e seus itens em uma única transação.
        db.commit()

        logger.info("Venda %s finalizada com sucesso.", venda_id)

        # ----------------------------------------------------
        # 10. Abrir o comprovante após salvar a venda
        # ----------------------------------------------------

        return RedirectResponse(
            url=f"/pdv/venda/{venda_id}?sucesso=ok",
            status_code=303
        )

    except (json.JSONDecodeError, InvalidOperation, ValueError, TypeError):
        logger.exception("Dados inválidos ao finalizar a venda.")
        return redirecionar_erro(db, "dados")

    except SQLAlchemyError:
        logger.exception("Erro no banco ao finalizar a venda.")
        return redirecionar_erro(db, "banco")

    except Exception:
        logger.exception("Erro inesperado ao finalizar a venda.")
        return redirecionar_erro(db, "inesperado")


# ============================================================
# COMPROVANTE DA VENDA
# ============================================================

@router.get("/venda/{venda_id}")
def detalhe_venda(
    venda_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    venda = (
        db.query(Venda)
        .filter(Venda.id == venda_id)
        .first()
    )

    if not venda:
        return RedirectResponse(
            url="/pdv/?erro=venda_nao_encontrada",
            status_code=303
        )

    return templates.TemplateResponse(
        request,
        "pdv/comprovante.html",
        {
            "request": request,
            "usuario": usuario,
            "venda": venda,
        }
    )


# ============================================================
# HISTÓRICO DE VENDAS
# ============================================================

@router.get("/historico")
def historico_vendas(
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    vendas = (
        db.query(Venda)
        .order_by(Venda.criado_em.desc())
        .limit(100)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "pdv/historico.html",
        {
            "request": request,
            "usuario": usuario,
            "vendas": vendas,
        }
    )
