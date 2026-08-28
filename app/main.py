# Ponte de entrada do meu sistema
import os
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.auth import get_usuario_opcional
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


from app.controllers import auth_controller
from app.controllers import usuario_controller
from app.controllers import categoria_controller
from app.controllers import produto_controller
from app.controllers import movimentacoes_controller
from app.controllers import cliente_controller
from app.controllers import pvd_controller

app = FastAPI(title="Sistema de Ponto de venda")

#Configurar a pasta para servir os arquivos estáticos (CSS, JS e IMG)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

#Configurar o jinja2 para renderizar os HTML
templates = Jinja2Templates(directory="app/templates")

#Inclui os routers dos controladores
app.include_router(auth_controller.router)
app.include_router(usuario_controller.router)
app.include_router(categoria_controller.router)
app.include_router(produto_controller.router)
app.include_router(movimentacoes_controller.router)
app.include_router(cliente_controller.router)
app.include_router(pvd_controller.router)


@app.get("/")
def tela_inicial(
    request: Request,
    usuario = Depends(get_usuario_opcional)
):
    #Tela não logado
    if usuario is None:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"request": request}
        )
    #Logado - exibir a tela de funcionario
    return templates.TemplateResponse(
        request,
        "home.html",
        {"request": request, "usuario": usuario}
    )