# controllers/cliente_controller.py
# ============================================================
# CRUD DE CLIENTES / ASSOCIADOS
# Somente administradores podem realizar alterações.
# ============================================================

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cliente import Cliente
from app.auth import get_admin


router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

templates = Jinja2Templates(
    directory="app/templates"
)


# ============================================================
# LISTAR CLIENTES
# ============================================================

@router.get("/", response_class=HTMLResponse)
def listar_clientes(
    request: Request,
    busca: str = "",
    apenas_associados: bool = False,
    db: Session = Depends(get_db),
    admin=Depends(get_admin)
):

    query = db.query(Cliente)

    # --------------------------------------------------------
    # BUSCA POR NOME OU MATRÍCULA
    # --------------------------------------------------------

    if busca.strip():

        termo = busca.strip()

        query = query.filter(
            Cliente.nome.ilike(f"%{termo}%") |
            Cliente.matricula.ilike(f"%{termo}%")
        )

    # --------------------------------------------------------
    # FILTRO DE ASSOCIADOS
    # --------------------------------------------------------

    if apenas_associados:

        query = query.filter(
            Cliente.is_associado == True
        )

    # --------------------------------------------------------
    # CLIENTES
    # --------------------------------------------------------

    clientes = query.order_by(
        Cliente.nome
    ).all()

    # --------------------------------------------------------
    # TOTAL DE ASSOCIADOS ATIVOS
    # --------------------------------------------------------

    total_associados = db.query(Cliente).filter(
        Cliente.is_associado == True,
        Cliente.ativo == True
    ).count()

    # --------------------------------------------------------
    # TEMPLATE
    # --------------------------------------------------------

    return templates.TemplateResponse(
        request,
        "clientes/index.html",
        {
            "request": request,
            "usuario": admin,
            "clientes": clientes,
            "busca": busca,
            "apenas_associados": apenas_associados,
            "total_associados": total_associados,
        }
    )


# ============================================================
# FORMULÁRIO — NOVO CLIENTE
# Somente ADMIN
# ============================================================

@router.get("/novo", response_class=HTMLResponse)
def form_novo(
    request: Request,
    admin=Depends(get_admin)
):

    return templates.TemplateResponse(
        request,
        "clientes/form.html",
        {
            "request": request,
            "usuario": admin,
            "editando": None,
            "valores": None,
            "erro": None
        }
    )


# ============================================================
# CADASTRAR CLIENTE
# Somente ADMIN
# ============================================================

@router.post("/novo")
def criar(
    request: Request,
    nome: str = Form(...),
    matricula: str = Form(""),
    telefone: str = Form(""),
    is_associado: bool = Form(False),
    db: Session = Depends(get_db),
    admin=Depends(get_admin)
):

    # --------------------------------------------------------
    # LIMPAR DADOS
    # --------------------------------------------------------

    nome = nome.strip()
    matricula = matricula.strip()
    telefone = telefone.strip()

    # --------------------------------------------------------
    # VERIFICAR MATRÍCULA DUPLICADA
    # --------------------------------------------------------

    if matricula:

        existente = db.query(Cliente).filter(
            Cliente.matricula == matricula
        ).first()

        if existente:

            return templates.TemplateResponse(
                request,
                "clientes/form.html",
                {
                    "request": request,
                    "usuario": admin,
                    "editando": None,
                    "erro": f"Matrícula {matricula} já cadastrada.",
                    "valores": {
                        "nome": nome,
                        "matricula": matricula,
                        "telefone": telefone,
                        "is_associado": is_associado
                    }
                },
                status_code=400
            )

    # --------------------------------------------------------
    # CRIAR CLIENTE
    # --------------------------------------------------------

    cliente = Cliente(
        nome=nome,
        matricula=matricula or None,
        telefone=telefone or None,
        is_associado=is_associado
    )

    db.add(cliente)

    db.commit()

    # --------------------------------------------------------
    # VOLTAR PARA LISTA
    # --------------------------------------------------------

    return RedirectResponse(
        url="/clientes?criado=ok",
        status_code=302
    )


# ============================================================
# FORMULÁRIO — EDITAR CLIENTE
# Somente ADMIN
# ============================================================

@router.get(
    "/{cliente_id}/editar",
    response_class=HTMLResponse
)
def form_editar(
    cliente_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(get_admin)
):

    # --------------------------------------------------------
    # BUSCAR CLIENTE
    # --------------------------------------------------------

    editando = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    # --------------------------------------------------------
    # CLIENTE NÃO ENCONTRADO
    # --------------------------------------------------------

    if not editando:

        return RedirectResponse(
            url="/clientes",
            status_code=302
        )

    # --------------------------------------------------------
    # ABRIR FORMULÁRIO
    # --------------------------------------------------------

    return templates.TemplateResponse(
        request,
        "clientes/form.html",
        {
            "request": request,
            "usuario": admin,
            "editando": editando,
            "valores": None,
            "erro": None
        }
    )


# ============================================================
# EDITAR CLIENTE
# Somente ADMIN
# ============================================================

@router.post("/{cliente_id}/editar")
def editar(
    cliente_id: int,
    request: Request,
    nome: str = Form(...),
    matricula: str = Form(""),
    telefone: str = Form(""),
    is_associado: bool = Form(False),
    db: Session = Depends(get_db),
    admin=Depends(get_admin)
):

    # --------------------------------------------------------
    # LIMPAR DADOS
    # --------------------------------------------------------

    nome = nome.strip()
    matricula = matricula.strip()
    telefone = telefone.strip()

    # --------------------------------------------------------
    # BUSCAR CLIENTE
    # --------------------------------------------------------

    editando = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if not editando:

        return RedirectResponse(
            url="/clientes",
            status_code=302
        )

    # --------------------------------------------------------
    # VERIFICAR MATRÍCULA DUPLICADA
    # --------------------------------------------------------

    if matricula:

        conflito = db.query(Cliente).filter(
            Cliente.matricula == matricula,
            Cliente.id != cliente_id
        ).first()

        if conflito:

            return templates.TemplateResponse(
                request,
                "clientes/form.html",
                {
                    "request": request,
                    "usuario": admin,
                    "editando": editando,
                    "erro": f"Matrícula {matricula} já está em uso.",
                    "valores": {
                        "nome": nome,
                        "matricula": matricula,
                        "telefone": telefone,
                        "is_associado": is_associado
                    }
                },
                status_code=400
            )

    # --------------------------------------------------------
    # ATUALIZAR CLIENTE
    # --------------------------------------------------------

    editando.nome = nome
    editando.matricula = matricula or None
    editando.telefone = telefone or None
    editando.is_associado = is_associado

    db.commit()

    # --------------------------------------------------------
    # VOLTAR PARA LISTA
    # --------------------------------------------------------

    return RedirectResponse(
        url="/clientes?editado=ok",
        status_code=302
    )


# ============================================================
# ATIVAR / DESATIVAR CLIENTE
# Somente ADMIN
# ============================================================

@router.post("/{cliente_id}/toggle-ativo")
def toggle_ativo(
    cliente_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_admin)
):

    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if cliente:

        cliente.ativo = not cliente.ativo

        db.commit()

    return RedirectResponse(
        url="/clientes",
        status_code=302
    )