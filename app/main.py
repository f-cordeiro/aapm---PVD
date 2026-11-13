
# Ponte de entrada do meu sistema

import os

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import get_usuario_opcional
<<<<<<< HEAD
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

=======
>>>>>>> 33a01c7ddebe0284b5c635854316f1e0131cd01e

# Controllers
from app.controllers import auth_controller
from app.controllers import usuario_controller
from app.controllers import categoria_controller
from app.controllers import produto_controller
from app.controllers import movimentacoes_controller
from app.controllers import cliente_controller
from app.controllers import pdv_controller


# ==========================================
# CONFIGURAÇÃO PRINCIPAL
# ==========================================

app = FastAPI(title="Sistema de Ponto de Venda")

current_dir = os.path.dirname(os.path.abspath(__file__))

static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

# Arquivos estáticos: CSS, JS e imagens
app.mount(
    "/static",
    StaticFiles(directory=static_dir),
    name="static"
)

# Configuração Jinja2
templates = Jinja2Templates(directory=templates_dir)


# ==========================================
# INCLUSÃO DOS CONTROLLERS
# ==========================================

app.include_router(auth_controller.router)
app.include_router(usuario_controller.router)
app.include_router(categoria_controller.router)
app.include_router(produto_controller.router)
app.include_router(movimentacoes_controller.router)
app.include_router(cliente_controller.router)
app.include_router(pdv_controller.router)


# ==========================================
# ROTA INICIAL
# ==========================================

@app.get("/")
def tela_inicial(
    request: Request,
    usuario=Depends(get_usuario_opcional)
):
    if usuario is None:
        return templates.TemplateResponse(
<<<<<<< HEAD
            request,
            "auth/login.html",
            {"request": request}
        )
    #Logado - exibir a tela de funcionario
    return RedirectResponse(url="/pdv/", status_code=302)
=======
            "index.html",
            {"request": request}
        )

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "usuario": usuario
        }
    )


# ==========================================
# DASHBOARD PRINCIPAL
# ==========================================

@app.get("/dashboard")
def dashboard(
    request: Request,
    usuario=Depends(get_usuario_opcional)
):
    if usuario is None:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "usuario": usuario
        }
    )


# ==========================================
# DASHBOARD DE MOVIMENTAÇÕES
# ==========================================

@app.get("/movimentacoes/dashboard")
def dashboard_movimentacoes(
    request: Request,
    usuario=Depends(get_usuario_opcional)
):
    if usuario is None:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse(
        "movimentacoes/dashboard.html",
        {
            "request": request,
            "usuario": usuario
        }
    )
>>>>>>> 33a01c7ddebe0284b5c635854316f1e0131cd01e
