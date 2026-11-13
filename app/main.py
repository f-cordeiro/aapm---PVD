
# Ponte de entrada do meu sistema

import os

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import get_usuario_opcional

# Controllers
from app.controllers import auth_controller
from app.controllers import usuario_controller
from app.controllers import categoria_controller
from app.controllers import produto_controller
from app.controllers import movimentacoes_controller
from app.controllers import cliente_controller
from app.controllers import pvd_controller


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
app.include_router(pvd_controller.router)


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
